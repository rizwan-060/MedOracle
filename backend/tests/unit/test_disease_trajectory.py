"""Unit tests for Disease Trajectory Forecasting (longitudinal processing, leakage prevention, ML, and Step 12 integration)."""

from datetime import datetime, timezone
from pathlib import Path
import tempfile
import pytest

from app.agents.disease_trajectory_agent import DiseaseTrajectoryAgent
from app.graph import create_initial_graph_state, run_clinical_graph
from app.ml.forecasting.longitudinal import LongitudinalFeatureExtractor
from app.ml.forecasting.trajectory import (
    ClinicalTrendForecaster,
    LongitudinalMLForecaster,
    generate_synthetic_longitudinal_benchmark,
    temporal_patient_split,
)
from app.schemas.trajectory import TrajectoryDirection


def test_longitudinal_feature_extraction_irregular_and_missing():
    """Verify temporal features on irregular visits without interpolating missing biomarkers."""
    extractor = LongitudinalFeatureExtractor()
    labs = [
        {
            "id": "lab-1",
            "test_date": "2026-01-01",
            "biomarkers": {"systolic_bp": 132.0, "hba1c_percent": 6.4},
        },
        {
            "id": "lab-2",
            "test_date": "2026-02-15",  # 45 days later
            "biomarkers": {"systolic_bp": 144.0, "hba1c_percent": 6.9},
        },
        {
            "id": "lab-3",
            "test_date": "2026-03-17",  # 30 days later
            "biomarkers": {"systolic_bp": 156.0},  # hba1c omitted on visit 3
        },
    ]
    fv = extractor.extract(lab_history=labs, patient_id="p-1")

    assert fv.total_lab_visits == 3
    assert fv.observation_window_days == 75.0

    sbp = fv.biomarker_trends["systolic_bp"]
    assert sbp.observation_count == 3
    assert sbp.latest_value == 156.0
    assert sbp.previous_value == 144.0
    assert sbp.time_since_previous_days == 30.0
    assert sbp.absolute_change == 12.0
    assert sbp.rate_of_change_per_30d == 12.0
    assert sbp.moving_average_3 == 144.0
    assert sbp.variability_std is not None and sbp.variability_std > 0
    assert sbp.abnormal_value_duration_days == 30.0  # 144 >= 140 for 30 days until 156
    assert sbp.trend_direction == TrajectoryDirection.WORSENING

    # Missing biomarker must NOT be interpolated or fabricated
    ldl = fv.biomarker_trends["ldl_cholesterol_mg_dl"]
    assert ldl.is_missing is True
    assert ldl.insufficient_history is True
    assert ldl.latest_value is None
    assert ldl.rate_of_change_per_30d is None


def test_longitudinal_cutoff_prevents_future_leakage():
    """Verify observations after cutoff_time are strictly excluded from extracted features."""
    extractor = LongitudinalFeatureExtractor()
    labs = [
        {"id": "l1", "test_date": "2026-01-01", "biomarkers": {"systolic_bp": 125.0}},
        {"id": "l2", "test_date": "2026-02-01", "biomarkers": {"systolic_bp": 130.0}},
        {"id": "l3", "test_date": "2026-06-01", "biomarkers": {"systolic_bp": 195.0}},  # Future!
    ]
    cutoff = datetime(2026, 2, 15, tzinfo=timezone.utc)
    fv = extractor.extract(lab_history=labs, cutoff_time=cutoff)

    assert fv.total_lab_visits == 2
    assert fv.biomarker_trends["systolic_bp"].latest_value == 130.0
    assert "l3" not in fv.source_record_ids


def test_temporal_patient_split_zero_overlap():
    """Verify patient_ids never cross train/val/test partitions and temporal ordering holds."""
    bench = generate_synthetic_longitudinal_benchmark(num_patients=60, seed=7)
    assert bench["is_synthetic_benchmark"] is True
    assert bench["clinically_validated"] is False

    train, val, test = temporal_patient_split(bench["records"])
    train_p = {r["patient_id"] for r in train}
    val_p = {r["patient_id"] for r in val}
    test_p = {r["patient_id"] for r in test}

    assert train_p.isdisjoint(val_p)
    assert train_p.isdisjoint(test_p)
    assert val_p.isdisjoint(test_p)
    assert max(r["prediction_time"] for r in train) <= min(r["prediction_time"] for r in test)


@pytest.mark.parametrize("algorithm", ["logistic_regression", "random_forest", "gradient_boosting"])
def test_ml_forecaster_training_evaluation_and_persistence(algorithm: str):
    """Verify reproducible training, metrics, and save/load across candidate ML algorithms."""
    bench = generate_synthetic_longitudinal_benchmark(num_patients=90, seed=42)
    forecaster = LongitudinalMLForecaster(algorithm=algorithm, horizon_days=180)
    report = forecaster.train_and_evaluate(bench["records"])

    assert 0.0 <= report["test_metrics"]["auroc"] <= 1.0
    assert 0.0 <= report["test_metrics"]["auprc"] <= 1.0
    assert 0.0 <= report["test_metrics"]["brier_score"] <= 1.0

    with tempfile.TemporaryDirectory() as tmpdir:
        forecaster.save(models_dir=Path(tmpdir))
        reloaded = LongitudinalMLForecaster.load(report["model_id"], models_dir=Path(tmpdir))
        extractor = LongitudinalFeatureExtractor()
        fv = extractor.extract(
            lab_history=[
                {"test_date": "2026-01-01", "biomarkers": {"systolic_bp": 145.0, "hba1c_percent": 7.2}},
                {"test_date": "2026-02-01", "biomarkers": {"systolic_bp": 152.0, "hba1c_percent": 7.6}},
            ]
        )
        prob = reloaded.predict_worsening_probability(fv)
        assert 0.0 <= prob <= 1.0


def test_forecaster_uncertainty_widens_with_epistemic_doubt_and_insufficient_data():
    """Verify Step 12 epistemic doubt widens uncertainty and empty input yields INSUFFICIENT_DATA."""
    extractor = LongitudinalFeatureExtractor()
    forecaster = ClinicalTrendForecaster()

    # 1. Empty patient data -> INSUFFICIENT_DATA
    empty_fv = extractor.extract()
    empty_res = forecaster.forecast(empty_fv)
    assert empty_res.overall_direction == TrajectoryDirection.INSUFFICIENT_DATA
    assert all(h.projected_risk_percent is None for h in empty_res.horizons)

    # 2. Epistemic doubt widens uncertainty bounds
    fv = extractor.extract(
        lab_history=[
            {"test_date": "2026-01-01", "biomarkers": {"systolic_bp": 140.0}},
            {"test_date": "2026-02-01", "biomarkers": {"systolic_bp": 150.0}},
        ]
    )
    low_doubt = forecaster.forecast(fv, current_risk_percent=20.0, epistemic_doubt_score=0.05)
    high_doubt = forecaster.forecast(fv, current_risk_percent=20.0, epistemic_doubt_score=0.75)

    w_low = low_doubt.horizons[0].uncertainty_upper_percent - low_doubt.horizons[0].uncertainty_lower_percent
    w_high = high_doubt.horizons[0].uncertainty_upper_percent - high_doubt.horizons[0].uncertainty_lower_percent
    assert w_high > w_low
    assert high_doubt.horizons[0].confidence_level < low_doubt.horizons[0].confidence_level


def test_langgraph_end_to_end_preserves_safety_warnings_in_trajectory():
    """Verify Step 11 -> Step 12 -> Disease Trajectory Forecasting preserves emergent safety alerts."""
    initial_state = create_initial_graph_state(
        patient_demographics={"age": 63, "sex": "male"},
        symptoms_data={"symptoms": ["chest_pain"], "severity": 9},
        laboratory_data={
            "cardiac_troponin_ng_ml": 0.09,
            "cardiac_troponin_assay": "hs_ctnt_roche",
            "systolic_bp": 165.0,
        },
        clinical_scores={"framingham_risk_percent": 24.0},
        provider="mock",
        use_cache=False,
    )
    final_state = run_clinical_graph(initial_state)
    assert final_state["status"] == "completed"
    assert final_state["current_phase"] == "trajectory_forecasting_completed"
    traj = final_state["disease_trajectory"]
    assert traj is not None
    assert len(traj["horizons"]) == 3
    assert any("Acute Coronary" in w["condition_name"] for w in traj["preserved_safety_warnings"])
    assert "NOT an established clinical diagnosis" in traj["decision_support_disclaimer"]
