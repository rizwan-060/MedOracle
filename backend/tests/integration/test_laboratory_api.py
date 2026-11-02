"""Integration tests for Laboratory API endpoints including Step 8.4.3 OCR Biomarker Normalization."""

import pytest
from fastapi.testclient import TestClient

from app.core.security import create_access_token
from app.database.models import User
from app.database.repositories import UserRepository


def _create_authenticated_user(db_session, email: str = "lab_test_clinician@example.com") -> tuple[User, dict]:
    """Helper to seed a test clinician user and generate Bearer authorization headers."""
    user_repo = UserRepository(db_session)
    user = user_repo.create(
        email=email,
        hashed_password="hashed_dummy_pw",
        full_name="Dr. Lab Integrator",
    )
    token = create_access_token(subject=user.id)
    headers = {"Authorization": f"Bearer {token}"}
    return user, headers


def test_normalize_biomarkers_unauthenticated_rejected(client: TestClient):
    """Normalization endpoint must reject unauthenticated requests with HTTP 401."""
    payload = {
        "extracted_items": [
            {"label": "Fasting Blood Glucose", "value": "100.0", "unit": "mg/dL"}
        ]
    }
    res = client.post("/api/v1/laboratory/biomarkers/normalize", json=payload)
    assert res.status_code == 401


def test_normalize_biomarkers_authenticated_batch(client: TestClient, db_session):
    """Authenticated clinicians can normalize OCR-extracted items with full unit conversion and provenance."""
    user, headers = _create_authenticated_user(db_session, email="lab_doc_batch@example.com")

    payload = {
        "patient_id": user.id,
        "source_document_id": "ocr_doc_9901",
        "lab_name": "Aga Khan University Hospital Labs",
        "specimen_collection_date": "2026-11-02T08:30:00Z",
        "extracted_items": [
            {
                "label": "Fasting B.S.",
                "value": "5.55",
                "unit": "mmol/L",
                "reference_range": "3.9 - 5.5 mmol/L",
                "ocr_confidence": 99.0,
            },
            {
                "label": "Cholesterol Tot.",
                "value": "215",
                "unit": "mg/dL",
                "reference_range": "< 200",
                "flag": "H",
                "ocr_confidence": 98.5,
            },
            {
                "label": "S. Creatinine",
                "value": "88.42",
                "unit": "µmol/L",
                "reference_range": "60 - 110 µmol/L",
                "ocr_confidence": 97.0,
            },
            {
                "label": "High-Sensitivity Troponin I",
                "value": "14.5",
                "unit": "ng/L",
                "reference_range": "< 14 ng/L",
                "flag": "H",
                "ocr_confidence": 99.2,
            },
        ],
    }

    res = client.post("/api/v1/laboratory/biomarkers/normalize", json=payload, headers=headers)
    assert res.status_code == 200

    data = res.json()
    assert data["status"] == "success"
    assert data["total_extracted"] == 4
    assert data["normalized_count"] == 4
    assert data["unmapped_count"] == 0
    assert data["ambiguous_count"] == 0

    canon_dict = data["canonical_biomarkers_dict"]
    # Fasting glucose: 5.55 mmol/L * 18.0156 = 99.99 mg/dL
    assert "fasting_blood_glucose_mg_dl" in canon_dict
    assert canon_dict["fasting_blood_glucose_mg_dl"] == pytest.approx(99.99, abs=0.1)

    # Total cholesterol: 215 mg/dL
    assert canon_dict["total_cholesterol_mg_dl"] == 215.0

    # Creatinine: 88.42 µmol/L -> 1.0 mg/dL
    assert canon_dict["serum_creatinine_mg_dl"] == pytest.approx(1.0, abs=0.02)

    # Troponin: 14.5 ng/L -> 0.0145 ng/mL
    assert canon_dict["hs_troponin_i_ng_ml"] == pytest.approx(0.0145, abs=0.0001)

    # Downstream compatibility aliases
    assert canon_dict["cardiac_troponin_ng_ml"] == pytest.approx(0.0145, abs=0.0001)
    assert canon_dict["cardiac_troponin_assay"] == "hs_cTnI"

    # Verify provenance on records
    records = data["records"]
    assert len(records) == 4
    for r in records:
        assert r["patient_id"] == user.id
        assert r["source_document_id"] == "ocr_doc_9901"
        assert r["lab_name"] == "Aga Khan University Hospital Labs"
        assert r["specimen_collection_date"] == "2026-11-02T08:30:00Z"
        assert r["validation_status"] in ["NORMALIZED", "NEEDS_REVIEW"]


def test_normalize_biomarkers_ambiguous_and_unsupported_units(client: TestClient, db_session):
    """Verify unspecific labels and invalid units are explicitly flagged without breaking the batch."""
    user, headers = _create_authenticated_user(db_session, email="lab_doc_ambig@example.com")

    payload = {
        "extracted_items": [
            {
                "label": "Troponin",  # Ambiguous (cannot distinguish I vs T or hs)
                "value": "0.05",
                "unit": "ng/mL",
                "ocr_confidence": 95.0,
            },
            {
                "label": "Serum Sodium",
                "value": "140",
                "unit": "lightyears",  # Dimensionally incompatible
                "ocr_confidence": 95.0,
            },
            {
                "label": "Hepatitis C Antibody",
                "value": "Non-Reactive",  # Qualitative result
                "unit": None,
                "ocr_confidence": 99.0,
            },
        ]
    }

    res = client.post("/api/v1/laboratory/biomarkers/normalize", json=payload, headers=headers)
    assert res.status_code == 200

    data = res.json()
    assert data["total_extracted"] == 3
    assert data["ambiguous_count"] == 1
    assert data["invalid_count"] >= 1

    records = data["records"]
    # 1. Ambiguous Troponin
    troponin_rec = records[0]
    assert troponin_rec["validation_status"] == "AMBIGUOUS_BIOMARKER"
    assert troponin_rec["canonical_id"] is None
    assert any("cannot differentiate" in c.lower() for c in troponin_rec["clinical_caveats"])

    # 2. Unsupported Unit
    sodium_rec = records[1]
    assert sodium_rec["validation_status"] == "UNSUPPORTED_UNIT"
    assert sodium_rec["canonical_id"] == "sodium_mmol_l"

    # 3. Qualitative
    hep_rec = records[2]
    assert hep_rec["validation_status"] == "QUALITATIVE_VALUE"
    assert hep_rec["qualitative_value"] == "Non-Reactive"
    assert hep_rec["normalized_value"] is None  # Must never invent arbitrary floats


def test_laboratory_crud_endpoints(client: TestClient, db_session):
    """Ensure standard laboratory result storage, retrieval, and deletion remain fully functional."""
    user, headers = _create_authenticated_user(db_session, email="lab_crud_user@example.com")

    # 1. Create Lab Result
    create_payload = {
        "test_date": "2026-11-02",
        "lab_name": "National Pathology Services",
        "biomarkers": {
            "fasting_blood_glucose_mg_dl": 98.0,
            "serum_creatinine_mg_dl": 0.95,
            "sodium_mmol_l": 141.0,
            "potassium_mmol_l": 4.2,
        },
        "notes": "Fasting verified for 12 hours.",
    }

    res = client.post("/api/v1/laboratory/", json=create_payload, headers=headers)
    assert res.status_code == 201
    lab_data = res.json()
    lab_id = lab_data["id"]
    assert lab_data["lab_name"] == "National Pathology Services"
    assert lab_data["test_date"] == "2026-11-02"
    assert lab_data["biomarkers"]["fasting_blood_glucose_mg_dl"] == 98.0

    # 2. Retrieve Latest
    res_latest = client.get("/api/v1/laboratory/latest", headers=headers)
    assert res_latest.status_code == 200
    assert res_latest.json()["id"] == lab_id

    # 3. Retrieve by ID
    res_get = client.get(f"/api/v1/laboratory/{lab_id}", headers=headers)
    assert res_get.status_code == 200
    assert res_get.json()["id"] == lab_id

    # 4. List Results
    res_list = client.get("/api/v1/laboratory/", headers=headers)
    assert res_list.status_code == 200
    assert len(res_list.json()) >= 1

    # 5. Delete Result
    res_del = client.delete(f"/api/v1/laboratory/{lab_id}", headers=headers)
    assert res_del.status_code == 204

    # 6. Verify 404 after deletion
    res_after = client.get(f"/api/v1/laboratory/{lab_id}", headers=headers)
    assert res_after.status_code == 404
