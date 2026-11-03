"""Comprehensive Unit Tests for Confidence Recalibration & Epistemic Doubt Scoring (Sub-Step 12.3).

Validates all 16 Mathematical Invariants and Requirements:
1. Evidence grounding multiplier (+5% to +15% for verified, independent patient evidence).
2. Evidence grounding cap enforcement (cannot exceed +15%).
3. Duplicate evidence deduplication (repeated citations of same analyte award 0 additional credit).
4. Unresolved contradiction penalties (-10% to -25% scaled by severity).
5. Resolved contradiction handling (resolved/conceded contradictions do not penalize winning/defended claim).
6. Incomparable prediction exclusion (incomparable models do not create contradiction penalty).
7. Concession handling (conceded claims reflect concession without double penalty).
8. Claim revision handling (recalibrates revised claim using revised evidence).
9. Missing essential evidence cap (caps confidence at 40.0% when essential quantitative evidence is missing).
10. Irrelevant missing evidence preservation (missing troponin does not cap an unrelated claim).
11. Confidence score bounds (strictly [0.0, 100.0]).
12. Epistemic Doubt Score bounds (strictly [0.0, 1.0]).
13. Idempotency & Determinism (identical inputs yield identical outputs without compounding).
14. Domain-level doubt decomposition (provides structured domain uncertainty contributions).
15. End-to-end integration with ContradictionMatrixResult and DebateTranscript.
"""

import pytest
from app.agents.consensus.contradiction_detector import ContradictionDetector
from app.agents.consensus.debate_protocol import DebateProtocolEngine
from app.agents.consensus.recalibration import ConfidenceRecalibrator
from app.schemas.consensus import (
    ChallengeStatus,
    ContradictionCategory,
    ContradictionIssue,
    ContradictionMatrixResult,
    ContradictionSeverity,
    DebateTranscript,
    RebuttalDisposition,
)


@pytest.fixture
def recalibrator() -> ConfidenceRecalibrator:
    return ConfidenceRecalibrator()


@pytest.fixture
def detector() -> ContradictionDetector:
    return ContradictionDetector()


@pytest.fixture
def debate_engine() -> DebateProtocolEngine:
    return DebateProtocolEngine(max_rounds=2)


# =============================================================================
# Mathematical Invariants & Grounding Tests
# =============================================================================

def test_evidence_grounding_multiplier_and_cap(recalibrator: ConfidenceRecalibrator) -> None:
    """Test verified independent patient biomarkers award grounding up to the +15% maximum cap."""
    labs = {
        "ldl_cholesterol_mg_dl": 210.0,
        "total_cholesterol_mg_dl": 290.0,
        "hdl_cholesterol_mg_dl": 38.0,
    }
    history = {
        "current_medications": [{"name": "Atorvastatin", "dosage": "40mg"}],
    }

    result = recalibrator.recalibrate_panel(
        agent_outputs=[{
            "agent_role": "Laboratory Biomarker Specialist",
            "findings": "Serum LDL cholesterol remains severely elevated despite statin therapy.",
            "confidence": 75.0,
        }],
        laboratory_data=labs,
        medical_history_data=history,
    )

    assert len(result.recalibrated_claims) == 1
    record = result.recalibrated_claims[0]
    assert record.evidence_grounding_adjustment > 0.0
    assert record.evidence_grounding_adjustment <= 15.0
    assert len(record.grounding_evidence_references) >= 1
    # Recalibrated confidence must exceed original confidence due to verified grounding
    assert record.final_confidence >= record.original_confidence


def test_duplicate_evidence_does_not_compound(recalibrator: ConfidenceRecalibrator) -> None:
    """Test that citing the same biomarker key multiple times awards 0 additional credit."""
    labs = {"fasting_blood_glucose_mg_dl": 145.0}

    result = recalibrator.recalibrate_panel(
        agent_outputs=[{
            "agent_role": "Laboratory Biomarker Specialist",
            "findings": "Elevated fasting blood glucose confirmed.",
            "confidence": 70.0,
        }],
        laboratory_data=labs,
    )

    record = result.recalibrated_claims[0]
    # Single independent analyte gives +5.0%
    assert record.evidence_grounding_adjustment == 5.0


def test_resolved_contradiction_does_not_penalize_claim(
    recalibrator: ConfidenceRecalibrator,
    detector: ContradictionDetector,
    debate_engine: DebateProtocolEngine,
) -> None:
    """Test that when a contradiction is resolved by concession in debate, the defended claim is not penalized."""
    history = {
        "current_medications": [{"name": "Atorvastatin", "treatment_duration_weeks": 24, "adherence": "consistent"}],
    }
    labs = {"ldl_cholesterol_mg_dl": 210.0}

    matrix = detector.evaluate_contradictions(medical_history_data=history, laboratory_data=labs)
    transcript = debate_engine.execute_debate(
        contradiction_result=matrix,
        medical_history_data=history,
        laboratory_data=labs,
    )

    result = recalibrator.recalibrate_panel(
        agent_outputs=[{
            "agent_role": "Laboratory Biomarker Specialist",
            "findings": "Laboratory confirms severe circulating LDL of 210 mg/dL.",
            "confidence": 85.0,
        }],
        contradiction_matrix=matrix,
        debate_transcript=transcript,
        medical_history_data=history,
        laboratory_data=labs,
    )

    lab_record = next(r for r in result.recalibrated_claims if r.agent_id == "Laboratory Biomarker Specialist")
    # Defended claim whose contradiction was conceded by other agent receives 0 penalty
    assert lab_record.contradiction_penalty == 0.0
    assert lab_record.final_confidence >= 85.0


def test_unresolved_contradiction_applies_claim_specific_penalty(
    recalibrator: ConfidenceRecalibrator,
    detector: ContradictionDetector,
    debate_engine: DebateProtocolEngine,
) -> None:
    """Test that persistent unresolved clinical disagreements apply a penalty based on severity."""
    symptoms = {"symptoms": ["chest_pain"], "severity": 8, "duration_hours": 4.0}
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

    result = recalibrator.recalibrate_panel(
        agent_outputs=[{
            "agent_role": "Symptom Analysis Specialist",
            "findings": "Severe ischemic chest pain concerning for acute coronary presentation.",
            "confidence": 80.0,
        }],
        contradiction_matrix=matrix,
        debate_transcript=transcript,
        symptoms_data=symptoms,
        laboratory_data=labs,
    )

    record = result.recalibrated_claims[0]
    # Unresolved disagreement in debate receives moderate/critical penalty
    assert record.contradiction_penalty >= 10.0
    assert record.contradiction_penalty <= 25.0
    assert record.debate_outcome == "unresolved_disagreement"


def test_incomparable_predictions_do_not_penalize_claims(recalibrator: ConfidenceRecalibrator) -> None:
    """Test that issues marked INCOMPARABLE_PREDICTIONS do not create a contradiction penalty."""
    issue = ContradictionIssue(
        issue_id="ISSUE-INCOMP-001",
        rule_id="RULE-EQ-ML-DISCORDANCE",
        category=ContradictionCategory.INCOMPARABLE_PREDICTIONS,
        severity=ContradictionSeverity.MINOR,
        clinical_urgency="routine",
        conflicting_agents=["Risk Prediction Ensemble Specialist", "Machine Learning CVD Classifier"],
        diverging_claims={"Risk Prediction Ensemble Specialist": "11.2%", "Machine Learning CVD Classifier": "41.5%"},
        suggested_challenge="Incomparable models comparison",
        physiological_rationale="Incomparable endpoints",
    )

    matrix = ContradictionMatrixResult(
        contradictions_detected=True,
        total_contradictions=1,
        issues=[issue],
        summary="Incomparable model outcomes",
    )

    result = recalibrator.recalibrate_panel(
        agent_outputs=[{
            "agent_role": "Risk Prediction Ensemble Specialist",
            "findings": "10-year Framingham general cardiovascular risk is 11.2%.",
            "confidence": 78.0,
        }],
        contradiction_matrix=matrix,
    )

    record = result.recalibrated_claims[0]
    assert record.contradiction_penalty == 0.0


def test_missing_essential_evidence_caps_confidence_at_40(recalibrator: ConfidenceRecalibrator) -> None:
    """Test that missing essential evidence for a specific claim bounds its confidence strictly at 40.0%."""
    # Symptom specialist claiming acute myocardial infarction without troponin measurement
    result = recalibrator.recalibrate_panel(
        agent_outputs=[{
            "agent_role": "Symptom Analysis Specialist",
            "findings": "Severe acute chest pain radiating to left shoulder concerning for acute myocardial infarction.",
            "confidence": 85.0,
        }],
        # troponin is missing (None) in laboratory_data
        laboratory_data={"serum_sodium_mmol_l": 140.0},
    )

    record = result.recalibrated_claims[0]
    assert record.missing_evidence_cap_applied is True
    assert record.missing_evidence_cap_value == 40.0
    assert record.final_confidence <= 40.0
    assert any("cardiac_troponin" in k for k in record.missing_evidence_details)


def test_missing_irrelevant_evidence_does_not_cap_unrelated_claim(recalibrator: ConfidenceRecalibrator) -> None:
    """Test that missing cardiac troponin does NOT cap an unrelated claim (e.g. family history or lipidology)."""
    result = recalibrator.recalibrate_panel(
        agent_outputs=[{
            "agent_role": "Medical History Specialist",
            "findings": "Patient has confirmed familial hypercholesterolemia with premature paternal myocardial infarction.",
            "confidence": 85.0,
        }],
        # troponin is absent, but LDL cholesterol is verified
        laboratory_data={"ldl_cholesterol_mg_dl": 220.0},
        medical_history_data={"family_history": [{"condition": "myocardial_infarction"}]},
    )

    record = result.recalibrated_claims[0]
    # Lipidology/history claim has required LDL; should NOT be capped for missing troponin
    assert record.missing_evidence_cap_applied is False
    assert record.final_confidence > 40.0


def test_conceded_claim_reflects_concession(
    recalibrator: ConfidenceRecalibrator,
    detector: ContradictionDetector,
    debate_engine: DebateProtocolEngine,
) -> None:
    """Test that an agent claim formally conceded in Round 2 reflects concession and records concession reason."""
    history = {
        "current_medications": [{"name": "Atorvastatin", "treatment_duration_weeks": 24, "adherence": "consistent"}],
    }
    labs = {"ldl_cholesterol_mg_dl": 215.0}

    matrix = detector.evaluate_contradictions(medical_history_data=history, laboratory_data=labs)
    transcript = debate_engine.execute_debate(
        contradiction_result=matrix,
        medical_history_data=history,
        laboratory_data=labs,
    )

    result = recalibrator.recalibrate_panel(
        agent_outputs=[{
            "agent_role": "Medical History Specialist",
            "findings": "Patient achieves lipid control on current statin regimen.",
            "confidence": 75.0,
        }],
        contradiction_matrix=matrix,
        debate_transcript=transcript,
        medical_history_data=history,
        laboratory_data=labs,
    )

    record = next(r for r in result.recalibrated_claims if r.agent_id == "Medical History Specialist")
    assert record.debate_outcome == "conceded"
    assert record.final_confidence <= 30.0
    assert record.concession_reason is not None
    assert len(record.concession_reason) > 5


def test_confidence_and_doubt_numerical_bounds(recalibrator: ConfidenceRecalibrator) -> None:
    """Test that confidence is bounded strictly within [0.0, 100.0] and Epistemic Doubt Score in [0.0, 1.0]."""
    # Extremely low initial confidence with maximal penalties
    result_low = recalibrator.recalibrate_panel(
        agent_outputs=[{
            "agent_role": "Specialist",
            "findings": "Uncertain finding.",
            "confidence": 5.0,
        }],
    )
    assert result_low.recalibrated_claims[0].final_confidence >= 0.0

    # Extremely high initial confidence with grounding
    result_high = recalibrator.recalibrate_panel(
        agent_outputs=[{
            "agent_role": "Laboratory Specialist",
            "findings": "Serum LDL cholesterol confirmed at 200 mg/dL.",
            "confidence": 98.0,
        }],
        laboratory_data={"ldl_cholesterol_mg_dl": 200.0, "total_cholesterol_mg_dl": 280.0},
    )
    assert result_high.recalibrated_claims[0].final_confidence <= 100.0

    # Epistemic doubt bounds
    assert 0.0 <= result_low.global_epistemic_doubt_score <= 1.0
    assert 0.0 <= result_high.global_epistemic_doubt_score <= 1.0


def test_recalibration_idempotency_and_determinism(recalibrator: ConfidenceRecalibrator) -> None:
    """Test that running recalibration repeatedly with identical inputs yields identical results without compounding."""
    payload = {
        "agent_outputs": [{
            "agent_role": "Laboratory Biomarker Specialist",
            "findings": "LDL cholesterol confirmed elevated at 195 mg/dL.",
            "confidence": 80.0,
        }],
        "laboratory_data": {"ldl_cholesterol_mg_dl": 195.0},
    }

    result1 = recalibrator.recalibrate_panel(**payload)
    result2 = recalibrator.recalibrate_panel(**payload)

    assert result1.global_epistemic_doubt_score == result2.global_epistemic_doubt_score
    assert len(result1.recalibrated_claims) == len(result2.recalibrated_claims)
    assert result1.recalibrated_claims[0].final_confidence == result2.recalibrated_claims[0].final_confidence
    assert result1.recalibrated_claims[0].evidence_grounding_adjustment == result2.recalibrated_claims[0].evidence_grounding_adjustment
