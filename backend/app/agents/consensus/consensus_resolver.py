"""Consensus Resolution and Audit Transcript Generation Engine (Sub-Step 12.4).

Integrates the multi-agent deliberation outputs from:
1. Contradiction Detection Engine (Sub-Step 12.1)
2. Adversarial Debate Protocol (Sub-Step 12.2)
3. Mathematical Confidence Recalibration & Epistemic Doubt Scoring (Sub-Step 12.3)

Core Architectural Invariants:
- Evidence-Aware Claim Resolution: Verified patient evidence strictly takes precedence
  over ungrounded narrative claims. Seniority or agent role confers zero evidential weight.
- No Simple Majority Voting: Majority consensus is strictly prohibited; clinical correctness
  is governed by physiological evidence grounding and guideline concordance.
- Explicit Consensus State Taxonomy: Evaluates each specialist claim into:
  SUPPORTED, PROVISIONAL, CONFLICTING, UNRESOLVED, INSUFFICIENT_EVIDENCE, UNSUPPORTED, WITHDRAWN.
- Multi-Claim Comorbidity Preservation: Multiple coexisting medical conditions (e.g.
  Type 2 Diabetes, Essential Hypertension, Dyslipidemia) are preserved as independent,
  valid claims without forced single-diagnosis reductionism.
- Clinical Safety Overrides: Life-threatening presentations (ACS, DKA, HHS, Hypertensive Emergency)
  trigger non-suppressible safety alerts that persist regardless of agent disagreements.
- Immutable Audit Transcript: Generates a complete, traceable, deterministic audit trail
  documenting pre-debate claims, contradiction matrix issues, debate exchanges,
  recalibrated support scores, domain doubts, and final resolution rationales.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

from app.agents.consensus.contradiction_detector import ContradictionDetector
from app.agents.consensus.debate_protocol import DebateProtocolEngine
from app.agents.consensus.recalibration import ConfidenceRecalibrator
from app.schemas.consensus import (
    AuditDebateTranscript,
    ChallengeStatus,
    ClaimConsensusState,
    ClaimRecalibrationRecord,
    ClaimResolutionRecord,
    ConfidenceRecalibrationResult,
    ContradictionCategory,
    ContradictionIssue,
    ContradictionMatrixResult,
    ContradictionSeverity,
    DebateTranscript,
    EvidenceSupportClassification,
    OverallConsensusOutcome,
    SafetyOverrideLevel,
    SafetyOverrideWarning,
    ConsensusResolutionResult,
)

logger = logging.getLogger("consensus_resolver")


class ConsensusResolver:
    """Evidence-Aware Multi-Agent Consensus Resolution and Audit Transcript Engine."""

    VERSION = "consensus_resolution_v1.0.0"

    def __init__(
        self,
        support_confidence_threshold: float = 65.0,
        provisional_confidence_threshold: float = 40.0,
    ) -> None:
        """Initialize ConsensusResolver with bounded evidence thresholds."""
        self.support_confidence_threshold = float(support_confidence_threshold)
        self.provisional_confidence_threshold = float(provisional_confidence_threshold)

        logger.info(
            "Initialized ConsensusResolver (%s) with Support Threshold: %.1f%%, Provisional Threshold: %.1f%%",
            self.VERSION,
            self.support_confidence_threshold,
            self.provisional_confidence_threshold,
        )

    def resolve_consensus(
        self,
        recalibration_result: Optional[ConfidenceRecalibrationResult] = None,
        contradiction_matrix: Optional[ContradictionMatrixResult] = None,
        debate_transcript: Optional[DebateTranscript] = None,
        agent_outputs: Optional[List[Any]] = None,
        symptoms_data: Optional[Dict[str, Any]] = None,
        medical_history_data: Optional[Dict[str, Any]] = None,
        laboratory_data: Optional[Dict[str, Any]] = None,
        clinical_scores: Optional[Dict[str, Any]] = None,
        ml_predictions: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
        analysis_id: Optional[str] = None,
        patient_id: Optional[str] = None,
        disagreement_threshold: float = 25.0,
    ) -> ConsensusResolutionResult:
        """Execute complete evidence-aware consensus resolution and audit transcript generation."""
        symptoms = symptoms_data or {}
        history = medical_history_data or {}
        labs = laboratory_data or {}
        scores = clinical_scores or {}
        ml = ml_predictions or {}

        session_token = session_id or (recalibration_result.session_id if recalibration_result else f"sess-{uuid.uuid4().hex[:6]}")
        patient_token = patient_id or (recalibration_result.patient_id if recalibration_result else "anon")
        analysis_token = analysis_id or f"analysis-{uuid.uuid4().hex[:8]}"

        # 1. Pipeline Execution / Fallback Recovery
        if contradiction_matrix is None:
            detector = ContradictionDetector(default_disagreement_threshold=disagreement_threshold)
            contradiction_matrix = detector.evaluate_contradictions(
                symptoms_data=symptoms,
                medical_history_data=history,
                laboratory_data=labs,
                clinical_scores=scores,
                ml_predictions=ml,
                agent_outputs=agent_outputs,
                session_id=session_token,
                patient_id=patient_token,
                disagreement_threshold=disagreement_threshold,
            )

        if debate_transcript is None:
            debate_engine = DebateProtocolEngine(max_rounds=2)
            debate_transcript = debate_engine.execute_debate(
                contradiction_result=contradiction_matrix,
                agent_outputs=agent_outputs,
                symptoms_data=symptoms,
                medical_history_data=history,
                laboratory_data=labs,
                clinical_scores=scores,
                ml_predictions=ml,
                session_id=session_token,
                patient_id=patient_token,
            )

        if recalibration_result is None:
            recalibrator = ConfidenceRecalibrator()
            recalibration_result = recalibrator.recalibrate_panel(
                agent_outputs=agent_outputs,
                contradiction_matrix=contradiction_matrix,
                debate_transcript=debate_transcript,
                symptoms_data=symptoms,
                medical_history_data=history,
                laboratory_data=labs,
                clinical_scores=scores,
                ml_predictions=ml,
                session_id=session_token,
                patient_id=patient_token,
            )

        # 2. Claim-Level Consensus Resolution
        claim_resolutions = self.resolve_claims(
            recalibration_result=recalibration_result,
            contradiction_matrix=contradiction_matrix,
            debate_transcript=debate_transcript,
            labs=labs,
            symptoms=symptoms,
        )

        # 3. Extract Clinical Safety Overrides (Independent of Consensus)
        safety_warnings = self.extract_safety_overrides(
            claim_resolutions=claim_resolutions,
            symptoms=symptoms,
            labs=labs,
            history=history,
        )

        # 4. Multi-Claim Overall Consensus Aggregation
        overall_outcome = self.aggregate_overall_outcome(
            claim_resolutions=claim_resolutions,
            contradiction_matrix=contradiction_matrix,
            debate_transcript=debate_transcript,
            safety_warnings=safety_warnings,
        )

        # 5. Generate Immutable Audit Debate Transcript
        audit_transcript = self.generate_audit_transcript(
            session_id=session_token,
            analysis_id=analysis_token,
            patient_id=patient_token,
            contradiction_matrix=contradiction_matrix,
            debate_transcript=debate_transcript,
            recalibration_result=recalibration_result,
            claim_resolutions=claim_resolutions,
            overall_outcome=overall_outcome,
            safety_warnings=safety_warnings,
        )

        # 6. Formulate Executive Clinical Summary
        supported_count = sum(1 for c in claim_resolutions if c.consensus_state == ClaimConsensusState.SUPPORTED)
        provisional_count = sum(1 for c in claim_resolutions if c.consensus_state == ClaimConsensusState.PROVISIONAL)
        unresolved_count = sum(1 for c in claim_resolutions if c.consensus_state in [ClaimConsensusState.CONFLICTING, ClaimConsensusState.UNRESOLVED])
        insufficient_count = sum(1 for c in claim_resolutions if c.consensus_state == ClaimConsensusState.INSUFFICIENT_EVIDENCE)

        summary = (
            f"Consensus Resolution Engine ({self.VERSION}) finalized overall outcome: {overall_outcome.value}. "
            f"Evaluated {len(claim_resolutions)} clinical claims: {supported_count} Supported, "
            f"{provisional_count} Provisional, {unresolved_count} Conflicting/Unresolved, "
            f"{insufficient_count} Insufficient Evidence. "
            f"Preserved {len(safety_warnings)} active clinical safety override(s). "
            f"Global Epistemic Doubt Score: {recalibration_result.global_epistemic_doubt_score:.3f}."
        )

        methodological_notes = [
            "Consensus resolution operates under structured clinical decision rules and guideline-grounded evidentiary standards. It does not replace clinical physician judgment.",
            "Majority voting is strictly rejected in MedOracle; agent agreement does not independently confer diagnostic correctness.",
            "Clinical safety overrides operate independently of consensus resolution and persist regardless of specialist disagreements or debate concessions.",
            "Multiple concordant comorbidities (e.g. Type 2 Diabetes, Essential Hypertension) are preserved as independent valid clinical entities rather than compressed into a single diagnosis.",
            "Missing quantitative clinical evidence enforces an epistemic bound and is never equated with a negative or normal finding.",
        ]

        logger.info(
            "Consensus resolution completed for analysis %s: outcome %s with %d safety overrides",
            analysis_token,
            overall_outcome.value,
            len(safety_warnings),
        )

        return ConsensusResolutionResult(
            session_id=session_token,
            analysis_id=analysis_token,
            patient_id=patient_token,
            overall_outcome=overall_outcome,
            claim_resolutions=claim_resolutions,
            clinical_safety_warnings=safety_warnings,
            global_epistemic_doubt_score=recalibration_result.global_epistemic_doubt_score,
            audit_transcript=audit_transcript,
            resolution_summary=summary,
            methodological_notes=methodological_notes,
        )

    # -------------------------------------------------------------------------
    # Claim-Level Consensus Evaluation
    # -------------------------------------------------------------------------

    def resolve_claims(
        self,
        recalibration_result: ConfidenceRecalibrationResult,
        contradiction_matrix: ContradictionMatrixResult,
        debate_transcript: DebateTranscript,
        labs: Dict[str, Any],
        symptoms: Dict[str, Any],
    ) -> List[ClaimResolutionRecord]:
        """Resolve consensus state individually for each recalibrated specialist claim."""
        resolved_records: List[ClaimResolutionRecord] = []

        # Map domain doubts for rapid lookup
        domain_doubt_map = {
            d.domain: d.doubt_contribution for d in recalibration_result.domain_uncertainty_contributions
        }

        for rec in recalibration_result.recalibrated_claims:
            state, rationale = self._evaluate_single_claim_state(
                record=rec,
                contradiction_matrix=contradiction_matrix,
                debate_transcript=debate_transcript,
                labs=labs,
                symptoms=symptoms,
            )

            resolved_records.append(
                ClaimResolutionRecord(
                    claim_id=rec.claim_id,
                    agent_id=rec.agent_id,
                    original_claim=rec.claim_text,
                    clinical_domain=rec.clinical_domain,
                    consensus_state=state,
                    recalibrated_confidence=rec.recalibrated_confidence,
                    final_confidence=rec.final_confidence,
                    evidence_grounding_references=rec.grounding_evidence_references,
                    evidence_classifications=rec.evidence_classifications,
                    conflicting_evidence_references=rec.conflicting_evidence_references,
                    missing_evidence_details=rec.missing_evidence_details,
                    contradiction_issue_ids=rec.contradiction_issue_ids,
                    debate_outcome=rec.debate_outcome,
                    is_withdrawn=rec.is_withdrawn,
                    is_revised=(rec.debate_outcome == "revised"),
                    revised_claim_text=rec.claim_text if rec.debate_outcome == "revised" else None,
                    domain_epistemic_doubt=domain_doubt_map.get(rec.clinical_domain, 0.0),
                    resolution_rationale=rationale,
                )
            )

        return resolved_records

    def _evaluate_single_claim_state(
        self,
        record: ClaimRecalibrationRecord,
        contradiction_matrix: ContradictionMatrixResult,
        debate_transcript: DebateTranscript,
        labs: Dict[str, Any],
        symptoms: Dict[str, Any],
    ) -> Tuple[ClaimConsensusState, str]:
        """Determine explicit consensus state using verified evidence priority principles."""
        # 1. State: WITHDRAWN
        if record.is_withdrawn or (record.debate_outcome == "conceded" and not record.grounding_evidence_references and record.final_confidence <= 30.0):
            reason = record.concession_reason or "Claim formally conceded or withdrawn during multi-agent adversarial debate."
            return ClaimConsensusState.WITHDRAWN, f"Claim withdrawn by specialist ({reason})."

        # 2. State: UNSUPPORTED
        if record.debate_outcome == "unsupported":
            return ClaimConsensusState.UNSUPPORTED, "Claim lacked any verified clinical evidence during adversarial cross-examination."

        # 3. State: INSUFFICIENT_EVIDENCE
        if record.missing_evidence_cap_applied:
            missing_str = ", ".join(record.missing_evidence_details)
            return (
                ClaimConsensusState.INSUFFICIENT_EVIDENCE,
                f"Mandatory diagnostic evidence is missing ({missing_str}); confidence strictly capped at {record.missing_evidence_cap_value:.0f}%.",
            )

        # Check if essential evidence items are classified as INSUFFICIENT or UNVERIFIABLE
        has_insufficient_class = any(
            cls == EvidenceSupportClassification.INSUFFICIENT.value for cls in record.evidence_classifications.values()
        )
        has_unverifiable_class = any(
            cls == EvidenceSupportClassification.UNVERIFIABLE.value for cls in record.evidence_classifications.values()
        )
        if has_unverifiable_class:
            return ClaimConsensusState.INSUFFICIENT_EVIDENCE, "Referenced laboratory evidence failed verification or quality audit."

        # 4. State: CONFLICTING
        if record.conflicting_evidence_references:
            conf_str = "; ".join(record.conflicting_evidence_references)
            return (
                ClaimConsensusState.CONFLICTING,
                f"Directly contradicted by verified objective laboratory findings: {conf_str}.",
            )

        # Check for active unresolved contradiction with material severity
        has_active_critical = False
        if contradiction_matrix and contradiction_matrix.issues:
            for issue in contradiction_matrix.issues:
                if issue.issue_id in record.contradiction_issue_ids:
                    if issue.category != ContradictionCategory.INCOMPARABLE_PREDICTIONS:
                        if issue.severity == ContradictionSeverity.CRITICAL and record.debate_outcome == "unresolved_disagreement":
                            has_active_critical = True

        if has_active_critical:
            return (
                ClaimConsensusState.CONFLICTING,
                "Persistent critical contradiction remains unresolved between specialists with valid opposing arguments.",
            )

        # 5. State: UNRESOLVED
        if record.debate_outcome == "unresolved_disagreement":
            return (
                ClaimConsensusState.UNRESOLVED,
                "Adversarial debate ended in unresolved clinical disagreement without empirical objective proof.",
            )

        # 6. State: PROVISIONAL
        # Evidence supports claim, but caveats exist or confidence is intermediate
        if has_insufficient_class or len(record.evidence_quality_caveats) > 0 or record.final_confidence < self.support_confidence_threshold:
            caveats_str = "; ".join(record.evidence_quality_caveats) if record.evidence_quality_caveats else f"Confidence ({record.final_confidence:.1f}%) below full support threshold ({self.support_confidence_threshold:.0f}%)"
            return (
                ClaimConsensusState.PROVISIONAL,
                f"Evidence provisionally supports claim, but clinical caveats or uncertainty remain: {caveats_str}.",
            )

        # 7. State: SUPPORTED
        if record.grounding_evidence_references and record.final_confidence >= self.support_confidence_threshold:
            evidence_str = ", ".join(record.grounding_evidence_references)
            return (
                ClaimConsensusState.SUPPORTED,
                f"Fully supported by verified patient evidence ({evidence_str}) with zero active contradiction penalty.",
            )

        # Default fallback: PROVISIONAL
        return (
            ClaimConsensusState.PROVISIONAL,
            f"Plausible clinical claim with final confidence of {record.final_confidence:.1f}%.",
        )

    # -------------------------------------------------------------------------
    # Clinical Safety Overrides Extraction
    # -------------------------------------------------------------------------

    def extract_safety_overrides(
        self,
        claim_resolutions: List[ClaimResolutionRecord],
        symptoms: Dict[str, Any],
        labs: Dict[str, Any],
        history: Dict[str, Any],
    ) -> List[SafetyOverrideWarning]:
        """Extract urgent clinical safety overrides that must never be suppressed by consensus."""
        warnings: List[SafetyOverrideWarning] = []
        sym_list = [s.lower() for s in symptoms.get("symptoms", [])]

        # 1. Acute Coronary Syndrome / Myocardial Infarction Alert
        has_chest_pain = any(s in ["chest_pain", "angina", "substernal_pressure"] for s in sym_list)
        troponin_val = labs.get("cardiac_troponin_ng_ml") or labs.get("hs_troponin_i_ng_ml") or labs.get("hs_troponin_t_ng_ml")
        ecg_val = str(labs.get("resting_ecg") or "").lower()

        is_troponin_elevated = False
        if troponin_val is not None:
            try:
                is_troponin_elevated = float(troponin_val) > 0.04
            except (ValueError, TypeError):
                pass

        has_ecg_ischemia = any(k in ecg_val for k in ["st_elevation", "st_depression", "ischemi", "t_wave_inversion"])
        has_acs_claim = any(
            any(k in c.original_claim.lower() for k in ["acute myocardial", "stemi", "nstemi", "acute coronary"])
            for c in claim_resolutions
        )
        has_chest_pain_claim = any(
            any(k in c.original_claim.lower() for k in ["chest pain", "angina", "substernal", "acute chest"])
            for c in claim_resolutions
        )

        if has_acs_claim or has_chest_pain or has_chest_pain_claim or is_troponin_elevated or has_ecg_ischemia:
            warnings.append(
                SafetyOverrideWarning(
                    warning_id=f"WARN-ACS-{uuid.uuid4().hex[:6]}",
                    condition_name="Suspected Acute Coronary Syndrome (ACS)",
                    level=SafetyOverrideLevel.EMERGENT,
                    trigger_rationale="Acute ischemic symptoms or objective cardiac markers indicate potential ongoing myocardial necrosis or unstable plaque rupture.",
                    action_recommendation="Immediate Emergency Department evaluation, 12-lead ECG, continuous telemetry, and serial high-sensitivity troponin at 0h and 1h/3h per ESC guidelines.",
                    overrides_consensus=True,
                )
            )

        # 2. Diabetic Ketoacidosis (DKA) / Hyperosmolar Hyperglycemic State (HHS) Alert
        glucose_val = labs.get("fasting_blood_glucose_mg_dl") or labs.get("random_blood_glucose_mg_dl") or labs.get("blood_glucose_mg_dl")
        ketone_val = labs.get("blood_ketones_mmol_l") or labs.get("beta_hydroxybutyrate_mmol_l")
        has_dka_claim = any(
            any(k in c.original_claim.lower() for k in ["diabetic ketoacidosis", "dka", "ketoacidosis", "hyperglycemic hyperosmolar", "hhs"])
            for c in claim_resolutions
        )

        is_severe_hyperglycemia = False
        if glucose_val is not None:
            try:
                is_severe_hyperglycemia = float(glucose_val) >= 300.0
            except (ValueError, TypeError):
                pass

        is_ketonemia = False
        if ketone_val is not None:
            try:
                is_ketonemia = float(ketone_val) >= 1.5
            except (ValueError, TypeError):
                pass

        if has_dka_claim or (is_severe_hyperglycemia and (is_ketonemia or ketone_val is None)):
            warnings.append(
                SafetyOverrideWarning(
                    warning_id=f"WARN-DKA-{uuid.uuid4().hex[:6]}",
                    condition_name="Suspected Diabetic Ketoacidosis / Hyperglycemic Crisis",
                    level=SafetyOverrideLevel.EMERGENT,
                    trigger_rationale="Marked hyperglycemia or clinical suspicion of acute metabolic decompensation with risk of life-threatening acidosis or hyperosmolality.",
                    action_recommendation="Immediate evaluation of venous blood gas (pH, bicarbonate), serum beta-hydroxybutyrate, electrolytes, and aggressive IV fluid resuscitation.",
                    overrides_consensus=True,
                )
            )

        # 3. Hypertensive Emergency Alert
        sbp = labs.get("systolic_bp")
        dbp = labs.get("diastolic_bp")
        is_severe_bp = False
        if sbp is not None or dbp is not None:
            try:
                s_num = float(sbp) if sbp is not None else 0.0
                d_num = float(dbp) if dbp is not None else 0.0
                if s_num >= 180.0 or d_num >= 120.0:
                    is_severe_bp = True
            except (ValueError, TypeError):
                pass

        has_tod = False
        if labs.get("serum_creatinine_mg_dl") and float(labs.get("serum_creatinine_mg_dl", 0)) >= 2.0:
            has_tod = True
        if is_troponin_elevated:
            has_tod = True
        if has_chest_pain or any(s in ["dyspnea", "breathlessness"] for s in sym_list):
            has_tod = True

        has_htn_emerg_claim = any("hypertensive emergency" in c.original_claim.lower() for c in claim_resolutions)

        if is_severe_bp:
            if has_tod or has_htn_emerg_claim:
                warnings.append(
                    SafetyOverrideWarning(
                        warning_id=f"WARN-HTN-EMERG-{uuid.uuid4().hex[:6]}",
                        condition_name="Suspected Hypertensive Emergency",
                        level=SafetyOverrideLevel.EMERGENT,
                        trigger_rationale=f"Severe blood pressure elevation ({sbp}/{dbp} mmHg) concurrent with signs of acute target-organ involvement (cardiac/renal/symptom).",
                        action_recommendation="Immediate Emergency Department admission for controlled IV antihypertensive administration and acute target-organ assessment.",
                        overrides_consensus=True,
                    )
                )
            else:
                warnings.append(
                    SafetyOverrideWarning(
                        warning_id=f"WARN-HTN-URG-{uuid.uuid4().hex[:6]}",
                        condition_name="Severe Blood Pressure Elevation (Hypertensive Urgency)",
                        level=SafetyOverrideLevel.URGENT,
                        trigger_rationale=f"Severe blood pressure elevation ({sbp}/{dbp} mmHg) without documented acute target-organ damage.",
                        action_recommendation="Prompt outpatient or urgent care medical evaluation within 24 hours for oral antihypertensive titration and organ damage screening.",
                        overrides_consensus=True,
                    )
                )

        return warnings

    # -------------------------------------------------------------------------
    # Multi-Claim Overall Consensus Aggregation
    # -------------------------------------------------------------------------

    def aggregate_overall_outcome(
        self,
        claim_resolutions: List[ClaimResolutionRecord],
        contradiction_matrix: ContradictionMatrixResult,
        debate_transcript: DebateTranscript,
        safety_warnings: List[SafetyOverrideWarning],
    ) -> OverallConsensusOutcome:
        """Aggregate individual claim decisions into an overall analysis-level consensus outcome."""
        if not claim_resolutions:
            return OverallConsensusOutcome.INSUFFICIENT_EVIDENCE

        active_claims = [c for c in claim_resolutions if c.consensus_state != ClaimConsensusState.WITHDRAWN]

        if not active_claims:
            return OverallConsensusOutcome.UNRESOLVED_CONSENSUS

        states = [c.consensus_state for c in active_claims]

        # Rule 1: Acute life-threatening claims with missing essential evidence enforce INSUFFICIENT_EVIDENCE
        acute_domains = ["ischemia", "glycemia", "hemodynamics"]
        acute_insufficient = any(
            c.consensus_state == ClaimConsensusState.INSUFFICIENT_EVIDENCE
            and c.clinical_domain in acute_domains
            and any(k in c.original_claim.lower() for k in ["acute", "infarction", "dka", "emergency", "crisis"])
            for c in active_claims
        )
        if acute_insufficient:
            return OverallConsensusOutcome.INSUFFICIENT_EVIDENCE

        # Rule 2: Unresolved critical contradictions across the debate enforce UNRESOLVED_CONSENSUS
        has_unresolved_critical = False
        if contradiction_matrix and contradiction_matrix.issues:
            for issue in contradiction_matrix.issues:
                if issue.category != ContradictionCategory.INCOMPARABLE_PREDICTIONS:
                    if issue.severity == ContradictionSeverity.CRITICAL:
                        if debate_transcript and issue.issue_id not in debate_transcript.conceded_challenges:
                            # Not conceded and not revised
                            revised = any(ch.issue_id == issue.issue_id and ch.status == ChallengeStatus.REVISED for ch in debate_transcript.challenges)
                            if not revised:
                                has_unresolved_critical = True

        if has_unresolved_critical or ClaimConsensusState.CONFLICTING in states:
            return OverallConsensusOutcome.UNRESOLVED_CONSENSUS

        # Rule 3: All active claims are SUPPORTED -> CONSENSUS_SUPPORTED
        if all(s == ClaimConsensusState.SUPPORTED for s in states):
            return OverallConsensusOutcome.CONSENSUS_SUPPORTED

        # Rule 4: All active claims are PROVISIONAL -> CONSENSUS_PROVISIONAL
        if all(s == ClaimConsensusState.PROVISIONAL for s in states):
            return OverallConsensusOutcome.CONSENSUS_PROVISIONAL

        # Rule 5: Mix of SUPPORTED and PROVISIONAL (or independent concordant comorbidities) -> PARTIAL_CONSENSUS
        supported_present = any(s == ClaimConsensusState.SUPPORTED for s in states)
        non_damaging_remainder = all(
            s in [ClaimConsensusState.SUPPORTED, ClaimConsensusState.PROVISIONAL, ClaimConsensusState.INSUFFICIENT_EVIDENCE]
            for s in states
        )
        if supported_present and non_damaging_remainder:
            return OverallConsensusOutcome.PARTIAL_CONSENSUS

        # Rule 6: If all claims have insufficient evidence -> INSUFFICIENT_EVIDENCE
        if all(s == ClaimConsensusState.INSUFFICIENT_EVIDENCE for s in states):
            return OverallConsensusOutcome.INSUFFICIENT_EVIDENCE

        # Default fallback
        return OverallConsensusOutcome.PARTIAL_CONSENSUS

    # -------------------------------------------------------------------------
    # Immutable Audit Debate Transcript Generation
    # -------------------------------------------------------------------------

    def generate_audit_transcript(
        self,
        session_id: str,
        analysis_id: str,
        patient_id: str,
        contradiction_matrix: ContradictionMatrixResult,
        debate_transcript: DebateTranscript,
        recalibration_result: ConfidenceRecalibrationResult,
        claim_resolutions: List[ClaimResolutionRecord],
        overall_outcome: OverallConsensusOutcome,
        safety_warnings: List[SafetyOverrideWarning],
    ) -> AuditDebateTranscript:
        """Construct the immutable, traceable audit debate transcript."""
        transcript_token = f"TRANSCRIPT-{session_id}-{uuid.uuid4().hex[:6]}"

        participating_agents = list({c.agent_id for c in claim_resolutions})

        original_claims = [
            {
                "claim_id": c.claim_id,
                "agent_id": c.agent_id,
                "claim_text": c.original_claim,
                "clinical_domain": c.clinical_domain,
            }
            for c in claim_resolutions
        ]

        all_evidence_refs = list({
            ref for c in claim_resolutions for ref in c.evidence_grounding_references
        })

        contradiction_records = [
            {
                "issue_id": i.issue_id,
                "rule_id": i.rule_id,
                "category": i.category.value,
                "severity": i.severity.value,
                "conflicting_agents": i.conflicting_agents,
                "diverging_claims": i.diverging_claims,
                "physiological_rationale": i.physiological_rationale,
            }
            for i in contradiction_matrix.issues
        ]

        challenges = [
            {
                "challenge_id": ch.challenge_id,
                "challenging_agent": getattr(ch, "challenging_agent", getattr(ch, "challenger_agent", "unknown")),
                "challenged_agent": getattr(ch, "challenged_agent", "unknown"),
                "challenge_text": getattr(ch, "challenge_text", ""),
                "status": ch.status.value if hasattr(ch.status, "value") else str(ch.status),
            }
            for ch in debate_transcript.challenges
        ]

        rebuttals = [
            {
                "rebuttal_id": r.rebuttal_id,
                "challenge_id": r.challenge_id,
                "responding_agent": r.responding_agent,
                "disposition": r.disposition.value if hasattr(r.disposition, "value") else str(r.disposition),
                "rebuttal_text": r.rebuttal_text,
                "is_concession": (
                    getattr(r, "is_concession", False)
                    or (r.disposition.value == "concede" if hasattr(r.disposition, "value") else str(r.disposition) == "concede")
                    or r.concession_reason is not None
                ),
            }
            for r in debate_transcript.rebuttals
        ]

        revisions = [
            {
                "challenge_id": r.challenge_id,
                "responding_agent": r.responding_agent,
                "revised_claim": r.revised_claim,
            }
            for r in debate_transcript.rebuttals if getattr(r, "revised_claim", None)
        ]

        concessions = [
            {
                "challenge_id": r.challenge_id,
                "responding_agent": r.responding_agent,
                "concession_reason": r.concession_reason,
            }
            for r in debate_transcript.rebuttals
            if (
                getattr(r, "concession_reason", None)
                or (r.disposition.value == "concede" if hasattr(r.disposition, "value") else str(r.disposition) == "concede")
            )
        ]

        unsupported_findings = [
            ch.challenged_claim for ch in debate_transcript.challenges if ch.status == ChallengeStatus.UNSUPPORTED
        ]

        recalibrated_scores = {
            c.claim_id: c.final_confidence for c in claim_resolutions
        }

        epistemic_doubts = {
            d.domain: d.doubt_contribution for d in recalibration_result.domain_uncertainty_contributions
        }

        unresolved_issues = [
            ch.challenge_text for ch in debate_transcript.challenges if ch.status == ChallengeStatus.UNRESOLVED_DISAGREEMENT
        ]
        if recalibration_result.missing_evidence_summary:
            unresolved_issues.extend([
                f"Missing essential diagnostic analyte: {m}" for m in recalibration_result.missing_evidence_summary
            ])

        rationale = (
            f"Multi-agent adversarial debate finalized with convergence status: {debate_transcript.convergence_status}. "
            f"Across {len(claim_resolutions)} claims, overall consensus was determined as {overall_outcome.value} "
            f"following mathematical evidence grounding, domain-deduplicated contradiction penalties, and essential evidence bounds. "
            f"Global residual epistemic doubt is {recalibration_result.global_epistemic_doubt_score:.3f}."
        )

        return AuditDebateTranscript(
            transcript_id=transcript_token,
            session_id=session_id,
            analysis_id=analysis_id,
            patient_id=patient_id,
            participating_agents=participating_agents,
            original_claims=original_claims,
            evidence_references=all_evidence_refs,
            contradiction_records=contradiction_records,
            debate_rounds_executed=debate_transcript.total_rounds_executed,
            challenges=challenges,
            rebuttals=rebuttals,
            revisions=revisions,
            concessions=concessions,
            unsupported_findings=unsupported_findings,
            recalibrated_claim_support_scores=recalibrated_scores,
            epistemic_doubt_values=epistemic_doubts,
            claim_resolutions=claim_resolutions,
            overall_outcome=overall_outcome,
            clinical_safety_warnings=safety_warnings,
            unresolved_issues=unresolved_issues,
            final_resolution_rationale=rationale,
            transcript_version=self.VERSION,
            is_immutable=True,
        )


# Backward-compatible alias
ConsensusResolutionEngine = ConsensusResolver
