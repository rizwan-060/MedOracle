"""Integration tests for Clinical NLP & Dynamic Ontology Expansion APIs (/api/v1/nlp)."""

import pytest
from fastapi.testclient import TestClient

from app.core.security import create_access_token
from app.database.models import User
from app.database.repositories import UserRepository
from app.ml.inference.predictor import RealtimePredictor


@pytest.fixture(autouse=True)
def clean_dynamic_ontology():
    """Ensure dynamic synonyms and unmapped buffer are isolated for tests."""
    predictor = RealtimePredictor.get_instance()
    test_phrase = "pins and needles"
    predictor.nlp_extractor.dynamic_ontology_manager.remove_synonym(test_phrase)
    predictor.nlp_extractor.reload_dynamic_synonyms()
    yield
    predictor.nlp_extractor.dynamic_ontology_manager.remove_synonym(test_phrase)
    predictor.nlp_extractor.reload_dynamic_synonyms()


def _create_authenticated_clinician(db_session, email: str = "clinician_nlp@example.com") -> tuple[User, dict]:
    """Helper to seed a test clinician user and generate Bearer authorization headers."""
    user_repo = UserRepository(db_session)
    user = user_repo.create(
        email=email,
        hashed_password="hashed_test_password",
        full_name="Dr. Clinical NLP",
    )
    token = create_access_token(subject=user.id)
    headers = {"Authorization": f"Bearer {token}"}
    return user, headers


def test_unauthenticated_nlp_endpoints_rejected(client: TestClient):
    """All NLP and ontology expansion endpoints must reject unauthenticated requests with 401."""
    # 1. GET /api/v1/nlp/ontology
    res = client.get("/api/v1/nlp/ontology")
    assert res.status_code == 401

    # 2. GET /api/v1/nlp/unmapped-phrases
    res = client.get("/api/v1/nlp/unmapped-phrases")
    assert res.status_code == 401

    # 3. POST /api/v1/nlp/expand-ontology
    res = client.post(
        "/api/v1/nlp/expand-ontology",
        json={"phrase": "brain zaps", "canonical_symptom": "altered_sensorium"},
    )
    assert res.status_code == 401

    # 4. POST /api/v1/nlp/extract-entities
    res = client.post(
        "/api/v1/nlp/extract-entities",
        json={"narrative": "Patient has severe headache."},
    )
    assert res.status_code == 401


def test_get_ontology_catalog(client: TestClient, db_session):
    """Verifies that the catalog endpoint exposes the 132 benchmark canonical symptoms."""
    _, headers = _create_authenticated_clinician(db_session)
    response = client.get("/api/v1/nlp/ontology", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["total_canonical_symptoms"] == 132
    assert "chest_pain" in data["canonical_symptoms"]
    assert "high_fever" in data["canonical_symptoms"]
    assert "headache" in data["canonical_symptoms"]
    assert data["total_synonyms"] > 100
    assert isinstance(data["dynamic_synonyms"], dict)


def test_extract_clinical_entities_with_negation(client: TestClient, db_session):
    """Verifies entity extraction, typo tolerance, and NegEx negation filtering."""
    _, headers = _create_authenticated_clinician(db_session, email="negex_test@example.com")
    payload = {
        "narrative": "Patient reports severe chest pain and sore throught, but denies high fever and has no chills.",
        "record_unmapped": True,
    }
    response = client.post("/api/v1/nlp/extract-entities", json=payload, headers=headers)

    assert response.status_code == 200
    data = response.json()

    # Positive symptoms
    assert "chest_pain" in data["detected_symptoms"]
    assert "throat_irritation" in data["detected_symptoms"]  # typo 'sore throught' resolved

    # Negated symptoms
    assert "high_fever" in data["negated_symptoms"]
    assert "chills" in data["negated_symptoms"]

    # Negated symptoms MUST NOT be in positive detected symptoms
    assert "high_fever" not in data["detected_symptoms"]
    assert "chills" not in data["detected_symptoms"]

    # Verify structured entity span details
    mentions = {e["raw_mention"]: e for e in data["extracted_entities"]}
    assert "chest pain" in mentions
    assert mentions["chest pain"]["canonical_symptom"] == "chest_pain"
    assert mentions["chest pain"]["is_negated"] is False

    assert "sore throught" in mentions
    assert mentions["sore throught"]["canonical_symptom"] == "throat_irritation"
    assert mentions["sore throught"]["match_type"] in ["synonym", "fuzzy_typo"]

    assert "high fever" in mentions
    assert mentions["high fever"]["is_negated"] is True


def test_dynamic_ontology_expansion_active_learning_loop(client: TestClient, db_session):
    """End-to-end active learning test:

    1. Patient uses colloquial phrase ('pins and needles') which is unrecognized.
    2. Phrase is captured in unmapped buffer with candidate suggestions.
    3. Clinician reviews and maps 'pins and needles' -> 'altered_sensorium'.
    4. Immediate re-extraction of the same text detects 'altered_sensorium' as dynamic_synonym.
    """
    _, headers = _create_authenticated_clinician(db_session, email="e2e_active_learning@example.com")
    test_phrase = "pins and needles"
    narrative = f"Patient complains of sudden {test_phrase} in hands and feet."

    # Step 1: Initial extraction - phrase is not in default ontology
    res_1 = client.post(
        "/api/v1/nlp/extract-entities",
        json={"narrative": narrative, "record_unmapped": True},
        headers=headers,
    )
    assert res_1.status_code == 200
    data_1 = res_1.json()
    assert "altered_sensorium" not in data_1["detected_symptoms"]

    # Step 2: Unmapped buffer contains candidate phrase
    res_unmapped = client.get("/api/v1/nlp/unmapped-phrases", headers=headers)
    assert res_unmapped.status_code == 200
    unmapped_data = res_unmapped.json()
    assert unmapped_data["total_unmapped"] >= 1

    # Step 3: Clinician binds colloquial phrase to canonical symptom
    expand_payload = {
        "phrase": test_phrase,
        "canonical_symptom": "altered_sensorium",
        "clinical_notes": "Peripheral paresthesia sensation mapped to altered sensorium",
    }
    res_expand = client.post("/api/v1/nlp/expand-ontology", json=expand_payload, headers=headers)
    assert res_expand.status_code == 201
    expand_data = res_expand.json()
    assert expand_data["status"] == "success"
    assert expand_data["phrase"] == test_phrase
    assert expand_data["canonical_symptom"] == "altered_sensorium"
    assert expand_data["total_dynamic_synonyms"] >= 1

    # Step 4: Re-extract with same narrative -> dynamic synonym immediately identified!
    res_2 = client.post(
        "/api/v1/nlp/extract-entities",
        json={"narrative": narrative, "record_unmapped": False},
        headers=headers,
    )
    assert res_2.status_code == 200
    data_2 = res_2.json()
    assert "altered_sensorium" in data_2["detected_symptoms"]

    # Verify match_type is explicitly dynamic_synonym
    dynamic_entity = next(e for e in data_2["extracted_entities"] if e["raw_mention"] == test_phrase)
    assert dynamic_entity["match_type"] == "dynamic_synonym"
    assert dynamic_entity["canonical_symptom"] == "altered_sensorium"


def test_expand_ontology_invalid_symptom_rejected(client: TestClient, db_session):
    """Validation test: Attempting to map to an invalid canonical symptom returns 422 Unprocessable Entity."""
    _, headers = _create_authenticated_clinician(db_session, email="invalid_sym@example.com")
    payload = {
        "phrase": "strange buzzing sensation",
        "canonical_symptom": "non_existent_symptom_xyz",
    }
    response = client.post("/api/v1/nlp/expand-ontology", json=payload, headers=headers)
    assert response.status_code == 422
    assert "Unknown canonical symptom" in response.json()["detail"]
