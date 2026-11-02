"""Integration tests for Consensus & Multi-Agent Debate APIs (/api/v1/consensus).

Validates:
1. POST /api/v1/consensus/contradictions/test (Sub-Step 12.1)
   - 401 Unauthorized rejection for missing credentials
   - 200 OK with detected multi-agent contradictions and targeted challenges
   - 200 OK with fully concordant clinical inputs (0 contradictions, 0.0 doubt)
   - Proper response schema serialization and latency tracking
"""

import pytest
from fastapi.testclient import TestClient

from app.core.security import create_access_token
from app.database.models import User
from app.database.repositories import UserRepository


def _create_authenticated_doctor(db_session, email: str = "doctor_consensus@example.com") -> tuple[User, dict]:
    """Helper to seed a test clinician and generate Bearer authorization headers."""
    user_repo = UserRepository(db_session)
    user = user_repo.create(
        email=email,
        hashed_password="hashed_test_password",
        full_name="Dr. Consensus Specialist",
    )
    token = create_access_token(subject=user.id)
    headers = {"Authorization": f"Bearer {token}"}
    return user, headers


def test_unauthenticated_contradiction_test_rejected(client: TestClient) -> None:
    """POST /api/v1/consensus/contradictions/test must reject unauthenticated requests with 401."""
    res = client.post(
        "/api/v1/consensus/contradictions/test",
        json={"symptoms_data": {"symptoms": ["chest_pain"], "severity": 8}},
    )
    assert res.status_code == 401


def test_authenticated_contradiction_test_default_payload(client: TestClient, db_session) -> None:
    """POST /api/v1/consensus/contradictions/test with default payload detects multi-agent contradictions."""
    _, headers = _create_authenticated_doctor(db_session, email="dr_eval_1@example.com")

    # Use default request payload by sending empty JSON object
    res = client.post(
        "/api/v1/consensus/contradictions/test",
        json={},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()

    assert data["status"] == "success"
    assert data["execution_time_ms"] >= 0.0

    result = data["result"]
    assert result["contradictions_detected"] is True
    assert result["total_contradictions"] >= 3
    assert result["critical_count"] >= 1
    assert result["preliminary_epistemic_doubt"] > 0.0
    assert len(result["issues"]) >= 3

    # Check issue IDs present in default scenario:
    # 1. Acute chest pain + palpitations vs normal troponin & ECG -> ISSUE-SUBJ-OBJ-001
    # 2. Atorvastatin vs LDL 195 -> ISSUE-MED-BIO-001
    # 3. Lisinopril vs BP 154/96 -> ISSUE-MED-BIO-002
    # 4. Framingham 14.5% vs ML CVD 45.2% (gap 30.7%) -> ISSUE-EQ-ML-001
    issue_ids = [issue["issue_id"] for issue in result["issues"]]
    assert "ISSUE-SUBJ-OBJ-001" in issue_ids
    assert "ISSUE-MED-BIO-001" in issue_ids
    assert "ISSUE-EQ-ML-001" in issue_ids

    # Verify structured fields of a critical issue
    cardiac_issue = next(i for i in result["issues"] if i["issue_id"] == "ISSUE-SUBJ-OBJ-001")
    assert cardiac_issue["category"] == "subjective_vs_objective"
    assert cardiac_issue["severity"] == "critical"
    assert "Symptom Analysis Specialist" in cardiac_issue["conflicting_agents"]
    assert "Laboratory Biomarker Specialist" in cardiac_issue["conflicting_agents"]
    assert len(cardiac_issue["suggested_challenge"]) > 10
    assert "troponin" in cardiac_issue["physiological_rationale"].lower()


def test_authenticated_contradiction_test_concordant_scenario(client: TestClient, db_session) -> None:
    """POST /api/v1/consensus/contradictions/test returns concordant result when no contradictions exist."""
    _, headers = _create_authenticated_doctor(db_session, email="dr_eval_2@example.com")

    payload = {
        "symptoms_data": {
            "symptoms": ["mild_fatigue"],
            "severity": 3,
            "duration_days": 1,
            "notes": "Mild non-specific fatigue after work.",
        },
        "medical_history_data": {
            "chronic_conditions": [],
            "current_medications": [],
        },
        "laboratory_data": {
            "systolic_bp": 118.0,
            "diastolic_bp": 76.0,
            "total_cholesterol_mg_dl": 180.0,
            "ldl_cholesterol_mg_dl": 95.0,
            "hdl_cholesterol_mg_dl": 55.0,
            "fasting_blood_glucose_mg_dl": 88.0,
            "hba1c_percent": 5.1,
            "cardiac_troponin_ng_ml": 0.005,
            "resting_ecg": "normal_sinus_rhythm",
        },
        "clinical_scores": {
            "framingham_risk_percent": 3.8,
            "framingham_risk_category": "low",
            "findrisc_score": 3,
            "findrisc_risk_category": "low",
        },
        "ml_predictions": {
            "cardiovascular_risk_percent": 5.2,
            "cardiovascular_risk_category": "low",
            "diabetes_risk_percent": 4.1,
            "diabetes_risk_category": "low",
        },
    }

    res = client.post(
        "/api/v1/consensus/contradictions/test",
        json=payload,
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()

    result = data["result"]
    assert result["contradictions_detected"] is False
    assert result["total_contradictions"] == 0
    assert result["critical_count"] == 0
    assert result["preliminary_epistemic_doubt"] == 0.0
    assert "Concordant" in result["summary"]


def test_authenticated_contradiction_test_undiagnosed_diabetes(client: TestClient, db_session) -> None:
    """POST /api/v1/consensus/contradictions/test detects undiagnosed diabetes (Rule B4)."""
    _, headers = _create_authenticated_doctor(db_session, email="dr_eval_3@example.com")

    payload = {
        "symptoms_data": {"symptoms": ["fatigue"], "severity": 4},
        "medical_history_data": {
            "chronic_conditions": ["hypertension"],  # denies diabetes
            "current_medications": [],
        },
        "laboratory_data": {
            "fasting_blood_glucose_mg_dl": 158.0,
            "hba1c_percent": 8.2,
        },
    }

    res = client.post(
        "/api/v1/consensus/contradictions/test",
        json=payload,
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()

    result = data["result"]
    assert result["contradictions_detected"] is True
    assert any(i["issue_id"] == "ISSUE-MED-BIO-004" for i in result["issues"])
    issue = next(i for i in result["issues"] if i["issue_id"] == "ISSUE-MED-BIO-004")
    assert issue["severity"] == "critical"
    assert "undiagnosed" in issue["physiological_rationale"].lower()
