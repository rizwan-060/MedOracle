"""Unit tests for ML model training pipelines and model registry."""

import json
from pathlib import Path
import numpy as np
import pytest

from app.ml.model_registry import (
    ModelMetadata,
    list_registered_models,
    load_model_bundle,
    save_model_bundle,
)
from app.ml.training.cardiovascular import load_heart_data, train_cardiovascular_model
from app.ml.training.diabetes import load_diabetes_data, train_diabetes_model


def test_train_cardiovascular_model():
    """Verify training cardiovascular model produces valid champion and metrics."""
    model, metadata = train_cardiovascular_model(save=False)

    assert metadata.model_id == "cardiovascular_risk_v1"
    assert len(metadata.feature_columns) == 13
    assert metadata.target_column == "target"
    assert metadata.version == "1.0.0"

    # Clinical performance boundaries for UCI Heart
    assert metadata.metrics["accuracy"] >= 0.75
    assert metadata.metrics["roc_auc"] >= 0.80
    assert metadata.metrics["f1"] >= 0.70

    # Test probability output shape
    data = load_heart_data()
    probs = model.predict_proba(data["X_test"][:5])
    assert probs.shape == (5, 2)
    assert np.allclose(probs.sum(axis=1), 1.0)


def test_train_diabetes_model():
    """Verify training diabetes model produces valid champion and metrics."""
    model, metadata = train_diabetes_model(save=False)

    assert metadata.model_id == "diabetes_risk_v1"
    assert len(metadata.feature_columns) == 8
    assert metadata.target_column == "Outcome"
    assert metadata.version == "1.0.0"

    # Clinical performance boundaries for PIMA Diabetes
    assert metadata.metrics["accuracy"] >= 0.70
    assert metadata.metrics["roc_auc"] >= 0.75
    assert metadata.metrics["f1"] >= 0.55

    # Test probability output shape
    data = load_diabetes_data()
    probs = model.predict_proba(data["X_test"][:5])
    assert probs.shape == (5, 2)
    assert np.allclose(probs.sum(axis=1), 1.0)


def test_model_registry_save_load_lifecycle(tmp_path: Path):
    """Verify model artifact and metadata serialization/deserialization lifecycle."""
    model, metadata = train_cardiovascular_model(save=False)

    # Save to custom temp directory
    artifact_path, meta_path = save_model_bundle(model, metadata, models_dir=tmp_path)
    assert artifact_path.exists()
    assert meta_path.exists()

    # Load back
    loaded_model, loaded_meta = load_model_bundle("cardiovascular_risk_v1", models_dir=tmp_path)
    assert loaded_meta.model_id == metadata.model_id
    assert loaded_meta.model_type == metadata.model_type
    assert loaded_meta.metrics == metadata.metrics

    # Verify deterministic inference reproduction
    data = load_heart_data()
    sample = data["X_test"][:10]
    orig_preds = model.predict_proba(sample)
    loaded_preds = loaded_model.predict_proba(sample)
    assert np.allclose(orig_preds, loaded_preds)

    # Verify registry listing
    all_models = list_registered_models(models_dir=tmp_path)
    assert len(all_models) == 1
    assert all_models[0].model_id == "cardiovascular_risk_v1"


def test_train_symptoms_model():
    """Verify training 41-class symptom disease model produces champion and valid metrics."""
    from app.ml.training.symptoms import load_symptoms_data, predict_top_candidates, train_symptoms_model

    model, metadata = train_symptoms_model(save=False)

    assert metadata.model_id == "symptoms_disease_v1"
    assert len(metadata.feature_columns) == 132
    assert metadata.target_column == "target"
    assert metadata.version == "1.0.0"

    # Multiclass diagnostic boundaries
    assert metadata.metrics["accuracy"] >= 0.90
    assert metadata.metrics["macro_f1"] >= 0.90
    assert metadata.metrics["top_3_accuracy"] >= 0.95
    assert metadata.metrics["top_5_accuracy"] >= 0.98

    # Test top candidate prediction
    data = load_symptoms_data()
    sample = data["X_test"][0]
    candidates = predict_top_candidates(model, sample, data["index_to_disease"], k=5)
    assert len(candidates) == 5
    assert candidates[0]["probability"] >= candidates[1]["probability"]
    assert "disease_name" in candidates[0]
    assert "confidence_percentage" in candidates[0]


def test_saved_model_registry_artifacts():
    """Verify actual trained artifacts in models/saved/ can be loaded and executed."""
    # Cardio model
    cardio_model, cardio_meta = load_model_bundle("cardiovascular_risk_v1")
    assert cardio_meta.model_id == "cardiovascular_risk_v1"
    assert len(cardio_meta.feature_columns) == 13

    # Diabetes model
    diab_model, diab_meta = load_model_bundle("diabetes_risk_v1")
    assert diab_meta.model_id == "diabetes_risk_v1"
    assert len(diab_meta.feature_columns) == 8

    # Symptoms model
    symp_model, symp_meta = load_model_bundle("symptoms_disease_v1")
    assert symp_meta.model_id == "symptoms_disease_v1"
    assert len(symp_meta.feature_columns) == 132

    # Run inference test on dummy patient inputs
    dummy_cardio = np.zeros((1, 13), dtype=np.float64)
    cardio_prob = cardio_model.predict_proba(dummy_cardio)[0, 1]
    assert 0.0 <= cardio_prob <= 1.0

    dummy_diab = np.zeros((1, 8), dtype=np.float64)
    diab_prob = diab_model.predict_proba(dummy_diab)[0, 1]
    assert 0.0 <= diab_prob <= 1.0

    dummy_symp = np.zeros((1, 132), dtype=np.float64)
    symp_probs = symp_model.predict_proba(dummy_symp)[0]
    assert len(symp_probs) == 41
    assert np.isclose(symp_probs.sum(), 1.0)

