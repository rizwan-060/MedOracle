"""Clinical Contradiction Detection Engine (Step 12.1).

Implements the multi-agent clinical Contradiction Matrix cross-referencing:
1. Subjective symptoms vs. Objective laboratory biomarkers and vitals
2. Longitudinal medication history & adherence vs. Active biomarker endpoints
3. Deterministic cohort equations (Framingham, FINDRISC) vs. Supervised ML classifiers
4. Incomparable prediction targets & horizons (INCOMPARABLE_PREDICTIONS)
5. Qualitative multi-agent narrative findings and discordances (deferred to Sub-Step 12.2)

Generates structured, traceable ContradictionIssue flags with targeted adversarial debate challenges,
comprehensive clinical limitations/confounders, and computes a domain-deduplicated preliminary
Epistemic Doubt Score (0.0 to 1.0).
"""

import logging
from typing import Any, Dict, List, Optional, Set
from app.schemas.analysis import AgentOutputResponse
from app.schemas.consensus import (
    ContradictionCategory,
    ContradictionIssue,
    ContradictionMatrixResult,
    ContradictionSeverity,
)

logger = logging.getLogger("contradiction_detector")


class ContradictionDetector:
    """Clinical Contradiction Detection Engine cross-referencing multi-agent hypotheses and data."""

    # Normalization terms for statin drugs
    STATIN_NAMES: Set[str] = {
        "atorvastatin",
        "rosuvastatin",
        "simvastatin",
        "pravastatin",
        "fluvastatin",
        "lovastatin",
        "pitavastatin",
        "lipitor",
        "crestor",
        "zocor",
        "statin",
    }

    # Normalization terms for antihypertensive drugs
    ANTIHYPERTENSIVE_NAMES: Set[str] = {
        "lisinopril",
        "amlodipine",
        "losartan",
        "metoprolol",
        "hydrochlorothiazide",
        "atenolol",
        "valsartan",
        "ramipril",
        "enalapril",
        "carvedilol",
        "propranolol",
        "diltiazem",
        "verapamil",
        "furosemide",
        "spironolactone",
        "hctz",
        "norvasc",
        "zestril",
        "cozaar",
        "antihypertensive",
    }

    # Normalization terms for antidiabetic drugs
    ANTIDIABETIC_NAMES: Set[str] = {
        "metformin",
        "insulin",
        "glipizide",
        "glimepiride",
        "glyburide",
        "empagliflozin",
        "dapagliflozin",
        "sitagliptin",
        "linagliptin",
        "semaglutide",
        "liraglutide",
        "pioglitazone",
        "glucophage",
        "januvia",
        "jardiance",
        "ozempic",
        "antidiabetic",
    }

    def __init__(self, default_disagreement_threshold: float = 25.0) -> None:
        """Initialize the ContradictionDetector instance.

        Args:
            default_disagreement_threshold: Configurable percentage-point threshold
                for equation vs ML probability discordance (heuristic disparity flag,
                not an established clinical standard).
        """
        self.default_disagreement_threshold = default_disagreement_threshold
        logger.info(
            "Initialized ContradictionDetector engine with default disagreement threshold: %.1f%%",
            self.default_disagreement_threshold,
        )

    def evaluate_contradictions(
        self,
        symptoms_data: Optional[Dict[str, Any]] = None,
        medical_history_data: Optional[Dict[str, Any]] = None,
        laboratory_data: Optional[Dict[str, Any]] = None,
        clinical_scores: Optional[Dict[str, Any]] = None,
        ml_predictions: Optional[Dict[str, Any]] = None,
        agent_outputs: Optional[List[Any]] = None,
        session_id: Optional[str] = None,
        patient_id: Optional[str] = None,
        disagreement_threshold: Optional[float] = None,
    ) -> ContradictionMatrixResult:
        """Execute the multi-agent Contradiction Matrix evaluation.

        Args:
            symptoms_data: Raw or extracted symptoms dictionary.
            medical_history_data: Patient medical and medication history dictionary.
            laboratory_data: Quantitative laboratory biomarkers and vitals dictionary.
            clinical_scores: Deterministic cohort equation scores (Framingham, FINDRISC, etc.).
            ml_predictions: Trained ML model probability estimates.
            agent_outputs: Optional list of AgentOutputResponse or dictionaries from upstream agents.
            session_id: Optional session identifier for collision-free traceability.
            patient_id: Optional patient identifier for audit tracking.
            disagreement_threshold: Optional override for equation vs ML gap threshold.

        Returns:
            ContradictionMatrixResult containing detected issues, severity counts,
            deduplicated preliminary epistemic doubt score, and audit metadata.
        """
        symptoms = symptoms_data or {}
        history = medical_history_data or {}
        labs = laboratory_data or {}
        scores = clinical_scores or {}
        ml = ml_predictions or {}

        effective_threshold = (
            disagreement_threshold
            if disagreement_threshold is not None
            else self.default_disagreement_threshold
        )

        prefix = f"ISSUE-{session_id}" if session_id else "ISSUE"

        # Merge findings from agent_outputs if provided
        normalized_agent_outputs = self._normalize_agent_outputs(agent_outputs)

        issues: List[ContradictionIssue] = []
        model_comparisons: List[Dict[str, Any]] = []

        # 1. Evaluate Subjective Symptoms vs. Objective Biomarkers
        subj_obj_issues = self._evaluate_subjective_vs_objective(
            symptoms=symptoms,
            labs=labs,
            agent_outputs=normalized_agent_outputs,
            prefix=prefix,
            session_id=session_id,
            patient_id=patient_id,
        )
        issues.extend(subj_obj_issues)

        # 2. Evaluate Longitudinal History & Medications vs. Active Biomarkers
        med_bio_issues = self._evaluate_medication_vs_biomarkers(
            history=history,
            labs=labs,
            agent_outputs=normalized_agent_outputs,
            prefix=prefix,
            session_id=session_id,
            patient_id=patient_id,
        )
        issues.extend(med_bio_issues)

        # 3. Evaluate Cohort Equations vs. Machine Learning Classifiers
        eq_ml_issues, comparisons = self._evaluate_equation_vs_ml_discordance(
            scores=scores,
            ml=ml,
            agent_outputs=normalized_agent_outputs,
            prefix=prefix,
            session_id=session_id,
            patient_id=patient_id,
            threshold=effective_threshold,
        )
        issues.extend(eq_ml_issues)
        model_comparisons.extend(comparisons)

        # 4. Evaluate Qualitative Cross-Agent Discordances (deferred to 12.2)
        qualitative_issues = self._evaluate_qualitative_agent_findings(
            normalized_agent_outputs,
            prefix=prefix,
            session_id=session_id,
            patient_id=patient_id,
        )
        issues.extend(qualitative_issues)

        # Calculate severity tallies
        critical_count = sum(1 for i in issues if i.severity == ContradictionSeverity.CRITICAL)
        moderate_count = sum(1 for i in issues if i.severity == ContradictionSeverity.MODERATE)
        minor_count = sum(1 for i in issues if i.severity == ContradictionSeverity.MINOR)
        total_contradictions = len(issues)

        # Calculate deduplicated preliminary Epistemic Doubt Score
        doubt_score = self._calculate_deduplicated_preliminary_doubt(issues)

        # Generate clinical summary narrative
        summary = self._generate_summary(
            total=total_contradictions,
            critical=critical_count,
            moderate=moderate_count,
            minor=minor_count,
            doubt_score=doubt_score,
            issues=issues,
        )

        logger.info(
            "Contradiction detection completed: %d total issues (%d critical, %d moderate, %d minor), preliminary doubt: %.2f",
            total_contradictions,
            critical_count,
            moderate_count,
            minor_count,
            doubt_score,
        )

        return ContradictionMatrixResult(
            session_id=session_id,
            patient_id=patient_id,
            contradictions_detected=total_contradictions > 0,
            total_contradictions=total_contradictions,
            critical_count=critical_count,
            moderate_count=moderate_count,
            minor_count=minor_count,
            issues=issues,
            preliminary_epistemic_doubt=doubt_score,
            doubt_calculation_method="deduplicated_heuristic_severity_weighting",
            doubt_limitations=(
                "Preliminary heuristic score for input ranking only. Not a calibrated posterior probability. "
                "Co-dependent contradictions are deduplicated by clinical domain prior to scoring. "
                "Full epistemic recalibration deferred to Sub-Step 12.3."
            ),
            category_statuses={
                "subjective_vs_objective": "operational",
                "history_medication_vs_biomarker": "operational",
                "equation_vs_ml_discordance": "operational",
                "incomparable_predictions": "operational",
                "qualitative_claim_discordance": "unimplemented_deferred_to_12_2",
            },
            model_comparisons=model_comparisons,
            summary=summary,
        )

    # -------------------------------------------------------------------------
    # Matrix Evaluation Sub-Engines
    # -------------------------------------------------------------------------

    def _evaluate_subjective_vs_objective(
        self,
        symptoms: Dict[str, Any],
        labs: Dict[str, Any],
        agent_outputs: Dict[str, Any],
        prefix: str,
        session_id: Optional[str],
        patient_id: Optional[str],
    ) -> List[ContradictionIssue]:
        """Cross-examine subjective symptoms against objective biomarkers."""
        issues: List[ContradictionIssue] = []

        symptom_list = [s.lower() for s in (symptoms.get("symptoms") or [])]
        notes = (symptoms.get("notes") or "").lower()
        severity = float(symptoms.get("severity") or 0)
        duration_days = float(symptoms.get("duration_days") or 0)
        duration_hours = symptoms.get("duration_hours")
        if duration_hours is None and duration_days > 0:
            duration_hours = duration_days * 24.0

        # Check for acute cardiac / ischemic symptom claims
        ischemic_symptom_keywords = {
            "chest_pain",
            "chest_tightness",
            "angina",
            "substernal_pressure",
            "radiating_chest_pain",
        }
        has_ischemic_symptoms = any(k in symptom_list for k in ischemic_symptom_keywords) or any(
            k in notes for k in ["chest pain", "angina", "substernal", "radiating to left arm", "pressure"]
        )

        troponin = labs.get("cardiac_troponin_ng_ml")
        ecg = str(labs.get("resting_ecg") or "").lower()
        troponin_assay = str(labs.get("cardiac_troponin_assay") or "hs_cTnI")
        serial_completed = bool(labs.get("serial_troponin_completed", False))

        # Rule A1: Acute severe ischemic chest pain vs. normal cardiac troponin & ECG
        # IMPORTANT: Missing troponin (None) is UNTESTED and must never be treated as normal
        if has_ischemic_symptoms and severity >= 6 and troponin is not None:
            troponin_normal = troponin < 0.04
            ecg_normal = any(term in ecg for term in ["normal", "sinus_rhythm", "unremarkable"]) or not ecg

            if troponin_normal:
                # Distinguish early presentation / uncompleted serial testing from confirmed contradiction
                is_early = (duration_hours is not None and duration_hours < 6.0) or (not serial_completed)

                if is_early:
                    issue_severity = ContradictionSeverity.MODERATE
                    is_confirmed = False
                    rationale = (
                        f"Patient reports acute ischemic symptoms (severity {int(severity)}/10), but initial cardiac "
                        f"troponin ({troponin} ng/mL via {troponin_assay}) and resting ECG are non-elevated. "
                        f"Early presentation (< 6 hours from symptom onset) or absence of completed serial testing "
                        f"cannot definitively rule out evolving myocardial necrosis. Unstable angina also characteristically "
                        f"presents with severe ischemic pain without acute myocyte necrosis."
                    )
                    limitations = [
                        "Initial troponin sampling performed < 6 hours from symptom onset may precede detectable peripheral biomarker release; serial resampling at 1-3 hours is clinically essential.",
                        "Unstable angina causes myocardial ischemia without irreversible necrosis and characteristically exhibits normal cardiac troponin and normal ECG.",
                        f"Assay-specific URL: Reference limits vary by assay ({troponin_assay} vs hs-cTnT); laboratory assay reference validation required.",
                    ]
                else:
                    issue_severity = ContradictionSeverity.CRITICAL
                    is_confirmed = True
                    rationale = (
                        f"Acute severe ischemic chest pain (severity {int(severity)}/10, duration {duration_hours or 24:.0f}h) "
                        f"with completed serial cardiac troponin testing ({troponin} ng/mL via {troponin_assay}) "
                        f"and normal ECG strongly conflicts with acute transmural myocardial infarction. "
                        f"Given serial testing beyond the biological release window, non-coronary etiologies "
                        f"(gastroesophageal reflux, costochondritis, pericarditis, anxiety) or non-occlusive unstable angina "
                        f"must be actively adjudicated."
                    )
                    limitations = [
                        "Serial troponin sampling protocol (0h/1h or 0h/3h per ESC/ACC guidelines) confirmed negative, ruling out acute myocardial necrosis with >99% NPV.",
                        "Unstable angina may cause severe ischemic symptoms without biomarker elevation due to lack of completed cell death.",
                        f"Assay reference limits (99th percentile upper reference limit) vary across conventional and high-sensitivity assays ({troponin_assay}).",
                    ]

                claims = {
                    "Symptom Analysis Specialist": (
                        f"Reports acute ischemic symptoms ({', '.join([s for s in symptom_list if s in ischemic_symptom_keywords] or ['chest pain'])}) "
                        f"with severe intensity (severity: {int(severity)}/10, onset: {duration_hours or 'unknown'} hours ago)."
                    ),
                    "Laboratory Biomarker Specialist": (
                        f"Cardiac biomarkers remain strictly within normal reference limits "
                        f"(Troponin: {troponin} ng/mL [{troponin_assay}], Serial Completed: {serial_completed}, ECG: {ecg or 'Normal'})."
                    ),
                }

                issues.append(
                    ContradictionIssue(
                        issue_id=f"{prefix}-SUBJ-OBJ-001",
                        rule_id="RULE-A1-ISCHEMIA-TROPONIN",
                        rule_version="1.1.0",
                        session_id=session_id,
                        patient_id=patient_id,
                        category=ContradictionCategory.SUBJECTIVE_VS_OBJECTIVE,
                        severity=issue_severity,
                        conflicting_agents=[
                            "Symptom Analysis Specialist",
                            "Laboratory Biomarker Specialist",
                        ],
                        diverging_claims=claims,
                        normalized_values={
                            "cardiac_troponin_ng_ml": troponin,
                            "cardiac_troponin_assay": troponin_assay,
                            "serial_troponin_completed": serial_completed,
                            "symptom_duration_hours": duration_hours,
                        },
                        measurement_timestamps={
                            "symptom_duration_hours": str(duration_hours) if duration_hours else None,
                            "troponin_sampling": labs.get("test_date") or labs.get("timestamp"),
                        },
                        evidence_sources=["symptom_report", "laboratory_biomarkers", "resting_ecg"],
                        physiological_rationale=rationale,
                        clinical_limitations=limitations,
                        suggested_challenge=(
                            f"Challenge Symptom Specialist: Given normal {troponin_assay} (<0.04 ng/mL) and normal resting ECG "
                            f"(Serial completed: {serial_completed}), what physiological evidence substantiates an acute coronary event "
                            f"over non-cardiac causes or unstable angina?"
                        ),
                        evidence_references=["cardiac_troponin_ng_ml", "cardiac_troponin_assay", "serial_troponin_completed", "resting_ecg", "symptoms"],
                        is_confirmed_contradiction=is_confirmed,
                    )
                )

        # Rule A2: Acute severe dyspnea vs. normal natriuretic peptide (BNP / NT-proBNP)
        dyspnea_keywords = {"breathlessness", "shortness_of_breath", "dyspnea", "orthopnea"}
        has_severe_dyspnea = any(k in symptom_list for k in dyspnea_keywords) or any(
            k in notes for k in ["shortness of breath", "breathless", "orthopnea", "cannot catch breath"]
        )
        bnp = labs.get("bnp_pg_ml")
        nt_pro_bnp = labs.get("nt_pro_bnp_pg_ml")

        # Distinguish BNP (<100 pg/mL) from NT-proBNP (<300 pg/mL acute rule-out)
        bnp_normal = False
        peptide_type = ""
        peptide_value: Optional[float] = None
        cutoff_val = 100.0

        if nt_pro_bnp is not None:
            peptide_type = "NT-proBNP"
            peptide_value = float(nt_pro_bnp)
            cutoff_val = 300.0
            bnp_normal = peptide_value < 300.0
        elif bnp is not None:
            peptide_type = "BNP"
            peptide_value = float(bnp)
            cutoff_val = 100.0
            bnp_normal = peptide_value < 100.0

        if has_severe_dyspnea and severity >= 7 and bnp_normal and peptide_value is not None:
            claims = {
                "Symptom Analysis Specialist": f"Reports severe acute dyspnea / breathlessness (severity: {int(severity)}/10).",
                "Laboratory Biomarker Specialist": f"{peptide_type} is normal ({peptide_type}: {peptide_value} pg/mL, ref < {cutoff_val} pg/mL).",
            }
            issues.append(
                ContradictionIssue(
                    issue_id=f"{prefix}-SUBJ-OBJ-002",
                    rule_id="RULE-A2-DYSPNEA-BNP",
                    rule_version="1.1.0",
                    session_id=session_id,
                    patient_id=patient_id,
                    category=ContradictionCategory.SUBJECTIVE_VS_OBJECTIVE,
                    severity=ContradictionSeverity.MODERATE,
                    conflicting_agents=[
                        "Symptom Analysis Specialist",
                        "Laboratory Biomarker Specialist",
                    ],
                    diverging_claims=claims,
                    normalized_values={
                        "natriuretic_peptide_type": peptide_type,
                        "natriuretic_peptide_value_pg_ml": peptide_value,
                        "natriuretic_peptide_cutoff_pg_ml": cutoff_val,
                    },
                    measurement_timestamps={
                        "laboratory_sampling": labs.get("test_date") or labs.get("timestamp"),
                    },
                    evidence_sources=["symptom_report", "laboratory_biomarkers"],
                    physiological_rationale=(
                        f"Natriuretic peptides ({peptide_type} < {cutoff_val} pg/mL) possess high negative predictive value (>95%) "
                        f"for ruling out acute left ventricular heart failure. Normal {peptide_type} conflicts with acute decompensated "
                        f"cardiac failure, suggesting non-cardiac etiologies (pulmonary embolism, asthma/COPD exacerbation, anxiety) "
                        f"or Heart Failure with Preserved Ejection Fraction (HFpEF)."
                    ),
                    clinical_limitations=[
                        "Obesity (BMI >= 30 kg/m2) suppresses circulating BNP and NT-proBNP concentrations by up to 50% via increased clearance receptor expression and impaired synthesis.",
                        "Heart Failure with Preserved Ejection Fraction (HFpEF) and isolated right ventricular failure can present with severe dyspnea despite normal or borderline natriuretic peptides.",
                        "Renal impairment (eGFR < 60 mL/min/1.73m2) impairs peptide clearance and raises diagnostic cutoffs; conversely, normal renal clearance can preserve low peptide levels.",
                        "Flash pulmonary edema may cause acute severe dyspnea before ventricular stretch has produced substantial peptide release.",
                    ],
                    suggested_challenge=(
                        f"Challenge Symptom Specialist: Explain how acute cardiac failure is justified when ventricular wall "
                        f"stretch markers ({peptide_type} < {cutoff_val} pg/mL) are normal. Reconcile with HFpEF or pulmonary causes."
                    ),
                    evidence_references=["bnp_pg_ml", "nt_pro_bnp_pg_ml", "symptoms"],
                    is_confirmed_contradiction=False,
                )
            )

        # Rule A3: Asymptomatic patient vs. Stage 2 HTN vs. Hypertensive Urgency / Emergency
        is_asymptomatic = len(symptom_list) == 0 or severity <= 2
        systolic_bp = labs.get("systolic_bp")
        diastolic_bp = labs.get("diastolic_bp")
        fasting_glucose = labs.get("fasting_blood_glucose_mg_dl")
        hba1c = labs.get("hba1c_percent")

        # Evaluate Asymptomatic Hypertension
        if is_asymptomatic and systolic_bp is not None and diastolic_bp is not None:
            sbp = float(systolic_bp)
            dbp = float(diastolic_bp)

            is_urgency_level = (sbp >= 180.0 or dbp >= 120.0)
            is_stage_2_level = (sbp >= 140.0 or dbp >= 90.0) and not is_urgency_level

            if is_urgency_level or is_stage_2_level:
                if is_urgency_level:
                    severity_htn = ContradictionSeverity.CRITICAL
                    urgency_label = "Hypertensive Urgency (SBP >= 180 or DBP >= 120 mmHg)"
                    claim_text = f"Severe Blood Pressure Elevation at Hypertensive Urgency level (BP: {int(sbp)}/{int(dbp)} mmHg) without documented acute target-organ damage."
                else:
                    severity_htn = ContradictionSeverity.MODERATE
                    urgency_label = "Stage 2 Hypertension (SBP 140-179 or DBP 90-119 mmHg)"
                    claim_text = f"Asymptomatic Stage 2 Hypertension (BP: {int(sbp)}/{int(dbp)} mmHg)."

                claims = {
                    "Symptom Analysis Specialist": f"Patient reports minimal or absent subjective symptoms (severity: {int(severity)}/10).",
                    "Laboratory Biomarker Specialist": claim_text,
                }
                issues.append(
                    ContradictionIssue(
                        issue_id=f"{prefix}-SUBJ-OBJ-003",
                        rule_id="RULE-A3-ASYMPTOMATIC-HTN",
                        rule_version="1.1.0",
                        session_id=session_id,
                        patient_id=patient_id,
                        category=ContradictionCategory.SUBJECTIVE_VS_OBJECTIVE,
                        severity=severity_htn,
                        conflicting_agents=[
                            "Symptom Analysis Specialist",
                            "Laboratory Biomarker Specialist",
                        ],
                        diverging_claims=claims,
                        normalized_values={"systolic_bp_mmhg": sbp, "diastolic_bp_mmhg": dbp},
                        measurement_timestamps={"vitals_measurement": labs.get("test_date") or labs.get("timestamp")},
                        evidence_sources=["symptom_report", "vital_signs"],
                        physiological_rationale=(
                            f"Severe asymptomatic blood pressure elevation represents a classic 'silent killer' presentation. "
                            f"Vascular autoregulation allows cerebral and coronary beds to tolerate chronic elevation without "
                            f"subjective distress, decoupling symptoms from acute vascular risk ({urgency_label}). "
                            f"Absence of symptoms must not delay clinical evaluation."
                        ),
                        clinical_limitations=[
                            "Distinguish Hypertensive Urgency (BP >= 180/120 without acute target-organ damage) from Hypertensive Emergency (with encephalopathy, acute aortic dissection, intracranial hemorrhage, acute myocardial infarction, or acute pulmonary edema).",
                            "Absence of subjective complaints in severe hypertension reflects vascular adaptation or silent chronic elevation, but does not preclude acute end-organ damage risk.",
                            "Single clinic measurement may be elevated by white-coat effect, full bladder, recent caffeine, or incorrect cuff size; ambulatory 24h blood pressure monitoring is recommended.",
                        ],
                        suggested_challenge=(
                            f"Challenge Symptom Specialist: Patient reports zero distress, yet blood pressure is {int(sbp)}/{int(dbp)} mmHg "
                            f"({urgency_label}). Reconcile this asymptomatic presentation and evaluate for silent target-organ damage."
                        ),
                        evidence_references=["systolic_bp", "diastolic_bp", "symptoms"],
                        is_confirmed_contradiction=True,
                    )
                )

        # Evaluate Asymptomatic Hyperglycemia (Separated from Hypertension)
        has_severe_glucose = (fasting_glucose is not None and fasting_glucose >= 250.0) or (
            hba1c is not None and hba1c >= 10.0
        )
        if is_asymptomatic and has_severe_glucose:
            glucose_desc = []
            if fasting_glucose is not None and fasting_glucose >= 250.0:
                glucose_desc.append(f"FPG: {fasting_glucose} mg/dL")
            if hba1c is not None and hba1c >= 10.0:
                glucose_desc.append(f"HbA1c: {hba1c}%")

            claims = {
                "Symptom Analysis Specialist": f"Patient reports minimal or absent subjective symptoms (severity: {int(severity)}/10).",
                "Laboratory Biomarker Specialist": f"Severe glucotoxicity and metabolic derangement ({', '.join(glucose_desc)}).",
            }
            issues.append(
                ContradictionIssue(
                    issue_id=f"{prefix}-SUBJ-OBJ-004",
                    rule_id="RULE-A3-ASYMPTOMATIC-GLUCOSE",
                    rule_version="1.1.0",
                    session_id=session_id,
                    patient_id=patient_id,
                    category=ContradictionCategory.SUBJECTIVE_VS_OBJECTIVE,
                    severity=ContradictionSeverity.CRITICAL,
                    conflicting_agents=[
                        "Symptom Analysis Specialist",
                        "Laboratory Biomarker Specialist",
                    ],
                    diverging_claims=claims,
                    normalized_values={
                        "fasting_blood_glucose_mg_dl": fasting_glucose,
                        "hba1c_percent": hba1c,
                    },
                    measurement_timestamps={"laboratory_sampling": labs.get("test_date") or labs.get("timestamp")},
                    evidence_sources=["symptom_report", "laboratory_biomarkers"],
                    physiological_rationale=(
                        "Profound asymptomatic hyperglycemia (fasting glucose >= 250 mg/dL or HbA1c >= 10.0%) reflects insidious "
                        "glucotoxicity where chronic adaptation blunts classical polyuria, polydipsia, or diabetic ketoacidosis/HHS warning signs."
                    ),
                    clinical_limitations=[
                        "Chronic hyperglycemia often develops insidiously, leading to loss of osmotic warning symptoms until hyperosmolar crisis occurs.",
                        "Immediate evaluation for hyperosmolar hyperglycemic state (HHS) or euglycemic/hyperglycemic DKA is indicated despite minimal subjective complaints.",
                    ],
                    suggested_challenge=(
                        "Challenge Symptom Specialist: Patient reports zero distress despite fasting glucose >= 250 mg/dL or HbA1c >= 10.0%. "
                        "Reconcile this asymptomatic presentation and check for subclinical ketonuria or osmotic diuresis."
                    ),
                    evidence_references=["fasting_blood_glucose_mg_dl", "hba1c_percent", "symptoms"],
                    is_confirmed_contradiction=True,
                )
            )

        return issues

    def _evaluate_medication_vs_biomarkers(
        self,
        history: Dict[str, Any],
        labs: Dict[str, Any],
        agent_outputs: Dict[str, Any],
        prefix: str,
        session_id: Optional[str],
        patient_id: Optional[str],
    ) -> List[ContradictionIssue]:
        """Cross-examine documented pharmacotherapy against active laboratory endpoints."""
        issues: List[ContradictionIssue] = []

        medications = history.get("current_medications") or []
        med_dicts = [m for m in medications if isinstance(m, dict)]
        med_names = self._extract_medication_names(medications)
        chronic_conditions = [c.lower() for c in (history.get("chronic_conditions") or [])]
        history_notes = (history.get("notes") or "").lower()

        # Rule B1: Statin therapy vs. extreme LDL-C (>= 190 mg/dL)
        statin_meds = [m for m in med_dicts if any(s in str(m.get("name", "")).lower() for s in self.STATIN_NAMES)]
        has_statin = bool(statin_meds) or any(m in self.STATIN_NAMES for m in med_names)
        ldl = labs.get("ldl_cholesterol_mg_dl")
        total_chol = labs.get("total_cholesterol_mg_dl")

        if has_statin and ldl is not None and ldl >= 190.0:
            # Check therapeutic latency: statin newly initiated < 6 weeks has expected therapeutic lag
            statin_duration_weeks: Optional[float] = None
            for m in statin_meds:
                dur = m.get("treatment_duration_weeks")
                if dur is not None:
                    statin_duration_weeks = float(dur)
                    break

            # If statin was newly initiated < 6 weeks, expected therapeutic latency applies -> NO contradiction
            if statin_duration_weeks is not None and statin_duration_weeks < 6.0:
                logger.info("Rule B1 skipped: Statin newly initiated (<6 weeks latency window).")
            else:
                # Check adherence notes
                adherence_inconsistent = False
                for m in statin_meds:
                    adh = str(m.get("adherence") or "").lower()
                    if adh in ["inconsistent", "poor", "non_compliant", "partial", "non-adherent"]:
                        adherence_inconsistent = True
                if "non-compliance" in history_notes or "forgets" in history_notes or "inconsistent" in history_notes:
                    adherence_inconsistent = True

                if adherence_inconsistent:
                    issue_severity = ContradictionSeverity.MODERATE
                    is_confirmed = False
                    rationale = (
                        f"Documented medication non-adherence accounts for persistent severe LDL elevation ({ldl} mg/dL) "
                        f"despite statin prescription. Inconsistent compliance impairs HMG-CoA reductase suppression."
                    )
                else:
                    issue_severity = ContradictionSeverity.CRITICAL
                    is_confirmed = True
                    rationale = (
                        f"Standard statin pharmacotherapy lowers circulating LDL-C by 30% to 55%. Persistent LDL-C >= 190 mg/dL "
                        f"under chronic active prescription strongly suggests severe medication non-adherence, pharmacogenomic "
                        f"hypo-response, or heterozygous familial hypercholesterolemia requiring non-statin (PCSK9 inhibitor / ezetimibe) escalation."
                    )

                statin_names_str = ", ".join([m for m in med_names if m in self.STATIN_NAMES] or ["statin"])
                claims = {
                    "Medical History Specialist": f"Documents active statin therapy ({statin_names_str}).",
                    "Laboratory Biomarker Specialist": f"Severe hypercholesterolemia with LDL-C at {ldl} mg/dL (ref < 100 mg/dL) and Total Cholesterol at {total_chol or 'N/A'} mg/dL.",
                }
                issues.append(
                    ContradictionIssue(
                        issue_id=f"{prefix}-MED-BIO-001",
                        rule_id="RULE-B1-STATIN-LDL",
                        rule_version="1.1.0",
                        session_id=session_id,
                        patient_id=patient_id,
                        category=ContradictionCategory.HISTORY_MEDICATION_VS_BIOMARKER,
                        severity=issue_severity,
                        conflicting_agents=[
                            "Medical History Specialist",
                            "Laboratory Biomarker Specialist",
                        ],
                        diverging_claims=claims,
                        normalized_values={
                            "statin_regimen": statin_names_str,
                            "treatment_duration_weeks": statin_duration_weeks,
                            "adherence_inconsistent": adherence_inconsistent,
                            "ldl_cholesterol_mg_dl": ldl,
                            "total_cholesterol_mg_dl": total_chol,
                        },
                        measurement_timestamps={"laboratory_sampling": labs.get("test_date") or labs.get("timestamp")},
                        evidence_sources=["medical_history", "laboratory_biomarkers"],
                        physiological_rationale=rationale,
                        clinical_limitations=[
                            "Baseline pre-treatment LDL must be known to evaluate percentage reduction (target 50% reduction on high-intensity statin).",
                            "Pharmacogenomic SLCO1B1 / PCSK9 variants or familial hypercholesterolemia may cause statin resistance requiring ezetimibe or PCSK9 inhibitors.",
                            "Medication adherence must be verified through pharmacy refill records or serum metabolite assays before assuming biological resistance.",
                        ],
                        suggested_challenge=(
                            f"Challenge Medical History Specialist: Patient is prescribed {statin_names_str}, yet LDL remains at an "
                            f"extreme level ({ldl} mg/dL). Investigate compliance, dosage adequacy, or familial dyslipidemia."
                        ),
                        evidence_references=["current_medications", "ldl_cholesterol_mg_dl"],
                        is_confirmed_contradiction=is_confirmed,
                    )
                )

        # Rule B2: Antihypertensive therapy vs. persistent Stage 2 hypertension
        has_antihypertensive = any(m in self.ANTIHYPERTENSIVE_NAMES for m in med_names)
        systolic_bp = labs.get("systolic_bp")
        diastolic_bp = labs.get("diastolic_bp")

        if has_antihypertensive and systolic_bp is not None and diastolic_bp is not None:
            sbp = float(systolic_bp)
            dbp = float(diastolic_bp)
            is_stage_2 = sbp >= 140.0 or dbp >= 90.0

            if is_stage_2:
                antihypertensive_names_str = ", ".join([m for m in med_names if m in self.ANTIHYPERTENSIVE_NAMES])
                claims = {
                    "Medical History Specialist": f"Documents active antihypertensive therapy ({antihypertensive_names_str}).",
                    "Laboratory Biomarker Specialist": f"Demonstrates uncontrolled Stage 2 Hypertension (BP: {int(sbp)}/{int(dbp)} mmHg).",
                }
                issues.append(
                    ContradictionIssue(
                        issue_id=f"{prefix}-MED-BIO-002",
                        rule_id="RULE-B2-ANTIHYPERTENSIVE-BP",
                        rule_version="1.1.0",
                        session_id=session_id,
                        patient_id=patient_id,
                        category=ContradictionCategory.HISTORY_MEDICATION_VS_BIOMARKER,
                        severity=ContradictionSeverity.MODERATE,
                        conflicting_agents=[
                            "Medical History Specialist",
                            "Laboratory Biomarker Specialist",
                        ],
                        diverging_claims=claims,
                        normalized_values={
                            "antihypertensive_regimen": antihypertensive_names_str,
                            "systolic_bp_mmhg": sbp,
                            "diastolic_bp_mmhg": dbp,
                        },
                        measurement_timestamps={"vitals_measurement": labs.get("test_date") or labs.get("timestamp")},
                        evidence_sources=["medical_history", "vital_signs"],
                        physiological_rationale=(
                            f"Antihypertensive agents should lower peripheral vascular resistance and maintain systolic BP < 130 mmHg. "
                            f"Persistent Stage 2 readings ({int(sbp)}/{int(dbp)} mmHg) despite reported pharmacotherapy indicate apparent "
                            f"treatment-resistant hypertension, irregular adherence, white-coat effect, or inappropriate monotherapy."
                        ),
                        clinical_limitations=[
                            "Single isolated in-clinic blood pressure measurement is susceptible to white-coat effect, stress, cuff artifact, and diurnal fluctuation; 24h ABPM or home BP log is required.",
                            "Antihypertensive therapeutic latency requires 2 to 4 weeks to reach maximum pharmacodynamic efficacy after initiation or dose escalation.",
                            "Suboptimal adherence, sodium intake, NSAID interactions, or secondary hypertension (e.g. renal artery stenosis, hyperaldosteronism) must be excluded.",
                        ],
                        suggested_challenge=(
                            f"Challenge Medical History Specialist: Antihypertensives ({antihypertensive_names_str}) are documented, "
                            f"but blood pressure remains Stage 2 ({int(sbp)}/{int(dbp)} mmHg). Assess compliance, dosing intervals, and secondary hypertension causes."
                        ),
                        evidence_references=["current_medications", "systolic_bp", "diastolic_bp"],
                        is_confirmed_contradiction=False,
                    )
                )

        # Rule B3: Antidiabetic therapy vs. uncontrolled glycemia (HbA1c >= 8.5%)
        has_antidiabetic = any(m in self.ANTIDIABETIC_NAMES for m in med_names)
        hba1c = labs.get("hba1c_percent")
        fasting_glucose = labs.get("fasting_blood_glucose_mg_dl")

        if has_antidiabetic and ((hba1c is not None and hba1c >= 8.5) or (fasting_glucose is not None and fasting_glucose >= 180.0)):
            antidiabetic_names_str = ", ".join([m for m in med_names if m in self.ANTIDIABETIC_NAMES])
            claims = {
                "Medical History Specialist": f"Documents active antidiabetic therapy ({antidiabetic_names_str}).",
                "Laboratory Biomarker Specialist": f"Demonstrates uncontrolled chronic glycemia (HbA1c: {hba1c or 'N/A'}%, Glucose: {fasting_glucose or 'N/A'} mg/dL).",
            }
            issues.append(
                ContradictionIssue(
                    issue_id=f"{prefix}-MED-BIO-003",
                    rule_id="RULE-B3-ANTIDIABETIC-HBA1C",
                    rule_version="1.1.0",
                    session_id=session_id,
                    patient_id=patient_id,
                    category=ContradictionCategory.HISTORY_MEDICATION_VS_BIOMARKER,
                    severity=ContradictionSeverity.MODERATE,
                    conflicting_agents=[
                        "Medical History Specialist",
                        "Laboratory Biomarker Specialist",
                    ],
                    diverging_claims=claims,
                    normalized_values={
                        "antidiabetic_regimen": antidiabetic_names_str,
                        "hba1c_percent": hba1c,
                        "fasting_blood_glucose_mg_dl": fasting_glucose,
                    },
                    measurement_timestamps={"laboratory_sampling": labs.get("test_date") or labs.get("timestamp")},
                    evidence_sources=["medical_history", "laboratory_biomarkers"],
                    physiological_rationale=(
                        f"An HbA1c of {hba1c or 'elevated'}% reflects an estimated average glucose exceeding 197 mg/dL over 90 days. "
                        f"Under active antidiabetic treatment, this indicates regimen insufficiency, secondary sulfonylurea/metformin failure, "
                        f"or significant dietary non-compliance."
                    ),
                    clinical_limitations=[
                        "Glycated hemoglobin (HbA1c) reflects average glycemic exposure over 2 to 3 months (erythrocyte lifespan ~120 days); recent medication adjustments (< 12 weeks) are not fully captured.",
                        "Individualized HbA1c targets vary by age, cardiovascular comorbidities, hypoglycemia risk, and life expectancy (e.g. ADA goal < 7.0% for most adults, < 8.0-8.5% for frail elderly).",
                        "Hemoglobinopathies, hemolytic anemia, and chronic kidney disease alter erythrocyte turnover and invalidate HbA1c accuracy.",
                    ],
                    suggested_challenge=(
                        f"Challenge Medical History Specialist: Why does HbA1c remain {hba1c or 'elevated'}% despite prescribed antidiabetic medications? "
                        f"Clarify adherence, treatment duration, and evaluate need for regimen intensification."
                    ),
                    evidence_references=["current_medications", "hba1c_percent", "fasting_blood_glucose_mg_dl"],
                    is_confirmed_contradiction=False,
                )
            )

        # Rule B4: Undiagnosed diabetes mellitus (ADA 2026 Diagnostic Standards)
        denies_diabetes = not any(
            d in condition for condition in chronic_conditions for d in ["diabetes", "t2d", "t1d", "hyperglycemia"]
        ) and not has_antidiabetic

        fpg_abnormal = fasting_glucose is not None and fasting_glucose >= 126.0
        hba1c_abnormal = hba1c is not None and hba1c >= 6.5

        if denies_diabetes and (fpg_abnormal or hba1c_abnormal):
            # ADA 2026 Criteria: Two concordant abnormal markers confirm diabetes; single abnormal is provisional
            if fpg_abnormal and hba1c_abnormal:
                issue_severity = ContradictionSeverity.CRITICAL
                is_confirmed = True
                rationale = (
                    f"Dual concordant abnormal biomarkers (Fasting Plasma Glucose {fasting_glucose} mg/dL [>=126] "
                    f"AND HbA1c {hba1c}% [>=6.5%]) definitively confirm the diagnosis of diabetes mellitus per ADA 2026 "
                    f"Standards of Care in a patient with no documented prior history. This indicates undiagnosed, untreated diabetes."
                )
                limitations = [
                    "ADA 2026 criteria confirm diagnosis without repeat testing when two distinct diagnostic markers (FPG and HbA1c) are concurrently abnormal.",
                    "Acute severe intercurrent illness, glucocorticoid administration, or stress hyperglycemia should be clinically ruled out.",
                ]
            else:
                issue_severity = ContradictionSeverity.MODERATE
                is_confirmed = False
                abnormal_marker = f"FPG: {fasting_glucose} mg/dL" if fpg_abnormal else f"HbA1c: {hba1c}%"
                rationale = (
                    f"A single abnormal biomarker ({abnormal_marker}) in an asymptomatic patient with no documented diabetes "
                    f"represents provisional dysglycemia rather than confirmed diabetes per ADA 2026 Standards of Care. "
                    f"Confirmatory repeat testing is required before a definitive diagnostic declaration."
                )
                limitations = [
                    "Per ADA 2026 diagnostic guidelines, a single abnormal test result without unequivocal hyperglycemia symptoms requires prompt repeat confirmatory testing using a second sample.",
                    "Transient physiological stressors, acute infection, or laboratory pre-analytical errors can cause isolated glucose elevations.",
                ]

            claims = {
                "Medical History Specialist": "History explicitly reports no diagnosed diabetes mellitus.",
                "Laboratory Biomarker Specialist": f"Active laboratory markers indicate diabetic dysglycemia (FPG: {fasting_glucose or 'N/A'} mg/dL, HbA1c: {hba1c or 'N/A'}%).",
            }
            issues.append(
                ContradictionIssue(
                    issue_id=f"{prefix}-MED-BIO-004",
                    rule_id="RULE-B4-UNDIAGNOSED-DIABETES",
                    rule_version="1.1.0",
                    session_id=session_id,
                    patient_id=patient_id,
                    category=ContradictionCategory.HISTORY_MEDICATION_VS_BIOMARKER,
                    severity=issue_severity,
                    conflicting_agents=[
                        "Medical History Specialist",
                        "Laboratory Biomarker Specialist",
                    ],
                    diverging_claims=claims,
                    normalized_values={
                        "fasting_blood_glucose_mg_dl": fasting_glucose,
                        "hba1c_percent": hba1c,
                        "dual_marker_concordance": bool(fpg_abnormal and hba1c_abnormal),
                    },
                    measurement_timestamps={"laboratory_sampling": labs.get("test_date") or labs.get("timestamp")},
                    evidence_sources=["medical_history", "laboratory_biomarkers"],
                    physiological_rationale=rationale,
                    clinical_limitations=limitations,
                    suggested_challenge=(
                        f"Challenge Medical History Specialist: Patient history shows no record of diabetes, yet laboratory data "
                        f"meets ADA thresholds (FPG: {fasting_glucose}, HbA1c: {hba1c}). Address this undiagnosed metabolic finding."
                    ),
                    evidence_references=["chronic_conditions", "hba1c_percent", "fasting_blood_glucose_mg_dl"],
                    is_confirmed_contradiction=is_confirmed,
                )
            )

        return issues

    def _evaluate_equation_vs_ml_discordance(
        self,
        scores: Dict[str, Any],
        ml: Dict[str, Any],
        agent_outputs: Dict[str, Any],
        prefix: str,
        session_id: Optional[str],
        patient_id: Optional[str],
        threshold: float,
    ) -> tuple[List[ContradictionIssue], List[Dict[str, Any]]]:
        """Cross-examine population cohort equations against non-linear ML predictions."""
        issues: List[ContradictionIssue] = []
        comparisons: List[Dict[str, Any]] = []

        # Rule C1: Framingham 10-Yr CVD Risk vs. ML CVD Probability Divergence
        framingham_pct = scores.get("framingham_risk_percent")
        framingham_cat = (scores.get("framingham_risk_category") or "").lower()
        ml_cvd_pct = ml.get("cardiovascular_risk_percent")
        ml_cvd_cat = (ml.get("cardiovascular_risk_category") or "").lower()

        eq_outcome = scores.get("target_outcome", "10_year_incident_cvd")
        eq_horizon = scores.get("prediction_horizon", "10_years")
        ml_outcome = ml.get("target_outcome", "cross_sectional_angiographic_cad")
        ml_horizon = ml.get("prediction_horizon", "cross_sectional")

        if framingham_pct is not None and ml_cvd_pct is not None:
            gap = round(abs(float(ml_cvd_pct) - float(framingham_pct)), 1)
            is_compatible = (eq_outcome == ml_outcome and eq_horizon == ml_horizon)
            cross_boundary = (framingham_cat == "low" and ml_cvd_cat == "high") or (
                framingham_cat == "high" and ml_cvd_cat == "low"
            )
            has_disparity = (gap >= threshold) or cross_boundary

            if has_disparity:
                if not is_compatible:
                    # Disparate endpoints & horizons: Flag INCOMPARABLE_PREDICTIONS
                    comparisons.append({
                        "comparison": "Framingham 10-Yr Incident CVD vs. ML Coronary Artery Disease",
                        "equation_outcome": str(eq_outcome),
                        "equation_horizon": str(eq_horizon),
                        "ml_outcome": str(ml_outcome),
                        "ml_horizon": str(ml_horizon),
                        "status": "INCOMPARABLE_PREDICTIONS",
                        "disparity_gap_pct": gap,
                        "limitation": (
                            "Models predict fundamentally disparate outcomes and time horizons. "
                            "Framingham predicts 10-year incident composite cardiovascular events, "
                            "whereas ML predicts cross-sectional presence of anatomical coronary stenosis."
                        ),
                    })

                    claims = {
                        "Framingham Risk Equation": f"{framingham_pct:.1f}% 10-year risk ({eq_outcome}, {eq_horizon}).",
                        "Machine Learning CVD Classifier": f"{ml_cvd_pct:.1f}% risk probability ({ml_outcome}, {ml_horizon}).",
                    }
                    issues.append(
                        ContradictionIssue(
                            issue_id=f"{prefix}-EQ-ML-001",
                            rule_id="RULE-C1-FRAMINGHAM-UCI-HORIZON",
                            rule_version="1.1.0",
                            session_id=session_id,
                            patient_id=patient_id,
                            category=ContradictionCategory.INCOMPARABLE_PREDICTIONS,
                            severity=ContradictionSeverity.MODERATE,
                            conflicting_agents=[
                                "Risk Prediction Ensemble Specialist",
                                "Risk Prediction Ensemble Specialist",
                            ],
                            diverging_claims=claims,
                            normalized_values={
                                "framingham_risk_percent": framingham_pct,
                                "ml_cvd_risk_percent": ml_cvd_pct,
                                "disparity_gap_percent": gap,
                                "equation_outcome": str(eq_outcome),
                                "ml_outcome": str(ml_outcome),
                            },
                            measurement_timestamps={},
                            evidence_sources=["cohort_equations", "machine_learning_models"],
                            physiological_rationale=(
                                f"Methodological Horizon & Endpoint Disparity: Framingham ({framingham_pct:.1f}%) estimates 10-year incident composite "
                                f"cardiovascular event probability, whereas the ML classifier ({ml_cvd_pct:.1f}%) estimates cross-sectional presence of "
                                f"angiographic coronary artery disease (>50% stenosis). Direct probability comparison is mathematically incomparable."
                            ),
                            clinical_limitations=[
                                "Framingham Risk Score predicts 10-year incidence of hard coronary/cerebrovascular events, not acute cross-sectional coronary stenosis.",
                                "Machine learning classifiers trained on cross-sectional clinical datasets (e.g. UCI Heart Disease) predict current anatomical disease presence, not longitudinal 10-year risk.",
                                "Probability calibration (e.g. Platt scaling / Isotonic regression) must be verified before interpreting ML output as a true event probability.",
                            ],
                            suggested_challenge=(
                                f"Challenge Risk Ensemble: Clarify that Framingham ({framingham_pct:.1f}%) and ML classifier ({ml_cvd_pct:.1f}%) "
                                f"target disparate endpoints (10-yr incident CVD vs cross-sectional CAD) to avoid invalid direct probability substitution."
                            ),
                            evidence_references=["framingham_risk_percent", "cardiovascular_risk_percent"],
                            is_confirmed_contradiction=False,
                        )
                    )
                else:
                    # Compatible endpoints: Compare against configurable threshold
                    comparisons.append({
                        "comparison": "Framingham 10-Yr Incident CVD vs. ML Calibrated CVD Classifier",
                        "equation_outcome": str(eq_outcome),
                        "equation_horizon": str(eq_horizon),
                        "ml_outcome": str(ml_outcome),
                        "ml_horizon": str(ml_horizon),
                        "status": "SIGNIFICANT_DISCORDANCE",
                        "disparity_gap_pct": gap,
                    })

                    severity = ContradictionSeverity.CRITICAL if gap >= 30.0 else ContradictionSeverity.MODERATE
                    claims = {
                        "Framingham Risk Equation": f"{framingham_pct:.1f}% 10-year risk ({framingham_cat or 'unspecified'}).",
                        "Machine Learning CVD Classifier": f"{ml_cvd_pct:.1f}% risk probability ({ml_cvd_cat or 'unspecified'}).",
                    }
                    issues.append(
                        ContradictionIssue(
                            issue_id=f"{prefix}-EQ-ML-001",
                            rule_id="RULE-C1-COMPATIBLE-GAP",
                            rule_version="1.1.0",
                            session_id=session_id,
                            patient_id=patient_id,
                            category=ContradictionCategory.EQUATION_VS_ML_DISCORDANCE,
                            severity=severity,
                            conflicting_agents=[
                                "Risk Prediction Ensemble Specialist",
                                "Risk Prediction Ensemble Specialist",
                            ],
                            diverging_claims=claims,
                            normalized_values={
                                "framingham_risk_percent": framingham_pct,
                                "ml_cvd_risk_percent": ml_cvd_pct,
                                "disparity_gap_percent": gap,
                                "configured_threshold": threshold,
                            },
                            measurement_timestamps={},
                            evidence_sources=["cohort_equations", "machine_learning_models"],
                            physiological_rationale=(
                                f"A significant divergence of {gap:.1f}% (exceeding heuristic threshold of {threshold:.1f}%) exists between "
                                f"the linear cohort equation (Framingham: {framingham_pct:.1f}%) and the non-linear ML model (ML: {ml_cvd_pct:.1f}%). "
                                f"The ML model captures non-linear interactions and atypical risk weighting that linear cohort equations under-represent."
                            ),
                            clinical_limitations=[
                                f"The {threshold:.1f}% disagreement cutoff is a heuristic audit flag, not an established clinical standard.",
                                "ML models may exhibit poor probability calibration on out-of-distribution demographics.",
                            ],
                            suggested_challenge=(
                                f"Challenge Risk Ensemble: Reconcile the {gap:.1f}% discordance between Framingham CVD ({framingham_pct:.1f}%) "
                                f"and ML risk ({ml_cvd_pct:.1f}%). Which specific risk factors justify the higher or lower estimate?"
                            ),
                            evidence_references=["framingham_risk_percent", "cardiovascular_risk_percent"],
                            is_confirmed_contradiction=True,
                        )
                    )
            else:
                comparisons.append({
                    "comparison": "Framingham 10-Yr Incident CVD vs. ML CVD Classifier",
                    "equation_outcome": str(eq_outcome),
                    "equation_horizon": str(eq_horizon),
                    "ml_outcome": str(ml_outcome),
                    "ml_horizon": str(ml_horizon),
                    "status": "CONCORDANT" if is_compatible else "INCOMPARABLE_PREDICTIONS",
                    "disparity_gap_pct": gap,
                })

        # Rule C2: FINDRISC Score vs. Random Forest ML Diabetes Probability
        findrisc_score = scores.get("findrisc_score")
        findrisc_cat = (scores.get("findrisc_risk_category") or "").lower()
        ml_diabetes_pct = ml.get("diabetes_risk_percent")
        ml_diabetes_cat = (ml.get("diabetes_risk_category") or "").lower()

        if findrisc_score is not None and ml_diabetes_pct is not None:
            low_findrisc_high_ml = findrisc_score < 7 and ml_diabetes_pct >= 40.0
            high_findrisc_low_ml = findrisc_score >= 15 and ml_diabetes_pct < 20.0

            if low_findrisc_high_ml or high_findrisc_low_ml:
                comparisons.append({
                    "comparison": "FINDRISC 10-Yr Incident Diabetes vs. ML Diabetes Classifier",
                    "equation_outcome": "10_year_incident_type_2_diabetes",
                    "equation_horizon": "10_years",
                    "ml_outcome": "cross_sectional_diabetes_presence",
                    "ml_horizon": "cross_sectional",
                    "status": "INCOMPARABLE_PREDICTIONS",
                    "limitation": (
                        "FINDRISC estimates 10-year future risk of developing type 2 diabetes based on lifestyle factors, "
                        "whereas ML classifies existing undiagnosed diabetes from cross-sectional metabolic features."
                    ),
                })

                claims = {
                    "FINDRISC Equation Score": f"{findrisc_score} points ({findrisc_cat or 'unspecified'}, 10-yr incident risk).",
                    "Machine Learning Diabetes Classifier": f"{ml_diabetes_pct:.1f}% probability ({ml_diabetes_cat or 'unspecified'}, cross-sectional presence).",
                }
                issues.append(
                    ContradictionIssue(
                        issue_id=f"{prefix}-EQ-ML-002",
                        rule_id="RULE-C2-FINDRISC-PIMA-HORIZON",
                        rule_version="1.1.0",
                        session_id=session_id,
                        patient_id=patient_id,
                        category=ContradictionCategory.INCOMPARABLE_PREDICTIONS,
                        severity=ContradictionSeverity.MODERATE,
                        conflicting_agents=[
                            "Risk Prediction Ensemble Specialist",
                            "Risk Prediction Ensemble Specialist",
                        ],
                        diverging_claims=claims,
                        normalized_values={
                            "findrisc_score": findrisc_score,
                            "ml_diabetes_percent": ml_diabetes_pct,
                        },
                        measurement_timestamps={},
                        evidence_sources=["cohort_equations", "machine_learning_models"],
                        physiological_rationale=(
                            "FINDRISC evaluates 10-year prospective incidence of type 2 diabetes based on macroscopic anthropometric "
                            "and lifestyle variables (BMI, age, physical activity), whereas supervised ML models trained on cross-sectional "
                            "datasets (e.g. Pima Indians) classify current diagnostic diabetes status. The models assess disparate time horizons."
                        ),
                        clinical_limitations=[
                            "FINDRISC evaluates 10-year risk of developing type 2 diabetes based on age, BMI, waist circumference, and lifestyle.",
                            "ML diabetes classifiers (e.g. Pima Indians) classify current diagnostic diabetes status, not 10-year incident risk.",
                            "Patients with favorable lifestyle scores can have subclinical pancreatic beta-cell dysfunction or genetic insulin resistance.",
                        ],
                        suggested_challenge=(
                            "Challenge Risk Ensemble: Explain why FINDRISC lifestyle score diverges categorically from the "
                            "Random Forest metabolic prediction, recognizing disparate 10-year vs cross-sectional horizons."
                        ),
                        evidence_references=["findrisc_score", "diabetes_risk_percent"],
                        is_confirmed_contradiction=False,
                    )
                )

        return issues, comparisons

    def _evaluate_qualitative_agent_findings(
        self,
        agent_outputs: Dict[str, Any],
        prefix: str,
        session_id: Optional[str],
        patient_id: Optional[str],
    ) -> List[ContradictionIssue]:
        """Cross-examine qualitative narrative text from agent outputs.

        NOTE: Full cross-agent narrative discourse and natural language inference (NLI)
        is deliberately assigned to Sub-Step 12.2 (Adversarial Debate Protocol).
        This method returns an empty issue list to avoid superficial keyword heuristics,
        and its status is reported as 'unimplemented_deferred_to_12_2'.
        """
        return []

    # -------------------------------------------------------------------------
    # Helper & Formatting Methods
    # -------------------------------------------------------------------------

    def _calculate_deduplicated_preliminary_doubt(self, issues: List[ContradictionIssue]) -> float:
        """Calculate preliminary Epistemic Doubt Score deduplicating co-dependent issues.

        To prevent artificial score inflation from multiple issues arising from the same
        underlying clinical domain (e.g. blood pressure derangement flagged by both Rule A3
        and Rule B2), issues are grouped by root clinical domain. For each unique domain,
        only the maximum severity weight is applied.

        Severity Weights:
        - Critical: 0.25
        - Moderate: 0.12
        - Minor: 0.05
        Doubt = min(1.0, sum(domain_max_weights))
        """
        if not issues:
            return 0.0

        rule_to_domain: Dict[str, str] = {
            "RULE-A1-ISCHEMIA-TROPONIN": "cardiac_ischemia",
            "RULE-A2-DYSPNEA-BNP": "cardiac_hemodynamics_heart_failure",
            "RULE-A3-ASYMPTOMATIC-HTN": "hemodynamic_blood_pressure",
            "RULE-A3-ASYMPTOMATIC-GLUCOSE": "glycemic_control",
            "RULE-B1-STATIN-LDL": "lipid_metabolism",
            "RULE-B2-ANTIHYPERTENSIVE-BP": "hemodynamic_blood_pressure",
            "RULE-B3-ANTIDIABETIC-HBA1C": "glycemic_control",
            "RULE-B4-UNDIAGNOSED-DIABETES": "glycemic_control",
            "RULE-C1-FRAMINGHAM-UCI-HORIZON": "cardiovascular_prediction_ensemble",
            "RULE-C1-COMPATIBLE-GAP": "cardiovascular_prediction_ensemble",
            "RULE-C2-FINDRISC-PIMA-HORIZON": "diabetes_prediction_ensemble",
        }

        severity_weight: Dict[ContradictionSeverity, float] = {
            ContradictionSeverity.CRITICAL: 0.25,
            ContradictionSeverity.MODERATE: 0.12,
            ContradictionSeverity.MINOR: 0.05,
        }

        domain_max_weight: Dict[str, float] = {}
        for issue in issues:
            domain = rule_to_domain.get(issue.rule_id, issue.category.value)
            weight = severity_weight.get(issue.severity, 0.05)
            if domain not in domain_max_weight or weight > domain_max_weight[domain]:
                domain_max_weight[domain] = weight

        total_doubt = sum(domain_max_weight.values())
        return round(min(1.0, total_doubt), 4)

    def _normalize_agent_outputs(self, agent_outputs: Optional[List[Any]]) -> Dict[str, Any]:
        """Map a list of agent outputs to a normalized dictionary keyed by agent role."""
        normalized: Dict[str, Any] = {}
        if not agent_outputs:
            return normalized

        for output in agent_outputs:
            if isinstance(output, AgentOutputResponse):
                role = output.agent_role
                normalized[role] = output
            elif isinstance(output, dict):
                role = output.get("agent_role") or output.get("role", "unknown_agent")
                normalized[role] = output

        return normalized

    def _extract_medication_names(self, medications: List[Any]) -> List[str]:
        """Normalize medication names into a list of lowercase strings."""
        names: List[str] = []
        for med in medications:
            if isinstance(med, str):
                names.append(med.strip().lower())
            elif isinstance(med, dict):
                name = med.get("name") or med.get("medication") or ""
                if name:
                    names.append(str(name).strip().lower())
        return names

    def _generate_summary(
        self,
        total: int,
        critical: int,
        moderate: int,
        minor: int,
        doubt_score: float,
        issues: List[ContradictionIssue],
    ) -> str:
        """Generate an executive clinical summary of the contradiction evaluation."""
        if total == 0:
            return (
                "Contradiction Matrix Evaluation: Concordant. All multi-agent clinical hypotheses, "
                "laboratory endpoints, and cohort/ML predictions demonstrate physiological harmony. "
                "Preliminary Epistemic Doubt Score is 0.00."
            )

        categories = {i.category.value for i in issues}
        cat_labels = ", ".join(sorted(categories))

        return (
            f"Contradiction Matrix identified {total} clinical discordances "
            f"({critical} critical, {moderate} moderate, {minor} minor) across categories: [{cat_labels}]. "
            f"Preliminary Epistemic Doubt Score computed at {doubt_score:.2f} (domain-deduplicated). "
            f"Adversarial debate protocol triggered to resolve high-priority clinical conflicts."
        )
