"""Versioned Event Schemas for Live Agent Debate Event Infrastructure (Step 12.5.1)."""

from datetime import datetime, timezone
from enum import Enum
import json
import re
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field, field_validator


SUPPORTED_EVENT_SCHEMA_MAJOR = "1"
_SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
_FORBIDDEN_PAYLOAD_KEYS = frozenset({
    "chain_of_thought",
    "raw_llm_prompt",
    "system_prompt",
    "private_reasoning",
    "hidden_reasoning",
})


class EventType(str, Enum):
    """Standardized machine-readable taxonomy for multi-agent debate lifecycle events."""

    # Session Lifecycle
    SESSION_CREATED = "session_created"
    DEBATE_STARTED = "debate_started"
    DEBATE_COMPLETED = "debate_completed"
    DEBATE_FAILED = "debate_failed"
    DEBATE_TIMED_OUT = "debate_timed_out"

    # Specialist Agent Lifecycle (Step 11)
    AGENT_ACTIVATED = "agent_activated"
    AGENT_ANALYSIS_STARTED = "agent_analysis_started"
    AGENT_ANALYSIS_COMPLETED = "agent_analysis_completed"
    AGENT_CLAIM_SUBMITTED = "agent_claim_submitted"

    # Contradiction Detection Lifecycle (Step 12.1)
    CONTRADICTION_DETECTED = "contradiction_detected"
    CONTRADICTION_CLASSIFIED = "contradiction_classified"
    CONTRADICTION_REVIEWED = "contradiction_reviewed"

    # Adversarial Debate Lifecycle (Step 12.2)
    CHALLENGE_SUBMITTED = "challenge_submitted"
    REBUTTAL_SUBMITTED = "rebuttal_submitted"
    CLAIM_DEFENDED = "claim_defended"
    CLAIM_REVISED = "claim_revised"
    CLAIM_CONCEDED = "claim_conceded"
    EVIDENCE_VALIDATION_COMPLETED = "evidence_validation_completed"
    DEBATE_ROUND_COMPLETED = "debate_round_completed"

    # Confidence Recalibration Lifecycle (Step 12.3)
    CONFIDENCE_RECALIBRATION_STARTED = "confidence_recalibration_started"
    CONFIDENCE_RECALIBRATION_COMPLETED = "confidence_recalibration_completed"
    EPISTEMIC_DOUBT_CALCULATED = "epistemic_doubt_calculated"

    # Consensus Resolution Lifecycle (Step 12.4)
    CONSENSUS_RESOLUTION_STARTED = "consensus_resolution_started"
    CONSENSUS_REACHED = "consensus_reached"
    CONSENSUS_PARTIAL = "consensus_partial"
    CONSENSUS_UNRESOLVED = "consensus_unresolved"
    UNSUPPORTED_DIVERGENCE = "unsupported_divergence"
    FINAL_VERDICT_GENERATED = "final_verdict_generated"


class EventStatus(str, Enum):
    """Operational or clinical severity status of a debate event."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    COMPLETED = "completed"
    FAILED = "failed"


class DebateEvent(BaseModel):
    """Authoritative, versioned event contract for live agent debate observation."""

    event_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Globally unique RFC 4122 v4 UUID for this event.",
    )
    schema_version: str = Field(
        default="1.0.0",
        description="SemVer version of the event schema contract.",
    )
    session_id: str = Field(
        ...,
        min_length=1,
        description="AnalysisSession identifier this event belongs to.",
    )
    patient_id: Optional[str] = Field(
        default=None,
        description="Internal patient/user UUID (never raw patient PII/name).",
    )
    sequence_number: int = Field(
        ...,
        ge=1,
        description="Strictly monotonic, 1-indexed sequence integer per session.",
    )
    event_type: EventType = Field(
        ...,
        description="Standardized event taxonomy type.",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timezone-aware UTC timestamp of event generation.",
    )
    agent_role: Optional[str] = Field(
        default=None,
        description="Specialist agent role responsible for the event.",
    )
    target_agent_role: Optional[str] = Field(
        default=None,
        description="Opposing agent role targeted (for challenges/rebuttals).",
    )
    round_number: Optional[int] = Field(
        default=None,
        ge=1,
        le=2,
        description="Adversarial debate round number (1 or 2).",
    )
    claim_id: Optional[str] = Field(
        default=None,
        description="Identifier of the clinical claim affected.",
    )
    evidence_references: List[str] = Field(
        default_factory=list,
        description="Canonical analyte or guideline keys grounded in this event.",
    )
    status: EventStatus = Field(
        default=EventStatus.INFO,
        description="Operational or clinical severity status.",
    )
    payload: Dict[str, Any] = Field(
        default_factory=dict,
        description="Structured, sanitized event-specific data payload.",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Optional non-sensitive execution metadata.",
    )

    model_config = ConfigDict(from_attributes=True)

    @field_validator("schema_version")
    @classmethod
    def validate_schema_version(cls, value: str) -> str:
        if not _SEMVER_RE.match(value):
            raise ValueError(f"schema_version '{value}' must follow SemVer 'X.Y.Z'")
        major = value.split(".")[0]
        if major != SUPPORTED_EVENT_SCHEMA_MAJOR:
            raise ValueError(
                f"Incompatible schema_version '{value}'; supported major version is {SUPPORTED_EVENT_SCHEMA_MAJOR}.x.x"
            )
        return value

    @field_validator("session_id")
    @classmethod
    def validate_session_id(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("session_id cannot be empty or whitespace")
        return cleaned

    @field_validator("timestamp", mode="before")
    @classmethod
    def validate_timestamp(cls, value: Any) -> datetime:
        if isinstance(value, str):
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        elif isinstance(value, datetime):
            dt = value
        else:
            raise ValueError("timestamp must be an ISO 8601 string or datetime")
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)

    @field_validator("payload")
    @classmethod
    def validate_payload_sanitized(cls, value: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(value, dict):
            raise ValueError("payload must be a dictionary")
        forbidden = _FORBIDDEN_PAYLOAD_KEYS.intersection({str(k).lower() for k in value.keys()})
        if forbidden:
            raise ValueError(
                f"payload contains forbidden internal reasoning keys: {sorted(forbidden)}"
            )
        return value

    def to_sse_frame(self) -> str:
        """Format event as a standard Server-Sent Events (SSE) wire frame."""
        data_json = json.dumps(self.model_dump(mode="json"), separators=(",", ":"), default=str)
        return f"id: {self.sequence_number}\nevent: {self.event_type.value}\ndata: {data_json}\n\n"
