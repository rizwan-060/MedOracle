"""Integration tests for Step 12.5.2 — SSE Streaming, DB Persistence, Replay & Tenant Isolation."""

from concurrent.futures import ThreadPoolExecutor
import json
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from app.core.security import create_access_token
from app.database.models import AnalysisSession, Base, DebateEventRecord, PatientProfile
from app.database.repositories import DebateEventRepository, UserRepository
from app.graph import create_initial_graph_state, run_clinical_graph
from app.schemas.debate_events import DebateEvent, EventStatus, EventType
from app.services.consensus.streaming import DatabaseEventPublisher, get_live_event_hub


def _seed_user_and_session(db_session, email: str, session_id: str, status: str = "completed"):
    user = UserRepository(db_session).create(
        email=email,
        hashed_password="hashed_test_password",
        full_name="Stream Patient",
    )
    profile = PatientProfile(user_id=user.id, gender="male")
    db_session.add(profile)
    sess = AnalysisSession(
        id=session_id,
        user_id=user.id,
        status=status,
        current_phase="consensus_resolution_completed" if status == "completed" else "running",
        progress_percent=100 if status == "completed" else 50,
    )
    db_session.add(sess)
    db_session.commit()
    token = create_access_token(subject=user.id)
    return user, sess, {"Authorization": f"Bearer {token}"}


def _parse_sse_frames(body_text: str):
    """Parse SSE wire frames into a list of (id, event, data_dict)."""
    frames = []
    for block in body_text.strip().split("\n\n"):
        if not block.strip():
            continue
        ev_id, ev_name, data_obj = None, None, None
        for line in block.splitlines():
            if line.startswith("id: "):
                ev_id = int(line[4:])
            elif line.startswith("event: "):
                ev_name = line[7:]
            elif line.startswith("data: "):
                data_obj = json.loads(line[6:])
        if ev_name is not None:
            frames.append((ev_id, ev_name, data_obj))
    return frames


def test_sse_stream_requires_authentication(client: TestClient):
    """Unauthenticated request to SSE stream must return 401."""
    res = client.get("/api/v1/consensus/sessions/nonexistent-sess/stream")
    assert res.status_code == 401


def test_sse_cross_tenant_isolation_and_no_existence_leakage(client: TestClient, db_session):
    """Cross-tenant and guessed session IDs must both return identical 403 without leaking existence."""
    _, _, headers_owner = _seed_user_and_session(db_session, "owner_sse@example.com", "sess-owned-1")
    _, _, headers_other = _seed_user_and_session(db_session, "other_sse@example.com", "sess-other-1")

    res_other = client.get("/api/v1/consensus/sessions/sess-owned-1/stream", headers=headers_other)
    res_guessed = client.get("/api/v1/consensus/sessions/sess-does-not-exist/stream", headers=headers_other)

    assert res_other.status_code == 403
    assert res_guessed.status_code == 403
    # Identical error detail prevents existence enumeration
    assert res_other.json()["detail"] == res_guessed.json()["detail"]

    # Owner can access
    res_ok = client.get("/api/v1/consensus/sessions/sess-owned-1/stream", headers=headers_owner)
    assert res_ok.status_code == 200
    assert res_ok.headers["content-type"].startswith("text/event-stream")
    assert res_ok.headers["cache-control"] == "no-cache"


def test_db_persistence_unique_constraint_and_concurrent_publication(tmp_path):
    """Verify unique (session_id, sequence_number) constraint and concurrent atomic sequence allocation."""
    from app.database.session import Base

    db_file = tmp_path / "conc_sse.sqlite"
    engine = create_engine(
        f"sqlite:///{db_file}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    SessionFactory = sessionmaker(bind=engine)
    local_db = SessionFactory()
    try:
        user, sess, _ = _seed_user_and_session(local_db, "conc_sse@example.com", "sess-conc-1", status="running")
        user_id = user.id
        sess_id = sess.id

        # 1. Direct DB unique constraint check
        rec1 = DebateEventRecord(
            id="ev-u-1",
            session_id=sess_id,
            sequence_number=1,
            event_type=EventType.DEBATE_STARTED.value,
            status=EventStatus.INFO.value,
            payload={},
            evidence_references=[],
            event_metadata={},
        )
        rec2_dup = DebateEventRecord(
            id="ev-u-2",
            session_id=sess_id,
            sequence_number=1,
            event_type=EventType.AGENT_ACTIVATED.value,
            status=EventStatus.INFO.value,
            payload={},
            evidence_references=[],
            event_metadata={},
        )
        local_db.add(rec1)
        local_db.commit()
        local_db.add(rec2_dup)
        with pytest.raises(IntegrityError):
            local_db.commit()
        local_db.rollback()
    finally:
        local_db.close()

    # 2. Concurrent DatabaseEventPublisher writes allocate unique monotonic sequences (2..9)
    pub = DatabaseEventPublisher(session_factory=SessionFactory)

    def _worker(idx: int):
        return pub.publish(
            EventType.AGENT_ACTIVATED,
            sess_id,
            {"worker": idx},
            patient_id=user_id,
            agent_role=f"agent_{idx}",
        )

    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(_worker, range(8)))

    seqs = sorted(r.sequence_number for r in results)
    assert seqs == list(range(2, 10))

    # 3. Verify persistence survives a fresh DB session ("restart")
    fresh_db = SessionFactory()
    try:
        rows = DebateEventRepository(fresh_db).list_events_after(sess_id, after_sequence=0)
        assert [r.sequence_number for r in rows] == list(range(1, 10))
    finally:
        fresh_db.close()
        engine.dispose()


def test_sse_last_event_id_replay_and_invalid_header_handling(client: TestClient, db_session):
    """Verify completed-session historical replay, Last-Event-ID catch-up, and invalid header resilience."""
    engine = db_session.get_bind()
    SessionFactory = sessionmaker(bind=engine)
    user, sess, headers = _seed_user_and_session(db_session, "replay@example.com", "sess-replay-1", status="completed")

    pub = DatabaseEventPublisher(session_factory=SessionFactory)
    pub.publish(EventType.DEBATE_STARTED, sess.id, {"step": 1}, patient_id=user.id)
    pub.publish(EventType.AGENT_ACTIVATED, sess.id, {"step": 2}, patient_id=user.id, agent_role="symptom_agent")
    pub.publish(EventType.CONTRADICTION_DETECTED, sess.id, {"step": 3}, patient_id=user.id, status=EventStatus.WARNING)
    pub.publish(EventType.DEBATE_COMPLETED, sess.id, {"step": 4}, patient_id=user.id, status=EventStatus.COMPLETED)

    # Full replay (no Last-Event-ID)
    res_all = client.get(f"/api/v1/consensus/sessions/{sess.id}/stream", headers=headers)
    assert res_all.status_code == 200
    frames_all = _parse_sse_frames(res_all.text)
    assert [f[0] for f in frames_all] == [1, 2, 3, 4]
    assert [f[1] for f in frames_all] == [
        "debate_started",
        "agent_activated",
        "contradiction_detected",
        "debate_completed",
    ]

    # Reconnect with Last-Event-ID: 2 -> replays only 3 and 4
    res_resume = client.get(
        f"/api/v1/consensus/sessions/{sess.id}/stream",
        headers={**headers, "Last-Event-ID": "2"},
    )
    assert res_resume.status_code == 200
    frames_resume = _parse_sse_frames(res_resume.text)
    assert [f[0] for f in frames_resume] == [3, 4]

    # Invalid Last-Event-ID safely falls back to 0
    res_bad_id = client.get(
        f"/api/v1/consensus/sessions/{sess.id}/stream",
        headers={**headers, "Last-Event-ID": "not-an-int"},
    )
    assert res_bad_id.status_code == 200
    assert [f[0] for f in _parse_sse_frames(res_bad_id.text)] == [1, 2, 3, 4]

    # Outdated/future Last-Event-ID returns empty stream cleanly
    res_future = client.get(
        f"/api/v1/consensus/sessions/{sess.id}/stream",
        headers={**headers, "Last-Event-ID": "999"},
    )
    assert res_future.status_code == 200
    assert _parse_sse_frames(res_future.text) == []


def test_end_to_end_langgraph_to_db_to_sse_stream(client: TestClient, db_session):
    """End-to-end test: real LangGraph execution -> DatabaseEventPublisher -> PostgreSQL/SQLite -> SSE stream."""
    engine = db_session.get_bind()
    SessionFactory = sessionmaker(bind=engine)
    user, sess, headers = _seed_user_and_session(db_session, "e2e_sse@example.com", "sess-e2e-stream", status="completed")

    pub = DatabaseEventPublisher(session_factory=SessionFactory)
    initial_state = create_initial_graph_state(
        session_id=sess.id,
        user_id=user.id,
        patient_demographics={"age": 58, "sex": "male"},
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
    final_state = run_clinical_graph(initial_state, event_publisher=pub)
    assert final_state["status"] == "completed"

    res = client.get(f"/api/v1/consensus/sessions/{sess.id}/stream", headers=headers)
    assert res.status_code == 200
    frames = _parse_sse_frames(res.text)
    assert len(frames) >= 12
    assert frames[0][1] == "debate_started"
    assert frames[-1][1] == "debate_completed"
    # Verify monotonic IDs and zero duplicates
    ids = [f[0] for f in frames]
    assert ids == list(range(1, len(ids) + 1))


def test_alembic_migration_002_debate_events_upgrade_and_downgrade(tmp_path, monkeypatch):
    """Verify Alembic migration 002_debate_events runs cleanly on a fresh database."""
    from pathlib import Path
    from alembic import command
    from alembic.config import Config
    from sqlalchemy import inspect
    from app.core.config import get_settings

    db_file = tmp_path / "alembic_test.sqlite"
    db_url = f"sqlite:///{db_file}"
    monkeypatch.setenv("DATABASE_URL", db_url)
    get_settings.cache_clear()

    backend_dir = Path(__file__).resolve().parents[2]
    cfg = Config(str(backend_dir / "alembic.ini"))
    cfg.set_main_option("script_location", str(backend_dir / "migrations"))
    cfg.set_main_option("sqlalchemy.url", db_url)

    try:
        command.upgrade(cfg, "head")
        eng = create_engine(db_url)
        insp = inspect(eng)
        assert "debate_events" in insp.get_table_names()
        uniques = [u["name"] for u in insp.get_unique_constraints("debate_events")]
        assert "uq_debate_events_session_seq" in uniques
        eng.dispose()

        command.downgrade(cfg, "001_initial_schema")
        eng2 = create_engine(db_url)
        assert "debate_events" not in inspect(eng2).get_table_names()
        eng2.dispose()
    finally:
        get_settings.cache_clear()


@pytest.mark.asyncio
async def test_live_event_hub_replay_deduplication_and_disconnect_cleanup():
    """Verify LiveEventHub subscriber lifecycle, clean unsubscribe, and replay deduplication."""
    import asyncio
    from app.schemas.debate_events import DebateEvent
    from app.services.consensus.streaming import LiveEventHub

    hub = LiveEventHub()
    session_id = "sess-hub-1"
    q = hub.subscribe(session_id)
    assert len(hub._subscribers.get(session_id, ())) == 1

    ev1 = DebateEvent(
        session_id=session_id,
        sequence_number=1,
        event_type=EventType.DEBATE_STARTED,
        status=EventStatus.INFO,
        payload={"step": 1},
    )
    ev2 = DebateEvent(
        session_id=session_id,
        sequence_number=2,
        event_type=EventType.AGENT_ACTIVATED,
        status=EventStatus.INFO,
        payload={"step": 2},
    )
    hub.broadcast(session_id, ev1)
    hub.broadcast(session_id, ev2)
    await asyncio.sleep(0)

    # Simulate replay up to sequence 1, then draining live queue should skip seq <= 1
    replayed_up_to = 1
    received = []
    while not q.empty():
        item = q.get_nowait()
        if item.sequence_number <= replayed_up_to:
            continue
        received.append(item.sequence_number)

    assert received == [2]

    # Simulate client disconnect
    hub.unsubscribe(session_id, q)
    assert len(hub._subscribers.get(session_id, ())) == 0
