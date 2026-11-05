"""Integration tests for Consensus & Multi-Agent Debate APIs (/api/v1/consensus).

Validates:
1. POST /api/v1/consensus/contradictions/test (Sub-Step 12.1)
   - 401 Unauthorized rejection for missing credentials
   - 200 OK with detected multi-agent contradictions and targeted challenges
   - 200 OK with fully concordant clinical inputs (0 contradictions, 0.0 doubt)
   - Proper response schema serialization and latency tracking
"""

import pytest
from fastapi.testclient import TestClient

from app.core.security import create_access_token
from app.database.models import User
from app.database.repositories import UserRepository


def _create_authenticated_doctor(db_session, email: str = "doctor_consensus@example.com") -> tuple[User, dict]:
    """Helper to seed a test clinician and generate Bearer authorization headers."""
    user_repo = UserRepository(db_session)
    user = user_repo.create(
        email=email,
        hashed_password="hashed_test_password",
        full_name="Dr. Consensus Specialist",
    )
    token = create_access_token(subject=user.id)
    headers = {"Authorization": f"Bearer {token}"}
    return user, headers


def test_unauthenticated_contradiction_test_rejected(client: TestClient) -> None:
    """POST /api/v1/consensus/contradictions/test must reject unauthenticated requests with 401."""
    res = client.post(
        "/api/v1/consensus/contradictions/test",
        json={"symptoms_data": {"symptoms": ["chest_pain"], "severity": 8}},
    )
    assert res.status_code == 401


def test_authenticated_contradiction_test_default_payload(client: TestClient, db_session) -> None:
    """POST /api/v1/consensus/contradictions/test with default payload detects multi-agent contradictions."""
    _, headers = _create_authenticated_doctor(db_session, email="dr_eval_1@example.com")

    # Use default request payload by sending empty JSON object
    res = client.post(
        "/api/v1/consensus/contradictions/test",
        json={},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()

    assert data["status"] == "success"
    assert data["execution_time_ms"] >= 0.0

    result = data["result"]
    assert result["contradictions_detected"] is True
    assert result["total_contradictions"] >= 3
    assert result["critical_count"] >= 1
    assert result["preliminary_epistemic_doubt"] > 0.0
    assert len(result["issues"]) >= 3

    # Check issue IDs present in default scenario:
    # 1. Acute chest pain + palpitations vs normal troponin & ECG -> SUBJ-OBJ-001
    # 2. Atorvastatin vs LDL 195 -> MED-BIO-001
    # 3. Lisinopril vs BP 154/96 -> MED-BIO-002
    # 4. Framingham 14.5% vs ML CVD 45.2% (gap 30.7%) -> EQ-ML-001
    issue_ids = [issue["issue_id"] for issue in result["issues"]]
    assert any("SUBJ-OBJ-001" in i for i in issue_ids)
    assert any("MED-BIO-001" in i for i in issue_ids)
    assert any("EQ-ML-001" in i for i in issue_ids)

    # Verify structured fields of cardiac issue
    cardiac_issue = next(i for i in result["issues"] if "SUBJ-OBJ-001" in i["issue_id"])
    assert cardiac_issue["category"] == "subjective_vs_objective"
    assert cardiac_issue["severity"] == "moderate"
    assert "Symptom Analysis Specialist" in cardiac_issue["conflicting_agents"]
    assert "Laboratory Biomarker Specialist" in cardiac_issue["conflicting_agents"]
    assert len(cardiac_issue["suggested_challenge"]) > 10
    assert "troponin" in cardiac_issue["physiological_rationale"].lower()


def test_authenticated_contradiction_test_concordant_scenario(client: TestClient, db_session) -> None:
    """POST /api/v1/consensus/contradictions/test returns concordant result when no contradictions exist."""
    _, headers = _create_authenticated_doctor(db_session, email="dr_eval_2@example.com")

    payload = {
        "symptoms_data": {
            "symptoms": ["mild_fatigue"],
            "severity": 3,
            "duration_days": 1,
            "notes": "Mild non-specific fatigue after work.",
        },
        "medical_history_data": {
            "chronic_conditions": [],
            "current_medications": [],
        },
        "laboratory_data": {
            "systolic_bp": 118.0,
            "diastolic_bp": 76.0,
            "total_cholesterol_mg_dl": 180.0,
            "ldl_cholesterol_mg_dl": 95.0,
            "hdl_cholesterol_mg_dl": 55.0,
            "fasting_blood_glucose_mg_dl": 88.0,
            "hba1c_percent": 5.1,
            "cardiac_troponin_ng_ml": 0.005,
            "resting_ecg": "normal_sinus_rhythm",
        },
        "clinical_scores": {
            "framingham_risk_percent": 3.8,
            "framingham_risk_category": "low",
            "findrisc_score": 3,
            "findrisc_risk_category": "low",
        },
        "ml_predictions": {
            "cardiovascular_risk_percent": 5.2,
            "cardiovascular_risk_category": "low",
            "diabetes_risk_percent": 4.1,
            "diabetes_risk_category": "low",
        },
    }

    res = client.post(
        "/api/v1/consensus/contradictions/test",
        json=payload,
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()

    result = data["result"]
    assert result["contradictions_detected"] is False
    assert result["total_contradictions"] == 0
    assert result["critical_count"] == 0
    assert result["preliminary_epistemic_doubt"] == 0.0
    assert "Concordant" in result["summary"]


def test_authenticated_contradiction_test_undiagnosed_diabetes(client: TestClient, db_session) -> None:
    """POST /api/v1/consensus/contradictions/test detects undiagnosed diabetes (Rule B4)."""
    _, headers = _create_authenticated_doctor(db_session, email="dr_eval_3@example.com")

    payload = {
        "symptoms_data": {"symptoms": ["fatigue"], "severity": 4},
        "medical_history_data": {
            "chronic_conditions": ["hypertension"],  # denies diabetes
            "current_medications": [],
        },
        "laboratory_data": {
            "fasting_blood_glucose_mg_dl": 158.0,
            "hba1c_percent": 8.2,
        },
    }

    res = client.post(
        "/api/v1/consensus/contradictions/test",
        json=payload,
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()

    result = data["result"]
    assert result["contradictions_detected"] is True
    assert any("MED-BIO-004" in i["issue_id"] for i in result["issues"])
    issue = next(i for i in result["issues"] if "MED-BIO-004" in i["issue_id"])
    assert issue["severity"] == "moderate"
    assert "undiagnosed" in issue["physiological_rationale"].lower()


def test_unauthenticated_debate_test_rejected(client: TestClient) -> None:
    """POST /api/v1/consensus/debate/test must reject unauthenticated requests with 401."""
    res = client.post(
        "/api/v1/consensus/debate/test",
        json={},
    )
    assert res.status_code == 401


def test_authenticated_debate_test_default_payload(client: TestClient, db_session) -> None:
    """POST /api/v1/consensus/debate/test executes full 2-round multi-agent debate."""
    _, headers = _create_authenticated_doctor(db_session, email="dr_eval_debate_1@example.com")

    res = client.post(
        "/api/v1/consensus/debate/test",
        json={},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()

    assert data["status"] == "success"
    assert data["execution_time_ms"] >= 0.0

    transcript = data["debate_transcript"]
    contradiction = data["contradiction_result"]

    assert contradiction["contradictions_detected"] is True
    assert transcript["total_rounds_executed"] == 2
    assert len(transcript["challenges"]) >= 3
    assert len(transcript["rebuttals"]) >= 3
    assert transcript["convergence_status"] in ["converged", "partial_convergence", "unresolved_divergence"]
    assert "concession" in transcript["summary"].lower() or "debate" in transcript["summary"].lower() or "challenge" in transcript["summary"].lower()

    # Verify structured fields in challenges and rebuttals
    first_challenge = transcript["challenges"][0]
    assert first_challenge["challenging_agent"]
    assert first_challenge["challenged_agent"]
    assert len(first_challenge["physiological_rationale"]) > 5

    first_rebuttal = transcript["rebuttals"][0]
    assert first_rebuttal["disposition"] in ["defend", "revise", "concede", "unsupported", "inconclusive"]
    assert first_rebuttal["responding_agent"]


def test_authenticated_debate_test_concordant_scenario(client: TestClient, db_session) -> None:
    """POST /api/v1/consensus/debate/test produces immediate consensus on concordant input."""
    _, headers = _create_authenticated_doctor(db_session, email="dr_eval_debate_2@example.com")

    payload = {
        "symptoms_data": {
            "symptoms": ["mild_fatigue"],
            "severity": 2,
        },
        "medical_history_data": {
            "chronic_conditions": [],
            "current_medications": [],
        },
        "laboratory_data": {
            "systolic_bp": 118.0,
            "diastolic_bp": 76.0,
            "cardiac_troponin_ng_ml": 0.005,
        },
        "clinical_scores": {
            "framingham_risk_percent": 3.8,
            "framingham_risk_category": "low",
            "target_outcome": "10_year_incident_cvd",
            "prediction_horizon": "10_years",
        },
        "ml_predictions": {
            "cardiovascular_risk_percent": 5.2,
            "cardiovascular_risk_category": "low",
            "target_outcome": "10_year_incident_cvd",
            "prediction_horizon": "10_years",
            "calibrated": True,
        },
    }

    res = client.post(
        "/api/v1/consensus/debate/test",
        json=payload,
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()

    transcript = data["debate_transcript"]
    contradiction = data["contradiction_result"]
    assert contradiction["contradictions_detected"] is False
    assert transcript["total_rounds_executed"] == 1
    assert transcript["convergence_status"] == "no_contradictions"
    assert len(transcript["challenges"]) == 0
    assert len(transcript["rebuttals"]) == 0


def test_unauthenticated_recalibration_rejected(client: TestClient) -> None:
    """Test that POST /api/v1/consensus/recalibrate rejects unauthenticated requests with 401."""
    res = client.post("/api/v1/consensus/recalibrate", json={})
    assert res.status_code == 401


def test_authenticated_recalibration_default_payload(client: TestClient, db_session) -> None:
    """Test authenticated recalibration returns auditable claim adjustments and bounded epistemic doubt."""
    _, headers = _create_authenticated_doctor(db_session, email="dr_recal_1@example.com")

    res = client.post("/api/v1/consensus/recalibrate", json={}, headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert data["status"] == "success"
    assert data["execution_time_ms"] >= 0.0
    assert "contradiction_result" in data
    assert "debate_transcript" in data

    recal = data["recalibration_result"]
    assert "global_epistemic_doubt_score" in recal
    assert 0.0 <= recal["global_epistemic_doubt_score"] <= 1.0
    assert len(recal["recalibrated_claims"]) >= 1

    claim = recal["recalibrated_claims"][0]
    assert 0.0 <= claim["final_confidence"] <= 100.0
    assert "recalibration_explanation" in claim
    assert len(recal["domain_uncertainty_contributions"]) >= 1


def test_authenticated_recalibration_missing_evidence_cap(client: TestClient, db_session) -> None:
    """Test authenticated recalibration enforces 40% cap on acute ischemia claims missing troponin."""
    _, headers = _create_authenticated_doctor(db_session, email="dr_recal_2@example.com")

    payload = {
        "agent_outputs": [{
            "agent_role": "Symptom Analysis Specialist",
            "findings": "Patient reports severe crushing substernal chest pain concerning for acute myocardial infarction.",
            "confidence": 88.0,
        }],
        # Omit cardiac troponin
        "laboratory_data": {
            "serum_sodium_mmol_l": 140.0,
        },
    }

    res = client.post("/api/v1/consensus/recalibrate", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()

    recal = data["recalibration_result"]
    claim = recal["recalibrated_claims"][0]
    assert claim["missing_evidence_cap_applied"] is True
    assert claim["missing_evidence_cap_value"] == 40.0
    assert claim["final_confidence"] <= 40.0
    assert any("troponin" in k for k in claim["missing_evidence_details"])


def test_authenticated_recalibration_concordant_scenario(client: TestClient, db_session) -> None:
    """Test completely concordant panel produces minimal/zero epistemic doubt."""
    _, headers = _create_authenticated_doctor(db_session, email="dr_recal_3@example.com")

    payload = {
        "symptoms_data": {"symptoms": ["mild_fatigue"], "severity": 2},
        "laboratory_data": {
            "systolic_bp": 118.0,
            "diastolic_bp": 76.0,
            "fasting_blood_glucose_mg_dl": 88.0,
            "hba1c_percent": 5.1,
            "ldl_cholesterol_mg_dl": 95.0,
            "cardiac_troponin_ng_ml": 0.005,
        },
    }

    res = client.post("/api/v1/consensus/recalibrate", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()

    recal = data["recalibration_result"]
    assert recal["global_epistemic_doubt_score"] <= 0.15


def test_cross_tenant_recalibration_forbidden(client: TestClient, db_session) -> None:
    """POST /api/v1/consensus/recalibrate must reject cross-tenant patient access with 403."""
    _, headers = _create_authenticated_doctor(db_session, email="dr_recal_tenant@example.com")

    payload = {
        "patient_id": "00000000-0000-0000-0000-000000000099",
        "symptoms_data": {"symptoms": ["chest_pain"], "severity": 8},
    }

    res = client.post("/api/v1/consensus/recalibrate", json=payload, headers=headers)
    assert res.status_code == 403
    assert "Cross-tenant access forbidden" in res.json()["detail"]


def test_authenticated_owner_patient_profile_access_allowed(client: TestClient, db_session) -> None:
    """Authenticated user accessing their own database-backed PatientProfile succeeds with 200."""
    from app.database.repositories import PatientProfileRepository
    user_a, headers_a = _create_authenticated_doctor(db_session, email="user_owner_a@example.com")

    # Create PatientProfile in DB belonging to User A
    profile_repo = PatientProfileRepository(db_session)
    profile_a = profile_repo.create_or_update(
        user_id=user_a.id,
        gender="male",
        height_cm=180.0,
        weight_kg=78.0,
    )

    payload = {
        "patient_id": profile_a.id,
        "symptoms_data": {"symptoms": ["chest_pain"], "severity": 6},
    }

    res = client.post("/api/v1/consensus/recalibrate", json=payload, headers=headers_a)
    assert res.status_code == 200
    assert res.json()["status"] == "success"


def test_cross_tenant_patient_profile_access_denied(client: TestClient, db_session) -> None:
    """User A attempting to process data using User B's persistent database PatientProfile is rejected with 403."""
    from app.database.repositories import PatientProfileRepository
    user_a, headers_a = _create_authenticated_doctor(db_session, email="user_attacker_a@example.com")
    user_b, _ = _create_authenticated_doctor(db_session, email="user_victim_b@example.com")

    # Create PatientProfile in DB belonging to User B
    profile_repo = PatientProfileRepository(db_session)
    profile_b = profile_repo.create_or_update(
        user_id=user_b.id,
        gender="female",
        height_cm=165.0,
        weight_kg=60.0,
    )

    # User A tries to pass User B's profile ID
    payload = {
        "patient_id": profile_b.id,
        "symptoms_data": {"symptoms": ["chest_pain"], "severity": 8},
    }

    res = client.post("/api/v1/consensus/recalibrate", json=payload, headers=headers_a)
    assert res.status_code == 403
    assert "Cross-tenant access forbidden" in res.json()["detail"]


def test_cross_tenant_access_denied_on_contradiction_and_debate(client: TestClient, db_session) -> None:
    """Cross-tenant access is consistently blocked on /contradictions/test and /debate/test endpoints."""
    from app.database.repositories import PatientProfileRepository
    user_a, headers_a = _create_authenticated_doctor(db_session, email="dr_sec_a@example.com")
    user_b, _ = _create_authenticated_doctor(db_session, email="dr_sec_b@example.com")

    profile_repo = PatientProfileRepository(db_session)
    profile_b = profile_repo.create_or_update(
        user_id=user_b.id,
        gender="male",
        height_cm=170.0,
        weight_kg=75.0,
    )

    payload = {"patient_id": profile_b.id}

    # 1. Contradictions endpoint
    res1 = client.post("/api/v1/consensus/contradictions/test", json=payload, headers=headers_a)
    assert res1.status_code == 403
    assert "Cross-tenant access forbidden" in res1.json()["detail"]

    # 2. Debate endpoint
    res2 = client.post("/api/v1/consensus/debate/test", json=payload, headers=headers_a)
    assert res2.status_code == 403
    assert "Cross-tenant access forbidden" in res2.json()["detail"]

    # 3. Step 12.4: Resolve endpoint
    res3 = client.post("/api/v1/consensus/resolve", json=payload, headers=headers_a)
    assert res3.status_code == 403
    assert "Cross-tenant access forbidden" in res3.json()["detail"]


# =============================================================================
# Sub-Step 12.4: Consensus Resolution & Audit Debate Transcript Tests
# =============================================================================

def test_unauthenticated_resolve_endpoint_rejected(client: TestClient) -> None:
    """POST /api/v1/consensus/resolve must reject unauthenticated requests with 401."""
    res = client.post("/api/v1/consensus/resolve", json={})
    assert res.status_code == 401


def test_authenticated_resolve_endpoint_default_payload(client: TestClient, db_session) -> None:
    """POST /api/v1/consensus/resolve with default payload executes resolution pipeline."""
    _, headers = _create_authenticated_doctor(db_session, email="dr_resolver_1@example.com")

    res = client.post(
        "/api/v1/consensus/resolve",
        json={},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()

    assert data["status"] == "success"
    assert data["execution_time_ms"] >= 0.0

    resolution = data["resolution"]
    assert "overall_outcome" in resolution
    assert "claim_resolutions" in resolution
    assert "audit_transcript" in resolution
    assert "clinical_safety_warnings" in resolution

    # Claims evaluated
    assert len(resolution["claim_resolutions"]) >= 1
    for claim in resolution["claim_resolutions"]:
        assert "claim_id" in claim
        assert "consensus_state" in claim
        assert "recalibrated_confidence" in claim
        assert "resolution_rationale" in claim

    # Audit transcript structure
    transcript = resolution["audit_transcript"]
    assert transcript["transcript_id"].startswith("TRANSCRIPT-")
    assert transcript["is_immutable"] is True
    assert transcript["debate_rounds_executed"] >= 1


def test_authenticated_verdict_test_backward_compatible_alias(client: TestClient, db_session) -> None:
    """POST /api/v1/consensus/verdict/test functions as a valid alias for /resolve."""
    _, headers = _create_authenticated_doctor(db_session, email="dr_alias_test@example.com")

    res = client.post(
        "/api/v1/consensus/verdict/test",
        json={},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "resolution" in data
    assert data["resolution"]["overall_outcome"] in [
        "CONSENSUS_SUPPORTED",
        "CONSENSUS_PROVISIONAL",
        "PARTIAL_CONSENSUS",
        "UNRESOLVED_CONSENSUS",
        "INSUFFICIENT_EVIDENCE",
    ]


def test_end_to_end_consensus_with_acute_safety_override(client: TestClient, db_session) -> None:
    """POST /api/v1/consensus/resolve extracts emergent safety override for acute chest pain."""
    _, headers = _create_authenticated_doctor(db_session, email="dr_e2e_safety@example.com")

    payload = {
        "symptoms_data": {
            "symptoms": ["acute crushing chest pain", "diaphoresis"],
            "severity": 9,
            "duration_days": 1,
            "notes": "Sudden onset substernal chest pressure radiating to left arm.",
        },
        "laboratory_data": {
            "systolic_bp": 150.0,
            "diastolic_bp": 95.0,
            # troponin_i not provided -> missing essential evidence
        },
    }

    res = client.post("/api/v1/consensus/resolve", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()["resolution"]

    # Critical emergent safety override must be present
    assert len(data["clinical_safety_warnings"]) >= 1
    emergent_overrides = [
        o for o in data["clinical_safety_warnings"]
        if o["level"] == "emergent" and "ACS" in o["condition_name"]
    ]
    assert len(emergent_overrides) >= 1
    assert "troponin" in emergent_overrides[0]["action_recommendation"].lower()


def test_persisted_consensus_result_and_transcript_endpoints(client: TestClient, db_session) -> None:
    """GET /{analysis_id}/result and /{analysis_id}/transcript retrieve stored records with tenant security."""
    from app.agents.consensus.consensus_resolver import ConsensusResolver
    from app.database.models import AnalysisSession
    import uuid

    user_owner, headers_owner = _create_authenticated_doctor(db_session, email="dr_owner_rec@example.com")
    user_other, headers_other = _create_authenticated_doctor(db_session, email="dr_other_rec@example.com")

    # Generate a genuine, schema-compliant ConsensusResolutionResult
    test_session_id = str(uuid.uuid4())
    resolver = ConsensusResolver()
    valid_resolution = resolver.resolve_consensus(
        session_id=test_session_id,
        analysis_id=test_session_id,
    )

    session_record = AnalysisSession(
        id=test_session_id,
        user_id=user_owner.id,
        status="completed",
        consensus_verdict=valid_resolution.model_dump(),
    )
    db_session.add(session_record)
    db_session.commit()

    # 1. Owner can access result
    res_result = client.get(f"/api/v1/consensus/{test_session_id}/result", headers=headers_owner)
    assert res_result.status_code == 200
    data = res_result.json()
    assert data["analysis_id"] == test_session_id
    assert "overall_outcome" in data

    # 2. Owner can access transcript
    res_trans = client.get(f"/api/v1/consensus/{test_session_id}/transcript", headers=headers_owner)
    assert res_trans.status_code == 200
    trans_data = res_trans.json()
    assert trans_data["analysis_id"] == test_session_id
    assert trans_data["is_immutable"] is True

    # 3. Other clinician receives 403 Forbidden
    res_forbidden_result = client.get(f"/api/v1/consensus/{test_session_id}/result", headers=headers_other)
    assert res_forbidden_result.status_code == 403
    assert "Forbidden" in res_forbidden_result.json()["detail"]

    res_forbidden_trans = client.get(f"/api/v1/consensus/{test_session_id}/transcript", headers=headers_other)
    assert res_forbidden_trans.status_code == 403
    assert "Forbidden" in res_forbidden_trans.json()["detail"]

    # 4. Non-existent session returns 404
    non_existent = str(uuid.uuid4())
    res_404 = client.get(f"/api/v1/consensus/{non_existent}/result", headers=headers_owner)
    assert res_404.status_code == 404





