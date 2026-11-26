"""Decoupled EventPublisher protocol and implementations for Step 12.5.

Decouples clinical workflow instrumentation from delivery/persistence backends
(in-memory test collection, PostgreSQL persistence, or live SSE broadcast).
"""

from collections import defaultdict
import logging
import threading
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable

from app.schemas.debate_events import DebateEvent, EventStatus, EventType

logger = logging.getLogger("services.consensus.event_publisher")


@runtime_checkable
class EventPublisher(Protocol):
    """Abstract protocol for publishing structured debate events from clinical workflows."""

    def publish(
        self,
        event_type: EventType,
        session_id: str,
        payload: Optional[Dict[str, Any]] = None,
        *,
        patient_id: Optional[str] = None,
        agent_role: Optional[str] = None,
        target_agent_role: Optional[str] = None,
        round_number: Optional[int] = None,
        claim_id: Optional[str] = None,
        evidence_references: Optional[List[str]] = None,
        status: EventStatus = EventStatus.INFO,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> DebateEvent:
        """Synchronously publish an event with a monotonic per-session sequence number."""
        ...

    async def apublish(
        self,
        event_type: EventType,
        session_id: str,
        payload: Optional[Dict[str, Any]] = None,
        *,
        patient_id: Optional[str] = None,
        agent_role: Optional[str] = None,
        target_agent_role: Optional[str] = None,
        round_number: Optional[int] = None,
        claim_id: Optional[str] = None,
        evidence_references: Optional[List[str]] = None,
        status: EventStatus = EventStatus.INFO,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> DebateEvent:
        """Asynchronously publish an event with a monotonic per-session sequence number."""
        ...


class NullEventPublisher:
    """No-op EventPublisher used when live observation is disabled."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._seq: Dict[str, int] = defaultdict(int)

    def publish(
        self,
        event_type: EventType,
        session_id: str,
        payload: Optional[Dict[str, Any]] = None,
        *,
        patient_id: Optional[str] = None,
        agent_role: Optional[str] = None,
        target_agent_role: Optional[str] = None,
        round_number: Optional[int] = None,
        claim_id: Optional[str] = None,
        evidence_references: Optional[List[str]] = None,
        status: EventStatus = EventStatus.INFO,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> DebateEvent:
        with self._lock:
            self._seq[session_id] += 1
            seq = self._seq[session_id]
        return DebateEvent(
            session_id=session_id,
            patient_id=patient_id,
            sequence_number=seq,
            event_type=event_type,
            agent_role=agent_role,
            target_agent_role=target_agent_role,
            round_number=round_number,
            claim_id=claim_id,
            evidence_references=evidence_references or [],
            status=status,
            payload=payload or {},
            metadata=metadata or {},
        )

    async def apublish(self, *args: Any, **kwargs: Any) -> DebateEvent:
        return self.publish(*args, **kwargs)


class InMemoryEventPublisher:
    """Thread-safe, session-isolated in-memory EventPublisher for testing and local inspection."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._seq: Dict[str, int] = defaultdict(int)
        self._events: Dict[str, List[DebateEvent]] = defaultdict(list)

    def publish(
        self,
        event_type: EventType,
        session_id: str,
        payload: Optional[Dict[str, Any]] = None,
        *,
        patient_id: Optional[str] = None,
        agent_role: Optional[str] = None,
        target_agent_role: Optional[str] = None,
        round_number: Optional[int] = None,
        claim_id: Optional[str] = None,
        evidence_references: Optional[List[str]] = None,
        status: EventStatus = EventStatus.INFO,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> DebateEvent:
        with self._lock:
            next_seq = self._seq[session_id] + 1
            event = DebateEvent(
                session_id=session_id,
                patient_id=patient_id,
                sequence_number=next_seq,
                event_type=event_type,
                agent_role=agent_role,
                target_agent_role=target_agent_role,
                round_number=round_number,
                claim_id=claim_id,
                evidence_references=evidence_references or [],
                status=status,
                payload=payload or {},
                metadata=metadata or {},
            )
            self._seq[session_id] = next_seq
            self._events[session_id].append(event)
            return event

    async def apublish(
        self,
        event_type: EventType,
        session_id: str,
        payload: Optional[Dict[str, Any]] = None,
        *,
        patient_id: Optional[str] = None,
        agent_role: Optional[str] = None,
        target_agent_role: Optional[str] = None,
        round_number: Optional[int] = None,
        claim_id: Optional[str] = None,
        evidence_references: Optional[List[str]] = None,
        status: EventStatus = EventStatus.INFO,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> DebateEvent:
        return self.publish(
            event_type=event_type,
            session_id=session_id,
            payload=payload,
            patient_id=patient_id,
            agent_role=agent_role,
            target_agent_role=target_agent_role,
            round_number=round_number,
            claim_id=claim_id,
            evidence_references=evidence_references,
            status=status,
            metadata=metadata,
        )

    def get_events(self, session_id: str, after_sequence: int = 0) -> List[DebateEvent]:
        with self._lock:
            return [e for e in self._events.get(session_id, []) if e.sequence_number > after_sequence]

    def clear(self, session_id: Optional[str] = None) -> None:
        with self._lock:
            if session_id is None:
                self._events.clear()
                self._seq.clear()
            else:
                self._events.pop(session_id, None)
                self._seq.pop(session_id, None)


class PublisherRegistry:
    """Thread-safe registry mapping active session_id -> EventPublisher without polluting LangGraph state."""

    _lock = threading.Lock()
    _publishers: Dict[str, EventPublisher] = {}

    @classmethod
    def register(cls, session_id: str, publisher: EventPublisher) -> None:
        with cls._lock:
            cls._publishers[session_id] = publisher

    @classmethod
    def get(cls, session_id: str) -> Optional[EventPublisher]:
        with cls._lock:
            return cls._publishers.get(session_id)

    @classmethod
    def unregister(cls, session_id: str) -> None:
        with cls._lock:
            cls._publishers.pop(session_id, None)


def safe_publish_event(
    session_id: Optional[str],
    event_type: EventType,
    payload: Optional[Dict[str, Any]] = None,
    *,
    publisher: Optional[EventPublisher] = None,
    patient_id: Optional[str] = None,
    agent_role: Optional[str] = None,
    target_agent_role: Optional[str] = None,
    round_number: Optional[int] = None,
    claim_id: Optional[str] = None,
    evidence_references: Optional[List[str]] = None,
    status: EventStatus = EventStatus.INFO,
    metadata: Optional[Dict[str, Any]] = None,
) -> Optional[DebateEvent]:
    """Publish an event safely; publisher errors are logged and never corrupt clinical execution."""
    if not session_id:
        return None
    target_pub = publisher or PublisherRegistry.get(session_id)
    if target_pub is None:
        return None
    try:
        return target_pub.publish(
            event_type=event_type,
            session_id=session_id,
            payload=payload or {},
            patient_id=patient_id,
            agent_role=agent_role,
            target_agent_role=target_agent_role,
            round_number=round_number,
            claim_id=claim_id,
            evidence_references=evidence_references or [],
            status=status,
            metadata=metadata or {},
        )
    except Exception as exc:
        logger.warning(
            "Non-fatal EventPublisher failure for session %s (%s): %s",
            session_id,
            event_type.value,
            exc,
        )
        return None
