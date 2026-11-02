"""Unit tests for MedOracle Clinical Symptom Corpus Acquisition (Step 8.3.1)."""

import csv
import json
from pathlib import Path
import pytest

from backend.scripts.download_symptom_corpus import (
    RAW_CORPUS_DIR,
    CANONICAL_DATASET,
    curate_and_export_corpora,
    load_canonical_symptom_set,
)


@pytest.fixture(scope="module")
def corpus_dir():
    """Ensure corpora are generated before running tests."""
    curate_and_export_corpora(force=True)
    return RAW_CORPUS_DIR


def test_corpus_files_exist_and_non_empty(corpus_dir):
    """Verify all 3 corpus artifacts exist and have non-zero size."""
    phrases_csv = corpus_dir / "clinical_symptom_phrases.csv"
    transcripts_json = corpus_dir / "mtsamples_clinical_transcripts.json"
    metadata_json = corpus_dir / "corpus_metadata.json"

    assert phrases_csv.exists()
    assert phrases_csv.stat().st_size > 0

    assert transcripts_json.exists()
    assert transcripts_json.stat().st_size > 0

    assert metadata_json.exists()
    assert metadata_json.stat().st_size > 0


def test_phrases_csv_schema_and_canonical_mapping(corpus_dir):
    """Verify CSV header, row formatting, and canonical symptom mapping integrity."""
    phrases_csv = corpus_dir / "clinical_symptom_phrases.csv"
    canonical_set = set(load_canonical_symptom_set())

    with open(phrases_csv, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        expected_fields = {"phrase_id", "phrase_text", "canonical_symptom", "clinical_domain", "linguistic_category"}
        assert set(reader.fieldnames or []).issuperset(expected_fields)

        rows = list(reader)
        assert len(rows) >= 50, f"Expected at least 50 phrases, got {len(rows)}"

        for row in rows:
            assert row["phrase_id"].startswith("CSP-")
            assert len(row["phrase_text"].strip()) > 2
            assert len(row["clinical_domain"].strip()) > 0
            assert row["linguistic_category"] in {"formal_medical", "patient_colloquial"}

            canonical = row["canonical_symptom"]
            if canonical_set:
                assert canonical in canonical_set, f"Phrase '{row['phrase_text']}' mapped to invalid canonical: '{canonical}'"


def test_transcripts_ner_spans_accuracy(corpus_dir):
    """Verify character-level span offsets in transcripts NER ground truth."""
    transcripts_json = corpus_dir / "mtsamples_clinical_transcripts.json"

    with open(transcripts_json, mode="r", encoding="utf-8") as f:
        transcripts = json.load(f)

    assert len(transcripts) >= 5
    total_annotations = 0
    negated_count = 0

    for doc in transcripts:
        assert "id" in doc
        assert "specialty" in doc
        assert "full_text" in doc
        assert "annotations" in doc

        text = doc["full_text"]
        for ann in doc["annotations"]:
            start = ann["start"]
            end = ann["end"]
            mention = ann["mention"]

            assert 0 <= start < end <= len(text)
            extracted_span = text[start:end]
            assert extracted_span.lower() == mention.lower(), (
                f"Span mismatch in {doc['id']}: '{extracted_span}' != '{mention}'"
            )
            assert isinstance(ann["is_negated"], bool)
            if ann["is_negated"]:
                negated_count += 1
            total_annotations += 1

    assert total_annotations > 15
    assert negated_count > 0, "Corpus must include clinical negation examples for NegEx evaluation"


def test_corpus_metadata_hashes_and_coverage(corpus_dir):
    """Verify metadata statistics, checksums, and domain diversity."""
    metadata_json = corpus_dir / "corpus_metadata.json"

    with open(metadata_json, mode="r", encoding="utf-8") as f:
        meta = json.load(f)

    assert meta["dataset_id"] == "DS-SYM-02"
    assert meta["status"] == "curated_and_verified"
    assert "clinical_symptom_phrases_csv" in meta["files"]
    assert "mtsamples_clinical_transcripts_json" in meta["files"]

    coverage = meta["vocabulary_coverage"]
    assert coverage["total_domains"] >= 5
    assert coverage["unique_canonical_symptoms_covered"] >= 20
    assert "cardiovascular" in coverage["unique_clinical_domains"]
    assert "metabolic" in coverage["unique_clinical_domains"]


def test_download_script_idempotency():
    """Verify that rerun of acquisition function completes with consistent output."""
    meta1 = curate_and_export_corpora(force=True)
    meta2 = curate_and_export_corpora(force=False)
    assert meta1["dataset_id"] == meta2["dataset_id"]
    assert meta1["files"]["clinical_symptom_phrases_csv"]["total_rows"] == meta2["files"]["clinical_symptom_phrases_csv"]["total_rows"]
