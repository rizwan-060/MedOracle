"""Comprehensive ML Evaluation Metrics for MedOracle.

Implements evaluation protocols for:
1. Binary Clinical Classifiers (Cardiovascular Disease, Diabetes Risk):
   - ROC-AUC, PR-AUC, Accuracy, Precision, Recall, F1 score.
   - Brier Score (probabilistic calibration error).
   - Confusion Matrix (TN, FP, FN, TP).
2. Multi-Class Diagnostic Classifiers (41-Class Disease-Symptom Mapping):
   - Top-1, Top-3, Top-5 differential diagnosis accuracy.
   - Macro and Weighted F1 scores.
   - Per-class classification reports.
"""

from typing import Any, Dict, List, Optional, Sequence
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    brier_score_loss,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    top_k_accuracy_score,
)


def evaluate_binary_classifier(
    y_true: Sequence[int],
    y_pred: Sequence[int],
    y_prob: Sequence[float],
) -> Dict[str, Any]:
    """Calculate comprehensive performance metrics for a binary clinical classifier.

    Args:
        y_true: Ground truth binary labels (0 or 1).
        y_pred: Hard class predictions (0 or 1).
        y_prob: Continuous class probabilities for the positive class (0.0 to 1.0).

    Returns:
        Dictionary containing quantitative evaluation metrics.
    """
    y_true_arr = np.asarray(y_true)
    y_pred_arr = np.asarray(y_pred)
    y_prob_arr = np.asarray(y_prob)

    acc = float(accuracy_score(y_true_arr, y_pred_arr))
    prec = float(precision_score(y_true_arr, y_pred_arr, zero_division=0))
    rec = float(recall_score(y_true_arr, y_pred_arr, zero_division=0))
    f1 = float(f1_score(y_true_arr, y_pred_arr, zero_division=0))

    try:
        val_roc = roc_auc_score(y_true_arr, y_prob_arr)
        roc_auc = 0.5 if np.isnan(val_roc) else float(val_roc)
    except (ValueError, Exception):
        roc_auc = 0.5

    try:
        val_pr = average_precision_score(y_true_arr, y_prob_arr)
        pr_auc = 0.0 if np.isnan(val_pr) else float(val_pr)
    except (ValueError, Exception):
        pr_auc = 0.0

    brier = float(brier_score_loss(y_true_arr, y_prob_arr))
    cm = confusion_matrix(y_true_arr, y_pred_arr, labels=[0, 1]).tolist()

    tn, fp, fn, tp = int(cm[0][0]), int(cm[0][1]), int(cm[1][0]), int(cm[1][1])
    specificity = float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0

    return {
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1": round(f1, 4),
        "roc_auc": round(roc_auc, 4),
        "pr_auc": round(pr_auc, 4),
        "brier_score": round(brier, 4),
        "specificity": round(specificity, 4),
        "confusion_matrix": {
            "true_negative": tn,
            "false_positive": fp,
            "false_negative": fn,
            "true_positive": tp,
            "raw": cm,
        },
    }


def evaluate_multiclass_classifier(
    y_true: Sequence[Any],
    y_pred: Sequence[Any],
    y_prob: Sequence[Sequence[float]],
    labels: Optional[Sequence[Any]] = None,
) -> Dict[str, Any]:
    """Calculate multi-class diagnostic accuracy and differential diagnosis metrics.

    Args:
        y_true: Ground truth class labels.
        y_pred: Top-1 predicted class labels.
        y_prob: Predicted probability distributions across all classes.
        labels: Optional explicit list of class label names/indices.

    Returns:
        Dictionary of multi-class metrics including Top-1, Top-3, Top-5 differential accuracy.
    """
    y_true_arr = np.asarray(y_true)
    y_pred_arr = np.asarray(y_pred)
    y_prob_arr = np.asarray(y_prob)

    acc = float(accuracy_score(y_true_arr, y_pred_arr))
    macro_f1 = float(f1_score(y_true_arr, y_pred_arr, average="macro", zero_division=0))
    weighted_f1 = float(f1_score(y_true_arr, y_pred_arr, average="weighted", zero_division=0))

    all_labels = labels if labels is not None else np.unique(y_true_arr)
    num_classes = len(all_labels)

    top1 = float(top_k_accuracy_score(y_true_arr, y_prob_arr, k=min(1, num_classes), labels=all_labels))
    top3 = float(top_k_accuracy_score(y_true_arr, y_prob_arr, k=min(3, num_classes), labels=all_labels))
    top5 = float(top_k_accuracy_score(y_true_arr, y_prob_arr, k=min(5, num_classes), labels=all_labels))

    report = classification_report(y_true_arr, y_pred_arr, output_dict=True, zero_division=0)

    return {
        "accuracy": round(acc, 4),
        "macro_f1": round(macro_f1, 4),
        "weighted_f1": round(weighted_f1, 4),
        "top_1_accuracy": round(top1, 4),
        "top_3_accuracy": round(top3, 4),
        "top_5_accuracy": round(top5, 4),
        "num_classes": num_classes,
        "classification_report": report,
    }
