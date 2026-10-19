"""Integration tests for Clinical Risk API Endpoints (/api/v1/risk)."""

import pytest
from fastapi.testclient import TestClient

from app.core.security import create_access_token
from app.database.models import User
from app.database.repositories import UserRepository


def _create_authenticated_user(db_session, email: str = "risk_user@example.com") -> tuple[User, dict]:
    """Helper to seed a test user and generate Bearer authorization headers."""
    user_repo = UserRepository(db_session)
    user = user_repo.create(
        email=email,
        hashed_password="hashed_dummy_pw",
        full_name="Risk Test User",
    )
    token = create_access_token(subject=user.id)
    headers = {"Authorization": f"Bearer {token}"}
    return user, headers


def test_unauthenticated_requests_rejected(client: TestClient):
    """All risk endpoints must reject unauthenticated requests with 401."""
    cvd_payload = {
        "age": 55,
        "gender": "male",
        "total_cholesterol_mg_dl": 220,
        "hdl_cholesterol_mg_dl": 45,
        "systolic_bp": 135,
    }
    res = client.post("/api/v1/risk/cardiovascular", json=cvd_payload)
    assert res.status_code == 401

    diabetes_payload = {
        "age": 50,
        "gender": "male",
        "bmi": 26.5,
        "waist_circumference_cm": 92.0,
        "daily_physical_activity_30min": True,
        "daily_vegetable_fruit_intake": True,
        "takes_antihypertensive_meds": False,
        "history_of_high_blood_glucose": False,
        "family_history_of_diabetes": "none",
    }
    res = client.post("/api/v1/risk/diabetes", json=diabetes_payload)
    assert res.status_code == 401

    kidney_payload = {
        "serum_creatinine_mg_dl": 1.0,
        "age": 45,
        "gender": "male",
    }
    res = client.post("/api/v1/risk/kidney", json=kidney_payload)
    assert res.status_code == 401


def test_cardiovascular_risk_endpoint(client: TestClient, db_session):
    """POST /api/v1/risk/cardiovascular computes Framingham 10-year score."""
    _, headers = _create_authenticated_user(db_session, "cvd_user@example.com")

    payload = {
        "age": 55,
        "gender": "male",
        "total_cholesterol_mg_dl": 220.0,
        "hdl_cholesterol_mg_dl": 42.0,
        "systolic_bp": 140.0,
        "is_treated_for_hypertension": True,
        "is_smoker": True,
        "has_diabetes": False,
    }

    res = client.post("/api/v1/risk/cardiovascular", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "Framingham 10-Year General Cardiovascular Risk" in data["model"]
    assert data["risk_score_percent"] > 0
    assert data["risk_category"] in ["low", "moderate", "high"]
    assert "disclaimer" in data


def test_diabetes_risk_endpoint(client: TestClient, db_session):
    """POST /api/v1/risk/diabetes calculates FINDRISC score."""
    _, headers = _create_authenticated_user(db_session, "diabetes_user@example.com")

    payload = {
        "age": 52,
        "gender": "female",
        "bmi": 28.4,
        "waist_circumference_cm": 86.0,
        "daily_physical_activity_30min": False,
        "daily_vegetable_fruit_intake": True,
        "takes_antihypertensive_meds": True,
        "history_of_high_blood_glucose": False,
        "family_history_of_diabetes": "second_degree",
    }

    res = client.post("/api/v1/risk/diabetes", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "FINDRISC" in data["model"]
    assert 0 <= data["total_score"] <= 26
    assert data["risk_category"] in ["low", "slightly_elevated", "moderate", "high", "very_high"]
    assert data["points_breakdown"]["hypertension_meds"] == 2
    assert "disclaimer" in data


def test_kidney_risk_endpoint(client: TestClient, db_session):
    """POST /api/v1/risk/kidney calculates race-free CKD-EPI 2021 eGFR."""
    _, headers = _create_authenticated_user(db_session, "kidney_user@example.com")

    payload = {
        "serum_creatinine_mg_dl": 1.2,
        "age": 60,
        "gender": "male",
    }

    res = client.post("/api/v1/risk/kidney", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "CKD-EPI 2021" in data["model"]
    assert data["egfr_ml_min_1_73m2"] > 0
    assert data["kdigo_stage"] in ["G1", "G2", "G3a", "G3b", "G4", "G5"]
    assert "disclaimer" in data


def test_risk_validation_errors(client: TestClient, db_session):
    """Invalid input values should return HTTP 422 with validation errors."""
    _, headers = _create_authenticated_user(db_session, "validation_user@example.com")

    # Invalid gender and out of range age
    res = client.post(
        "/api/v1/risk/cardiovascular",
        json={"age": 10, "gender": "unknown", "total_cholesterol_mg_dl": 200, "hdl_cholesterol_mg_dl": 50, "systolic_bp": 120},
        headers=headers,
    )
    assert res.status_code == 422
