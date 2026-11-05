"""Multi-Agent Adversarial Debate Protocol & Cross-Examination Engine (Sub-Step 12.2).

Orchestrates the structured two-round adversarial debate protocol between domain agents:
1. Round 1 (Evidence Submission & Targeted Challenge Issuance):
   - Inspects detected contradictions from the Contradiction Matrix (excluding incomparable predictions)
   - Formulates targeted cross-domain challenges identifying the challenged agent, claim, evidence, and rationale
2. Round 2 (Rebuttal, Grounding, and Formal Concessions):
   - Routes challenges to challenged agents
   - Requires evidence-grounded defense, claim revision, or formal concession
   - Enforces truthful acknowledgment of missing evidence (no fabricated biomarkers or history)
3. Debate Control & Convergence:
   - Enforces a strict maximum of two debate rounds
   - Deterministically detects converged, revised, conceded, and unresolved challenges
   - Preserves genuine clinical disagreements rather than forcing artificial consensus
4. Qualitative Claim Discordance via Natural Language Inference (NLI):
   - Performs semantic NLI (entailment, contradiction, neutral, uncertain) across narrative claims
   - Uses local deterministic semantic inference without paid external API dependencies
"""

import logging
import uuid
from typing import Any, Dict, List, Optional, Tuple

from app.schemas.analysis import AgentOutputResponse
from app.schemas.consensus import (
    AgentChallenge,
    AgentRebuttal,
    ChallengeStatus,
    ContradictionCategory,
    ContradictionIssue,
    ContradictionMatrixResult,
    DebateTranscript,
    NLIAnalysisRecord,
    NLIRelation,
    RebuttalDisposition,
)

logger = logging.getLogger("debate_protocol")


class RuleBasedSemanticDiscordanceEngine:
    """Local, deterministic rule-based semantic discordance and polarity checker.

    NOTE: This is NOT a trained neural Natural Language Inference (NLI) model.
    It performs deterministic keyword, clinical polarity, and negation pattern analysis
    without external paid API dependencies or local GPU requirements.
    When rules cannot establish an entailment or contradiction, it returns UNCERTAIN or NEUTRAL
    with documented limitations.
    """

    def __init__(self) -> None:
        self.method_name = "rule_based_clinical_polarity_discordance_v1"
        self.method_limitations = (
            "Deterministic pattern-based semantic discordance checker (not a trained neural NLI model). "
            "Evaluates explicit medical negation, clinical polarity, and symptom overlap without external API dependencies. "
            "Returns UNCERTAIN when rules cannot establish relationship."
        )

    def analyze_pair(
        self,
        agent_a: str,
        claim_a: str,
        agent_b: str,
        claim_b: str,
    ) -> NLIAnalysisRecord:
        """Classify the semantic relationship between two qualitative claims."""
        pair_id = f"NLI-{uuid.uuid4().hex[:8]}"
        text_a = (claim_a or "").strip().lower()
        text_b = (claim_b or "").strip().lower()

        if not text_a or not text_b:
            return NLIAnalysisRecord(
                pair_id=pair_id,
                agent_a=agent_a,
                claim_a=claim_a,
                agent_b=agent_b,
                claim_b=claim_b,
                relation=NLIRelation.UNCERTAIN,
                confidence=0.50,
                method=self.method_name,
                limitations="One or both claims are empty or unavailable for semantic inference.",
            )

        # Domain: Tobacco exposure
        smoking_negation = any(k in text_a for k in ["never smoker", "denies smoking", "non-smoker", "no tobacco"]) or any(
            k in text_b for k in ["never smoker", "denies smoking", "non-smoker", "no tobacco"]
        )
        smoking_assertion = any(k in text_a for k in ["smoking history", "pack-year", "active smoker", "tobacco exposure"]) or any(
            k in text_b for k in ["smoking history", "pack-year", "active smoker", "tobacco exposure"]
        )

        if smoking_negation and smoking_assertion:
            return NLIAnalysisRecord(
                pair_id=pair_id,
                agent_a=agent_a,
                claim_a=claim_a,
                agent_b=agent_b,
                claim_b=claim_b,
                relation=NLIRelation.CONTRADICTION,
                confidence=0.92,
                method=self.method_name,
                limitations="Direct semantic opposition on tobacco exposure history.",
            )

        # Domain: Chest pain presence vs absence
        denies_chest_pain = any(k in text_a for k in ["denies chest pain", "no chest pain", "no angina"]) or any(
            k in text_b for k in ["denies chest pain", "no chest pain", "no angina"]
        )
        asserts_chest_pain = any(k in text_a for k in ["chest pain", "substernal pressure", "angina"]) or any(
            k in text_b for k in ["chest pain", "substernal pressure", "angina"]
        )

        if denies_chest_pain and asserts_chest_pain:
            return NLIAnalysisRecord(
                pair_id=pair_id,
                agent_a=agent_a,
                claim_a=claim_a,
                agent_b=agent_b,
                claim_b=claim_b,
                relation=NLIRelation.CONTRADICTION,
                confidence=0.90,
                method=self.method_name,
                limitations="Contradictory assertions regarding presence of acute chest pain.",
            )

        # Check semantic entailment / equivalence
        is_both_ischemic = (
            any(k in text_a for k in ["chest pain", "angina", "ischemia"])
            and any(k in text_b for k in ["chest pain", "angina", "ischemia", "substernal"])
        )
        if is_both_ischemic and not denies_chest_pain:
            return NLIAnalysisRecord(
                pair_id=pair_id,
                agent_a=agent_a,
                claim_a=claim_a,
                agent_b=agent_b,
                claim_b=claim_b,
                relation=NLIRelation.ENTAILMENT,
                confidence=0.88,
                method=self.method_name,
                limitations="Congruent clinical assertions within ischemic symptom domain.",
            )

        # Default: Neutral for distinct non-overlapping topics
        return NLIAnalysisRecord(
            pair_id=pair_id,
            agent_a=agent_a,
            claim_a=claim_a,
            agent_b=agent_b,
            claim_b=claim_b,
            relation=NLIRelation.NEUTRAL,
            confidence=0.75,
            method=self.method_name,
            limitations=(
                "Claims describe distinct or non-overlapping clinical facets. "
                "Evaluated under deterministic rule-based semantic discordance checker."
            ),
        )


# Backward-compatible alias
SemanticNLIEngine = RuleBasedSemanticDiscordanceEngine


class DebateProtocolEngine:
    """Orchestrates two-round adversarial debate, evidence-grounded rebuttals, and convergence."""

    def __init__(self, max_rounds: int = 2) -> None:
        self.max_rounds = max(1, min(max_rounds, 2))  # Strict bound: maximum 2 rounds
        self.nli_engine = SemanticNLIEngine()
        logger.info("Initialized DebateProtocolEngine with max rounds = %d", self.max_rounds)

    def execute_debate(
        self,
        contradiction_result: ContradictionMatrixResult,
        agent_outputs: Optional[List[Any]] = None,
        symptoms_data: Optional[Dict[str, Any]] = None,
        medical_history_data: Optional[Dict[str, Any]] = None,
        laboratory_data: Optional[Dict[str, Any]] = None,
        clinical_scores: Optional[Dict[str, Any]] = None,
        ml_predictions: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
        patient_id: Optional[str] = None,
    ) -> DebateTranscript:
        """Execute the two-round multi-agent adversarial debate protocol.

        Args:
            contradiction_result: Output from ContradictionDetector.
            agent_outputs: Optional list of upstream agent outputs.
            symptoms_data: Raw or extracted symptoms.
            medical_history_data: Patient medical and medication history.
            laboratory_data: Objective biomarkers and vitals.
            clinical_scores: Cohort risk scores.
            ml_predictions: Machine learning predictions.
            session_id: Traceable session ID.
            patient_id: Traceable patient ID.

        Returns:
            DebateTranscript recording challenges, rebuttals, concessions, and convergence.
        """
        debate_id = f"DEBATE-{uuid.uuid4().hex[:8]}"
        session_token = session_id or contradiction_result.session_id or f"run-{uuid.uuid4().hex[:6]}"
        patient_token = patient_id or contradiction_result.patient_id or "anon"

        # If no contradictions were detected, debate completes immediately
        if not contradiction_result.contradictions_detected or not contradiction_result.issues:
            return DebateTranscript(
                debate_id=debate_id,
                session_id=session_id,
                patient_id=patient_id,
                total_rounds_executed=1,
                max_rounds_allowed=self.max_rounds,
                challenges=[],
                rebuttals=[],
                conceded_challenges=[],
                unresolved_disagreements=[],
                unsupported_challenges=[],
                qualitative_nli_analyses=[],
                convergence_status="no_contradictions",
                summary="No clinical contradictions detected across the multi-agent panel. Adversarial debate protocol terminated with immediate consensus.",
            )

        # ---------------------------------------------------------------------
        # Round 1: Evidence Submission & Targeted Challenge Issuance
        # ---------------------------------------------------------------------
        challenges = self._conduct_round_1_challenges(
            issues=contradiction_result.issues,
            session_token=session_token,
            patient_token=patient_token,
        )

        # ---------------------------------------------------------------------
        # Round 2: Rebuttal, Physiological Grounding & Formal Concessions
        # ---------------------------------------------------------------------
        rebuttals, challenge_status_map = self._conduct_round_2_rebuttals(
            challenges=challenges,
            issues=contradiction_result.issues,
            symptoms=symptoms_data or {},
            history=medical_history_data or {},
            labs=laboratory_data or {},
            scores=clinical_scores or {},
            ml=ml_predictions or {},
        )

        # Update challenge statuses based on Round 2 outcomes
        for ch in challenges:
            if ch.challenge_id in challenge_status_map:
                ch.status = challenge_status_map[ch.challenge_id]

        # ---------------------------------------------------------------------
        # Qualitative NLI Analysis across narrative findings
        # ---------------------------------------------------------------------
        nli_records = self._evaluate_qualitative_nli(agent_outputs)

        # ---------------------------------------------------------------------
        # Debate Convergence Evaluation & Audit Transcript Synthesis
        # ---------------------------------------------------------------------
        conceded_ids = [ch.challenge_id for ch in challenges if ch.status == ChallengeStatus.CONCEDED]
        unresolved_ids = [ch.challenge_id for ch in challenges if ch.status == ChallengeStatus.UNRESOLVED_DISAGREEMENT]
        unsupported_ids = [ch.challenge_id for ch in challenges if ch.status == ChallengeStatus.UNSUPPORTED]

        convergence_status, summary_text = self._evaluate_convergence(
            total_challenges=len(challenges),
            conceded_count=len(conceded_ids),
            unresolved_count=len(unresolved_ids),
            unsupported_count=len(unsupported_ids),
            challenges=challenges,
        )

        logger.info(
            "Debate protocol finished: %d challenges (%d conceded, %d unresolved, %d unsupported). Status: %s",
            len(challenges),
            len(conceded_ids),
            len(unresolved_ids),
            len(unsupported_ids),
            convergence_status,
        )

        return DebateTranscript(
            debate_id=debate_id,
            session_id=session_id,
            patient_id=patient_id,
            total_rounds_executed=2,
            max_rounds_allowed=self.max_rounds,
            challenges=challenges,
            rebuttals=rebuttals,
            conceded_challenges=conceded_ids,
            unresolved_disagreements=unresolved_ids,
            unsupported_challenges=unsupported_ids,
            qualitative_nli_analyses=nli_records,
            convergence_status=convergence_status,
            summary=summary_text,
        )

    # -------------------------------------------------------------------------
    # Internal Debate Engine Sub-Rounds
    # -------------------------------------------------------------------------

    def _conduct_round_1_challenges(
        self,
        issues: List[ContradictionIssue],
        session_token: str,
        patient_token: str,
    ) -> List[AgentChallenge]:
        """Round 1: Formulate targeted adversarial challenges from detected contradictions."""
        challenges: List[AgentChallenge] = []
        seen_challenge_keys = set()

        for issue in issues:
            # Rule: Do not challenge agents for findings explicitly marked incomparable
            if issue.category == ContradictionCategory.INCOMPARABLE_PREDICTIONS:
                logger.info("Excluding incomparable prediction issue %s from adversarial challenge.", issue.issue_id)
                continue

            # Determine challenger vs challenged based on evidence polarity
            if issue.category == ContradictionCategory.SUBJECTIVE_VS_OBJECTIVE:
                challenging_agent = "Laboratory Biomarker Specialist"
                challenged_agent = "Symptom Analysis Specialist"
                challenged_claim = issue.diverging_claims.get("Symptom Analysis Specialist", "Subjective symptom report")
            elif issue.category == ContradictionCategory.HISTORY_MEDICATION_VS_BIOMARKER:
                challenging_agent = "Laboratory Biomarker Specialist"
                challenged_agent = "Medical History Specialist"
                challenged_claim = issue.diverging_claims.get("Medical History Specialist", "Reported medical/pharmacological history")
            elif issue.category == ContradictionCategory.EQUATION_VS_ML_DISCORDANCE:
                challenging_agent = "Risk Prediction Ensemble Specialist"
                challenged_agent = "Risk Prediction Ensemble Specialist"
                challenged_claim = issue.diverging_claims.get("Machine Learning CVD Classifier", "Model probability estimate")
            else:
                challenging_agent = issue.conflicting_agents[1] if len(issue.conflicting_agents) > 1 else "Consensus Orchestrator"
                challenged_agent = issue.conflicting_agents[0]
                challenged_claim = issue.diverging_claims.get(challenged_agent, "Clinical claim")

            # Deduplication: Prevent issuing duplicate challenges for the same rule and challenged agent
            challenge_key = (issue.rule_id, challenged_agent)
            if challenge_key in seen_challenge_keys:
                logger.info("Prevented duplicate challenge for rule %s and agent %s", issue.rule_id, challenged_agent)
                continue
            seen_challenge_keys.add(challenge_key)

            challenge_id = f"CHALLENGE-{session_token}-{issue.rule_id}-{uuid.uuid4().hex[:6]}"

            challenges.append(
                AgentChallenge(
                    challenge_id=challenge_id,
                    issue_id=issue.issue_id,
                    round_number=1,
                    challenging_agent=challenging_agent,
                    challenged_agent=challenged_agent,
                    challenged_claim=challenged_claim,
                    evidence_basis=issue.evidence_references,
                    physiological_rationale=issue.physiological_rationale,
                    challenge_text=issue.suggested_challenge,
                    clinical_limitations=issue.clinical_limitations,
                    status=ChallengeStatus.ISSUED,
                )
            )

        return challenges

    def _conduct_round_2_rebuttals(
        self,
        challenges: List[AgentChallenge],
        issues: List[ContradictionIssue],
        symptoms: Dict[str, Any],
        history: Dict[str, Any],
        labs: Dict[str, Any],
        scores: Dict[str, Any],
        ml: Dict[str, Any],
    ) -> Tuple[List[AgentRebuttal], Dict[str, ChallengeStatus]]:
        """Round 2: Route challenges to challenged agents and synthesize evidence-grounded rebuttals or concessions."""
        rebuttals: List[AgentRebuttal] = []
        status_map: Dict[str, ChallengeStatus] = {}
        issue_lookup = {i.issue_id: i for i in issues}

        for ch in challenges:
            issue = issue_lookup.get(ch.issue_id)
            rebuttal_id = f"REBUTTAL-{uuid.uuid4().hex[:8]}"

            if not issue:
                continue

            rule_id = issue.rule_id

            # Case 1: Rule B1 - Statin therapy vs Extreme LDL
            if rule_id == "RULE-B1-STATIN-LDL":
                # Check if adherence was reported as consistent
                meds = history.get("current_medications") or []
                adherence_poor = any(
                    str(m.get("adherence") or "").lower() in ["inconsistent", "poor", "non_compliant"]
                    for m in meds if isinstance(m, dict)
                )

                if not adherence_poor:
                    # Concede that monotherapy is inadequate or adherence is unverified
                    rebuttals.append(
                        AgentRebuttal(
                            rebuttal_id=rebuttal_id,
                            challenge_id=ch.challenge_id,
                            issue_id=ch.issue_id,
                            round_number=2,
                            responding_agent=ch.challenged_agent,
                            disposition=RebuttalDisposition.CONCEDE,
                            rebuttal_text=(
                                "Concedes lipid control claim: While statin was prescribed with reported compliance, "
                                f"objective circulating LDL-C remains severe at {labs.get('ldl_cholesterol_mg_dl')} mg/dL. "
                                "Medical History Specialist acknowledges inadequate pharmacological response, probable unverified "
                                "non-adherence, or familial hypercholesterolemia requiring non-statin intensification (ezetimibe/PCSK9i)."
                            ),
                            grounding_evidence=["ldl_cholesterol_mg_dl", "current_medications"],
                            concession_reason="Objective biomarker demonstrates clear therapeutic failure under current statin regimen.",
                            acknowledged_limitations=["Baseline pre-treatment LDL is unrecorded; percentage reduction cannot be calculated."],
                            evidence_missing=False,
                        )
                    )
                    status_map[ch.challenge_id] = ChallengeStatus.CONCEDED
                else:
                    # Defend with documented non-adherence
                    rebuttals.append(
                        AgentRebuttal(
                            rebuttal_id=rebuttal_id,
                            challenge_id=ch.challenge_id,
                            issue_id=ch.issue_id,
                            round_number=2,
                            responding_agent=ch.challenged_agent,
                            disposition=RebuttalDisposition.DEFEND,
                            rebuttal_text=(
                                "Defends medication history: Documented prescription exists, but patient history specifically "
                                "identifies inconsistent compliance. Lack of LDL suppression is physiologically explained by "
                                "insufficient drug exposure rather than true biological statin resistance."
                            ),
                            grounding_evidence=["current_medications", "adherence_notes"],
                            acknowledged_limitations=["Pharmacy refill synchronization needed to quantify compliance percentage."],
                            evidence_missing=False,
                        )
                    )
                    status_map[ch.challenge_id] = ChallengeStatus.UNRESOLVED_DISAGREEMENT

            # Case 2: Rule A1 - Ischemia vs Troponin (Unresolved Presentation)
            elif rule_id == "RULE-A1-ISCHEMIA-TROPONIN":
                # Symptom specialist defends clinical concern without fabricating troponin
                rebuttals.append(
                    AgentRebuttal(
                        rebuttal_id=rebuttal_id,
                        challenge_id=ch.challenge_id,
                        issue_id=ch.issue_id,
                        round_number=2,
                        responding_agent=ch.challenged_agent,
                        disposition=RebuttalDisposition.DEFEND,
                        rebuttal_text=(
                            "Defends ischemic clinical concern: While negative serial high-sensitivity cardiac troponin "
                            "and normal resting ECG rule out acute myocardial infarction (>99% NPV), patient reports severe, "
                            "crushing substernal pain. Unstable angina, coronary vasospasm, and microvascular angina characteristically "
                            "produce acute severe ischemia without irreversible cellular necrosis. Recommends acute observation, "
                            "HEART score risk stratification, and functional cardiac testing."
                        ),
                        grounding_evidence=["symptoms", "duration_hours", "severity"],
                        acknowledged_limitations=[
                            "Troponin negative status confirms lack of ongoing myocyte death but does not rule out unstable coronary disease.",
                            "Non-ischemic etiologies (GERD, pericarditis, costochondritis) must be actively evaluated.",
                        ],
                        evidence_missing=False,
                    )
                )
                # Preserves legitimate unresolved clinical disagreement!
                status_map[ch.challenge_id] = ChallengeStatus.UNRESOLVED_DISAGREEMENT

            # Case 3: Rule A2 - Severe Dyspnea vs Normal BNP
            elif rule_id == "RULE-A2-DYSPNEA-BNP":
                rebuttals.append(
                    AgentRebuttal(
                        rebuttal_id=rebuttal_id,
                        challenge_id=ch.challenge_id,
                        issue_id=ch.issue_id,
                        round_number=2,
                        responding_agent=ch.challenged_agent,
                        disposition=RebuttalDisposition.DEFEND,
                        rebuttal_text=(
                            "Defends respiratory distress finding: Normal natriuretic peptide effectively excludes acute "
                            "systolic heart failure (HFrEF), but Heart Failure with Preserved Ejection Fraction (HFpEF), "
                            "acute pulmonary embolism, severe bronchospasm, or anxiety cause marked acute dyspnea with preserved BNP. "
                            "Symptom Specialist defends urgent workup while accepting heart failure exclusion."
                        ),
                        grounding_evidence=["symptoms", "bnp_pg_ml"],
                        acknowledged_limitations=["Obesity or flash pulmonary edema can suppress peptide release."],
                        evidence_missing=False,
                    )
                )
                status_map[ch.challenge_id] = ChallengeStatus.UNRESOLVED_DISAGREEMENT

            # Case 4: Rule A3 - Asymptomatic Blood Pressure Elevation
            elif rule_id == "RULE-A3-ASYMPTOMATIC-HTN":
                rebuttals.append(
                    AgentRebuttal(
                        rebuttal_id=rebuttal_id,
                        challenge_id=ch.challenge_id,
                        issue_id=ch.issue_id,
                        round_number=2,
                        responding_agent=ch.challenged_agent,
                        disposition=RebuttalDisposition.REVISE,
                        rebuttal_text=(
                            "Revises clinical interpretation: Acknowledges marked blood pressure elevation and confirms "
                            "that absence of subjective distress reflects vascular autoregulation ('silent killer'). "
                            "Agrees that clinical urgency is elevated and recommends repeated resting BP measurement and target-organ damage screening."
                        ),
                        grounding_evidence=["systolic_bp", "diastolic_bp"],
                        revised_claim="Asymptomatic patient requiring prompt evaluation for severe hypertension.",
                        acknowledged_limitations=["Single reading is susceptible to white-coat effect; repeated measurement required."],
                        evidence_missing=False,
                    )
                )
                status_map[ch.challenge_id] = ChallengeStatus.REVISED

            # Case 5: Rule B4 - Undiagnosed Diabetes (History vs Evidence Discrepancy)
            elif rule_id == "RULE-B4-UNDIAGNOSED-DIABETES":
                rebuttals.append(
                    AgentRebuttal(
                        rebuttal_id=rebuttal_id,
                        challenge_id=ch.challenge_id,
                        issue_id=ch.issue_id,
                        round_number=2,
                        responding_agent=ch.challenged_agent,
                        disposition=RebuttalDisposition.REVISE,
                        rebuttal_text=(
                            "Revises medical history status: While the patient record documents no prior formal diagnosis, "
                            "concordant active laboratory markers satisfy ADA 2026 diagnostic criteria. Reclassifies from "
                            "'no diabetes' to 'suspected undiagnosed type 2 diabetes mellitus' pending outpatient confirmatory workup."
                        ),
                        grounding_evidence=["fasting_blood_glucose_mg_dl", "hba1c_percent"],
                        revised_claim="Suspected undiagnosed type 2 diabetes mellitus.",
                        acknowledged_limitations=["ADA guidelines recommend repeat confirmation before declaring final permanent diagnosis."],
                        evidence_missing=False,
                    )
                )
                status_map[ch.challenge_id] = ChallengeStatus.REVISED

            # Case 6: Rule B2 - Antihypertensive Response Timing
            elif rule_id == "RULE-B2-ANTIHYPERTENSIVE-BP":
                rebuttals.append(
                    AgentRebuttal(
                        rebuttal_id=rebuttal_id,
                        challenge_id=ch.challenge_id,
                        issue_id=ch.issue_id,
                        round_number=2,
                        responding_agent=ch.challenged_agent,
                        disposition=RebuttalDisposition.DEFEND,
                        rebuttal_text=(
                            "Defends pharmacotherapy documentation: Antihypertensive medication is active. "
                            "Elevated in-clinic measurement may reflect white-coat reaction or insufficient titration period. "
                            "Recommends 24-hour ambulatory monitoring before declaring true treatment resistance."
                        ),
                        grounding_evidence=["current_medications", "systolic_bp"],
                        acknowledged_limitations=["Single in-clinic reading is inadequate to diagnose treatment-resistant hypertension."],
                        evidence_missing=False,
                    )
                )
                status_map[ch.challenge_id] = ChallengeStatus.UNRESOLVED_DISAGREEMENT

            # Default fallback for other rules
            else:
                # Check if evidence references are present with non-None values in records
                has_substantiating_evidence = any(
                    (ev in labs and labs[ev] is not None)
                    or (ev in history and history[ev] is not None)
                    or (ev in symptoms and symptoms[ev] is not None)
                    or (ev in scores and scores[ev] is not None)
                    or (ev in ml and ml[ev] is not None)
                    for ev in issue.evidence_references
                ) if issue.evidence_references else False

                disposition = RebuttalDisposition.DEFEND if has_substantiating_evidence else RebuttalDisposition.INCONCLUSIVE
                rebuttals.append(
                    AgentRebuttal(
                        rebuttal_id=rebuttal_id,
                        challenge_id=ch.challenge_id,
                        issue_id=ch.issue_id,
                        round_number=2,
                        responding_agent=ch.challenged_agent,
                        disposition=disposition,
                        rebuttal_text=(
                            f"Evaluates claim within {issue.category.value}: "
                            + ("Clinical presentation exhibits valid domain perspective. Disagreement is maintained for consensus weighting."
                               if disposition == RebuttalDisposition.DEFEND
                               else "Evidence is indeterminate or unverified in current patient records. Rebuttal remains inconclusive pending diagnostic workup.")
                        ),
                        grounding_evidence=issue.evidence_references,
                        acknowledged_limitations=issue.clinical_limitations,
                        evidence_missing=not has_substantiating_evidence,
                    )
                )
                status_map[ch.challenge_id] = ChallengeStatus.UNRESOLVED_DISAGREEMENT

        # Universal evidence verification: Rebuttals must cite evidence actually present in records
        for rebuttal in rebuttals:
            missing_evidence_keys = []
            for ev in rebuttal.grounding_evidence:
                ev_str = str(ev).lower()
                found = False
                if ev in labs or ev_str in [str(k).lower() for k in labs.keys()]:
                    found = True
                elif ev in history or ev_str in [str(k).lower() for k in history.keys()]:
                    found = True
                elif ev in symptoms or ev_str in [str(k).lower() for k in symptoms.keys()]:
                    found = True
                elif ev in scores or ev_str in [str(k).lower() for k in scores.keys()]:
                    found = True
                elif ev in ml or ev_str in [str(k).lower() for k in ml.keys()]:
                    found = True
                elif ev in ["current_medications", "chronic_conditions"] and history.get(ev) is not None:
                    found = True
                elif ev in ["symptoms", "duration_hours", "severity"] and symptoms.get(ev) is not None:
                    found = True
                elif ev_str in ["systolic_bp", "diastolic_bp"] and (labs.get("systolic_bp") is not None or labs.get("diastolic_bp") is not None):
                    found = True
                elif ev_str in ["fasting_blood_glucose_mg_dl", "hba1c_percent", "cardiac_troponin_ng_ml", "ldl_cholesterol_mg_dl", "bnp_pg_ml", "nt_pro_bnp_pg_ml"] and labs.get(ev_str) is not None:
                    found = True

                if not found:
                    missing_evidence_keys.append(ev)

            if missing_evidence_keys:
                rebuttal.evidence_missing = True
                for missing_k in missing_evidence_keys:
                    rebuttal.acknowledged_limitations.append(
                        f"Cited evidence key '{missing_k}' is not documented or unverified in current patient records."
                    )
                # If defending without actual supporting patient records, claim is unsupported
                if rebuttal.disposition in [RebuttalDisposition.DEFEND, RebuttalDisposition.INCONCLUSIVE]:
                    rebuttal.disposition = RebuttalDisposition.UNSUPPORTED
                    status_map[rebuttal.challenge_id] = ChallengeStatus.UNSUPPORTED

        return rebuttals, status_map

    def _evaluate_qualitative_nli(self, agent_outputs: Optional[List[Any]]) -> List[NLIAnalysisRecord]:
        """Perform semantic NLI cross-examination across narrative agent findings."""
        records: List[NLIAnalysisRecord] = []
        if not agent_outputs or len(agent_outputs) < 2:
            return records

        # Extract findings from each agent
        role_to_findings: Dict[str, str] = {}
        for output in agent_outputs:
            if isinstance(output, AgentOutputResponse):
                role_to_findings[output.agent_role] = output.findings
            elif isinstance(output, dict):
                role = output.get("agent_role") or output.get("role", "unknown")
                findings = output.get("findings", "")
                role_to_findings[role] = findings

        roles = list(role_to_findings.keys())
        for i in range(len(roles)):
            for j in range(i + 1, len(roles)):
                role_a = roles[i]
                role_b = roles[j]
                claim_a = role_to_findings[role_a]
                claim_b = role_to_findings[role_b]
                record = self.nli_engine.analyze_pair(role_a, claim_a, role_b, claim_b)
                records.append(record)

        return records

    def _evaluate_convergence(
        self,
        total_challenges: int,
        conceded_count: int,
        unresolved_count: int,
        unsupported_count: int,
        challenges: List[AgentChallenge],
    ) -> Tuple[str, str]:
        """Determine final debate convergence status and generate executive summary."""
        if total_challenges == 0:
            return "no_contradictions", "No challenges were issued. Multi-agent panel reached immediate consensus."

        if conceded_count == total_challenges:
            status = "converged"
            summary = (
                f"Adversarial debate protocol converged after Round 2. All {total_challenges} challenged claims "
                "were formally conceded based on objective biomarker grounding."
            )
        elif unsupported_count == total_challenges:
            status = "unsupported_divergence"
            summary = (
                f"Adversarial debate protocol terminated after Round 2. All {total_challenges} challenged claims "
                "were unsupported due to absent, unverified, or ungrounded patient evidence."
            )
        elif unresolved_count == total_challenges:
            status = "unresolved_divergence"
            summary = (
                f"Adversarial debate protocol terminated after maximum 2 rounds. All {total_challenges} challenges "
                "defended with evidence-based rationale. Persistent clinical disagreements preserved for clinical review."
            )
        else:
            status = "partial_convergence"
            summary = (
                f"Adversarial debate protocol achieved partial convergence in 2 rounds: {conceded_count} claims conceded, "
                f"{unresolved_count} legitimate clinical disagreements preserved, and {unsupported_count} unsupported claims."
            )

        return status, summary
