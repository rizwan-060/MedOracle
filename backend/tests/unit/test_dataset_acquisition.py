"""Unit tests for ML benchmark dataset acquisition and validation (Sub-Step 6.1)."""

import csv
from pathlib import Path
import pytest

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent.parent
RAW_DATA_DIR = WORKSPACE_ROOT / "datasets" / "raw"


def test_uci_heart_dataset_integrity():
    """Verify that UCI Heart Disease CSV exists, has 14 columns and ~303 rows."""
    file_path = RAW_DATA_DIR / "heart_disease_uci.csv"
    assert file_path.exists(), f"File {file_path} not found"

    with open(file_path, mode="r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)

    expected_cols = [
        "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
        "thalach", "exang", "oldpeak", "slope", "ca", "thal", "target"
    ]
    assert header == expected_cols
    assert len(rows) >= 300
    assert len(rows) <= 305


def test_pima_diabetes_dataset_integrity():
    """Verify that PIMA Indians Diabetes CSV exists, has 9 columns and 768 rows."""
    file_path = RAW_DATA_DIR / "diabetes_pima.csv"
    assert file_path.exists(), f"File {file_path} not found"

    with open(file_path, mode="r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)

    expected_cols = [
        "Pregnancies", "Glucose", "BloodPressure", "SkinThickness",
        "Insulin", "BMI", "DiabetesPedigreeFunction", "Age", "Outcome"
    ]
    assert header == expected_cols
    assert len(rows) == 768

    # Verify Outcome values are 0 or 1
    outcomes = set(r[-1] for r in rows)
    assert outcomes == {"0", "1"}


def test_symptom_disease_dataset_integrity():
    """Verify that Disease-Symptom CSV exists, has 133 columns and 4,920 rows."""
    file_path = RAW_DATA_DIR / "symptoms_disease.csv"
    assert file_path.exists(), f"File {file_path} not found"

    with open(file_path, mode="r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)

    assert len(header) == 133
    assert header[-1] == "prognosis"
    assert len(rows) == 4920

    # Ensure 41 unique disease categories are present
    diseases = set(r[-1] for r in rows)
    assert len(diseases) == 41
