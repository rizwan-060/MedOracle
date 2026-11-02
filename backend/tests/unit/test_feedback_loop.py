"""Unit tests for the Continuous Active Learning Feedback and Retraining Loop."""

from pathlib import Path
import numpy as np
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.models import TrainedModel
from app.database.session import Base
from app.ml.feedback.buffer import FeedbackBuffer, FeedbackRecord
from app.ml.feedback.retrainer import ContinuousRetrainer
from app.ml.feedback.sync import sync_all_models_to_db


@pytest.fixture
def test_db_session():
    """Create an isolated in-memory SQLite database session for unit tests."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()


def test_feedback_record_schema():
    """Verify FeedbackRecord creation, default UUID, and serialization."""
    rec = FeedbackRecord(
        target_disease="cardio",
        features={"age": 55.0, "chol": 240.0, "trestbps": 130.0},
        ground_truth_label=1,
        source="clinician_verified",
        confidence_at_prediction=82.5,
    )
    assert rec.sample_id is not None
    assert rec.target_disease == "cardio"
    assert rec.features["age"] == 55.0
    assert rec.ground_truth_label == 1
    assert rec.created_at is not None

    dumped = rec.model_dump_json()
    assert "clinician_verified" in dumped


def test_feedback_buffer_lifecycle(tmp_path: Path):
    """Verify appending, counting, loading, and archiving feedback records."""
    buffer = FeedbackBuffer(base_dir=tmp_path)

    # Empty buffer count
    assert buffer.get_count("cardio") == 0
    assert buffer.load_records("cardio") == []
    assert not buffer.should_retrain("cardio", threshold=3)

    # Append 3 records
    for i in range(3):
        rec = FeedbackRecord(
            target_disease="cardio",
            features={"age": 50.0 + i, "chol": 200.0 + i * 10},
            ground_truth_label=i % 2,
        )
        sample_id = buffer.add_record(rec)
        assert sample_id is not None

    assert buffer.get_count("cardio") == 3
    assert buffer.should_retrain("cardio", threshold=3)

    records = buffer.load_records("cardio")
    assert len(records) == 3
    assert records[0].features["age"] == 50.0

    # Archive and clear
    archived_file = buffer.archive_and_clear("cardio")
    assert archived_file is not None
    assert archived_file.exists()
    assert buffer.get_count("cardio") == 0
    assert len(buffer.load_records("cardio")) == 0


def test_retrainer_insufficient_samples(tmp_path: Path):
    """Verify retrainer gracefully aborts when buffer does not meet min_samples."""
    buffer = FeedbackBuffer(base_dir=tmp_path)
    retrainer = ContinuousRetrainer(buffer=buffer)

    result = retrainer.retrain_model("cardio", min_samples=10, force=False)
    assert not result.success
    assert not result.promoted
    assert "Insufficient feedback records" in result.message
    assert result.samples_used == 0


def test_retrainer_cardio_continuous_learning(tmp_path: Path, test_db_session):
    """Verify that adding verified feedback samples retrains the model with promotion gate."""
    import shutil
    from app.ml.model_registry import DEFAULT_MODELS_DIR

    tmp_models = tmp_path / "models"
    tmp_models.mkdir(parents=True, exist_ok=True)
    shutil.copy(DEFAULT_MODELS_DIR / "cardiovascular_risk_v1.joblib", tmp_models / "cardiovascular_risk_v1.joblib")
    shutil.copy(DEFAULT_MODELS_DIR / "cardiovascular_risk_v1_metadata.json", tmp_models / "cardiovascular_risk_v1_metadata.json")

    buffer = FeedbackBuffer(base_dir=tmp_path)
    retrainer = ContinuousRetrainer(buffer=buffer, models_dir=tmp_models)

    # Populate buffer with 4 realistic feedback samples for heart disease
    sample_features = {
        "age": 0.5,
        "sex": 1.0,
        "cp": 3.0,
        "trestbps": 0.2,
        "chol": -0.1,
        "fbs": 0.0,
        "restecg": 0.0,
        "thalach": 0.4,
        "exang": 0.0,
        "oldpeak": 0.1,
        "slope": 1.0,
        "ca": 0.0,
        "thal": 3.0,
    }
    for label in [0, 1, 0, 1]:
        buffer.add_record(
            FeedbackRecord(
                target_disease="cardio",
                features=sample_features,
                ground_truth_label=label,
                source="clinician_verified",
            )
        )

    assert buffer.get_count("cardio") == 4

    # Run continuous retraining
    result = retrainer.retrain_model(
        target_disease="cardio",
        min_samples=2,
        force=False,
        tolerance=0.05,
        db_session=test_db_session,
    )

    assert result.success is True
    assert result.samples_used == 4
    assert result.promoted is True
    assert result.new_version == "1.1.0"
    assert "roc_auc" in result.retrained_metrics
    assert result.retrained_metrics["roc_auc"] >= 0.80

    # Buffer should be cleared and archived after successful promotion
    assert buffer.get_count("cardio") == 0


def test_retrainer_rejection_gate(tmp_path: Path):
    """Verify that a degraded candidate model is rejected by the performance gate."""
    import shutil
    from app.ml.model_registry import DEFAULT_MODELS_DIR

    tmp_models = tmp_path / "models"
    tmp_models.mkdir(parents=True, exist_ok=True)
    shutil.copy(DEFAULT_MODELS_DIR / "cardiovascular_risk_v1.joblib", tmp_models / "cardiovascular_risk_v1.joblib")
    shutil.copy(DEFAULT_MODELS_DIR / "cardiovascular_risk_v1_metadata.json", tmp_models / "cardiovascular_risk_v1_metadata.json")

    buffer = FeedbackBuffer(base_dir=tmp_path)
    retrainer = ContinuousRetrainer(buffer=buffer, models_dir=tmp_models)

    # Add samples but test with an impossible zero-tolerance strict gate
    sample_features = {f"col_{i}": 0.0 for i in range(13)}
    buffer.add_record(
        FeedbackRecord(
            target_disease="cardio",
            features=sample_features,
            ground_truth_label=1,
        )
    )

    # Passing a negative tolerance forces the gate to reject unless retrained score strictly beats current + 1.0
    result = retrainer.retrain_model(
        target_disease="cardio",
        min_samples=1,
        force=True,
        tolerance=-0.50,  # Impossible threshold to guarantee trigger of rejection gate
    )

    assert result.success is True
    assert result.promoted is False
    assert "failed performance gate" in result.message
    assert result.rejection_reason is not None


def test_sync_models_to_database(test_db_session):
    """Verify synchronizing filesystem model metadata descriptors into the relational DB."""
    synced = sync_all_models_to_db(test_db_session)
    assert len(synced) >= 3

    model_ids = [m.name for m in synced]
    assert "cardiovascular_risk_v1" in model_ids
    assert "diabetes_risk_v1" in model_ids
    assert "symptoms_disease_v1" in model_ids

    # Check active status and metrics persistence
    for m in synced:
        assert m.is_active is True
        assert isinstance(m.metrics, dict)
        assert len(m.metrics) > 0
        assert m.artifact_path.startswith("models/saved/")
