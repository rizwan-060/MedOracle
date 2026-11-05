"""LangGraph clinical multi-agent workflow compilation and execution engine (Step 11 & Step 12).

Defines the directed execution topology:
1. START fan-out in parallel:
   - symptom_node
   - medical_history_node
   - laboratory_node
2. Fan-in aggregation into:
   - risk_prediction_node (synthesizes domain agent findings + clinical formulas + ML models)
3. Step 12 Consensus Deliberation Sequence:
   - contradiction_node (Step 12.1 deterministic physiological conflict detection)
   - debate_node (Step 12.2 adversarial multi-agent debate protocol)
   - recalibration_node (Step 12.3 mathematical confidence recalibration & epistemic doubt scoring)
   - consensus_node (Step 12.4 evidence-aware consensus resolution & tamper-evident audit transcript)
4. Directs to END.
"""

import logging
from typing import Optional

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.graph.nodes import (
    consensus_node,
    contradiction_node,
    debate_node,
    laboratory_node,
    medical_history_node,
    recalibration_node,
    risk_prediction_node,
    symptom_node,
)
from app.graph.state import ClinicalAgentState

logger = logging.getLogger("graph.workflow")

_COMPILED_GRAPH: Optional[CompiledStateGraph] = None
_COMPILED_SPECIALIST_GRAPH: Optional[CompiledStateGraph] = None


def build_clinical_orchestration_graph(include_consensus: bool = True) -> StateGraph:
    """Construct the uncompiled StateGraph topology for clinical agent orchestration."""
    builder = StateGraph(ClinicalAgentState)

    # 1. Register domain agent nodes
    builder.add_node("symptom_node", symptom_node)
    builder.add_node("medical_history_node", medical_history_node)
    builder.add_node("laboratory_node", laboratory_node)
    builder.add_node("risk_prediction_node", risk_prediction_node)

    # 2. Parallel fan-out from START to data agents
    builder.add_edge(START, "symptom_node")
    builder.add_edge(START, "medical_history_node")
    builder.add_edge(START, "laboratory_node")

    # 3. Fan-in from data agents to Risk Prediction ensemble
    builder.add_edge("symptom_node", "risk_prediction_node")
    builder.add_edge("medical_history_node", "risk_prediction_node")
    builder.add_edge("laboratory_node", "risk_prediction_node")

    if include_consensus:
        # 4. Register consensus deliberation nodes (Step 12)
        builder.add_node("contradiction_node", contradiction_node)
        builder.add_node("debate_node", debate_node)
        builder.add_node("recalibration_node", recalibration_node)
        builder.add_node("consensus_node", consensus_node)

        # 5. Wire full Step 12 consensus pipeline
        builder.add_edge("risk_prediction_node", "contradiction_node")
        builder.add_edge("contradiction_node", "debate_node")
        builder.add_edge("debate_node", "recalibration_node")
        builder.add_edge("recalibration_node", "consensus_node")
        builder.add_edge("consensus_node", END)
    else:
        builder.add_edge("risk_prediction_node", END)

    return builder


def get_compiled_clinical_graph(include_consensus: bool = True) -> CompiledStateGraph:
    """Retrieve or construct the compiled LangGraph instance."""
    global _COMPILED_GRAPH, _COMPILED_SPECIALIST_GRAPH
    if include_consensus:
        if _COMPILED_GRAPH is None:
            logger.info("Compiling MedOracle Full Multi-Agent Clinical Graph with Consensus (Step 11 + 12)...")
            builder = build_clinical_orchestration_graph(include_consensus=True)
            _COMPILED_GRAPH = builder.compile()
            logger.info("MedOracle Full Clinical Graph compiled successfully.")
        return _COMPILED_GRAPH
    else:
        if _COMPILED_SPECIALIST_GRAPH is None:
            logger.info("Compiling MedOracle Specialist Multi-Agent Clinical Graph (Step 11)...")
            builder = build_clinical_orchestration_graph(include_consensus=False)
            _COMPILED_SPECIALIST_GRAPH = builder.compile()
            logger.info("MedOracle Specialist Graph compiled successfully.")
        return _COMPILED_SPECIALIST_GRAPH


def run_clinical_graph(state: ClinicalAgentState, include_consensus: bool = True) -> ClinicalAgentState:
    """Execute the clinical orchestration graph synchronously."""
    graph = get_compiled_clinical_graph(include_consensus=include_consensus)
    result = graph.invoke(state)
    return result


async def arun_clinical_graph(state: ClinicalAgentState, include_consensus: bool = True) -> ClinicalAgentState:
    """Execute the clinical orchestration graph asynchronously."""
    graph = get_compiled_clinical_graph(include_consensus=include_consensus)
    result = await graph.ainvoke(state)
    return result
