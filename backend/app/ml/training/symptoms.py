"""41-Class Disease-to-Symptom model training pipeline.

Trains and evaluates multiclass candidate classifiers on the 132-symptom diagnostic matrix:
- Multinomial Naive Bayes (probabilistic baseline for binary symptom occurrences)
- Random Forest Classifier (ensemble of 100 decision trees)
- Multinomial Logistic Regression (L2 regularized multiclass)

Selects the champion model based on validation top-3 accuracy and macro F1,
computes test metrics (top-1, top-3, top-5 accuracy, macro/weighted F1),
and registers the model bundle in the model registry.
"""

import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.naive_bayes import MultinomialNB

from app.ml.model_registry import ModelMetadata, save_model_bundle

WORKSPACE_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_DATA_DIR = WORKSPACE_ROOT / "datasets" / "processed" / "symptoms"


def load_dataset_split(csv_path: Path, feature_cols: List[str], target_col: str) -> Tuple[np.ndarray, np.ndarray]:
    """Read a processed symptoms CSV split into feature matrix X and label vector y."""
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


def load_symptoms_data(data_dir: Path = DEFAULT_DATA_DIR) -> Dict[str, Any]:
    """Load train, val, and test splits along with symptom metadata."""
    meta_path = data_dir / "metadata.json"
    if not meta_path.exists():
        raise FileNotFoundError(f"Symptoms metadata not found at {meta_path}")

    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    feature_cols = meta["symptom_features"]
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
        "disease_to_index": meta.get("disease_to_index", {}),
        "index_to_disease": meta.get("index_to_disease", {}),
        "total_diseases": meta.get("total_diseases", 41),
    }


def compute_top_k_accuracy(probs: np.ndarray, y_true: np.ndarray, k: int) -> float:
    """Calculate top-k accuracy (true class is among top-k highest predicted probabilities)."""
    top_k_indices = np.argsort(probs, axis=1)[:, -k:]
    correct = [y in top_k for y, top_k in zip(y_true, top_k_indices)]
    return round(float(np.mean(correct)), 4)


def evaluate_multiclass_classifier(
    model: Any,
    x: np.ndarray,
    y: np.ndarray,
) -> Dict[str, float]:
    """Compute standard and clinical top-k multiclass evaluation metrics."""
    y_pred = model.predict(x)
    probs = model.predict_proba(x)

    return {
        "accuracy": round(float(accuracy_score(y, y_pred)), 4),
        "macro_f1": round(float(f1_score(y, y_pred, average="macro", zero_division=0)), 4),
        "weighted_f1": round(float(f1_score(y, y_pred, average="weighted", zero_division=0)), 4),
        "top_3_accuracy": compute_top_k_accuracy(probs, y, k=3),
        "top_5_accuracy": compute_top_k_accuracy(probs, y, k=5),
    }


def get_candidate_models() -> Dict[str, Any]:
    """Instantiate candidate classifiers for 41-class disease prediction."""
    return {
        "MultinomialNB": MultinomialNB(alpha=1.0),
        "RandomForestClassifier": RandomForestClassifier(
            n_estimators=100,
            max_depth=15,
            min_samples_split=4,
            random_state=42,
        ),
        "LogisticRegression": LogisticRegression(
            C=1.0,
            max_iter=1000,
            solver="lbfgs",
            random_state=42,
        ),
    }


def predict_top_candidates(
    model: Any,
    symptom_vector: np.ndarray,
    index_to_disease: Dict[str, str],
    k: int = 5,
) -> List[Dict[str, Any]]:
    """Generate top-k differential diagnosis predictions with calibrated probabilities."""
    if symptom_vector.ndim == 1:
        symptom_vector = symptom_vector.reshape(1, -1)

    probs = model.predict_proba(symptom_vector)[0]
    top_indices = np.argsort(probs)[::-1][:k]

    candidates = []
    for idx in top_indices:
        prob = float(probs[idx])
        disease_name = index_to_disease.get(str(idx), f"Unknown ({idx})")
        candidates.append({
            "disease_id": int(idx),
            "disease_name": disease_name,
            "probability": round(prob, 4),
            "confidence_percentage": round(prob * 100.0, 2),
        })

    return candidates


def train_symptoms_model(
    data_dir: Path = DEFAULT_DATA_DIR,
    models_dir: Optional[Path] = None,
    save: bool = True,
) -> Tuple[Any, ModelMetadata]:
    """Train candidate models, select champion by validation top-3 accuracy & F1, and register bundle.

    Args:
        data_dir: Directory containing processed symptoms CSV splits and metadata.
        models_dir: Target directory for saving serialized artifacts.
        save: If True, writes the champion model bundle to disk.

    Returns:
        Tuple of (champion_estimator, ModelMetadata).
    """
    data = load_symptoms_data(data_dir)
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
        val_metrics = evaluate_multiclass_classifier(clf, x_val, y_val)

        comparison.append({
            "model_type": name,
            "validation_metrics": val_metrics,
        })

        composite_score = val_metrics["top_3_accuracy"] * 10.0 + val_metrics["macro_f1"]
        if composite_score > best_score:
            best_score = composite_score
            best_name = name

    champion = trained_models[best_name]
    test_metrics = evaluate_multiclass_classifier(champion, x_test, y_test)

    params = champion.get_params()
    clean_params = {k: v for k, v in params.items() if isinstance(v, (int, float, str, bool, type(None)))}

    metadata = ModelMetadata(
        model_id="symptoms_disease_v1",
        model_name="41-Class Disease-Symptom Classifier",
        model_type=best_name,
        version="1.0.0",
        dataset_name="Disease-to-Symptom Benchmark Diagnostic Matrix",
        target_column=data["target_column"],
        feature_columns=data["feature_columns"],
        metrics=test_metrics,
        hyperparameters=clean_params,
        scaler_params={
            "index_to_disease": data["index_to_disease"],
            "disease_to_index": data["disease_to_index"],
        },
        candidate_comparison=comparison,
    )

    if save:
        save_model_bundle(champion, metadata, models_dir=models_dir)

    return champion, metadata
