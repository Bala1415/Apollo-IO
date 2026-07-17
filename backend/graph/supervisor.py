"""
backend.graph.supervisor

Implements the LangGraph Supervisor for orchestrating the execution of AI Agents.
The Supervisor is strictly responsible for orchestration and does not execute business logic.
"""

import logging
from enum import Enum
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timezone

from backend.graph.state import (
    GraphState, 
    update_state, 
    deep_copy_state, 
    mark_agent_completed as state_mark_agent_completed, 
    mark_failure as state_mark_failure
)

logger = logging.getLogger(__name__)

# ==========================================
# Enums & Constants
# ==========================================

class SupervisorStatus(str, Enum):
    """Supported statuses for the execution graph."""
    INITIALIZED = "INITIALIZED"
    VALIDATED = "VALIDATED"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    FAILED = "FAILED"
    RETRYING = "RETRYING"
    COMPLETED = "COMPLETED"
    TERMINATED = "TERMINATED"

class SupervisorStage(str, Enum):
    """Supported workflow stages for the execution graph."""
    VALIDATION = "Validation"
    RESEARCH = "Research"
    COMPANY_PROFILE = "Company Profile"
    INDUSTRY_CLASSIFICATION = "Industry Classification"
    QUALIFICATION = "Qualification"
    LEAD_SCORING = "Lead Scoring"
    RECOMMENDATION = "Recommendation"
    FINAL_REPORT = "Final Report"
    COMPLETED = "Completed"

class AgentOrder(str, Enum):
    """Order of agent execution."""
    RESEARCH_AGENT = "ResearchAgent"
    COMPANY_PROFILE_AGENT = "CompanyProfileAgent"
    INDUSTRY_CLASSIFICATION_AGENT = "IndustryClassificationAgent"
    LEAD_QUALIFICATION_AGENT = "LeadQualificationAgent"
    LEAD_SCORE_AGENT = "LeadScoreAgent"
    RECOMMENDATION_AGENT = "RecommendationAgent"

AGENT_EXECUTION_ORDER = [
    AgentOrder.RESEARCH_AGENT,
    AgentOrder.COMPANY_PROFILE_AGENT,
    AgentOrder.INDUSTRY_CLASSIFICATION_AGENT,
    AgentOrder.LEAD_QUALIFICATION_AGENT,
    AgentOrder.LEAD_SCORE_AGENT,
    AgentOrder.RECOMMENDATION_AGENT
]

STAGE_MAPPING = {
    AgentOrder.RESEARCH_AGENT: SupervisorStage.RESEARCH,
    AgentOrder.COMPANY_PROFILE_AGENT: SupervisorStage.COMPANY_PROFILE,
    AgentOrder.INDUSTRY_CLASSIFICATION_AGENT: SupervisorStage.INDUSTRY_CLASSIFICATION,
    AgentOrder.LEAD_QUALIFICATION_AGENT: SupervisorStage.QUALIFICATION,
    AgentOrder.LEAD_SCORE_AGENT: SupervisorStage.LEAD_SCORING,
    AgentOrder.RECOMMENDATION_AGENT: SupervisorStage.RECOMMENDATION
}

MAX_RETRIES = 3

# ==========================================
# Internal Helper
# ==========================================

def _log_execution_step(
    state: GraphState, 
    action: str, 
    prev_agent: Optional[str], 
    next_agent: Optional[str], 
    stage: Union[str, SupervisorStage],
    message: str
) -> None:
    """
    Internal helper to log every execution step and store it in execution history.
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    current_agent = state.get("current_agent", "Supervisor")
    retry_count = state.get("retry_count", 0)
    status = state.get("status", SupervisorStatus.INITIALIZED.value)
    
    stage_str = stage.value if isinstance(stage, SupervisorStage) else str(stage)
    
    log_entry = {
        "timestamp": timestamp,
        "action": action,
        "current_agent": current_agent,
        "previous_agent": prev_agent,
        "next_agent": next_agent,
        "stage": stage_str,
        "retry_count": retry_count,
        "status": status,
        "message": message
    }
    
    if "execution_trace" not in state:
        state["execution_trace"] = []
    state["execution_trace"].append(log_entry)
    
    logger.info(f"[Supervisor] [{stage_str}] [{status}] {message} | Current: {current_agent} -> Next: {next_agent}")


# ==========================================
# Core Functions
# ==========================================

def initialize_graph(state: GraphState) -> GraphState:
    """
    Initializes the execution graph. Sets up internal tracking, status, and stages.
    """
    new_state = deep_copy_state(state)
    _log_execution_step(new_state, "initialize_graph", None, None, SupervisorStage.VALIDATION, "Initializing Graph")
    
    update = {
        "status": SupervisorStatus.INITIALIZED.value,
        "processing_stage": SupervisorStage.VALIDATION.value,
        "retry_count": 0,
        "errors": new_state.get("errors", []),
        "completed_agents": new_state.get("completed_agents", []),
        "execution_trace": new_state.get("execution_trace", [])
    }
    return update_state(new_state, update, agent_name="Supervisor")

def validate_graph_state(state: GraphState) -> bool:
    """
    Validates that the provided state is capable of beginning execution.
    Returns True if valid, False otherwise.
    """
    status = state.get("status")
    if status not in [SupervisorStatus.INITIALIZED.value, SupervisorStatus.RETRYING.value]:
        logger.warning(f"Graph state validation failed. Invalid status: {status}")
        return False
        
    _log_execution_step(state, "validate_graph_state", None, None, state.get("processing_stage", SupervisorStage.VALIDATION), "Graph State Validated")
    return True

def start_execution(state: GraphState) -> GraphState:
    """
    Starts the execution of the workflow. Transitions state to RUNNING.
    """
    new_state = deep_copy_state(state)
    
    # First, mark it as validated.
    update_validated = {
        "status": SupervisorStatus.VALIDATED.value,
    }
    new_state = update_state(new_state, update_validated, agent_name="Supervisor")
    
    _log_execution_step(new_state, "start_execution", None, AGENT_EXECUTION_ORDER[0].value, SupervisorStage.RESEARCH, "Execution Started")
    
    # Then transition to running the first agent.
    update_running = {
        "status": SupervisorStatus.RUNNING.value,
        "processing_stage": SupervisorStage.RESEARCH.value,
        "current_agent": AGENT_EXECUTION_ORDER[0].value
    }
    return update_state(new_state, update_running, agent_name="Supervisor")

def determine_next_agent(state: GraphState) -> Optional[str]:
    """
    Determines the next agent to execute based on completed agents.
    Returns the agent name if found, else None.
    """
    completed_agents = state.get("completed_agents", [])
    for agent in AGENT_EXECUTION_ORDER:
        if agent.value not in completed_agents:
            return agent.value
    return None

def execute_next_agent(state: GraphState) -> GraphState:
    """
    Prepares the state for the execution of the next agent.
    If no agents are left, terminates execution.
    """
    new_state = deep_copy_state(state)
    current = new_state.get("current_agent")
    next_agent = determine_next_agent(new_state)
    
    if not next_agent:
        return terminate_execution(new_state, success=True, reason="All agents completed")
        
    next_agent_enum = AgentOrder(next_agent)
    stage = STAGE_MAPPING.get(next_agent_enum, SupervisorStage.COMPLETED)
    
    update = {
        "current_agent": next_agent,
        "processing_stage": stage.value,
        "status": SupervisorStatus.RUNNING.value
    }
    
    _log_execution_step(new_state, "execute_next_agent", current, next_agent, stage, f"Transitioning to {next_agent}")
    
    return update_state(new_state, update, agent_name="Supervisor")

def mark_agent_completed(state: GraphState, agent_name: str) -> GraphState:
    """
    Marks the given agent as successfully completed.
    Resets the retry counter upon success.
    """
    new_state = deep_copy_state(state)
    state_mark_agent_completed(new_state, agent_name)
    
    _log_execution_step(new_state, "mark_agent_completed", agent_name, None, new_state.get("processing_stage", SupervisorStage.COMPLETED), f"{agent_name} completed successfully")
    
    update = {
        "retry_count": 0
    }
    return update_state(new_state, update, agent_name="Supervisor")

def mark_agent_failed(state: GraphState, agent_name: str, error_message: str) -> GraphState:
    """
    Marks the given agent as failed and appends the error message.
    Transitions status to FAILED.
    """
    new_state = deep_copy_state(state)
    state_mark_failure(new_state, error_message, agent_name)
    
    update = {
        "status": SupervisorStatus.FAILED.value
    }
    new_state = update_state(new_state, update, agent_name="Supervisor")
    
    _log_execution_step(new_state, "mark_agent_failed", agent_name, None, new_state.get("processing_stage", SupervisorStage.COMPLETED), f"{agent_name} failed: {error_message}")
    
    return new_state

def can_retry(state: GraphState) -> bool:
    """
    Checks if the graph can retry the current operation based on max retries.
    """
    retry_count = state.get("retry_count", 0)
    return retry_count < MAX_RETRIES

def retry_agent(state: GraphState, agent_name: str) -> GraphState:
    """
    Increments retry count and sets status to RETRYING.
    If max retries are exceeded, it terminates the graph.
    """
    new_state = deep_copy_state(state)
    retries = new_state.get("retry_count", 0)
    
    if not can_retry(new_state):
        return terminate_execution(new_state, success=False, reason="Max retries exceeded")
        
    update = {
        "retry_count": retries + 1,
        "status": SupervisorStatus.RETRYING.value
    }
    
    _log_execution_step(new_state, "retry_agent", agent_name, agent_name, new_state.get("processing_stage", SupervisorStage.COMPLETED), f"Retrying {agent_name} (Attempt {retries + 1})")
    
    return update_state(new_state, update, agent_name="Supervisor")

def rollback_if_needed(state: GraphState) -> GraphState:
    """
    Provides a hook for rolling back changes if the state is corrupted or execution failed fatally.
    Terminates the execution if the state was marked FAILED.
    """
    new_state = deep_copy_state(state)
    if new_state.get("status") == SupervisorStatus.FAILED.value:
         update = {
             "status": SupervisorStatus.TERMINATED.value
         }
         return update_state(new_state, update, agent_name="Supervisor")
    return new_state

def skip_agent(state: GraphState, agent_name: str) -> GraphState:
    """
    Explicitly skips an agent by marking it completed without executing it.
    """
    new_state = deep_copy_state(state)
    _log_execution_step(new_state, "skip_agent", agent_name, None, new_state.get("processing_stage", SupervisorStage.COMPLETED), f"Skipping {agent_name}")
    return mark_agent_completed(new_state, agent_name)

def can_continue(state: GraphState) -> bool:
    """
    Checks if the graph can proceed to the next agent.
    Cannot continue if FAILED, TERMINATED, or COMPLETED.
    """
    status = state.get("status")
    if status in [SupervisorStatus.FAILED.value, SupervisorStatus.TERMINATED.value, SupervisorStatus.COMPLETED.value]:
        return False
    return True

def is_completed(state: GraphState) -> bool:
    """
    Checks if all agents have completed.
    """
    completed_agents = state.get("completed_agents", [])
    for agent in AGENT_EXECUTION_ORDER:
        if agent.value not in completed_agents:
            return False
    return True

def terminate_execution(state: GraphState, success: bool, reason: str = "") -> GraphState:
    """
    Terminates execution safely, marking final status and stage.
    """
    new_state = deep_copy_state(state)
    status = SupervisorStatus.COMPLETED.value if success else SupervisorStatus.TERMINATED.value
    stage = SupervisorStage.COMPLETED.value if success else new_state.get("processing_stage", SupervisorStage.COMPLETED.value)
    
    update = {
        "status": status,
        "processing_stage": stage
    }
    
    msg = f"Execution Terminated. Success: {success}. Reason: {reason}"
    _log_execution_step(new_state, "terminate_execution", new_state.get("current_agent"), None, stage, msg)
    
    return update_state(new_state, update, agent_name="Supervisor")

def finalize_graph(state: GraphState) -> GraphState:
    """
    Finalizes graph execution, ensuring all statuses and logs are cleanly closed.
    """
    new_state = deep_copy_state(state)
    if is_completed(new_state):
        update = {
            "status": SupervisorStatus.COMPLETED.value,
            "processing_stage": SupervisorStage.COMPLETED.value
        }
        new_state = update_state(new_state, update, agent_name="Supervisor")
        _log_execution_step(new_state, "finalize_graph", None, None, SupervisorStage.COMPLETED, "Graph Finalized Successfully")
    return new_state
