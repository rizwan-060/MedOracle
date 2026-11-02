"""Integration tests for Patient Data APIs (Profile, Medical History, Symptoms, Laboratory)."""

import pytest
from fastapi.testclient import TestClient

from app.core.security import create_access_token
from app.database.models import User
from app.database.repositories import UserRepository


def _create_authenticated_user(db_session, email: str = "patient_test@example.com") -> tuple[User, dict]:
    """Helper to seed a test user and generate Bearer authorization headers."""
    user_repo = UserRepository(db_session)
    user = user_repo.create(
        email=email,
        hashed_password="hashed_dummy_pw",
        full_name="Patient Tester",
    )
    token = create_access_token(subject=user.id)
    headers = {"Authorization": f"Bearer {token}"}
    return user, headers


def test_patient_profile_get_and_update(client: TestClient, db_session):
    user, headers = _create_authenticated_user(db_session, "profile_user@example.com")

    # GET default profile (auto-provisioned)
    res_get = client.get("/api/v1/patient/profile", headers=headers)
    assert res_get.status_code == 200
    data = res_get.json()
    assert data["user_id"] == user.id

    # PUT update profile
    update_payload = {
        "gender": "male",
        "height_cm": 178.5,
        "weight_kg": 76.0,
        "smoking_status": "never",
        "activity_level": "moderate",
    }
    res_put = client.put("/api/v1/patient/profile", json=update_payload, headers=headers)
    assert res_put.status_code == 200
    updated_data = res_put.json()
    assert updated_data["gender"] == "male"
    assert updated_data["height_cm"] == 178.5
    assert updated_data["weight_kg"] == 76.0
    assert updated_data["smoking_status"] == "never"
    assert updated_data["activity_level"] == "moderate"


def test_patient_profile_isolation(client: TestClient, db_session):
    user_a, headers_a = _create_authenticated_user(db_session, "user_a@example.com")
    user_b, headers_b = _create_authenticated_user(db_session, "user_b@example.com")

    client.put("/api/v1/patient/profile", json={"gender": "female", "weight_kg": 62.0}, headers=headers_a)
    client.put("/api/v1/patient/profile", json={"gender": "male", "weight_kg": 85.0}, headers=headers_b)

    res_a = client.get("/api/v1/patient/profile", headers=headers_a)
    assert res_a.status_code == 200
    assert res_a.json()["gender"] == "female"
    assert res_a.json()["weight_kg"] == 62.0

    res_b = client.get("/api/v1/patient/profile", headers=headers_b)
    assert res_b.status_code == 200
    assert res_b.json()["gender"] == "male"
    assert res_b.json()["weight_kg"] == 85.0


def test_medical_history_lifecycle_and_isolation(client: TestClient, db_session):
    user_a, headers_a = _create_authenticated_user(db_session, "history_a@example.com")
    user_b, headers_b = _create_authenticated_user(db_session, "history_b@example.com")

    # Initial GET before creation should return 404
    res_init = client.get("/api/v1/medical-history/", headers=headers_a)
    assert res_init.status_code == 404

    # POST create
    payload = {
        "chronic_conditions": ["hypertension"],
        "past_surgeries": ["appendectomy"],
        "current_medications": [{"name": "Lisinopril", "dosage": "10mg"}],
        "allergies": ["penicillin"],
        "family_history": [{"relative": "father", "condition": "type_2_diabetes", "age_at_onset": 55}],
    }
    res_post = client.post("/api/v1/medical-history/", json=payload, headers=headers_a)
    assert res_post.status_code == 201
    created = res_post.json()
    assert created["chronic_conditions"] == ["hypertension"]
    assert created["user_id"] == user_a.id

    # User B should NOT see User A's medical history
    res_b = client.get("/api/v1/medical-history/", headers=headers_b)
    assert res_b.status_code == 404

    # PUT update
    res_put = client.put(
        "/api/v1/medical-history/",
        json={"chronic_conditions": ["hypertension", "dyslipidemia"]},
        headers=headers_a,
    )
    assert res_put.status_code == 200
    assert "dyslipidemia" in res_put.json()["chronic_conditions"]


def test_symptom_reporting_crud_and_tenant_isolation(client: TestClient, db_session):
    user_a, headers_a = _create_authenticated_user(db_session, "symptoms_a@example.com")
    user_b, headers_b = _create_authenticated_user(db_session, "symptoms_b@example.com")

    # POST create report
    symptom_payload = {
        "reported_text": "Severe chest pressure radiating to left shoulder and jaw for 3 days.",
        "duration_days": 3,
        "severity_self_rating": 8,
        "body_locations": ["chest", "left shoulder"],
        "triggers": ["physical exertion"],
        "structured_symptoms": ["chest_pain", "dyspnea"],
    }
    res_create = client.post("/api/v1/symptoms/", json=symptom_payload, headers=headers_a)
    assert res_create.status_code == 201
    report_data = res_create.json()
    report_id = report_data["id"]
    assert report_data["user_id"] == user_a.id
    assert report_data["duration_days"] == 3

    # GET list for user A
    res_list_a = client.get("/api/v1/symptoms/", headers=headers_a)
    assert res_list_a.status_code == 200
    assert len(res_list_a.json()) == 1
    assert res_list_a.json()[0]["id"] == report_id

    # GET list for user B should be empty
    res_list_b = client.get("/api/v1/symptoms/", headers=headers_b)
    assert res_list_b.status_code == 200
    assert len(res_list_b.json()) == 0

    # User B attempting to GET report of User A -> 404
    res_unauth_get = client.get(f"/api/v1/symptoms/{report_id}", headers=headers_b)
    assert res_unauth_get.status_code == 404

    # User B attempting to DELETE report of User A -> 404
    res_unauth_del = client.delete(f"/api/v1/symptoms/{report_id}", headers=headers_b)
    assert res_unauth_del.status_code == 404

    # User A GET single report -> 200
    res_auth_get = client.get(f"/api/v1/symptoms/{report_id}", headers=headers_a)
    assert res_auth_get.status_code == 200
    assert res_auth_get.json()["id"] == report_id

    # User A DELETE report -> 204
    res_auth_del = client.delete(f"/api/v1/symptoms/{report_id}", headers=headers_a)
    assert res_auth_del.status_code == 204

    # GET after delete -> 404
    res_after_del = client.get(f"/api/v1/symptoms/{report_id}", headers=headers_a)
    assert res_after_del.status_code == 404


def test_symptom_validation_errors(client: TestClient, db_session):
    _, headers = _create_authenticated_user(db_session, "symptom_val@example.com")

    # reported_text too short (< 5 chars)
    res = client.post("/api/v1/symptoms/", json={"reported_text": "pain"}, headers=headers)
    assert res.status_code == 422


def test_laboratory_crud_and_tenant_isolation(client: TestClient, db_session):
    user_a, headers_a = _create_authenticated_user(db_session, "lab_a@example.com")
    user_b, headers_b = _create_authenticated_user(db_session, "lab_b@example.com")

    lab_payload = {
        "test_date": "2026-10-10",
        "lab_name": "City Diagnostic Center",
        "biomarkers": {
            "total_cholesterol_mg_dl": 220,
            "hdl_cholesterol_mg_dl": 45,
            "fasting_blood_glucose_mg_dl": 110,
            "serum_creatinine_mg_dl": 1.0,
        },
        "notes": "Fasting sample confirmed.",
    }

    # POST create lab
    res_create = client.post("/api/v1/laboratory/", json=lab_payload, headers=headers_a)
    assert res_create.status_code == 201
    lab_data = res_create.json()
    lab_id = lab_data["id"]
    assert lab_data["user_id"] == user_a.id
    assert lab_data["biomarkers"]["total_cholesterol_mg_dl"] == 220

    # GET latest for user A
    res_latest_a = client.get("/api/v1/laboratory/latest", headers=headers_a)
    assert res_latest_a.status_code == 200
    assert res_latest_a.json()["id"] == lab_id

    # GET latest for user B -> 404
    res_latest_b = client.get("/api/v1/laboratory/latest", headers=headers_b)
    assert res_latest_b.status_code == 404

    # User B attempting to GET lab of user A -> 404
    res_cross_get = client.get(f"/api/v1/laboratory/{lab_id}", headers=headers_b)
    assert res_cross_get.status_code == 404

    # User B attempting to DELETE lab of user A -> 404
    res_cross_del = client.delete(f"/api/v1/laboratory/{lab_id}", headers=headers_b)
    assert res_cross_del.status_code == 404

    # User A lists labs -> 1 record
    res_list_a = client.get("/api/v1/laboratory/", headers=headers_a)
    assert res_list_a.status_code == 200
    assert len(res_list_a.json()) == 1

    # User A deletes lab -> 204
    res_del = client.delete(f"/api/v1/laboratory/{lab_id}", headers=headers_a)
    assert res_del.status_code == 204


def test_patient_endpoints_unauthorized_rejection(client: TestClient):
    endpoints = [
        ("GET", "/api/v1/patient/profile"),
        ("PUT", "/api/v1/patient/profile"),
        ("GET", "/api/v1/medical-history/"),
        ("POST", "/api/v1/medical-history/"),
        ("GET", "/api/v1/symptoms/"),
        ("POST", "/api/v1/symptoms/"),
        ("GET", "/api/v1/laboratory/"),
        ("POST", "/api/v1/laboratory/"),
        ("GET", "/api/v1/laboratory/latest"),
    ]
    for method, path in endpoints:
        if method == "GET":
            res = client.get(path)
        elif method == "POST":
            res = client.post(path, json={})
        elif method == "PUT":
            res = client.put(path, json={})
        assert res.status_code == 401, f"{method} {path} should return 401 Unauthorized"
