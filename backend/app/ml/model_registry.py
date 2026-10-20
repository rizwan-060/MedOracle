"""Model Registry for saving, loading, versioning, and inspecting ML artifacts.

Handles:
1. Serialization of trained estimators via joblib.
2. Metadata tracking (model_id, algorithm, version, features, metrics, scaler parameters).
3. Retrieval and inspection of available models in `models/saved/`.
"""

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import joblib

WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_MODELS_DIR = WORKSPACE_ROOT / "models" / "saved"


@dataclass
class ModelMetadata:
    """Metadata schema for a registered machine learning model."""

    model_id: str
    model_name: str
    model_type: str
    version: str
    dataset_name: str
    target_column: str
    feature_columns: List[str]
    metrics: Dict[str, float]
    hyperparameters: Dict[str, Any]
    scaler_params: Optional[Dict[str, Any]] = None
    candidate_comparison: Optional[List[Dict[str, Any]]] = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    artifact_filename: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to JSON-serializable dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelMetadata":
        """Instantiate ModelMetadata from a dictionary."""
        return cls(
            model_id=data["model_id"],
            model_name=data["model_name"],
            model_type=data["model_type"],
            version=data["version"],
            dataset_name=data["dataset_name"],
            target_column=data["target_column"],
            feature_columns=data["feature_columns"],
            metrics=data["metrics"],
            hyperparameters=data["hyperparameters"],
            scaler_params=data.get("scaler_params"),
            candidate_comparison=data.get("candidate_comparison"),
            created_at=data.get("created_at", datetime.now(timezone.utc).isoformat()),
            artifact_filename=data.get("artifact_filename", f"{data['model_id']}.joblib"),
        )


def save_model_bundle(
    model: Any,
    metadata: ModelMetadata,
    models_dir: Optional[Path] = None,
) -> Tuple[Path, Path]:
    """Serialize model artifact and metadata JSON to the model registry directory.

    Args:
        model: Trained scikit-learn estimator.
        metadata: ModelMetadata instance describing the model.
        models_dir: Optional directory override. Defaults to `models/saved`.

    Returns:
        Tuple of (artifact_path, metadata_path).
    """
    target_dir = Path(models_dir) if models_dir else DEFAULT_MODELS_DIR
    target_dir.mkdir(parents=True, exist_ok=True)

    artifact_filename = f"{metadata.model_id}.joblib"
    metadata_filename = f"{metadata.model_id}_metadata.json"

    metadata.artifact_filename = artifact_filename

    artifact_path = target_dir / artifact_filename
    metadata_path = target_dir / metadata_filename

    # Save binary estimator via joblib
    joblib.dump(model, artifact_path)

    # Save JSON metadata
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata.to_dict(), f, indent=2)

    return artifact_path, metadata_path


def load_model_bundle(
    model_id: str,
    models_dir: Optional[Path] = None,
) -> Tuple[Any, ModelMetadata]:
    """Load trained estimator and metadata bundle by model_id.

    Args:
        model_id: Unique model identifier (e.g. 'cardiovascular_risk_v1').
        models_dir: Optional directory override. Defaults to `models/saved`.

    Returns:
        Tuple of (model, ModelMetadata).
    """
    target_dir = Path(models_dir) if models_dir else DEFAULT_MODELS_DIR
    metadata_path = target_dir / f"{model_id}_metadata.json"

    if not metadata_path.exists():
        raise FileNotFoundError(f"Model metadata not found at {metadata_path}")

    with open(metadata_path, "r", encoding="utf-8") as f:
        meta_dict = json.load(f)

    metadata = ModelMetadata.from_dict(meta_dict)
    artifact_path = target_dir / metadata.artifact_filename

    if not artifact_path.exists():
        raise FileNotFoundError(f"Model artifact not found at {artifact_path}")

    model = joblib.load(artifact_path)
    return model, metadata


def list_registered_models(models_dir: Optional[Path] = None) -> List[ModelMetadata]:
    """List all registered models present in the registry directory."""
    target_dir = Path(models_dir) if models_dir else DEFAULT_MODELS_DIR
    if not target_dir.exists():
        return []

    models = []
    for meta_file in target_dir.glob("*_metadata.json"):
        try:
            with open(meta_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            models.append(ModelMetadata.from_dict(data))
        except Exception:
            continue
    return sorted(models, key=lambda m: m.model_id)
