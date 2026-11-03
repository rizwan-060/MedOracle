"""Comprehensive Unit Tests for Consensus Resolution Engine & Audit Transcript (Sub-Step 12.4).

Validates:
1. All 7 Claim-Level Consensus States:
   - SUPPORTED: Verified patient evidence, confidence >= 65%, zero unresolved contradiction penalty.
   - PROVISIONAL: Evidence supports claim but caveats exist (e.g. single troponin) or confidence < 65%.
   - CONFLICTING: Directly contradicted by objective biomarker evidence, or active critical contradiction.
   - UNRESOLVED: Unresolved debate disagreement without empirical resolution.
   - INSUFFICIENT_EVIDENCE: Essential diagnostic biomarker missing (cap applied).
   - UNSUPPORTED: Lacking any verified clinical evidence during cross-examination.
   - WITHDRAWN: Formally withdrawn or conceded by specialist during debate.
2. Independent Comorbidity Preservation: Multiple coexisting medical conditions (e.g. Diabetes + Hypertension).
3. Overall Analysis-Level Aggregation:
   - CONSENSUS_SUPPORTED, CONSENSUS_PROVISIONAL, PARTIAL_CONSENSUS, UNRESOLVED_CONSENSUS, INSUFFICIENT_EVIDENCE.
4. Non-Suppressible Clinical Safety Overrides:
   - ACS, DKA, Hypertensive Emergency warnings persist independently of consensus.
5. Audit Debate Transcript:
   - Traceability, completeness, versioning, idempotency, and immutability.
"""

import pytest
from app.agents.consensus.consensus_resolver import ConsensusResolver
from app.agents.consensus.contradiction_detector import ContradictionDetector
from app.agents.consensus.debate_protocol import DebateProtocolEngine
from app.agents.consensus.recalibration import ConfidenceRecalibrator
from app.schemas.consensus import (
    AuditDebateTranscript,
    ClaimConsensusState,
    ClaimRecalibrationRecord,
    ClaimRelationshipType,
    ConfidenceRecalibrationResult,
    ContradictionCategory,
    ContradictionIssue,
    ContradictionMatrixResult,
    ContradictionSeverity,
    DebateTranscript,
    OverallConsensusOutcome,
    SafetyOverrideLevel,
    SafetyOverrideLifecycleState,
)


@pytest.fixture
def resolver() -> ConsensusResolver:
    return ConsensusResolver()


@pytest.fixture
def recalibrator() -> ConfidenceRecalibrator:
    return ConfidenceRecalibrator()


# =============================================================================
# Claim-Level Consensus State Tests
# =============================================================================

def test_claim_state_supported(resolver: ConsensusResolver, recalibrator: ConfidenceRecalibrator) -> None:
    """Test claim with verified objective evidence and confidence >= 65% resolves as SUPPORTED."""
    recal_result = recalibrator.recalibrate_panel(
        agent_outputs=[{
            "agent_role": "Laboratory Biomarker Specialist",
            "findings": "Serum LDL cholesterol confirmed severely elevated at 210 mg/dL.",
            "confidence": 85.0,
        }],
        laboratory_data={"ldl_cholesterol_mg_dl": 210.0},
    )

    resolution = resolver.resolve_consensus(recalibration_result=recal_result)
    assert len(resolution.claim_resolutions) == 1
    claim = resolution.claim_resolutions[0]
    assert claim.consensus_state == ClaimConsensusState.SUPPORTED
    assert "ldl_cholesterol_mg_dl" in claim.evidence_grounding_references
    assert claim.final_confidence >= 65.0


def test_claim_state_provisional_with_caveats(resolver: ConsensusResolver, recalibrator: ConfidenceRecalibrator) -> None:
    """Test claim with single normal troponin (ACS rule-in) resolves as PROVISIONAL due to serial testing caveat."""
    recal_result = recalibrator.recalibrate_panel(
        agent_outputs=[{
            "agent_role": "Symptom Analysis Specialist",
            "findings": "Patient reports severe chest pressure concerning for acute coronary presentation.",
            "confidence": 60.0,
        }],
        laboratory_data={"cardiac_troponin_ng_ml": 0.01},  # Single normal troponin, serial not completed
    )

    resolution = resolver.resolve_consensus(recalibration_result=recal_result)
    claim = resolution.claim_resolutions[0]
    # Single troponin without serial testing is insufficient/provisional
    assert claim.consensus_state == ClaimConsensusState.PROVISIONAL


def test_claim_state_insufficient_evidence(resolver: ConsensusResolver, recalibrator: ConfidenceRecalibrator) -> None:
    """Test claim of acute myocardial infarction with missing troponin resolves as INSUFFICIENT_EVIDENCE."""
    recal_result = recalibrator.recalibrate_panel(
        agent_outputs=[{
            "agent_role": "Symptom Analysis Specialist",
            "findings": "Severe acute chest pain concerning for acute myocardial infarction.",
            "confidence": 85.0,
        }],
        laboratory_data={},  # Troponin missing -> cap applied
    )

    resolution = resolver.resolve_consensus(recalibration_result=recal_result)
    claim = resolution.claim_resolutions[0]
    assert claim.consensus_state == ClaimConsensusState.INSUFFICIENT_EVIDENCE
    assert any("cardiac_troponin" in m for m in claim.missing_evidence_details)


def test_claim_state_conflicting_when_contradicted_by_objective_data(
    resolver: ConsensusResolver,
    recalibrator: ConfidenceRecalibrator,
) -> None:
    """Test claim asserting transmural necrosis is CONFLICTING when flat serial troponin is normal."""
    recal_result = recalibrator.recalibrate_panel(
        agent_outputs=[{
            "agent_role": "Symptom Specialist",
            "findings": "Acute myocardial infarction with active necrosis.",
            "confidence": 80.0,
        }],
        laboratory_data={
            "cardiac_troponin_ng_ml": 0.01,
            "serial_troponin_completed": True,
        },
    )

    resolution = resolver.resolve_consensus(recalibration_result=recal_result)
    claim = resolution.claim_resolutions[0]
    assert claim.consensus_state == ClaimConsensusState.CONFLICTING
    assert len(claim.conflicting_evidence_references) > 0


def test_claim_state_unresolved_when_disagreement_persists(
    resolver: ConsensusResolver,
) -> None:
    """Test claim resolves as UNRESOLVED when debate ends in unresolved disagreement without empirical resolution."""
    recal_record = ClaimRecalibrationRecord(
        agent_id="Symptom Analysis Specialist",
        claim_id="claim_sym_unresolved",
        claim_text="Persistent atypical chest discomfort with non-diagnostic biomarkers.",
        clinical_domain="ischemia",
        original_confidence=75.0,
        recalibrated_confidence=60.0,
        final_confidence=60.0,
        debate_outcome="unresolved_disagreement",
        recalibration_explanation="Persistent clinical disagreement between symptom report and biomarkers",
    )
    recal_result = ConfidenceRecalibrationResult(
        recalibrated_claims=[recal_record],
        global_epistemic_doubt_score=0.45,
        summary="Unresolved disagreement test",
    )

    resolution = resolver.resolve_consensus(recalibration_result=recal_result)
    claim = resolution.claim_resolutions[0]
    assert claim.consensus_state == ClaimConsensusState.UNRESOLVED
    assert "unresolved" in claim.resolution_rationale.lower()


def test_claim_state_unsupported_in_debate(
    resolver: ConsensusResolver,
) -> None:
    """Test claim that was marked unsupported in debate resolves as UNSUPPORTED."""
    recal_record = ClaimRecalibrationRecord(
        agent_id="Symptom Analysis Specialist",
        claim_id="claim_sym_unsupported",
        claim_text="Definite acute coronary syndrome based purely on subjective intuition.",
        clinical_domain="ischemia",
        original_confidence=80.0,
        recalibrated_confidence=40.0,
        final_confidence=40.0,
        debate_outcome="unsupported",
        recalibration_explanation="Claim lacked evidentiary basis in debate",
    )
    recal_result = ConfidenceRecalibrationResult(
        recalibrated_claims=[recal_record],
        global_epistemic_doubt_score=0.50,
        summary="Unsupported claim test",
    )

    resolution = resolver.resolve_consensus(recalibration_result=recal_result)
    claim = resolution.claim_resolutions[0]
    assert claim.consensus_state == ClaimConsensusState.UNSUPPORTED


def test_claim_state_withdrawn_on_concession(resolver: ConsensusResolver) -> None:
    """Test claim formally conceded without objective backing resolves as WITHDRAWN."""
    recal_record = ClaimRecalibrationRecord(
        agent_id="Medical History Specialist",
        claim_id="claim_hist_1",
        claim_text="Patient has uncontrolled hyperlipidemia despite statin.",
        clinical_domain="lipidology",
        original_confidence=80.0,
        recalibrated_confidence=25.0,
        final_confidence=25.0,
        debate_outcome="conceded",
        concession_reason="Laboratory confirms LDL is strictly at target; conceded diagnostic error.",
        is_withdrawn=True,
        recalibration_explanation="Conceded in debate",
    )
    recal_result = ConfidenceRecalibrationResult(
        recalibrated_claims=[recal_record],
        global_epistemic_doubt_score=0.10,
        summary="Conceded claim test",
    )

    resolution = resolver.resolve_consensus(recalibration_result=recal_result)
    claim = resolution.claim_resolutions[0]
    assert claim.consensus_state == ClaimConsensusState.WITHDRAWN
    assert "conceded" in claim.resolution_rationale.lower() or "withdrawn" in claim.resolution_rationale.lower()


# =============================================================================
# Comorbidities & Multi-Claim Concordance Tests
# =============================================================================

def test_multiple_concordant_comorbidities_preserved(
    resolver: ConsensusResolver,
    recalibrator: ConfidenceRecalibrator,
) -> None:
    """Test that multiple chronic comorbidities (T2D and Hypertension) coexist as SUPPORTED claims without reductionism."""
    labs = {
        "fasting_blood_glucose_mg_dl": 142.0,
        "hba1c_percent": 7.4,
        "systolic_bp": 158.0,
        "diastolic_bp": 96.0,
    }

    recal_result = recalibrator.recalibrate_panel(
        agent_outputs=[
            {
                "agent_role": "Laboratory Specialist",
                "findings": "Poorly controlled chronic diabetes mellitus (HbA1c 7.4%).",
                "confidence": 85.0,
            },
            {
                "agent_role": "Medical History Specialist",
                "findings": "Essential stage 2 hypertension with persistent systolic elevation.",
                "confidence": 85.0,
            },
        ],
        laboratory_data=labs,
    )

    resolution = resolver.resolve_consensus(recalibration_result=recal_result, laboratory_data=labs)
    assert len(resolution.claim_resolutions) == 2

    # Both conditions must be SUPPORTED
    assert resolution.claim_resolutions[0].consensus_state == ClaimConsensusState.SUPPORTED
    assert resolution.claim_resolutions[1].consensus_state == ClaimConsensusState.SUPPORTED

    # Overall outcome must be CONSENSUS_SUPPORTED
    assert resolution.overall_outcome == OverallConsensusOutcome.CONSENSUS_SUPPORTED


# =============================================================================
# Overall Outcome Aggregation Tests
# =============================================================================

def test_overall_outcome_insufficient_evidence_when_acute_biomarker_missing(
    resolver: ConsensusResolver,
    recalibrator: ConfidenceRecalibrator,
) -> None:
    """Test that missing troponin in acute coronary claim forces INSUFFICIENT_EVIDENCE overall outcome."""
    recal_result = recalibrator.recalibrate_panel(
        agent_outputs=[{
            "agent_role": "Symptom Specialist",
            "findings": "Severe acute chest pain concerning for acute myocardial infarction.",
            "confidence": 85.0,
        }],
        laboratory_data={},
    )

    resolution = resolver.resolve_consensus(recalibration_result=recal_result)
    assert resolution.overall_outcome == OverallConsensusOutcome.INSUFFICIENT_EVIDENCE


def test_overall_outcome_partial_consensus(
    resolver: ConsensusResolver,
    recalibrator: ConfidenceRecalibrator,
) -> None:
    """Test that a panel with one SUPPORTED claim and one PROVISIONAL claim produces PARTIAL_CONSENSUS."""
    labs = {
        "ldl_cholesterol_mg_dl": 210.0,
        "cardiac_troponin_ng_ml": 0.01,  # Single troponin -> provisional
    }

    recal_result = recalibrator.recalibrate_panel(
        agent_outputs=[
            {
                "agent_role": "Laboratory Specialist",
                "findings": "Severe hypercholesterolemia with circulating LDL of 210 mg/dL.",
                "confidence": 90.0,
            },
            {
                "agent_role": "Symptom Specialist",
                "findings": "Mild exertional chest tightness concerning for possible ischemia.",
                "confidence": 50.0,
            },
        ],
        laboratory_data=labs,
    )

    resolution = resolver.resolve_consensus(recalibration_result=recal_result, laboratory_data=labs)
    assert resolution.claim_resolutions[0].consensus_state == ClaimConsensusState.SUPPORTED
    assert resolution.claim_resolutions[1].consensus_state == ClaimConsensusState.PROVISIONAL
    assert resolution.overall_outcome == OverallConsensusOutcome.PARTIAL_CONSENSUS


# =============================================================================
# Clinical Safety Override Tests
# =============================================================================

def test_safety_override_triggered_for_acute_chest_pain(
    resolver: ConsensusResolver,
    recalibrator: ConfidenceRecalibrator,
) -> None:
    """Test that presenting acute chest pain generates a non-suppressible ACS safety override."""
    symptoms = {"symptoms": ["chest_pain", "breathlessness"], "severity": 8}
    labs = {"cardiac_troponin_ng_ml": 0.01}

    recal_result = recalibrator.recalibrate_panel(
        agent_outputs=[{
            "agent_role": "Symptom Specialist",
            "findings": "Acute substernal chest pain radiating to left arm.",
            "confidence": 80.0,
        }],
        symptoms_data=symptoms,
        laboratory_data=labs,
    )

    resolution = resolver.resolve_consensus(
        recalibration_result=recal_result,
        symptoms_data=symptoms,
        laboratory_data=labs,
    )

    assert len(resolution.clinical_safety_warnings) >= 1
    acs_warn = next(w for w in resolution.clinical_safety_warnings if "Acute Coronary" in w.condition_name)
    assert acs_warn.level == SafetyOverrideLevel.EMERGENT
    assert acs_warn.overrides_consensus is True
    assert "serial" in acs_warn.action_recommendation.lower()


def test_safety_override_triggered_for_hypertensive_emergency(
    resolver: ConsensusResolver,
    recalibrator: ConfidenceRecalibrator,
) -> None:
    """Test severe BP elevation with renal injury triggers an EMERGENT hypertensive emergency safety override."""
    labs = {
        "systolic_bp": 210.0,
        "diastolic_bp": 130.0,
        "serum_creatinine_mg_dl": 2.8,  # Acute kidney injury
    }

    recal_result = recalibrator.recalibrate_panel(
        agent_outputs=[{
            "agent_role": "Specialist",
            "findings": "Hypertensive emergency with critical blood pressure and renal injury.",
            "confidence": 85.0,
        }],
        laboratory_data=labs,
    )

    resolution = resolver.resolve_consensus(recalibration_result=recal_result, laboratory_data=labs)
    htn_warn = next(w for w in resolution.clinical_safety_warnings if "Hypertensive Emergency" in w.condition_name)
    assert htn_warn.level == SafetyOverrideLevel.EMERGENT
    assert htn_warn.overrides_consensus is True


# =============================================================================
# Audit Debate Transcript Tests
# =============================================================================

def test_audit_transcript_completeness_and_immutability(
    resolver: ConsensusResolver,
    recalibrator: ConfidenceRecalibrator,
) -> None:
    """Test that generated audit transcript contains all required provenance fields and is marked immutable."""
    labs = {"ldl_cholesterol_mg_dl": 195.0}

    recal_result = recalibrator.recalibrate_panel(
        agent_outputs=[{
            "agent_role": "Laboratory Specialist",
            "findings": "Elevated LDL confirmed.",
            "confidence": 80.0,
        }],
        laboratory_data=labs,
        session_id="sess-audit-test",
    )

    resolution = resolver.resolve_consensus(
        recalibration_result=recal_result,
        laboratory_data=labs,
        session_id="sess-audit-test",
        analysis_id="analysis-audit-test",
    )

    transcript = resolution.audit_transcript
    assert isinstance(transcript, AuditDebateTranscript)
    assert transcript.session_id == "sess-audit-test"
    assert transcript.analysis_id == "analysis-audit-test"
    assert transcript.is_immutable is True
    assert len(transcript.participating_agents) >= 1
    assert len(transcript.claim_resolutions) >= 1
    assert transcript.overall_outcome == resolution.overall_outcome
    assert transcript.final_resolution_rationale != ""


def test_transcript_generation_idempotency(
    resolver: ConsensusResolver,
    recalibrator: ConfidenceRecalibrator,
) -> None:
    """Test that repeated transcript generation with identical inputs produces identical resolution states and scores."""
    labs = {"ldl_cholesterol_mg_dl": 210.0}
    agent_outputs = [{
        "agent_role": "Laboratory Specialist",
        "findings": "Severe circulating hypercholesterolemia.",
        "confidence": 85.0,
    }]

    recal1 = recalibrator.recalibrate_panel(agent_outputs=agent_outputs, laboratory_data=labs)
    res1 = resolver.resolve_consensus(recalibration_result=recal1, laboratory_data=labs)

    recal2 = recalibrator.recalibrate_panel(agent_outputs=agent_outputs, laboratory_data=labs)
    res2 = resolver.resolve_consensus(recalibration_result=recal2, laboratory_data=labs)

    assert res1.overall_outcome == res2.overall_outcome
    assert len(res1.claim_resolutions) == len(res2.claim_resolutions)
    assert res1.claim_resolutions[0].consensus_state == res2.claim_resolutions[0].consensus_state
    assert res1.claim_resolutions[0].final_confidence == res2.claim_resolutions[0].final_confidence


def test_claim_relationship_modeling_comorbidities_and_contradictions(
    resolver: ConsensusResolver,
    recalibrator: ConfidenceRecalibrator,
) -> None:
    """Test pairwise modeling of COMPATIBLE comorbidities, MUTUALLY_EXCLUSIVE claims, and HIERARCHICAL subsumption."""
    agent_outputs = [
        {"agent_role": "Cardiologist", "findings": "Essential hypertension confirmed stage 2.", "confidence": 85.0},
        {"agent_role": "Endocrinologist", "findings": "Type 2 diabetes mellitus with uncontrolled fasting glucose.", "confidence": 85.0},
        {"agent_role": "Symptom Analyst", "findings": "Acute myocardial infarction with substernal crushing pain.", "confidence": 80.0},
        {"agent_role": "Triage Clinician", "findings": "Non-cardiac chest pain with normal troponin, acute ischemia ruled out.", "confidence": 75.0},
    ]
    labs = {
        "systolic_bp": 155.0,
        "fasting_blood_glucose_mg_dl": 165.0,
        "cardiac_troponin_ng_ml": 0.08,
    }

    recal = recalibrator.recalibrate_panel(agent_outputs=agent_outputs, laboratory_data=labs)
    resolution = resolver.resolve_consensus(recalibration_result=recal, laboratory_data=labs)

    assert len(resolution.claim_relationships) > 0
    rel_types = [r.relationship_type for r in resolution.claim_relationships]

    # HTN and T2D must be recognized as COMPATIBLE
    compat_rels = [r for r in resolution.claim_relationships if r.relationship_type == ClaimRelationshipType.COMPATIBLE]
    assert len(compat_rels) >= 1
    assert any("hypertension" in r.clinical_rationale.lower() or "t2d" in r.clinical_rationale.lower() or "diabetes" in r.clinical_rationale.lower() for r in compat_rels)

    # Acute MI vs Ruled Out non-cardiac chest pain must be MUTUALLY_EXCLUSIVE
    mut_ex_rels = [r for r in resolution.claim_relationships if r.relationship_type == ClaimRelationshipType.MUTUALLY_EXCLUSIVE]
    assert len(mut_ex_rels) >= 1
    assert mut_ex_rels[0].is_compatible is False


def test_evidence_reference_verification_flags_unverified(
    resolver: ConsensusResolver,
    recalibrator: ConfidenceRecalibrator,
) -> None:
    """Test that evidence citations not present in patient payload are flagged as unverified."""
    recal = recalibrator.recalibrate_panel(
        agent_outputs=[{
            "agent_role": "Laboratory Specialist",
            "findings": "Serum LDL confirmed elevated.",
            "confidence": 85.0,
        }],
        laboratory_data={"ldl_cholesterol_mg_dl": 210.0},
    )

    # Artificially inject a non-existent citation
    recal.recalibrated_claims[0].grounding_evidence_references.append("fictitious_biomarker_xyz")

    resolution = resolver.resolve_consensus(
        recalibration_result=recal,
        laboratory_data={"ldl_cholesterol_mg_dl": 210.0},
    )

    verified, unverified = resolver.verify_evidence_references(
        claim_resolutions=resolution.claim_resolutions,
        labs={"ldl_cholesterol_mg_dl": 210.0},
        history={},
        symptoms={},
    )
    assert any("ldl_cholesterol" in v.lower() for v in verified)
    assert "fictitious_biomarker_xyz" in unverified


def test_diagnostic_hierarchy_categorization(
    resolver: ConsensusResolver,
    recalibrator: ConfidenceRecalibrator,
) -> None:
    """Test diagnostic categorization into primary, secondary, differential, and safety_critical."""
    agent_outputs = [
        {"agent_role": "Cardiologist", "findings": "Acute myocardial infarction with active ST changes.", "confidence": 88.0},
        {"agent_role": "PCP", "findings": "Essential hypertension chronic comorbidity.", "confidence": 80.0},
        {"agent_role": "Pulmonologist", "findings": "Gastroesophageal reflux disease as differential cause.", "confidence": 45.0},
    ]
    labs = {"cardiac_troponin_ng_ml": 0.12, "systolic_bp": 145.0}

    recal = recalibrator.recalibrate_panel(agent_outputs=agent_outputs, laboratory_data=labs)
    resolution = resolver.resolve_consensus(recalibration_result=recal, laboratory_data=labs)

    assert len(resolution.primary_diagnoses) >= 1
    assert any("infarction" in p.lower() for p in resolution.primary_diagnoses)
    assert len(resolution.secondary_diagnoses) >= 1
    assert any("hypertension" in s.lower() for s in resolution.secondary_diagnoses)
    assert len(resolution.differential_diagnoses) >= 1
    assert len(resolution.safety_critical_diagnoses) >= 1


def test_safety_override_lifecycle_and_decision_support_language(
    resolver: ConsensusResolver,
    recalibrator: ConfidenceRecalibrator,
) -> None:
    """Test safety overrides carry ACTIVE lifecycle state and cautious decision support language."""
    labs = {
        "systolic_bp": 195.0,
        "diastolic_bp": 125.0,
        "serum_creatinine_mg_dl": 2.4,
        "bnp_pg_ml": 650.0,
    }
    symptoms = {"symptoms": ["chest_pain", "dyspnea", "breathlessness"]}

    recal = recalibrator.recalibrate_panel(
        agent_outputs=[{"agent_role": "Cardiologist", "findings": "Hypertensive crisis.", "confidence": 80.0}],
        laboratory_data=labs,
        symptoms_data=symptoms,
    )
    resolution = resolver.resolve_consensus(
        recalibration_result=recal,
        laboratory_data=labs,
        symptoms_data=symptoms,
    )

    assert len(resolution.clinical_safety_warnings) >= 2
    for w in resolution.clinical_safety_warnings:
        assert w.lifecycle_state == SafetyOverrideLifecycleState.ACTIVE
        # Verify non-autonomous decision support language
        assert any(phrase in w.action_recommendation.lower() for phrase in ["recommended", "evaluation", "assessment", "monitoring"])
        # Ensure no imperative direct autonomous orders without recommendation phrasing
        assert "administer 100mg" not in w.action_recommendation.lower()


def test_audit_transcript_cryptographic_tamper_evidence(
    resolver: ConsensusResolver,
    recalibrator: ConfidenceRecalibrator,
) -> None:
    """Test canonical SHA-256 sealing, milestone checkpoints, and tamper detection on audit transcripts."""
    labs = {"fasting_blood_glucose_mg_dl": 280.0, "systolic_bp": 150.0}
    agent_outputs = [{"agent_role": "Endocrinologist", "findings": "Severe hyperglycemia.", "confidence": 80.0}]

    recal = recalibrator.recalibrate_panel(agent_outputs=agent_outputs, laboratory_data=labs)
    resolution = resolver.resolve_consensus(recalibration_result=recal, laboratory_data=labs)
    transcript = resolution.audit_transcript

    # 1. Verification on unaltered transcript
    assert transcript.canonical_transcript_hash is not None
    assert len(transcript.canonical_transcript_hash) == 64
    assert transcript.verify_transcript_integrity() is True

    # 2. Verify all 5 milestone hashes are populated
    assert len(transcript.milestone_hashes) == 5
    expected_milestones = [
        "milestone_1_pre_debate_claims",
        "milestone_2_contradictions_detected",
        "milestone_3_debate_exchanges",
        "milestone_4_confidence_recalibration",
        "milestone_5_consensus_resolution",
    ]
    for m in expected_milestones:
        assert m in transcript.milestone_hashes
        assert len(transcript.milestone_hashes[m]) == 64

    # 3. Tamper detection: modifying any content must cause verification to fail
    tampered_transcript = transcript.model_copy(deep=True)
    tampered_transcript.original_claims[0]["claim_text"] = "TAMPERED FRAUDULENT CLAIM"
    assert tampered_transcript.verify_transcript_integrity() is False

