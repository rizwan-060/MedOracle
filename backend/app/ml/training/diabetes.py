"""Type 2 Diabetes model training pipeline.

Trains and evaluates candidate classifiers on the preprocessed PIMA Indians Diabetes dataset:
- Logistic Regression (L2 regularized baseline)
- Random Forest Classifier (ensemble of decision trees with bagging)
- Gradient Boosting Classifier (sequential boosted decision trees)

Selects the champion model based on validation ROC-AUC, computes test metrics,
and saves the artifact + metadata bundle to the model registry.
"""

import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score

from app.ml.model_registry import ModelMetadata, save_model_bundle

WORKSPACE_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_DATA_DIR = WORKSPACE_ROOT / "datasets" / "processed" / "diabetes"


def load_dataset_split(csv_path: Path, feature_cols: List[str], target_col: str) -> Tuple[np.ndarray, np.ndarray]:
    """Read a processed CSV split into feature matrix X and label vector y."""
    if not csv_path.exists():
        raise FileNotFoundError(f"Split file not found at {csv_path}")

    x_rows: List[List[float]] = []
    y_vals: List[int] = []

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            features = [float(row[col]) for col in feature_cols]
            target = int(float(row[target_col]))
            x_rows.append(features)
            y_vals.append(target)

    return np.array(x_rows, dtype=np.float64), np.array(y_vals, dtype=np.int64)


def load_diabetes_data(data_dir: Path = DEFAULT_DATA_DIR) -> Dict[str, Any]:
    """Load train, val, and test splits along with preprocessing metadata."""
    meta_path = data_dir / "metadata.json"
    if not meta_path.exists():
        raise FileNotFoundError(f"Diabetes preprocessing metadata not found at {meta_path}")

    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    feature_cols = meta["feature_columns"]
    target_col = meta["target_column"]

    x_train, y_train = load_dataset_split(data_dir / "train.csv", feature_cols, target_col)
    x_val, y_val = load_dataset_split(data_dir / "val.csv", feature_cols, target_col)
    x_test, y_test = load_dataset_split(data_dir / "test.csv", feature_cols, target_col)

    return {
        "X_train": x_train,
        "y_train": y_train,
        "X_val": x_val,
        "y_val": y_val,
        "X_test": x_test,
        "y_test": y_test,
        "feature_columns": feature_cols,
        "target_column": target_col,
        "scaler_parameters": meta.get("scaler_parameters", {}),
    }


def evaluate_binary_classifier(
    model: Any,
    x: np.ndarray,
    y: np.ndarray,
) -> Dict[str, float]:
    """Compute standard binary classification metrics."""
    y_pred = model.predict(x)
    if hasattr(model, "predict_proba"):
        y_prob = model.predict_proba(x)[:, 1]
    else:
        y_prob = model.decision_function(x)

    return {
        "accuracy": round(float(accuracy_score(y, y_pred)), 4),
        "precision": round(float(precision_score(y, y_pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y, y_pred, zero_division=0)), 4),
        "f1": round(float(f1_score(y, y_pred, zero_division=0)), 4),
        "roc_auc": round(float(roc_auc_score(y, y_prob)), 4),
    }


def get_candidate_models() -> Dict[str, Any]:
    """Instantiate candidate classifiers for diabetes risk prediction."""
    return {
        "LogisticRegression": LogisticRegression(
            C=1.0,
            max_iter=1000,
            solver="lbfgs",
            random_state=42,
        ),
        "RandomForestClassifier": RandomForestClassifier(
            n_estimators=100,
            max_depth=5,
            min_samples_split=4,
            random_state=42,
        ),
        "GradientBoostingClassifier": GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.05,
            max_depth=3,
            random_state=42,
        ),
    }


def train_diabetes_model(
    data_dir: Path = DEFAULT_DATA_DIR,
    models_dir: Optional[Path] = None,
    save: bool = True,
) -> Tuple[Any, ModelMetadata]:
    """Train candidate models, select champion by validation ROC-AUC, and register bundle.

    Args:
        data_dir: Directory containing processed diabetes CSV splits and metadata.
        models_dir: Target directory for saving serialized artifacts.
        save: If True, writes the champion model bundle to disk.

    Returns:
        Tuple of (champion_estimator, ModelMetadata).
    """
    data = load_diabetes_data(data_dir)
    x_train, y_train = data["X_train"], data["y_train"]
    x_val, y_val = data["X_val"], data["y_val"]
    x_test, y_test = data["X_test"], data["y_test"]

    candidates = get_candidate_models()
    comparison: List[Dict[str, Any]] = []

    best_name = ""
    best_score = -1.0
    trained_models: Dict[str, Any] = {}

    for name, clf in candidates.items():
        clf.fit(x_train, y_train)
        trained_models[name] = clf
        val_metrics = evaluate_binary_classifier(clf, x_val, y_val)

        comparison.append({
            "model_type": name,
            "validation_metrics": val_metrics,
        })

        composite_score = val_metrics["roc_auc"] * 10.0 + val_metrics["f1"]
        if composite_score > best_score:
            best_score = composite_score
            best_name = name

    champion = trained_models[best_name]
    test_metrics = evaluate_binary_classifier(champion, x_test, y_test)

    params = champion.get_params()
    clean_params = {k: v for k, v in params.items() if isinstance(v, (int, float, str, bool, type(None)))}

    metadata = ModelMetadata(
        model_id="diabetes_risk_v1",
        model_name="Type 2 Diabetes Risk Classifier",
        model_type=best_name,
        version="1.0.0",
        dataset_name="PIMA Indians Diabetes (NIDDK Cohort)",
        target_column=data["target_column"],
        feature_columns=data["feature_columns"],
        metrics=test_metrics,
        hyperparameters=clean_params,
        scaler_params=data["scaler_parameters"],
        candidate_comparison=comparison,
    )

    if save:
        save_model_bundle(champion, metadata, models_dir=models_dir)

    return champion, metadata
