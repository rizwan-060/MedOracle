"""Unit tests for ClinicalSymptomExtractor NLP component."""

import pytest
from app.ml.inference.nlp_extractor import ClinicalSymptomExtractor


@pytest.fixture
def extractor() -> ClinicalSymptomExtractor:
    return ClinicalSymptomExtractor(
        known_symptoms=[
            "headache",
            "runny_nose",
            "continuous_sneezing",
            "throat_irritation",
            "patches_in_throat",
            "high_fever",
            "mild_fever",
            "chills",
            "sweating",
            "cough",
            "chest_pain",
            "breathlessness",
            "nausea",
            "vomiting",
            "abdominal_pain",
            "fatigue",
            "joint_pain",
            "muscle_pain",
            "dizziness",
        ]
    )


def test_nlp_extract_free_text_with_typo(extractor: ClinicalSymptomExtractor):
    """Verifies that free-text input with typos (sore throught) is mapped to canonical symptoms."""
    sentence = "i am experiencing severe headache from the past 3 days. i also have a runny nose and a sore throught."
    result = extractor.extract(sentence)

    assert "headache" in result["detected_symptoms"]
    assert "runny_nose" in result["detected_symptoms"]
    assert "throat_irritation" in result["detected_symptoms"]

    # Verify extracted entities metadata
    mentions = {e["raw_mention"]: e for e in result["extracted_entities"]}
    assert "severe headache" in mentions or "headache" in mentions
    assert "runny nose" in mentions
    assert "sore throught" in mentions
    assert mentions["sore throught"]["canonical_symptom"] == "throat_irritation"


def test_nlp_extract_clinical_negation(extractor: ClinicalSymptomExtractor):
    """Verifies that NegEx clinical negation excludes negated symptoms from positive vector."""
    sentence = "Patient has severe headache and runny nose, but no fever and denies chest pain."
    result = extractor.extract(sentence)

    # Positive symptoms
    assert "headache" in result["detected_symptoms"]
    assert "runny_nose" in result["detected_symptoms"]

    # Negated symptoms must be excluded from detected_symptoms
    assert "high_fever" not in result["detected_symptoms"]
    assert "chest_pain" not in result["detected_symptoms"]

    # Must be tracked in negated_symptoms list
    assert "high_fever" in result["negated_symptoms"]
    assert "chest_pain" in result["negated_symptoms"]


def test_nlp_extract_punctuation_terminates_negation(extractor: ClinicalSymptomExtractor):
    """Verifies that punctuation boundaries terminate negation scope propagation."""
    sentence = "No chills. Severe cough and muscle ache reported."
    result = extractor.extract(sentence)

    assert "chills" in result["negated_symptoms"]
    assert "chills" not in result["detected_symptoms"]
    assert "cough" in result["detected_symptoms"]
    assert "muscle_pain" in result["detected_symptoms"]


def test_nlp_extract_empty_string(extractor: ClinicalSymptomExtractor):
    """Verifies graceful handling of empty or blank input."""
    result = extractor.extract("   ")
    assert result["detected_symptoms"] == []
    assert result["extracted_entities"] == []
    assert result["negated_symptoms"] == []
