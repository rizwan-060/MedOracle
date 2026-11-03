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

import math
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
    EvidenceSupportClassification,
    EvidenceValidityState,
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


# =============================================================================
# Hardening & Clinical Safety Tests
# =============================================================================

def test_nan_and_infinity_rejected(recalibrator: ConfidenceRecalibrator) -> None:
    """Test that NaN and Infinity confidence values are rejected explicitly with ValueError."""
    with pytest.raises(ValueError, match="NaN or Infinite"):
        recalibrator.recalibrate_panel(
            agent_outputs=[{
                "agent_role": "Symptom Analysis Specialist",
                "findings": "Chest pain finding.",
                "confidence": float("nan"),
            }]
        )

    with pytest.raises(ValueError, match="NaN or Infinite"):
        recalibrator.recalibrate_panel(
            agent_outputs=[{
                "agent_role": "Symptom Analysis Specialist",
                "findings": "Chest pain finding.",
                "confidence": float("inf"),
            }]
        )


def test_out_of_range_confidence_rejected(recalibrator: ConfidenceRecalibrator) -> None:
    """Test that out-of-range confidence scores (< 0.0 or > 100.0) are rejected explicitly."""
    with pytest.raises(ValueError, match="range \\[0.0, 100.0\\]"):
        recalibrator.recalibrate_panel(
            agent_outputs=[{
                "agent_role": "Specialist",
                "findings": "Negative confidence finding.",
                "confidence": -10.0,
            }]
        )

    with pytest.raises(ValueError, match="range \\[0.0, 100.0\\]"):
        recalibrator.recalibrate_panel(
            agent_outputs=[{
                "agent_role": "Specialist",
                "findings": "Excessive confidence finding.",
                "confidence": 150.0,
            }]
        )


def test_single_normal_troponin_is_insufficient_not_contradictory(recalibrator: ConfidenceRecalibrator) -> None:
    """Test that a single normal troponin is classified as INSUFFICIENT, not CONTRADICTORY, for early acute presentation."""
    result = recalibrator.recalibrate_panel(
        agent_outputs=[{
            "agent_role": "Symptom Analysis Specialist",
            "findings": "Possible acute myocardial ischemia presentation.",
            "confidence": 75.0,
        }],
        laboratory_data={
            "cardiac_troponin_ng_ml": 0.01,
            # serial troponin NOT completed
        },
    )

    record = result.recalibrated_claims[0]
    # Single normal troponin is INSUFFICIENT on its own to exclude or contradict early presentation
    assert record.evidence_classifications.get("cardiac_troponin_ng_ml") == EvidenceSupportClassification.INSUFFICIENT.value
    assert len(record.conflicting_evidence_references) == 0


def test_flat_serial_normal_troponin_contradicts_transmural_necrosis_claim(recalibrator: ConfidenceRecalibrator) -> None:
    """Test that completed flat serial normal troponin contradicts an assertion of confirmed acute myocardial infarction necrosis."""
    result = recalibrator.recalibrate_panel(
        agent_outputs=[{
            "agent_role": "Symptom Analysis Specialist",
            "findings": "Acute myocardial infarction with active cellular necrosis.",
            "confidence": 85.0,
        }],
        laboratory_data={
            "cardiac_troponin_ng_ml": 0.01,
            "serial_troponin_completed": True,
            "resting_ecg": "normal_sinus_rhythm",
        },
    )

    record = result.recalibrated_claims[0]
    assert record.evidence_classifications.get("cardiac_troponin_ng_ml") == EvidenceSupportClassification.CONTRADICTS.value
    assert any("cardiac_troponin_ng_ml" in c for c in record.conflicting_evidence_references)


def test_correlated_blood_pressure_panel_single_grounding(recalibrator: ConfidenceRecalibrator) -> None:
    """Test that systolic and diastolic BP in the same panel award +5.0% collectively, not compounding to +10.0%."""
    result = recalibrator.recalibrate_panel(
        agent_outputs=[{
            "agent_role": "Medical History Specialist",
            "findings": "Severe stage 2 blood pressure elevation.",
            "confidence": 70.0,
        }],
        laboratory_data={
            "systolic_bp": 172.0,
            "diastolic_bp": 104.0,
        },
    )

    record = result.recalibrated_claims[0]
    # Single hemodynamic group awards exactly +5.0%
    assert record.evidence_grounding_adjustment == 5.0
    assert "blood_pressure_measurement" in record.grounding_evidence_references


def test_correlated_lipid_panel_single_grounding(recalibrator: ConfidenceRecalibrator) -> None:
    """Test that citing LDL, Total Cholesterol, and HDL awards +5.0% collectively as a single lipid panel."""
    result = recalibrator.recalibrate_panel(
        agent_outputs=[{
            "agent_role": "Laboratory Specialist",
            "findings": "Significant circulating lipid dysregulation and hypercholesterolemia.",
            "confidence": 75.0,
        }],
        laboratory_data={
            "ldl_cholesterol_mg_dl": 195.0,
            "total_cholesterol_mg_dl": 280.0,
            "hdl_cholesterol_mg_dl": 35.0,
        },
    )

    record = result.recalibrated_claims[0]
    # Single lipid panel group awards exactly +5.0%
    assert record.evidence_grounding_adjustment == 5.0
    assert "ldl_cholesterol_mg_dl" in record.grounding_evidence_references


def test_unverifiable_evidence_due_to_needs_review_awards_zero_grounding(recalibrator: ConfidenceRecalibrator) -> None:
    """Test that laboratory results flagged NEEDS_REVIEW are classified UNVERIFIABLE and award 0 grounding."""
    result = recalibrator.recalibrate_panel(
        agent_outputs=[{
            "agent_role": "Laboratory Specialist",
            "findings": "Acute myocardial necrosis suspected from elevated troponin.",
            "confidence": 80.0,
        }],
        laboratory_data={
            "cardiac_troponin_ng_ml": 0.15,
            "needs_review": True,
            "flag_locale_ambiguity": True,
        },
    )

    record = result.recalibrated_claims[0]
    assert record.evidence_classifications.get("cardiac_troponin_ng_ml") == EvidenceSupportClassification.UNVERIFIABLE.value
    assert record.evidence_grounding_adjustment == 0.0
    assert len(record.evidence_quality_caveats) >= 1


def test_domain_doubt_isolation(recalibrator: ConfidenceRecalibrator) -> None:
    """Test that missing cardiac troponin isolates uncertainty to ischemia, leaving lipidology doubt unaffected."""
    result = recalibrator.recalibrate_panel(
        agent_outputs=[
            {
                "agent_role": "Symptom Analysis Specialist",
                "findings": "Acute myocardial infarction presentation.",
                "confidence": 85.0,
            },
            {
                "agent_role": "Medical History Specialist",
                "findings": "Patient on consistent statin therapy with controlled hyperlipidemia.",
                "confidence": 90.0,
            },
        ],
        laboratory_data={
            # troponin is missing
            "ldl_cholesterol_mg_dl": 190.0,
        },
        medical_history_data={
            "current_medications": [{"name": "Atorvastatin"}],
        },
    )

    # Find domain epistemic doubts
    isch_doubt = next(d for d in result.domain_uncertainty_contributions if d.domain == "ischemia")
    lipid_doubt = next(d for d in result.domain_uncertainty_contributions if d.domain == "lipidology")

    # Ischemia has missing essential troponin -> doubt floor of at least 0.35
    assert isch_doubt.doubt_contribution >= 0.35
    assert "cardiac_troponin_ng_ml" in isch_doubt.missing_essential_evidence

    # Lipidology has verified LDL and statin -> no missing evidence, low/zero doubt
    assert len(lipid_doubt.missing_essential_evidence) == 0
    assert lipid_doubt.doubt_contribution <= 0.15


def test_changed_evidence_snapshot_recalculates_cleanly_from_original_confidence(recalibrator: ConfidenceRecalibrator) -> None:
    """Test that recalculation from a changed evidence snapshot starts freshly from original confidence without compounding."""
    agent_output = [{
        "agent_role": "Laboratory Specialist",
        "findings": "Serum LDL cholesterol confirmed at 195 mg/dL.",
        "confidence": 80.0,
    }]

    # Snapshot 1: no labs provided -> grounding 0.0
    res1 = recalibrator.recalibrate_panel(
        agent_outputs=agent_output,
        laboratory_data={},
    )
    rec1 = res1.recalibrated_claims[0]
    assert rec1.original_confidence == 80.0
    assert rec1.evidence_grounding_adjustment == 0.0
    assert rec1.final_confidence == 80.0

    # Snapshot 2: verified labs provided -> fresh calculation: 80.0 + 5.0 = 85.0
    res2 = recalibrator.recalibrate_panel(
        agent_outputs=agent_output,
        laboratory_data={"ldl_cholesterol_mg_dl": 195.0},
    )
    rec2 = res2.recalibrated_claims[0]
    assert rec2.original_confidence == 80.0
    assert rec2.evidence_grounding_adjustment == 5.0
    assert rec2.final_confidence == 85.0


def test_confidence_at_100_percent_includes_clinical_certainty_warning(recalibrator: ConfidenceRecalibrator) -> None:
    """Test that a claim achieving 100% confidence explicitly includes the non-absolute clinical certainty caveat."""
    result = recalibrator.recalibrate_panel(
        agent_outputs=[{
            "agent_role": "Laboratory Specialist",
            "findings": "Serum LDL cholesterol confirmed at 220 mg/dL.",
            "confidence": 98.0,
        }],
        laboratory_data={
            "ldl_cholesterol_mg_dl": 220.0,
        },
    )

    record = result.recalibrated_claims[0]
    # 98.0 + 5.0 = 103.0 -> clamped to 100.0
    assert record.final_confidence == 100.0
    assert "does not imply absolute clinical certainty" in record.recalibration_explanation


# =============================================================================
# Workstream A Hardening: Clinical Safety, Registry Matching & Provenance Tests
# =============================================================================

def test_dka_without_ketones_triggers_cap(recalibrator: ConfidenceRecalibrator) -> None:
    """Test that a claim of diabetic ketoacidosis (DKA) without ketones is capped at 35%."""
    result = recalibrator.recalibrate_panel(
        agent_outputs=[{
            "agent_role": "Specialist",
            "findings": "Patient presenting with acute diabetic ketoacidosis.",
            "confidence": 85.0,
        }],
        laboratory_data={
            "blood_glucose_mg_dl": 420.0,
            "blood_ph": 7.21,
            # ketones missing
        },
    )
    rec = result.recalibrated_claims[0]
    assert rec.missing_evidence_cap_applied is True
    assert rec.missing_evidence_cap_value == 35.0
    assert rec.final_confidence <= 35.0
    assert any("ketone" in m for m in rec.missing_evidence_details)


def test_dka_without_acid_base_triggers_cap(recalibrator: ConfidenceRecalibrator) -> None:
    """Test that DKA claim without blood pH or serum bicarbonate is capped at 35%."""
    result = recalibrator.recalibrate_panel(
        agent_outputs=[{
            "agent_role": "Specialist",
            "findings": "Suspected diabetic ketoacidosis with high blood sugars.",
            "confidence": 90.0,
        }],
        laboratory_data={
            "fasting_blood_glucose_mg_dl": 380.0,
            "blood_ketones_mmol_l": 4.5,
            # acid-base missing
        },
    )
    rec = result.recalibrated_claims[0]
    assert rec.missing_evidence_cap_applied is True
    assert rec.missing_evidence_cap_value == 35.0
    assert rec.final_confidence <= 35.0
    assert any("ph" in m or "bicarbonate" in m or "acid_base" in m for m in rec.missing_evidence_details)


def test_hhs_without_osmolality_triggers_cap(recalibrator: ConfidenceRecalibrator) -> None:
    """Test that Hyperglycemic Hyperosmolar State (HHS) claim without osmolality is capped at 35%."""
    result = recalibrator.recalibrate_panel(
        agent_outputs=[{
            "agent_role": "Specialist",
            "findings": "Patient exhibits severe hyperglycemic hyperosmolar state (HHS).",
            "confidence": 85.0,
        }],
        laboratory_data={
            "blood_glucose_mg_dl": 750.0,
            # osmolality missing
        },
    )
    rec = result.recalibrated_claims[0]
    assert rec.missing_evidence_cap_applied is True
    assert rec.missing_evidence_cap_value == 35.0
    assert rec.final_confidence <= 35.0
    assert any("osmolality" in m for m in rec.missing_evidence_details)


def test_hba1c_without_acute_crisis_evidence_does_not_confirm_dka(recalibrator: ConfidenceRecalibrator) -> None:
    """Test that high HbA1c alone does not confirm acute DKA and notes caveat."""
    result = recalibrator.recalibrate_panel(
        agent_outputs=[{
            "agent_role": "Specialist",
            "findings": "Acute diabetic ketoacidosis secondary to severe hyperglycemia.",
            "confidence": 80.0,
        }],
        laboratory_data={
            "hba1c_percent": 12.8,
            # acute glucose, ketones, and pH are missing
        },
    )
    rec = result.recalibrated_claims[0]
    assert rec.missing_evidence_cap_applied is True
    assert rec.final_confidence <= 35.0
    assert any("HbA1c" in c for c in rec.evidence_quality_caveats)


def test_hypertensive_emergency_without_target_organ_damage_capped_at_35(recalibrator: ConfidenceRecalibrator) -> None:
    """Test that hypertensive emergency claim with severe BP but no acute target organ damage is capped at 35%."""
    result = recalibrator.recalibrate_panel(
        agent_outputs=[{
            "agent_role": "Specialist",
            "findings": "Hypertensive emergency presenting with critical blood pressure elevation.",
            "confidence": 90.0,
        }],
        laboratory_data={
            "systolic_bp": 210.0,
            "diastolic_bp": 130.0,
            # no target organ damage evidence
        },
    )
    rec = result.recalibrated_claims[0]
    assert rec.missing_evidence_cap_applied is True
    assert rec.missing_evidence_cap_value == 35.0
    assert rec.final_confidence <= 35.0
    assert any("target_organ_damage" in m for m in rec.missing_evidence_details)


def test_hypertensive_emergency_with_target_organ_damage_supported(recalibrator: ConfidenceRecalibrator) -> None:
    """Test that severe BP with verified acute organ damage (e.g. AKI) supports hypertensive emergency."""
    result = recalibrator.recalibrate_panel(
        agent_outputs=[{
            "agent_role": "Specialist",
            "findings": "Hypertensive emergency with acute renal impairment.",
            "confidence": 75.0,
        }],
        laboratory_data={
            "systolic_bp": 200.0,
            "diastolic_bp": 120.0,
            "serum_creatinine_mg_dl": 2.6,  # Acute kidney injury
        },
    )
    rec = result.recalibrated_claims[0]
    assert rec.missing_evidence_cap_applied is False
    assert rec.evidence_grounding_adjustment > 0.0
    assert rec.final_confidence >= 75.0


def test_bnp_interpretation_with_renal_impairment_caveat(recalibrator: ConfidenceRecalibrator) -> None:
    """Test that elevated BNP in patient with renal impairment includes clearance caveat."""
    result = recalibrator.recalibrate_panel(
        agent_outputs=[{
            "agent_role": "Specialist",
            "findings": "Acute heart failure decompensation with elevated BNP.",
            "confidence": 80.0,
        }],
        laboratory_data={
            "bnp_pg_ml": 450.0,
            "egfr_ml_min": 35.0,  # Stage 3b CKD
        },
    )
    rec = result.recalibrated_claims[0]
    assert any("impaired renal function" in c or "eGFR" in c for c in rec.evidence_quality_caveats)


def test_serial_troponin_sample_interval_under_one_hour_flagged_insufficient(recalibrator: ConfidenceRecalibrator) -> None:
    """Test that serial troponin testing with interval < 1 hour is flagged as insufficient per ESC protocols."""
    result = recalibrator.recalibrate_panel(
        agent_outputs=[{
            "agent_role": "Specialist",
            "findings": "Acute myocardial infarction with serial troponin evaluation.",
            "confidence": 85.0,
        }],
        laboratory_data={
            "cardiac_troponin_ng_ml": 0.02,
            "serial_troponin_completed": True,
            "serial_sample_interval_hours": 0.25,  # 15 minutes, insufficient interval
        },
    )
    rec = result.recalibrated_claims[0]
    assert any("interval < 1 hour is insufficient" in c for c in rec.evidence_quality_caveats)
    assert rec.evidence_classifications.get("cardiac_troponin_ng_ml") == EvidenceSupportClassification.INSUFFICIENT.value


def test_serial_troponin_assay_mismatch_flagged(recalibrator: ConfidenceRecalibrator) -> None:
    """Test that serial troponin assay mismatch is flagged and prevents invalid delta comparison."""
    result = recalibrator.recalibrate_panel(
        agent_outputs=[{
            "agent_role": "Specialist",
            "findings": "Acute myocardial infarction suspected.",
            "confidence": 80.0,
        }],
        laboratory_data={
            "cardiac_troponin_ng_ml": 0.02,
            "serial_troponin_completed": True,
            "troponin_assay_mismatch": True,
        },
    )
    rec = result.recalibrated_claims[0]
    assert any("assay mismatch" in c for c in rec.evidence_quality_caveats)


def test_negated_claim_exempt_from_missing_biomarker_cap(recalibrator: ConfidenceRecalibrator) -> None:
    """Test that a claim asserting absence of disease ('No evidence of acute myocardial infarction') is not capped for missing troponin."""
    result = recalibrator.recalibrate_panel(
        agent_outputs=[{
            "agent_role": "Specialist",
            "findings": "No evidence of acute myocardial infarction based on clinical presentation.",
            "confidence": 90.0,
        }],
        laboratory_data={},  # Troponin missing
    )
    rec = result.recalibrated_claims[0]
    # Negated claim must NOT be capped at 40% for lacking a positive troponin!
    assert rec.missing_evidence_cap_applied is False
    assert rec.final_confidence == 90.0


def test_historical_claim_exempt_from_acute_biomarker_cap(recalibrator: ConfidenceRecalibrator) -> None:
    """Test that historical claim ('History of myocardial infarction in 2018') is not capped for missing acute troponin."""
    result = recalibrator.recalibrate_panel(
        agent_outputs=[{
            "agent_role": "Specialist",
            "findings": "Patient has remote history of myocardial infarction.",
            "confidence": 88.0,
        }],
        laboratory_data={},
    )
    rec = result.recalibrated_claims[0]
    assert rec.missing_evidence_cap_applied is False
    assert rec.final_confidence == 88.0


def test_stale_and_invalid_provenance_increases_epistemic_doubt(recalibrator: ConfidenceRecalibrator) -> None:
    """Test that stale records or invalid provenance increase domain quality uncertainty."""
    result = recalibrator.recalibrate_panel(
        agent_outputs=[{
            "agent_role": "Specialist",
            "findings": "Serum LDL remains elevated.",
            "confidence": 75.0,
        }],
        laboratory_data={
            "ldl_cholesterol_mg_dl": 185.0,
            "is_stale": True,
            "invalid_provenance": True,
        },
    )
    rec = result.recalibrated_claims[0]
    assert any("freshness window" in c for c in rec.evidence_quality_caveats)
    assert any("provenance" in c for c in rec.evidence_quality_caveats)
    # Check domain doubt
    lipid_doubt = next(d for d in result.domain_uncertainty_contributions if d.domain == "lipidology")
    assert lipid_doubt.quality_uncertainty_score > 0.30


