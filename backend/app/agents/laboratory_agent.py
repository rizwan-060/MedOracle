"""Laboratory Biomarker Specialist Clinical Agent for MedOracle (Step 10.4).

Specializes in:
1. Quantitative objective evaluation of metabolic, glycemic, lipid, and renal panels.
2. Clinical threshold stratification (AHA/ACC, ADA, ATP III, KDIGO).
3. Detecting biomarker discordance (e.g. FBG vs. HbA1c, atherogenic dyslipidemia).
4. Automated safety alerts for hypertensive crisis, severe hyperglycemia, and renal decline.
5. Graceful handling of missing or unavailable laboratory panels under epistemic uncertainty.
6. Formulating adversarial cross-examination challenges for Symptom, History, and Risk agents.
"""

from datetime import datetime, timezone
import logging
from typing import Any, Dict, List, Optional, Tuple

from app.agents.base import AgentExecutionError, BaseClinicalAgent
from app.schemas.analysis import AgentOutputResponse
from app.services.llm_service import LLMService

logger = logging.getLogger("agents.laboratory")

# Standard clinical thresholds
HYPERTENSIVE_CRISIS_SBP = 180.0
HYPERTENSIVE_CRISIS_DBP = 120.0
SEVERE_HYPERGLYCEMIA_FBG = 250.0
SEVERE_HBA1C_PERCENT = 10.0
SEVERE_HYPERTRIGLYCERIDEMIA = 500.0
CRITICAL_EGFR_CUTOFF = 30.0


class LaboratoryAgent(BaseClinicalAgent):
    """Domain reasoning agent dedicated to laboratory biomarkers, biochemical indices, and vital signs."""

    def __init__(self, llm_service: Optional[LLMService] = None):
        super().__init__(llm_service=llm_service)

    @property
    def agent_role(self) -> str:
        return "Laboratory Biomarker Specialist"

    @property
    def system_prompt(self) -> str:
        return (
            "You are an expert Clinical Laboratory Medicine Specialist and Pathologist within "
            "the MedOracle multi-agent clinical reasoning platform.\n\n"
            "YOUR RESPONSIBILITIES:\n"
            "1. Objectively evaluate laboratory biomarkers across Glycemic, Lipid, Renal, and Cardiovascular panels.\n"
            "2. Apply gold-standard clinical threshold guidelines (ADA for diabetes, ATP III for lipids, KDIGO for eGFR, AHA/ACC for BP).\n"
            "3. Identify biochemical DISCORDANCE and PHENOTYPES (e.g. normal fasting glucose with elevated HbA1c indicating postprandial surges; "
            "high triglycerides with low HDL indicative of atherogenic insulin resistance; isolated systolic hypertension).\n"
            "4. Screen vigilantly for CRITICAL METABOLIC / HEMODYNAMIC CRISES (hypertensive urgency/crisis, severe hyperglycemia, stage 4-5 CKD).\n"
            "5. If laboratory panels are missing or unrecorded, acknowledge the objective data gap, operate under epistemic uncertainty "
            "with discounted confidence, and demand essential laboratory requisitions.\n"
            "6. Formulate precise, adversarial CHALLENGES targeting the Symptom Agent (questioning whether complaints are biochemically substantiated) "
            "and the Medical History Agent (questioning therapeutic adequacy of prescribed drug dosages).\n\n"
            "OUTPUT REQUIREMENTS:\n"
            "- agent_role: Exactly 'Laboratory Biomarker Specialist'.\n"
            "- findings: 2-3 sentence objective synthesis of biomarker abnormalities, metabolic staging, and organ-system strain.\n"
            "- confidence: Numerical score (0.0 to 100.0) reflecting certainty derived purely from objective laboratory data.\n"
            "- reasoning_chain: 3-5 concise, clinical logic steps connecting quantitative lab values to pathophysiological states.\n"
            "- evidence: Explicitly list verified numerical values with clinical units and reference ranges.\n"
            "- challenges: 2-4 critical doubts, confounding sample factors (e.g. fasting duration, hemoconcentration), or required lab tests."
        )

    def extract_biomarkers(self, context: Dict[str, Any]) -> Dict[str, Optional[float]]:
        """Normalize biomarkers from nested dicts, raw context keys, or lab objects."""
        # Check potential sources
        raw_bio = context.get("biomarkers") or {}
        lab_obj = context.get("laboratory") or context.get("latest_labs") or {}
        if isinstance(lab_obj, dict) and "biomarkers" in lab_obj:
            nested_bio = lab_obj.get("biomarkers") or {}
        else:
            nested_bio = lab_obj

        def _get_val(*keys: str) -> Optional[float]:
            for k in keys:
                v = context.get(k)
                if v is not None:
                    try:
                        return float(v)
                    except (ValueError, TypeError):
                        pass
                if isinstance(raw_bio, dict):
                    v = raw_bio.get(k)
                    if v is not None:
                        try:
                            return float(v)
                        except (ValueError, TypeError):
                            pass
                if isinstance(nested_bio, dict):
                    v = nested_bio.get(k)
                    if v is not None:
                        try:
                            return float(v)
                        except (ValueError, TypeError):
                            pass
            return None

        return {
            "systolic_bp": _get_val("systolic_bp", "sbp", "systolic"),
            "diastolic_bp": _get_val("diastolic_bp", "dbp", "diastolic"),
            "total_cholesterol_mg_dl": _get_val("total_cholesterol_mg_dl", "total_cholesterol", "tc"),
            "hdl_cholesterol_mg_dl": _get_val("hdl_cholesterol_mg_dl", "hdl_cholesterol", "hdl"),
            "ldl_cholesterol_mg_dl": _get_val("ldl_cholesterol_mg_dl", "ldl_cholesterol", "ldl"),
            "triglycerides_mg_dl": _get_val("triglycerides_mg_dl", "triglycerides", "tg"),
            "fasting_blood_glucose_mg_dl": _get_val("fasting_blood_glucose_mg_dl", "fasting_glucose", "fbg", "glucose"),
            "hba1c_percent": _get_val("hba1c_percent", "hba1c"),
            "serum_creatinine_mg_dl": _get_val("serum_creatinine_mg_dl", "creatinine", "serum_creatinine"),
            "estimated_gfr": _get_val("estimated_gfr", "egfr"),
        }

    def has_recorded_labs(self, context: Dict[str, Any]) -> bool:
        """Determine whether any quantitative lab markers or vital signs are available."""
        biomarkers = self.extract_biomarkers(context)
        return any(v is not None for v in biomarkers.values())

    def validate_context(self, context: Dict[str, Any]) -> None:
        """Verify context format.
        
        Permits empty or missing lab contexts to support de novo presentation or uncollected
        laboratory workups without failing the multi-agent consensus workflow.
        """
        super().validate_context(context)

    def analyze(
        self,
        context: Dict[str, Any],
        provider: Optional[str] = None,
        use_cache: bool = True,
    ) -> AgentOutputResponse:
        """Execute clinical laboratory reasoning with graceful missing-data discounting."""
        output = super().analyze(context=context, provider=provider, use_cache=use_cache)

        # If no quantitative lab tests are on file, enforce epistemic uncertainty adjustments
        if not self.has_recorded_labs(context):
            if output.confidence > 40.0:
                output.confidence = 30.0

            missing_marker = "No objective laboratory panels (lipids, glycemic, renal, or blood pressure) on record (objective data gap)."
            if missing_marker not in output.evidence:
                output.evidence.insert(0, missing_marker)

            lab_req_challenge = "Urgent laboratory requisition required: Fasting Lipid Panel, HbA1c, Fasting Blood Glucose, and Comprehensive Metabolic Panel (eGFR/Creatinine)."
            if lab_req_challenge not in output.challenges:
                output.challenges.insert(0, lab_req_challenge)

        return output

    def build_prompt(self, context: Dict[str, Any]) -> str:
        """Construct structured clinical laboratory briefing detailing quantitative panels."""
        lines: List[str] = ["# PATIENT CLINICAL LABORATORY & BIOMARKER BRIEFING\n"]

        # 1. Demographics
        demo = context.get("patient_demographics") or {}
        age = demo.get("age", context.get("age", "Unknown"))
        sex = demo.get("sex", context.get("sex", "Unknown"))
        lines.append(f"**Patient Demographics:** Age: {age} | Biological Sex: {sex}\n")

        # 2. Check if labs are completely unavailable
        if not self.has_recorded_labs(context):
            lines.append("## ⚠️ CLINICAL STATUS: LABORATORY PANELS UNAVAILABLE / UNRECORDED")
            lines.append(
                "- **Status:** No quantitative laboratory biomarker tests or vital sign panels are on file for this patient.\n"
                "- **Clinical Reality:** Patient has not undergone diagnostic venipuncture, or recent external laboratory results are pending.\n"
                "- **Epistemic Uncertainty Guidance:**\n"
                "  1. Cannot verify subclinical atherogenesis, glycemic dysregulation, or early renal impairment without objective values.\n"
                "  2. Apply a strict confidence penalty (confidence between 20.0 and 35.0) reflecting the complete absence of objective measurements.\n"
                "  3. In `findings`, synthesize that diagnostic conclusions are limited by the absence of baseline laboratory values.\n"
                "  4. In `reasoning_chain`, highlight that subjective symptoms and clinical risk calculators cannot be calibrated without objective biomarkers.\n"
                "  5. In `evidence`, state that no objective blood pressure or laboratory parameters are documented.\n"
                "  6. In `challenges`, demand an urgent complete diagnostic panel requisition (Lipids, HbA1c, FBG, eGFR/Creatinine)."
            )
            lines.append("")
            return "\n".join(lines)

        bio = self.extract_biomarkers(context)
        alerts: List[str] = []

        # 3. Cardiovascular & Hemodynamic Panel
        lines.append("## 1. Cardiovascular & Hemodynamic Vitals")
        sbp = bio.get("systolic_bp")
        dbp = bio.get("diastolic_bp")
        if sbp is not None or dbp is not None:
            sbp_str = f"{round(sbp)} mmHg" if sbp is not None else "Unrecorded"
            dbp_str = f"{round(dbp)} mmHg" if dbp is not None else "Unrecorded"
            lines.append(f"- **Resting Blood Pressure:** {sbp_str} / {dbp_str}")

            # Stratify BP stage
            if sbp is not None and dbp is not None:
                if sbp >= HYPERTENSIVE_CRISIS_SBP or dbp >= HYPERTENSIVE_CRISIS_DBP:
                    alerts.append(f"🚨 **Hypertensive Crisis Alert:** BP {round(sbp)}/{round(dbp)} mmHg exceeds critical urgency cutoffs.")
                    lines.append("  - *Clinical Stage:* Hypertensive Crisis / Severe Urgency (AHA/ACC 2017)")
                elif sbp >= 140 or dbp >= 90:
                    lines.append("  - *Clinical Stage:* Stage 2 Hypertension")
                elif sbp >= 130 or dbp >= 80:
                    lines.append("  - *Clinical Stage:* Stage 1 Hypertension")
                elif sbp >= 120 and dbp < 80:
                    lines.append("  - *Clinical Stage:* Elevated Blood Pressure")
                else:
                    lines.append("  - *Clinical Stage:* Normal Blood Pressure (<120/<80 mmHg)")

                # Isolated Systolic Hypertension
                if sbp >= 140 and dbp < 90:
                    lines.append("  - *Phenotype:* Isolated Systolic Hypertension (indicates advanced aortic stiffness).")
        else:
            lines.append("- Blood pressure measurements unrecorded.")
        lines.append("")

        # 4. Glycemic Panel
        lines.append("## 2. Glycemic & Metabolic Panel")
        fbg = bio.get("fasting_blood_glucose_mg_dl")
        hba1c = bio.get("hba1c_percent")

        if fbg is not None:
            lines.append(f"- **Fasting Blood Glucose (FBG):** {round(fbg, 1)} mg/dL")
            if fbg >= SEVERE_HYPERGLYCEMIA_FBG:
                alerts.append(f"🚨 **Severe Hyperglycemia Alert:** FBG {round(fbg, 1)} mg/dL carries acute osmotic and ketoacidosis risk.")
            elif fbg >= 126.0:
                lines.append("  - *ADA Classification:* Overt Diabetes Threshold (>= 126 mg/dL)")
            elif fbg >= 100.0:
                lines.append("  - *ADA Classification:* Impaired Fasting Glucose / Prediabetes (100-125 mg/dL)")
            else:
                lines.append("  - *ADA Classification:* Normal Fasting Glucose (< 100 mg/dL)")

        if hba1c is not None:
            lines.append(f"- **Glycated Hemoglobin (HbA1c):** {round(hba1c, 1)}%")
            if hba1c >= SEVERE_HBA1C_PERCENT:
                alerts.append(f"⚠️ **Poor Glycemic Control:** HbA1c {round(hba1c, 1)}% indicates severe long-term glucotoxicity.")
            elif hba1c >= 6.5:
                lines.append("  - *Diagnostic Tier:* Type 2 Diabetes Diagnostic Threshold (>= 6.5%)")
            elif hba1c >= 5.7:
                lines.append("  - *Diagnostic Tier:* High Risk for Diabetes / Prediabetes (5.7 - 6.4%)")
            else:
                lines.append("  - *Diagnostic Tier:* Normal Glycemia (< 5.7%)")

        # Glycemic Discordance Check
        if fbg is not None and hba1c is not None:
            if fbg < 100.0 and hba1c >= 6.5:
                lines.append(
                    "  - ⚡ *Biomarker Discordance Detected:* Normal fasting glucose with diabetic HbA1c. "
                    "Reflects severe postprandial glucose excursions or hemoglobinopathy."
                )

        if fbg is None and hba1c is None:
            lines.append("- No glycemic biomarkers recorded.")
        lines.append("")

        # 5. Lipid & Atherogenic Panel
        lines.append("## 3. Lipid Profile & Atherogenic Indices")
        tc = bio.get("total_cholesterol_mg_dl")
        hdl = bio.get("hdl_cholesterol_mg_dl")
        ldl = bio.get("ldl_cholesterol_mg_dl")
        tg = bio.get("triglycerides_mg_dl")

        if tc is not None:
            lines.append(f"- **Total Cholesterol:** {round(tc, 1)} mg/dL")
        if ldl is not None:
            lines.append(f"- **LDL-C (Atherogenic Particle Burden):** {round(ldl, 1)} mg/dL")
            if ldl >= 190.0:
                alerts.append(f"🚨 **Severe Hypercholesterolemia:** LDL-C {round(ldl, 1)} mg/dL raises high suspicion for Familial Hypercholesterolemia.")
            elif ldl >= 160.0:
                lines.append("  - *ATP III Tier:* High LDL-C (160-189 mg/dL)")
            elif ldl >= 130.0:
                lines.append("  - *ATP III Tier:* Borderline High LDL-C (130-159 mg/dL)")
            else:
                lines.append("  - *ATP III Tier:* Optimal / Near Optimal (< 130 mg/dL)")

        if hdl is not None:
            lines.append(f"- **HDL-C (Protective Fraction):** {round(hdl, 1)} mg/dL")
            is_female = str(sex).lower() == "female"
            hdl_cutoff = 50.0 if is_female else 40.0
            if hdl < hdl_cutoff:
                lines.append(f"  - *Atherogenic Risk:* Suppressed HDL-C (< {round(hdl_cutoff)} mg/dL for {sex})")
            elif hdl >= 60.0:
                lines.append("  - *Cardioprotective:* High HDL-C (>= 60 mg/dL)")

        if tg is not None:
            lines.append(f"- **Triglycerides:** {round(tg, 1)} mg/dL")
            if tg >= SEVERE_HYPERTRIGLYCERIDEMIA:
                alerts.append(f"🚨 **Extreme Hypertriglyceridemia Alert:** TG {round(tg, 1)} mg/dL carries acute pancreatitis risk.")
            elif tg >= 200.0:
                lines.append("  - *Risk Tier:* High Triglycerides (200-499 mg/dL)")

        # Atherogenic Dyslipidemia Triad Check
        if tg is not None and hdl is not None:
            is_female = str(sex).lower() == "female"
            hdl_risk = hdl < (50.0 if is_female else 40.0)
            if tg >= 200.0 and hdl_risk:
                lines.append(
                    "  - ⚡ *Atherogenic Dyslipidemia Phenotype:* Concurrent elevated Triglycerides and low HDL-C. "
                    "Hallmark indicator of small dense LDL particles, insulin resistance, and accelerated atherogenesis."
                )

        if tc is None and ldl is None and hdl is None and tg is None:
            lines.append("- No lipid profile recorded.")
        lines.append("")

        # 6. Renal Filtration & Excretory Panel
        lines.append("## 4. Renal Function & Filtration Panel")
        creat = bio.get("serum_creatinine_mg_dl")
        egfr = bio.get("estimated_gfr")

        if creat is not None:
            lines.append(f"- **Serum Creatinine:** {round(creat, 2)} mg/dL")
        if egfr is not None:
            lines.append(f"- **Estimated GFR (eGFR):** {round(egfr, 1)} mL/min/1.73m²")
            if egfr < CRITICAL_EGFR_CUTOFF:
                alerts.append(f"🚨 **Critical Renal Impairment:** eGFR {round(egfr, 1)} mL/min/1.73m² indicates Stage 4-5 Chronic Kidney Disease.")
            elif egfr < 60.0:
                lines.append("  - *KDIGO Staging:* Stage 3 Chronic Kidney Disease (30-59 mL/min/1.73m²)")
            elif egfr < 90.0:
                lines.append("  - *KDIGO Staging:* Stage 2 Mild GFR Reduction (60-89 mL/min/1.73m²)")
            else:
                lines.append("  - *KDIGO Staging:* Stage 1 Normal / Preserved Renal Filtration (>= 90 mL/min/1.73m²)")
        if creat is None and egfr is None:
            lines.append("- No renal biomarker panel recorded.")
        lines.append("")

        # 7. Automated Safety Alerts
        if alerts:
            lines.append("## AUTOMATED LABORATORY SAFETY ALERTS")
            for alert in alerts:
                lines.append(alert)
            lines.append("")

        lines.append(
            "Synthesize these objective quantitative findings into the standard structured format. "
            "Correlate hemodynamic, metabolic, and renal biomarkers, articulate a step-by-step reasoning chain, "
            "and formulate rigorous cross-examination challenges for the Symptom and History agents."
        )

        return "\n".join(lines)
