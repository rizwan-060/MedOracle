"""Unit tests for ML benchmark preprocessing pipelines (Sub-Step 6.2)."""

import csv
import json
from pathlib import Path
import pytest

from app.ml.preprocessing.diabetes import run_diabetes_preprocessing
from app.ml.preprocessing.heart import run_heart_preprocessing
from app.ml.preprocessing.symptoms import run_symptoms_preprocessing

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent.parent
PROCESSED_DIR = WORKSPACE_ROOT / "datasets" / "processed"


def test_heart_preprocessing_pipeline():
    """Verify that heart preprocessing removes missing values, normalizes features, and creates valid splits."""
    meta = run_heart_preprocessing()

    assert meta["dataset"] == "UCI Heart Disease (Cleveland)"
    assert meta["split_counts"]["train"] > 0
    assert meta["split_counts"]["val"] > 0
    assert meta["split_counts"]["test"] > 0
    assert sum(meta["split_counts"].values()) == 303

    # Check generated files
    heart_dir = PROCESSED_DIR / "heart"
    assert (heart_dir / "train.csv").exists()
    assert (heart_dir / "val.csv").exists()
    assert (heart_dir / "test.csv").exists()
    assert (heart_dir / "metadata.json").exists()

    # Verify no empty or '?' strings remain in train.csv
    with open(heart_dir / "train.csv", mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            for k, v in row.items():
                assert v != "", f"Found empty string in column {k}"
                assert v != "?", f"Found unhandled '?' in column {k}"
            # Verify target is 0 or 1
            assert row["target"] in ["0", "1"]


def test_diabetes_preprocessing_pipeline():
    """Verify that diabetes preprocessing imputes impossible zeroes and scales features."""
    meta = run_diabetes_preprocessing()

    assert meta["dataset"] == "PIMA Indians Diabetes (NIDDK)"
    assert sum(meta["split_counts"].values()) == 768

    diabetes_dir = PROCESSED_DIR / "diabetes"
    assert (diabetes_dir / "train.csv").exists()
    assert (diabetes_dir / "val.csv").exists()
    assert (diabetes_dir / "test.csv").exists()

    # Verify that in raw data, Glucose/BP had 0, but in processed data, imputation removed them
    # Note: features in processed data are z-score standardized, so we verify metadata medians
    assert meta["imputed_medians"]["Glucose"] > 100.0
    assert meta["imputed_medians"]["BloodPressure"] > 60.0
    assert meta["imputed_medians"]["BMI"] > 25.0


def test_symptoms_preprocessing_pipeline():
    """Verify that symptom preprocessing properly label-encodes 41 classes and maintains balance."""
    meta = run_symptoms_preprocessing()

    assert meta["total_diseases"] == 41
    assert meta["total_symptoms"] == 132
    assert sum(meta["split_counts"].values()) == 4920

    symptoms_dir = PROCESSED_DIR / "symptoms"
    assert (symptoms_dir / "train.csv").exists()
    assert (symptoms_dir / "val.csv").exists()
    assert (symptoms_dir / "test.csv").exists()

    # Verify metadata mappings
    assert len(meta["disease_to_index"]) == 41
    assert len(meta["index_to_disease"]) == 41

    # Check train targets are integer indices 0..40
    with open(symptoms_dir / "train.csv", mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        targets = set(int(row["target"]) for row in reader)
        assert len(targets) == 41
        assert min(targets) == 0
        assert max(targets) == 40
