"""Analysis session, multi-agent debate, and reasoning graph Pydantic v2 schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class AgentOutputResponse(BaseModel):
    """Structured output contract returned by an individual agent."""

    id: Optional[str] = None
    agent_role: str
    findings: str
    confidence: float = Field(..., ge=0.0, le=100.0)
    reasoning_chain: List[str] = Field(default_factory=list)
    evidence: List[str] = Field(default_factory=list)
    challenges: List[str] = Field(default_factory=list)
    metadata_payload: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ConsensusVerdictSchema(BaseModel):
    """Final consensus verdict reached by multi-agent debate protocol."""

    primary_risk_category: str
    overall_urgency: str  # "low", "moderate", "high", "immediate"
    consensus_confidence: float = Field(..., ge=0.0, le=100.0)
    summary: str


class GraphNode(BaseModel):
    """Reasoning graph node formatted for Flutter graphview."""

    id: str
    label: str
    type: str  # "symptom", "history", "lab", "risk", "consensus"
    confidence: Optional[float] = None


class GraphEdge(BaseModel):
    """Reasoning graph directed connection."""

    source: str
    target: str
    weight: Optional[float] = None
    label: Optional[str] = None


class ReasoningGraphSchema(BaseModel):
    """Complete reasoning graph with nodes and directed edges."""

    nodes: List[GraphNode]
    edges: List[GraphEdge]


class AnalysisStartRequest(BaseModel):
    """Request payload to initiate a multi-agent analysis session."""

    symptom_report_id: Optional[str] = None
    include_latest_labs: bool = True
    include_medical_history: bool = True


class AnalysisSessionStatusResponse(BaseModel):
    """Polling status schema for client progress indicators."""

    session_id: str
    status: str  # "pending", "running", "completed", "failed"
    current_phase: str
    progress_percent: int
    error_message: Optional[str] = None


class AnalysisSessionResponse(BaseModel):
    """Complete analysis session result including all agent outputs and debate."""

    id: str
    user_id: str
    symptom_report_id: Optional[str] = None
    status: str
    current_phase: str
    progress_percent: int
    consensus_verdict: Optional[Dict[str, Any]] = None
    debate_summary: Optional[Dict[str, Any]] = None
    disease_trajectory: Optional[Dict[str, Any]] = None
    counterfactuals: Optional[List[Dict[str, Any]]] = None
    reasoning_graph: Optional[Dict[str, Any]] = None
    recommended_specialty: Optional[str] = None
    error_message: Optional[str] = None
    completed_at: Optional[datetime] = None
    agent_outputs: List[AgentOutputResponse] = Field(default_factory=list)
    disclaimer: str = (
        "MedOracle is a decision-support assistant and does not provide clinical diagnosis. "
        "Consult a qualified healthcare professional."
    )
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
