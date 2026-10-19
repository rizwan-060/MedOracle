"""MedOracle ML Preprocessing Pipelines Package."""

from pathlib import Path
from typing import Any, Dict

from app.ml.preprocessing.diabetes import run_diabetes_preprocessing
from app.ml.preprocessing.heart import run_heart_preprocessing
from app.ml.preprocessing.symptoms import run_symptoms_preprocessing


def run_all_preprocessing() -> Dict[str, Any]:
    """Execute preprocessing for all three benchmark datasets."""
    heart_meta = run_heart_preprocessing()
    diabetes_meta = run_diabetes_preprocessing()
    symptoms_meta = run_symptoms_preprocessing()

    return {
        "heart_disease": heart_meta,
        "diabetes": diabetes_meta,
        "symptoms": symptoms_meta,
    }


__all__ = [
    "run_heart_preprocessing",
    "run_diabetes_preprocessing",
    "run_symptoms_preprocessing",
    "run_all_preprocessing",
]
