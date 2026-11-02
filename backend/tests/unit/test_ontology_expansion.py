"""Unit tests for Dynamic Symptom Vocabulary & Ontology Expansion (Step 8.3.2)."""

import json
from pathlib import Path
import pytest

from app.ml.inference.nlp_extractor import ClinicalSymptomExtractor
from app.ml.inference.ontology_manager import (
    CLINICAL_STOPWORDS,
    DynamicOntologyManager,
    UnmappedPhraseBuffer,
)


@pytest.fixture
def temp_ontology_file(tmp_path: Path) -> Path:
    return tmp_path / "test_dynamic_ontology.json"


@pytest.fixture
def temp_unmapped_file(tmp_path: Path) -> Path:
    return tmp_path / "test_unmapped_buffer.json"


@pytest.fixture
def dynamic_manager(temp_ontology_file: Path) -> DynamicOntologyManager:
    return DynamicOntologyManager(persistence_file=temp_ontology_file)


@pytest.fixture
def unmapped_buffer(temp_unmapped_file: Path, dynamic_manager: DynamicOntologyManager) -> UnmappedPhraseBuffer:
    return UnmappedPhraseBuffer(persistence_file=temp_unmapped_file, ontology_manager=dynamic_manager)


@pytest.fixture
def custom_extractor(dynamic_manager: DynamicOntologyManager, unmapped_buffer: UnmappedPhraseBuffer) -> ClinicalSymptomExtractor:
    return ClinicalSymptomExtractor(
        known_symptoms=[
            "headache",
            "high_fever",
            "cough",
            "chest_pain",
            "throat_irritation",
            "altered_sensorium",
            "unsteadiness",
            "chills",
            "fatigue",
        ],
        dynamic_ontology_manager=dynamic_manager,
        unmapped_buffer=unmapped_buffer,
    )


# -------------------------------------------------------------------------
# DynamicOntologyManager Unit Tests
# -------------------------------------------------------------------------
def test_dynamic_ontology_registration_and_persistence(dynamic_manager: DynamicOntologyManager, temp_ontology_file: Path):
    """Verifies that new synonyms are saved to disk and reloadable."""
    success = dynamic_manager.register_synonym(
        phrase="brain zaps",
        canonical_symptom="altered_sensorium",
        clinical_notes="Common SSRI withdrawal symptom reported by patients",
        source="clinician:dr_smith@example.com",
    )
    assert success is True
    assert "brain zaps" in dynamic_manager.get_synonyms()
    assert dynamic_manager.get_synonyms()["brain zaps"] == "altered_sensorium"

    # Verify disk persistence
    assert temp_ontology_file.exists()
    with open(temp_ontology_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["synonyms"]["brain zaps"] == "altered_sensorium"
    assert data["metadata"]["brain zaps"]["clinical_notes"] == "Common SSRI withdrawal symptom reported by patients"

    # Reload from disk into fresh instance
    reloaded_manager = DynamicOntologyManager(persistence_file=temp_ontology_file)
    assert "brain zaps" in reloaded_manager.get_synonyms()
    assert reloaded_manager.get_synonyms()["brain zaps"] == "altered_sensorium"


def test_dynamic_ontology_removal(dynamic_manager: DynamicOntologyManager):
    """Verifies removing dynamic synonyms cleanly updates store and disk."""
    dynamic_manager.register_synonym("fluttering in chest", "chest_pain")
    assert "fluttering in chest" in dynamic_manager.get_synonyms()

    removed = dynamic_manager.remove_synonym("fluttering in chest")
    assert removed is True
    assert "fluttering in chest" not in dynamic_manager.get_synonyms()

    # Removing non-existent phrase returns False
    assert dynamic_manager.remove_synonym("random phrase") is False


# -------------------------------------------------------------------------
# UnmappedPhraseBuffer Unit Tests
# -------------------------------------------------------------------------
def test_unmapped_phrase_buffer_frequency_and_suggestions(unmapped_buffer: UnmappedPhraseBuffer, temp_unmapped_file: Path):
    """Verifies logging unmapped phrases, frequency incrementing, and fuzzy candidate suggestions."""
    ref_lexicon = {
        "headache": "headache",
        "throat irritation": "throat_irritation",
        "cough": "cough",
        "chest pain": "chest_pain",
    }

    # Record unmapped phrase
    unmapped_buffer.record_unmapped_phrase("bad head throbbing", reference_lexicon=ref_lexicon)
    items = unmapped_buffer.list_unmapped_phrases()
    assert len(items) == 1
    assert items[0]["phrase"] == "bad head throbbing"
    assert items[0]["occurrence_count"] == 1

    # Record same phrase again -> frequency increases
    unmapped_buffer.record_unmapped_phrase("bad head throbbing", reference_lexicon=ref_lexicon)
    items = unmapped_buffer.list_unmapped_phrases()
    assert items[0]["occurrence_count"] == 2

    # Verify fuzzy candidate suggestions were generated
    suggestions = items[0]["suggested_matches"]
    assert isinstance(suggestions, list)

    # Verify stopword rejection
    unmapped_buffer.record_unmapped_phrase("the", reference_lexicon=ref_lexicon)
    unmapped_buffer.record_unmapped_phrase("and", reference_lexicon=ref_lexicon)
    assert len(unmapped_buffer.list_unmapped_phrases()) == 1  # Stopwords not added


def test_unmapped_phrase_resolution(unmapped_buffer: UnmappedPhraseBuffer):
    """Verifies that resolving a candidate phrase removes it from the unmapped buffer."""
    unmapped_buffer.record_unmapped_phrase("tingling extremities")
    assert len(unmapped_buffer.list_unmapped_phrases()) == 1

    resolved = unmapped_buffer.resolve_unmapped_phrase("tingling extremities")
    assert resolved is True
    assert len(unmapped_buffer.list_unmapped_phrases()) == 0


# -------------------------------------------------------------------------
# Extractor Integration with Dynamic Ontology Tests
# -------------------------------------------------------------------------
def test_extractor_hot_reloads_dynamic_synonym(custom_extractor: ClinicalSymptomExtractor):
    """Verifies that registering a dynamic synonym immediately enables extraction with match_type='dynamic_synonym'."""
    text_before = "Patient reports persistent brain zaps after medication adjustment."
    result_before = custom_extractor.extract(text_before)
    assert "altered_sensorium" not in result_before["detected_symptoms"]
    assert "brain zaps" in result_before["unrecognized_spans"]

    # Clinician registers 'brain zaps' -> 'altered_sensorium'
    success = custom_extractor.register_dynamic_synonym(
        phrase="brain zaps",
        canonical_symptom="altered_sensorium",
        clinical_notes="SSRI cessation paresthesia / brain zaps",
    )
    assert success is True

    # Immediate re-extraction without restarting extractor
    result_after = custom_extractor.extract(text_before)
    assert "altered_sensorium" in result_after["detected_symptoms"]
    assert "brain zaps" not in result_after["unrecognized_spans"]

    # Verify entity metadata reflects dynamic_synonym
    matched_entity = next(e for e in result_after["extracted_entities"] if e["raw_mention"] == "brain zaps")
    assert matched_entity["match_type"] == "dynamic_synonym"
    assert matched_entity["canonical_symptom"] == "altered_sensorium"


def test_extractor_rejects_invalid_canonical_symptom(custom_extractor: ClinicalSymptomExtractor):
    """Attempting to bind a phrase to a non-existent canonical symptom raises ValueError."""
    with pytest.raises(ValueError, match="Unknown canonical symptom 'totally_fake_symptom'"):
        custom_extractor.register_dynamic_synonym(
            phrase="some weird thing",
            canonical_symptom="totally_fake_symptom",
        )


def test_extractor_ontology_overview(custom_extractor: ClinicalSymptomExtractor):
    """Verifies catalog summary returns accurate counts and lists."""
    overview = custom_extractor.get_ontology_overview()
    assert overview["total_canonical_symptoms"] == 9
    assert "headache" in overview["canonical_symptoms"]
    assert overview["total_dynamic_synonyms"] == 0

    custom_extractor.register_dynamic_synonym("splitting headache", "headache")
    overview_updated = custom_extractor.get_ontology_overview()
    assert overview_updated["total_dynamic_synonyms"] == 1
    assert overview_updated["dynamic_synonyms"]["splitting headache"] == "headache"
