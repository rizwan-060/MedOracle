"""Integration tests for Real-Time Machine Learning Prediction APIs (/api/v1/predictions)."""

import pytest
from fastapi.testclient import TestClient

from app.core.security import create_access_token
from app.database.models import User
from app.database.repositories import UserRepository


def _create_authenticated_user(db_session, email: str = "ml_test_user@example.com") -> tuple[User, dict]:
    """Helper to seed a test user and generate Bearer authorization headers."""
    user_repo = UserRepository(db_session)
    user = user_repo.create(
        email=email,
        hashed_password="hashed_dummy_pw",
        full_name="ML Test Clinician",
    )
    token = create_access_token(subject=user.id)
    headers = {"Authorization": f"Bearer {token}"}
    return user, headers


def test_unauthenticated_predictions_rejected(client: TestClient):
    """All prediction and feedback endpoints must reject unauthenticated requests with 401."""
    cardio_payload = {
        "age": 63,
        "sex": 1,
        "cp": 3,
        "trestbps": 145.0,
        "chol": 233.0,
        "fbs": 1,
        "restecg": 0,
        "thalach": 150.0,
        "exang": 0,
        "oldpeak": 2.3,
        "slope": 0,
        "ca": 0,
        "thal": 1,
    }
    res = client.post("/api/v1/predictions/cardiovascular", json=cardio_payload)
    assert res.status_code == 401

    diabetes_payload = {
        "pregnancies": 6,
        "glucose": 148.0,
        "blood_pressure": 72.0,
        "skin_thickness": 35.0,
        "insulin": 0.0,
        "bmi": 33.6,
        "diabetes_pedigree": 0.627,
        "age": 50,
    }
    res = client.post("/api/v1/predictions/diabetes", json=diabetes_payload)
    assert res.status_code == 401

    symptoms_payload = {
        "symptoms": ["chills", "high_fever", "sweating"],
        "top_k": 3,
    }
    res = client.post("/api/v1/predictions/symptoms", json=symptoms_payload)
    assert res.status_code == 401

    feedback_payload = {
        "target_disease": "cardio",
        "features": cardio_payload,
        "ground_truth_label": 0,
    }
    res = client.post("/api/v1/predictions/feedback", json=feedback_payload)
    assert res.status_code == 401


def test_cardiovascular_prediction_endpoint(client: TestClient, db_session):
    """POST /api/v1/predictions/cardiovascular returns calibrated risk predictions."""
    _, headers = _create_authenticated_user(db_session, "cardio_pred_user@example.com")
    payload = {
        "age": 63,
        "sex": 1,
        "cp": 3,
        "trestbps": 145.0,
        "chol": 233.0,
        "fbs": 1,
        "restecg": 0,
        "thalach": 150.0,
        "exang": 0,
        "oldpeak": 2.3,
        "slope": 0,
        "ca": 0,
        "thal": 1,
    }

    res = client.post("/api/v1/predictions/cardiovascular", json=payload, headers=headers)
    assert res.status_code == 200

    data = res.json()
    assert data["model_id"] == "cardiovascular_risk_v1"
    assert "probability" in data
    assert 0.0 <= data["probability"] <= 1.0
    assert data["predicted_class"] in [0, 1]
    assert data["risk_tier"] in ["low", "moderate", "high"]
    assert 50.0 <= data["confidence_score"] <= 100.0
    assert len(data["top_contributing_factors"]) > 0
    assert "disclaimer" in data


def test_cardiovascular_prediction_validation_error(client: TestClient, db_session):
    """POST /api/v1/predictions/cardiovascular rejects out-of-range clinical parameters."""
    _, headers = _create_authenticated_user(db_session, "cardio_val_user@example.com")
    invalid_payload = {
        "age": 10,  # Below minimum ge=18
        "sex": 5,   # Must be 0 or 1
        "cp": 0,
        "trestbps": 120.0,
        "chol": 200.0,
        "thalach": 140.0,
    }
    res = client.post("/api/v1/predictions/cardiovascular", json=invalid_payload, headers=headers)
    assert res.status_code == 422


def test_diabetes_prediction_endpoint(client: TestClient, db_session):
    """POST /api/v1/predictions/diabetes returns calibrated Type 2 diabetes risk."""
    _, headers = _create_authenticated_user(db_session, "diabetes_pred_user@example.com")
    payload = {
        "pregnancies": 6,
        "glucose": 148.0,
        "blood_pressure": 72.0,
        "skin_thickness": 35.0,
        "insulin": 0.0,
        "bmi": 33.6,
        "diabetes_pedigree": 0.627,
        "age": 50,
    }

    res = client.post("/api/v1/predictions/diabetes", json=payload, headers=headers)
    assert res.status_code == 200

    data = res.json()
    assert data["model_id"] == "diabetes_risk_v1"
    assert 0.0 <= data["probability"] <= 1.0
    assert data["predicted_class"] in [0, 1]
    assert data["risk_tier"] in ["low", "moderate", "high"]
    assert 50.0 <= data["confidence_score"] <= 100.0
    assert len(data["top_contributing_factors"]) > 0
    assert "disclaimer" in data


def test_diabetes_prediction_validation_error(client: TestClient, db_session):
    """POST /api/v1/predictions/diabetes rejects invalid demographic/biomarker values."""
    _, headers = _create_authenticated_user(db_session, "diabetes_val_user@example.com")
    invalid_payload = {
        "glucose": -50.0,  # Negative glucose impossible
        "blood_pressure": 72.0,
        "bmi": 30.0,
        "diabetes_pedigree": 0.5,
        "age": 40,
    }
    res = client.post("/api/v1/predictions/diabetes", json=invalid_payload, headers=headers)
    assert res.status_code == 422


def test_symptom_differential_endpoint(client: TestClient, db_session):
    """POST /api/v1/predictions/symptoms returns ranked differential diagnosis."""
    _, headers = _create_authenticated_user(db_session, "symptoms_pred_user@example.com")
    payload = {
        "symptoms": ["chills", "high_fever", "sweating", "headache", "nausea"],
        "top_k": 3,
    }

    res = client.post("/api/v1/predictions/symptoms", json=payload, headers=headers)
    assert res.status_code == 200

    data = res.json()
    assert data["model_id"] == "symptoms_disease_v1"
    assert len(data["top_candidates"]) == 3
    assert data["top_candidates"][0]["rank"] == 1
    assert data["top_candidates"][0]["disease"] == "Malaria"
    assert data["top_candidates"][0]["probability"] > 0.8
    assert len(data["detected_symptoms"]) == 5
    assert len(data["unrecognized_symptoms"]) == 0
    assert "disclaimer" in data


def test_symptom_differential_partial_unrecognized(client: TestClient, db_session):
    """POST /api/v1/predictions/symptoms identifies unmatched tokens while proceeding with recognized symptoms."""
    _, headers = _create_authenticated_user(db_session, "symptoms_partial_user@example.com")
    payload = {
        "symptoms": ["chills", "high_fever", "extraterrestrial_fatigue_syndrome"],
        "top_k": 2,
    }

    res = client.post("/api/v1/predictions/symptoms", json=payload, headers=headers)
    assert res.status_code == 200

    data = res.json()
    assert len(data["top_candidates"]) == 2
    assert "chills" in data["detected_symptoms"]
    assert "high_fever" in data["detected_symptoms"]
    assert "extraterrestrial_fatigue_syndrome" in data["unrecognized_symptoms"]


def test_symptom_differential_all_unrecognized(client: TestClient, db_session):
    """POST /api/v1/predictions/symptoms returns 422 when zero tokens match ontology."""
    _, headers = _create_authenticated_user(db_session, "symptoms_none_user@example.com")
    payload = {
        "symptoms": ["totally_fake_symptom_123", "nonexistent_condition_abc"],
    }
    res = client.post("/api/v1/predictions/symptoms", json=payload, headers=headers)
    assert res.status_code == 422


def test_prediction_feedback_endpoint(client: TestClient, db_session):
    """POST /api/v1/predictions/feedback queues confirmed feedback into active learning buffer."""
    _, headers = _create_authenticated_user(db_session, "feedback_user@example.com")
    payload = {
        "target_disease": "cardio",
        "features": {
            "age": 60,
            "sex": 1,
            "cp": 2,
            "trestbps": 140.0,
            "chol": 250.0,
            "fbs": 0,
            "restecg": 1,
            "thalach": 145.0,
            "exang": 1,
            "oldpeak": 1.5,
            "slope": 1,
            "ca": 1,
            "thal": 2,
        },
        "ground_truth_label": 1,
        "confidence_at_prediction": 78.5,
        "notes": "Coronary angiography confirmed 75% LAD stenosis.",
    }

    res = client.post("/api/v1/predictions/feedback", json=payload, headers=headers)
    assert res.status_code == 201

    data = res.json()
    assert "sample_id" in data
    assert data["target_disease"] == "cardio"
    assert data["status"] == "recorded"


def test_predict_current_patient_assessment_unauthenticated(client: TestClient):
    """POST /api/v1/predictions/patient/me rejects unauthenticated callers with 401."""
    res = client.post("/api/v1/predictions/patient/me")
    assert res.status_code == 401


def test_predict_current_patient_assessment_with_full_records(client: TestClient, db_session):
    """POST /api/v1/predictions/patient/me extracts stored patient profile, labs, and symptoms to predict."""
    from datetime import date
    from app.database.repositories import (
        LabResultRepository,
        PatientProfileRepository,
        SymptomReportRepository,
    )

    user, headers = _create_authenticated_user(db_session, "patient_assessment_user@example.com")

    # 1. Seed patient profile
    profile_repo = PatientProfileRepository(db_session)
    profile_repo.create_or_update(
        user_id=user.id,
        date_of_birth=date(1975, 4, 12),
        gender="male",
        height_cm=175.0,
        weight_kg=82.0,
        smoking_status="current_smoker",
    )

    # 2. Seed lab results
    lab_repo = LabResultRepository(db_session)
    lab_repo.create(
        user_id=user.id,
        test_date=date(2026, 10, 1),
        lab_name="Central Clinical Lab",
        biomarkers={
            "total_cholesterol": 245.0,
            "fasting_glucose": 155.0,
            "resting_blood_pressure": 138.0,
            "diastolic_bp": 84.0,
            "max_heart_rate": 142.0,
        },
    )

    # 3. Seed symptom report
    symptom_repo = SymptomReportRepository(db_session)
    symptom_repo.create(
        user_id=user.id,
        reported_text="Periodic high fever with severe chills and sweating.",
        structured_symptoms=["chills", "high_fever", "sweating", "headache", "nausea"],
    )

    # 4. Trigger patient prediction
    res = client.post("/api/v1/predictions/patient/me", headers=headers)
    assert res.status_code == 200

    data = res.json()
    assert data["user_id"] == user.id
    assert data["patient_gender"] == "male"
    assert data["patient_age"] > 40
    assert "cardiovascular" in data
    assert 0.0 <= data["cardiovascular"]["probability"] <= 1.0
    assert "diabetes" in data
    assert 0.0 <= data["diabetes"]["probability"] <= 1.0
    assert data["differential_diagnosis"] is not None
    assert len(data["differential_diagnosis"]["top_candidates"]) > 0
    assert data["differential_diagnosis"]["top_candidates"][0]["disease"] == "Malaria"
    assert "clinical_summary" in data
    assert len(data["clinical_summary"]) > 20


def test_predict_current_patient_assessment_empty_profile_fallbacks(client: TestClient, db_session):
    """POST /api/v1/predictions/patient/me handles unpopulated profiles using safe defaults and reports missing items."""
    user, headers = _create_authenticated_user(db_session, "empty_patient_user@example.com")

    res = client.post("/api/v1/predictions/patient/me", headers=headers)
    assert res.status_code == 200

    data = res.json()
    assert data["user_id"] == user.id
    assert len(data["imputed_or_defaulted_parameters"]) > 0
    assert data["differential_diagnosis"] is None
    assert "clinical_summary" in data
