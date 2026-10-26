r"""CLI Retraining Script for Biomedical Symptom NER & Semantic Matcher (Step 8.3.3).

Usage:
    backend\.venv\Scripts\python backend\scripts\retrain_nlp_extractor.py
"""

import logging
import sys
from pathlib import Path

# Add backend directory to sys.path
BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.ml.inference.ner_model import BiomedicalSymptomNER
from app.ml.training.ner import train_symptom_ner_model

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("retrain_ner")


def main() -> int:
    logger.info("Starting Biomedical Symptom NER retraining pipeline...")
    try:
        bundle, metadata = train_symptom_ner_model()
        logger.info("Successfully trained symptom NER model '%s' version %s", metadata.model_id, metadata.version)
        logger.info("Training Samples: %d across %d canonical classes", bundle["total_phrases"], bundle["total_classes"])

        metrics = metadata.metrics
        print("\n" + "=" * 65)
        print("    MEDORACLE BIOMEDICAL SYMPTOM NER BENCHMARK REPORT")
        print("=" * 65)
        print(f"  Model ID:            {metadata.model_id}")
        print(f"  Algorithm:           {metadata.model_type}")
        print(f"  Total Test Spans:    {metrics.get('total_test_spans', 0)}")
        print(f"  Top-1 Accuracy:      {metrics.get('top_1_accuracy', 0.0) * 100:.2f}%")
        print(f"  Top-3 Accuracy:      {metrics.get('top_3_accuracy', 0.0) * 100:.2f}%")
        print(f"  Precision:           {metrics.get('precision', 0.0):.4f}")
        print(f"  Recall:              {metrics.get('recall', 0.0):.4f}")
        print(f"  F1-Score:            {metrics.get('f1_score', 0.0):.4f}")
        print("=" * 65 + "\n")

        # Hot-reload in-memory inference singleton
        BiomedicalSymptomNER.get_instance().reload()
        logger.info("Reloaded BiomedicalSymptomNER in-memory singleton. Ready for live inference.")
        return 0
    except Exception as e:
        logger.exception("Failed to retrain symptom NER model: %s", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
