"""Integration tests for LLM Router, Diagnostics, and Clinical Testing APIs (/api/v1/llm)."""

import pytest
from fastapi.testclient import TestClient

from app.core.security import create_access_token
from app.database.models import User
from app.database.repositories import UserRepository


def _create_authenticated_doctor(db_session, email: str = "doctor_llm@example.com") -> tuple[User, dict]:
    """Helper to seed a test clinician and generate Bearer authorization headers."""
    user_repo = UserRepository(db_session)
    user = user_repo.create(
        email=email,
        hashed_password="hashed_test_password",
        full_name="Dr. LLM Evaluator",
    )
    token = create_access_token(subject=user.id)
    headers = {"Authorization": f"Bearer {token}"}
    return user, headers


def test_get_llm_status(client: TestClient):
    """GET /api/v1/llm/status returns 200 with operational readiness and caching diagnostics."""
    response = client.get("/api/v1/llm/status")
    assert response.status_code == 200
    data = response.json()

    assert "configured_default" in data
    assert "cache_backend" in data
    assert "cache_enabled" in data
    assert "providers" in data
    assert "mock" in data["providers"]
    assert "groq" in data["providers"]
    assert "gemini" in data["providers"]
    assert data["providers"]["mock"]["available"] is True


def test_unauthenticated_llm_test_rejected(client: TestClient):
    """POST /api/v1/llm/test must reject unauthenticated requests with 401 Unauthorized."""
    response = client.post(
        "/api/v1/llm/test",
        json={"prompt": "Assess patient cardiovascular risk."},
    )
    assert response.status_code == 401


def test_authenticated_llm_test_success_and_caching(client: TestClient, db_session):
    """POST /api/v1/llm/test executes structured clinical completion and caches subsequent identical calls."""
    _, headers = _create_authenticated_doctor(db_session)
    prompt = "Synthesize 10-year CVD risk with elevated LDL (160 mg/dL)."

    # 1. First execution: Cache miss
    res1 = client.post(
        "/api/v1/llm/test",
        json={"prompt": prompt, "temperature": 0.2, "use_cache": True},
        headers=headers,
    )
    assert res1.status_code == 200
    data1 = res1.json()

    assert data1["agent_role"] == "Clinical Risk Evaluator"
    assert "findings" in data1 and len(data1["findings"]) > 0
    assert 0.0 <= data1["confidence"] <= 100.0
    assert len(data1["reasoning_chain"]) > 0
    assert len(data1["evidence"]) > 0
    assert data1["execution_metadata"]["cached"] is False
    assert data1["execution_metadata"]["provider"] == "mock"

    # 2. Second execution with identical prompt: Cache hit
    res2 = client.post(
        "/api/v1/llm/test",
        json={"prompt": prompt, "temperature": 0.2, "use_cache": True},
        headers=headers,
    )
    assert res2.status_code == 200
    data2 = res2.json()

    assert data2["execution_metadata"]["cached"] is True
    assert data2["execution_metadata"]["latency_ms"] == 0.0
    assert data2["findings"] == data1["findings"]
    assert data2["confidence"] == data1["confidence"]
