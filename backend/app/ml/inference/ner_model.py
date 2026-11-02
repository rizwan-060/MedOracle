"""Biomedical Symptom NER & Semantic Vector Matcher Inference Engine (Step 8.3.3).

Provides low-latency semantic inference:
1. Vectorizes candidate symptom mentions via character and word TF-IDF subword n-grams.
2. Evaluates cosine similarity against 132 canonical symptom centroid vectors.
3. Classifies complex, descriptive, and metaphorical patient symptom phrases that
   bypass simple dictionary lookup.
"""

import logging
from pathlib import Path
import threading
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from app.ml.model_registry import ModelMetadata, load_model_bundle
from app.ml.training.ner import train_symptom_ner_model

logger = logging.getLogger("ner_model")

WORKSPACE_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_MODELS_DIR = WORKSPACE_ROOT / "models" / "saved"


class BiomedicalSymptomNER:
    """Inference engine for biomedical symptom NER and semantic embedding matching."""

    _instance: Optional["BiomedicalSymptomNER"] = None
    _lock = threading.Lock()

    def __init__(self, models_dir: Optional[Path] = None):
        self.models_dir = Path(models_dir) if models_dir else DEFAULT_MODELS_DIR
        self._bundle: Optional[Dict[str, Any]] = None
        self._meta: Optional[ModelMetadata] = None
        self._rw_lock = threading.RLock()
        self._load()

    @classmethod
    def get_instance(cls, models_dir: Optional[Path] = None) -> "BiomedicalSymptomNER":
        """Singleton accessor."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls(models_dir=models_dir)
            return cls._instance

    def _load(self) -> None:
        """Load trained symptom NER model artifact or train initial model if missing."""
        with self._rw_lock:
            artifact_file = self.models_dir / "symptom_ner_v1.joblib"
            if not artifact_file.exists():
                logger.info("symptom_ner_v1 artifact not found at %s. Triggering training pipeline...", artifact_file)
                try:
                    self._bundle, self._meta = train_symptom_ner_model(models_dir=self.models_dir)
                except Exception as e:
                    logger.error("Failed to train symptom NER model: %s", e)
                    self._bundle = None
                    self._meta = None
                    return
            else:
                try:
                    self._bundle, self._meta = load_model_bundle("symptom_ner_v1", models_dir=self.models_dir)
                    logger.info("Loaded symptom_ner_v1 artifact successfully.")
                except Exception as e:
                    logger.error("Failed to load symptom_ner_v1: %s", e)
                    self._bundle = None
                    self._meta = None

    def reload(self) -> None:
        """Reload or refresh model weights from disk."""
        with self._rw_lock:
            self._load()

    @property
    def is_ready(self) -> bool:
        """Return True if model bundle is loaded and functional."""
        with self._rw_lock:
            return self._bundle is not None

    def predict_mention(
        self, phrase: str, threshold: float = 0.30
    ) -> Optional[Tuple[str, float]]:
        """Match an unmapped phrase against 132 canonical symptom centroids and classifier.

        Args:
            phrase: Mention string (e.g., 'tight band around chest', 'air hunger').
            threshold: Minimum similarity/confidence score required.

        Returns:
            Tuple of (canonical_symptom, confidence_score) if above threshold, else None.
        """
        clean_phrase = phrase.strip().lower()
        if not clean_phrase or len(clean_phrase) < 3 or not self.is_ready:
            return None

        with self._rw_lock:
            vectorizer = self._bundle["vectorizer"]
            centroids = self._bundle["canonical_centroids"]
            classes = self._bundle["canonical_classes"]
            classifier = self._bundle.get("classifier")

            try:
                v = vectorizer.transform([clean_phrase])
                v_dense = v.toarray()
                norm = np.linalg.norm(v_dense)
                if norm == 0:
                    return None
                v_norm = v_dense / norm

                # 1. Cosine similarity against 132 centroids
                sims = np.dot(centroids, v_norm.T).flatten()
                best_idx = int(np.argmax(sims))
                best_centroid_class = classes[best_idx]
                best_sim = float(sims[best_idx])

                # 2. Supervised classifier predictions
                clf_pred = None
                clf_prob = 0.0
                if classifier is not None:
                    try:
                        probs = classifier.predict_proba(v)[0]
                        max_prob_idx = int(np.argmax(probs))
                        clf_pred = classifier.classes_[max_prob_idx]
                        clf_prob = float(probs[max_prob_idx])
                    except Exception:
                        pass

                # Agreement boost
                if clf_pred is not None and clf_pred == best_centroid_class:
                    confidence = round(max(best_sim, clf_prob), 3)
                    if confidence >= threshold:
                        return best_centroid_class, confidence

                # High centroid similarity
                if best_sim >= threshold:
                    return best_centroid_class, round(best_sim, 3)

                # High classifier probability
                if clf_prob >= max(0.40, threshold):
                    return clf_pred, round(clf_prob, 3)

                return None
            except Exception as e:
                logger.warning("Error predicting mention '%s': %s", phrase, e)
                return None

    def get_top_k_candidates(
        self, phrase: str, top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """Return top-k candidate canonical symptoms with similarity scores."""
        clean_phrase = phrase.strip().lower()
        if not clean_phrase or not self.is_ready:
            return []

        with self._rw_lock:
            vectorizer = self._bundle["vectorizer"]
            centroids = self._bundle["canonical_centroids"]
            classes = self._bundle["canonical_classes"]

            try:
                v = vectorizer.transform([clean_phrase])
                v_dense = v.toarray()
                norm = np.linalg.norm(v_dense)
                if norm == 0:
                    return []
                v_norm = v_dense / norm

                sims = np.dot(centroids, v_norm.T).flatten()
                top_indices = np.argsort(sims)[::-1][:top_k]

                results = []
                for idx in top_indices:
                    results.append({
                        "canonical_symptom": classes[idx],
                        "similarity_score": round(float(sims[idx]), 3),
                    })
                return results
            except Exception as e:
                logger.warning("Error computing top-k candidates for '%s': %s", phrase, e)
                return []
