"""Unit tests for deterministic clinical risk models (Step 5).

Verifies equations, coefficients, edge cases, and disclaimer adherence for:
1. Framingham 10-Year General CVD Risk (D'Agostino 2008)
2. FINDRISC Type 2 Diabetes Score (Lindström 2003)
3. CKD-EPI 2021 Race-Free Creatinine eGFR (Inker 2021)
"""

import pytest
from app.clinical.cardiovascular import calculate_framingham_10yr_cvd
from app.clinical.diabetes import calculate_findrisc_score
from app.clinical.kidney import calculate_ckd_epi_2021


class TestFraminghamModel:
    """Test suite for Framingham 10-Year CVD Risk Calculation."""

    def test_male_high_risk_profile(self):
        """A 55yo male smoker with hypertension, high cholesterol, low HDL, and diabetes."""
        result = calculate_framingham_10yr_cvd(
            age=55,
            gender="male",
            total_cholesterol_mg_dl=240.0,
            hdl_cholesterol_mg_dl=38.0,
            systolic_bp=145.0,
            is_treated_for_hypertension=True,
            is_smoker=True,
            has_diabetes=True,
        )

        assert result["risk_category"] == "high"
        assert result["risk_score_percent"] > 20.0
        assert "disclaimer" in result
        assert "MedOracle is a decision-support assistant" in result["disclaimer"]

    def test_female_low_risk_profile(self):
        """A 35yo non-smoking female with optimal lipids and blood pressure."""
        result = calculate_framingham_10yr_cvd(
            age=35,
            gender="female",
            total_cholesterol_mg_dl=170.0,
            hdl_cholesterol_mg_dl=65.0,
            systolic_bp=110.0,
            is_treated_for_hypertension=False,
            is_smoker=False,
            has_diabetes=False,
        )

        assert result["risk_category"] == "low"
        assert result["risk_score_percent"] < 5.0
        assert "D'Agostino 2008" in result["model"]

    def test_invalid_parameters_raise_value_error(self):
        """Out-of-bound age and non-positive numbers must raise ValueError."""
        with pytest.raises(ValueError, match="Age must be between 20 and 100"):
            calculate_framingham_10yr_cvd(
                age=15,
                gender="male",
                total_cholesterol_mg_dl=200,
                hdl_cholesterol_mg_dl=50,
                systolic_bp=120,
                is_treated_for_hypertension=False,
                is_smoker=False,
                has_diabetes=False,
            )

        with pytest.raises(ValueError, match="Cholesterol values must be positive"):
            calculate_framingham_10yr_cvd(
                age=45,
                gender="male",
                total_cholesterol_mg_dl=-200,
                hdl_cholesterol_mg_dl=50,
                systolic_bp=120,
                is_treated_for_hypertension=False,
                is_smoker=False,
                has_diabetes=False,
            )


class TestFindriscModel:
    """Test suite for FINDRISC 10-Year Diabetes Score."""

    def test_minimal_points_healthy_profile(self):
        """Young healthy subject with all 0-point categories."""
        result = calculate_findrisc_score(
            age=30,
            gender="male",
            bmi=22.0,
            waist_circumference_cm=80.0,
            physical_activity_30min_daily=True,
            daily_fruit_veg_intake=True,
            takes_hypertension_meds=False,
            history_high_blood_glucose=False,
            family_history_diabetes="none",
        )

        assert result["total_score"] == 0
        assert result["risk_category"] == "low"
        assert result["ten_year_risk_percent_approx"] == 1.0
        assert "disclaimer" in result

    def test_maximum_points_profile(self):
        """Patient with maximum risk factor point allocations (score = 26)."""
        result = calculate_findrisc_score(
            age=68,  # 4 pts
            gender="male",
            bmi=34.0,  # 3 pts
            waist_circumference_cm=108.0,  # 4 pts
            physical_activity_30min_daily=False,  # 2 pts
            daily_fruit_veg_intake=False,  # 1 pt
            takes_hypertension_meds=True,  # 2 pts
            history_high_blood_glucose=True,  # 5 pts
            family_history_diabetes="first_degree",  # 5 pts
        )

        assert result["total_score"] == 26
        assert result["risk_category"] == "very_high"
        assert result["ten_year_risk_percent_approx"] == 50.0

    def test_bmi_computation_from_height_and_weight(self):
        """When BMI is omitted, it should be calculated from height and weight."""
        result = calculate_findrisc_score(
            age=50,
            gender="female",
            height_cm=160.0,
            weight_kg=70.0,  # BMI = 70 / (1.6^2) = 27.34 -> 1 pt
            waist_circumference_cm=84.0,  # 3 pts
            physical_activity_30min_daily=True,  # 0 pt
            daily_fruit_veg_intake=True,  # 0 pt
            takes_hypertension_meds=False,  # 0 pt
            history_high_blood_glucose=False,  # 0 pt
            family_history_diabetes="none",  # 0 pt
        )

        # Age 50: 2 pts; BMI ~27.3: 1 pt; Waist 84cm: 3 pts -> Total = 6 pts (low)
        assert result["total_score"] == 6
        assert result["risk_category"] == "low"
        assert result["parameters"]["bmi"] == 27.3


class TestCkdEpiModel:
    """Test suite for CKD-EPI 2021 race-free eGFR calculation."""

    def test_normal_male_renal_function(self):
        """A 30yo male with normal serum creatinine (0.9 mg/dL)."""
        result = calculate_ckd_epi_2021(
            serum_creatinine_mg_dl=0.9,
            age=30,
            gender="male",
        )

        assert result["egfr_ml_min_1_73m2"] >= 90.0
        assert result["kdigo_stage"] == "G1"
        assert result["clinical_severity"] == "normal"
        assert "CKD-EPI 2021" in result["model"]
        assert "disclaimer" in result

    def test_moderate_female_renal_impairment(self):
        """A 65yo female with elevated serum creatinine (1.6 mg/dL)."""
        result = calculate_ckd_epi_2021(
            serum_creatinine_mg_dl=1.6,
            age=65,
            gender="female",
        )

        # Inker 2021 formula: 142 * (1.6/0.7)^-1.2 * 0.9938^65 * 1.012 ≈ 36 mL/min/1.73m2 (Stage G3b)
        assert 30.0 <= result["egfr_ml_min_1_73m2"] < 45.0
        assert result["kdigo_stage"] == "G3b"
        assert result["clinical_severity"] == "substantial"

    def test_kidney_failure_stage_g5(self):
        """A patient with severe renal failure (serum creatinine 6.0 mg/dL)."""
        result = calculate_ckd_epi_2021(
            serum_creatinine_mg_dl=6.0,
            age=55,
            gender="male",
        )

        assert result["egfr_ml_min_1_73m2"] < 15.0
        assert result["kdigo_stage"] == "G5"
        assert result["clinical_severity"] == "critical"

    def test_invalid_creatinine_raises_error(self):
        """Non-positive creatinine must raise ValueError."""
        with pytest.raises(ValueError, match="Serum creatinine must be a positive number"):
            calculate_ckd_epi_2021(
                serum_creatinine_mg_dl=-1.0,
                age=40,
                gender="male",
            )
