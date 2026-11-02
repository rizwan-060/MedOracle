"""Integration tests for LangGraph multi-agent pipeline API (/api/v1/agents/pipeline/test)."""

import pytest
from fastapi.testclient import TestClient

from app.core.security import create_access_token
from app.database.models import User
from app.database.repositories import UserRepository


def _create_authenticated_doctor(db_session, email: str = "dr_graph@example.com") -> tuple[User, dict]:
    """Helper to seed a test clinician and generate Bearer authorization headers."""
    user_repo = UserRepository(db_session)
    user = user_repo.create(
        email=email,
        hashed_password="hashed_test_password",
        full_name="Dr. LangGraph Evaluator",
    )
    token = create_access_token(subject=user.id)
    headers = {"Authorization": f"Bearer {token}"}
    return user, headers


def test_unauthenticated_pipeline_rejected(client: TestClient):
    """POST /api/v1/agents/pipeline/test must reject unauthenticated requests with 401."""
    res = client.post("/api/v1/agents/pipeline/test", json={})
    assert res.status_code == 401


def test_authenticated_pipeline_success(client: TestClient, db_session):
    """POST /api/v1/agents/pipeline/test executes full LangGraph multi-agent workflow."""
    _, headers = _create_authenticated_doctor(db_session)

    payload = {
        "patient_demographics": {"age": 58, "sex": "male"},
        "symptoms_data": {
            "symptoms": ["chest_pain", "breathlessness", "fatigue"],
            "severity": 8,
            "duration_days": 3,
            "notes": "Patient reports substernal chest heaviness, denies fever.",
        },
        "medical_history_data": {
            "chronic_conditions": ["hypertension", "type_2_diabetes"],
            "current_medications": [{"name": "Lisinopril", "dosage": "10mg"}],
            "family_history": [{"relative": "father", "condition": "myocardial_infarction", "age_at_onset": 52}],
            "smoking_status": "current_smoker",
        },
        "laboratory_data": {
            "systolic_bp": 146.0,
            "diastolic_bp": 92.0,
            "total_cholesterol_mg_dl": 228.0,
            "hdl_cholesterol_mg_dl": 38.0,
            "fasting_blood_glucose_mg_dl": 142.0,
            "hba1c_percent": 7.5,
            "estimated_gfr": 74.0,
        },
        "clinical_scores": {
            "framingham_risk_percent": 19.2,
            "framingham_risk_category": "moderate",
            "findrisc_score": 15,
            "findrisc_risk_category": "high",
            "ckd_epi_egfr": 74.0,
        },
        "ml_predictions": {
            "cardiovascular_risk_percent": 26.5,
            "cardiovascular_risk_category": "high",
            "diabetes_risk_percent": 42.0,
            "top_differential_conditions": [
                {"disease": "coronary_artery_disease", "probability": 0.44},
            ],
        },
        "provider": "mock",
        "use_cache": False,
    }

    res = client.post("/api/v1/agents/pipeline/test", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert data["session_id"].startswith("session_")
    assert data["status"] == "completed"
    assert data["current_phase"] == "risk_prediction_completed"
    assert data["completed_at"] is not None

    # Verify agent outputs
    assert len(data["agent_outputs"]) == 4
    roles = [out["agent_role"] for out in data["agent_outputs"]]
    assert "Symptom Analysis Specialist" in roles
    assert "Medical History Specialist" in roles
    assert "Laboratory Biomarker Specialist" in roles
    assert "Risk Prediction Ensemble Specialist" in roles

    # Verify domain-mapped keys
    assert data["symptom_output"] is not None
    assert data["medical_history_output"] is not None
    assert data["laboratory_output"] is not None
    assert data["risk_prediction_output"] is not None
    assert len(data["errors"]) == 0
