"""Unit tests for Step 12.5.1 — Backend Event Architecture & LangGraph Instrumentation."""

from datetime import datetime, timezone
import pytest
from pydantic import ValidationError

from app.graph import create_initial_graph_state, run_clinical_graph
from app.schemas.debate_events import DebateEvent, EventStatus, EventType
from app.services.consensus.event_publisher import (
    EventPublisher,
    InMemoryEventPublisher,
    NullEventPublisher,
    safe_publish_event,
)


def test_debate_event_schema_validation_and_version_compatibility():
    """Verify valid DebateEvent construction, SemVer compatibility, and UTC timezone normalization."""
    ev = DebateEvent(
        session_id="sess-1",
        patient_id="pat-1",
        sequence_number=1,
        event_type=EventType.DEBATE_STARTED,
        schema_version="1.2.0",
        timestamp="2026-11-26T10:00:00+05:00",
        status=EventStatus.INFO,
        payload={"mode": "full_debate"},
    )
    assert ev.schema_version == "1.2.0"
    assert ev.timestamp.tzinfo == timezone.utc
    assert ev.timestamp.hour == 5
    sse = ev.to_sse_frame()
    assert sse.startswith("id: 1\nevent: debate_started\ndata: ")
    assert sse.endswith("\n\n")


def test_debate_event_rejects_invalid_types_versions_and_forbidden_payloads():
    """Verify unsupported event types, incompatible major versions, bad sequences, and forbidden keys fail."""
    # Invalid event type
    with pytest.raises(ValidationError):
        DebateEvent(session_id="s1", sequence_number=1, event_type="not_a_real_event")

    # Incompatible major version
    with pytest.raises(ValidationError):
        DebateEvent(session_id="s1", sequence_number=1, event_type=EventType.DEBATE_STARTED, schema_version="2.0.0")

    # Invalid SemVer format
    with pytest.raises(ValidationError):
        DebateEvent(session_id="s1", sequence_number=1, event_type=EventType.DEBATE_STARTED, schema_version="v1")

    # Sequence < 1
    with pytest.raises(ValidationError):
        DebateEvent(session_id="s1", sequence_number=0, event_type=EventType.DEBATE_STARTED)

    # Empty session_id
    with pytest.raises(ValidationError):
        DebateEvent(session_id="   ", sequence_number=1, event_type=EventType.DEBATE_STARTED)

    # Forbidden chain-of-thought key in payload
    with pytest.raises(ValidationError):
        DebateEvent(
            session_id="s1",
            sequence_number=1,
            event_type=EventType.AGENT_CLAIM_SUBMITTED,
            payload={"chain_of_thought": "secret"},
        )


def test_in_memory_publisher_ordering_and_session_isolation():
    """Verify monotonic sequence numbers per session and strict isolation across sessions."""
    pub = InMemoryEventPublisher()
    assert isinstance(pub, EventPublisher)

    e1 = pub.publish(EventType.DEBATE_STARTED, "sess-A", {"step": 1})
    e2 = pub.publish(EventType.AGENT_ACTIVATED, "sess-B", {"step": 1})
    e3 = pub.publish(EventType.AGENT_ACTIVATED, "sess-A", {"step": 2})

    assert e1.sequence_number == 1
    assert e3.sequence_number == 2
    assert e2.sequence_number == 1

    events_a = pub.get_events("sess-A")
    events_b = pub.get_events("sess-B")
    assert [e.sequence_number for e in events_a] == [1, 2]
    assert [e.sequence_number for e in events_b] == [1]
    assert all(e.session_id == "sess-A" for e in events_a)


def test_null_publisher_and_failure_isolation():
    """Verify NullEventPublisher and safe_publish_event resilience against publisher crashes."""
    null_pub = NullEventPublisher()
    assert isinstance(null_pub, EventPublisher)
    ev = null_pub.publish(EventType.DEBATE_STARTED, "sess-null", {})
    assert ev.sequence_number == 1

    class BrokenPublisher:
        def publish(self, *args, **kwargs):
            raise RuntimeError("Simulated transport failure")

        async def apublish(self, *args, **kwargs):
            raise RuntimeError("Simulated async transport failure")

    res = safe_publish_event("sess-broken", EventType.DEBATE_STARTED, {}, publisher=BrokenPublisher())
    assert res is None  # Must not raise or crash workflow


def test_langgraph_workflow_emits_real_events_without_altering_consensus():
    """Verify actual LangGraph execution emits real ordered events and preserves identical Step 12 outcome."""
    pub = InMemoryEventPublisher()
    base_kwargs = dict(
        patient_demographics={"age": 60, "sex": "male"},
        symptoms_data={"symptoms": ["chest_pain"], "severity": 8, "duration_hours": 2.0},
        laboratory_data={
            "cardiac_troponin_ng_ml": 0.008,
            "cardiac_troponin_assay": "hs_ctni_abbott",
            "resting_ecg": "normal",
            "serial_troponin_completed": False,
        },
        provider="mock",
        use_cache=False,
    )

    state_no_pub = run_clinical_graph(create_initial_graph_state(session_id="sess-nopub", **base_kwargs))
    state_with_pub = run_clinical_graph(
        create_initial_graph_state(session_id="sess-withpub", **base_kwargs),
        event_publisher=pub,
    )

    # Clinical consensus must be completely invariant to event publishing
    assert state_no_pub["consensus_resolution"]["overall_outcome"] == state_with_pub["consensus_resolution"]["overall_outcome"]
    assert state_no_pub["consensus_resolution"]["global_epistemic_doubt_score"] == state_with_pub["consensus_resolution"]["global_epistemic_doubt_score"]

    events = pub.get_events("sess-withpub")
    assert len(events) >= 12
    assert [e.sequence_number for e in events] == list(range(1, len(events) + 1))

    types = [e.event_type for e in events]
    assert types[0] == EventType.DEBATE_STARTED
    assert EventType.AGENT_ACTIVATED in types
    assert EventType.AGENT_ANALYSIS_COMPLETED in types
    assert EventType.CONTRADICTION_DETECTED in types
    assert EventType.CHALLENGE_SUBMITTED in types
    assert EventType.REBUTTAL_SUBMITTED in types
    assert EventType.CONFIDENCE_RECALIBRATION_COMPLETED in types
    assert EventType.EPISTEMIC_DOUBT_CALCULATED in types
    assert EventType.FINAL_VERDICT_GENERATED in types
    assert types[-1] == EventType.DEBATE_COMPLETED


def test_langgraph_concordant_session_emits_no_fabricated_contradictions():
    """Verify concordant patient data does NOT emit fabricated contradiction or debate challenge events."""
    pub = InMemoryEventPublisher()
    state = create_initial_graph_state(
        session_id="sess-concordant",
        patient_demographics={"age": 40, "sex": "female"},
        symptoms_data={"symptoms": [], "severity": 1},
        laboratory_data={"systolic_bp": 118.0, "diastolic_bp": 74.0, "hba1c_percent": 5.1},
        clinical_scores={"framingham_risk_percent": 2.0},
        ml_predictions={"cardiovascular_risk_percent": 3.0},
        provider="mock",
        use_cache=False,
    )
    run_clinical_graph(state, event_publisher=pub)
    types = [e.event_type for e in pub.get_events("sess-concordant")]
    assert EventType.CONTRADICTION_DETECTED not in types
    assert EventType.CHALLENGE_SUBMITTED not in types
    assert EventType.DEBATE_COMPLETED in types
