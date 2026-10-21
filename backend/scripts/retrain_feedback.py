"""CLI Script for continuous active learning model retraining in MedOracle.

Usage:
    python backend/scripts/retrain_feedback.py --target all --force
    python backend/scripts/retrain_feedback.py --target cardio --min-samples 10
    python backend/scripts/retrain_feedback.py --target diabetes
    python backend/scripts/retrain_feedback.py --target symptoms
"""

import argparse
import sys
from pathlib import Path

# Add backend directory to sys.path
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.database.session import SessionLocal
from app.ml.feedback.buffer import FeedbackBuffer
from app.ml.feedback.retrainer import ContinuousRetrainer


def run_retraining(target: str, min_samples: int, force: bool, sync_db: bool):
    """Execute active learning evaluation and continuous retraining."""
    print("=" * 70)
    print("MEDORACLE CONTINUOUS ACTIVE LEARNING RETRAINING RUNNER")
    print("=" * 70)

    buffer = FeedbackBuffer()
    retrainer = ContinuousRetrainer(buffer=buffer)

    db_session = SessionLocal() if sync_db else None

    targets = ["cardio", "diabetes", "symptoms"] if target == "all" else [target]

    try:
        for idx, t in enumerate(targets, 1):
            count = buffer.get_count(t)
            print(f"\n[{idx}/{len(targets)}] Evaluating Target Domain: {t.upper()}")
            print(f"  - Pending Feedback Records in Buffer: {count}")
            print(f"  - Retraining Threshold: {min_samples} (Force Mode: {force})")
            print("-" * 70)

            result = retrainer.retrain_model(
                target_disease=t,
                min_samples=min_samples,
                force=force,
                db_session=db_session,
            )

            if result.success and result.promoted:
                print(f"  >>> SUCCESS: Model Promoted to v{result.new_version}!")
                print(f"  - Samples Used: {result.samples_used}")
                print("  - Updated Test Metrics:")
                for k, v in result.retrained_metrics.items():
                    print(f"      {k.upper():<16}: {v:.4f}")
                print(f"  - Artifact Saved: {result.artifact_path}")
            elif result.success and not result.promoted:
                print("  >>> PROMOTION REJECTED (Performance Gate Protected Champion):")
                print(f"  - Reason: {result.rejection_reason}")
                print("  - Retrained Test Metrics:")
                for k, v in result.retrained_metrics.items():
                    print(f"      {k.upper():<16}: {v:.4f}")
            else:
                print(f"  >>> SKIPPED: {result.message}")

    finally:
        if db_session:
            db_session.close()

    print("\n" + "=" * 70)
    print("ACTIVE LEARNING EVALUATION RUN COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MedOracle Active Learning Retraining Runner")
    parser.add_argument(
        "--target",
        choices=["cardio", "diabetes", "symptoms", "all"],
        default="all",
        help="Target model domain to retrain (default: all)",
    )
    parser.add_argument(
        "--min-samples",
        type=int,
        default=5,
        help="Minimum number of verified feedback samples required (default: 5)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force retraining regardless of buffer size",
    )
    parser.add_argument(
        "--sync-db",
        action="store_true",
        help="Sync model registry state to relational database",
    )
    args = parser.parse_args()

    run_retraining(
        target=args.target,
        min_samples=args.min_samples,
        force=args.force,
        sync_db=args.sync_db,
    )
