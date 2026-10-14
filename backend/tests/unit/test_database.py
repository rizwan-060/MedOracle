"""Unit tests for MedOracle database models, relationships, and repositories.

Executes on an in-memory SQLite database ensuring isolation, speed, and safety.
"""

from datetime import date
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.models import (
    AgentOutput,
    AnalysisSession,
    Base,
    Doctor,
    LabResult,
    MedicalHistory,
    PatientProfile,
    RiskResult,
    SymptomReport,
    TrainedModel,
    User,
)
from app.database.repositories import (
    AgentOutputRepository,
    AnalysisSessionRepository,
    DoctorRepository,
    LabResultRepository,
    MedicalHistoryRepository,
    PatientProfileRepository,
    RiskResultRepository,
    SymptomReportRepository,
    TrainedModelRepository,
    UserRepository,
)


@pytest.fixture
def db_session():
    """Create a fresh in-memory SQLite database and session for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=engine, expire_on_commit=False
    )
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def test_schema_tables_exist():
    """Verify all 10 expected tables are registered in Base metadata."""
    expected_tables = {
        "users",
        "patient_profiles",
        "medical_histories",
        "symptom_reports",
        "lab_results",
        "analysis_sessions",
        "agent_outputs",
        "risk_results",
        "doctors",
        "trained_models",
    }
    actual_tables = set(Base.metadata.tables.keys())
    assert expected_tables.issubset(actual_tables)


def test_user_and_patient_profile_crud(db_session):
    """Test user creation and 1:1 patient profile association."""
    user_repo = UserRepository(db_session)
    profile_repo = PatientProfileRepository(db_session)

    user = user_repo.create(
        email="john.doe@example.com",
        hashed_password="hashed_secret_password_123",
        full_name="John Doe",
    )
    assert user.id is not None
    assert user.email == "john.doe@example.com"
    assert user.is_active is True

    # Associate profile
    profile = profile_repo.create_or_update(
        user_id=user.id,
        date_of_birth=date(1980, 5, 12),
        gender="male",
        height_cm=178.0,
        weight_kg=82.5,
        waist_circumference_cm=94.0,
        smoking_status="current_smoker",
        activity_level="low",
    )
    assert profile.id is not None
    assert profile.user_id == user.id
    assert profile.height_cm == 178.0

    # Retrieve by user
    retrieved = profile_repo.get_by_user_id(user.id)
    assert retrieved is not None
    assert retrieved.weight_kg == 82.5


def test_medical_history_repository(db_session):
    """Test medical history creation and retrieval."""
    user_repo = UserRepository(db_session)
    history_repo = MedicalHistoryRepository(db_session)

    user = user_repo.create(
        email="patient2@example.com",
        hashed_password="hash",
        full_name="Jane Doe",
    )
    history = history_repo.create(
        user_id=user.id,
        chronic_conditions=["hypertension"],
        past_surgeries=[],
        current_medications=[{"name": "lisinopril", "dosage": "10mg"}],
        allergies=["penicillin"],
        family_history=[
            {"relative": "father", "condition": "coronary_artery_disease", "age_at_onset": 54}
        ],
        notes="Patient reports good compliance with meds.",
    )
    assert history.id is not None
    assert "hypertension" in history.chronic_conditions

    latest = history_repo.get_latest_by_user_id(user.id)
    assert latest is not None
    assert latest.id == history.id


def test_symptom_report_repository(db_session):
    """Test symptom reporting and user-scoped listing."""
    user_repo = UserRepository(db_session)
    symptom_repo = SymptomReportRepository(db_session)

    user = user_repo.create(
        email="patient3@example.com",
        hashed_password="hash",
        full_name="Alice Smith",
    )
    report = symptom_repo.create(
        user_id=user.id,
        reported_text="Severe chest pressure during fast walking, radiates to jaw.",
        duration_days=4,
        severity_self_rating=8,
        body_locations=["chest", "jaw"],
        triggers=["walking", "stress"],
        structured_symptoms=["chest_pressure", "jaw_radiation", "exertional_dyspnea"],
    )
    assert report.id is not None
    assert report.severity_self_rating == 8

    user_reports = symptom_repo.list_by_user_id(user.id)
    assert len(user_reports) == 1
    assert user_reports[0].id == report.id


def test_lab_result_repository(db_session):
    """Test lab result storage with biomarker payloads."""
    user_repo = UserRepository(db_session)
    lab_repo = LabResultRepository(db_session)

    user = user_repo.create(
        email="patient4@example.com",
        hashed_password="hash",
        full_name="Bob Brown",
    )
    biomarkers = {
        "systolic_bp": 145,
        "diastolic_bp": 92,
        "total_cholesterol_mg_dl": 235,
        "hdl_cholesterol_mg_dl": 39,
        "fasting_blood_glucose_mg_dl": 112,
        "serum_creatinine_mg_dl": 1.05,
        "hba1c_percent": 6.0,
    }
    lab = lab_repo.create(
        user_id=user.id,
        test_date=date(2026, 10, 1),
        lab_name="Central Diagnostic Labs",
        biomarkers=biomarkers,
    )
    assert lab.id is not None
    assert lab.biomarkers["systolic_bp"] == 145

    latest = lab_repo.get_latest_by_user_id(user.id)
    assert latest is not None
    assert latest.biomarkers["total_cholesterol_mg_dl"] == 235


def test_analysis_session_and_agent_outputs(db_session):
    """Test analysis session orchestration lifecycle and agent outputs."""
    user_repo = UserRepository(db_session)
    session_repo = AnalysisSessionRepository(db_session)
    agent_output_repo = AgentOutputRepository(db_session)

    user = user_repo.create(
        email="patient5@example.com",
        hashed_password="hash",
        full_name="Charlie Davis",
    )
    session = session_repo.create(user_id=user.id)
    assert session.status == "pending"
    assert session.progress_percent == 0

    # Add agent outputs
    out1 = agent_output_repo.create(
        analysis_session_id=session.id,
        agent_role="symptom_agent",
        findings="Cluster suggestive of exertional angina.",
        confidence=85.0,
        reasoning_chain=["Patient reports exertional chest pressure", "Radiation to jaw"],
        evidence=["Duration 4 days", "Severity 8/10"],
    )
    assert out1.id is not None
    assert out1.confidence == 85.0

    out2 = agent_output_repo.create(
        analysis_session_id=session.id,
        agent_role="laboratory_agent",
        findings="Borderline dyslipidemia and elevated systolic BP.",
        confidence=88.0,
        reasoning_chain=["Total cholesterol 235 > 200", "HDL 39 < 40"],
        evidence=["Panel from 2026-10-01"],
    )
    assert out2.id is not None

    # Update session results
    updated = session_repo.update_results(
        session_id=session.id,
        status="completed",
        current_phase="completed",
        progress_percent=100,
        consensus_verdict={
            "primary_risk_category": "Cardiovascular Disease",
            "overall_urgency": "high",
            "consensus_confidence": 86.5,
        },
        recommended_specialty="Cardiology",
    )
    assert updated.status == "completed"
    assert updated.recommended_specialty == "Cardiology"

    session_outputs = agent_output_repo.list_by_session_id(session.id)
    assert len(session_outputs) == 2


def test_risk_result_repository(db_session):
    """Test risk result calculation persistence."""
    user_repo = UserRepository(db_session)
    risk_repo = RiskResultRepository(db_session)

    user = user_repo.create(
        email="patient6@example.com",
        hashed_password="hash",
        full_name="Diana Prince",
    )
    risk = risk_repo.create(
        user_id=user.id,
        model_name="Framingham 10-Year General CVD",
        model_type="clinical_formula",
        risk_score=21.4,
        risk_category="high",
        horizon="10_year",
        input_parameters={"age": 55, "systolic_bp": 140, "cholesterol": 220},
        disclaimer="MedOracle decision support only.",
    )
    assert risk.id is not None
    assert risk.risk_score == 21.4

    results = risk_repo.list_by_user_id(user.id)
    assert len(results) == 1
    assert results[0].risk_category == "high"


def test_doctor_repository(db_session):
    """Test doctor directory persistence and specialty search."""
    doc_repo = DoctorRepository(db_session)

    doc_repo.create(
        name="Dr. Sarah Khan",
        specialty="Cardiology",
        sub_specialty="Interventional Cardiology",
        hospital_clinic="Punjab Institute of Cardiology",
        city="Lahore",
        area="Jail Road",
        contact_phone="+92-42-99203051",
        rating=4.9,
    )
    doc_repo.create(
        name="Dr. Tariq Mahmood",
        specialty="Endocrinology",
        hospital_clinic="Shaukat Khanum Memorial",
        city="Lahore",
        area="Johar Town",
        contact_phone="+92-42-35905000",
        rating=4.8,
    )

    cardiologists = doc_repo.search_by_specialty(specialty="Cardiology", city="Lahore")
    assert len(cardiologists) == 1
    assert cardiologists[0].name == "Dr. Sarah Khan"


def test_trained_model_repository(db_session):
    """Test trained ML model cataloging in the model registry."""
    model_repo = TrainedModelRepository(db_session)

    model = model_repo.register_model(
        name="cardiovascular_rf_classifier",
        version="v1.0.0",
        target_disease="Cardiovascular Disease",
        algorithm="RandomForestClassifier",
        dataset_source="UCI Heart Disease",
        artifact_path="backend/app/ml/models/cardio_rf_v1.joblib",
        metrics={"roc_auc": 0.884, "f1_score": 0.821, "accuracy": 0.845},
        feature_names=["age", "sex", "cp", "trestbps", "chol", "fbs", "restecg"],
        is_active=True,
    )
    assert model.id is not None

    active_model = model_repo.get_active_by_name("cardiovascular_rf_classifier")
    assert active_model is not None
    assert active_model.metrics["roc_auc"] == 0.884
