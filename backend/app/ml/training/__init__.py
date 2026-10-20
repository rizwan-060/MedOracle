"""MedOracle ML Training package."""

from app.ml.training.cardiovascular import train_cardiovascular_model
from app.ml.training.diabetes import train_diabetes_model

__all__ = [
    "train_cardiovascular_model",
    "train_diabetes_model",
]
