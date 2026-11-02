"""Framingham 10-Year Cardiovascular Disease (CVD) Risk Model.

Implementation of the 2008 Framingham General Cardiovascular Risk algorithm using
multivariable Cox proportional-hazards regression models.

Citation:
    D'Agostino RB Sr, Vasan RS, Pencina MJ, Wolf PA, Cobain M, Massaro JM, Kannel WB.
    General cardiovascular risk profile for use in primary care: the Framingham Heart Study.
    Circulation. 2008 Feb 12;117(6):743-53. doi: 10.1161/CIRCULATIONAHA.107.699579.
"""

import math
from typing import Any, Dict, List, Literal, Tuple

DISCLAIMER: str = (
    "MedOracle is a decision-support assistant and does not provide clinical diagnosis. "
    "Consult a qualified healthcare professional."
)


def calculate_framingham_10yr_cvd(
    age: int,
    gender: Literal["male", "female"],
    total_cholesterol_mg_dl: float,
    hdl_cholesterol_mg_dl: float,
    systolic_bp: float,
    is_treated_for_hypertension: bool,
    is_smoker: bool,
    has_diabetes: bool,
) -> Dict[str, Any]:
    """Calculate 10-year general cardiovascular disease risk percentage.

    Uses the continuous multivariable Cox regression model from D'Agostino et al. (2008),
    Table 4 (lipids-based model).

    Args:
        age: Age in years (validated range 30-79).
        gender: Patient biological sex ('male' or 'female').
        total_cholesterol_mg_dl: Total serum cholesterol in mg/dL.
        hdl_cholesterol_mg_dl: High-density lipoprotein cholesterol in mg/dL.
        systolic_bp: Systolic blood pressure in mmHg.
        is_treated_for_hypertension: Whether the patient is on antihypertensive medication.
        is_smoker: Current cigarette smoking status.
        has_diabetes: Diagnosis of type 1 or type 2 diabetes.

    Returns:
        Dict with model name, risk_score_percent, risk_category, factors, and disclaimer.
    """
    if age < 20 or age > 100:
        raise ValueError("Age must be between 20 and 100 years.")
    if total_cholesterol_mg_dl <= 0 or hdl_cholesterol_mg_dl <= 0:
        raise ValueError("Cholesterol values must be positive.")
    if systolic_bp <= 0:
        raise ValueError("Systolic blood pressure must be positive.")

    ln_age = math.log(age)
    ln_tc = math.log(total_cholesterol_mg_dl)
    ln_hdl = math.log(hdl_cholesterol_mg_dl)
    ln_sbp = math.log(systolic_bp)

    missing_or_assumed: List[str] = []

    if gender == "male":
        # Table 4 Male Lipid-based Model Coefficients
        beta_age = 3.06117
        beta_tc = 1.12370
        beta_hdl = -0.93263
        beta_sbp = 1.99881 if is_treated_for_hypertension else 1.93303
        beta_smoker = 0.65451 if is_smoker else 0.0
        beta_diabetes = 0.57367 if has_diabetes else 0.0

        mean_linear_predictor = 23.9802
        baseline_survival_10yr = 0.88936

        linear_predictor = (
            beta_age * ln_age
            + beta_tc * ln_tc
            + beta_hdl * ln_hdl
            + beta_sbp * ln_sbp
            + beta_smoker
            + beta_diabetes
        )
    else:
        # Table 4 Female Lipid-based Model Coefficients
        beta_age = 2.32888
        beta_tc = 1.20904
        beta_hdl = -0.70833
        beta_sbp = 2.82263 if is_treated_for_hypertension else 2.76157
        beta_smoker = 0.52873 if is_smoker else 0.0
        beta_diabetes = 0.69154 if has_diabetes else 0.0

        mean_linear_predictor = 26.1931
        baseline_survival_10yr = 0.95012

        linear_predictor = (
            beta_age * ln_age
            + beta_tc * ln_tc
            + beta_hdl * ln_hdl
            + beta_sbp * ln_sbp
            + beta_smoker
            + beta_diabetes
        )

    exponent = linear_predictor - mean_linear_predictor
    risk = 1.0 - math.pow(baseline_survival_10yr, math.exp(exponent))
    risk_percent = round(max(0.0, min(100.0, risk * 100.0)), 2)

    # Risk categorization
    if risk_percent < 10.0:
        risk_category = "low"
    elif risk_percent < 20.0:
        risk_category = "moderate"
    else:
        risk_category = "high"

    return {
        "model": "Framingham 10-Year General Cardiovascular Risk (D'Agostino 2008)",
        "risk_score_percent": risk_percent,
        "risk_category": risk_category,
        "missing_or_assumed": missing_or_assumed,
        "parameters": {
            "age": age,
            "gender": gender,
            "total_cholesterol_mg_dl": total_cholesterol_mg_dl,
            "hdl_cholesterol_mg_dl": hdl_cholesterol_mg_dl,
            "systolic_bp": systolic_bp,
            "is_treated_for_hypertension": is_treated_for_hypertension,
            "is_smoker": is_smoker,
            "has_diabetes": has_diabetes,
        },
        "disclaimer": DISCLAIMER,
    }
