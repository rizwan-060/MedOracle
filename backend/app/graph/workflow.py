"""LangGraph clinical multi-agent workflow compilation and execution engine (Step 11).

Defines the directed execution topology:
1. START fan-out in parallel:
   - symptom_node
   - medical_history_node
   - laboratory_node
2. Fan-in aggregation into:
   - risk_prediction_node (synthesizes domain agent findings + clinical formulas + ML models)
3. Directs to END (ready for Step 12 debate loop extension).
"""

import logging
from typing import Optional

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.graph.nodes import (
    laboratory_node,
    medical_history_node,
    risk_prediction_node,
    symptom_node,
)
from app.graph.state import ClinicalAgentState

logger = logging.getLogger("graph.workflow")

_COMPILED_GRAPH: Optional[CompiledStateGraph] = None


def build_clinical_orchestration_graph() -> StateGraph:
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

    # 4. Termination (or routing to debate in Step 12)
    builder.add_edge("risk_prediction_node", END)

    return builder


def get_compiled_clinical_graph() -> CompiledStateGraph:
    """Retrieve or construct the singleton compiled LangGraph instance."""
    global _COMPILED_GRAPH
    if _COMPILED_GRAPH is None:
        logger.info("Compiling MedOracle Clinical Multi-Agent LangGraph...")
        builder = build_clinical_orchestration_graph()
        _COMPILED_GRAPH = builder.compile()
        logger.info("MedOracle LangGraph compiled successfully.")
    return _COMPILED_GRAPH


def run_clinical_graph(state: ClinicalAgentState) -> ClinicalAgentState:
    """Execute the clinical orchestration graph synchronously."""
    graph = get_compiled_clinical_graph()
    result = graph.invoke(state)
    return result


async def arun_clinical_graph(state: ClinicalAgentState) -> ClinicalAgentState:
    """Execute the clinical orchestration graph asynchronously."""
    graph = get_compiled_clinical_graph()
    result = await graph.ainvoke(state)
    return result
