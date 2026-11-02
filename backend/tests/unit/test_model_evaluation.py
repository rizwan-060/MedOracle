"""Unit tests for ML evaluation metrics and model evaluation runner."""

import pytest
from app.ml.evaluation.metrics import evaluate_binary_classifier, evaluate_multiclass_classifier
from scripts.evaluate_models import (
    evaluate_cardiovascular_model,
    evaluate_diabetes_model,
    evaluate_symptoms_model,
    run_all_evaluations,
)


def test_evaluate_binary_classifier_perfect():
    """Verify metrics computation with a perfect binary classifier."""
    y_true = [0, 0, 1, 1]
    y_pred = [0, 0, 1, 1]
    y_prob = [0.05, 0.1, 0.9, 0.95]

    res = evaluate_binary_classifier(y_true, y_pred, y_prob)

    assert res["accuracy"] == 1.0
    assert res["precision"] == 1.0
    assert res["recall"] == 1.0
    assert res["f1"] == 1.0
    assert res["roc_auc"] == 1.0
    assert res["pr_auc"] == 1.0
    assert res["specificity"] == 1.0
    assert res["brier_score"] < 0.05
    assert res["confusion_matrix"]["true_positive"] == 2
    assert res["confusion_matrix"]["true_negative"] == 2
    assert res["confusion_matrix"]["false_positive"] == 0
    assert res["confusion_matrix"]["false_negative"] == 0


def test_evaluate_binary_classifier_mixed():
    """Verify metrics computation with mixed predictions and errors."""
    y_true = [0, 0, 1, 1]
    y_pred = [0, 1, 0, 1]  # 1 FP, 1 FN
    y_prob = [0.2, 0.7, 0.3, 0.8]

    res = evaluate_binary_classifier(y_true, y_pred, y_prob)

    assert res["accuracy"] == 0.5
    assert res["precision"] == 0.5
    assert res["recall"] == 0.5
    assert res["f1"] == 0.5
    assert res["specificity"] == 0.5
    assert res["confusion_matrix"]["true_negative"] == 1
    assert res["confusion_matrix"]["false_positive"] == 1
    assert res["confusion_matrix"]["false_negative"] == 1
    assert res["confusion_matrix"]["true_positive"] == 1


def test_evaluate_binary_classifier_single_class_edge_case():
    """Verify handling when all true labels belong to a single class."""
    y_true = [0, 0, 0, 0]
    y_pred = [0, 0, 0, 0]
    y_prob = [0.1, 0.15, 0.2, 0.05]

    res = evaluate_binary_classifier(y_true, y_pred, y_prob)

    assert res["accuracy"] == 1.0
    assert res["roc_auc"] == 0.5  # Fallback value when ROC AUC is undefined
    assert res["pr_auc"] == 0.0
    assert res["confusion_matrix"]["true_negative"] == 4


def test_evaluate_multiclass_classifier_synthetic():
    """Verify multiclass metrics with top-k ranking calculation."""
    y_true = [0, 1, 2]
    y_pred = [0, 1, 1]  # Last sample predicted 1 instead of 2
    # Probabilities:
    # Sample 0: [0.7, 0.2, 0.1] -> True 0 is rank 1
    # Sample 1: [0.1, 0.8, 0.1] -> True 1 is rank 1
    # Sample 2: [0.1, 0.5, 0.4] -> True 2 is rank 2 (in top 2 and top 3)
    y_prob = [
        [0.7, 0.2, 0.1],
        [0.1, 0.8, 0.1],
        [0.1, 0.5, 0.4],
    ]
    labels = [0, 1, 2]

    res = evaluate_multiclass_classifier(y_true, y_pred, y_prob, labels=labels)

    assert res["accuracy"] == pytest.approx(0.6667, abs=1e-3)
    assert res["top_1_accuracy"] == pytest.approx(0.6667, abs=1e-3)
    assert res["top_3_accuracy"] == 1.0  # True class is in top 3 for all samples
    assert res["num_classes"] == 3
    assert "classification_report" in res


def test_evaluate_cardiovascular_model_test_split():
    """Verify champion cardiovascular model evaluation on held-out test data."""
    res = evaluate_cardiovascular_model()
    assert res["model_id"] == "cardiovascular_risk_v1"
    assert res["sample_count"] == 48
    assert res["metrics"]["accuracy"] >= 0.75
    assert res["metrics"]["roc_auc"] >= 0.80
    assert res["metrics"]["brier_score"] <= 0.25


def test_evaluate_diabetes_model_test_split():
    """Verify champion diabetes model evaluation on held-out test data."""
    res = evaluate_diabetes_model()
    assert res["model_id"] == "diabetes_risk_v1"
    assert res["sample_count"] == 116
    assert res["metrics"]["accuracy"] >= 0.70
    assert res["metrics"]["roc_auc"] >= 0.80
    assert res["metrics"]["brier_score"] <= 0.25


def test_evaluate_symptoms_model_test_split():
    """Verify champion symptoms diagnostic model evaluation on held-out test data."""
    res = evaluate_symptoms_model()
    assert res["model_id"] == "symptoms_disease_v1"
    assert res["sample_count"] == 738
    assert res["metrics"]["top_1_accuracy"] >= 0.95
    assert res["metrics"]["top_3_accuracy"] >= 0.98
    assert res["metrics"]["top_5_accuracy"] >= 0.99


def test_run_all_evaluations():
    """Verify full evaluation suite runs and aggregates all model metrics."""
    results = run_all_evaluations()
    assert "cardiovascular" in results
    assert "diabetes" in results
    assert "symptoms" in results
