"""CKD-EPI 2021 Race-Free Creatinine Equation for Estimated Glomerular Filtration Rate (eGFR).

Implementation of the race-free CKD-EPI 2021 equation recommended by the National Kidney
Foundation (NKF) and American Society of Nephrology (ASN) Task Force.

Citation:
    Inker LA, Eneanya ND, Coresh J, Tighiouart H, Wang D, Sang Y, et al.
    New Creatinine- and Cystatin C-Based Equations to Estimate GFR without Race.
    N Engl J Med. 2021 Nov 4;385(19):1737-1749. doi: 10.1056/NEJMoa2102953.
"""

import math
from typing import Any, Dict, Literal

DISCLAIMER: str = (
    "MedOracle is a decision-support assistant and does not provide clinical diagnosis. "
    "Consult a qualified healthcare professional."
)


def calculate_ckd_epi_2021(
    serum_creatinine_mg_dl: float,
    age: int,
    gender: Literal["male", "female"],
) -> Dict[str, Any]:
    """Calculate race-free eGFR using the CKD-EPI 2021 equation.

    Formula:
        eGFR = 142 * min(Scr / kappa, 1)^alpha * max(Scr / kappa, 1)^(-1.200) *
               (0.9938^Age) * (1.012 if female else 1.0)

    Args:
        serum_creatinine_mg_dl: Serum creatinine in mg/dL (must be > 0).
        age: Age in years (must be >= 18).
        gender: Biological sex ('male' or 'female').

    Returns:
        Dict with model name, egfr_ml_min_1_73m2, kdigo_stage, stage_description,
        and disclaimer.
    """
    if serum_creatinine_mg_dl <= 0:
        raise ValueError("Serum creatinine must be a positive number.")
    if age < 18 or age > 120:
        raise ValueError("Age must be between 18 and 120 years.")

    if gender == "female":
        kappa = 0.7
        alpha = -0.241
        sex_factor = 1.012
    else:  # male
        kappa = 0.9
        alpha = -0.302
        sex_factor = 1.0

    scr_over_kappa = serum_creatinine_mg_dl / kappa
    min_term = math.pow(min(scr_over_kappa, 1.0), alpha)
    max_term = math.pow(max(scr_over_kappa, 1.0), -1.200)
    age_term = math.pow(0.9938, age)

    egfr = 142.0 * min_term * max_term * age_term * sex_factor
    egfr_rounded = round(egfr, 1)

    # KDIGO 2012 Clinical Staging
    if egfr_rounded >= 90.0:
        kdigo_stage = "G1"
        stage_description = "Normal or high kidney function"
        clinical_severity = "normal"
    elif egfr_rounded >= 60.0:
        kdigo_stage = "G2"
        stage_description = "Mildly decreased kidney function"
        clinical_severity = "mild"
    elif egfr_rounded >= 45.0:
        kdigo_stage = "G3a"
        stage_description = "Mildly to moderately decreased kidney function"
        clinical_severity = "moderate"
    elif egfr_rounded >= 30.0:
        kdigo_stage = "G3b"
        stage_description = "Moderately to severely decreased kidney function"
        clinical_severity = "substantial"
    elif egfr_rounded >= 15.0:
        kdigo_stage = "G4"
        stage_description = "Severely decreased kidney function"
        clinical_severity = "severe"
    else:
        kdigo_stage = "G5"
        stage_description = "Kidney failure / End-stage renal disease"
        clinical_severity = "critical"

    return {
        "model": "CKD-EPI 2021 Race-Free Creatinine eGFR (Inker 2021)",
        "egfr_ml_min_1_73m2": egfr_rounded,
        "kdigo_stage": kdigo_stage,
        "stage_description": stage_description,
        "clinical_severity": clinical_severity,
        "parameters": {
            "serum_creatinine_mg_dl": serum_creatinine_mg_dl,
            "age": age,
            "gender": gender,
        },
        "disclaimer": DISCLAIMER,
    }
