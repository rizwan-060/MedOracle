"""CLI Script for training MedOracle supervised machine learning models.

Usage:
    python backend/scripts/train_models.py --target all
    python backend/scripts/train_models.py --target cardio
    python backend/scripts/train_models.py --target diabetes
    python backend/scripts/train_models.py --target symptoms
"""

import argparse
import sys
from pathlib import Path

# Add backend directory to sys.path so app modules are resolvable
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.ml.training.cardiovascular import train_cardiovascular_model
from app.ml.training.diabetes import train_diabetes_model
from app.ml.training.symptoms import train_symptoms_model


def run_training(target: str):
    """Execute training for specified target models."""
    print("=" * 70)
    print("MEDORACLE MACHINE LEARNING MODEL TRAINING PIPELINE")
    print("=" * 70)

    if target in ("cardio", "all"):
        print("\n[1/3] Training Cardiovascular Disease Models (UCI Heart Dataset)...")
        print("-" * 70)
        clf_cardio, meta_cardio = train_cardiovascular_model(save=True)
        print(f"Selected Champion Model: {meta_cardio.model_type}")
        print("Candidate Validation Comparison:")
        for cand in meta_cardio.candidate_comparison:
            vm = cand["validation_metrics"]
            print(f"  - {cand['model_type']:<28} ROC-AUC: {vm['roc_auc']:.4f} | F1: {vm['f1']:.4f} | Acc: {vm['accuracy']:.4f}")
        print("\nTest Set Evaluation:")
        for k, v in meta_cardio.metrics.items():
            print(f"  - {k.upper():<10}: {v:.4f}")
        print(f"Artifact Saved: models/saved/{meta_cardio.artifact_filename}")

    if target in ("diabetes", "all"):
        print("\n[2/3] Training Type 2 Diabetes Models (PIMA Indians Dataset)...")
        print("-" * 70)
        clf_diab, meta_diab = train_diabetes_model(save=True)
        print(f"Selected Champion Model: {meta_diab.model_type}")
        print("Candidate Validation Comparison:")
        for cand in meta_diab.candidate_comparison:
            vm = cand["validation_metrics"]
            print(f"  - {cand['model_type']:<28} ROC-AUC: {vm['roc_auc']:.4f} | F1: {vm['f1']:.4f} | Acc: {vm['accuracy']:.4f}")
        print("\nTest Set Evaluation:")
        for k, v in meta_diab.metrics.items():
            print(f"  - {k.upper():<10}: {v:.4f}")
        print(f"Artifact Saved: models/saved/{meta_diab.artifact_filename}")

    if target in ("symptoms", "all"):
        print("\n[3/3] Training 41-Class Disease-Symptom Models (Diagnostic Matrix)...")
        print("-" * 70)
        clf_symp, meta_symp = train_symptoms_model(save=True)
        print(f"Selected Champion Model: {meta_symp.model_type}")
        print("Candidate Validation Comparison:")
        for cand in meta_symp.candidate_comparison:
            vm = cand["validation_metrics"]
            print(f"  - {cand['model_type']:<28} Top-3 Acc: {vm['top_3_accuracy']:.4f} | Macro F1: {vm['macro_f1']:.4f} | Acc: {vm['accuracy']:.4f}")
        print("\nTest Set Evaluation:")
        for k, v in meta_symp.metrics.items():
            print(f"  - {k.upper():<16}: {v:.4f}")
        print(f"Artifact Saved: models/saved/{meta_symp.artifact_filename}")

    print("\n" + "=" * 70)
    print("TRAINING PIPELINE COMPLETE - ALL CHAMPIONS REGISTERED")
    print("=" * 70)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MedOracle ML Training Runner")
    parser.add_argument(
        "--target",
        choices=["cardio", "diabetes", "symptoms", "all"],
        default="all",
        help="Target model(s) to train (default: all)",
    )
    args = parser.parse_args()
    run_training(args.target)
