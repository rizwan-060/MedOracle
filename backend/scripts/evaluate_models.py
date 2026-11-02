"""CLI Model Evaluation Runner for MedOracle ML Suite.

Evaluates registered champion models on held-out test splits:
1. Cardiovascular Disease Classifier (GradientBoosting on UCI Heart test split)
2. Diabetes Risk Classifier (RandomForest on PIMA Indians test split)
3. 41-Class Disease Diagnostic Classifier (MultinomialNB on Symptoms matrix test split)

Usage:
    python backend/scripts/evaluate_models.py
"""

import csv
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Ensure backend root is on sys.path
SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_ROOT = SCRIPT_DIR.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

WORKSPACE_ROOT = BACKEND_ROOT.parent

from app.ml.evaluation.metrics import evaluate_binary_classifier, evaluate_multiclass_classifier
from app.ml.model_registry import load_model_bundle


def load_test_csv(csv_path: Path, feature_cols: List[str], target_col: str) -> Tuple[List[List[float]], List[int]]:
    """Load feature matrix X and target vector y from a processed CSV file."""
    if not csv_path.exists():
        raise FileNotFoundError(f"Test split file not found at {csv_path}")

    x_rows: List[List[float]] = []
    y_vals: List[int] = []

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            x_rows.append([float(row[col]) for col in feature_cols])
            y_vals.append(int(float(row[target_col])))

    return x_rows, y_vals


def evaluate_cardiovascular_model(models_dir: Path = None, data_dir: Path = None) -> Dict[str, Any]:
    """Evaluate cardiovascular champion model on held-out test set."""
    m_dir = models_dir or (WORKSPACE_ROOT / "models" / "saved")
    d_dir = data_dir or (WORKSPACE_ROOT / "datasets" / "processed" / "heart")

    model, meta = load_model_bundle("cardiovascular_risk_v1", models_dir=m_dir)
    test_csv = d_dir / "test.csv"
    x_test, y_test = load_test_csv(test_csv, meta.feature_columns, meta.target_column)

    y_pred = model.predict(x_test).tolist()
    y_prob = model.predict_proba(x_test)[:, 1].tolist()

    metrics = evaluate_binary_classifier(y_test, y_pred, y_prob)
    return {
        "model_id": meta.model_id,
        "model_name": meta.model_name,
        "algorithm": meta.model_type,
        "sample_count": len(y_test),
        "metrics": metrics,
    }


def evaluate_diabetes_model(models_dir: Path = None, data_dir: Path = None) -> Dict[str, Any]:
    """Evaluate diabetes champion model on held-out test set."""
    m_dir = models_dir or (WORKSPACE_ROOT / "models" / "saved")
    d_dir = data_dir or (WORKSPACE_ROOT / "datasets" / "processed" / "diabetes")

    model, meta = load_model_bundle("diabetes_risk_v1", models_dir=m_dir)
    test_csv = d_dir / "test.csv"
    x_test, y_test = load_test_csv(test_csv, meta.feature_columns, meta.target_column)

    y_pred = model.predict(x_test).tolist()
    y_prob = model.predict_proba(x_test)[:, 1].tolist()

    metrics = evaluate_binary_classifier(y_test, y_pred, y_prob)
    return {
        "model_id": meta.model_id,
        "model_name": meta.model_name,
        "algorithm": meta.model_type,
        "sample_count": len(y_test),
        "metrics": metrics,
    }


def evaluate_symptoms_model(models_dir: Path = None, data_dir: Path = None) -> Dict[str, Any]:
    """Evaluate 41-class disease diagnostic model on held-out test set."""
    m_dir = models_dir or (WORKSPACE_ROOT / "models" / "saved")
    d_dir = data_dir or (WORKSPACE_ROOT / "datasets" / "processed" / "symptoms")

    model, meta = load_model_bundle("symptoms_disease_v1", models_dir=m_dir)
    test_csv = d_dir / "test.csv"
    x_test, y_test = load_test_csv(test_csv, meta.feature_columns, meta.target_column)

    y_pred = model.predict(x_test).tolist()
    y_prob = model.predict_proba(x_test).tolist()

    metrics = evaluate_multiclass_classifier(y_test, y_pred, y_prob)
    return {
        "model_id": meta.model_id,
        "model_name": meta.model_name,
        "algorithm": meta.model_type,
        "sample_count": len(y_test),
        "metrics": metrics,
    }


def run_all_evaluations() -> Dict[str, Any]:
    """Run evaluation protocol for all registered clinical models."""
    print("=" * 80)
    print("MEDORACLE ML CHAMPION MODELS: CLINICAL EVALUATION SUITE")
    print("=" * 80)

    cardio_results = evaluate_cardiovascular_model()
    print(f"\n[1/3] {cardio_results['model_name']} ({cardio_results['algorithm']})")
    print(f"      Held-out Test Samples: {cardio_results['sample_count']}")
    cm = cardio_results["metrics"]
    print(f"      - Accuracy:    {cm['accuracy']:.4f} ({cm['accuracy']*100:.2f}%)")
    print(f"      - Precision:   {cm['precision']:.4f}")
    print(f"      - Recall:      {cm['recall']:.4f}")
    print(f"      - F1 Score:    {cm['f1']:.4f}")
    print(f"      - ROC-AUC:     {cm['roc_auc']:.4f}")
    print(f"      - PR-AUC:      {cm['pr_auc']:.4f}")
    print(f"      - Brier Score: {cm['brier_score']:.4f} (calibration)")
    print(f"      - Specificity: {cm['specificity']:.4f}")
    print(f"      - Confusion:   TN={cm['confusion_matrix']['true_negative']}, "
          f"FP={cm['confusion_matrix']['false_positive']}, "
          f"FN={cm['confusion_matrix']['false_negative']}, "
          f"TP={cm['confusion_matrix']['true_positive']}")

    diabetes_results = evaluate_diabetes_model()
    print(f"\n[2/3] {diabetes_results['model_name']} ({diabetes_results['algorithm']})")
    print(f"      Held-out Test Samples: {diabetes_results['sample_count']}")
    dm = diabetes_results["metrics"]
    print(f"      - Accuracy:    {dm['accuracy']:.4f} ({dm['accuracy']*100:.2f}%)")
    print(f"      - Precision:   {dm['precision']:.4f}")
    print(f"      - Recall:      {dm['recall']:.4f}")
    print(f"      - F1 Score:    {dm['f1']:.4f}")
    print(f"      - ROC-AUC:     {dm['roc_auc']:.4f}")
    print(f"      - PR-AUC:      {dm['pr_auc']:.4f}")
    print(f"      - Brier Score: {dm['brier_score']:.4f} (calibration)")
    print(f"      - Specificity: {dm['specificity']:.4f}")
    print(f"      - Confusion:   TN={dm['confusion_matrix']['true_negative']}, "
          f"FP={dm['confusion_matrix']['false_positive']}, "
          f"FN={dm['confusion_matrix']['false_negative']}, "
          f"TP={dm['confusion_matrix']['true_positive']}")

    symptoms_results = evaluate_symptoms_model()
    print(f"\n[3/3] {symptoms_results['model_name']} ({symptoms_results['algorithm']})")
    print(f"      Held-out Test Samples: {symptoms_results['sample_count']} across {symptoms_results['metrics']['num_classes']} diseases")
    sm = symptoms_results["metrics"]
    print(f"      - Top-1 Diagnostic Accuracy: {sm['top_1_accuracy']:.4f} ({sm['top_1_accuracy']*100:.2f}%)")
    print(f"      - Top-3 Diagnostic Accuracy: {sm['top_3_accuracy']:.4f} ({sm['top_3_accuracy']*100:.2f}%)")
    print(f"      - Top-5 Diagnostic Accuracy: {sm['top_5_accuracy']:.4f} ({sm['top_5_accuracy']*100:.2f}%)")
    print(f"      - Macro F1:                  {sm['macro_f1']:.4f}")
    print(f"      - Weighted F1:               {sm['weighted_f1']:.4f}")

    print("\n" + "=" * 80)
    print("ALL EVALUATIONS COMPLETED SUCCESSFULLY")
    print("=" * 80)

    return {
        "cardiovascular": cardio_results,
        "diabetes": diabetes_results,
        "symptoms": symptoms_results,
    }


if __name__ == "__main__":
    run_all_evaluations()
