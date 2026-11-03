"""Consensus & Multi-Agent Debate package (Step 12).

Exports:
- ContradictionDetector (Sub-Step 12.1)
- DebateProtocolEngine (Sub-Step 12.2)
- SemanticNLIEngine (Sub-Step 12.2)
- ConfidenceRecalibrator (Sub-Step 12.3)
- ConfidenceRecalibrationEngine (Sub-Step 12.3)
"""

from app.agents.consensus.contradiction_detector import ContradictionDetector
from app.agents.consensus.debate_protocol import DebateProtocolEngine, SemanticNLIEngine
from app.agents.consensus.recalibration import ConfidenceRecalibrator, ConfidenceRecalibrationEngine

__all__ = [
    "ContradictionDetector",
    "DebateProtocolEngine",
    "SemanticNLIEngine",
    "ConfidenceRecalibrator",
    "ConfidenceRecalibrationEngine",
]

