"""
backend.graph.utils

Utility functions for inspecting and validating GraphState.
"""
from typing import List, Optional

from backend.graph.state import GraphState
from backend.graph.constants import ProcessingStage, AgentName

def get_missing_fields(state: GraphState, required_fields: List[str]) -> List[str]:
    """
    Checks the GraphState for any missing or None required fields.
    Returns a list of field names that are missing.
    """
    missing = []
    for field in required_fields:
        if field not in state or state.get(field) is None:
            missing.append(field)
    return missing

def has_agent_completed(state: GraphState, agent_name: str) -> bool:
    """
    Checks if a specific agent has already completed its processing.
    """
    completed = state.get("completed_agents", [])
    if isinstance(agent_name, AgentName):
        return agent_name.value in completed
    return agent_name in completed

def get_current_workflow_stage(state: GraphState) -> Optional[str]:
    """
    Returns the current processing stage of the GraphState.
    """
    return state.get("processing_stage")

def is_graph_execution_complete(state: GraphState) -> bool:
    """
    Checks if the graph has finished executing.
    Returns True if stage is COMPLETED or FAILED.
    """
    stage = state.get("processing_stage")
    return stage in [ProcessingStage.COMPLETED.value, ProcessingStage.FAILED.value]
