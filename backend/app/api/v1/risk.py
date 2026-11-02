"""Pure clinical risk model calculation endpoints."""

from fastapi import APIRouter, Depends, status

from app.clinical.cardiovascular import calculate_framingham_10yr_cvd
from app.clinical.diabetes import calculate_findrisc_score
from app.clinical.kidney import calculate_ckd_epi_2021
from app.core.security import get_current_user
from app.database.models import User
from app.schemas.risk import (
    CkdEpiRequest,
    CkdEpiResponse,
    FindriscRequest,
    FindriscResponse,
    FraminghamRiskRequest,
    FraminghamRiskResponse,
)

router = APIRouter(prefix="/risk", tags=["Clinical Risk"])


@router.post(
    "/cardiovascular",
    response_model=FraminghamRiskResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate Framingham 10-Year Cardiovascular Disease Risk",
)
def compute_cardiovascular_risk(
    payload: FraminghamRiskRequest,
    current_user: User = Depends(get_current_user),
) -> FraminghamRiskResponse:
    """Calculate 10-year general CVD risk using published D'Agostino et al. (2008) Cox regression."""
    result = calculate_framingham_10yr_cvd(
        age=payload.age,
        gender=payload.gender,
        total_cholesterol_mg_dl=payload.total_cholesterol_mg_dl,
        hdl_cholesterol_mg_dl=payload.hdl_cholesterol_mg_dl,
        systolic_bp=payload.systolic_bp,
        is_treated_for_hypertension=payload.is_treated_for_hypertension,
        is_smoker=payload.is_smoker,
        has_diabetes=payload.has_diabetes,
    )
    return FraminghamRiskResponse(**result)


@router.post(
    "/diabetes",
    response_model=FindriscResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate FINDRISC 10-Year Type 2 Diabetes Risk",
)
def compute_diabetes_risk(
    payload: FindriscRequest,
    current_user: User = Depends(get_current_user),
) -> FindriscResponse:
    """Calculate 10-year Type 2 diabetes risk using the validated Finnish Diabetes Risk Score."""
    result = calculate_findrisc_score(
        age=payload.age,
        gender=payload.gender,
        bmi=payload.bmi,
        height_cm=payload.height_cm,
        weight_kg=payload.weight_kg,
        waist_circumference_cm=payload.waist_circumference_cm,
        physical_activity_30min_daily=payload.daily_physical_activity_30min,
        daily_fruit_veg_intake=payload.daily_vegetable_fruit_intake,
        takes_hypertension_meds=payload.takes_antihypertensive_meds,
        history_high_blood_glucose=payload.history_of_high_blood_glucose,
        family_history_diabetes=payload.family_history_of_diabetes,
    )
    return FindriscResponse(**result)


@router.post(
    "/kidney",
    response_model=CkdEpiResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate CKD-EPI 2021 Race-Free eGFR & KDIGO Staging",
)
def compute_kidney_function(
    payload: CkdEpiRequest,
    current_user: User = Depends(get_current_user),
) -> CkdEpiResponse:
    """Calculate race-free eGFR and chronic kidney disease staging via CKD-EPI 2021 equation."""
    result = calculate_ckd_epi_2021(
        serum_creatinine_mg_dl=payload.serum_creatinine_mg_dl,
        age=payload.age,
        gender=payload.gender,
    )
    return CkdEpiResponse(**result)
