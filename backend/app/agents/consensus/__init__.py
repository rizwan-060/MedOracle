"""Consensus & Multi-Agent Debate package (Step 12).

Exports:
- ContradictionDetector (Sub-Step 12.1)
- DebateProtocolEngine (Sub-Step 12.2)
- SemanticNLIEngine (Sub-Step 12.2)
"""

from app.agents.consensus.contradiction_detector import ContradictionDetector
from app.agents.consensus.debate_protocol import DebateProtocolEngine, SemanticNLIEngine

__all__ = [
    "ContradictionDetector",
    "DebateProtocolEngine",
    "SemanticNLIEngine",
]
