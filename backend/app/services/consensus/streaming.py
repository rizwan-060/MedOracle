"""Database-backed EventPublisher and asyncio LiveEventHub for Step 12.5.2 SSE streaming."""

import asyncio
from collections import defaultdict
import logging
import threading
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
from sqlalchemy.orm import Session

from app.database.repositories import DebateEventRepository
from app.schemas.debate_events import DebateEvent, EventStatus, EventType

logger = logging.getLogger("services.consensus.streaming")


class LiveEventHub:
    """Thread-safe pub/sub hub dispatching live DebateEvents to active SSE asyncio queues."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._subscribers: Dict[str, Set[Tuple[asyncio.Queue, Optional[asyncio.AbstractEventLoop]]]] = defaultdict(set)

    def subscribe(self, session_id: str) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue()
        try:
            loop: Optional[asyncio.AbstractEventLoop] = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        with self._lock:
            self._subscribers[session_id].add((queue, loop))
        return queue

    def unsubscribe(self, session_id: str, queue: asyncio.Queue) -> None:
        with self._lock:
            subs = self._subscribers.get(session_id)
            if not subs:
                return
            to_remove = [item for item in subs if item[0] is queue]
            for item in to_remove:
                subs.discard(item)
            if not subs:
                self._subscribers.pop(session_id, None)

    def broadcast(self, session_id: str, event: DebateEvent) -> None:
        with self._lock:
            targets = list(self._subscribers.get(session_id, ()))
        for queue, loop in targets:
            try:
                if loop is not None and loop.is_running():
                    loop.call_soon_threadsafe(queue.put_nowait, event)
                else:
                    queue.put_nowait(event)
            except Exception as exc:
                logger.warning("Failed to enqueue live event for session %s: %s", session_id, exc)


_DEFAULT_EVENT_HUB = LiveEventHub()


def get_live_event_hub() -> LiveEventHub:
    """Return the singleton LiveEventHub instance."""
    return _DEFAULT_EVENT_HUB


class DatabaseEventPublisher:
    """Durable PostgreSQL-backed EventPublisher with live SSE hub fan-out."""

    def __init__(
        self,
        session_factory: Callable[[], Session],
        hub: Optional[LiveEventHub] = None,
    ) -> None:
        self._session_factory = session_factory
        self._hub = hub or get_live_event_hub()

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
        # Validate event contract before persistence (sanitized payload, valid SemVer, etc.)
        validated = DebateEvent(
            session_id=session_id,
            patient_id=patient_id,
            sequence_number=1,  # Assigned atomically by DebateEventRepository
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

        db = self._session_factory()
        try:
            repo = DebateEventRepository(db)
            record = repo.append_event(
                event_id=validated.event_id,
                session_id=validated.session_id,
                schema_version=validated.schema_version,
                event_type=validated.event_type.value,
                status=validated.status.value,
                payload=validated.payload,
                evidence_references=validated.evidence_references,
                event_metadata=validated.metadata,
                agent_role=validated.agent_role,
                target_agent_role=validated.target_agent_role,
                round_number=validated.round_number,
                claim_id=validated.claim_id,
                created_at=validated.timestamp,
            )
            persisted_event = DebateEvent(
                event_id=record.id,
                schema_version=record.schema_version,
                session_id=record.session_id,
                patient_id=patient_id,
                sequence_number=record.sequence_number,
                event_type=EventType(record.event_type),
                timestamp=record.created_at,
                agent_role=record.agent_role,
                target_agent_role=record.target_agent_role,
                round_number=record.round_number,
                claim_id=record.claim_id,
                evidence_references=record.evidence_references or [],
                status=EventStatus(record.status),
                payload=record.payload or {},
                metadata=record.event_metadata or {},
            )
        finally:
            db.close()

        self._hub.broadcast(session_id, persisted_event)
        return persisted_event

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

