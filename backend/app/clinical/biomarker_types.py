"""Biomarker taxonomy, canonical identities, and clinical unit definitions.

Establishes:
1. CanonicalBiomarker: Standardized MedOracle biomarker identifiers.
2. NormalizationStatus: Explicit validation and audit statuses.
3. AbnormalityFlag: Laboratory and clinical range flags.
4. BiomarkerDefinition: Clinical metadata, molecular weights, and canonical units.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set


class CanonicalBiomarker(str, Enum):
    """Canonical MedOracle laboratory biomarker identifiers."""

    # Glycemic
    FASTING_BLOOD_GLUCOSE = "fasting_blood_glucose_mg_dl"
    RANDOM_BLOOD_GLUCOSE = "random_blood_glucose_mg_dl"
    HBA1C = "hba1c_percent"

    # Lipid Panel
    TOTAL_CHOLESTEROL = "total_cholesterol_mg_dl"
    LDL_CHOLESTEROL = "ldl_cholesterol_mg_dl"
    HDL_CHOLESTEROL = "hdl_cholesterol_mg_dl"
    TRIGLYCERIDES = "triglycerides_mg_dl"

    # Renal & Metabolic
    SERUM_CREATININE = "serum_creatinine_mg_dl"
    ESTIMATED_GFR = "estimated_gfr"
    BLOOD_UREA_NITROGEN = "blood_urea_nitrogen_mg_dl"

    # Cardiac Biomarkers (Strictly Delineated Assays)
    BNP = "bnp_pg_ml"
    NT_PROBNP = "nt_probnp_pg_ml"
    TROPONIN_I = "troponin_i_ng_ml"
    TROPONIN_T = "troponin_t_ng_ml"
    HS_TROPONIN_I = "hs_troponin_i_ng_ml"
    HS_TROPONIN_T = "hs_troponin_t_ng_ml"

    # Hematology
    HEMOGLOBIN = "hemoglobin_g_dl"
    WBC_COUNT = "wbc_count"
    PLATELETS_COUNT = "platelets_count"

    # Hepatic Panel
    ALT = "alt_u_l"
    AST = "ast_u_l"

    # Electrolytes
    SODIUM = "sodium_mmol_l"
    POTASSIUM = "potassium_mmol_l"

    # Hemodynamic Vitals
    SYSTOLIC_BP = "systolic_bp"
    DIASTOLIC_BP = "diastolic_bp"


class NormalizationStatus(str, Enum):
    """Explicit validation status for OCR-extracted biomarker entities."""

    NORMALIZED = "NORMALIZED"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    AMBIGUOUS_BIOMARKER = "AMBIGUOUS_BIOMARKER"
    UNSUPPORTED_UNIT = "UNSUPPORTED_UNIT"
    INVALID_VALUE = "INVALID_VALUE"
    MISSING_UNIT = "MISSING_UNIT"
    LOW_OCR_CONFIDENCE = "LOW_OCR_CONFIDENCE"
    QUALITATIVE_VALUE = "QUALITATIVE_VALUE"
    UNMAPPED = "UNMAPPED"


class AbnormalityFlag(str, Enum):
    """Laboratory and reference range abnormality classification."""

    NORMAL = "NORMAL"
    HIGH = "HIGH"
    LOW = "LOW"
    CRITICAL_HIGH = "CRITICAL_HIGH"
    CRITICAL_LOW = "CRITICAL_LOW"
    ABNORMAL = "ABNORMAL"
    INDETERMINATE = "INDETERMINATE"


@dataclass(frozen=True)
class BiomarkerMetadata:
    """Clinical metadata and conversion specifications for a canonical biomarker."""

    canonical_id: CanonicalBiomarker
    display_name: str
    canonical_unit: str
    supported_units: Set[str]
    molecular_weight: Optional[float] = None
    min_biological_value: Optional[float] = None
    max_biological_value: Optional[float] = None
    critical_low_threshold: Optional[float] = None
    critical_high_threshold: Optional[float] = None
    description: str = ""


# Master biomarker specifications repository
BIOMARKER_REGISTRY: Dict[CanonicalBiomarker, BiomarkerMetadata] = {
    CanonicalBiomarker.FASTING_BLOOD_GLUCOSE: BiomarkerMetadata(
        canonical_id=CanonicalBiomarker.FASTING_BLOOD_GLUCOSE,
        display_name="Fasting Blood Glucose",
        canonical_unit="mg/dL",
        supported_units={"mg/dl", "mg/dl", "mmol/l", "mmol/l"},
        molecular_weight=180.156,
        min_biological_value=10.0,
        max_biological_value=1500.0,
        critical_low_threshold=50.0,
        critical_high_threshold=400.0,
        description="Fasting plasma glucose after at least 8 hours fasting (ADA standard: < 100 mg/dL normal).",
    ),
    CanonicalBiomarker.RANDOM_BLOOD_GLUCOSE: BiomarkerMetadata(
        canonical_id=CanonicalBiomarker.RANDOM_BLOOD_GLUCOSE,
        display_name="Random Blood Glucose",
        canonical_unit="mg/dL",
        supported_units={"mg/dl", "mmol/l"},
        molecular_weight=180.156,
        min_biological_value=10.0,
        max_biological_value=1500.0,
        critical_low_threshold=50.0,
        critical_high_threshold=400.0,
        description="Non-fasting random blood glucose measurement.",
    ),
    CanonicalBiomarker.HBA1C: BiomarkerMetadata(
        canonical_id=CanonicalBiomarker.HBA1C,
        display_name="Glycated Hemoglobin (HbA1c)",
        canonical_unit="%",
        supported_units={"%", "percent", "mmol/mol"},
        min_biological_value=2.0,
        max_biological_value=25.0,
        critical_high_threshold=14.0,
        description="Glycated hemoglobin percentage representing 2-3 month glycemic control.",
    ),
    CanonicalBiomarker.TOTAL_CHOLESTEROL: BiomarkerMetadata(
        canonical_id=CanonicalBiomarker.TOTAL_CHOLESTEROL,
        display_name="Total Serum Cholesterol",
        canonical_unit="mg/dL",
        supported_units={"mg/dl", "mmol/l"},
        molecular_weight=386.654,
        min_biological_value=30.0,
        max_biological_value=1000.0,
        critical_high_threshold=400.0,
        description="Total circulating cholesterol fraction (ATP III desirable: < 200 mg/dL).",
    ),
    CanonicalBiomarker.LDL_CHOLESTEROL: BiomarkerMetadata(
        canonical_id=CanonicalBiomarker.LDL_CHOLESTEROL,
        display_name="Low-Density Lipoprotein Cholesterol",
        canonical_unit="mg/dL",
        supported_units={"mg/dl", "mmol/l"},
        molecular_weight=386.654,
        min_biological_value=10.0,
        max_biological_value=600.0,
        critical_high_threshold=250.0,
        description="Atherogenic LDL-C fraction.",
    ),
    CanonicalBiomarker.HDL_CHOLESTEROL: BiomarkerMetadata(
        canonical_id=CanonicalBiomarker.HDL_CHOLESTEROL,
        display_name="High-Density Lipoprotein Cholesterol",
        canonical_unit="mg/dL",
        supported_units={"mg/dl", "mmol/l"},
        molecular_weight=386.654,
        min_biological_value=5.0,
        max_biological_value=200.0,
        critical_low_threshold=20.0,
        description="Cardioprotective reverse-cholesterol transport HDL-C fraction.",
    ),
    CanonicalBiomarker.TRIGLYCERIDES: BiomarkerMetadata(
        canonical_id=CanonicalBiomarker.TRIGLYCERIDES,
        display_name="Serum Triglycerides",
        canonical_unit="mg/dL",
        supported_units={"mg/dl", "mmol/l"},
        molecular_weight=885.4,  # Triolein molecular weight standard
        min_biological_value=10.0,
        max_biological_value=3000.0,
        critical_high_threshold=500.0,
        description="Circulating triglycerides (severe pancreatitis risk >= 500 mg/dL).",
    ),
    CanonicalBiomarker.SERUM_CREATININE: BiomarkerMetadata(
        canonical_id=CanonicalBiomarker.SERUM_CREATININE,
        display_name="Serum Creatinine",
        canonical_unit="mg/dL",
        supported_units={"mg/dl", "µmol/l", "umol/l"},
        molecular_weight=113.12,
        min_biological_value=0.1,
        max_biological_value=30.0,
        critical_high_threshold=5.0,
        description="Endogenous muscle metabolite for renal filtration staging.",
    ),
    CanonicalBiomarker.ESTIMATED_GFR: BiomarkerMetadata(
        canonical_id=CanonicalBiomarker.ESTIMATED_GFR,
        display_name="Estimated Glomerular Filtration Rate",
        canonical_unit="mL/min/1.73m2",
        supported_units={"ml/min/1.73m2", "ml/min"},
        min_biological_value=1.0,
        max_biological_value=250.0,
        critical_low_threshold=15.0,
        description="CKD-EPI / MDRD estimated renal glomerular filtration rate.",
    ),
    CanonicalBiomarker.BLOOD_UREA_NITROGEN: BiomarkerMetadata(
        canonical_id=CanonicalBiomarker.BLOOD_UREA_NITROGEN,
        display_name="Blood Urea Nitrogen (BUN)",
        canonical_unit="mg/dL",
        supported_units={"mg/dl", "mmol/l"},
        molecular_weight=28.01,  # Nitrogen molecular weight in urea
        min_biological_value=1.0,
        max_biological_value=200.0,
        critical_high_threshold=80.0,
        description="Urea nitrogen concentration measuring protein catabolism and renal excretion.",
    ),
    CanonicalBiomarker.BNP: BiomarkerMetadata(
        canonical_id=CanonicalBiomarker.BNP,
        display_name="B-type Natriuretic Peptide (BNP)",
        canonical_unit="pg/mL",
        supported_units={"pg/ml", "ng/l"},
        min_biological_value=1.0,
        max_biological_value=10000.0,
        critical_high_threshold=400.0,
        description="Biologically active cardiac neurohormone secreted from ventricular myocardium under wall stress.",
    ),
    CanonicalBiomarker.NT_PROBNP: BiomarkerMetadata(
        canonical_id=CanonicalBiomarker.NT_PROBNP,
        display_name="N-Terminal pro-B-type Natriuretic Peptide (NT-proBNP)",
        canonical_unit="pg/mL",
        supported_units={"pg/ml", "ng/l", "pmol/l"},
        min_biological_value=1.0,
        max_biological_value=50000.0,
        critical_high_threshold=1800.0,
        description="Biologically inactive N-terminal cleavage fragment of proBNP with longer half-life.",
    ),
    CanonicalBiomarker.TROPONIN_I: BiomarkerMetadata(
        canonical_id=CanonicalBiomarker.TROPONIN_I,
        display_name="Cardiac Troponin I (cTnI)",
        canonical_unit="ng/mL",
        supported_units={"ng/ml", "µg/l", "ug/l", "ng/l", "pg/ml"},
        min_biological_value=0.001,
        max_biological_value=100.0,
        critical_high_threshold=0.04,
        description="Conventional standard-sensitivity cardiac troponin I assay.",
    ),
    CanonicalBiomarker.TROPONIN_T: BiomarkerMetadata(
        canonical_id=CanonicalBiomarker.TROPONIN_T,
        display_name="Cardiac Troponin T (cTnT)",
        canonical_unit="ng/mL",
        supported_units={"ng/ml", "µg/l", "ug/l", "ng/l", "pg/ml"},
        min_biological_value=0.001,
        max_biological_value=100.0,
        critical_high_threshold=0.01,
        description="Conventional standard-sensitivity cardiac troponin T assay.",
    ),
    CanonicalBiomarker.HS_TROPONIN_I: BiomarkerMetadata(
        canonical_id=CanonicalBiomarker.HS_TROPONIN_I,
        display_name="High-Sensitivity Cardiac Troponin I (hs-cTnI)",
        canonical_unit="ng/mL",
        supported_units={"ng/ml", "ng/l", "pg/ml"},
        min_biological_value=0.0001,
        max_biological_value=50.0,
        critical_high_threshold=0.026,
        description="High-sensitivity assay capable of detecting sub-nanogram myocardial necrosis.",
    ),
    CanonicalBiomarker.HS_TROPONIN_T: BiomarkerMetadata(
        canonical_id=CanonicalBiomarker.HS_TROPONIN_T,
        display_name="High-Sensitivity Cardiac Troponin T (hs-cTnT)",
        canonical_unit="ng/mL",
        supported_units={"ng/ml", "ng/l", "pg/ml"},
        min_biological_value=0.0001,
        max_biological_value=50.0,
        critical_high_threshold=0.014,
        description="High-sensitivity troponin T assay with 99th percentile cutoff around 14 ng/L (0.014 ng/mL).",
    ),
    CanonicalBiomarker.HEMOGLOBIN: BiomarkerMetadata(
        canonical_id=CanonicalBiomarker.HEMOGLOBIN,
        display_name="Hemoglobin (Hb)",
        canonical_unit="g/dL",
        supported_units={"g/dl", "g/l", "mmol/l"},
        min_biological_value=2.0,
        max_biological_value=26.0,
        critical_low_threshold=7.0,
        critical_high_threshold=20.0,
        description="Total erythrocyte hemoglobin carrying oxygen.",
    ),
    CanonicalBiomarker.WBC_COUNT: BiomarkerMetadata(
        canonical_id=CanonicalBiomarker.WBC_COUNT,
        display_name="White Blood Cell Count (WBC)",
        canonical_unit="10^3/µL",
        supported_units={"10^3/µl", "10^3/ul", "10^9/l", "cells/mcl", "/ul", "thou/ul"},
        min_biological_value=0.2,
        max_biological_value=200.0,
        critical_low_threshold=2.0,
        critical_high_threshold=30.0,
        description="Total circulating leukocyte count.",
    ),
    CanonicalBiomarker.PLATELETS_COUNT: BiomarkerMetadata(
        canonical_id=CanonicalBiomarker.PLATELETS_COUNT,
        display_name="Platelet Count",
        canonical_unit="10^3/µL",
        supported_units={"10^3/µl", "10^3/ul", "10^9/l", "cells/mcl", "/ul", "thou/ul"},
        min_biological_value=5.0,
        max_biological_value=2000.0,
        critical_low_threshold=50.0,
        critical_high_threshold=1000.0,
        description="Thrombocyte count critical for hemostasis.",
    ),
    CanonicalBiomarker.ALT: BiomarkerMetadata(
        canonical_id=CanonicalBiomarker.ALT,
        display_name="Alanine Aminotransferase (ALT / SGPT)",
        canonical_unit="U/L",
        supported_units={"u/l", "iu/l", "µkat/l", "ukat/l"},
        min_biological_value=1.0,
        max_biological_value=5000.0,
        critical_high_threshold=500.0,
        description="Hepatocellular enzyme marker for acute hepatic injury.",
    ),
    CanonicalBiomarker.AST: BiomarkerMetadata(
        canonical_id=CanonicalBiomarker.AST,
        display_name="Aspartate Aminotransferase (AST / SGOT)",
        canonical_unit="U/L",
        supported_units={"u/l", "iu/l", "µkat/l", "ukat/l"},
        min_biological_value=1.0,
        max_biological_value=5000.0,
        critical_high_threshold=500.0,
        description="Mitochondrial and cytoplasmic enzyme present in liver, heart, and muscle.",
    ),
    CanonicalBiomarker.SODIUM: BiomarkerMetadata(
        canonical_id=CanonicalBiomarker.SODIUM,
        display_name="Serum Sodium (Na+)",
        canonical_unit="mmol/L",
        supported_units={"mmol/l", "meq/l"},
        min_biological_value=90.0,
        max_biological_value=190.0,
        critical_low_threshold=120.0,
        critical_high_threshold=160.0,
        description="Primary extracellular cation determining plasma tonicity and volume.",
    ),
    CanonicalBiomarker.POTASSIUM: BiomarkerMetadata(
        canonical_id=CanonicalBiomarker.POTASSIUM,
        display_name="Serum Potassium (K+)",
        canonical_unit="mmol/L",
        supported_units={"mmol/l", "meq/l"},
        min_biological_value=1.0,
        max_biological_value=10.0,
        critical_low_threshold=2.8,
        critical_high_threshold=6.2,
        description="Primary intracellular cation regulating myocardial membrane excitability.",
    ),
    CanonicalBiomarker.SYSTOLIC_BP: BiomarkerMetadata(
        canonical_id=CanonicalBiomarker.SYSTOLIC_BP,
        display_name="Systolic Blood Pressure",
        canonical_unit="mmHg",
        supported_units={"mmhg", "torr", "kpa"},
        min_biological_value=40.0,
        max_biological_value=300.0,
        critical_low_threshold=70.0,
        critical_high_threshold=180.0,
        description="Peak arterial pressure during cardiac ventricular contraction.",
    ),
    CanonicalBiomarker.DIASTOLIC_BP: BiomarkerMetadata(
        canonical_id=CanonicalBiomarker.DIASTOLIC_BP,
        display_name="Diastolic Blood Pressure",
        canonical_unit="mmHg",
        supported_units={"mmhg", "torr", "kpa"},
        min_biological_value=20.0,
        max_biological_value=200.0,
        critical_low_threshold=40.0,
        critical_high_threshold=120.0,
        description="Minimum arterial pressure during cardiac ventricular relaxation.",
    ),
}
