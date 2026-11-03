"""Consensus Agent Framework for MedOracle (Step 12.4).

Wraps the evidence-aware ConsensusResolver engine into an autonomous specialist agent.
Consumes upstream findings, contradiction matrix, adversarial debate transcript,
and recalibrated confidence records to formulate the definitive clinical consensus verdict.
"""

import logging
from typing import Any, Dict, List, Optional

from app.agents.base import BaseClinicalAgent
from app.agents.consensus.consensus_resolver import ConsensusResolver
from app.schemas.analysis import AgentOutputResponse
from app.schemas.consensus import (
    ConfidenceRecalibrationResult,
    ConsensusResolutionResult,
    ContradictionMatrixResult,
    DebateTranscript,
    OverallConsensusOutcome,
)
from app.services.llm_service import LLMService

logger = logging.getLogger("agents.consensus")


class ConsensusAgent(BaseClinicalAgent):
    """Consensus Agent executing evidence-aware resolution and audit transcript generation."""

    def __init__(
        self,
        llm_service: Optional[LLMService] = None,
        resolver: Optional[ConsensusResolver] = None,
    ):
        super().__init__(llm_service=llm_service)
        self.resolver = resolver or ConsensusResolver()

    @property
    def agent_role(self) -> str:
        return "Consensus Resolution Specialist"

    @property
    def system_prompt(self) -> str:
        return (
            "You are the MedOracle Clinical Consensus Resolution Specialist. Your responsibility "
            "is to synthesize multi-agent findings, detected clinical contradictions, adversarial debate "
            "transcripts, and recalibrated epistemic doubt scores into an evidence-grounded final consensus outcome. "
            "Never perform simple majority voting. Base conclusions on objective patient evidence, preserve "
            "unresolved disagreements and minority dissents, and uphold critical clinical safety overrides."
        )

    def build_prompt(self, context: Dict[str, Any]) -> str:
        claims = context.get("claims", [])
        contradictions = context.get("contradictions", [])
        doubt = context.get("global_epistemic_doubt", 0.0)
        return (
            f"Synthesize the following {len(claims)} specialist claims and {len(contradictions)} contradiction issues "
            f"with global epistemic doubt {doubt:.3f}. Provide a structured consensus verdict."
        )

    def resolve(
        self,
        recalibration_result: Optional[ConfidenceRecalibrationResult] = None,
        contradiction_matrix: Optional[ContradictionMatrixResult] = None,
        debate_transcript: Optional[DebateTranscript] = None,
        agent_outputs: Optional[List[Any]] = None,
        symptoms_data: Optional[Dict[str, Any]] = None,
        medical_history_data: Optional[Dict[str, Any]] = None,
        laboratory_data: Optional[Dict[str, Any]] = None,
        clinical_scores: Optional[Dict[str, Any]] = None,
        ml_predictions: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
        analysis_id: Optional[str] = None,
        patient_id: Optional[str] = None,
    ) -> ConsensusResolutionResult:
        """Execute consensus resolution via the deterministic ConsensusResolver engine."""
        return self.resolver.resolve_consensus(
            recalibration_result=recalibration_result,
            contradiction_matrix=contradiction_matrix,
            debate_transcript=debate_transcript,
            agent_outputs=agent_outputs,
            symptoms_data=symptoms_data,
            medical_history_data=medical_history_data,
            laboratory_data=laboratory_data,
            clinical_scores=clinical_scores,
            ml_predictions=ml_predictions,
            session_id=session_id,
            analysis_id=analysis_id,
            patient_id=patient_id,
        )
