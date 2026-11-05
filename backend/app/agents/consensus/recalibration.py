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
  Awarded only for verified, normalized, traceable, independent patient evidence that SUPPORTS the claim.
  Claim-specific evidence evaluation classifies each item as SUPPORTS, CONTRADICTS, NEUTRAL, INSUFFICIENT, or UNVERIFIABLE.
  Collinear measurements within the same panel (e.g. SBP/DBP or LDL/Total Cholesterol) award zero compounding credit.
  A single normal result is never classified as contradictory without assay-specific timing and clinical context.
- Unresolved Contradiction Penalty (-10% to -25%):
  Claim-specific penalty scaled by contradiction severity (Critical: -25%, Moderate: -15%, Minor: -10%).
  A concession in debate is an argumentative event, not empirical proof of clinical truth.
  Resolved contradictions do not continue to penalize claims.
  Unresolved contradictions retain domain-deduplicated severity penalties.
- Configurable Essential Evidence Registry (Cap at 40%):
  When mandatory clinical evidence required for an acute diagnostic claim is missing, untested, or unverified,
  that claim's confidence is bounded strictly at 40.0% (or the rule-specific ceiling).
  Unrelated claims (e.g. chronic conditions, family history disclosures) are exempt from acute diagnostic caps.
  Missing evidence is never equated with a negative or normal finding.
- Domain-Isolated Epistemic Doubt & Global Aggregation (0.0 to 1.0):
  Uncertainty is evaluated independently per clinical domain. Missing cardiac evidence does not increase doubt
  in unrelated lipid or metabolic domains.
  Domain doubt floors apply strictly to affected domains.
  Global doubt aggregates peak domain uncertainty and panel mean without concealing high-risk domains.
  Explicitly designated as a heuristic mathematical score (heuristic_recalibration_v1.0.0).
"""

import logging
import math
import uuid
from dataclasses import dataclass, field
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
    EvidenceSupportClassification,
    EvidenceValidityState,
    SerialTroponinValidationStatus,
    TargetOrganDamageState,
)

logger = logging.getLogger("confidence_recalibration")



# =============================================================================
# Biological Analyte & Diagnostic Groups (Separation Registry)
# =============================================================================

OBJECTIVE_LAB_GROUPS: Dict[str, List[str]] = {
    "troponin": [
        "cardiac_troponin_ng_ml",
        "hs_troponin_i_ng_ml",
        "hs_troponin_t_ng_ml",
        "troponin_i_ng_ml",
        "troponin_t_ng_ml",
        "cardiac_troponin_assay",
    ],
    "natriuretic_peptide": [
        "bnp_pg_ml",
        "nt_pro_bnp_pg_ml",
    ],
    "glycemia": [
        "fasting_blood_glucose_mg_dl",
        "hba1c_percent",
        "random_blood_glucose_mg_dl",
        "blood_glucose_mg_dl",
        "blood_ketones_mmol_l",
    ],
    "glycemia_acute": [
        "fasting_blood_glucose_mg_dl",
        "random_blood_glucose_mg_dl",
        "blood_glucose_mg_dl",
    ],
    "glycemia_chronic": [
        "hba1c_percent",
    ],
    "ketones": [
        "blood_ketones_mmol_l",
        "beta_hydroxybutyrate_mmol_l",
        "serum_ketones_mmol_l",
        "urine_ketones",
    ],
    "acid_base": [
        "blood_ph",
        "arterial_ph",
        "venous_ph",
        "serum_bicarbonate_mmol_l",
        "bicarbonate_mEq_L",
    ],
    "osmolality": [
        "serum_osmolality_mosm_kg",
        "effective_osmolality_mosm_kg",
    ],
    "lipid_panel": [
        "ldl_cholesterol_mg_dl",
        "total_cholesterol_mg_dl",
        "hdl_cholesterol_mg_dl",
        "triglycerides_mg_dl",
    ],
    "kidney": [
        "serum_creatinine_mg_dl",
        "egfr_ml_min",
        "blood_urea_nitrogen_mg_dl",
    ],
    "target_organ_damage": [
        "serum_creatinine_mg_dl",
        "egfr_ml_min",
        "cardiac_troponin_ng_ml",
        "hs_troponin_i_ng_ml",
        "resting_ecg",
        "bnp_pg_ml",
    ],
}

OBJECTIVE_DIAGNOSTIC_GROUPS: Dict[str, List[str]] = {
    "resting_ecg": [
        "resting_ecg",
        "ecg",
        "12_lead_ecg",
    ],
    "blood_pressure": [
        "systolic_bp",
        "diastolic_bp",
        "blood_pressure",
        "systolic_diastolic_bp",
    ],
    "cardiac_function": [
        "echocardiogram_lvef_percent",
        "ejection_fraction",
        "lvef",
        "echocardiogram",
    ],
}

PHARMACOTHERAPY_GROUPS: Dict[str, List[str]] = {
    "statin_therapy": [
        "current_medications:statin",
    ],
    "antihypertensive_therapy": [
        "current_medications:antihypertensive",
    ],
}

SYMPTOM_GROUPS: Dict[str, List[str]] = {
    "symptom_report": [
        "symptoms",
        "chest_pain",
        "dyspnea",
    ],
}

# Unified analyte groups map for canonical lookup
ANALYTE_GROUPS: Dict[str, List[str]] = {
    **OBJECTIVE_LAB_GROUPS,
    **OBJECTIVE_DIAGNOSTIC_GROUPS,
    **PHARMACOTHERAPY_GROUPS,
    **SYMPTOM_GROUPS,
}


# =============================================================================
# Biomarker Freshness & Assay Metadata Registries (A5 & A10)
# =============================================================================

BIOMARKER_FRESHNESS_HOURS: Dict[str, float] = {
    # Acute biomarkers (short physiological half-life / rapid kinetics)
    "cardiac_troponin_ng_ml": 24.0,
    "hs_troponin_i_ng_ml": 24.0,
    "hs_troponin_t_ng_ml": 24.0,
    "resting_ecg": 24.0,
    "blood_ph": 24.0,
    "arterial_ph": 24.0,
    "venous_ph": 24.0,
    "beta_hydroxybutyrate_mmol_l": 24.0,
    "blood_ketones_mmol_l": 24.0,
    "serum_bicarbonate_mmol_l": 24.0,
    "random_blood_glucose_mg_dl": 24.0,
    "blood_glucose_mg_dl": 24.0,
    "bnp_pg_ml": 48.0,
    "nt_pro_bnp_pg_ml": 48.0,
    # Subacute / renal function
    "serum_creatinine_mg_dl": 720.0,  # 30 days
    "egfr_ml_min": 720.0,
    # Chronic biomarkers (long-term glycemic and lipid exposure)
    "hba1c_percent": 4320.0,  # 180 days (6 months)
    "ldl_cholesterol_mg_dl": 8760.0,  # 365 days (1 year)
    "total_cholesterol_mg_dl": 8760.0,
    "hdl_cholesterol_mg_dl": 8760.0,
    "triglycerides_mg_dl": 8760.0,
}

TROPONIN_ASSAY_PROFILES: Dict[str, Dict[str, Any]] = {
    "hs_ctni_abbott": {
        "name": "Abbott Architect / Alinity hs-cTnI",
        "type": "hs-cTnI",
        "standard_unit": "ng/L",
        "url_overall_ng_l": 26.0,
        "url_female_ng_l": 15.6,
        "url_male_ng_l": 34.2,
        "url_female_ng_ml": 0.0156,
        "url_male_ng_ml": 0.0342,
        "url_ng_ml": 0.026,
    },
    "hs_ctnt_roche": {
        "name": "Roche Elecsys hs-cTnT",
        "type": "hs-cTnT",
        "standard_unit": "ng/L",
        "url_overall_ng_l": 14.0,
        "url_female_ng_l": 9.0,
        "url_male_ng_l": 15.5,
        "url_female_ng_ml": 0.009,
        "url_male_ng_ml": 0.0155,
        "url_ng_ml": 0.014,
    },
    "hs_ctni_siemens": {
        "name": "Siemens Atellica hs-cTnI",
        "type": "hs-cTnI",
        "standard_unit": "ng/L",
        "url_overall_ng_l": 45.0,
        "url_female_ng_l": 34.0,
        "url_male_ng_l": 53.0,
        "url_female_ng_ml": 0.034,
        "url_male_ng_ml": 0.053,
        "url_ng_ml": 0.045,
    },
    "hs_ctni_beckman": {
        "name": "Beckman Coulter Access hs-cTnI",
        "type": "hs-cTnI",
        "standard_unit": "ng/L",
        "url_overall_ng_l": 17.5,
        "url_female_ng_l": 11.6,
        "url_male_ng_l": 19.8,
        "url_female_ng_ml": 0.0116,
        "url_male_ng_ml": 0.0198,
        "url_ng_ml": 0.018,
    },
    "conventional_ctni": {
        "name": "Conventional cTnI",
        "type": "cTnI",
        "standard_unit": "ng/mL",
        "url_overall_ng_l": 40.0,
        "url_male_ng_l": 40.0,
        "url_female_ng_l": 40.0,
        "url_male_ng_ml": 0.04,
        "url_female_ng_ml": 0.04,
        "url_ng_ml": 0.04,
    },
    "conventional_ctnt": {
        "name": "Conventional cTnT",
        "type": "cTnT",
        "standard_unit": "ng/mL",
        "url_overall_ng_l": 10.0,
        "url_male_ng_l": 10.0,
        "url_female_ng_l": 10.0,
        "url_male_ng_ml": 0.01,
        "url_female_ng_ml": 0.01,
        "url_ng_ml": 0.01,
    },
}


# =============================================================================
# Configurable Logical Claim Evidence Requirements Registry (A1)
# =============================================================================

@dataclass
class EvidenceGroup:
    """Logical grouping of diagnostic evidence keys or clinical conditions."""

    operator: str = "OR"  # "OR" or "AND"
    keys: List[str] = field(default_factory=list)
    description: str = ""
    min_required: int = 1


@dataclass
class ClinicalEvidenceRequirement:
    """Structured clinical rule governing essential diagnostic evidence with logical expressions."""

    requirement_id: str
    clinical_domain: str
    trigger_keywords: List[str]
    required_groups: List[EvidenceGroup] = field(default_factory=list)
    supportive_groups: List[EvidenceGroup] = field(default_factory=list)
    contradictory_groups: List[EvidenceGroup] = field(default_factory=list)
    exempt_keywords: List[str] = field(default_factory=list)
    confidence_cap: float = 40.0
    guideline_reference: str = ""
    rationale: str = ""

    # Backwards-compatibility property
    @property
    def mandatory_analyte_groups(self) -> List[str]:
        groups = []
        for g in self.required_groups:
            if g.description:
                groups.append(g.description)
            elif g.keys:
                groups.append(g.keys[0])
        return groups


# Backwards compatible alias
ClaimEvidenceRequirement = ClinicalEvidenceRequirement


CLAIM_REQUIREMENT_REGISTRY: List[ClinicalEvidenceRequirement] = [
    ClinicalEvidenceRequirement(
        requirement_id="REQ-ACUTE-ISCHEMIA",
        clinical_domain="ischemia",
        trigger_keywords=[
            "acute myocardial",
            "myocardial infarction",
            "stemi",
            "nstemi",
            "acute coronary",
            "ischemic event",
            "coronary syndrome",
            "acute ischemia",
        ],
        required_groups=[
            EvidenceGroup(
                operator="OR",
                keys=["cardiac_troponin_ng_ml", "hs_troponin_i_ng_ml", "hs_troponin_t_ng_ml", "troponin_i_ng_ml", "troponin_t_ng_ml", "cardiac_troponin_assay"],
                description="troponin",
            ),
        ],
        supportive_groups=[
            EvidenceGroup(operator="OR", keys=["resting_ecg", "ecg", "12_lead_ecg"], description="resting_ecg"),
            EvidenceGroup(operator="OR", keys=["symptoms", "chest_pain", "dyspnea"], description="symptom_report"),
        ],
        exempt_keywords=[
            "paternal",
            "maternal",
            "family history",
            "father",
            "mother",
            "sibling",
            "past history",
            "chronic",
            "non-ischemic",
            "history of myocardial",
            "no evidence of",
            "rules out",
            "rule out",
            "unlikely",
            "cannot be ruled out",
            "remote",
        ],
        confidence_cap=40.0,
        guideline_reference="Fourth Universal Definition of MI (ESC/ACC/AHA/WHF 2018) & ESC 2023 ACS Guidelines",
        rationale="Objective confirmation or exclusion of acute myocardial necrosis strictly mandates serial cardiac troponin; resting ECG alone cannot confirm or exclude acute necrosis.",
    ),
    ClinicalEvidenceRequirement(
        requirement_id="REQ-UNSTABLE-ANGINA",
        clinical_domain="ischemia",
        trigger_keywords=[
            "unstable angina",
        ],
        required_groups=[
            EvidenceGroup(operator="OR", keys=["resting_ecg", "ecg"], description="resting_ecg"),
        ],
        supportive_groups=[
            EvidenceGroup(operator="OR", keys=["cardiac_troponin_ng_ml", "hs_troponin_i_ng_ml", "hs_troponin_t_ng_ml"], description="troponin"),
            EvidenceGroup(operator="OR", keys=["symptoms", "chest_pain"], description="symptom_report"),
        ],
        exempt_keywords=[
            "family history",
            "stable angina",
            "chronic",
            "history of",
            "no evidence of",
        ],
        confidence_cap=45.0,
        guideline_reference="AHA/ACC 2014 / ESC 2023 NSTE-ACS Guideline",
        rationale="Unstable angina presentation is characterized by acute myocardial ischemia without troponin elevation; mandates objective ECG and symptom evaluation.",
    ),
    ClinicalEvidenceRequirement(
        requirement_id="REQ-ACUTE-HEART-FAILURE",
        clinical_domain="heart_failure",
        trigger_keywords=[
            "acute heart failure",
            "acute decompensated heart failure",
            "cardiogenic pulmonary edema",
            "acute decompensation",
            "pulmonary edema",
        ],
        required_groups=[
            EvidenceGroup(
                operator="OR",
                keys=["bnp_pg_ml", "nt_pro_bnp_pg_ml", "echocardiogram", "chest_xray_pulmonary_congestion"],
                description="natriuretic_peptide",
            ),
        ],
        supportive_groups=[
            EvidenceGroup(operator="OR", keys=["resting_ecg", "ecg"], description="resting_ecg"),
            EvidenceGroup(operator="OR", keys=["symptoms", "dyspnea", "breathlessness"], description="symptom_report"),
            EvidenceGroup(operator="OR", keys=["serum_creatinine_mg_dl", "egfr_ml_min"], description="kidney"),
        ],
        exempt_keywords=[
            "family history",
            "chronic heart failure",
            "stable",
            "history of heart failure",
            "no evidence of",
        ],
        confidence_cap=35.0,
        guideline_reference="ESC/HFA 2021 Heart Failure Guidelines / ACC/AHA/HFSA 2022",
        rationale="Acute decompensated heart failure evaluation requires objective circulating natriuretic peptide (BNP >= 100 pg/mL or NT-proBNP >= 300 pg/mL) or imaging evidence of pulmonary congestion alongside clinical symptoms.",
    ),
    ClinicalEvidenceRequirement(
        requirement_id="REQ-CHRONIC-HEART-FAILURE",
        clinical_domain="heart_failure",
        trigger_keywords=[
            "chronic heart failure",
            "congestive heart failure",
            "hfref",
            "hfpef",
            "stable heart failure",
            "heart failure",
        ],
        required_groups=[
            EvidenceGroup(
                operator="OR",
                keys=["bnp_pg_ml", "nt_pro_bnp_pg_ml", "echocardiogram_lvef_percent", "ejection_fraction", "lvef"],
                description="natriuretic_peptide",
            ),
        ],
        supportive_groups=[
            EvidenceGroup(operator="OR", keys=["echocardiogram_lvef_percent", "ejection_fraction"], description="cardiac_function"),
            EvidenceGroup(operator="OR", keys=["serum_creatinine_mg_dl", "egfr_ml_min"], description="kidney"),
            EvidenceGroup(operator="OR", keys=["resting_ecg"], description="resting_ecg"),
        ],
        exempt_keywords=[
            "family history",
            "risk of heart failure",
            "no evidence of",
        ],
        confidence_cap=45.0,
        guideline_reference="ACC/AHA/HFSA 2022 Guideline for the Management of Heart Failure",
        rationale="Chronic heart failure classification (HFrEF vs HFpEF) requires objective assessment of left ventricular ejection fraction and natriuretic peptides in clinical context.",
    ),
    ClinicalEvidenceRequirement(
        requirement_id="REQ-DKA",
        clinical_domain="glycemia",
        trigger_keywords=[
            "diabetic ketoacidosis",
            "dka",
            "ketoacidosis",
        ],
        required_groups=[
            EvidenceGroup(
                operator="OR",
                keys=["fasting_blood_glucose_mg_dl", "random_blood_glucose_mg_dl", "blood_glucose_mg_dl", "documented_diabetes", "type_1_diabetes", "type_2_diabetes", "sglt2_inhibitor_use"],
                description="glycemia_acute",
            ),
            EvidenceGroup(
                operator="OR",
                keys=["beta_hydroxybutyrate_mmol_l", "blood_ketones_mmol_l", "serum_ketones_mmol_l", "urine_ketones"],
                description="ketones",
            ),
            EvidenceGroup(
                operator="OR",
                keys=["blood_ph", "arterial_ph", "venous_ph", "serum_bicarbonate_mmol_l", "bicarbonate_mEq_L"],
                description="acid_base",
            ),
        ],
        supportive_groups=[
            EvidenceGroup(operator="OR", keys=["serum_creatinine_mg_dl", "egfr_ml_min", "blood_urea_nitrogen_mg_dl"], description="kidney"),
            EvidenceGroup(operator="OR", keys=["serum_osmolality_mosm_kg", "effective_osmolality_mosm_kg"], description="osmolality"),
        ],
        exempt_keywords=[
            "family history",
            "history of dka",
            "past dka",
            "resolved dka",
            "no evidence of",
        ],
        confidence_cap=35.0,
        guideline_reference="ADA Standards of Care 2024 / ADA/EASD Consensus: Hyperglycemic Crises in Adults",
        rationale="Diagnostic confirmation of DKA mandates documented hyperketonemia (beta-hydroxybutyrate >= 3.0 mmol/L) AND metabolic acidosis (pH < 7.30 or bicarbonate <= 18 mEq/L) concurrent with hyperglycemia or known diabetes (euglycemic DKA). Missing ketones or acid-base testing cannot confirm DKA.",
    ),
    ClinicalEvidenceRequirement(
        requirement_id="REQ-HHS",
        clinical_domain="glycemia",
        trigger_keywords=[
            "hyperglycemic hyperosmolar",
            "hhs",
            "hyperosmolar hyperglycemic",
            "honk",
        ],
        required_groups=[
            EvidenceGroup(
                operator="OR",
                keys=["fasting_blood_glucose_mg_dl", "random_blood_glucose_mg_dl", "blood_glucose_mg_dl"],
                description="glycemia_acute",
            ),
            EvidenceGroup(
                operator="OR",
                keys=["serum_osmolality_mosm_kg", "effective_osmolality_mosm_kg"],
                description="osmolality",
            ),
        ],
        supportive_groups=[
            EvidenceGroup(operator="OR", keys=["beta_hydroxybutyrate_mmol_l", "blood_ketones_mmol_l"], description="ketones"),
            EvidenceGroup(operator="OR", keys=["blood_ph", "arterial_ph", "venous_ph", "serum_bicarbonate_mmol_l"], description="acid_base"),
            EvidenceGroup(operator="OR", keys=["serum_creatinine_mg_dl", "blood_urea_nitrogen_mg_dl"], description="kidney"),
        ],
        exempt_keywords=[
            "family history",
            "history of hhs",
            "resolved hhs",
            "no evidence of",
        ],
        confidence_cap=35.0,
        guideline_reference="ADA Standards of Care 2024: Hyperglycemic Crises in Adults",
        rationale="Diagnostic confirmation of HHS mandates marked hyperglycemia (>600 mg/dL) and effective hyperosmolality (>320 mOsm/kg) in the absence of significant ketoacidosis.",
    ),
    ClinicalEvidenceRequirement(
        requirement_id="REQ-SEVERE-HYPERGLYCEMIA",
        clinical_domain="glycemia",
        trigger_keywords=[
            "severe hyperglycemia",
            "marked hyperglycemia",
            "uncontrolled hyperglycemia",
            "severe glucotoxicity",
        ],
        required_groups=[
            EvidenceGroup(
                operator="OR",
                keys=["fasting_blood_glucose_mg_dl", "random_blood_glucose_mg_dl", "blood_glucose_mg_dl"],
                description="glycemia_acute",
            ),
        ],
        supportive_groups=[
            EvidenceGroup(operator="OR", keys=["beta_hydroxybutyrate_mmol_l", "blood_ketones_mmol_l"], description="ketones"),
            EvidenceGroup(operator="OR", keys=["serum_creatinine_mg_dl"], description="kidney"),
        ],
        exempt_keywords=[
            "family history",
            "chronic",
            "history of",
            "no evidence of",
        ],
        confidence_cap=40.0,
        guideline_reference="ADA 2024 Standards of Care: Glycemic Targets",
        rationale="Severe hyperglycemia without established DKA/HHS confirms elevated blood glucose but cannot confirm metabolic crisis without ketone/osmolality biomarkers.",
    ),
    ClinicalEvidenceRequirement(
        requirement_id="REQ-CHRONIC-DIABETES",
        clinical_domain="glycemia",
        trigger_keywords=[
            "type 2 diabetes",
            "t2d",
            "diabetes mellitus",
            "poor glycemic control",
            "chronic diabetes",
        ],
        required_groups=[
            EvidenceGroup(
                operator="OR",
                keys=["hba1c_percent", "fasting_blood_glucose_mg_dl", "random_blood_glucose_mg_dl", "documented_diabetes"],
                description="glycemia",
            ),
        ],
        supportive_groups=[
            EvidenceGroup(operator="OR", keys=["serum_creatinine_mg_dl", "egfr_ml_min"], description="kidney"),
        ],
        exempt_keywords=[
            "family history",
            "father",
            "mother",
            "prediabetes",
            "pre-diabetes",
            "no evidence of",
        ],
        confidence_cap=50.0,
        guideline_reference="ADA 2024 Standards of Care: Diagnosis and Classification of Diabetes",
        rationale="Assessment of chronic diabetes or glycemic control accepts HbA1c (>=6.5%) or fasting glucose (>=126 mg/dL); HbA1c alone cannot confirm acute metabolic emergencies.",
    ),
    ClinicalEvidenceRequirement(
        requirement_id="REQ-HYPERTENSIVE-EMERGENCY",
        clinical_domain="hemodynamics",
        trigger_keywords=[
            "hypertensive emergency",
            "malignant hypertension",
            "hypertensive crisis with target organ",
        ],
        required_groups=[
            EvidenceGroup(
                operator="OR",
                keys=["systolic_bp", "diastolic_bp", "blood_pressure"],
                description="blood_pressure",
            ),
            EvidenceGroup(
                operator="OR",
                keys=["target_organ_damage", "serum_creatinine_mg_dl", "cardiac_troponin_ng_ml", "hs_troponin_i_ng_ml", "pulmonary_edema_confirmed"],
                description="target_organ_damage",
            ),
        ],
        supportive_groups=[
            EvidenceGroup(operator="OR", keys=["serum_creatinine_mg_dl", "egfr_ml_min"], description="kidney"),
            EvidenceGroup(operator="OR", keys=["cardiac_troponin_ng_ml", "hs_troponin_i_ng_ml"], description="troponin"),
            EvidenceGroup(operator="OR", keys=["resting_ecg"], description="resting_ecg"),
        ],
        exempt_keywords=[
            "history of hypertension",
            "chronic hypertension",
            "essential hypertension",
            "hypertensive urgency",
            "asymptomatic hypertension",
            "no evidence of",
        ],
        confidence_cap=35.0,
        guideline_reference="ACC/AHA 2017 / ESC 2018 / ESH 2023 Guidelines for Arterial Hypertension",
        rationale="Hypertensive emergency strictly mandates severe blood pressure elevation (typically >=180/120 mmHg) CONCURRENT WITH acute, progressive target-organ damage (heart, brain, kidney, retina, aorta). Severe BP alone without organ damage is hypertensive urgency.",
    ),
    ClinicalEvidenceRequirement(
        requirement_id="REQ-HYPERTENSIVE-URGENCY",
        clinical_domain="hemodynamics",
        trigger_keywords=[
            "hypertensive urgency",
            "severe asymptomatic hypertension",
            "severe stage 2",
            "hypertensive crisis",
        ],
        required_groups=[
            EvidenceGroup(
                operator="OR",
                keys=["systolic_bp", "diastolic_bp", "blood_pressure"],
                description="blood_pressure",
            ),
        ],
        supportive_groups=[
            EvidenceGroup(operator="OR", keys=["serum_creatinine_mg_dl", "egfr_ml_min"], description="kidney"),
            EvidenceGroup(operator="OR", keys=["resting_ecg"], description="resting_ecg"),
        ],
        exempt_keywords=[
            "history of hypertension",
            "chronic hypertension",
            "essential hypertension",
            "no evidence of",
        ],
        confidence_cap=45.0,
        guideline_reference="ACC/AHA 2017 Guidelines for High Blood Pressure in Adults",
        rationale="Hypertensive urgency represents severe BP elevation without acute target-organ damage; mandates blood pressure verification while monitoring for subclinical organ involvement.",
    ),
]


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
            ml=ml,
        )

        # 4. Calculate Global Epistemic Doubt Score [0.0, 1.0]
        global_doubt = self._calculate_global_epistemic_doubt(domain_doubts, contradiction_matrix, debate_transcript, missing_summary)

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
        """Extract structured claims from agent outputs, validating numeric inputs strictly."""
        claims: List[Dict[str, Any]] = []

        if agent_outputs:
            for idx, out in enumerate(agent_outputs):
                if isinstance(out, dict):
                    agent_id = (
                        out.get("agent_role")
                        or out.get("agent_name")
                        or out.get("agent_id")
                        or f"Specialist_{idx}"
                    )
                    confidence = out.get("confidence", 50.0)
                    findings = out.get("findings", [])
                    recommendations = out.get("recommendations", [])
                    narrative = out.get("summary", "")
                else:
                    agent_id = (
                        getattr(out, "agent_name", None)
                        or getattr(out, "agent_role", None)
                        or getattr(out, "agent_id", f"Specialist_{idx}")
                    )
                    confidence = getattr(out, "confidence", 50.0)
                    findings = getattr(out, "findings", [])
                    recommendations = getattr(out, "recommendations", [])
                    narrative = getattr(out, "summary", "")

                # Strict numeric validation: reject NaN / Inf explicitly
                try:
                    conf_float = float(confidence)
                except (ValueError, TypeError) as e:
                    raise ValueError(f"Agent confidence score must be a valid numeric float, got: {confidence}") from e

                if math.isnan(conf_float) or math.isinf(conf_float):
                    raise ValueError(f"Agent confidence score cannot be NaN or Infinite: {confidence}")

                if conf_float < 0.0 or conf_float > 100.0:
                    raise ValueError(f"Agent confidence score must be in range [0.0, 100.0], got: {conf_float}")

                claim_statements: List[str] = []
                if isinstance(findings, str) and findings.strip():
                    claim_statements.append(findings.strip())
                elif isinstance(findings, (list, tuple)):
                    claim_statements.extend([str(f).strip() for f in findings if str(f).strip()])
                elif narrative:
                    claim_statements.append(str(narrative).strip())
                elif recommendations and isinstance(recommendations, (list, tuple)) and recommendations[0]:
                    claim_statements.append(str(recommendations[0]).strip())
                else:
                    claim_statements.append(f"Clinical evaluation by {agent_id}")

                for c_idx, stmt in enumerate(claim_statements):
                    domain = self._infer_clinical_domain(stmt, agent_id)
                    claims.append({
                        "agent_id": str(agent_id),
                        "claim_id": f"claim_{agent_id}_{idx}_{c_idx}",
                        "claim_text": stmt,
                        "clinical_domain": domain,
                        "original_confidence": conf_float,
                    })

        # If no agent outputs, extract from debate transcript challenges
        if not claims and debate_transcript and debate_transcript.challenges:
            for ch in debate_transcript.challenges:
                domain = self._infer_clinical_domain(ch.challenged_claim, ch.challenged_agent)
                claims.append({
                    "agent_id": ch.challenged_agent,
                    "claim_id": f"claim_ch_{ch.challenge_id}",
                    "claim_text": ch.challenged_claim,
                    "clinical_domain": domain,
                    "original_confidence": 75.0,  # Baseline pre-debate confidence
                })

        # Default rich fallback panel if empty
        if not claims:
            claims = [
                {
                    "agent_id": "Symptom Analysis Specialist",
                    "claim_id": "claim_sym_0",
                    "claim_text": "Possible acute myocardial ischemia",
                    "clinical_domain": "ischemia",
                    "original_confidence": 85.0,
                },
                {
                    "agent_id": "Medical History Specialist",
                    "claim_id": "claim_hist_0",
                    "claim_text": "Patient on consistent statin therapy with controlled hyperlipidemia",
                    "clinical_domain": "lipidology",
                    "original_confidence": 90.0,
                },
                {
                    "agent_id": "Laboratory Biomarker Specialist",
                    "claim_id": "claim_lab_0",
                    "claim_text": "Cardiac troponin strictly normal, but severe hypercholesterolemia (LDL 195.0 mg/dL)",
                    "clinical_domain": "lipidology",
                    "original_confidence": 95.0,
                },
                {
                    "agent_id": "Risk Prediction Ensemble Specialist",
                    "claim_id": "claim_risk_0",
                    "claim_text": "High 10-year cardiovascular disease risk probability",
                    "clinical_domain": "cardiovascular_risk",
                    "original_confidence": 80.0,
                },
            ]

        return claims

    def _infer_clinical_domain(self, text: str, agent_role: str) -> str:
        """Infer clinical domain from claim narrative and agent role with explicit priority."""
        text_lower = text.lower()
        role_lower = agent_role.lower()

        # Explicit lipidology priority
        if any(kw in text_lower for kw in ["ldl", "cholesterol", "statin", "lipid", "atorvastatin", "triglyceride"]):
            return "lipidology"

        # Domain keyword inspection
        for domain, keywords in DOMAIN_KEYWORDS.items():
            if any(kw in text_lower for kw in keywords):
                return domain

        # Role fallback
        if "symptom" in role_lower:
            return "ischemia"
        if "lab" in role_lower:
            return "lipidology"
        if "history" in role_lower:
            return "hemodynamics"
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

        # Strict input verification
        raw_orig = float(claim_info["original_confidence"])
        if math.isnan(raw_orig) or math.isinf(raw_orig):
            raise ValueError(f"Invalid non-finite confidence: {raw_orig}")
        original_conf = max(0.0, min(100.0, raw_orig))

        # Trace related contradiction issues
        related_issues: List[ContradictionIssue] = []
        if contradiction_matrix and contradiction_matrix.issues:
            for issue in contradiction_matrix.issues:
                if agent_id in issue.conflicting_agents or self._issue_matches_domain(issue, domain):
                    related_issues.append(issue)

        # Trace debate outcome for this claim
        debate_outcome: Optional[str] = None
        concession_reason: Optional[str] = None
        revised_claim_text: Optional[str] = None
        is_withdrawn = False

        if debate_transcript and debate_transcript.challenges:
            for ch in debate_transcript.challenges:
                if ch.challenged_agent == agent_id and (domain == self._infer_clinical_domain(ch.challenged_claim, agent_id)):
                    if ch.status == ChallengeStatus.CONCEDED:
                        debate_outcome = "conceded"
                        reb = next((r for r in debate_transcript.rebuttals if r.challenge_id == ch.challenge_id), None)
                        if reb:
                            concession_reason = reb.concession_reason
                            if getattr(reb, "is_withdrawn", False):
                                is_withdrawn = True
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

        effective_claim_text = revised_claim_text if revised_claim_text else claim_text

        # ---------------------------------------------------------------------
        # 1. Evidence Grounding Multiplier (+0% to +15%) with Directionality & Deduplication
        # ---------------------------------------------------------------------
        (
            grounding_adj,
            verified_evidence,
            conflicting_evidence,
            quality_caveats,
            evidence_classifications,
            evidence_states,
            grounding_notes,
        ) = self._calculate_evidence_grounding(
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
            verified_evidence=verified_evidence,
        )

        # ---------------------------------------------------------------------
        # 3. Intermediate Confidence Calculation (Pure Functional Recalculation)
        # ---------------------------------------------------------------------
        if debate_outcome == "conceded" and not revised_claim_text:
            # Conceded claim without revision receives zero grounding credit and is bounded
            # reflecting admission of diagnostic error
            intermediate_conf = min(30.0, max(10.0, original_conf - 40.0))
        else:
            # Clean functional recalculation from original confidence + G_i - P_i
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
            effective_cap = cap_val if cap_val is not None else self.missing_evidence_cap
            final_conf = min(intermediate_conf, effective_cap)
        else:
            effective_cap = None
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
        if cap_applied and effective_cap is not None:
            explanation += f"Capped at {effective_cap:.1f}% due to missing essential evidence: {', '.join(missing_keys)}. "
        if debate_outcome:
            explanation += f"Debate resolution: {debate_outcome}. "
        if conflicting_evidence:
            explanation += f"Conflicting evidence noted: {', '.join(conflicting_evidence)}. "
        explanation += f"Final confidence: {final_conf:.1f}%."

        if final_conf >= 100.0:
            explanation += " (Maximum heuristic claim support; does not imply absolute clinical certainty)."

        return ClaimRecalibrationRecord(
            agent_id=agent_id,
            claim_id=claim_id,
            claim_text=effective_claim_text,
            clinical_domain=domain,
            original_confidence=original_conf,
            evidence_grounding_adjustment=grounding_adj,
            contradiction_penalty=penalty_adj,
            missing_evidence_cap_applied=cap_applied,
            missing_evidence_cap_value=effective_cap if cap_applied else None,
            missing_evidence_details=missing_keys,
            recalibrated_confidence=intermediate_conf,
            final_confidence=final_conf,
            claim_support_score=final_conf,
            heuristic_support_score=final_conf,
            grounding_evidence_references=verified_evidence,
            conflicting_evidence_references=conflicting_evidence,
            evidence_quality_caveats=quality_caveats,
            evidence_classifications=evidence_classifications,
            evidence_states=evidence_states,
            contradiction_issue_ids=issue_ids,
            debate_outcome=debate_outcome,
            concession_reason=concession_reason,
            is_withdrawn=is_withdrawn,
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

    def _classify_claim_intent(self, claim_text: str) -> Dict[str, Any]:
        """Classify clinical claim intent with clause segmentation, negation scope, and temporality (A7)."""
        claim_lower = claim_text.lower().strip()

        # Split into clauses by common conjunctions
        delimiters = [", but ", "; but ", ", however ", "; however ", ", although ", ". ", "; "]
        clauses = [claim_lower]
        for d in delimiters:
            new_clauses = []
            for c in clauses:
                new_clauses.extend(c.split(d))
            clauses = [c.strip() for c in new_clauses if c.strip()]

        negation_markers = [
            "no evidence of", "rules out", "ruled out", "negative for", "absence of",
            "unlikely", "not consistent with", "without evidence", "excludes", "excluded",
            "normal troponin", "troponin strictly normal", "non-ischemic", "no acute",
            "patient denies", "denies previous", "denies history", "denies",
        ]
        historical_markers = [
            "history of", "past medical history", "past history", "prior", "previous",
            "remote", "resolved", "documented in 20", "chronic history",
        ]
        family_history_markers = [
            "family history", "father", "mother", "paternal", "maternal", "sibling",
            "brother", "sister", "parents",
        ]
        suspected_markers = [
            "possible", "probable", "suspected", "presumed", "differential",
            "potential", "cannot exclude", "concern for", "borderline", "cannot be ruled out",
            "cannot rule out",
        ]
        confirmed_markers = [
            "confirmed", "established", "definite", "active acute", "diagnosed with",
            "severe acute", "overt",
        ]

        is_negated = False
        is_historical = False
        is_family_history = False
        is_patient_reported = False
        is_suspected = False
        is_confirmed = False
        is_rule_out_instruction = False
        is_uncertain = False

        # Rule out instruction: e.g. "Rule out acute MI"
        if claim_lower.startswith("rule out ") or claim_lower.startswith("r/o "):
            is_rule_out_instruction = True
            is_uncertain = True

        # Check for "cannot be ruled out" / "cannot rule out" / "cannot exclude"
        if "cannot be ruled out" in claim_lower or "cannot rule out" in claim_lower or "cannot exclude" in claim_lower:
            is_uncertain = True
            is_suspected = True

        if any(m in claim_lower for m in family_history_markers):
            is_family_history = True

        if any(m in claim_lower for m in ["patient denies", "patient reports", "patient states"]):
            is_patient_reported = True

        # Negation check (excluding "cannot be ruled out")
        has_negation_marker = any(m in claim_lower for m in negation_markers)
        if has_negation_marker and "cannot be ruled out" not in claim_lower and "cannot rule out" not in claim_lower:
            is_negated = True

        if any(m in claim_lower for m in historical_markers) and not is_family_history:
            is_historical = True

        if any(m in claim_lower for m in suspected_markers):
            is_suspected = True
            is_uncertain = True

        if any(m in claim_lower for m in confirmed_markers) and not is_negated:
            is_confirmed = True

        # Determine primary intent category
        if is_rule_out_instruction:
            intent_cat = "RULE_OUT_INSTRUCTION"
        elif is_family_history:
            intent_cat = "FAMILY_HISTORY"
        elif is_patient_reported and is_negated:
            intent_cat = "PATIENT_REPORTED_HISTORY"
        elif is_negated and is_historical:
            intent_cat = "HISTORICAL_DIAGNOSIS"
        elif is_negated:
            intent_cat = "EXPLICIT_NEGATION"
        elif is_uncertain or is_suspected:
            if is_historical:
                intent_cat = "HISTORICAL_DIAGNOSIS"
            else:
                intent_cat = "CURRENT_SUSPECTED_DIAGNOSIS"
        elif is_historical:
            intent_cat = "HISTORICAL_DIAGNOSIS"
        elif is_confirmed:
            intent_cat = "CURRENT_POSITIVE_DIAGNOSIS"
        else:
            intent_cat = "CURRENT_POSITIVE_DIAGNOSIS"

        has_contrastive_clause = any(d in claim_lower for d in [", but ", "; but ", ", however ", "; however ", ", although ", " but ", " however ", " although "])

        if has_contrastive_clause and clauses:
            primary_text = clauses[0]
            primary_negated = any(m in primary_text for m in negation_markers) and "cannot be ruled out" not in primary_text and "cannot rule out" not in primary_text
            if not primary_negated and is_negated:
                is_negated = False
                intent_cat = "CURRENT_POSITIVE_DIAGNOSIS" if is_confirmed else "CURRENT_SUSPECTED_DIAGNOSIS"

        return {
            "intent_category": intent_cat,
            "is_negated": is_negated,
            "is_historical": is_historical,
            "is_family_history": is_family_history,
            "is_patient_reported": is_patient_reported,
            "is_suspected": is_suspected,
            "is_confirmed": is_confirmed,
            "is_rule_out": is_rule_out_instruction,
            "is_rule_out_instruction": is_rule_out_instruction,
            "has_contrastive_clause": bool(has_contrastive_clause),
            "is_uncertain": is_uncertain,
            "primary_clause": clauses[0] if clauses else claim_lower,
            "clauses": [{"clause_text": c} for c in clauses],
        }

    def _resolve_troponin_cutoff(
        self,
        labs: Dict[str, Any],
        sex: Optional[str] = None,
    ) -> Tuple[float, str, bool, Optional[str]]:
        """Resolve assay-specific 99th percentile upper reference limit (URL) for cardiac troponin (A5)."""
        lab_url = labs.get("troponin_url_ng_ml") or labs.get("lab_reference_limit") or labs.get("reference_range_upper")
        if lab_url is not None:
            try:
                url_float = float(lab_url)
                return url_float, "ng/mL", (url_float <= 0.03), "Laboratory-Reported Reference URL"
            except (ValueError, TypeError):
                pass

        assay_raw = str(labs.get("cardiac_troponin_assay") or labs.get("troponin_assay") or labs.get("assay") or "").lower()
        unit_raw = str(labs.get("cardiac_troponin_unit") or labs.get("troponin_unit") or "ng/ml").lower()

        profile_key = None
        if assay_raw in TROPONIN_ASSAY_PROFILES:
            profile_key = assay_raw
        elif "abbott" in assay_raw or "architect" in assay_raw or "alinity" in assay_raw:
            profile_key = "hs_ctni_abbott"
        elif "roche" in assay_raw or "elecsys" in assay_raw or "hs_ctnt" in assay_raw or "hs-ctnt" in assay_raw:
            profile_key = "hs_ctnt_roche"
        elif "siemens" in assay_raw or "atellica" in assay_raw:
            profile_key = "hs_ctni_siemens"
        elif "beckman" in assay_raw or "access" in assay_raw:
            profile_key = "hs_ctni_beckman"
        elif "conventional_ctnt" in assay_raw:
            profile_key = "conventional_ctnt"
        elif "conventional" in assay_raw or "standard" in assay_raw:
            profile_key = "conventional_ctni"
        elif "hs" in assay_raw or labs.get("hs_troponin_i_ng_ml") is not None or labs.get("hs_troponin_t_ng_ml") is not None:
            profile_key = "hs_ctni_abbott"

        resolved_sex = str(sex or labs.get("sex") or labs.get("gender") or "").lower()
        is_female = resolved_sex in ["female", "f", "woman"]
        is_male = resolved_sex in ["male", "m", "man"]
        is_ng_l = "ng/l" in unit_raw or "pg/ml" in unit_raw

        if profile_key and profile_key in TROPONIN_ASSAY_PROFILES:
            prof = TROPONIN_ASSAY_PROFILES[profile_key]
            is_hs = "hs" in prof["type"].lower()
            if is_ng_l:
                if is_female and "url_female_ng_l" in prof:
                    return prof["url_female_ng_l"], "ng/L", is_hs, f"{prof['name']} (Female 99th %ile URL)"
                elif is_male and "url_male_ng_l" in prof:
                    return prof["url_male_ng_l"], "ng/L", is_hs, f"{prof['name']} (Male 99th %ile URL)"
                return prof["url_overall_ng_l"], "ng/L", is_hs, prof["name"]
            else:
                if is_female and "url_female_ng_ml" in prof:
                    return prof["url_female_ng_ml"], "ng/mL", is_hs, f"{prof['name']} (Female 99th %ile URL)"
                elif is_male and "url_male_ng_ml" in prof:
                    return prof["url_male_ng_ml"], "ng/mL", is_hs, f"{prof['name']} (Male 99th %ile URL)"
                return prof["url_ng_ml"], "ng/mL", is_hs, prof["name"]

        is_hs_key = labs.get("hs_troponin_i_ng_ml") is not None or labs.get("hs_troponin_t_ng_ml") is not None or "hs" in assay_raw
        if is_hs_key:
            if is_female:
                return 0.009, "ng/mL", True, "Generic hs-cTn (Female URL, Platform Unspecified)"
            elif is_male:
                return 0.0155, "ng/mL", True, "Generic hs-cTn (Male URL, Platform Unspecified)"
            return 0.014, "ng/mL", True, "Generic hs-cTn"
        else:
            return 0.04, "ng/mL", False, "Conventional cTn"

    def _validate_serial_troponin_protocol(self, labs: Dict[str, Any]) -> Tuple[str, List[str], bool]:
        """Validate serial cardiac troponin testing against protocol standards (ESC 0h/1h, 0h/2h, 0h/3h) (A6)."""
        caveats: List[str] = []
        serial_completed = bool(labs.get("serial_troponin_completed"))
        assay_mismatch = bool(labs.get("troponin_assay_mismatch") or labs.get("assay_mismatch"))
        sample_interval = labs.get("serial_sample_interval_hours")
        timestamps = labs.get("serial_timestamps") or labs.get("sample_timestamps")

        if assay_mismatch:
            caveats.append(
                "Serial troponin assay mismatch (conventional vs high-sensitivity or disparate manufacturers); "
                "serial delta cannot be computed across disparate assay technologies."
            )
            return SerialTroponinValidationStatus.INCOMPATIBLE_ASSAY.value, caveats, False

        if timestamps and isinstance(timestamps, (list, tuple)) and len(timestamps) >= 2:
            try:
                def _parse_ts(ts_raw: Any) -> datetime:
                    dt = datetime.fromisoformat(str(ts_raw).replace("Z", "+00:00"))
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    else:
                        dt = dt.astimezone(timezone.utc)
                    return dt

                t0 = _parse_ts(timestamps[0])
                t1 = _parse_ts(timestamps[1])
                delta_h = (t1 - t0).total_seconds() / 3600.0
                if delta_h < 0:
                    caveats.append("Serial troponin sample timestamps in reverse chronological order.")
                    return SerialTroponinValidationStatus.INVALID_SEQUENCE.value, caveats, False
                if delta_h < 0.8:
                    caveats.append(
                        f"Serial troponin interval ({delta_h:.2f}h < 1 hour) is insufficient per ESC 0h/1h or 0h/3h protocol to rule in or rule out acute myocardial necrosis."
                    )
                    return SerialTroponinValidationStatus.INSUFFICIENT_TIMING.value, caveats, False
            except (ValueError, TypeError):
                caveats.append("Serial troponin sample timestamps malformed.")

        if sample_interval is not None:
            try:
                interval_float = float(sample_interval)
                if interval_float < 1.0:
                    caveats.append(
                        "Serial troponin interval < 1 hour is insufficient per ESC 0h/1h or 0h/3h protocol to rule in or rule out acute myocardial necrosis."
                    )
                    return SerialTroponinValidationStatus.INSUFFICIENT_TIMING.value, caveats, False
            except (ValueError, TypeError):
                pass

        if not serial_completed:
            return SerialTroponinValidationStatus.INCOMPLETE_SERIAL_SERIES.value, caveats, False

        return SerialTroponinValidationStatus.VALID_SERIAL_SERIES.value, caveats, True

    def _evaluate_target_organ_damage(
        self,
        labs: Dict[str, Any],
        history: Dict[str, Any],
        symptoms: Dict[str, Any],
    ) -> Tuple[TargetOrganDamageState, List[str], str]:
        """Evaluate acute target-organ damage status in severe hypertension presentations (A3)."""
        markers: List[str] = []

        if labs.get("target_organ_damage") is True:
            markers.append("Documented acute target-organ damage")

        creat = labs.get("serum_creatinine_mg_dl")
        baseline_creat = labs.get("baseline_creatinine_mg_dl")
        if creat is not None:
            try:
                c_num = float(creat)
                if baseline_creat is not None and (c_num - float(baseline_creat)) >= 0.3:
                    markers.append(f"Acute kidney injury (creatinine delta +{(c_num - float(baseline_creat)):.2f} mg/dL)")
                elif c_num >= 2.0:
                    markers.append(f"Acute kidney injury (serum creatinine {c_num:.1f} mg/dL)")
            except (ValueError, TypeError):
                pass

        troponin = labs.get("cardiac_troponin_ng_ml") or labs.get("hs_troponin_i_ng_ml") or labs.get("hs_troponin_t_ng_ml")
        if troponin is not None:
            try:
                t_num = float(troponin)
                cutoff, _, _, _ = self._resolve_troponin_cutoff(labs)
                if t_num > cutoff:
                    markers.append(f"Acute myocardial injury (troponin {t_num} > {cutoff})")
            except (ValueError, TypeError):
                pass

        if labs.get("pulmonary_edema_confirmed") is True or labs.get("pulmonary_edema") is True:
            markers.append("Acute pulmonary edema (cardiogenic)")

        ecg = str(labs.get("resting_ecg") or "").lower()
        if any(k in ecg for k in ["st_elevation", "acute_ischemia", "st_depression"]):
            markers.append("Acute ischemic ECG abnormalities")

        if markers:
            return TargetOrganDamageState.PRESENT, markers, f"Acute target-organ damage present: {', '.join(markers)}"

        has_tests = (
            labs.get("serum_creatinine_mg_dl") is not None
            or labs.get("cardiac_troponin_ng_ml") is not None
            or labs.get("hs_troponin_i_ng_ml") is not None
            or labs.get("resting_ecg") is not None
            or labs.get("target_organ_damage") is False
        )

        if not has_tests:
            return (
                TargetOrganDamageState.UNKNOWN,
                [],
                "Target-organ damage status UNKNOWN: Renal and cardiac biomarkers not evaluated in severe hypertension presentation.",
            )

        sym_list = [str(s).lower() for s in symptoms.get("symptoms", [])]
        if any(s in ["chest_pain", "dyspnea", "vision_loss", "confusion", "neurological_deficit"] for s in sym_list):
            return (
                TargetOrganDamageState.SUSPECTED,
                ["Concerning symptoms with pending confirmatory biomarker panels"],
                "Acute target-organ damage SUSPECTED based on presenting clinical symptoms; mandates emergency confirmation.",
            )

        return TargetOrganDamageState.ABSENT, [], "No acute target-organ damage identified across evaluated laboratory endpoints."

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
    ) -> Tuple[float, List[str], List[str], List[str], Dict[str, str], Dict[str, str], str]:
        """Compute positive evidence grounding multiplier (+0% to +15%) with analyte deduplication and directional validation.

        Returns:
            Tuple of (grounding_adj, verified_evidence, conflicting_evidence, quality_caveats,
                      evidence_classifications, evidence_states, notes)
        """
        # Rule: Unsupported or conceded claims receive zero grounding bonus
        if debate_outcome in ["unsupported", "conceded"]:
            return 0.0, [], [], [], {}, {}, f"No grounding awarded for {debate_outcome} claim"

        claim_lower = claim_text.lower()
        verified_evidence: List[str] = []
        conflicting_evidence: List[str] = []
        quality_caveats: List[str] = []
        evidence_classifications: Dict[str, str] = {}
        evidence_states: Dict[str, str] = {}
        credited_analyte_groups: Set[str] = set()

        # Quality flag inspection
        has_locale_ambiguity = bool(labs.get("flag_locale_ambiguity"))
        has_needs_review = bool(labs.get("needs_review"))
        has_stale_evidence = bool(labs.get("is_stale") or labs.get("stale_evidence"))
        has_provenance_issue = bool(labs.get("invalid_provenance") or labs.get("provenance_issue"))

        if has_locale_ambiguity:
            quality_caveats.append("Potential locale separator ambiguity noted in laboratory extraction.")
        if has_needs_review:
            quality_caveats.append("Laboratory result marked NEEDS_REVIEW; verification pending.")
        if has_stale_evidence:
            quality_caveats.append("Biomarker records exceed clinically acceptable freshness window (>30 days).")
        if has_provenance_issue:
            quality_caveats.append("Biomarker extraction failed provenance or digital signature validation.")

        # ---------------------------------------------------------------------
        # 1. Evaluate Objective Laboratory Biomarkers
        # ---------------------------------------------------------------------

        # Analyte Group: Troponin (with Assay Nuance, Serial Timing & Protocol Validation - A5/A6)
        troponin_val = labs.get("cardiac_troponin_ng_ml") or labs.get("hs_troponin_i_ng_ml") or labs.get("hs_troponin_t_ng_ml")
        troponin_cutoff, trop_unit, is_hs_assay, assay_name = self._resolve_troponin_cutoff(labs)
        protocol_status, protocol_caveats, is_valid_series = self._validate_serial_troponin_protocol(labs)
        quality_caveats.extend(protocol_caveats)

        if troponin_val is not None:
            trop_key = "cardiac_troponin_ng_ml"
            evidence_states["troponin"] = (
                EvidenceValidityState.INVALID.value if has_provenance_issue
                else EvidenceValidityState.STALE.value if has_stale_evidence
                else EvidenceValidityState.AMBIGUOUS.value if has_locale_ambiguity
                else EvidenceValidityState.VERIFIED_PRESENT.value
            )

            try:
                trop_num = float(troponin_val)
                is_acute_infarct_claim = any(k in claim_lower for k in ["acute myocardial", "infarction", "stemi", "nstemi", "acute coronary", "acute ischemia"])
                is_unstable_angina = "unstable angina" in claim_lower
                is_rule_out = any(k in claim_lower for k in ["rule out", "ruled out", "normal troponin", "no myocardial necrosis"])

                serial_completed = bool(labs.get("serial_troponin_completed")) and is_valid_series

                if has_needs_review or has_provenance_issue:
                    evidence_classifications[trop_key] = EvidenceSupportClassification.UNVERIFIABLE.value
                elif is_rule_out and trop_num <= troponin_cutoff:
                    evidence_classifications[trop_key] = EvidenceSupportClassification.SUPPORTS.value
                    credited_analyte_groups.add("troponin")
                    verified_evidence.append(trop_key)
                elif is_unstable_angina:
                    if trop_num <= troponin_cutoff:
                        evidence_classifications[trop_key] = EvidenceSupportClassification.NEUTRAL.value
                        quality_caveats.append("Unstable angina presents with acute ischemia without troponin elevation; normal troponin is consistent with unstable angina.")
                    else:
                        evidence_classifications[trop_key] = EvidenceSupportClassification.SUPPORTS.value
                        credited_analyte_groups.add("troponin")
                        verified_evidence.append(trop_key)
                elif is_acute_infarct_claim and trop_num <= troponin_cutoff:
                    if serial_completed:
                        evidence_classifications[trop_key] = EvidenceSupportClassification.CONTRADICTS.value
                        conflicting_evidence.append(f"{trop_key} ({trop_num} {trop_unit} <= {troponin_cutoff} ref with completed serial evaluation)")
                    else:
                        evidence_classifications[trop_key] = EvidenceSupportClassification.INSUFFICIENT.value
                        quality_caveats.append("Single normal troponin without adequate serial testing does not rule out early acute coronary syndrome.")
                elif trop_num > troponin_cutoff and (domain == "ischemia" or is_acute_infarct_claim):
                    evidence_classifications[trop_key] = EvidenceSupportClassification.SUPPORTS.value
                    credited_analyte_groups.add("troponin")
                    verified_evidence.append(trop_key)
                    # Check for ischemic context (symptoms or ECG) per Fourth Universal Definition
                    has_ischemic_context = (
                        bool(symptoms.get("symptoms"))
                        or any(s in str(labs.get("resting_ecg") or "").lower() for s in ["st_elevation", "st_depression", "t_wave_inversion", "ischemi"])
                    )
                    if not has_ischemic_context:
                        quality_caveats.append("Myocardial injury detected (troponin elevation > 99th percentile URL); Fourth Universal Definition of MI distinguishes myocardial injury from acute myocardial infarction pending clinical ischemic context.")
                elif domain == "ischemia" or "troponin" in claim_lower or "cardiac" in claim_lower:
                    if trop_num <= troponin_cutoff and not is_acute_infarct_claim:
                        evidence_classifications[trop_key] = EvidenceSupportClassification.SUPPORTS.value
                        credited_analyte_groups.add("troponin")
                        verified_evidence.append(trop_key)
                    else:
                        evidence_classifications[trop_key] = EvidenceSupportClassification.NEUTRAL.value
            except (ValueError, TypeError):
                evidence_classifications[trop_key] = EvidenceSupportClassification.UNVERIFIABLE.value
        else:
            evidence_states["troponin"] = EvidenceValidityState.NOT_COLLECTED.value

        # Analyte Group: Resting ECG
        ecg_val = labs.get("resting_ecg") or labs.get("ecg")
        if ecg_val is not None:
            ecg_key = "resting_ecg"
            evidence_states["resting_ecg"] = EvidenceValidityState.VERIFIED_PRESENT.value
            ecg_str = str(ecg_val).lower()

            if domain == "ischemia" or "ecg" in claim_lower or "infarct" in claim_lower or "angina" in claim_lower:
                if "st_elevation" in ecg_str or "ischemi" in ecg_str or "depression" in ecg_str or "t_wave_inversion" in ecg_str:
                    evidence_classifications[ecg_key] = EvidenceSupportClassification.SUPPORTS.value
                    credited_analyte_groups.add("resting_ecg")
                    verified_evidence.append(ecg_key)
                elif "normal" in ecg_str:
                    if "stemi" in claim_lower:
                        evidence_classifications[ecg_key] = EvidenceSupportClassification.CONTRADICTS.value
                        conflicting_evidence.append(f"{ecg_key} (normal rhythm contradicts active STEMI)")
                    elif any(k in claim_lower for k in ["acute myocardial", "nstemi", "unstable angina"]):
                        evidence_classifications[ecg_key] = EvidenceSupportClassification.INSUFFICIENT.value
                        quality_caveats.append("Normal resting ECG does not exclude NSTEMI or unstable angina; serial troponin and clinical context are essential.")
                    else:
                        evidence_classifications[ecg_key] = EvidenceSupportClassification.SUPPORTS.value
                        credited_analyte_groups.add("resting_ecg")
                        verified_evidence.append(ecg_key)
                else:
                    evidence_classifications[ecg_key] = EvidenceSupportClassification.NEUTRAL.value

        # Analyte Group: Blood Pressure & Target-Organ Damage (Hypertensive Emergency vs Urgency - A3)
        sbp = labs.get("systolic_bp")
        dbp = labs.get("diastolic_bp")
        if sbp is not None or dbp is not None:
            bp_key = "blood_pressure_measurement"
            evidence_states["blood_pressure"] = EvidenceValidityState.VERIFIED_PRESENT.value
            is_htn_emergency_claim = any(k in claim_lower for k in ["hypertensive emergency", "malignant hypertension", "hypertensive crisis with target organ"])
            is_htn_urgency_claim = any(k in claim_lower for k in ["hypertensive urgency", "severe asymptomatic hypertension"])

            tod_state, tod_markers, tod_notes = self._evaluate_target_organ_damage(labs, history, symptoms)

            if is_htn_emergency_claim:
                if tod_state == TargetOrganDamageState.PRESENT:
                    evidence_states["target_organ_damage"] = EvidenceValidityState.VERIFIED_PRESENT.value
                    evidence_classifications[bp_key] = EvidenceSupportClassification.SUPPORTS.value
                    credited_analyte_groups.add("blood_pressure")
                    credited_analyte_groups.add("target_organ_damage")
                    verified_evidence.append(bp_key)
                    verified_evidence.append("target_organ_damage")
                elif tod_state == TargetOrganDamageState.UNKNOWN:
                    evidence_states["target_organ_damage"] = EvidenceValidityState.NOT_COLLECTED.value
                    evidence_classifications[bp_key] = EvidenceSupportClassification.INSUFFICIENT.value
                    quality_caveats.append("Severe BP elevation with UNKNOWN target-organ damage status; emergency evaluation required.")
                else:
                    evidence_states["target_organ_damage"] = EvidenceValidityState.VERIFIED_PRESENT.value
                    evidence_classifications[bp_key] = EvidenceSupportClassification.INSUFFICIENT.value
                    quality_caveats.append("Severe BP elevation without documented acute target-organ damage represents Hypertensive Urgency, not Hypertensive Emergency.")
            elif is_htn_urgency_claim:
                if tod_state == TargetOrganDamageState.PRESENT:
                    evidence_classifications[bp_key] = EvidenceSupportClassification.CONTRADICTS.value
                    conflicting_evidence.append("Target-organ damage present contradicts asymptomatic hypertensive urgency")
                else:
                    evidence_classifications[bp_key] = EvidenceSupportClassification.SUPPORTS.value
                    credited_analyte_groups.add("blood_pressure")
                    verified_evidence.append(bp_key)
            elif domain == "hemodynamics" or any(k in claim_lower for k in ["blood pressure", "hypertens", "bp"]):
                evidence_classifications[bp_key] = EvidenceSupportClassification.SUPPORTS.value
                credited_analyte_groups.add("blood_pressure")
                verified_evidence.append(bp_key)

        # Analyte Group: Natriuretic Peptide (Heart Failure Decompensated vs Chronic + Confounding - A4)
        bnp = labs.get("bnp_pg_ml") or labs.get("nt_pro_bnp_pg_ml")
        if bnp is not None:
            bnp_key = "natriuretic_peptide"
            evidence_states["natriuretic_peptide"] = EvidenceValidityState.VERIFIED_PRESENT.value
            try:
                bnp_num = float(bnp)
                is_acute_hf = any(k in claim_lower for k in ["acute heart failure", "decompensated", "pulmonary edema"])
                is_normal_peptide = bnp_num < 100.0

                # Confounder evaluation: Renal, Obesity, Age, AFib
                egfr = labs.get("egfr_ml_min")
                creat = labs.get("serum_creatinine_mg_dl")
                if (egfr is not None and float(egfr) < 60.0) or (creat is not None and float(creat) > 1.8):
                    quality_caveats.append("Elevated natriuretic peptide in presence of impaired renal function (eGFR < 60 mL/min) may reflect reduced clearance; interpret alongside clinical congestion.")

                bmi = labs.get("bmi") or history.get("bmi")
                if (bmi is not None and float(bmi) >= 30.0) or history.get("obesity"):
                    quality_caveats.append("Patient BMI >= 30 (obesity) is known to lower circulating natriuretic peptide levels by up to 50%; normal or borderline BNP does not rule out heart failure in obese patients.")

                age = labs.get("age") or history.get("age")
                if age is not None and float(age) > 75.0:
                    quality_caveats.append("Patient age > 75 years raises natriuretic peptide baseline (age-adjusted NT-proBNP rule-in cutoff is 1800 pg/mL).")

                ecg_str = str(labs.get("resting_ecg") or "").lower()
                if "atrial_fibrillation" in ecg_str or "afib" in ecg_str:
                    quality_caveats.append("Atrial fibrillation independently elevates baseline natriuretic peptides.")

                # Echocardiogram / LVEF evaluation (HFrEF vs HFpEF)
                lvef = labs.get("echocardiogram_lvef_percent") or labs.get("ejection_fraction") or labs.get("lvef")
                if lvef is not None:
                    try:
                        lvef_val = float(lvef)
                        if "hfref" in claim_lower and lvef_val > 40.0:
                            quality_caveats.append(f"HFrEF claim contradicts LVEF {lvef_val}% (HFrEF defined as LVEF <= 40%).")
                        elif "hfpef" in claim_lower and lvef_val < 50.0:
                            quality_caveats.append(f"HFpEF claim contradicts LVEF {lvef_val}% (HFpEF defined as LVEF >= 50%).")
                        elif lvef_val <= 40.0:
                            credited_analyte_groups.add("cardiac_function")
                            verified_evidence.append("cardiac_function (LVEF <= 40% HFrEF)")
                        elif lvef_val >= 50.0:
                            credited_analyte_groups.add("cardiac_function")
                            verified_evidence.append("cardiac_function (LVEF >= 50% HFpEF)")
                    except (ValueError, TypeError):
                        pass

                if is_acute_hf and is_normal_peptide:
                    evidence_classifications[bnp_key] = EvidenceSupportClassification.CONTRADICTS.value
                    conflicting_evidence.append(f"{bnp_key} ({bnp_num} pg/mL < 100 pg/mL cutoff contradicts acute decompensated heart failure)")
                elif domain == "heart_failure" or any(k in claim_lower for k in ["bnp", "heart failure", "dyspnea"]):
                    evidence_classifications[bnp_key] = EvidenceSupportClassification.SUPPORTS.value
                    credited_analyte_groups.add("natriuretic_peptide")
                    verified_evidence.append(bnp_key)
            except (ValueError, TypeError):
                evidence_classifications[bnp_key] = EvidenceSupportClassification.UNVERIFIABLE.value

        # Analyte Group: Glycemic Crisis Differentiation (DKA, HHS, Severe Hyperglycemia, Chronic Diabetes - A2)
        acute_glucose = labs.get("fasting_blood_glucose_mg_dl") or labs.get("random_blood_glucose_mg_dl") or labs.get("blood_glucose_mg_dl")
        chronic_glucose = labs.get("hba1c_percent")
        ketone_val = labs.get("beta_hydroxybutyrate_mmol_l") or labs.get("blood_ketones_mmol_l") or labs.get("serum_ketones_mmol_l") or labs.get("urine_ketones")
        ph_val = labs.get("blood_ph") or labs.get("arterial_ph") or labs.get("venous_ph")
        bicarb_val = labs.get("serum_bicarbonate_mmol_l") or labs.get("bicarbonate_mEq_L")
        osmolality_val = labs.get("serum_osmolality_mosm_kg") or labs.get("effective_osmolality_mosm_kg")

        is_dka_claim = any(k in claim_lower for k in ["diabetic ketoacidosis", "dka", "ketoacidosis"])
        is_hhs_claim = any(k in claim_lower for k in ["hyperglycemic hyperosmolar", "hhs", "hyperosmolar hyperglycemic", "honk"])

        # Check for Euglycemic DKA context (diabetes history or SGLT2i use with glucose < 250)
        has_diabetes_history = (
            any("diabet" in str(c).lower() for c in history.get("chronic_conditions", []))
            or bool(labs.get("documented_diabetes"))
            or bool(history.get("documented_diabetes"))
        )
        has_sglt2i = bool(labs.get("sglt2_inhibitor_use") or history.get("sglt2_inhibitor"))

        # Urine ketones screening caveat
        if labs.get("urine_ketones") is not None and labs.get("beta_hydroxybutyrate_mmol_l") is None:
            quality_caveats.append("Urine dipstick acetoacetate is a qualitative screening test and not equivalent to quantitative serum beta-hydroxybutyrate; mandates serum confirmation.")

        # Effective vs total osmolality
        na_val = labs.get("serum_sodium_meq_l") or labs.get("serum_sodium_mmol_l") or labs.get("sodium_meq_l")
        bun_val = labs.get("blood_urea_nitrogen_mg_dl") or labs.get("bun_mg_dl")
        eff_osm = None
        if na_val is not None and acute_glucose is not None:
            try:
                eff_osm = 2.0 * float(na_val) + (float(acute_glucose) / 18.0)
                quality_caveats.append(f"Effective osmolality calculated: {eff_osm:.1f} mOsm/kg (excluding urea/BUN).")
            except (ValueError, TypeError):
                pass

        # Mixed DKA/HHS presentation detection (A2)
        if eff_osm is not None and eff_osm > 320.0 and (is_dka_claim or is_hhs_claim):
            has_ketoacidosis = False
            if ketone_val is not None:
                try:
                    if float(ketone_val) >= 3.0:
                        has_ketoacidosis = True
                except (ValueError, TypeError):
                    pass
            if ph_val is not None:
                try:
                    if float(ph_val) < 7.30:
                        has_ketoacidosis = True
                except (ValueError, TypeError):
                    pass
            if has_ketoacidosis:
                quality_caveats.append("Mixed presentation of Diabetic Ketoacidosis (DKA) and Hyperglycemic Hyperosmolar State (HHS) identified.")

        if is_dka_claim:
            if chronic_glucose is not None and acute_glucose is None and ketone_val is None:
                evidence_classifications["hba1c_percent"] = EvidenceSupportClassification.INSUFFICIENT.value
                quality_caveats.append("Elevated HbA1c confirms chronic glycemic exposure but cannot establish acute diabetic ketoacidosis (DKA) without ketones and acid-base testing.")

            if acute_glucose is not None:
                try:
                    g_num = float(acute_glucose)
                    if g_num < 250.0 and (has_diabetes_history or has_sglt2i):
                        quality_caveats.append("Euglycemic DKA presentation: blood glucose < 250 mg/dL in patient with documented diabetes/SGLT2i context accompanied by ketonemia and metabolic acidosis.")
                        evidence_states["glycemia_acute"] = EvidenceValidityState.VERIFIED_PRESENT.value
                        credited_analyte_groups.add("glycemia_acute")
                        verified_evidence.append("glycemia_acute (euglycemic DKA presentation)")
                    else:
                        evidence_states["glycemia_acute"] = EvidenceValidityState.VERIFIED_PRESENT.value
                        credited_analyte_groups.add("glycemia_acute")
                        verified_evidence.append("glycemia_acute")
                except (ValueError, TypeError):
                    evidence_states["glycemia_acute"] = EvidenceValidityState.VERIFIED_PRESENT.value
                    credited_analyte_groups.add("glycemia_acute")
                    verified_evidence.append("glycemia_acute")
            elif has_diabetes_history or has_sglt2i:
                evidence_states["glycemia_acute"] = EvidenceValidityState.VERIFIED_PRESENT.value
                credited_analyte_groups.add("glycemia_acute")
                verified_evidence.append("documented_diabetes (euglycemic DKA context)")

            if ketone_val is not None:
                evidence_states["ketones"] = EvidenceValidityState.VERIFIED_PRESENT.value
                try:
                    k_num = float(ketone_val)
                    if k_num >= 3.0:
                        evidence_classifications["ketones"] = EvidenceSupportClassification.SUPPORTS.value
                        credited_analyte_groups.add("ketones")
                        verified_evidence.append("ketones")
                    elif k_num < 0.6:
                        evidence_classifications["ketones"] = EvidenceSupportClassification.CONTRADICTS.value
                        conflicting_evidence.append(f"ketones ({k_num} mmol/L normal contradicts active DKA)")
                    else:
                        credited_analyte_groups.add("ketones")
                        verified_evidence.append("ketones")
                except (ValueError, TypeError):
                    credited_analyte_groups.add("ketones")
                    verified_evidence.append("ketones")
            else:
                evidence_states["ketones"] = EvidenceValidityState.NOT_COLLECTED.value

            if ph_val is not None or bicarb_val is not None:
                evidence_states["acid_base"] = EvidenceValidityState.VERIFIED_PRESENT.value
                credited_analyte_groups.add("acid_base")
                verified_evidence.append("acid_base")
            else:
                evidence_states["acid_base"] = EvidenceValidityState.NOT_COLLECTED.value

        elif is_hhs_claim:
            if chronic_glucose is not None and acute_glucose is None:
                evidence_classifications["hba1c_percent"] = EvidenceSupportClassification.INSUFFICIENT.value
                quality_caveats.append("HbA1c cannot confirm acute hyperosmolar hyperglycemic state without acute blood glucose and serum osmolality.")

            if acute_glucose is not None:
                evidence_states["glycemia_acute"] = EvidenceValidityState.VERIFIED_PRESENT.value
                credited_analyte_groups.add("glycemia_acute")
                verified_evidence.append("glycemia_acute")

            if osmolality_val is not None:
                evidence_states["osmolality"] = EvidenceValidityState.VERIFIED_PRESENT.value
                credited_analyte_groups.add("osmolality")
                verified_evidence.append("osmolality")
            else:
                evidence_states["osmolality"] = EvidenceValidityState.NOT_COLLECTED.value

        elif any(k in claim_lower for k in ["severe hyperglycemia", "marked hyperglycemia", "uncontrolled hyperglycemia"]):
            if acute_glucose is not None:
                glyc_key = "fasting_blood_glucose_mg_dl"
                evidence_states["glycemia_acute"] = EvidenceValidityState.VERIFIED_PRESENT.value
                credited_analyte_groups.add("glycemia_acute")
                verified_evidence.append(glyc_key)
                evidence_classifications[glyc_key] = EvidenceSupportClassification.SUPPORTS.value
                quality_caveats.append("Severe hyperglycemia identified without diagnostic features of DKA or HHS.")
        elif acute_glucose is not None or chronic_glucose is not None:
            glyc_key = "fasting_blood_glucose_mg_dl" if acute_glucose is not None else "hba1c_percent"
            evidence_states["glycemia"] = EvidenceValidityState.VERIFIED_PRESENT.value
            if domain == "glycemia" or any(k in claim_lower for k in ["glucose", "diabet", "hba1c"]):
                evidence_classifications[glyc_key] = EvidenceSupportClassification.SUPPORTS.value
                credited_analyte_groups.add("glycemia")
                verified_evidence.append(glyc_key)

        # Analyte Group: Lipid Panel (LDL, Total, HDL count as ONE lipid panel group)
        ldl = labs.get("ldl_cholesterol_mg_dl")
        tc = labs.get("total_cholesterol_mg_dl")
        if ldl is not None or tc is not None:
            lipid_key = "ldl_cholesterol_mg_dl"
            evidence_states["lipid_panel"] = EvidenceValidityState.VERIFIED_PRESENT.value
            if domain == "lipidology" or any(k in claim_lower for k in ["lipid", "cholesterol", "ldl"]):
                evidence_classifications[lipid_key] = EvidenceSupportClassification.SUPPORTS.value
                credited_analyte_groups.add("lipid_panel")
                verified_evidence.append(lipid_key)

        # ---------------------------------------------------------------------
        # 2. Documented Medical History & Active Pharmacotherapy
        # ---------------------------------------------------------------------
        if domain == "lipidology" and history.get("current_medications"):
            for med in history.get("current_medications", []):
                if isinstance(med, dict) and "statin" in str(med.get("name", "")).lower():
                    med_key = "current_medications:statin"
                    evidence_classifications[med_key] = EvidenceSupportClassification.SUPPORTS.value
                    if "statin_therapy" not in credited_analyte_groups:
                        credited_analyte_groups.add("statin_therapy")
                        verified_evidence.append(med_key)

        # ---------------------------------------------------------------------
        # 3. Documented Symptoms
        # ---------------------------------------------------------------------
        if domain == "ischemia" and symptoms.get("symptoms"):
            syms = [s.lower() for s in symptoms.get("symptoms", [])]
            if any(s in ["chest_pain", "angina", "substernal_pressure"] for s in syms):
                sym_key = "symptoms:chest_pain"
                evidence_classifications[sym_key] = EvidenceSupportClassification.SUPPORTS.value
                if "symptom_report" not in credited_analyte_groups:
                    credited_analyte_groups.add("symptom_report")
                    verified_evidence.append(sym_key)

        # Calculate grounding adjustment from distinct credited groups
        independent_sources_count = len(credited_analyte_groups)
        raw_adjustment = independent_sources_count * self.base_grounding_increment
        final_adjustment = min(self.max_grounding_adjustment, raw_adjustment)

        if final_adjustment > 0:
            notes = f"{independent_sources_count} independent analyte/diagnostic group(s) (+{final_adjustment:.1f}%)"
        else:
            notes = "No independent supporting patient evidence found for this claim"

        return (
            final_adjustment,
            verified_evidence,
            conflicting_evidence,
            quality_caveats,
            evidence_classifications,
            evidence_states,
            notes,
        )

    def _calculate_contradiction_penalty(
        self,
        agent_id: str,
        domain: str,
        debate_outcome: Optional[str],
        related_issues: List[ContradictionIssue],
        debate_transcript: Optional[DebateTranscript],
        verified_evidence: Optional[List[str]] = None,
    ) -> Tuple[float, str, List[str]]:
        """Compute negative contradiction penalty (-0% to -25%)."""
        # Rule: Incomparable predictions never generate a contradiction penalty
        filtered_issues = [
            i for i in related_issues if i.category != ContradictionCategory.INCOMPARABLE_PREDICTIONS
        ]

        if not filtered_issues:
            return 0.0, "No active contradictions in domain", []

        if debate_outcome == "unsupported":
            return self.critical_contradiction_penalty, "Claim unsupported in debate due to absent evidence", [i.issue_id for i in filtered_issues]

        # Check if debate resolved the contradiction
        resolved_issue_ids: Set[str] = set()
        conceded_issue_ids: Set[str] = set()

        if debate_transcript:
            for ch in debate_transcript.challenges:
                if ch.status == ChallengeStatus.REVISED:
                    resolved_issue_ids.add(ch.issue_id)
                elif ch.status == ChallengeStatus.CONCEDED:
                    conceded_issue_ids.add(ch.issue_id)
            if debate_transcript.conceded_challenges:
                conceded_issue_ids.update(debate_transcript.conceded_challenges)

        active_penalties: List[float] = []
        issue_ids: List[str] = []

        for issue in filtered_issues:
            issue_ids.append(issue.issue_id)

            # Genuinely resolved issues (e.g. revised with clinical reconciliation) do not penalize
            if issue.issue_id in resolved_issue_ids:
                continue

            # If the contradiction was conceded in debate:
            if issue.issue_id in conceded_issue_ids:
                # Check whether this agent's claim was defended by verified objective evidence
                ch_record = next((c for c in debate_transcript.challenges if c.issue_id == issue.issue_id), None) if debate_transcript else None
                if ch_record and ch_record.challenged_agent != agent_id:
                    # This agent issued the challenge or defended verified evidence -> 0 penalty
                    continue
                elif verified_evidence and len(verified_evidence) > 0:
                    # Agent's claim is substantiated by objective patient evidence -> 0 penalty
                    continue
                else:
                    # Conceded claim without objective evidence
                    continue

            # Unresolved active contradiction
            if issue.severity == ContradictionSeverity.CRITICAL:
                base_pen = self.critical_contradiction_penalty
            elif issue.severity == ContradictionSeverity.MODERATE:
                base_pen = self.moderate_contradiction_penalty
            else:
                base_pen = self.minor_contradiction_penalty

            if not issue.is_confirmed_contradiction:
                base_pen = max(5.0, base_pen * 0.67)

            active_penalties.append(base_pen)

        if not active_penalties:
            return 0.0, "Contradictions resolved by clinical reconciliation in debate", issue_ids

        # Domain deduplication: Take the maximum penalty in this domain rather than compounding
        max_penalty = min(self.critical_contradiction_penalty, max(active_penalties))
        notes = f"Unresolved {domain} contradiction (domain-deduplicated maximum: -{max_penalty:.1f}%)"

        return max_penalty, notes, issue_ids

    def _evaluate_evidence_group(
        self,
        group: EvidenceGroup,
        labs: Dict[str, Any],
        history: Dict[str, Any],
        symptoms: Dict[str, Any],
    ) -> Tuple[bool, Optional[str]]:
        """Evaluate whether a logical evidence group is satisfied by patient data."""
        if group.description == "target_organ_damage":
            tod_state, markers, tod_notes = self._evaluate_target_organ_damage(labs, history, symptoms)
            if tod_state == TargetOrganDamageState.PRESENT:
                return True, None
            elif tod_state == TargetOrganDamageState.UNKNOWN:
                return False, "target_organ_damage (status UNKNOWN: cardiac and renal biomarkers not evaluated)"
            elif tod_state == TargetOrganDamageState.ABSENT:
                return False, "target_organ_damage (absent: clinical presentation is hypertensive urgency, not emergency)"
            elif tod_state == TargetOrganDamageState.SUSPECTED:
                return False, "target_organ_damage (suspected based on symptoms, pending biomarker confirmation)"

        def check_key(k: str) -> bool:
            if labs.get(k) is not None:
                return True
            if k in ["documented_diabetes", "type_1_diabetes", "type_2_diabetes"]:
                if labs.get("documented_diabetes") or history.get("documented_diabetes"):
                    return True
                conds = [str(c).lower() for c in history.get("chronic_conditions", [])]
                if any("diabet" in c for c in conds):
                    return True
                return False
            if k in ["sglt2_inhibitor_use", "sglt2_inhibitor"]:
                if labs.get("sglt2_inhibitor_use") or history.get("sglt2_inhibitor"):
                    return True
                meds = [str(m).lower() for m in history.get("current_medications", [])]
                if any("sglt2" in m for m in meds):
                    return True
                return False
            if k == "effective_osmolality_mosm_kg":
                na = labs.get("serum_sodium_meq_l") or labs.get("serum_sodium_mmol_l") or labs.get("sodium_meq_l")
                glu = labs.get("fasting_blood_glucose_mg_dl") or labs.get("random_blood_glucose_mg_dl") or labs.get("blood_glucose_mg_dl")
                if na is not None and glu is not None:
                    return True
            if k == "blood_pressure":
                if labs.get("systolic_bp") is not None or labs.get("diastolic_bp") is not None or labs.get("blood_pressure") is not None:
                    return True
            if history.get(k) is not None:
                return True
            if symptoms.get(k) is not None:
                return True
            if k in [str(s).lower() for s in symptoms.get("symptoms", [])]:
                return True
            return False

        if group.operator == "AND":
            satisfied = all(check_key(k) for k in group.keys)
        else:  # "OR"
            matching = [k for k in group.keys if check_key(k)]
            satisfied = len(matching) >= group.min_required

        if satisfied:
            return True, None

        if group.description == "troponin":
            desc = "cardiac_troponin_ng_ml"
        elif group.description:
            desc = group.description
        else:
            desc = group.keys[0] if group.keys else "essential_evidence"
        return False, desc

    def _check_missing_essential_evidence(
        self,
        domain: str,
        claim_text: str,
        labs: Dict[str, Any],
        history: Dict[str, Any],
        symptoms: Dict[str, Any],
    ) -> Tuple[bool, Optional[float], List[str], str]:
        """Check if essential quantitative evidence is missing for this claim, triggering confidence cap."""
        claim_lower = claim_text.lower()
        missing_keys: List[str] = []
        applied_cap = self.missing_evidence_cap

        # Intent classification safeguard: negative/exclusion or historical claims are exempt from acute positive biomarker caps
        intent = self._classify_claim_intent(claim_text)
        if intent["is_negated"]:
            return False, None, [], f"Claim is an exclusion or negative finding ('{claim_text}'); acute positive biomarker requirements waived."
        if intent["is_historical"]:
            return False, None, [], f"Claim refers to past medical history ('{claim_text}'); acute presentation requirements waived."

        # Iterate over registered claim evidence requirements
        for req in CLAIM_REQUIREMENT_REGISTRY:
            if req.clinical_domain != domain:
                continue

            # Check trigger match
            matches_trigger = any(kw in claim_lower for kw in req.trigger_keywords)
            if not matches_trigger:
                continue

            # Check exemption (e.g. family history, chronic past medical history)
            is_exempt = any(ex in claim_lower for ex in req.exempt_keywords)
            if is_exempt:
                continue

            # Check required logical evidence groups
            for group in req.required_groups:
                satisfied, missing_desc = self._evaluate_evidence_group(group, labs, history, symptoms)
                if not satisfied and missing_desc:
                    if missing_desc not in missing_keys:
                        missing_keys.append(missing_desc)
                        applied_cap = min(applied_cap, req.confidence_cap)

        if missing_keys:
            return True, applied_cap, missing_keys, f"Essential evidence missing: {', '.join(missing_keys)}"

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
        ml: Dict[str, Any],
    ) -> Tuple[List[DomainEpistemicDoubt], List[str]]:
        """Calculate domain-level uncertainty contributions strictly isolated to each domain."""
        domain_doubts: List[DomainEpistemicDoubt] = []
        all_missing_summary: List[str] = []

        all_domains = set(domain_claim_map.keys())
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
                        if debate_transcript and issue.issue_id in debate_transcript.conceded_challenges:
                            if issue.category not in [ContradictionCategory.SUBJECTIVE_VS_OBJECTIVE, ContradictionCategory.HISTORY_MEDICATION_VS_BIOMARKER]:
                                continue
                        unresolved_issues.append(issue)

            unresolved_count = len(unresolved_issues)

            # 2. Missing essential evidence in domain (only for active claims that triggered requirements)
            missing_for_domain: List[str] = []
            for r in records:
                if r.missing_evidence_cap_applied and r.missing_evidence_details:
                    for m_key in r.missing_evidence_details:
                        if m_key not in missing_for_domain:
                            missing_for_domain.append(m_key)
                        if m_key not in all_missing_summary:
                            all_missing_summary.append(m_key)

            # 3. Quality & provenance uncertainty (OCR, locale ambiguity, uncalibrated ML, stale evidence, invalid provenance)
            quality_uncertainty = 0.0
            if labs.get("flag_locale_ambiguity"):
                quality_uncertainty += 0.15
            if labs.get("needs_review"):
                quality_uncertainty += 0.20
            if labs.get("is_stale") or labs.get("stale_evidence"):
                quality_uncertainty += 0.20
            if labs.get("invalid_provenance") or labs.get("provenance_issue"):
                quality_uncertainty += 0.25
            if dom == "cardiovascular_risk" and ml.get("calibrated") is False:
                quality_uncertainty += 0.15
            quality_uncertainty = min(1.0, quality_uncertainty)

            # 4. Unsupported claims & inconclusive debate outcomes
            unsupported_count = sum(1 for r in records if r.debate_outcome == "unsupported")

            # 5. Compute domain uncertainty score [0.0, 1.0]
            crit_issues = sum(1 for i in unresolved_issues if i.severity == ContradictionSeverity.CRITICAL)
            mod_issues = sum(1 for i in unresolved_issues if i.severity == ContradictionSeverity.MODERATE)

            contradiction_contrib = min(1.0, (crit_issues * 0.70) + (mod_issues * 0.40) + ((unresolved_count - crit_issues - mod_issues) * 0.20))
            missing_contrib = 1.0 if missing_for_domain else 0.0
            unsupported_contrib = min(1.0, unsupported_count * 0.50)

            # Weighted domain combination
            raw_doubt = (
                (0.35 * contradiction_contrib)
                + (0.35 * missing_contrib)
                + (0.15 * quality_uncertainty)
                + (0.15 * unsupported_contrib)
            )

            # Domain doubt floor applies ONLY to this domain if mandatory evidence is missing
            if missing_for_domain:
                raw_doubt = max(0.35, raw_doubt)

            domain_score = max(0.0, min(1.0, round(raw_doubt, 3)))

            rationale_parts = []
            if unresolved_count > 0:
                rationale_parts.append(f"{unresolved_count} unresolved contradiction(s)")
            if missing_for_domain:
                rationale_parts.append(f"missing essential biomarker(s): {', '.join(missing_for_domain)}")
            if quality_uncertainty > 0:
                rationale_parts.append(f"evidence quality uncertainty: {quality_uncertainty:.2f}")
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
                    quality_uncertainty_score=quality_uncertainty,
                    rationale="; ".join(rationale_parts) + ".",
                )
            )

        return domain_doubts, all_missing_summary

    def _calculate_global_epistemic_doubt(
        self,
        domain_doubts: List[DomainEpistemicDoubt],
        contradiction_matrix: Optional[ContradictionMatrixResult],
        debate_transcript: Optional[DebateTranscript],
        missing_summary: List[str],
    ) -> float:
        """Calculate bounded Global Epistemic Doubt Score in range [0.0, 1.0]."""
        if not domain_doubts:
            return 0.0

        scores = [d.doubt_contribution for d in domain_doubts]
        max_doubt = max(scores)
        mean_doubt = sum(scores) / len(scores)

        # Domain-aware aggregation:
        # 55% weight to peak domain uncertainty + 45% weight to average panel uncertainty
        # Preserves critical domain uncertainty without diluting it in a naive average
        aggregated_doubt = (0.55 * max_doubt) + (0.45 * mean_doubt)

        # Convergence handling
        if debate_transcript and debate_transcript.convergence_status == "converged":
            if missing_summary:
                aggregated_doubt = max(0.35, min(aggregated_doubt, 0.45))
            else:
                aggregated_doubt = min(aggregated_doubt, 0.15)
        elif debate_transcript and debate_transcript.convergence_status == "no_contradictions":
            if missing_summary:
                aggregated_doubt = 0.35
            else:
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
            "Evidence grounding applies strictly to verified, normalized patient biomarkers; multiple measurements within the same analyte group do not compound bonuses.",
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
