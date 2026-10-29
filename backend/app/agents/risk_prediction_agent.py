"""Risk Prediction Ensemble Specialist Clinical Agent for MedOracle (Step 10.5).

Specializes in:
1. Ensembling deterministic clinical equations (Framingham 10-Yr CVD, FINDRISC Diabetes, CKD-EPI 2021 eGFR).
2. Synthesizing trained machine learning classifiers (Gradient Boosting CVD, Random Forest Diabetes, 41-class NB differential).
3. Detecting and reconciling clinical contradictions between mathematical equations and ML predictions.
4. Integrating domain agent findings (Symptom, Medical History, Laboratory) into a cohesive risk assessment.
5. Gracefully handling missing quantitative risk vectors under epistemic uncertainty.
6. Formulating cross-domain adversarial challenges for the Multi-Agent Consensus & Debate Protocol (Step 12).
"""

from datetime import datetime, timezone
import logging
from typing import Any, Dict, List, Optional, Tuple

from app.agents.base import AgentExecutionError, BaseClinicalAgent
from app.clinical.cardiovascular import calculate_framingham_10yr_cvd
from app.clinical.diabetes import calculate_findrisc_score
from app.clinical.kidney import calculate_ckd_epi_2021
from app.ml.inference.predictor import RealtimePredictor
from app.schemas.analysis import AgentOutputResponse
from app.services.llm_service import LLMService

logger = logging.getLogger("agents.risk_prediction")


class RiskPredictionAgent(BaseClinicalAgent):
    """Domain reasoning agent dedicated to quantitative risk synthesis, ML-deterministic ensembles, and contradiction resolution."""

    def __init__(self, llm_service: Optional[LLMService] = None):
        super().__init__(llm_service=llm_service)

    @property
    def agent_role(self) -> str:
        return "Risk Prediction Ensemble Specialist"

    @property
    def system_prompt(self) -> str:
        return (
            "You are an expert Clinical Epidemiologist, Biostatistician, and Risk Prediction Ensemble Specialist "
            "within the MedOracle multi-agent clinical reasoning platform.\n\n"
            "YOUR RESPONSIBILITIES:\n"
            "1. Synthesize quantitative outputs from both DETERMINISTIC CLINICAL FORMULAS (Framingham 10-Yr CVD %, "
            "FINDRISC 10-Yr Diabetes Score, CKD-EPI 2021 eGFR) and TRAINED MACHINE LEARNING MODELS (Gradient Boosting CVD %, "
            "Random Forest Diabetes %, Multinomial Naive Bayes 41-class differential).\n"
            "2. Identify and explicitly reconcile CLINICAL CONTRADICTIONS (e.g. Framingham predicts 'Low Risk' due to younger age, "
            "but the ML classifier predicts 'High Risk' due to non-linear interaction of severe hypertension, smoking, and family history).\n"
            "3. Cross-reference quantitative predictions against qualitative findings from upstream specialist agents "
            "(Symptom Analysis Specialist, Medical History Specialist, Laboratory Biomarker Specialist).\n"
            "4. If clinical scores or ML predictions are missing/unrecorded, acknowledge the quantitative modeling gap, "
            "operate under epistemic uncertainty with discounted confidence, and demand baseline biometric inputs.\n"
            "5. Prepare the definitive risk baseline for the Multi-Agent Consensus and Debate Protocol, highlighting where clinical "
            "consensus is robust versus where diagnostic doubt remains.\n\n"
            "OUTPUT REQUIREMENTS:\n"
            "- agent_role: Exactly 'Risk Prediction Ensemble Specialist'.\n"
            "- findings: 2-3 sentence multi-model ensemble synthesis of composite cardiovascular, metabolic, and renal risk.\n"
            "- confidence: Numerical score (0.0 to 100.0) reflecting the mathematical and clinical concordance across models.\n"
            "- reasoning_chain: 3-5 concise, clinical logic steps explaining how deterministic equations, ML predictions, and agent findings coalesce.\n"
            "- evidence: Explicitly list verified quantitative metrics (percentages, scores, eGFR numbers, and top driving risk factors).\n"
            "- challenges: 2-4 critical clinical contradictions, statistical limitations, or missing longitudinal markers required for debate resolution."
        )

    def has_quantitative_data(self, context: Dict[str, Any]) -> bool:
        """Verify whether any clinical risk score, ML prediction, or raw patient parameter is present."""
        if context.get("clinical_scores") or context.get("ml_predictions"):
            return True
        if context.get("framingham_risk_percent") is not None or context.get("findrisc_score") is not None:
            return True
        if context.get("cardio_risk_percent") is not None or context.get("diabetes_risk_percent") is not None:
            return True

        # Check if raw parameters exist to compute scores
        has_demo = bool(context.get("age") or (context.get("patient_demographics") and context["patient_demographics"].get("age")))
        has_bio = bool(context.get("biomarkers")) or any(
            k in context for k in ["systolic_bp", "fasting_blood_glucose_mg_dl", "total_cholesterol_mg_dl", "serum_creatinine_mg_dl"]
        )
        return has_demo and has_bio

    def validate_context(self, context: Dict[str, Any]) -> None:
        """Verify context format.

        Permits empty or missing risk contexts to support de novo patient presentations
        or uncomputed cases gracefully under epistemic uncertainty.
        """
        super().validate_context(context)

    def analyze(
        self,
        context: Dict[str, Any],
        provider: Optional[str] = None,
        use_cache: bool = True,
    ) -> AgentOutputResponse:
        """Execute risk ensemble reasoning with automated epistemic uncertainty adjustments."""
        output = super().analyze(context=context, provider=provider, use_cache=use_cache)

        # If quantitative risk vectors and raw patient data are absent, enforce epistemic discounting
        if not self.has_quantitative_data(context):
            if output.confidence > 35.0:
                output.confidence = 25.0

            missing_marker = "No quantitative risk calculations (Framingham, FINDRISC, CKD-EPI) or trained ML predictions available (modeling gap)."
            if missing_marker not in output.evidence:
                output.evidence.insert(0, missing_marker)

            intake_challenge = "Obtain complete baseline parameters (age, resting blood pressure, fasting lipid panel, glucose, creatinine) to compute validated risk models."
            if intake_challenge not in output.challenges:
                output.challenges.insert(0, intake_challenge)

        return output

    def build_prompt(self, context: Dict[str, Any]) -> str:
        """Construct structured clinical briefing ensembling deterministic equations, ML models, and agent findings."""
        lines: List[str] = ["# PATIENT QUANTITATIVE RISK ENSEMBLE BRIEFING\n"]

        # 1. Demographics
        demo = context.get("patient_demographics") or {}
        age = demo.get("age", context.get("age", "Unknown"))
        sex = demo.get("sex", context.get("sex", "Unknown"))
        lines.append(f"**Patient Demographics:** Age: {age} | Biological Sex: {sex}\n")

        # 2. Check if quantitative data is absent
        if not self.has_quantitative_data(context):
            lines.append("## ⚠️ CLINICAL STATUS: QUANTITATIVE RISK MODELS UNAVAILABLE / UNRECORDED")
            lines.append(
                "- **Status:** No deterministic clinical risk scores (Framingham, FINDRISC, CKD-EPI) or trained machine learning predictions are on file.\n"
                "- **Clinical Reality:** Patient has not undergone multi-model risk assessment, and insufficient baseline biometrics exist to auto-compute scores.\n"
                "- **Epistemic Uncertainty Guidance:**\n"
                "  1. Cannot reliably quantify 10-year cardiovascular or diabetes event likelihood without validated scoring inputs.\n"
                "  2. Apply a strict confidence penalty (confidence between 20.0 and 30.0) reflecting the complete absence of statistical models.\n"
                "  3. In `findings`, synthesize that risk stratification is severely constrained by missing quantitative endpoints.\n"
                "  4. In `reasoning_chain`, highlight that mathematical risk algorithms cannot be calculated without blood pressure, lipids, and glycemic indices.\n"
                "  5. In `evidence`, state that no validated risk percentages or scoring brackets are documented.\n"
                "  6. In `challenges`, demand essential biometric measurements to enable multi-model risk computation."
            )
            lines.append("")
            return "\n".join(lines)

        # 3. Deterministic Clinical Risk Equations (Step 5)
        lines.append("## 1. Deterministic Clinical Risk Equations")
        clinical_scores = context.get("clinical_scores") or {}

        # Framingham
        fram_pct = clinical_scores.get("framingham_risk_percent", context.get("framingham_risk_percent"))
        fram_cat = clinical_scores.get("framingham_risk_category", context.get("framingham_risk_category"))
        if fram_pct is not None:
            cat_str = f" ({fram_cat.title()})" if fram_cat else ""
            lines.append(f"- **Framingham 10-Yr General CVD Risk:** {round(float(fram_pct), 1)}%{cat_str}")
        else:
            lines.append("- Framingham 10-Yr CVD Risk: Uncomputed")

        # FINDRISC
        find_pts = clinical_scores.get("findrisc_score", context.get("findrisc_score"))
        find_cat = clinical_scores.get("findrisc_risk_category", context.get("findrisc_risk_category"))
        if find_pts is not None:
            cat_str = f" ({find_cat.title()})" if find_cat else ""
            lines.append(f"- **FINDRISC 10-Yr Type 2 Diabetes Score:** {find_pts}/26 points{cat_str}")
        else:
            lines.append("- FINDRISC Diabetes Score: Uncomputed")

        # CKD-EPI
        egfr_val = clinical_scores.get("ckd_epi_egfr", context.get("ckd_epi_egfr") or context.get("estimated_gfr"))
        ckd_stg = clinical_scores.get("ckd_stage", context.get("ckd_stage"))
        if egfr_val is not None:
            stg_str = f" ({ckd_stg})" if ckd_stg else ""
            lines.append(f"- **CKD-EPI 2021 eGFR:** {round(float(egfr_val), 1)} mL/min/1.73m²{stg_str}")
        else:
            lines.append("- CKD-EPI 2021 eGFR: Uncomputed")
        lines.append("")

        # 4. Trained Statistical ML Models (Step 8)
        lines.append("## 2. Trained Machine Learning Classifier Predictions")
        ml_preds = context.get("ml_predictions") or {}

        # Cardiovascular ML Model (Gradient Boosting)
        cardio_ml = ml_preds.get("cardiovascular_risk_percent", context.get("cardio_risk_percent"))
        cardio_cat = ml_preds.get("cardiovascular_risk_category", context.get("cardio_risk_category"))
        if cardio_ml is not None:
            cat_str = f" ({cardio_cat.title()})" if cardio_cat else ""
            lines.append(f"- **Gradient Boosting Cardiovascular Model:** {round(float(cardio_ml), 1)}% probability{cat_str}")
        else:
            lines.append("- Gradient Boosting CVD Model: Not executed")

        # Diabetes ML Model (Random Forest)
        diab_ml = ml_preds.get("diabetes_risk_percent", context.get("diabetes_risk_percent"))
        diab_cat = ml_preds.get("diabetes_risk_category", context.get("diabetes_risk_category"))
        if diab_ml is not None:
            cat_str = f" ({diab_cat.title()})" if diab_cat else ""
            lines.append(f"- **Random Forest Metabolic Diabetes Model:** {round(float(diab_ml), 1)}% probability{cat_str}")
        else:
            lines.append("- Random Forest Diabetes Model: Not executed")

        # 41-Class Naive Bayes Differential Candidates
        diff_cands = ml_preds.get("top_differential_conditions", context.get("differential_candidates") or [])
        if diff_cands:
            lines.append("- **Top Statistical Differential Candidates (Naive Bayes):**")
            for i, cand in enumerate(diff_cands[:3], start=1):
                d_name = cand.get("disease", "Unknown").replace("_", " ").title()
                d_prob = cand.get("probability", 0.0)
                lines.append(f"  {i}. {d_name} ({round(float(d_prob) * 100, 1)}%)")
        lines.append("")

        # 5. Model Discrepancy & Discordance Detection
        discordances: List[str] = []
        if fram_pct is not None and cardio_ml is not None:
            diff = abs(float(cardio_ml) - float(fram_pct))
            if diff >= 25.0:
                discordances.append(
                    f"⚡ **Cardiovascular Model Discordance ({round(diff, 1)}% gap):** "
                    f"Framingham deterministic risk is {round(float(fram_pct), 1)}% vs. Gradient Boosting ML prediction {round(float(cardio_ml), 1)}%. "
                    "Determine whether non-linear risk interactions or unmeasured factors drive this divergence."
                )

        if find_pts is not None and diab_ml is not None:
            find_high = int(find_pts) >= 15
            ml_high = float(diab_ml) >= 50.0
            if find_high != ml_high:
                discordances.append(
                    f"⚡ **Metabolic Diabetes Model Discordance:** "
                    f"FINDRISC score of {find_pts}/26 points conflicts with Random Forest ML prediction of {round(float(diab_ml), 1)}%. "
                    "Cross-reference objective glycemic biomarkers (FBG/HbA1c) to resolve."
                )

        if discordances:
            lines.append("## 3. Automated Model Discordance Flags")
            for disc in discordances:
                lines.append(disc)
            lines.append("")

        # 6. Upstream Domain Specialist Contexts
        agent_findings = context.get("agent_findings") or {}
        symptom_find = agent_findings.get("symptom_findings") or context.get("symptom_findings")
        history_find = agent_findings.get("medical_history_findings") or context.get("medical_history_findings")
        lab_find = agent_findings.get("laboratory_findings") or context.get("laboratory_findings")

        if symptom_find or history_find or lab_find:
            lines.append("## 4. Upstream Domain Specialist Findings")
            if symptom_find:
                lines.append(f"- **Symptom Specialist:** \"{symptom_find}\"")
            if history_find:
                lines.append(f"- **Medical History Specialist:** \"{history_find}\"")
            if lab_find:
                lines.append(f"- **Laboratory Specialist:** \"{lab_find}\"")
            lines.append("")

        lines.append(
            "Synthesize these quantitative mathematical models, ML classifications, and domain findings into a unified ensemble. "
            "Articulate a rigorous reasoning chain that reconciles any discrepancies between clinical equations and ML models, "
            "and formulate sharp challenges for the Multi-Agent Consensus Debate."
        )

        return "\n".join(lines)
