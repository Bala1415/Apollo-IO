"""
backend.graph.state

Defines the single source of truth GraphState for all AI Agents in LangGraph.
"""
import copy
import json
import logging
from typing import TypedDict, Optional, List, Dict, Any, Union
from datetime import datetime, timezone

from backend.graph.constants import ProcessingStage

logger = logging.getLogger(__name__)

class GraphState(TypedDict, total=False):
    """
    The shared state object for the LangGraph workflow.
    Supports partial updates and acts as the single source of truth.
    """
    
    # --- General Information ---
    scan_id: Optional[str]
    lead_id: Optional[str]
    timestamp: Optional[str]
    status: Optional[str]
    processing_stage: Optional[str]
    errors: List[str]
    warnings: List[str]

    # --- User Information ---
    user_profile: Optional[Dict[str, Any]]
    business_email: Optional[str]
    company_domain: Optional[str]
    browser_history: List[str]
    visited_domains: List[str]
    active_website: Optional[str]
    interest_categories: List[str]
    interest_profile: Optional[Dict[str, Any]]
    history_summary: Optional[str]

    # --- Company Research ---
    company_research: Optional[Dict[str, Any]]
    website: Optional[str]
    products: List[str]
    services: List[str]
    customers: List[str]
    employees: Optional[int]
    funding: Optional[str]
    headquarters: Optional[str]
    news: List[str]
    social_links: Dict[str, str]

    # --- Company Profile ---
    company_profile: Optional[Dict[str, Any]]
    business_model: Optional[str]
    company_size: Optional[str]
    growth_stage: Optional[str]
    revenue_estimate: Optional[str]
    technology_stack: List[str]
    organization_type: Optional[str]

    # --- Industry ---
    industry: Optional[str]
    sector: Optional[str]
    sub_industry: Optional[str]
    naics: Optional[str]
    sic: Optional[str]
    industry_confidence: Optional[float]

    # --- Qualification ---
    qualification: Optional[str]
    qualification_reason: Optional[str]
    icp_match: Optional[bool]
    budget_fit: Optional[str]
    technology_fit: Optional[str]
    need_analysis: Optional[str]

    # --- Lead Score ---
    lead_score: Optional[float]
    confidence: Optional[float]
    score_breakdown: Optional[Dict[str, float]]
    intent_score: Optional[float]
    growth_score: Optional[float]
    industry_score: Optional[float]
    company_size_score: Optional[float]
    technology_score: Optional[float]

    # --- Recommendation ---
    priority: Optional[str]
    recommendation: Optional[str]
    next_action: Optional[str]
    sales_pitch: Optional[str]
    executive_summary: Optional[str]
    sales_notes: Optional[str]

    # --- Final Report ---
    reasoning: Optional[str]
    final_report: Optional[str]
    report_id: Optional[str]
    generated_at: Optional[str]

    # --- Metadata ---
    processing_time: Optional[float]
    agent_history: List[str]
    completed_agents: List[str]
    current_agent: Optional[str]
    retry_count: int
    execution_trace: List[Dict[str, Any]]


# ==========================================
# Helper Functions
# ==========================================

def create_initial_state(payload: Dict[str, Any] = None) -> GraphState:
    """
    Initializes a new GraphState with default values and optional starting payload.
    """
    state: GraphState = {
        "errors": [],
        "warnings": [],
        "browser_history": [],
        "visited_domains": [],
        "interest_categories": [],
        "products": [],
        "services": [],
        "customers": [],
        "news": [],
        "social_links": {},
        "technology_stack": [],
        "agent_history": [],
        "completed_agents": [],
        "retry_count": 0,
        "execution_trace": [],
        "processing_stage": ProcessingStage.INITIALIZED.value,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    if payload:
        # Merge payload selectively or directly if it maps to state
        for k, v in payload.items():
            if k in GraphState.__annotations__:
                state[k] = v
                
    logger.info("Created initial GraphState.")
    return state


def update_state(state: GraphState, updates: Dict[str, Any], agent_name: str = None) -> GraphState:
    """
    Updates the GraphState in-place with new fields.
    Optionally logs the agent responsible for the update.
    """
    for key, value in updates.items():
        if key in GraphState.__annotations__:
            state[key] = value
        else:
            logger.warning(f"Attempted to update unknown state field: {key}")
            
    if agent_name:
        logger.info(f"[{agent_name}] Updated fields: {list(updates.keys())}")
        
    return state


def merge_state(state1: GraphState, state2: GraphState) -> GraphState:
    """
    Merges two GraphStates into a new GraphState. 
    Lists are concatenated, dicts are updated.
    """
    new_state = deep_copy_state(state1)
    
    for key, value in state2.items():
        if isinstance(value, list) and key in new_state and isinstance(new_state[key], list):
            new_state[key].extend(value)
            # Remove duplicates while preserving order
            new_state[key] = list(dict.fromkeys(new_state[key]))
        elif isinstance(value, dict) and key in new_state and isinstance(new_state[key], dict):
            new_state[key].update(value)
        else:
            new_state[key] = value
            
    return new_state


def append_agent_history(state: GraphState, agent_name: str) -> None:
    """Appends an agent to the agent_history list."""
    if "agent_history" not in state:
        state["agent_history"] = []
    state["agent_history"].append(agent_name)


def set_processing_stage(state: GraphState, stage: Union[ProcessingStage, str]) -> None:
    """Sets the current processing stage."""
    stage_val = stage.value if isinstance(stage, ProcessingStage) else stage
    state["processing_stage"] = stage_val
    logger.info(f"Processing stage transitioned to: {stage_val}")


def mark_agent_completed(state: GraphState, agent_name: str) -> None:
    """Marks an agent as successfully completed."""
    if "completed_agents" not in state:
        state["completed_agents"] = []
    if agent_name not in state["completed_agents"]:
        state["completed_agents"].append(agent_name)
    logger.info(f"Agent completed: {agent_name}")


def mark_failure(state: GraphState, error_msg: str, agent_name: str = None) -> None:
    """Marks the state as failed and appends the error message."""
    if "errors" not in state:
        state["errors"] = []
    
    formatted_msg = f"[{agent_name}] {error_msg}" if agent_name else error_msg
    state["errors"].append(formatted_msg)
    set_processing_stage(state, ProcessingStage.FAILED)
    logger.error(f"State failed: {formatted_msg}")


def reset_state() -> GraphState:
    """Returns a completely fresh state."""
    return create_initial_state()


def serialize_state(state: GraphState) -> str:
    """Converts the GraphState to a JSON string."""
    try:
        return json.dumps(state, default=str)
    except TypeError as e:
        logger.error(f"Failed to serialize state: {e}")
        return "{}"


def deserialize_state(data: str) -> GraphState:
    """Converts a JSON string back into a GraphState."""
    try:
        parsed = json.loads(data)
        return parsed
    except json.JSONDecodeError as e:
        logger.error(f"Failed to deserialize state: {e}")
        return create_initial_state()


def deep_copy_state(state: GraphState) -> GraphState:
    """Returns a deep copy of the GraphState."""
    return copy.deepcopy(state)
