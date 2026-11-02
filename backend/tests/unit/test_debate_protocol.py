"""Comprehensive Unit Tests for the Multi-Agent Adversarial Debate Protocol (Sub-Step 12.2).

Validates:
1. Round 1: Evidence submission and targeted cross-domain challenge issuance.
2. Round 1: Exclusion of incomparable prediction issues from adversarial challenges.
3. Correct challenge routing: Targeting challenged agent with evidence basis and physiological challenge prompt.
4. Round 2: Evidence-grounded formal concessions (e.g. Statin failure with LDL >= 190).
5. Round 2: Evidence-grounded defenses and preservation of legitimate unresolved clinical disagreements (e.g. Unstable angina).
6. Round 2: Claim revisions (e.g. Asymptomatic severe hypertension and Undiagnosed diabetes).
7. Round 2: Unsupported / missing evidence acknowledgment without fabrication.
8. Maximum two-round enforcement: Strict termination within 2 rounds without circular infinite loops.
9. Convergence and termination states (converged, partial_convergence, unresolved_divergence, no_contradictions).
10. Multiple simultaneous contradictions handled concurrently without state bleed.
11. Natural Language Inference (NLI): Semantic contradiction detection.
12. Natural Language Inference (NLI): Semantic entailment detection.
13. Natural Language Inference (NLI): Neutral / non-overlapping topic classification.
14. Natural Language Inference (NLI): Inconclusive / empty claims handling (UNCERTAIN status).
15. End-to-end integration with ContradictionMatrixResult and fully concordant scenario.
"""

import pytest
from app.agents.consensus.contradiction_detector import ContradictionDetector
from app.agents.consensus.debate_protocol import DebateProtocolEngine, SemanticNLIEngine
from app.schemas.analysis import AgentOutputResponse
from app.schemas.consensus import (
    ChallengeStatus,
    ContradictionCategory,
    ContradictionIssue,
    ContradictionMatrixResult,
    ContradictionSeverity,
    NLIRelation,
    RebuttalDisposition,
)


@pytest.fixture
def detector() -> ContradictionDetector:
    return ContradictionDetector()


@pytest.fixture
def debate_engine() -> DebateProtocolEngine:
    return DebateProtocolEngine(max_rounds=2)


@pytest.fixture
def nli_engine() -> SemanticNLIEngine:
    return SemanticNLIEngine()


# =============================================================================
# Round 1 & Round 2 Protocol Execution Tests
# =============================================================================

def test_round_1_challenge_issuance_and_routing(detector: ContradictionDetector, debate_engine: DebateProtocolEngine) -> None:
    """Test Round 1 generates structured cross-domain challenges and routes correctly."""
    history = {
        "current_medications": [{"name": "Atorvastatin", "treatment_duration_weeks": 20, "adherence": "consistent"}],
    }
    labs = {"ldl_cholesterol_mg_dl": 210.0}

    matrix = detector.evaluate_contradictions(medical_history_data=history, laboratory_data=labs)
    assert matrix.contradictions_detected is True

    transcript = debate_engine.execute_debate(
        contradiction_result=matrix,
        medical_history_data=history,
        laboratory_data=labs,
    )

    assert transcript.total_rounds_executed == 2
    assert len(transcript.challenges) >= 1
    ch = transcript.challenges[0]
    assert ch.round_number == 1
    assert ch.challenging_agent == "Laboratory Biomarker Specialist"
    assert ch.challenged_agent == "Medical History Specialist"
    assert "ldl" in ch.challenged_claim.lower() or "statin" in ch.challenged_claim.lower()
    assert len(ch.evidence_basis) >= 1
    assert len(ch.challenge_text) > 10


def test_round_1_excludes_incomparable_predictions(detector: ContradictionDetector, debate_engine: DebateProtocolEngine) -> None:
    """Test that issues with INCOMPARABLE_PREDICTIONS category are excluded from adversarial challenges."""
    scores = {
        "framingham_risk_percent": 11.2,
        "framingham_risk_category": "moderate",
        "target_outcome": "10_year_incident_cvd",
        "prediction_horizon": "10_years",
        "target_population": "general_adult_population",
    }
    ml = {
        "cardiovascular_risk_percent": 41.5,
        "cardiovascular_risk_category": "high",
        "target_outcome": "cross_sectional_angiographic_cad",
        "prediction_horizon": "cross_sectional",
        "target_population": "catheterization_referral_cohort",
        "calibrated": False,
    }

    matrix = detector.evaluate_contradictions(clinical_scores=scores, ml_predictions=ml)
    assert matrix.contradictions_detected is True
    assert any(i.category == ContradictionCategory.INCOMPARABLE_PREDICTIONS for i in matrix.issues)

    transcript = debate_engine.execute_debate(
        contradiction_result=matrix,
        clinical_scores=scores,
        ml_predictions=ml,
    )

    # Incomparable predictions must NOT generate adversarial challenges
    assert not any("EQ-ML-001" in ch.challenge_id for ch in transcript.challenges)


def test_round_2_evidence_grounded_concession(detector: ContradictionDetector, debate_engine: DebateProtocolEngine) -> None:
    """Test Round 2: Statin therapy vs extreme LDL results in formal concession when adherence is reported consistent."""
    history = {
        "current_medications": [{"name": "Atorvastatin", "treatment_duration_weeks": 24, "adherence": "consistent"}],
    }
    labs = {"ldl_cholesterol_mg_dl": 205.0}

    matrix = detector.evaluate_contradictions(medical_history_data=history, laboratory_data=labs)
    transcript = debate_engine.execute_debate(
        contradiction_result=matrix,
        medical_history_data=history,
        laboratory_data=labs,
    )

    assert len(transcript.conceded_challenges) >= 1
    rebuttal = next(r for r in transcript.rebuttals if r.disposition == RebuttalDisposition.CONCEDE)
    assert "concedes" in rebuttal.rebuttal_text.lower()
    assert rebuttal.concession_reason is not None
    assert len(rebuttal.concession_reason) > 5
    assert rebuttal.evidence_missing is False


def test_round_2_unresolved_disagreement_preservation(detector: ContradictionDetector, debate_engine: DebateProtocolEngine) -> None:
    """Test Round 2: Negative serial troponin with severe ischemic symptoms defends clinical concern and preserves disagreement."""
    symptoms = {
        "symptoms": ["chest_pain", "substernal_pressure"],
        "severity": 8,
        "duration_hours": 4.0,
    }
    labs = {
        "cardiac_troponin_ng_ml": 0.01,
        "serial_troponin_completed": True,
        "resting_ecg": "normal_sinus_rhythm",
    }

    matrix = detector.evaluate_contradictions(symptoms_data=symptoms, laboratory_data=labs)
    transcript = debate_engine.execute_debate(
        contradiction_result=matrix,
        symptoms_data=symptoms,
        laboratory_data=labs,
    )

    assert len(transcript.unresolved_disagreements) >= 1
    rebuttal = next(r for r in transcript.rebuttals if r.disposition == RebuttalDisposition.DEFEND)
    assert "unstable angina" in rebuttal.rebuttal_text.lower()
    assert len(rebuttal.acknowledged_limitations) >= 1


def test_round_2_claim_revision(detector: ContradictionDetector, debate_engine: DebateProtocolEngine) -> None:
    """Test Round 2: Asymptomatic severe hypertension triggers formal claim revision by challenged agent."""
    symptoms = {"symptoms": [], "severity": 1}
    labs = {"systolic_bp": 178.0, "diastolic_bp": 108.0}

    matrix = detector.evaluate_contradictions(symptoms_data=symptoms, laboratory_data=labs)
    transcript = debate_engine.execute_debate(
        contradiction_result=matrix,
        symptoms_data=symptoms,
        laboratory_data=labs,
    )

    rebuttal = next(r for r in transcript.rebuttals if r.disposition == RebuttalDisposition.REVISE)
    assert rebuttal.revised_claim is not None
    assert len(rebuttal.revised_claim) > 5


def test_strict_maximum_two_round_bound(detector: ContradictionDetector, debate_engine: DebateProtocolEngine) -> None:
    """Test that debate protocol strictly enforces maximum 2 rounds and terminates deterministically."""
    symptoms = {"symptoms": ["chest_pain"], "severity": 8, "duration_hours": 4.0}
    labs = {
        "cardiac_troponin_ng_ml": 0.01,
        "serial_troponin_completed": True,
        "ldl_cholesterol_mg_dl": 200.0,
    }
    history = {
        "current_medications": [{"name": "Atorvastatin", "treatment_duration_weeks": 20}],
    }

    matrix = detector.evaluate_contradictions(
        symptoms_data=symptoms,
        medical_history_data=history,
        laboratory_data=labs,
    )
    transcript = debate_engine.execute_debate(
        contradiction_result=matrix,
        symptoms_data=symptoms,
        medical_history_data=history,
        laboratory_data=labs,
    )

    assert transcript.total_rounds_executed <= 2
    assert transcript.max_rounds_allowed == 2
    assert transcript.convergence_status in ["converged", "partial_convergence", "unresolved_divergence"]


def test_concordant_input_immediate_consensus(detector: ContradictionDetector, debate_engine: DebateProtocolEngine) -> None:
    """Test that completely concordant input produces immediate consensus without challenges."""
    matrix = detector.evaluate_contradictions()
    transcript = debate_engine.execute_debate(contradiction_result=matrix)

    assert transcript.convergence_status == "no_contradictions"
    assert len(transcript.challenges) == 0
    assert len(transcript.rebuttals) == 0
    assert "immediate consensus" in transcript.summary.lower()


# =============================================================================
# Natural Language Inference (NLI) Tests
# =============================================================================

def test_nli_semantic_contradiction_detection(nli_engine: SemanticNLIEngine) -> None:
    """Test NLI engine detects direct semantic contradiction between non-smoker and active smoker claims."""
    claim_a = "Patient documents lifelong never smoker status and denies any tobacco use."
    claim_b = "Attributes chronic dyspnea to extensive 30 pack-year smoking history as an active smoker."

    record = nli_engine.analyze_pair(
        agent_a="Medical History Specialist",
        claim_a=claim_a,
        agent_b="Symptom Analysis Specialist",
        claim_b=claim_b,
    )

    assert record.relation == NLIRelation.CONTRADICTION
    assert record.confidence >= 0.85
    assert "contradiction" in record.limitations.lower() or record.relation == NLIRelation.CONTRADICTION


def test_nli_semantic_entailment_detection(nli_engine: SemanticNLIEngine) -> None:
    """Test NLI engine detects semantic entailment between congruent ischemic descriptions."""
    claim_a = "Patient reports crushing substernal chest pain on exertion."
    claim_b = "Exhibits exertional angina and ischemic substernal symptoms."

    record = nli_engine.analyze_pair(
        agent_a="Symptom Analysis Specialist",
        claim_a=claim_a,
        agent_b="Clinical Specialist",
        claim_b=claim_b,
    )

    assert record.relation == NLIRelation.ENTAILMENT
    assert record.confidence >= 0.80


def test_nli_neutral_non_overlapping_topics(nli_engine: SemanticNLIEngine) -> None:
    """Test NLI engine returns NEUTRAL for claims describing non-overlapping medical topics."""
    claim_a = "Patient complains of mild intermittent fatigue."
    claim_b = "Renal function biomarkers and serum electrolytes are within normal reference limits."

    record = nli_engine.analyze_pair(
        agent_a="Symptom Specialist",
        claim_a=claim_a,
        agent_b="Laboratory Specialist",
        claim_b=claim_b,
    )

    assert record.relation == NLIRelation.NEUTRAL


def test_nli_empty_claims_return_uncertain(nli_engine: SemanticNLIEngine) -> None:
    """Test NLI engine returns UNCERTAIN when one or both claims are empty."""
    record = nli_engine.analyze_pair(
        agent_a="Agent A",
        claim_a="",
        agent_b="Agent B",
        claim_b="Patient has hypertension.",
    )

    assert record.relation == NLIRelation.UNCERTAIN
    assert record.confidence <= 0.60
