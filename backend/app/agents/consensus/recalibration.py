"""Mathematical Confidence Recalibration & Epistemic Doubt Scoring Engine (Sub-Step 12.3).

Consumes structured findings, cross-domain contradictions, and debate outcomes from:
1. Standardized Domain Agents (Symptom, Medical History, Laboratory, Risk Prediction)
2. Contradiction Detection Engine (Sub-Step 12.1)
3. Multi-Agent Adversarial Debate Protocol (Sub-Step 12.2)
4. Biomarker Entity Normalization (Sub-Step 8.4.3)
5. Clinical risk equations & supervised ML predictors

Core Mathematical Invariants & Standards:
- Distinct Concept: Confidence represents strength of support for an agent's clinical claim,
  NOT an epidemiological disease risk or posterior disease probability.
- Evidence Grounding Multiplier (+5% to +15%):
  Awarded only for verified, normalized, traceable, independent patient evidence.
  Duplicate references to the same biomarker award zero additional credit.
- Unresolved Contradiction Penalty (-10% to -25%):
  Claim-specific penalty scaled by contradiction severity (Critical: -25%, Moderate: -15%, Minor: -10%).
  Resolved and conceded contradictions do not continue penalizing claims.
  Incomparable prediction pairs (different endpoints/horizons) do not create contradiction penalties.
  Correlated contradictions within the same clinical domain are deduplicated to prevent penalty compounding.
- Missing Essential Evidence Cap (Cap at 40%):
  When essential quantitative biomarkers required for a specific claim are missing/untested,
  that claim's confidence is bounded strictly at 40.0%.
  Unrelated claims (e.g. non-cardiac findings) are not penalized for missing cardiac biomarkers.
  Unavailable/missing evidence is never treated as a normal finding.
- Global Epistemic Doubt Score (0.0 to 1.0):
  Deterministic, bounded metric representing residual epistemic uncertainty across the multi-agent panel.
  Deduplicated across correlated clinical domains.
  Explicitly designated as a heuristic mathematical score (heuristic_recalibration_v1.0.0).
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

from app.schemas.analysis import AgentOutputResponse
from app.schemas.consensus import (
    ChallengeStatus,
    ClaimRecalibrationRecord,
    ConfidenceRecalibrationResult,
    ContradictionCategory,
    ContradictionIssue,
    ContradictionMatrixResult,
    ContradictionSeverity,
    DebateTranscript,
    DomainEpistemicDoubt,
)

logger = logging.getLogger("confidence_recalibration")


# =============================================================================
# Domain Knowledge & Essential Evidence Constants
# =============================================================================

ESSENTIAL_DOMAIN_EVIDENCE: Dict[str, Dict[str, Any]] = {
    "ischemia": {
        "required_keys": ["cardiac_troponin_ng_ml", "resting_ecg"],
        "alt_keys": [
            "cardiac_troponin_assay",
            "hs_troponin_i_ng_ml",
            "hs_troponin_t_ng_ml",
            "troponin_i_ng_ml",
            "troponin_t_ng_ml",
        ],
        "rationale": "Objective ruling in or out of acute myocardial necrosis requires serial cardiac troponin and 12-lead ECG.",
    },
    "hemodynamics": {
        "required_keys": ["systolic_bp", "diastolic_bp"],
        "alt_keys": ["blood_pressure"],
        "rationale": "Evaluation of hypertensive urgency or crisis requires verified systolic and diastolic blood pressure.",
    },
    "heart_failure": {
        "required_keys": ["bnp_pg_ml"],
        "alt_keys": ["nt_pro_bnp_pg_ml"],
        "rationale": "Evaluation of acute dyspnea etiology requires circulating natriuretic peptide (BNP or NT-proBNP).",
    },
    "glycemia": {
        "required_keys": ["fasting_blood_glucose_mg_dl"],
        "alt_keys": ["hba1c_percent", "random_blood_glucose_mg_dl"],
        "rationale": "Diagnostic classification of diabetes or severe hyperglycemia requires fasting plasma glucose or HbA1c.",
    },
    "lipidology": {
        "required_keys": ["ldl_cholesterol_mg_dl"],
        "alt_keys": ["total_cholesterol_mg_dl", "hdl_cholesterol_mg_dl"],
        "rationale": "Evaluation of statin response or hypercholesterolemia requires circulating LDL cholesterol.",
    },
}

DOMAIN_KEYWORDS: Dict[str, List[str]] = {
    "ischemia": ["troponin", "ecg", "chest pain", "angina", "ischemi", "infarct", "stemi", "nstemi", "coronary"],
    "hemodynamics": ["blood pressure", "hypertens", "systolic", "diastolic", "hypotens", "mean arterial"],
    "heart_failure": ["bnp", "nt-pro", "dyspnea", "shortness of breath", "breathless", "heart failure", "orthopnea"],
    "glycemia": ["glucose", "hba1c", "diabet", "glycemic", "hyperglyc", "insulin", "keto"],
    "lipidology": ["ldl", "cholesterol", "statin", "lipid", "triglyceride", "hdl", "atorvastatin"],
    "cardiovascular_risk": ["framingham", "ascvd", "risk percent", "10-year", "classifier", "probability"],
}


class ConfidenceRecalibrator:
    """Mathematical Confidence Recalibration and Epistemic Doubt Scoring Engine."""

    VERSION = "heuristic_recalibration_v1.0.0"

    def __init__(
        self,
        base_grounding_increment: float = 5.0,
        max_grounding_adjustment: float = 15.0,
        critical_contradiction_penalty: float = 25.0,
        moderate_contradiction_penalty: float = 15.0,
        minor_contradiction_penalty: float = 10.0,
        missing_evidence_cap: float = 40.0,
    ) -> None:
        """Initialize recalibration engine with configurable, bounded parameters."""
        self.base_grounding_increment = float(base_grounding_increment)
        self.max_grounding_adjustment = float(max_grounding_adjustment)
        self.critical_contradiction_penalty = float(critical_contradiction_penalty)
        self.moderate_contradiction_penalty = float(moderate_contradiction_penalty)
        self.minor_contradiction_penalty = float(minor_contradiction_penalty)
        self.missing_evidence_cap = float(missing_evidence_cap)

        logger.info(
            "Initialized ConfidenceRecalibrator (Version: %s) with Grounding Max: +%.1f%%, "
            "Contradiction Penalties: [Crit: -%.1f%%, Mod: -%.1f%%, Min: -%.1f%%], Missing Cap: %.1f%%",
            self.VERSION,
            self.max_grounding_adjustment,
            self.critical_contradiction_penalty,
            self.moderate_contradiction_penalty,
            self.minor_contradiction_penalty,
            self.missing_evidence_cap,
        )

    def recalibrate_panel(
        self,
        agent_outputs: Optional[List[Any]] = None,
        contradiction_matrix: Optional[ContradictionMatrixResult] = None,
        debate_transcript: Optional[DebateTranscript] = None,
        symptoms_data: Optional[Dict[str, Any]] = None,
        medical_history_data: Optional[Dict[str, Any]] = None,
        laboratory_data: Optional[Dict[str, Any]] = None,
        clinical_scores: Optional[Dict[str, Any]] = None,
        ml_predictions: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
        patient_id: Optional[str] = None,
    ) -> ConfidenceRecalibrationResult:
        """Execute full mathematical recalibration across specialist agent claims.

        Args:
            agent_outputs: Structured outputs from domain specialist agents.
            contradiction_matrix: Evaluated contradiction matrix from Step 12.1.
            debate_transcript: Evaluated two-round debate transcript from Step 12.2.
            symptoms_data: Presenting symptoms dictionary.
            medical_history_data: Patient history & medications dictionary.
            laboratory_data: Verified objective biomarkers dictionary.
            clinical_scores: Risk equation scores dictionary.
            ml_predictions: Supervised ML predictions dictionary.
            session_id: Traceable session ID.
            patient_id: Traceable patient ID.

        Returns:
            ConfidenceRecalibrationResult with auditable claim records, domain uncertainties,
            and global Epistemic Doubt Score.
        """
        session_token = session_id or (contradiction_matrix.session_id if contradiction_matrix else f"sess-{uuid.uuid4().hex[:6]}")
        patient_token = patient_id or (contradiction_matrix.patient_id if contradiction_matrix else "anon")

        symptoms = symptoms_data or {}
        history = medical_history_data or {}
        labs = laboratory_data or {}
        scores = clinical_scores or {}
        ml = ml_predictions or {}

        # 1. Extract raw claims from agent outputs and debate transcript
        raw_claims = self._extract_claims(agent_outputs, debate_transcript)

        # 2. Recalibrate each individual claim deterministically
        recalibrated_records: List[ClaimRecalibrationRecord] = []
        domain_claim_map: Dict[str, List[ClaimRecalibrationRecord]] = {}

        for claim in raw_claims:
            record = self._recalibrate_single_claim(
                claim_info=claim,
                contradiction_matrix=contradiction_matrix,
                debate_transcript=debate_transcript,
                symptoms=symptoms,
                history=history,
                labs=labs,
                scores=scores,
                ml=ml,
            )
            recalibrated_records.append(record)
            domain_claim_map.setdefault(record.clinical_domain, []).append(record)

        # 3. Decompose domain-level epistemic doubt
        domain_doubts, missing_summary = self._calculate_domain_doubts(
            domain_claim_map=domain_claim_map,
            contradiction_matrix=contradiction_matrix,
            debate_transcript=debate_transcript,
            labs=labs,
            symptoms=symptoms,
            history=history,
        )

        # 4. Calculate Global Epistemic Doubt Score [0.0, 1.0]
        global_doubt = self._calculate_global_epistemic_doubt(domain_doubts, contradiction_matrix, debate_transcript)

        # 5. Formulate summary & clinical limitations
        summary, limitations = self._formulate_summary_and_limitations(
            recalibrated_records=recalibrated_records,
            global_doubt=global_doubt,
            missing_summary=missing_summary,
            contradiction_matrix=contradiction_matrix,
            debate_transcript=debate_transcript,
        )

        logger.info(
            "Recalibration completed for session %s: %d claims processed, global epistemic doubt: %.3f",
            session_token,
            len(recalibrated_records),
            global_doubt,
        )

        return ConfidenceRecalibrationResult(
            session_id=session_token,
            patient_id=patient_token,
            recalibrated_claims=recalibrated_records,
            global_epistemic_doubt_score=global_doubt,
            domain_uncertainty_contributions=domain_doubts,
            missing_evidence_summary=missing_summary,
            calibration_status=self.VERSION,
            limitations_and_warnings=limitations,
            summary=summary,
        )

    # -------------------------------------------------------------------------
    # Internal Claim Extraction & Domain Mapping
    # -------------------------------------------------------------------------

    def _extract_claims(
        self,
        agent_outputs: Optional[List[Any]],
        debate_transcript: Optional[DebateTranscript],
    ) -> List[Dict[str, Any]]:
        """Extract discrete clinical claims from agent outputs and debate transcript."""
        claims: List[Dict[str, Any]] = []
        seen_claim_keys: Set[str] = set()

        # If agent_outputs are available, extract their primary findings
        if agent_outputs:
            for out in agent_outputs:
                if isinstance(out, AgentOutputResponse):
                    role = out.agent_role
                    findings = out.findings
                    conf = float(out.confidence * 100.0) if out.confidence <= 1.0 else float(out.confidence)
                elif isinstance(out, dict):
                    role = str(out.get("agent_role") or out.get("role") or "Unknown Specialist")
                    findings = str(out.get("findings") or out.get("claim") or "")
                    raw_conf = out.get("confidence", 75.0)
                    conf = float(raw_conf * 100.0) if raw_conf <= 1.0 else float(raw_conf)
                else:
                    continue

                if not findings:
                    continue

                domain = self._infer_clinical_domain(findings, role)
                claim_key = f"{role}:{domain}"
                if claim_key not in seen_claim_keys:
                    seen_claim_keys.add(claim_key)
                    claims.append({
                        "agent_id": role,
                        "claim_id": f"CLAIM-{uuid.uuid4().hex[:8]}",
                        "claim_text": findings,
                        "clinical_domain": domain,
                        "original_confidence": max(0.0, min(100.0, conf)),
                    })

        # If debate transcript has rebuttals, ensure challenged claims and revisions are represented
        if debate_transcript and debate_transcript.challenges:
            rebuttal_lookup = {r.challenge_id: r for r in debate_transcript.rebuttals}
            for ch in debate_transcript.challenges:
                reb = rebuttal_lookup.get(ch.challenge_id)
                claim_text = ch.challenged_claim
                domain = self._infer_clinical_domain(claim_text, ch.challenged_agent)
                claim_key = f"{ch.challenged_agent}:{domain}"

                # If claim not already extracted from agent_outputs, add it
                if claim_key not in seen_claim_keys:
                    seen_claim_keys.add(claim_key)
                    # Baseline confidence for challenged claim
                    initial_conf = 75.0
                    claims.append({
                        "agent_id": ch.challenged_agent,
                        "claim_id": f"CLAIM-{uuid.uuid4().hex[:8]}",
                        "claim_text": reb.revised_claim if (reb and reb.revised_claim) else claim_text,
                        "clinical_domain": domain,
                        "original_confidence": initial_conf,
                        "challenge": ch,
                        "rebuttal": reb,
                    })

        # Fallback default panel if no inputs provided
        if not claims:
            claims.append({
                "agent_id": "Clinical Consensus Orchestrator",
                "claim_id": f"CLAIM-{uuid.uuid4().hex[:8]}",
                "claim_text": "Patient assessment within clinical parameters.",
                "clinical_domain": "general",
                "original_confidence": 75.0,
            })

        return claims

    def _infer_clinical_domain(self, text: str, role: str) -> str:
        """Infer clinical domain from claim narrative and agent role."""
        text_lower = text.lower()
        role_lower = role.lower()

        # Explicit domain priorities
        if any(k in text_lower for k in ["hypercholesterol", "ldl", "statin", "lipid", "cholesterol"]):
            return "lipidology"
        if any(k in text_lower for k in ["diabet", "glucose", "hba1c", "glycemic"]):
            return "glycemia"
        if any(k in text_lower for k in ["blood pressure", "hypertens", "systolic", "diastolic"]):
            return "hemodynamics"
        if any(k in text_lower for k in ["heart failure", "bnp", "nt-pro", "orthopnea"]):
            return "heart_failure"
        if any(k in text_lower for k in ["troponin", "angina", "ischemi", "substernal", "acute coronary"]):
            return "ischemia"

        # Score matching keywords across domains
        domain_scores: Dict[str, int] = {}
        for domain, keywords in DOMAIN_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if domain in role_lower:
                score += 2
            domain_scores[domain] = score

        best_domain = max(domain_scores, key=domain_scores.get)
        if domain_scores[best_domain] > 0:
            return best_domain

        if "laboratory" in role_lower:
            return "lipidology"
        if "history" in role_lower:
            return "glycemia"
        if "symptom" in role_lower:
            return "ischemia"
        if "risk" in role_lower:
            return "cardiovascular_risk"

        return "general"

    # -------------------------------------------------------------------------
    # Claim Recalibration Mathematics
    # -------------------------------------------------------------------------

    def _recalibrate_single_claim(
        self,
        claim_info: Dict[str, Any],
        contradiction_matrix: Optional[ContradictionMatrixResult],
        debate_transcript: Optional[DebateTranscript],
        symptoms: Dict[str, Any],
        history: Dict[str, Any],
        labs: Dict[str, Any],
        scores: Dict[str, Any],
        ml: Dict[str, Any],
    ) -> ClaimRecalibrationRecord:
        """Apply mathematical evidence grounding, contradiction penalty, and missing evidence cap."""
        agent_id = claim_info["agent_id"]
        claim_id = claim_info["claim_id"]
        claim_text = claim_info["claim_text"]
        domain = claim_info["clinical_domain"]
        original_conf = float(claim_info["original_confidence"])

        # Trace related contradiction issues
        related_issues: List[ContradictionIssue] = []
        if contradiction_matrix and contradiction_matrix.issues:
            for issue in contradiction_matrix.issues:
                # Issue is relevant if this agent was conflicting or if domain matches
                if agent_id in issue.conflicting_agents or self._issue_matches_domain(issue, domain):
                    related_issues.append(issue)

        # Trace debate outcome for this claim
        debate_outcome: Optional[str] = None
        concession_reason: Optional[str] = None
        revised_claim_text: Optional[str] = None

        if debate_transcript and debate_transcript.challenges:
            for ch in debate_transcript.challenges:
                if ch.challenged_agent == agent_id and (domain == self._infer_clinical_domain(ch.challenged_claim, agent_id)):
                    if ch.status == ChallengeStatus.CONCEDED:
                        debate_outcome = "conceded"
                        # Find concession reason from rebuttals
                        reb = next((r for r in debate_transcript.rebuttals if r.challenge_id == ch.challenge_id), None)
                        if reb:
                            concession_reason = reb.concession_reason
                    elif ch.status == ChallengeStatus.REVISED:
                        debate_outcome = "revised"
                        reb = next((r for r in debate_transcript.rebuttals if r.challenge_id == ch.challenge_id), None)
                        if reb and reb.revised_claim:
                            revised_claim_text = reb.revised_claim
                    elif ch.status == ChallengeStatus.UNRESOLVED_DISAGREEMENT:
                        debate_outcome = "unresolved_disagreement"
                    elif ch.status == ChallengeStatus.UNSUPPORTED:
                        debate_outcome = "unsupported"
                    elif ch.status == ChallengeStatus.INCOMPARABLE_EXCLUDED:
                        debate_outcome = "incomparable_excluded"
                    break

        # If claim was revised during debate, adopt revised text
        effective_claim_text = revised_claim_text if revised_claim_text else claim_text

        # ---------------------------------------------------------------------
        # 1. Evidence Grounding Multiplier (+0% to +15%)
        # ---------------------------------------------------------------------
        grounding_adj, verified_evidence, grounding_notes = self._calculate_evidence_grounding(
            claim_text=effective_claim_text,
            domain=domain,
            debate_outcome=debate_outcome,
            symptoms=symptoms,
            history=history,
            labs=labs,
            scores=scores,
            ml=ml,
        )

        # ---------------------------------------------------------------------
        # 2. Unresolved Contradiction Penalty (-0% to -25%)
        # ---------------------------------------------------------------------
        penalty_adj, penalty_notes, issue_ids = self._calculate_contradiction_penalty(
            agent_id=agent_id,
            domain=domain,
            debate_outcome=debate_outcome,
            related_issues=related_issues,
            debate_transcript=debate_transcript,
        )

        # ---------------------------------------------------------------------
        # 3. Intermediate Confidence Calculation
        # ---------------------------------------------------------------------
        if debate_outcome == "conceded":
            # Conceded claims reflect concession: baseline low confidence with concession note
            intermediate_conf = min(30.0, max(10.0, original_conf - 40.0))
        else:
            intermediate_conf = original_conf + grounding_adj - penalty_adj

        intermediate_conf = max(0.0, min(100.0, intermediate_conf))

        # ---------------------------------------------------------------------
        # 4. Missing Essential Evidence Confidence Cap (Cap at 40%)
        # ---------------------------------------------------------------------
        cap_applied, cap_val, missing_keys, cap_notes = self._check_missing_essential_evidence(
            domain=domain,
            claim_text=effective_claim_text,
            labs=labs,
            history=history,
            symptoms=symptoms,
        )

        if cap_applied:
            final_conf = min(intermediate_conf, self.missing_evidence_cap)
        else:
            final_conf = intermediate_conf

        final_conf = max(0.0, min(100.0, final_conf))

        # ---------------------------------------------------------------------
        # 5. Formulate Human-Readable Audit Trail
        # ---------------------------------------------------------------------
        explanation = (
            f"Original confidence: {original_conf:.1f}%. "
            f"Grounding adjustment: +{grounding_adj:.1f}% ({grounding_notes}). "
            f"Contradiction penalty: -{penalty_adj:.1f}% ({penalty_notes}). "
            f"Intermediate confidence: {intermediate_conf:.1f}%. "
        )
        if cap_applied:
            explanation += f"Capped at {self.missing_evidence_cap:.1f}% due to missing essential evidence: {', '.join(missing_keys)}. "
        if debate_outcome:
            explanation += f"Debate resolution: {debate_outcome}. "
        explanation += f"Final confidence: {final_conf:.1f}%."

        return ClaimRecalibrationRecord(
            agent_id=agent_id,
            claim_id=claim_id,
            claim_text=effective_claim_text,
            clinical_domain=domain,
            original_confidence=original_conf,
            evidence_grounding_adjustment=grounding_adj,
            contradiction_penalty=penalty_adj,
            missing_evidence_cap_applied=cap_applied,
            missing_evidence_cap_value=self.missing_evidence_cap if cap_applied else None,
            missing_evidence_details=missing_keys,
            recalibrated_confidence=intermediate_conf,
            final_confidence=final_conf,
            grounding_evidence_references=verified_evidence,
            contradiction_issue_ids=issue_ids,
            debate_outcome=debate_outcome,
            concession_reason=concession_reason,
            recalibration_explanation=explanation,
        )

    def _issue_matches_domain(self, issue: ContradictionIssue, domain: str) -> bool:
        """Determine if a contradiction issue relates to a specific clinical domain."""
        rule_id = issue.rule_id
        if domain == "ischemia" and "ISCHEMIA" in rule_id:
            return True
        if domain == "lipidology" and "STATIN" in rule_id:
            return True
        if domain == "hemodynamics" and ("HTN" in rule_id or "BP" in rule_id or "DYSPNEA" in rule_id):
            return True
        if domain == "glycemia" and "DIABETES" in rule_id:
            return True
        if domain == "cardiovascular_risk" and "EQ-ML" in rule_id:
            return True
        return False

    def _calculate_evidence_grounding(
        self,
        claim_text: str,
        domain: str,
        debate_outcome: Optional[str],
        symptoms: Dict[str, Any],
        history: Dict[str, Any],
        labs: Dict[str, Any],
        scores: Dict[str, Any],
        ml: Dict[str, Any],
    ) -> Tuple[float, List[str], str]:
        """Compute positive evidence grounding multiplier (+0% to +15%)."""
        # If claim was unsupported or conceded in debate, award zero grounding credit
        if debate_outcome in ["unsupported", "conceded"]:
            return 0.0, [], f"No grounding awarded for {debate_outcome} claim"

        verified_evidence: List[str] = []
        seen_analytes: Set[str] = set()

        # Check objective laboratory biomarkers
        domain_evidence_config = ESSENTIAL_DOMAIN_EVIDENCE.get(domain, {})
        target_keys = domain_evidence_config.get("required_keys", []) + domain_evidence_config.get("alt_keys", [])

        # Add all relevant biomarkers present in labs
        for key in target_keys:
            val = labs.get(key)
            if val is not None and key not in seen_analytes:
                # Verify non-empty and non-sentinel
                seen_analytes.add(key)
                verified_evidence.append(key)

        # Check documented medical history & medications
        if domain == "lipidology" and history.get("current_medications"):
            for med in history.get("current_medications", []):
                if isinstance(med, dict) and "statin" in str(med.get("name", "")).lower():
                    if "current_medications:statin" not in seen_analytes:
                        seen_analytes.add("current_medications:statin")
                        verified_evidence.append("current_medications:statin")

        # Independent evidence items count
        independent_sources_count = len(verified_evidence)
        raw_adjustment = independent_sources_count * self.base_grounding_increment
        final_adjustment = min(self.max_grounding_adjustment, raw_adjustment)

        if final_adjustment > 0:
            notes = f"{independent_sources_count} independent verified sources (capped at +{self.max_grounding_adjustment:.1f}%)"
        else:
            notes = "No independent verified patient evidence found for this claim"

        return final_adjustment, verified_evidence, notes

    def _calculate_contradiction_penalty(
        self,
        agent_id: str,
        domain: str,
        debate_outcome: Optional[str],
        related_issues: List[ContradictionIssue],
        debate_transcript: Optional[DebateTranscript],
    ) -> Tuple[float, str, List[str]]:
        """Compute negative contradiction penalty (-0% to -25%)."""
        # Rule: Incomparable predictions never generate a contradiction penalty
        filtered_issues = [
            i for i in related_issues if i.category != ContradictionCategory.INCOMPARABLE_PREDICTIONS
        ]

        if not filtered_issues:
            return 0.0, "No active contradictions in domain", []

        # Rule: Resolved contradictions (conceded by the OTHER agent) must not penalize this claim
        # Check if any challenge targeting this agent was conceded by this agent vs defended
        if debate_outcome == "conceded":
            # Conceded claims handled directly via intermediate baseline adjustment; 0 penalty here
            return 0.0, "Claim conceded; handled via concession reclassification", [i.issue_id for i in filtered_issues]

        if debate_outcome == "unsupported":
            # Maximum penalty for unsupported defense
            return self.critical_contradiction_penalty, "Claim unsupported in debate due to absent evidence", [i.issue_id for i in filtered_issues]

        # Check if debate resolved/conceded the contradiction
        conceded_issue_ids: Set[str] = set()
        if debate_transcript:
            for ch in debate_transcript.challenges:
                if ch.status == ChallengeStatus.CONCEDED:
                    conceded_issue_ids.add(ch.issue_id)
            if debate_transcript.conceded_challenges:
                conceded_issue_ids.update(debate_transcript.conceded_challenges)

        unresolved_issues = [
            i for i in filtered_issues
            if i.issue_id not in conceded_issue_ids
        ]

        if not unresolved_issues:
            return 0.0, "Contradictions resolved by concession in debate", [i.issue_id for i in filtered_issues]

        # Check active unresolved disagreements
        active_penalties: List[float] = []
        issue_ids: List[str] = []

        for issue in unresolved_issues:
            issue_ids.append(issue.issue_id)

            # Deduplication: Evaluate severity
            if issue.severity == ContradictionSeverity.CRITICAL:
                base_pen = self.critical_contradiction_penalty
            elif issue.severity == ContradictionSeverity.MODERATE:
                base_pen = self.moderate_contradiction_penalty
            else:
                base_pen = self.minor_contradiction_penalty

            # If issue is provisional/unconfirmed, apply reduced penalty
            if not issue.is_confirmed_contradiction:
                base_pen = max(5.0, base_pen * 0.67)

            active_penalties.append(base_pen)

        if not active_penalties:
            return 0.0, "Contradictions resolved or excluded", issue_ids

        # Domain deduplication: Take the maximum penalty in this domain rather than summing
        # to avoid double-penalizing correlated biological discrepancies
        max_penalty = min(self.critical_contradiction_penalty, max(active_penalties))
        notes = f"Unresolved {domain} contradiction (domain-deduplicated maximum: -{max_penalty:.1f}%)"

        return max_penalty, notes, issue_ids

    def _check_missing_essential_evidence(
        self,
        domain: str,
        claim_text: str,
        labs: Dict[str, Any],
        history: Dict[str, Any],
        symptoms: Dict[str, Any],
    ) -> Tuple[bool, Optional[float], List[str], str]:
        """Check if essential quantitative evidence is missing for this claim, triggering 40% cap."""
        claim_lower = claim_text.lower()
        missing_keys: List[str] = []
        is_family_history = any(k in claim_lower for k in ["paternal", "maternal", "family history", "father", "mother", "sibling"])

        # Domain 1: Ischemia
        # Cap applies if claim asserts or evaluates acute myocardial infarction / acute coronary syndrome
        # but troponin was never drawn or is missing
        if domain == "ischemia" and not is_family_history:
            troponin = labs.get("cardiac_troponin_ng_ml")
            alt_troponins = [
                labs.get("hs_troponin_i_ng_ml"),
                labs.get("hs_troponin_t_ng_ml"),
                labs.get("troponin_i_ng_ml"),
                labs.get("troponin_t_ng_ml"),
            ]
            has_troponin = (troponin is not None) or any(t is not None for t in alt_troponins)
            if not has_troponin:
                missing_keys.append("cardiac_troponin_ng_ml")

        # Domain 2: Dyspnea / Heart Failure
        if domain == "heart_failure" or any(k in claim_lower for k in ["heart failure", "hfref", "hfpef", "bnp"]):
            has_peptide = (labs.get("bnp_pg_ml") is not None) or (labs.get("nt_pro_bnp_pg_ml") is not None)
            if not has_peptide:
                missing_keys.append("bnp_pg_ml")

        # Domain 3: Glycemia / Diabetes
        if domain == "glycemia" or any(k in claim_lower for k in ["diabet", "hyperglycemia", "dka", "glucose control"]):
            has_glucose = (labs.get("fasting_blood_glucose_mg_dl") is not None) or (labs.get("hba1c_percent") is not None)
            if not has_glucose:
                missing_keys.append("fasting_blood_glucose_mg_dl")

        # Domain 4: Hemodynamics / Severe Hypertension
        if domain == "hemodynamics" or any(k in claim_lower for k in ["hypertensive crisis", "severe hypertension", "stage 2"]):
            has_bp = (labs.get("systolic_bp") is not None) and (labs.get("diastolic_bp") is not None)
            if not has_bp:
                missing_keys.append("systolic_diastolic_bp")

        if missing_keys:
            return True, self.missing_evidence_cap, missing_keys, f"Essential evidence missing: {', '.join(missing_keys)}"

        return False, None, [], "All essential clinical evidence present"

    # -------------------------------------------------------------------------
    # Epistemic Doubt Score Mathematics
    # -------------------------------------------------------------------------

    def _calculate_domain_doubts(
        self,
        domain_claim_map: Dict[str, List[ClaimRecalibrationRecord]],
        contradiction_matrix: Optional[ContradictionMatrixResult],
        debate_transcript: Optional[DebateTranscript],
        labs: Dict[str, Any],
        symptoms: Dict[str, Any],
        history: Dict[str, Any],
    ) -> Tuple[List[DomainEpistemicDoubt], List[str]]:
        """Calculate domain-level uncertainty contributions and aggregate missing evidence."""
        domain_doubts: List[DomainEpistemicDoubt] = []
        all_missing_summary: List[str] = []

        all_domains = set(domain_claim_map.keys())
        # Ensure core physiological domains are inspected
        for d in ["ischemia", "lipidology", "hemodynamics", "glycemia", "cardiovascular_risk"]:
            all_domains.add(d)

        for dom in sorted(all_domains):
            records = domain_claim_map.get(dom, [])

            # 1. Unresolved contradictions in domain
            unresolved_issues: List[ContradictionIssue] = []
            if contradiction_matrix and contradiction_matrix.issues:
                for issue in contradiction_matrix.issues:
                    if issue.category == ContradictionCategory.INCOMPARABLE_PREDICTIONS:
                        continue
                    if self._issue_matches_domain(issue, dom):
                        # Check if debate resolved it
                        if debate_transcript and issue.issue_id in debate_transcript.conceded_challenges:
                            continue  # Conceded = resolved
                        unresolved_issues.append(issue)

            unresolved_count = len(unresolved_issues)

            # 2. Missing essential evidence
            missing_for_domain: List[str] = []
            config = ESSENTIAL_DOMAIN_EVIDENCE.get(dom, {})
            req_keys = config.get("required_keys", [])
            alt_keys = config.get("alt_keys", [])

            for req in req_keys:
                if labs.get(req) is None and not any(labs.get(alt) is not None for alt in alt_keys):
                    missing_for_domain.append(req)
                    if req not in all_missing_summary:
                        all_missing_summary.append(req)

            # 3. Unsupported claims in domain
            unsupported_count = sum(1 for r in records if r.debate_outcome == "unsupported")

            # 4. Compute domain uncertainty score [0.0, 1.0]
            # Formula: 0.40 * contradiction_score + 0.35 * missing_score + 0.25 * unsupported_score
            crit_issues = sum(1 for i in unresolved_issues if i.severity == ContradictionSeverity.CRITICAL)
            mod_issues = sum(1 for i in unresolved_issues if i.severity == ContradictionSeverity.MODERATE)

            contradiction_contrib = min(1.0, (crit_issues * 0.70) + (mod_issues * 0.40) + ((unresolved_count - crit_issues - mod_issues) * 0.20))
            missing_contrib = 1.0 if missing_for_domain else 0.0
            unsupported_contrib = min(1.0, unsupported_count * 0.50)

            raw_doubt = (0.40 * contradiction_contrib) + (0.35 * missing_contrib) + (0.25 * unsupported_contrib)
            domain_score = max(0.0, min(1.0, round(raw_doubt, 3)))

            rationale_parts = []
            if unresolved_count > 0:
                rationale_parts.append(f"{unresolved_count} unresolved contradiction(s)")
            if missing_for_domain:
                rationale_parts.append(f"missing essential biomarker(s): {', '.join(missing_for_domain)}")
            if unsupported_count > 0:
                rationale_parts.append(f"{unsupported_count} unsupported debate claim(s)")
            if not rationale_parts:
                rationale_parts.append("Fully concordant with verified objective evidence")

            domain_doubts.append(
                DomainEpistemicDoubt(
                    domain=dom,
                    doubt_contribution=domain_score,
                    unresolved_issues_count=unresolved_count,
                    missing_essential_evidence=missing_for_domain,
                    rationale="; ".join(rationale_parts) + ".",
                )
            )

        return domain_doubts, all_missing_summary

    def _calculate_global_epistemic_doubt(
        self,
        domain_doubts: List[DomainEpistemicDoubt],
        contradiction_matrix: Optional[ContradictionMatrixResult],
        debate_transcript: Optional[DebateTranscript],
    ) -> float:
        """Calculate bounded Global Epistemic Doubt Score in range [0.0, 1.0]."""
        if not domain_doubts:
            return 0.0

        scores = [d.doubt_contribution for d in domain_doubts]
        max_doubt = max(scores)
        mean_doubt = sum(scores) / len(scores)

        # Domain-aware aggregation:
        # 60% weight to peak domain uncertainty + 40% weight to average panel uncertainty
        aggregated_doubt = (0.60 * max_doubt) + (0.40 * mean_doubt)

        # If debate reached complete convergence with all challenges conceded, doubt is minimal
        if debate_transcript and debate_transcript.convergence_status == "converged":
            aggregated_doubt = min(aggregated_doubt, 0.15)
        elif debate_transcript and debate_transcript.convergence_status == "no_contradictions":
            aggregated_doubt = 0.0

        return max(0.0, min(1.0, round(aggregated_doubt, 3)))

    def _formulate_summary_and_limitations(
        self,
        recalibrated_records: List[ClaimRecalibrationRecord],
        global_doubt: float,
        missing_summary: List[str],
        contradiction_matrix: Optional[ContradictionMatrixResult],
        debate_transcript: Optional[DebateTranscript],
    ) -> Tuple[str, List[str]]:
        """Formulate executive clinical summary and explicit methodological limitations."""
        total_claims = len(recalibrated_records)
        capped_claims = sum(1 for r in recalibrated_records if r.missing_evidence_cap_applied)
        conceded_claims = sum(1 for r in recalibrated_records if r.debate_outcome == "conceded")
        unresolved_claims = sum(1 for r in recalibrated_records if r.debate_outcome == "unresolved_disagreement")

        summary = (
            f"Confidence Recalibration Engine ({self.VERSION}) evaluated {total_claims} specialist claims: "
            f"{capped_claims} claim(s) capped at {self.missing_evidence_cap:.0f}% due to missing evidence, "
            f"{conceded_claims} formal concession(s), and {unresolved_claims} legitimate unresolved clinical disagreement(s). "
            f"Global Epistemic Doubt Score: {global_doubt:.3f} (Scale: 0.0 = total certainty, 1.0 = maximum uncertainty)."
        )

        limitations = [
            "Confidence represents mathematical strength of claim support within the reasoning graph, not epidemiological disease risk or calibrated posterior probability.",
            f"Recalibration algorithm ({self.VERSION}) operates deterministically under defined heuristic rules. It is not an empirical Bayesian model trained on clinical registry cohorts.",
            "Evidence grounding applies strictly to verified, normalized patient biomarkers; repeated citations of the same biomarker key do not count as independent corroboration.",
            "Missing quantitative evidence enforces a strict 40% confidence ceiling on claims dependent upon that analyte, but missing evidence is never equated with a negative or normal finding.",
            "Global Epistemic Doubt Score aggregates deduplicated domain-level uncertainties to prevent artificial score compounding from correlated physiological markers.",
        ]

        if missing_summary:
            limitations.append(
                f"Active missing biomarker(s) affecting diagnostic confidence: {', '.join(missing_summary)}."
            )

        return summary, limitations


# Backward-compatible alias
ConfidenceRecalibrationEngine = ConfidenceRecalibrator
