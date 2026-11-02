"""Feedback buffer for continuous active learning.

Collects clinician-confirmed diagnostic outcomes and high-uncertainty
patient samples for automated model retraining.
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class FeedbackRecord(BaseModel):
    """Schema for a single verified clinical feedback record."""

    sample_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    target_disease: str = Field(..., description="Target model: 'cardio', 'diabetes', or 'symptoms'")
    features: Dict[str, Any] = Field(..., description="Map of feature names to raw/normalized values")
    ground_truth_label: Union[int, str] = Field(..., description="Verified ground truth outcome (0/1 or disease name)")
    source: str = Field(default="clinician_verified", description="Source of outcome verification")
    confidence_at_prediction: Optional[float] = Field(default=None, description="Prior prediction confidence score [0, 100]")
    notes: Optional[str] = Field(default=None, description="Optional clinician rationale or clinical notes")
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class FeedbackBuffer:
    """Manages appending, querying, and archiving continuous feedback records."""

    def __init__(self, base_dir: Optional[Path] = None):
        if base_dir is None:
            # Default to repo root datasets/feedback/
            self.base_dir = Path(__file__).resolve().parents[4] / "datasets" / "feedback"
        else:
            self.base_dir = Path(base_dir)

    def _get_buffer_file(self, target_disease: str) -> Path:
        target_dir = self.base_dir / target_disease
        target_dir.mkdir(parents=True, exist_ok=True)
        return target_dir / "feedback_records.jsonl"

    def add_record(self, record: FeedbackRecord) -> str:
        """Append a new verified feedback record to the target buffer.

        Returns:
            The sample_id of the appended record.
        """
        buffer_file = self._get_buffer_file(record.target_disease)
        record_json = record.model_dump_json()

        with open(buffer_file, "a", encoding="utf-8") as f:
            f.write(record_json + "\n")

        return record.sample_id

    def get_count(self, target_disease: str) -> int:
        """Return the number of un-archived feedback samples currently in buffer."""
        buffer_file = self._get_buffer_file(target_disease)
        if not buffer_file.exists():
            return 0

        count = 0
        with open(buffer_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    count += 1
        return count

    def load_records(self, target_disease: str) -> List[FeedbackRecord]:
        """Load and parse all feedback records from the buffer."""
        buffer_file = self._get_buffer_file(target_disease)
        if not buffer_file.exists():
            return []

        records = []
        with open(buffer_file, "r", encoding="utf-8") as f:
            for line in f:
                line_str = line.strip()
                if line_str:
                    records.append(FeedbackRecord.model_validate_json(line_str))
        return records

    def should_retrain(self, target_disease: str, threshold: int = 20) -> bool:
        """Check whether the accumulated feedback meets or exceeds the trigger threshold."""
        return self.get_count(target_disease) >= threshold

    def archive_and_clear(self, target_disease: str) -> Optional[Path]:
        """Move processed feedback records to an archived timestamped file and clear buffer."""
        buffer_file = self._get_buffer_file(target_disease)
        if not buffer_file.exists() or buffer_file.stat().st_size == 0:
            return None

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        archive_dir = self.base_dir / target_disease / "archived"
        archive_dir.mkdir(parents=True, exist_ok=True)
        archive_file = archive_dir / f"feedback_{timestamp}.jsonl"

        # Rename current buffer file to archive
        buffer_file.rename(archive_file)
        # Create empty buffer file
        buffer_file.touch()

        return archive_file
