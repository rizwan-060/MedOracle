"""Unit tests for Biomedical Symptom NER Training and Inference (Step 8.3.3)."""

from pathlib import Path
import pytest

from app.ml.inference.ner_model import BiomedicalSymptomNER
from app.ml.inference.nlp_extractor import ClinicalSymptomExtractor
from app.ml.training.ner import (
    evaluate_on_mtsamples,
    get_all_canonical_symptoms,
    load_ner_training_dataset,
    train_symptom_ner_model,
)
from scripts.retrain_nlp_extractor import main as run_retrain_script


@pytest.fixture
def temp_models_dir(tmp_path: Path) -> Path:
    return tmp_path / "models"


def test_get_all_canonical_symptoms():
    """Verify that 132 benchmark canonical symptoms are loaded."""
    canonicals = get_all_canonical_symptoms()
    assert len(canonicals) == 132
    assert "chest_pain" in canonicals
    assert "high_fever" in canonicals
    assert "polyuria" in canonicals


def test_load_ner_training_dataset():
    """Verify that symptom training corpus merges CSV, static synonyms, and canonicals."""
    texts, labels = load_ner_training_dataset()
    assert len(texts) > 350
    assert len(labels) == len(texts)
    assert len(set(labels)) <= 132

    # Check known colloquial and formal expressions
    text_set = set(texts)
    assert "squeezing chest tightness" in text_set
    assert "air hunger while lying flat" in text_set
    assert "chest pain" in text_set


def test_train_symptom_ner_model_and_bundle(temp_models_dir: Path):
    """Test full training pipeline and artifact serialization."""
    bundle, metadata = train_symptom_ner_model(models_dir=temp_models_dir)

    assert metadata.model_id == "symptom_ner_v1"
    assert metadata.version == "1.0.0"
    assert "top_1_accuracy" in metadata.metrics
    assert "top_3_accuracy" in metadata.metrics
    assert metadata.metrics["top_3_accuracy"] >= 0.85

    # Check saved artifacts on disk
    artifact_path = temp_models_dir / "symptom_ner_v1.joblib"
    meta_path = temp_models_dir / "symptom_ner_v1_metadata.json"
    assert artifact_path.exists()
    assert meta_path.exists()

    # Check bundle attributes
    assert "vectorizer" in bundle
    assert "canonical_centroids" in bundle
    assert "canonical_classes" in bundle
    assert bundle["canonical_centroids"].shape[0] == len(bundle["canonical_classes"])


def test_biomedical_symptom_ner_semantic_matching():
    """Test inference engine predictions on complex colloquial clinical expressions."""
    ner = BiomedicalSymptomNER.get_instance()
    assert ner.is_ready is True

    # 1. Test colloquial chest pain description
    pred_cardio = ner.predict_mention("squeezing chest tightness", threshold=0.50)
    assert pred_cardio is not None
    sym, conf = pred_cardio
    assert sym == "chest_pain"
    assert conf >= 0.50

    # 2. Test colloquial breathlessness description
    pred_resp = ner.predict_mention("air hunger while lying flat", threshold=0.45)
    assert pred_resp is not None
    sym_resp, _ = pred_resp
    assert sym_resp == "breathlessness"

    # 3. Test top-k candidate ranking
    candidates = ner.get_top_k_candidates("fluttering heartbeat", top_k=3)
    assert len(candidates) == 3
    candidate_syms = [c["canonical_symptom"] for c in candidates]
    assert "palpitations" in candidate_syms


def test_clinical_symptom_extractor_semantic_ner_integration():
    """Verify that ClinicalSymptomExtractor labels semantic NER matches with match_type='semantic_ner'."""
    extractor = ClinicalSymptomExtractor()
    sentence = "Patient complains of air hunger while lying flat."
    result = extractor.extract(sentence)

    assert "breathlessness" in result["detected_symptoms"]
    mentions = {e["raw_mention"]: e for e in result["extracted_entities"]}
    assert "air hunger while lying flat" in mentions
    assert mentions["air hunger while lying flat"]["canonical_symptom"] == "breathlessness"
    assert mentions["air hunger while lying flat"]["match_type"] == "semantic_ner"


def test_cli_retraining_script_execution():
    """Verify that the automated retrain script runs successfully and returns exit code 0."""
    exit_code = run_retrain_script()
    assert exit_code == 0
