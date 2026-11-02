"""Clinical Contradiction Detection Engine (Step 12.1).

Implements the multi-agent clinical Contradiction Matrix cross-referencing:
1. Subjective symptoms vs. Objective laboratory biomarkers and vitals
2. Longitudinal medication history & adherence vs. Active biomarker endpoints
3. Deterministic cohort equations (Framingham, FINDRISC) vs. Supervised ML classifiers
4. Qualitative multi-agent narrative findings and discordances

Generates structured ContradictionIssue flags with targeted adversarial debate challenges
and computes the preliminary Epistemic Doubt Score (0.0 to 1.0).
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

    def __init__(self) -> None:
        """Initialize the ContradictionDetector instance."""
        logger.info("Initialized ContradictionDetector engine.")

    def evaluate_contradictions(
        self,
        symptoms_data: Optional[Dict[str, Any]] = None,
        medical_history_data: Optional[Dict[str, Any]] = None,
        laboratory_data: Optional[Dict[str, Any]] = None,
        clinical_scores: Optional[Dict[str, Any]] = None,
        ml_predictions: Optional[Dict[str, Any]] = None,
        agent_outputs: Optional[List[Any]] = None,
    ) -> ContradictionMatrixResult:
        """Execute the multi-agent Contradiction Matrix evaluation.

        Args:
            symptoms_data: Raw or extracted symptoms dictionary.
            medical_history_data: Patient medical and medication history dictionary.
            laboratory_data: Quantitative laboratory biomarkers and vitals dictionary.
            clinical_scores: Deterministic cohort equation scores (Framingham, FINDRISC, etc.).
            ml_predictions: Trained ML model probability estimates.
            agent_outputs: Optional list of AgentOutputResponse or dictionaries from upstream agents.

        Returns:
            ContradictionMatrixResult containing detected issues, severity counts,
            and preliminary epistemic doubt score.
        """
        symptoms = symptoms_data or {}
        history = medical_history_data or {}
        labs = laboratory_data or {}
        scores = clinical_scores or {}
        ml = ml_predictions or {}

        # Merge findings from agent_outputs if provided
        normalized_agent_outputs = self._normalize_agent_outputs(agent_outputs)

        issues: List[ContradictionIssue] = []

        # 1. Evaluate Subjective Symptoms vs. Objective Biomarkers
        subj_obj_issues = self._evaluate_subjective_vs_objective(
            symptoms=symptoms,
            labs=labs,
            agent_outputs=normalized_agent_outputs,
        )
        issues.extend(subj_obj_issues)

        # 2. Evaluate Longitudinal History & Medications vs. Active Biomarkers
        med_bio_issues = self._evaluate_medication_vs_biomarkers(
            history=history,
            labs=labs,
            agent_outputs=normalized_agent_outputs,
        )
        issues.extend(med_bio_issues)

        # 3. Evaluate Cohort Equations vs. Machine Learning Classifiers
        eq_ml_issues = self._evaluate_equation_vs_ml_discordance(
            scores=scores,
            ml=ml,
            agent_outputs=normalized_agent_outputs,
        )
        issues.extend(eq_ml_issues)

        # 4. Evaluate Qualitative Cross-Agent Discordances (from agent text findings)
        qualitative_issues = self._evaluate_qualitative_agent_findings(
            normalized_agent_outputs
        )
        issues.extend(qualitative_issues)

        # Calculate severity tallies
        critical_count = sum(1 for i in issues if i.severity == ContradictionSeverity.CRITICAL)
        moderate_count = sum(1 for i in issues if i.severity == ContradictionSeverity.MODERATE)
        minor_count = sum(1 for i in issues if i.severity == ContradictionSeverity.MINOR)
        total_contradictions = len(issues)

        # Calculate mathematical preliminary Epistemic Doubt Score:
        # Doubt = min(1.0, 0.25 * critical + 0.12 * moderate + 0.05 * minor)
        doubt_score = min(
            1.0,
            (0.25 * critical_count) + (0.12 * moderate_count) + (0.05 * minor_count),
        )
        doubt_score = round(doubt_score, 4)

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
            "Contradiction detection completed: %d total issues (%d critical, %d moderate, %d minor), epistemic doubt: %.2f",
            total_contradictions,
            critical_count,
            moderate_count,
            minor_count,
            doubt_score,
        )

        return ContradictionMatrixResult(
            contradictions_detected=total_contradictions > 0,
            total_contradictions=total_contradictions,
            critical_count=critical_count,
            moderate_count=moderate_count,
            minor_count=minor_count,
            issues=issues,
            preliminary_epistemic_doubt=doubt_score,
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
    ) -> List[ContradictionIssue]:
        """Cross-examine subjective symptoms against objective biomarkers."""
        issues: List[ContradictionIssue] = []

        # Extract symptom indicators
        symptom_list = [s.lower() for s in (symptoms.get("symptoms") or [])]
        notes = (symptoms.get("notes") or "").lower()
        severity = float(symptoms.get("severity") or 0)

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

        # Laboratory cardiac biomarkers
        troponin = labs.get("cardiac_troponin_ng_ml")
        ecg = str(labs.get("resting_ecg") or "").lower()

        # Rule A1: Acute severe ischemic claims vs. Normal troponin and normal ECG
        if has_ischemic_symptoms and severity >= 6:
            troponin_normal = troponin is not None and troponin < 0.04
            ecg_normal = any(term in ecg for term in ["normal", "sinus_rhythm", "unremarkable"])

            if troponin_normal or ecg_normal:
                claims = {
                    "Symptom Analysis Specialist": (
                        f"Reports acute ischemic symptoms ({', '.join([s for s in symptom_list if s in ischemic_symptom_keywords] or ['chest pain'])}) "
                        f"with severe intensity (severity: {int(severity)}/10)."
                    ),
                    "Laboratory Biomarker Specialist": (
                        f"Cardiac biomarkers remain strictly within normal reference limits "
                        f"(Troponin: {troponin if troponin is not None else 'Not tested'} ng/mL, ECG: {ecg or 'Normal'})."
                    ),
                }
                issues.append(
                    ContradictionIssue(
                        issue_id="ISSUE-SUBJ-OBJ-001",
                        category=ContradictionCategory.SUBJECTIVE_VS_OBJECTIVE,
                        severity=ContradictionSeverity.CRITICAL,
                        conflicting_agents=[
                            "Symptom Analysis Specialist",
                            "Laboratory Biomarker Specialist",
                        ],
                        diverging_claims=claims,
                        physiological_rationale=(
                            "Acute myocardial ischemia or infarction characteristically triggers elevated cardiac "
                            "troponin release (>0.04 ng/mL) and ischemic ST-T segment abnormalities. Normal troponin "
                            "and ECG strongly conflict with transmural ischemia, suggesting non-cardiac chest pain "
                            "(gastroesophageal reflux, costochondritis, anxiety) or early pre-infarction unstable angina."
                        ),
                        suggested_challenge=(
                            "Challenge Symptom Specialist: Given normal cardiac troponin (<0.04 ng/mL) and normal resting ECG, "
                            "what physiological evidence substantiates an acute coronary event over non-cardiac causes?"
                        ),
                        evidence_references=["cardiac_troponin_ng_ml", "resting_ecg", "symptoms"],
                    )
                )

        # Rule A2: Acute severe dyspnea vs. Normal natriuretic peptide (BNP) & vitals
        dyspnea_keywords = {"breathlessness", "shortness_of_breath", "dyspnea", "orthopnea"}
        has_severe_dyspnea = any(k in symptom_list for k in dyspnea_keywords) or "shortness of breath" in notes
        bnp = labs.get("bnp_pg_ml") or labs.get("nt_pro_bnp_pg_ml")

        if has_severe_dyspnea and severity >= 7 and bnp is not None and bnp < 100.0:
            claims = {
                "Symptom Analysis Specialist": f"Reports severe acute dyspnea / breathlessness (severity: {int(severity)}/10).",
                "Laboratory Biomarker Specialist": f"B-type natriuretic peptide is normal (BNP: {bnp} pg/mL, ref < 100 pg/mL).",
            }
            issues.append(
                ContradictionIssue(
                    issue_id="ISSUE-SUBJ-OBJ-002",
                    category=ContradictionCategory.SUBJECTIVE_VS_OBJECTIVE,
                    severity=ContradictionSeverity.MODERATE,
                    conflicting_agents=[
                        "Symptom Analysis Specialist",
                        "Laboratory Biomarker Specialist",
                    ],
                    diverging_claims=claims,
                    physiological_rationale=(
                        "Natriuretic peptides (BNP < 100 pg/mL) possess high negative predictive value (>95%) "
                        "for ruling out acute left ventricular heart failure. Normal BNP conflicts with acute cardiac "
                        "decompensation, indicating primary pulmonary, hyperventilatory, or musculoskeletal etiology."
                    ),
                    suggested_challenge=(
                        "Challenge Symptom Specialist: Explain how acute cardiac failure is justified when ventricular wall "
                        "stretch markers (BNP < 100 pg/mL) are normal."
                    ),
                    evidence_references=["bnp_pg_ml", "symptoms"],
                )
            )

        # Rule A3: Asymptomatic patient vs. Malignant Hypertension or Severe Glycemia
        is_asymptomatic = len(symptom_list) == 0 or severity <= 2
        systolic_bp = labs.get("systolic_bp")
        diastolic_bp = labs.get("diastolic_bp")
        fasting_glucose = labs.get("fasting_blood_glucose_mg_dl")
        hba1c = labs.get("hba1c_percent")

        has_malignant_bp = (systolic_bp is not None and systolic_bp >= 160.0) or (
            diastolic_bp is not None and diastolic_bp >= 100.0
        )
        has_severe_glucose = (fasting_glucose is not None and fasting_glucose >= 250.0) or (
            hba1c is not None and hba1c >= 10.0
        )

        if is_asymptomatic and (has_malignant_bp or has_severe_glucose):
            deranged_findings = []
            if has_malignant_bp:
                deranged_findings.append(f"Stage 2 severe hypertension (BP: {systolic_bp}/{diastolic_bp} mmHg)")
            if has_severe_glucose:
                deranged_findings.append(f"Profound hyperglycemia (Glucose: {fasting_glucose} mg/dL, HbA1c: {hba1c}%)")

            claims = {
                "Symptom Analysis Specialist": f"Patient reports minimal or absent subjective symptoms (severity: {int(severity)}/10).",
                "Laboratory Biomarker Specialist": f"Demonstrates severe physiological derangement: {', '.join(deranged_findings)}.",
            }
            issues.append(
                ContradictionIssue(
                    issue_id="ISSUE-SUBJ-OBJ-003",
                    category=ContradictionCategory.SUBJECTIVE_VS_OBJECTIVE,
                    severity=ContradictionSeverity.CRITICAL,
                    conflicting_agents=[
                        "Symptom Analysis Specialist",
                        "Laboratory Biomarker Specialist",
                    ],
                    diverging_claims=claims,
                    physiological_rationale=(
                        "Severe hypertensive crisis or profound metabolic glucotoxicity is frequently asymptomatic "
                        "('silent killer'), decoupling patient perception from critical vascular risk. Absence of subjective "
                        "complaints must not diminish urgent escalation."
                    ),
                    suggested_challenge=(
                        "Challenge Symptom Specialist: Patient reports zero distress, yet hemodynamic/glycemic markers "
                        "exceed hypertensive crisis/severe diabetic thresholds. Reconcile this asymptomatic presentation."
                    ),
                    evidence_references=["systolic_bp", "diastolic_bp", "fasting_blood_glucose_mg_dl", "hba1c_percent"],
                )
            )

        return issues

    def _evaluate_medication_vs_biomarkers(
        self,
        history: Dict[str, Any],
        labs: Dict[str, Any],
        agent_outputs: Dict[str, Any],
    ) -> List[ContradictionIssue]:
        """Cross-examine documented pharmacotherapy against active laboratory endpoints."""
        issues: List[ContradictionIssue] = []

        medications = history.get("current_medications") or []
        med_names = self._extract_medication_names(medications)
        chronic_conditions = [c.lower() for c in (history.get("chronic_conditions") or [])]

        # Rule B1: Documented Statin Therapy vs. Extreme LDL-C (>= 190 mg/dL)
        has_statin = any(m in self.STATIN_NAMES for m in med_names)
        ldl = labs.get("ldl_cholesterol_mg_dl")
        total_chol = labs.get("total_cholesterol_mg_dl")

        if has_statin and ldl is not None and ldl >= 190.0:
            claims = {
                "Medical History Specialist": f"Documents active statin therapy ({', '.join([m for m in med_names if m in self.STATIN_NAMES])}).",
                "Laboratory Biomarker Specialist": f"Severe hypercholesterolemia with LDL-C at {ldl} mg/dL (ref < 100 mg/dL) and Total Cholesterol at {total_chol or 'N/A'} mg/dL.",
            }
            issues.append(
                ContradictionIssue(
                    issue_id="ISSUE-MED-BIO-001",
                    category=ContradictionCategory.HISTORY_MEDICATION_VS_BIOMARKER,
                    severity=ContradictionSeverity.CRITICAL,
                    conflicting_agents=[
                        "Medical History Specialist",
                        "Laboratory Biomarker Specialist",
                    ],
                    diverging_claims=claims,
                    physiological_rationale=(
                        "Standard statin pharmacotherapy lowers circulating LDL-C by 30% to 55%. Persistent LDL-C >= 190 mg/dL "
                        "under active prescription strongly suggests severe medication non-adherence, pharmacogenomic hypo-response, "
                        "or heterozygous familial hypercholesterolemia requiring non-statin (PCSK9 inhibitor / ezetimibe) escalation."
                    ),
                    suggested_challenge=(
                        "Challenge Medical History Specialist: Patient is prescribed statin therapy, yet LDL remains at an "
                        "extreme level (>= 190 mg/dL). Investigate compliance, dosage adequacy, or familial dyslipidemia."
                    ),
                    evidence_references=["current_medications", "ldl_cholesterol_mg_dl"],
                )
            )

        # Rule B2: Documented Antihypertensive Therapy vs. Persistent Stage 2 Hypertension
        has_antihypertensive = any(m in self.ANTIHYPERTENSIVE_NAMES for m in med_names)
        systolic_bp = labs.get("systolic_bp")
        diastolic_bp = labs.get("diastolic_bp")

        if has_antihypertensive and systolic_bp is not None and diastolic_bp is not None:
            is_stage_2 = systolic_bp >= 140.0 or diastolic_bp >= 90.0
            is_severe = systolic_bp >= 160.0 or diastolic_bp >= 100.0

            if is_stage_2:
                severity = ContradictionSeverity.CRITICAL if is_severe else ContradictionSeverity.MODERATE
                claims = {
                    "Medical History Specialist": f"Documents active antihypertensive therapy ({', '.join([m for m in med_names if m in self.ANTIHYPERTENSIVE_NAMES])}).",
                    "Laboratory Biomarker Specialist": f"Demonstrates uncontrolled Stage 2 Hypertension (BP: {systolic_bp}/{diastolic_bp} mmHg).",
                }
                issues.append(
                    ContradictionIssue(
                        issue_id="ISSUE-MED-BIO-002",
                        category=ContradictionCategory.HISTORY_MEDICATION_VS_BIOMARKER,
                        severity=severity,
                        conflicting_agents=[
                            "Medical History Specialist",
                            "Laboratory Biomarker Specialist",
                        ],
                        diverging_claims=claims,
                        physiological_rationale=(
                            "Antihypertensive agents should lower peripheral vascular resistance and maintain systolic BP < 130 mmHg. "
                            "Persistent Stage 2 readings despite reported pharmacotherapy indicate apparent treatment-resistant "
                            "hypertension, irregular adherence, white-coat effect, or inappropriate monotherapy."
                        ),
                        suggested_challenge=(
                            "Challenge Medical History Specialist: Antihypertensives are documented, but blood pressure remains Stage 2. "
                            "Assess compliance, dosing intervals, and secondary hypertension causes."
                        ),
                        evidence_references=["current_medications", "systolic_bp", "diastolic_bp"],
                    )
                )

        # Rule B3: Documented Antidiabetic Therapy vs. Uncontrolled Glycemia (HbA1c >= 8.5%)
        has_antidiabetic = any(m in self.ANTIDIABETIC_NAMES for m in med_names)
        hba1c = labs.get("hba1c_percent")
        fasting_glucose = labs.get("fasting_blood_glucose_mg_dl")

        if has_antidiabetic and ((hba1c is not None and hba1c >= 8.5) or (fasting_glucose is not None and fasting_glucose >= 180.0)):
            claims = {
                "Medical History Specialist": f"Documents active antidiabetic therapy ({', '.join([m for m in med_names if m in self.ANTIDIABETIC_NAMES])}).",
                "Laboratory Biomarker Specialist": f"Demonstrates uncontrolled chronic glycemia (HbA1c: {hba1c or 'N/A'}%, Glucose: {fasting_glucose or 'N/A'} mg/dL).",
            }
            issues.append(
                ContradictionIssue(
                    issue_id="ISSUE-MED-BIO-003",
                    category=ContradictionCategory.HISTORY_MEDICATION_VS_BIOMARKER,
                    severity=ContradictionSeverity.MODERATE,
                    conflicting_agents=[
                        "Medical History Specialist",
                        "Laboratory Biomarker Specialist",
                    ],
                    diverging_claims=claims,
                    physiological_rationale=(
                        "An HbA1c >= 8.5% reflects an estimated average glucose > 197 mg/dL over 90 days. Under active antidiabetic "
                        "treatment, this indicates regimen insufficiency, secondary sulfonylurea/metformin failure, or significant dietary non-compliance."
                    ),
                    suggested_challenge=(
                        "Challenge Medical History Specialist: Why does HbA1c remain >= 8.5% despite prescribed antidiabetic medications? "
                        "Clarify adherence and evaluate need for treatment escalation."
                    ),
                    evidence_references=["current_medications", "hba1c_percent", "fasting_blood_glucose_mg_dl"],
                )
            )

        # Rule B4: Denial of Diabetes in Chronic History vs. Diagnostic Diabetic Lab Markers
        denies_diabetes = not any(
            d in condition for condition in chronic_conditions for d in ["diabetes", "t2d", "t1d", "hyperglycemia"]
        )
        meets_diabetes_lab = (hba1c is not None and hba1c >= 6.5) or (
            fasting_glucose is not None and fasting_glucose >= 126.0
        )

        if denies_diabetes and meets_diabetes_lab:
            claims = {
                "Medical History Specialist": "History explicitly reports no diagnosed diabetes mellitus.",
                "Laboratory Biomarker Specialist": f"Active laboratory markers meet ADA diagnostic thresholds (HbA1c: {hba1c}%, FPG: {fasting_glucose} mg/dL).",
            }
            issues.append(
                ContradictionIssue(
                    issue_id="ISSUE-MED-BIO-004",
                    category=ContradictionCategory.HISTORY_MEDICATION_VS_BIOMARKER,
                    severity=ContradictionSeverity.CRITICAL,
                    conflicting_agents=[
                        "Medical History Specialist",
                        "Laboratory Biomarker Specialist",
                    ],
                    diverging_claims=claims,
                    physiological_rationale=(
                        "Objective biomarkers satisfy the American Diabetes Association (ADA) criteria for diabetes mellitus "
                        "(HbA1c >= 6.5% or Fasting Plasma Glucose >= 126 mg/dL) in a patient with no prior documented history. "
                        "This indicates undiagnosed, unmanaged diabetes requiring prompt clinical intervention."
                    ),
                    suggested_challenge=(
                        "Challenge Medical History Specialist: Patient history shows no record of diabetes, yet laboratory data "
                        "meets diagnostic criteria. Address this undiagnosed metabolic finding."
                    ),
                    evidence_references=["chronic_conditions", "hba1c_percent", "fasting_blood_glucose_mg_dl"],
                )
            )

        return issues

    def _evaluate_equation_vs_ml_discordance(
        self,
        scores: Dict[str, Any],
        ml: Dict[str, Any],
        agent_outputs: Dict[str, Any],
    ) -> List[ContradictionIssue]:
        """Cross-examine population cohort equations against non-linear ML predictions."""
        issues: List[ContradictionIssue] = []

        # Rule C1: Framingham 10-Yr CVD Risk vs. ML CVD Probability Divergence (>= 25% gap)
        framingham_pct = scores.get("framingham_risk_percent")
        framingham_cat = (scores.get("framingham_risk_category") or "").lower()
        ml_cvd_pct = ml.get("cardiovascular_risk_percent")
        ml_cvd_cat = (ml.get("cardiovascular_risk_category") or "").lower()

        if framingham_pct is not None and ml_cvd_pct is not None:
            gap = abs(float(ml_cvd_pct) - float(framingham_pct))

            # Trigger if gap >= 25.0% OR if crossing low-to-high categorical boundary
            cross_boundary = (framingham_cat == "low" and ml_cvd_cat == "high") or (
                framingham_cat == "high" and ml_cvd_cat == "low"
            )

            if gap >= 25.0 or cross_boundary:
                severity = ContradictionSeverity.CRITICAL if gap >= 30.0 or cross_boundary else ContradictionSeverity.MODERATE
                claims = {
                    "Framingham Risk Equation": f"{framingham_pct:.1f}% 10-year risk ({framingham_cat or 'unspecified'}).",
                    "Machine Learning CVD Classifier": f"{ml_cvd_pct:.1f}% risk probability ({ml_cvd_cat or 'unspecified'}).",
                }
                issues.append(
                    ContradictionIssue(
                        issue_id="ISSUE-EQ-ML-001",
                        category=ContradictionCategory.EQUATION_VS_ML_DISCORDANCE,
                        severity=severity,
                        conflicting_agents=[
                            "Risk Prediction Ensemble Specialist",
                            "Risk Prediction Ensemble Specialist",
                        ],
                        diverging_claims=claims,
                        physiological_rationale=(
                            f"A significant divergence of {gap:.1f}% exists between the linear population equation "
                            f"(Framingham: {framingham_pct:.1f}%) and the non-linear Gradient Boosting ML model "
                            f"(ML: {ml_cvd_pct:.1f}%). The ML model captures high-order non-linear feature interactions "
                            f"(e.g., family history weighting, extreme lipid fractions) that the cohort equation under-represents."
                        ),
                        suggested_challenge=(
                            f"Challenge Risk Ensemble: Reconcile the {gap:.1f}% discordance between Framingham CVD ({framingham_pct:.1f}%) "
                            f"and ML risk ({ml_cvd_pct:.1f}%). Which specific risk factors justify the higher or lower estimate?"
                        ),
                        evidence_references=["framingham_risk_percent", "cardiovascular_risk_percent"],
                    )
                )

        # Rule C2: FINDRISC Score vs. Random Forest ML Diabetes Probability
        findrisc_score = scores.get("findrisc_score")
        findrisc_cat = (scores.get("findrisc_risk_category") or "").lower()
        ml_diabetes_pct = ml.get("diabetes_risk_percent")
        ml_diabetes_cat = (ml.get("diabetes_risk_category") or "").lower()

        if findrisc_score is not None and ml_diabetes_pct is not None:
            # Low FINDRISC (< 7, < 1% risk) vs. High ML Diabetes (>= 40%)
            low_findrisc_high_ml = findrisc_score < 7 and ml_diabetes_pct >= 40.0
            # High FINDRISC (>= 15, >= 33% risk) vs. Low ML Diabetes (< 20%)
            high_findrisc_low_ml = findrisc_score >= 15 and ml_diabetes_pct < 20.0

            if low_findrisc_high_ml or high_findrisc_low_ml:
                claims = {
                    "FINDRISC Equation Score": f"{findrisc_score} points ({findrisc_cat or 'unspecified'}).",
                    "Machine Learning Diabetes Classifier": f"{ml_diabetes_pct:.1f}% risk probability ({ml_diabetes_cat or 'unspecified'}).",
                }
                issues.append(
                    ContradictionIssue(
                        issue_id="ISSUE-EQ-ML-002",
                        category=ContradictionCategory.EQUATION_VS_ML_DISCORDANCE,
                        severity=ContradictionSeverity.MODERATE,
                        conflicting_agents=[
                            "Risk Prediction Ensemble Specialist",
                            "Risk Prediction Ensemble Specialist",
                        ],
                        diverging_claims=claims,
                        physiological_rationale=(
                            "FINDRISC assesses macroscopic lifestyle and anthropometric factors (BMI, age, physical activity), "
                            "whereas the Random Forest ML classifier incorporates biochemical insulin resistance biomarkers. "
                            "Discordance highlights either early metabolic dysfunction without anthropometric changes, or lifestyle risk without biochemical manifestation."
                        ),
                        suggested_challenge=(
                            "Challenge Risk Ensemble: Explain why FINDRISC lifestyle score diverges categorically from the "
                            "Random Forest metabolic prediction."
                        ),
                        evidence_references=["findrisc_score", "diabetes_risk_percent"],
                    )
                )

        return issues

    def _evaluate_qualitative_agent_findings(
        self,
        agent_outputs: Dict[str, Any],
    ) -> List[ContradictionIssue]:
        """Cross-examine qualitative narrative text from agent outputs."""
        issues: List[ContradictionIssue] = []

        symptom_output = agent_outputs.get("Symptom Analysis Specialist") or agent_outputs.get("symptom_specialist")
        history_output = agent_outputs.get("Medical History Specialist") or agent_outputs.get("medical_history_specialist")

        if not symptom_output or not history_output:
            return issues

        symptom_findings = (getattr(symptom_output, "findings", None) or symptom_output.get("findings", "")).lower()
        history_findings = (getattr(history_output, "findings", None) or history_output.get("findings", "")).lower()

        # Check for denial of smoking in history vs acute smoking-related respiratory symptom findings
        if "never smoker" in history_findings or "denies smoking" in history_findings:
            if "smoking history" in symptom_findings or "pack-year" in symptom_findings:
                claims = {
                    "Symptom Analysis Specialist": "Attributes respiratory compromise in part to tobacco exposure.",
                    "Medical History Specialist": "Documents patient as a lifelong non-smoker.",
                }
                issues.append(
                    ContradictionIssue(
                        issue_id="ISSUE-QUAL-001",
                        category=ContradictionCategory.QUALITATIVE_CLAIM_DISCORDANCE,
                        severity=ContradictionSeverity.MINOR,
                        conflicting_agents=[
                            "Symptom Analysis Specialist",
                            "Medical History Specialist",
                        ],
                        diverging_claims=claims,
                        physiological_rationale=(
                            "Inconsistent smoking history documentation compromises accuracy of cardiovascular and "
                            "pulmonary risk stratification."
                        ),
                        suggested_challenge=(
                            "Challenge Medical History Specialist: Clarify exact tobacco exposure history to resolve contradictory agent assumptions."
                        ),
                        evidence_references=["smoking_status"],
                    )
                )

        return issues

    # -------------------------------------------------------------------------
    # Helper & Formatting Methods
    # -------------------------------------------------------------------------

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
            f"Preliminary Epistemic Doubt Score computed at {doubt_score:.2f}. "
            f"Adversarial debate protocol triggered to resolve high-priority clinical conflicts."
        )
