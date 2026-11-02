"""Medical History Specialist Clinical Agent for MedOracle (Step 10.3).

Specializes in:
1. Synthesizing longitudinal chronic conditions (hypertension, T2D, prior MI, CKD, stroke).
2. Family pedigree analysis and premature cardiovascular disease risk (<55M / <65F).
3. Medication profile review (adherence, drug-symptom interactions, contraindications).
4. Lifestyle risk stratification (tobacco exposure, physical activity, obesity indicators).
5. Cross-referencing chronic baseline against acute presenting symptoms.
6. Formulating adversarial challenges for Laboratory, Symptom, and Risk agents.
"""

from datetime import datetime, timezone
import logging
from typing import Any, Dict, List, Optional

from app.agents.base import AgentExecutionError, BaseClinicalAgent
from app.schemas.analysis import AgentOutputResponse
from app.services.llm_service import LLMService

logger = logging.getLogger("agents.medical_history")

# First-degree relatives for pedigree cardiovascular screening
FIRST_DEGREE_RELATIVES = {"father", "mother", "brother", "sister", "sibling", "parent", "son", "daughter"}

# High-risk chronic multimorbidity markers
HIGH_RISK_CONDITIONS = {
    "hypertension",
    "type_2_diabetes",
    "type_1_diabetes",
    "coronary_artery_disease",
    "myocardial_infarction",
    "heart_failure",
    "stroke",
    "transient_ischemic_attack",
    "chronic_kidney_disease",
    "hyperlipidemia",
    "peripheral_artery_disease",
    "atrial_fibrillation",
}


class MedicalHistoryAgent(BaseClinicalAgent):
    """Domain reasoning agent dedicated to longitudinal medical history, genetics, and pharmacotherapy."""

    def __init__(self, llm_service: Optional[LLMService] = None):
        super().__init__(llm_service=llm_service)

    @property
    def agent_role(self) -> str:
        return "Medical History Specialist"

    @property
    def system_prompt(self) -> str:
        return (
            "You are an expert Clinical Medical History Specialist and Preventive Cardiologist within "
            "the MedOracle multi-agent clinical reasoning platform.\n\n"
            "YOUR RESPONSIBILITIES:\n"
            "1. Synthesize the patient's longitudinal chronic disease burden (e.g. hypertension, T2D, prior MI, "
            "stroke, CKD, dyslipidemia).\n"
            "2. Evaluate family pedigree and hereditary risk, specifically screening for PREMATURE CORONARY ARTERY DISEASE "
            "(first-degree male relative < 55 yrs, female < 65 yrs) and familial metabolic syndromes.\n"
            "3. Audit current medications, dosages, and compliance. Identify potential drug-symptom adverse effects "
            "(e.g. ACE inhibitor cough, beta-blocker fatigue, statin myopathy) and critical drug contraindications.\n"
            "4. Assess lifestyle modifiers (smoking history/pack-years, sedentary behavior, alcohol intake).\n"
            "5. Cross-reference chronic conditions with presenting symptoms to identify disease decompensation or acute crises.\n"
            "6. Formulate precise, adversarial CHALLENGES targeting the Laboratory Agent (demanding specific biomarker checks) "
            "and the Risk Prediction Agent (questioning baseline assumptions or medication-masked vitals).\n\n"
            "OUTPUT REQUIREMENTS:\n"
            "- agent_role: Exactly 'Medical History Specialist'.\n"
            "- findings: 2-3 sentence clinical synthesis of historical risk architecture, genetic predispositions, and pharmacological context.\n"
            "- confidence: Numerical score (0.0 to 100.0) reflecting certainty derived from longitudinal and historical records.\n"
            "- reasoning_chain: 3-5 concise, clinical logic steps connecting historical risk factors to current vulnerability.\n"
            "- evidence: Explicitly list verified chronic conditions, medications with dosages, family history events, and lifestyle habits.\n"
            "- challenges: 2-4 critical clinical doubts, rule-outs, or required lab/imaging tests needed to resolve historical ambiguity."
        )

    def has_recorded_history(self, context: Dict[str, Any]) -> bool:
        """Check whether any longitudinal medical, medication, family, or lifestyle data is present."""
        chronic = context.get("chronic_conditions")
        meds = context.get("current_medications")
        family = context.get("family_history")
        surgeries = context.get("past_surgeries")
        allergies = context.get("allergies")
        lifestyle = context.get("lifestyle")
        notes = context.get("notes") or context.get("history_notes")
        history_obj = context.get("medical_history")

        return bool(
            chronic
            or meds
            or family
            or surgeries
            or allergies
            or lifestyle
            or context.get("smoking_status")
            or context.get("activity_level")
            or notes
            or (isinstance(history_obj, dict) and any(history_obj.values()))
        )

    def validate_context(self, context: Dict[str, Any]) -> None:
        """Verify context format.

        Permits empty or missing history contexts to support de novo patient presentations,
        emergency intake, or unrecorded historical profiles without crashing the pipeline.
        """
        super().validate_context(context)

    def analyze(
        self,
        context: Dict[str, Any],
        provider: Optional[str] = None,
        use_cache: bool = True,
    ) -> AgentOutputResponse:
        """Analyze medical history or handle unrecorded longitudinal data gracefully."""
        output = super().analyze(context=context, provider=provider, use_cache=use_cache)

        # If medical history is entirely unavailable or empty, enforce epistemic uncertainty adjustments
        if not self.has_recorded_history(context):
            # Cap confidence score to reflect high epistemic uncertainty from missing records
            if output.confidence > 45.0:
                output.confidence = 35.0

            # Ensure evidence and challenges reflect surveillance gap
            missing_evidence_marker = "No prior longitudinal medical history, medications, or family pedigree on record (surveillance gap)."
            if missing_evidence_marker not in output.evidence:
                output.evidence.insert(0, missing_evidence_marker)

            baseline_challenge = "Conduct comprehensive baseline clinical intake, medication reconciliation, and screening panels to establish historical reference."
            if not any("baseline" in c.lower() or "intake" in c.lower() or "screening" in c.lower() for c in output.challenges):
                output.challenges.insert(0, baseline_challenge)

        return output

    def build_prompt(self, context: Dict[str, Any]) -> str:
        """Construct structured clinical briefing detailing longitudinal history for LLM inference."""
        lines: List[str] = ["# PATIENT LONGITUDINAL MEDICAL HISTORY BRIEFING\n"]

        # 1. Demographics
        demo = context.get("patient_demographics") or {}
        age = demo.get("age", context.get("age", "Unknown"))
        sex = demo.get("sex", context.get("sex", "Unknown"))
        lines.append(f"**Patient Demographics:** Age: {age} | Biological Sex: {sex}\n")

        # 2. Check if longitudinal history is present or completely unrecorded
        if not self.has_recorded_history(context):
            lines.append("## ⚠️ CLINICAL STATUS: MEDICAL HISTORY UNAVAILABLE / UNRECORDED")
            lines.append(
                "- **Status:** No prior longitudinal records, chronic diagnoses, medication lists, or family pedigree data are on file.\n"
                "- **Clinical Presentation:** De novo presentation, healthy baseline, or historical records currently unavailable.\n"
                "- **Epistemic Uncertainty Guidance:**\n"
                "  1. Do NOT assume absence of recorded disease equals confirmed absence of pathology.\n"
                "  2. Apply a strict confidence penalty (confidence between 25.0 and 40.0) reflecting high epistemic uncertainty.\n"
                "  3. In `findings`, synthesize that the patient presents with an unrecorded longitudinal profile.\n"
                "  4. In `reasoning_chain`, explicitly note the surveillance gap and inability to adjust for hereditary or pharmacological baseline.\n"
                "  5. In `evidence`, state that no pre-existing conditions, active medications, or family history are recorded.\n"
                "  6. In `challenges`, demand an in-person medical intake interview, comprehensive medication reconciliation, and baseline screening labs."
            )
            lines.append("")


        # Extract nested medical history object if provided
        mh = context.get("medical_history") or {}

        # 2. Chronic Pre-Existing Conditions
        chronic = context.get("chronic_conditions") or mh.get("chronic_conditions") or []
        lines.append("## Pre-Existing Chronic Conditions")
        if chronic:
            for cond in chronic:
                clean_cond = str(cond).replace("_", " ").title()
                lines.append(f"- **Condition:** {clean_cond}")
        else:
            lines.append("- No diagnosed chronic conditions recorded.")
        lines.append("")

        # 3. Pharmacotherapy & Current Medications
        medications = context.get("current_medications") or mh.get("current_medications") or []
        lines.append("## Current Pharmacotherapy")
        if medications:
            for med in medications:
                if isinstance(med, dict):
                    name = med.get("name", "Unknown medication")
                    dose = med.get("dosage", "Unspecified dose")
                    freq = med.get("frequency", "")
                    freq_str = f" | Frequency: {freq}" if freq else ""
                    lines.append(f"- **{name}**: {dose}{freq_str}")
                else:
                    lines.append(f"- **{med}**")
        else:
            lines.append("- No active prescriptions recorded.")
        lines.append("")

        # 4. Family Medical History & Pedigree Risk
        family = context.get("family_history") or mh.get("family_history") or []
        lines.append("## Family Medical History (Pedigree)")
        premature_cad_alerts: List[str] = []

        if family:
            for item in family:
                if isinstance(item, dict):
                    rel = str(item.get("relative", "relative")).lower()
                    cond = str(item.get("condition", "unspecified condition")).replace("_", " ").title()
                    onset = item.get("age_at_onset")
                    onset_str = f" (age of onset: {onset})" if onset is not None else ""
                    lines.append(f"- **{rel.title()}**: {cond}{onset_str}")

                    # Screen for premature CAD (<55 in males, <65 in females)
                    is_cad = any(term in cond.lower() for term in ["myocardial", "infarction", "coronary", "heart attack", "cad", "angina"])
                    if is_cad and onset is not None and rel in FIRST_DEGREE_RELATIVES:
                        is_male_rel = rel in {"father", "brother", "son"}
                        is_female_rel = rel in {"mother", "sister", "daughter"}
                        if (is_male_rel and onset < 55) or (is_female_rel and onset < 65) or (onset < 55):
                            premature_cad_alerts.append(f"{rel.title()} ({cond} at age {onset})")
                else:
                    lines.append(f"- {item}")
        else:
            lines.append("- No known positive family medical history.")
        lines.append("")

        # 5. Lifestyle, Social History & Allergies
        lifestyle = context.get("lifestyle") or {}
        smoking = lifestyle.get("smoking_status") or context.get("smoking_status") or "unspecified"
        activity = lifestyle.get("activity_level") or context.get("activity_level") or "unspecified"
        surgeries = context.get("past_surgeries") or mh.get("past_surgeries") or []
        allergies = context.get("allergies") or mh.get("allergies") or []
        notes = context.get("notes") or mh.get("notes") or context.get("history_notes", "")

        lines.append("## Lifestyle & Clinical Baseline")
        lines.append(f"- **Smoking Status:** {str(smoking).replace('_', ' ').title()}")
        lines.append(f"- **Physical Activity Level:** {str(activity).replace('_', ' ').title()}")
        if surgeries:
            lines.append(f"- **Past Surgical History:** {', '.join(str(s) for s in surgeries)}")
        if allergies:
            lines.append(f"- **Known Allergies:** {', '.join(str(a) for a in allergies)}")
        if notes:
            lines.append(f"- **Clinical Intake Notes:** \"{notes}\"")
        lines.append("")

        # 6. Presenting Symptoms (Cross-Reference Context if available)
        active_symptoms = context.get("active_symptoms") or context.get("symptoms") or []
        if active_symptoms:
            lines.append("## Presenting Acute Symptoms (Cross-Examination)")
            lines.append(f"- **Active Complaints:** {', '.join(str(s).replace('_', ' ') for s in active_symptoms)}")
            lines.append("")

        # 7. Automated Clinical Alerts & Escalations
        alerts: List[str] = []
        if premature_cad_alerts:
            alerts.append(
                f"🚨 **Premature First-Degree CAD Detected:** {', '.join(premature_cad_alerts)}. "
                "Classifies patient under elevated lifetime cardiovascular risk tier."
            )

        # Multimorbidity detection
        chronic_lower = [str(c).lower().replace(" ", "_") for c in chronic]
        has_htn = any("hypertension" in c or "htn" in c for c in chronic_lower)
        has_dm = any("diabetes" in c or "t2d" in c or "dm" in c for c in chronic_lower)
        has_lipid = any("hyperlipidemia" in c or "dyslipidemia" in c or "cholesterol" in c for c in chronic_lower)
        has_ckd = any("kidney" in c or "ckd" in c or "renal" in c for c in chronic_lower)

        if has_htn and has_dm and has_lipid:
            alerts.append(
                "⚠️ **Cardiometabolic Triad Identified:** Co-existing Hypertension, Diabetes, and Dyslipidemia. "
                "Exponentially compounds vascular endothelitis and accelerates atherogenesis."
            )
        elif has_htn and has_ckd:
            alerts.append(
                "⚠️ **Cardio-Renal Overlap Identified:** Concurrent Hypertension and Renal Impairment. "
                "Demand stringent eGFR and electrolyte surveillance."
            )

        if alerts:
            lines.append("## AUTOMATED HISTORICAL RISK ALERTS")
            for alert in alerts:
                lines.append(alert)
            lines.append("")

        lines.append(
            "Synthesize this longitudinal background into the standard structured format. "
            "Examine how past conditions and medications predispose to or mask current pathology, "
            "and formulate rigorous challenges for the Laboratory and Risk Prediction agents."
        )

        return "\n".join(lines)
