"""Symptom Specialist Clinical Agent for MedOracle (Step 10.2).

Specializes in:
1. Patient-reported symptom interpretation, duration, and severity grading.
2. Clinical NLP entity integration (distinguishing affirmed from NegEx-negated symptoms).
3. Red flag detection for acute cardiovascular and metabolic emergencies.
4. Symptom clustering into clinical syndromes and correlation with ML differential candidates.
5. Formulating cross-examination challenges for Lab and History agents in debate.
"""

from datetime import datetime, timezone
import logging
from typing import Any, Dict, List, Optional

from app.agents.base import AgentExecutionError, BaseClinicalAgent
from app.schemas.analysis import AgentOutputResponse
from app.services.llm_service import LLMService

logger = logging.getLogger("agents.symptom")

# Acute cardiovascular and metabolic emergency signs requiring immediate clinical escalation
ACUTE_RED_FLAGS: List[str] = [
    "chest pain",
    "substernal pressure",
    "radiating pain to left arm",
    "jaw pain",
    "sudden onset dyspnea",
    "orthopnea",
    "syncope",
    "loss of consciousness",
    "altered mental status",
    "severe diaphoresis",
    "acute hemoptysis",
    "unilateral motor weakness",
]


class SymptomAgent(BaseClinicalAgent):
    """Domain reasoning agent dedicated to patient-reported symptoms and NLP extractions."""

    def __init__(self, llm_service: Optional[LLMService] = None):
        super().__init__(llm_service=llm_service)

    @property
    def agent_role(self) -> str:
        return "Symptom Analysis Specialist"

    @property
    def system_prompt(self) -> str:
        return (
            "You are an expert Clinical Symptom Specialist and Internist within the MedOracle "
            "multi-agent clinical reasoning platform.\n\n"
            "YOUR RESPONSIBILITIES:\n"
            "1. Evaluate reported symptoms, severity ratings (1-10 scale), onset patterns, and duration.\n"
            "2. Cross-reference affirmed symptoms against Clinical NLP extractions and differential ML predictions.\n"
            "3. Explicitly respect negated symptoms (NegEx confirmed negative) — do NOT treat denied symptoms as active.\n"
            "4. Screen vigilantly for acute life-threatening RED FLAGS (e.g. unstable angina, acute coronary syndrome, "
            "severe dyspnea, ketoacidosis equivalents).\n"
            "5. Group symptoms into coherent clinical syndromes (e.g. 'Ischemic Precordial Syndrome', 'Metabolic Syndrome').\n"
            "6. Formulate precise, adversarial CHALLENGES targeting missing objective lab markers (e.g. Troponin, FBG, Lipid panel) "
            "and historical risk factors for the Medical History and Laboratory agents.\n\n"
            "OUTPUT REQUIREMENTS:\n"
            "- agent_role: Exactly 'Symptom Analysis Specialist'.\n"
            "- findings: 2-3 sentence clinical synthesis of presenting syndrome, severity, and urgency.\n"
            "- confidence: Numerical score (0.0 to 100.0) reflecting diagnostic certainty from subjective data alone.\n"
            "- reasoning_chain: 3-5 concise, clinical logic steps explaining your deduction.\n"
            "- evidence: Explicitly list verified patient-reported symptoms, severity scores, and temporal markers.\n"
            "- challenges: 2-4 critical doubts, rule-outs, or specific laboratory/historical data points required to confirm."
        )

    def validate_context(self, context: Dict[str, Any]) -> None:
        """Verify context contains either direct symptoms list, report dict, or NLP extractions."""
        super().validate_context(context)

        symptoms = context.get("symptoms")
        symptom_report = context.get("symptom_report")
        nlp_entities = context.get("nlp_entities")
        notes = context.get("notes") or context.get("chief_complaint")

        has_symptoms = bool(symptoms)
        has_report = isinstance(symptom_report, dict) and bool(
            symptom_report.get("symptoms") or symptom_report.get("notes")
        )
        has_nlp = bool(nlp_entities)
        has_notes = bool(notes)

        if not (has_symptoms or has_report or has_nlp or has_notes):
            raise AgentExecutionError(
                self.agent_role,
                "Context must provide at least one symptom source: 'symptoms', 'symptom_report', 'nlp_entities', or 'notes'.",
            )

    def build_prompt(self, context: Dict[str, Any]) -> str:
        """Construct structured clinical briefing for LLM inference."""
        lines: List[str] = ["# PATIENT CLINICAL SYMPTOM BRIEFING\n"]

        # 1. Demographics
        demo = context.get("patient_demographics") or {}
        age = demo.get("age", context.get("age", "Unknown"))
        sex = demo.get("sex", context.get("sex", "Unknown"))
        lines.append(f"**Patient Demographics:** Age: {age} | Biological Sex: {sex}\n")

        # 2. Symptom Report Data
        report = context.get("symptom_report") or {}
        raw_symptoms = context.get("symptoms") or report.get("symptoms") or []
        severity = context.get("severity") or report.get("severity", "Unspecified")
        duration = context.get("duration_days") or report.get("duration_days", "Unspecified")
        onset = context.get("onset_date") or report.get("onset_date", "Unspecified")
        notes = context.get("notes") or report.get("notes") or context.get("chief_complaint", "")

        lines.append("## Reported Symptom Constellation")
        if raw_symptoms:
            lines.append(f"- **Active Symptoms:** {', '.join(str(s).replace('_', ' ') for s in raw_symptoms)}")
        lines.append(f"- **Patient-Reported Severity:** {severity}/10")
        lines.append(f"- **Onset / Duration:** Onset: {onset} | Duration: {duration} days")
        if notes:
            lines.append(f"- **Patient Narrative / Notes:** \"{notes}\"")
        lines.append("")

        # 3. Clinical NLP Extracted Entities (Affirmed vs Negated)
        nlp_entities = context.get("nlp_entities") or []
        if nlp_entities:
            lines.append("## Clinical NLP & NegEx Extractions")
            affirmed = [e for e in nlp_entities if not e.get("negated", False)]
            negated = [e for e in nlp_entities if e.get("negated", False)]

            if affirmed:
                aff_str = ", ".join(
                    f"{e.get('canonical_symptom', e.get('text', '')).replace('_', ' ')} (conf: {round(e.get('confidence', 1.0) * 100)}%)"
                    for e in affirmed
                )
                lines.append(f"- **Affirmed Present:** {aff_str}")
            if negated:
                neg_str = ", ".join(
                    f"{e.get('canonical_symptom', e.get('text', '')).replace('_', ' ')}"
                    for e in negated
                )
                lines.append(f"- **Explicitly Denied (NegEx Negated):** {neg_str}")
            lines.append("")

        # 4. Machine Learning Differential Predictions
        diff_candidates = context.get("differential_candidates") or []
        if diff_candidates:
            lines.append("## Statistical ML Differential Diagnosis Candidates (Step 8 Classifier)")
            for i, cand in enumerate(diff_candidates[:3], start=1):
                disease = cand.get("disease", "Unknown").replace("_", " ").title()
                prob = cand.get("probability", 0.0)
                lines.append(f"{i}. **{disease}**: {round(prob * 100, 1)}% probability")
            lines.append("")

        # 5. Red Flag Detection Hint
        detected_flags: List[str] = []
        all_symptom_text = (
            " ".join(str(s) for s in raw_symptoms).lower()
            + " "
            + str(notes).lower()
        )
        for flag in ACUTE_RED_FLAGS:
            if flag in all_symptom_text:
                detected_flags.append(flag)

        if detected_flags:
            lines.append("## AUTOMATED SAFETY ESCALATION")
            lines.append(
                f"⚠️ **High-Risk Signs Flagged:** {', '.join(detected_flags).title()}. "
                "Evaluate with heightened clinical urgency and emphasize acute exclusion in challenges."
            )
            lines.append("")

        lines.append(
            "Synthesize these observations into the standard structured format. "
            "Provide balanced clinical findings, articulate a step-by-step reasoning chain, "
            "and formulate rigorous challenges for the other agents."
        )

        return "\n".join(lines)
