"""Integration tests for Disease Trajectory Forecasting APIs (/api/v1/trajectory)."""

from datetime import date
from fastapi.testclient import TestClient

from app.core.security import create_access_token
from app.database.repositories import LabResultRepository, UserRepository


def _create_auth_user(db_session, email: str) -> tuple[str, dict]:
    user = UserRepository(db_session).create(
        email=email,
        hashed_password="hashed_password_placeholder",
        full_name="Test Patient",
    )
    token = create_access_token(subject=user.id)
    return user.id, {"Authorization": f"Bearer {token}"}


def test_trajectory_api_requires_authentication(client: TestClient) -> None:
    """Unauthenticated requests to /api/v1/trajectory/forecast must return 401."""
    res = client.post("/api/v1/trajectory/forecast", json={})
    assert res.status_code == 401


def test_trajectory_forecast_persistence_retrieval_comparison_and_observation(
    client: TestClient,
    db_session,
) -> None:
    """Verify end-to-end DB lab loading, forecast persistence, history, comparison, and outcome recording."""
    user_id, headers = _create_auth_user(db_session, "traj_patient_a@example.com")
    lab_repo = LabResultRepository(db_session)
    lab_repo.create(
        user_id=user_id,
        test_date=date(2026, 1, 10),
        biomarkers={"systolic_bp": 135.0, "hba1c_percent": 6.5},
    )
    lab_repo.create(
        user_id=user_id,
        test_date=date(2026, 2, 20),
        biomarkers={"systolic_bp": 148.0, "hba1c_percent": 7.1},
    )

    # 1. Generate first forecast from DB longitudinal history
    res1 = client.post(
        "/api/v1/trajectory/forecast",
        headers=headers,
        json={"current_risk_percent": 18.0, "horizons_days": [30, 180, 365]},
    )
    assert res1.status_code == 200
    body1 = res1.json()
    assert body1["persisted"] is True
    fc1_id = body1["forecast"]["forecast_id"]
    assert body1["forecast"]["overall_direction"] == "worsening"
    assert body1["forecast"]["longitudinal_summary"]["total_lab_visits"] == 2

    # 2. Generate second forecast with improving override
    res2 = client.post(
        "/api/v1/trajectory/forecast",
        headers=headers,
        json={
            "current_risk_percent": 15.0,
            "lab_history": [
                {"id": "x1", "test_date": "2026-01-10", "biomarkers": {"systolic_bp": 150.0}},
                {"id": "x2", "test_date": "2026-03-10", "biomarkers": {"systolic_bp": 128.0}},
            ],
        },
    )
    assert res2.status_code == 200
    fc2_id = res2.json()["forecast"]["forecast_id"]

    # 3. History & retrieval
    hist_res = client.get("/api/v1/trajectory/history", headers=headers)
    assert hist_res.status_code == 200
    assert len(hist_res.json()) == 2

    get_res = client.get(f"/api/v1/trajectory/{fc1_id}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["forecast_id"] == fc1_id

    # 4. Compare successive forecasts
    cmp_res = client.get(f"/api/v1/trajectory/compare/{fc1_id}/{fc2_id}", headers=headers)
    assert cmp_res.status_code == 200
    cmp_body = cmp_res.json()
    assert len(cmp_body["horizon_deltas"]) == 3
    assert "worsening -> improving" in cmp_body["direction_shift"]

    # 5. Record subsequent ground-truth observation
    obs_res = client.post(
        f"/api/v1/trajectory/{fc1_id}/observations",
        headers=headers,
        json={
            "actual_outcome_label": 1,
            "observed_risk_percent": 21.5,
            "observed_biomarkers": {"systolic_bp": 154.0},
            "notes": "Follow-up visit confirmed BP progression.",
        },
    )
    assert obs_res.status_code == 201
    assert obs_res.json()["forecast_id"] == fc1_id
    assert obs_res.json()["actual_outcome_label"] == 1


def test_trajectory_tenant_isolation_forbidden(client: TestClient, db_session) -> None:
    """User B must receive 403 Forbidden when accessing or modifying User A's forecasts."""
    _, headers_a = _create_auth_user(db_session, "traj_owner@example.com")
    _, headers_b = _create_auth_user(db_session, "traj_intruder@example.com")

    res_a = client.post(
        "/api/v1/trajectory/forecast",
        headers=headers_a,
        json={"current_risk_percent": 12.0},
    )
    assert res_a.status_code == 200
    fc_a_id = res_a.json()["forecast"]["forecast_id"]

    assert client.get(f"/api/v1/trajectory/{fc_a_id}", headers=headers_b).status_code == 403
    assert (
        client.post(
            f"/api/v1/trajectory/{fc_a_id}/observations",
            headers=headers_b,
            json={"actual_outcome_label": 0},
        ).status_code
        == 403
    )
