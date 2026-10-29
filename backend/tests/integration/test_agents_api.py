"""Integration tests for Domain Agents APIs (/api/v1/agents)."""

import pytest
from fastapi.testclient import TestClient

from app.core.security import create_access_token
from app.database.models import User
from app.database.repositories import UserRepository


def _create_authenticated_doctor(db_session, email: str = "doctor_agents@example.com") -> tuple[User, dict]:
    """Helper to seed a test clinician and generate Bearer authorization headers."""
    user_repo = UserRepository(db_session)
    user = user_repo.create(
        email=email,
        hashed_password="hashed_test_password",
        full_name="Dr. Multi-Agent Reviewer",
    )
    token = create_access_token(subject=user.id)
    headers = {"Authorization": f"Bearer {token}"}
    return user, headers


def test_unauthenticated_symptom_agent_rejected(client: TestClient):
    """POST /api/v1/agents/symptom/test must reject unauthenticated calls with 401."""
    res = client.post(
        "/api/v1/agents/symptom/test",
        json={"symptoms": ["chest_pain"], "severity": 8},
    )
    assert res.status_code == 401


def test_authenticated_symptom_agent_success(client: TestClient, db_session):
    """POST /api/v1/agents/symptom/test executes SymptomAgent with NLP & ML differential enrichment."""
    _, headers = _create_authenticated_doctor(db_session)

    payload = {
        "symptoms": ["chest_pain", "breathlessness"],
        "severity": 8,
        "duration_days": 3,
        "notes": "Patient complains of heaviness in chest, denies fever or cough.",
        "age": 62,
        "sex": "male",
        "provider": "mock",
        "use_cache": True,
    }

    # 1. Execution (Cache miss)
    res = client.post("/api/v1/agents/symptom/test", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert data["agent_role"] == "Symptom Analysis Specialist"
    assert "findings" in data and len(data["findings"]) > 0
    assert 0.0 <= data["confidence"] <= 100.0
    assert len(data["reasoning_chain"]) > 0
    assert len(data["evidence"]) > 0
    assert len(data["challenges"]) > 0
    assert data["metadata_payload"]["provider_used"] == "mock"
    assert data["metadata_payload"]["cached"] is False

    # 2. Execution with identical payload (Cache hit)
    res2 = client.post("/api/v1/agents/symptom/test", json=payload, headers=headers)
    assert res2.status_code == 200
    data2 = res2.json()

    assert data2["metadata_payload"]["cached"] is True
    assert data2["metadata_payload"]["latency_ms"] == 0.0
    assert data2["findings"] == data["findings"]
    assert data2["confidence"] == data["confidence"]


def test_symptom_agent_validation_bounds(client: TestClient, db_session):
    """POST /api/v1/agents/symptom/test validates severity bounds (1 to 10)."""
    _, headers = _create_authenticated_doctor(db_session)

    # Severity 15 exceeds le=10
    res = client.post(
        "/api/v1/agents/symptom/test",
        json={"symptoms": ["fatigue"], "severity": 15},
        headers=headers,
    )
    assert res.status_code == 422


def test_unauthenticated_medical_history_agent_rejected(client: TestClient):
    """POST /api/v1/agents/medical-history/test must reject unauthenticated requests with 401."""
    res = client.post(
        "/api/v1/agents/medical-history/test",
        json={"chronic_conditions": ["hypertension"]},
    )
    assert res.status_code == 401


def test_authenticated_medical_history_agent_success(client: TestClient, db_session):
    """POST /api/v1/agents/medical-history/test executes MedicalHistoryAgent and verifies caching."""
    _, headers = _create_authenticated_doctor(db_session, email="dr_history@example.com")

    payload = {
        "chronic_conditions": ["hypertension", "type_2_diabetes", "hyperlipidemia"],
        "current_medications": [
            {"name": "Metformin", "dosage": "500mg", "frequency": "twice daily"},
            {"name": "Lisinopril", "dosage": "10mg", "frequency": "once daily"},
        ],
        "family_history": [
            {"relative": "father", "condition": "myocardial_infarction", "age_at_onset": 50},
        ],
        "past_surgeries": ["cholecystectomy (2018)"],
        "allergies": ["penicillin"],
        "smoking_status": "current_smoker",
        "activity_level": "sedentary",
        "notes": "Patient reports poor diet and missed doses of Lisinopril.",
        "age": 57,
        "sex": "male",
        "active_symptoms": ["chest_tightness"],
        "provider": "mock",
        "use_cache": True,
    }

    # 1. Execution (Cache miss)
    res = client.post("/api/v1/agents/medical-history/test", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert data["agent_role"] == "Medical History Specialist"
    assert "findings" in data and len(data["findings"]) > 0
    assert 0.0 <= data["confidence"] <= 100.0
    assert len(data["reasoning_chain"]) > 0
    assert len(data["evidence"]) > 0
    assert len(data["challenges"]) > 0
    assert data["metadata_payload"]["provider_used"] == "mock"
    assert data["metadata_payload"]["cached"] is False

    # 2. Execution with identical payload (Cache hit)
    res2 = client.post("/api/v1/agents/medical-history/test", json=payload, headers=headers)
    assert res2.status_code == 200
    data2 = res2.json()

    assert data2["metadata_payload"]["cached"] is True
    assert data2["metadata_payload"]["latency_ms"] == 0.0
    assert data2["findings"] == data["findings"]
    assert data2["confidence"] == data["confidence"]


def test_authenticated_medical_history_agent_empty_history_graceful(client: TestClient, db_session):
    """POST /api/v1/agents/medical-history/test handles empty/unavailable history under epistemic uncertainty."""
    _, headers = _create_authenticated_doctor(db_session, email="dr_empty_history@example.com")

    payload = {
        "chronic_conditions": [],
        "current_medications": [],
        "family_history": [],
        "past_surgeries": [],
        "allergies": [],
        "smoking_status": None,
        "activity_level": None,
        "notes": None,
        "age": 45,
        "sex": "female",
        "provider": "mock",
        "use_cache": False,
    }

    res = client.post("/api/v1/agents/medical-history/test", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert data["agent_role"] == "Medical History Specialist"
    assert data["confidence"] <= 45.0
    assert any("surveillance gap" in ev.lower() or "no prior" in ev.lower() for ev in data["evidence"])
    assert any("baseline" in ch.lower() or "intake" in ch.lower() for ch in data["challenges"])


def test_unauthenticated_laboratory_agent_rejected(client: TestClient):
    """POST /api/v1/agents/laboratory/test must reject unauthenticated requests with 401."""
    res = client.post(
        "/api/v1/agents/laboratory/test",
        json={"systolic_bp": 130.0},
    )
    assert res.status_code == 401


def test_authenticated_laboratory_agent_success(client: TestClient, db_session):
    """POST /api/v1/agents/laboratory/test executes LaboratoryAgent and verifies caching."""
    _, headers = _create_authenticated_doctor(db_session, email="dr_lab@example.com")

    payload = {
        "systolic_bp": 142.0,
        "diastolic_bp": 88.0,
        "total_cholesterol_mg_dl": 225.0,
        "hdl_cholesterol_mg_dl": 38.0,
        "ldl_cholesterol_mg_dl": 145.0,
        "triglycerides_mg_dl": 210.0,
        "fasting_blood_glucose_mg_dl": 138.0,
        "hba1c_percent": 7.4,
        "serum_creatinine_mg_dl": 1.1,
        "estimated_gfr": 72.0,
        "test_date": "2026-10-15",
        "age": 58,
        "sex": "male",
        "provider": "mock",
        "use_cache": True,
    }

    # 1. Execution (Cache miss)
    res = client.post("/api/v1/agents/laboratory/test", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert data["agent_role"] == "Laboratory Biomarker Specialist"
    assert "findings" in data and len(data["findings"]) > 0
    assert 0.0 <= data["confidence"] <= 100.0
    assert len(data["reasoning_chain"]) > 0
    assert len(data["evidence"]) > 0
    assert len(data["challenges"]) > 0
    assert data["metadata_payload"]["provider_used"] == "mock"
    assert data["metadata_payload"]["cached"] is False

    # 2. Execution with identical payload (Cache hit)
    res2 = client.post("/api/v1/agents/laboratory/test", json=payload, headers=headers)
    assert res2.status_code == 200
    data2 = res2.json()

    assert data2["metadata_payload"]["cached"] is True
    assert data2["metadata_payload"]["latency_ms"] == 0.0
    assert data2["findings"] == data["findings"]
    assert data2["confidence"] == data["confidence"]


def test_authenticated_laboratory_agent_empty_labs_graceful(client: TestClient, db_session):
    """POST /api/v1/agents/laboratory/test handles empty/unrecorded labs under epistemic uncertainty."""
    _, headers = _create_authenticated_doctor(db_session, email="dr_empty_labs@example.com")

    payload = {
        "systolic_bp": None,
        "diastolic_bp": None,
        "total_cholesterol_mg_dl": None,
        "hdl_cholesterol_mg_dl": None,
        "ldl_cholesterol_mg_dl": None,
        "triglycerides_mg_dl": None,
        "fasting_blood_glucose_mg_dl": None,
        "hba1c_percent": None,
        "serum_creatinine_mg_dl": None,
        "estimated_gfr": None,
        "age": 50,
        "sex": "female",
        "provider": "mock",
        "use_cache": False,
    }

    res = client.post("/api/v1/agents/laboratory/test", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert data["agent_role"] == "Laboratory Biomarker Specialist"
    assert data["confidence"] <= 40.0
    assert any("objective data gap" in ev.lower() or "no objective" in ev.lower() for ev in data["evidence"])
    assert any("requisition" in ch.lower() or "order" in ch.lower() for ch in data["challenges"])


def test_laboratory_agent_validation_bounds(client: TestClient, db_session):
    """POST /api/v1/agents/laboratory/test validates numeric bounds."""
    _, headers = _create_authenticated_doctor(db_session, email="dr_bounds@example.com")

    # Systolic BP 350 exceeds le=280
    res = client.post(
        "/api/v1/agents/laboratory/test",
        json={"systolic_bp": 350.0},
        headers=headers,
    )
    assert res.status_code == 422



