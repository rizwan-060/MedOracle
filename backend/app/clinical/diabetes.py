"""FINDRISC (Finnish Diabetes Risk Score) 10-Year Type 2 Diabetes Prediction Model.

Implementation of the clinical point-scoring system developed and validated by
Lindström and Tuomilehto (2003) to predict 10-year risk of developing drug-treated
type 2 diabetes.

Citation:
    Lindström J, Tuomilehto J. The diabetes risk score: a practical tool to predict
    type 2 diabetes risk. Diabetes Care. 2003 Mar;26(3):725-31.
    doi: 10.2337/diacare.26.3.725.
"""

from typing import Any, Dict, List, Literal, Optional

DISCLAIMER: str = (
    "MedOracle is a decision-support assistant and does not provide clinical diagnosis. "
    "Consult a qualified healthcare professional."
)


def calculate_findrisc_score(
    age: int,
    gender: Literal["male", "female"],
    bmi: Optional[float] = None,
    height_cm: Optional[float] = None,
    weight_kg: Optional[float] = None,
    waist_circumference_cm: Optional[float] = None,
    physical_activity_30min_daily: bool = True,
    daily_fruit_veg_intake: bool = True,
    takes_hypertension_meds: bool = False,
    history_high_blood_glucose: bool = False,
    family_history_diabetes: Literal["none", "second_degree", "first_degree"] = "none",
) -> Dict[str, Any]:
    """Calculate the Finnish Diabetes Risk Score (0 to 26 points) and 10-year risk tier.

    Args:
        age: Age in years.
        gender: Biological sex ('male' or 'female') used for waist thresholds.
        bmi: Body Mass Index in kg/m2 (optional if height_cm and weight_kg provided).
        height_cm: Height in cm (used to calculate BMI if bmi not given).
        weight_kg: Weight in kg (used to calculate BMI if bmi not given).
        waist_circumference_cm: Waist circumference measured at umbilicus level.
        physical_activity_30min_daily: At least 30 minutes of physical activity daily.
        daily_fruit_veg_intake: Consumes vegetables, fruits, or berries every day.
        takes_hypertension_meds: Regular consumption of antihypertensive drugs.
        history_high_blood_glucose: Past history of high blood glucose (e.g. checkup, pregnancy).
        family_history_diabetes: Family history of diabetes ('none', 'second_degree', 'first_degree').

    Returns:
        Dict containing total_score (0-26), 10_year_risk_percent_approx, risk_category,
        points_breakdown, and disclaimer.
    """
    if age < 18 or age > 110:
        raise ValueError("Age must be between 18 and 110 years.")

    missing_or_assumed: List[str] = []

    # Calculate BMI if needed
    computed_bmi = bmi
    if computed_bmi is None:
        if height_cm and weight_kg and height_cm > 0 and weight_kg > 0:
            height_m = height_cm / 100.0
            computed_bmi = round(weight_kg / (height_m * height_m), 1)
        else:
            computed_bmi = 24.5  # Assumed healthy reference
            missing_or_assumed.append("BMI calculated with assumed reference of 24.5 kg/m2")

    # 1. Age points (0 to 4)
    if age < 45:
        age_points = 0
    elif 45 <= age <= 54:
        age_points = 2
    elif 55 <= age <= 64:
        age_points = 3
    else:  # >= 65
        age_points = 4

    # 2. BMI points (0 to 3)
    if computed_bmi < 25.0:
        bmi_points = 0
    elif 25.0 <= computed_bmi <= 30.0:
        bmi_points = 1
    else:  # > 30.0
        bmi_points = 3

    # 3. Waist circumference points (0 to 4, sex-stratified)
    if waist_circumference_cm is None:
        # Default assumed normal
        waist_circumference_cm = 85.0 if gender == "male" else 75.0
        missing_or_assumed.append(
            f"Waist circumference assumed average normal ({waist_circumference_cm} cm)"
        )

    if gender == "male":
        if waist_circumference_cm < 94.0:
            waist_points = 0
        elif 94.0 <= waist_circumference_cm <= 102.0:
            waist_points = 3
        else:
            waist_points = 4
    else:  # female
        if waist_circumference_cm < 80.0:
            waist_points = 0
        elif 80.0 <= waist_circumference_cm <= 88.0:
            waist_points = 3
        else:
            waist_points = 4

    # 4. Physical activity points (0 or 2)
    activity_points = 0 if physical_activity_30min_daily else 2

    # 5. Diet points (0 or 1)
    diet_points = 0 if daily_fruit_veg_intake else 1

    # 6. Antihypertensive medication points (0 or 2)
    bp_med_points = 2 if takes_hypertension_meds else 0

    # 7. History of high blood glucose (0 or 5)
    glucose_history_points = 5 if history_high_blood_glucose else 0

    # 8. Family history points (0, 3, or 5)
    if family_history_diabetes == "first_degree":
        family_points = 5
    elif family_history_diabetes == "second_degree":
        family_points = 3
    else:
        family_points = 0

    total_score = (
        age_points
        + bmi_points
        + waist_points
        + activity_points
        + diet_points
        + bp_med_points
        + glucose_history_points
        + family_points
    )

    # Risk tiers according to Lindström & Tuomilehto (2003):
    if total_score < 7:
        risk_category = "low"
        ten_year_risk_approx = 1.0  # ~1% (1 in 100)
    elif 7 <= total_score <= 11:
        risk_category = "slightly_elevated"
        ten_year_risk_approx = 4.0  # ~4% (1 in 25)
    elif 12 <= total_score <= 14:
        risk_category = "moderate"
        ten_year_risk_approx = 17.0  # ~17% (1 in 6)
    elif 15 <= total_score <= 20:
        risk_category = "high"
        ten_year_risk_approx = 33.0  # ~33% (1 in 3)
    else:  # > 20
        risk_category = "very_high"
        ten_year_risk_approx = 50.0  # ~50% (1 in 2)

    return {
        "model": "FINDRISC Type 2 Diabetes 10-Year Risk (Lindström 2003)",
        "total_score": total_score,
        "max_score": 26,
        "risk_category": risk_category,
        "ten_year_risk_percent_approx": ten_year_risk_approx,
        "missing_or_assumed": missing_or_assumed,
        "points_breakdown": {
            "age": age_points,
            "bmi": bmi_points,
            "waist_circumference": waist_points,
            "physical_activity": activity_points,
            "vegetables_fruit": diet_points,
            "hypertension_meds": bp_med_points,
            "high_blood_glucose_history": glucose_history_points,
            "family_history": family_points,
        },
        "parameters": {
            "age": age,
            "gender": gender,
            "bmi": computed_bmi,
            "waist_circumference_cm": waist_circumference_cm,
            "physical_activity_30min_daily": physical_activity_30min_daily,
            "daily_fruit_veg_intake": daily_fruit_veg_intake,
            "takes_hypertension_meds": takes_hypertension_meds,
            "history_high_blood_glucose": history_high_blood_glucose,
            "family_history_diabetes": family_history_diabetes,
        },
        "disclaimer": DISCLAIMER,
    }
