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
