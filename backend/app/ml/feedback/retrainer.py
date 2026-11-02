"""Continuous active learning retraining pipeline.

Ingests accumulated clinician/patient feedback, retrains candidate models
on augmented datasets, evaluates against held-out splits, applies a performance
promotion gate, and updates the model registry and database audit trail.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from sqlalchemy.orm import Session

from app.ml.feedback.buffer import FeedbackBuffer, FeedbackRecord
from app.ml.feedback.sync import sync_all_models_to_db
from app.ml.model_registry import ModelMetadata, load_model_bundle, save_model_bundle
from app.ml.training.cardiovascular import (
    evaluate_binary_classifier as evaluate_cardio_model,
    get_candidate_models as get_cardio_candidates,
    load_heart_data,
)
from app.ml.training.diabetes import (
    evaluate_binary_classifier as evaluate_diabetes_model,
    get_candidate_models as get_diabetes_candidates,
    load_diabetes_data,
)
from app.ml.training.symptoms import (
    evaluate_multiclass_classifier as evaluate_symptoms_model,
    get_candidate_models as get_symptoms_candidates,
    load_symptoms_data,
)


@dataclass
class RetrainingResult:
    """Result summary of an active learning retraining iteration."""

    target_disease: str
    success: bool
    promoted: bool
    message: str
    samples_used: int
    current_metrics: Dict[str, float] = field(default_factory=dict)
    retrained_metrics: Dict[str, float] = field(default_factory=dict)
    new_version: Optional[str] = None
    artifact_path: Optional[str] = None
    rejection_reason: Optional[str] = None


class ContinuousRetrainer:
    """Orchestrates model retraining on augmented feedback datasets with promotion gates."""

    def __init__(
        self,
        buffer: Optional[FeedbackBuffer] = None,
        models_dir: Optional[Path] = None,
    ):
        self.buffer = buffer or FeedbackBuffer()
        self.models_dir = Path(models_dir) if models_dir else None

    def _bump_version(self, current_version: str) -> str:
        """Increment the minor version (e.g. '1.0.0' -> '1.1.0')."""
        try:
            parts = current_version.split(".")
            major = int(parts[0])
            minor = int(parts[1]) + 1
            patch = 0
            return f"{major}.{minor}.{patch}"
        except Exception:
            return f"{current_version}.1"

    def _extract_feedback_arrays(
        self,
        records: List[FeedbackRecord],
        feature_cols: List[str],
        target_disease: str,
        disease_to_index: Optional[Dict[str, int]] = None,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Convert feedback records into numpy feature matrix X and label vector y."""
        x_rows: List[List[float]] = []
        y_vals: List[int] = []

        for rec in records:
            # Extract features in the exact column ordering
            row: List[float] = []
            for col in feature_cols:
                val = rec.features.get(col, 0.0)
                try:
                    row.append(float(val))
                except (ValueError, TypeError):
                    row.append(0.0)
            x_rows.append(row)

            # Extract target label
            raw_label = rec.ground_truth_label
            if target_disease in ("cardio", "diabetes"):
                y_vals.append(int(float(raw_label)))
            elif target_disease == "symptoms":
                if isinstance(raw_label, str) and disease_to_index and raw_label in disease_to_index:
                    y_vals.append(disease_to_index[raw_label])
                else:
                    y_vals.append(int(raw_label))

        return np.array(x_rows, dtype=np.float64), np.array(y_vals, dtype=np.int64)

    def retrain_model(
        self,
        target_disease: str,
        min_samples: int = 10,
        force: bool = False,
        tolerance: float = 0.03,
        db_session: Optional[Session] = None,
    ) -> RetrainingResult:
        """Execute a continuous retraining iteration for a target disease domain.

        Args:
            target_disease: 'cardio', 'diabetes', or 'symptoms'.
            min_samples: Minimum feedback samples required before retraining triggers.
            force: If True, retrain even if min_samples is not met.
            tolerance: Permissible metric variance for champion promotion.
            db_session: Optional SQLAlchemy session for registering in database.

        Returns:
            RetrainingResult with promotion status, metrics comparison, and artifact paths.
        """
        records = self.buffer.load_records(target_disease)
        if len(records) < min_samples and not force:
            return RetrainingResult(
                target_disease=target_disease,
                success=False,
                promoted=False,
                message=f"Insufficient feedback records (have {len(records)}, require {min_samples}).",
                samples_used=len(records),
            )

        # Map domain to model_id and loaders
        if target_disease == "cardio":
            model_id = "cardiovascular_risk_v1"
            data = load_heart_data()
            disease_to_index = None
        elif target_disease == "diabetes":
            model_id = "diabetes_risk_v1"
            data = load_diabetes_data()
            disease_to_index = None
        elif target_disease == "symptoms":
            model_id = "symptoms_disease_v1"
            data = load_symptoms_data()
            disease_to_index = data.get("disease_to_index")
        else:
            raise ValueError(f"Unsupported target_disease: {target_disease}")

        # Load currently active champion
        current_model, current_meta = load_model_bundle(model_id, models_dir=self.models_dir)
        current_metrics = current_meta.metrics

        # Prepare augmented training split
        feature_cols = current_meta.feature_columns
        base_x_train = data["X_train"]
        base_y_train = data["y_train"]

        if records:
            x_feedback, y_feedback = self._extract_feedback_arrays(
                records, feature_cols, target_disease, disease_to_index
            )
            x_augmented = np.vstack([base_x_train, x_feedback])
            y_augmented = np.concatenate([base_y_train, y_feedback])
        else:
            x_augmented = base_x_train
            y_augmented = base_y_train

        # Retrain candidates
        x_val = data["X_val"]
        y_val = data["y_val"]
        x_test = data["X_test"]
        y_test = data["y_test"]

        comparison: List[Dict[str, Any]] = []

        if target_disease == "cardio":
            candidate_models = get_cardio_candidates()
            for name, clf in candidate_models.items():
                clf.fit(x_augmented, y_augmented)
                vm = evaluate_cardio_model(clf, x_val, y_val)
                comparison.append({"name": name, "model": clf, "val_metric": vm["roc_auc"], "val_metrics": vm})
            best_candidate = max(comparison, key=lambda c: c["val_metric"])
            retrained_model = best_candidate["model"]
            retrained_metrics = evaluate_cardio_model(retrained_model, x_test, y_test)
            gate_current_score = current_metrics.get("roc_auc", 0.85)
            gate_retrained_score = retrained_metrics.get("roc_auc", 0.0)

        elif target_disease == "diabetes":
            candidate_models = get_diabetes_candidates()
            for name, clf in candidate_models.items():
                clf.fit(x_augmented, y_augmented)
                vm = evaluate_diabetes_model(clf, x_val, y_val)
                comparison.append({"name": name, "model": clf, "val_metric": vm["roc_auc"], "val_metrics": vm})
            best_candidate = max(comparison, key=lambda c: c["val_metric"])
            retrained_model = best_candidate["model"]
            retrained_metrics = evaluate_diabetes_model(retrained_model, x_test, y_test)
            gate_current_score = current_metrics.get("roc_auc", 0.85)
            gate_retrained_score = retrained_metrics.get("roc_auc", 0.0)

        else:  # symptoms
            candidate_models = get_symptoms_candidates()
            for name, clf in candidate_models.items():
                clf.fit(x_augmented, y_augmented)
                vm = evaluate_symptoms_model(clf, x_val, y_val)
                comparison.append({"name": name, "model": clf, "val_metric": vm["top_3_accuracy"], "val_metrics": vm})
            best_candidate = max(comparison, key=lambda c: c["val_metric"])
            retrained_model = best_candidate["model"]
            retrained_metrics = evaluate_symptoms_model(retrained_model, x_test, y_test)
            gate_current_score = current_metrics.get("top_3_accuracy", 1.0)
            gate_retrained_score = retrained_metrics.get("top_3_accuracy", 0.0)

        # Champion Promotion Gate
        # Retrained candidate is promoted if its held-out test score is within tolerance of champion
        passed_gate = gate_retrained_score >= (gate_current_score - tolerance)

        if not passed_gate:
            return RetrainingResult(
                target_disease=target_disease,
                success=True,
                promoted=False,
                message="Retrained model failed performance gate. Champion preserved without regression.",
                samples_used=len(records),
                current_metrics=current_metrics,
                retrained_metrics=retrained_metrics,
                rejection_reason=(
                    f"Test score {gate_retrained_score:.4f} dropped below gate threshold "
                    f"{(gate_current_score - tolerance):.4f} (current: {gate_current_score:.4f})."
                ),
            )

        # Promotion: Bump version and persist new artifact
        new_version = self._bump_version(current_meta.version)
        new_metadata = ModelMetadata(
            model_id=current_meta.model_id,
            model_name=current_meta.model_name,
            model_type=type(retrained_model).__name__,
            version=new_version,
            dataset_name=f"{current_meta.dataset_name} + ActiveLearningFeedback (N={len(records)})",
            target_column=current_meta.target_column,
            feature_columns=current_meta.feature_columns,
            metrics=retrained_metrics,
            hyperparameters=retrained_model.get_params(),
            scaler_params=current_meta.scaler_params,
            candidate_comparison=[
                {"name": c["name"], "model_type": type(c["model"]).__name__, "validation_metrics": c["val_metrics"]}
                for c in comparison
            ],
            artifact_filename=f"{model_id}.joblib",
        )

        saved_path, _ = save_model_bundle(retrained_model, new_metadata, models_dir=self.models_dir)

        # Sync to database if session provided
        if db_session:
            sync_all_models_to_db(db_session)

        # Archive and clear processed feedback buffer
        if records:
            self.buffer.archive_and_clear(target_disease)

        return RetrainingResult(
            target_disease=target_disease,
            success=True,
            promoted=True,
            message=f"Model successfully retrained on {len(records)} feedback samples and promoted to v{new_version}.",
            samples_used=len(records),
            current_metrics=current_metrics,
            retrained_metrics=retrained_metrics,
            new_version=new_version,
            artifact_path=str(saved_path),
        )
