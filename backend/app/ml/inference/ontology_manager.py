"""Dynamic Symptom Vocabulary & Ontology Expansion Engine (Step 8.3.2).

Provides:
1. DynamicOntologyManager: Thread-safe, disk-backed store for dynamic clinician-approved
   synonyms mapping colloquial phrases to MedOracle's 132 canonical symptoms.
2. UnmappedPhraseBuffer: Logs unrecognized patient phrases, tracks frequency, and
   computes semantic candidate matches to support active learning vocabulary expansion.
"""

from datetime import datetime, timezone
import difflib
import json
import logging
from pathlib import Path
import threading
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger("ontology_manager")

WORKSPACE_ROOT = Path(__file__).resolve().parents[4]
METADATA_DIR = WORKSPACE_ROOT / "datasets" / "metadata"
FEEDBACK_DIR = WORKSPACE_ROOT / "datasets" / "feedback"

DEFAULT_ONTOLOGY_FILE = METADATA_DIR / "dynamic_symptom_ontology.json"
DEFAULT_UNMAPPED_FILE = FEEDBACK_DIR / "unmapped_symptom_phrases.json"

# Common non-clinical English stopwords to ignore when analyzing unrecognized text
CLINICAL_STOPWORDS: Set[str] = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for", "of",
    "with", "by", "from", "up", "about", "into", "over", "after", "is", "are",
    "was", "were", "be", "been", "being", "have", "has", "had", "do", "does",
    "did", "can", "could", "should", "would", "may", "might", "must", "i",
    "me", "my", "myself", "we", "our", "you", "your", "he", "him", "his",
    "she", "her", "it", "its", "they", "them", "their", "this", "that", "these",
    "those", "am", "patient", "presents", "states", "feels", "feeling", "felt",
    "reports", "reported", "history", "ago", "since", "yesterday", "today",
    "week", "weeks", "month", "months", "day", "days", "times", "severe", "mild",
    "moderate", "very", "somewhat", "quite", "really", "almost", "non", "also",
    "complains", "complained", "complaining", "complaint", "experiences", "experiencing",
    "noted", "noting", "noticed", "suffering",
}


def utc_iso_now() -> str:
    """Return current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()


class DynamicOntologyManager:
    """Thread-safe manager for dynamic symptom synonyms."""

    _instance: Optional["DynamicOntologyManager"] = None
    _lock = threading.Lock()

    def __init__(self, persistence_file: Path = DEFAULT_ONTOLOGY_FILE):
        self.persistence_file = Path(persistence_file)
        self._synonyms: Dict[str, str] = {}
        self._metadata: Dict[str, Dict[str, Any]] = {}
        self._rw_lock = threading.RLock()
        self._load()

    @classmethod
    def get_instance(cls, persistence_file: Path = DEFAULT_ONTOLOGY_FILE) -> "DynamicOntologyManager":
        """Singleton accessor."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls(persistence_file)
            return cls._instance

    def _load(self) -> None:
        """Load dynamic ontology from disk if present."""
        with self._rw_lock:
            if self.persistence_file.exists():
                try:
                    with open(self.persistence_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        self._synonyms = data.get("synonyms", {})
                        self._metadata = data.get("metadata", {})
                        logger.info("Loaded %d dynamic synonyms from %s", len(self._synonyms), self.persistence_file)
                except Exception as e:
                    logger.warning("Failed to load dynamic ontology: %s. Starting empty.", e)
                    self._synonyms = {}
                    self._metadata = {}
            else:
                self._synonyms = {}
                self._metadata = {}

    def _save(self) -> None:
        """Persist dynamic ontology to disk."""
        with self._rw_lock:
            try:
                self.persistence_file.parent.mkdir(parents=True, exist_ok=True)
                payload = {
                    "version": "1.0.0",
                    "updated_at": utc_iso_now(),
                    "total_synonyms": len(self._synonyms),
                    "synonyms": self._synonyms,
                    "metadata": self._metadata,
                }
                with open(self.persistence_file, "w", encoding="utf-8") as f:
                    json.dump(payload, f, indent=2, ensure_ascii=False)
            except Exception as e:
                logger.error("Failed to save dynamic ontology to %s: %s", self.persistence_file, e)

    def register_synonym(
        self,
        phrase: str,
        canonical_symptom: str,
        clinical_notes: Optional[str] = None,
        source: str = "clinician_approval",
    ) -> bool:
        """Register a new phrase mapping to a canonical symptom."""
        cleaned_phrase = phrase.strip().lower()
        cleaned_canonical = canonical_symptom.strip().lower()

        if not cleaned_phrase or not cleaned_canonical:
            return False

        with self._rw_lock:
            self._synonyms[cleaned_phrase] = cleaned_canonical
            self._metadata[cleaned_phrase] = {
                "canonical_symptom": cleaned_canonical,
                "registered_at": utc_iso_now(),
                "clinical_notes": clinical_notes,
                "source": source,
            }
            self._save()
            logger.info("Registered dynamic synonym: '%s' -> '%s'", cleaned_phrase, cleaned_canonical)
            return True

    def remove_synonym(self, phrase: str) -> bool:
        """Remove a dynamic synonym."""
        cleaned_phrase = phrase.strip().lower()
        with self._rw_lock:
            if cleaned_phrase in self._synonyms:
                del self._synonyms[cleaned_phrase]
                self._metadata.pop(cleaned_phrase, None)
                self._save()
                return True
            return False

    def get_synonyms(self) -> Dict[str, str]:
        """Return a copy of all active dynamic synonyms."""
        with self._rw_lock:
            return dict(self._synonyms)

    def get_metadata(self) -> Dict[str, Dict[str, Any]]:
        """Return metadata for dynamic synonyms."""
        with self._rw_lock:
            return dict(self._metadata)

    def clear(self) -> None:
        """Clear all dynamic synonyms."""
        with self._rw_lock:
            self._synonyms.clear()
            self._metadata.clear()
            self._save()


class UnmappedPhraseBuffer:
    """Thread-safe active learning buffer recording unmapped symptom phrases."""

    _instance: Optional["UnmappedPhraseBuffer"] = None
    _lock = threading.Lock()

    def __init__(
        self,
        persistence_file: Path = DEFAULT_UNMAPPED_FILE,
        ontology_manager: Optional[DynamicOntologyManager] = None,
    ):
        self.persistence_file = Path(persistence_file)
        self.ontology_manager = ontology_manager or DynamicOntologyManager.get_instance()
        self._buffer: Dict[str, Dict[str, Any]] = {}
        self._rw_lock = threading.RLock()
        self._load()

    @classmethod
    def get_instance(
        cls,
        persistence_file: Path = DEFAULT_UNMAPPED_FILE,
        ontology_manager: Optional[DynamicOntologyManager] = None,
    ) -> "UnmappedPhraseBuffer":
        """Singleton accessor."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls(persistence_file, ontology_manager=ontology_manager)
            return cls._instance

    def _load(self) -> None:
        """Load unmapped phrases buffer from disk."""
        with self._rw_lock:
            if self.persistence_file.exists():
                try:
                    with open(self.persistence_file, "r", encoding="utf-8") as f:
                        self._buffer = json.load(f)
                except Exception as e:
                    logger.warning("Failed to load unmapped phrase buffer: %s. Starting empty.", e)
                    self._buffer = {}
            else:
                self._buffer = {}

    def _save(self) -> None:
        """Persist unmapped buffer to disk."""
        with self._rw_lock:
            try:
                self.persistence_file.parent.mkdir(parents=True, exist_ok=True)
                with open(self.persistence_file, "w", encoding="utf-8") as f:
                    json.dump(self._buffer, f, indent=2, ensure_ascii=False)
            except Exception as e:
                logger.error("Failed to save unmapped phrases to %s: %s", self.persistence_file, e)

    def record_unmapped_phrase(self, phrase: str, reference_lexicon: Optional[Dict[str, str]] = None) -> None:
        """Record an unrecognized symptom phrase and calculate candidate matches."""
        cleaned = phrase.strip().lower()
        # Skip pure stopwords or tiny tokens
        if not cleaned or len(cleaned) < 3 or cleaned in CLINICAL_STOPWORDS:
            return

        with self._rw_lock:
            now_str = utc_iso_now()
            if cleaned in self._buffer:
                self._buffer[cleaned]["occurrence_count"] += 1
                self._buffer[cleaned]["last_seen"] = now_str
            else:
                suggestions = self._find_suggested_matches(cleaned, reference_lexicon)
                self._buffer[cleaned] = {
                    "phrase": cleaned,
                    "occurrence_count": 1,
                    "first_seen": now_str,
                    "last_seen": now_str,
                    "suggested_matches": suggestions,
                }
            self._save()

    def _find_suggested_matches(
        self, phrase: str, reference_lexicon: Optional[Dict[str, str]] = None, top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """Find top-k closest canonical symptom targets using fuzzy similarity."""
        if not reference_lexicon:
            return []

        candidates = []
        for target_phrase, canonical in reference_lexicon.items():
            ratio = difflib.SequenceMatcher(None, phrase, target_phrase).ratio()
            if ratio >= 0.40:
                candidates.append({
                    "canonical_symptom": canonical,
                    "similarity_score": round(ratio, 3),
                    "reference_phrase": target_phrase,
                })

        # Sort descending by similarity score and take top_k unique canonicals
        candidates.sort(key=lambda x: x["similarity_score"], reverse=True)
        unique_matches: List[Dict[str, Any]] = []
        seen_canonicals: Set[str] = set()

        for c in candidates:
            if c["canonical_symptom"] not in seen_canonicals:
                seen_canonicals.add(c["canonical_symptom"])
                unique_matches.append(c)
            if len(unique_matches) >= top_k:
                break

        return unique_matches

    def list_unmapped_phrases(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List unmapped phrases sorted by occurrence frequency."""
        with self._rw_lock:
            items = list(self._buffer.values())
            items.sort(key=lambda x: x["occurrence_count"], reverse=True)
            return items[:limit]

    def resolve_unmapped_phrase(self, phrase: str) -> bool:
        """Remove a phrase from unmapped buffer upon clinician approval or dismissal."""
        cleaned = phrase.strip().lower()
        with self._rw_lock:
            if cleaned in self._buffer:
                del self._buffer[cleaned]
                self._save()
                return True
            return False

    def clear(self) -> None:
        """Clear all buffer records."""
        with self._rw_lock:
            self._buffer.clear()
            self._save()
