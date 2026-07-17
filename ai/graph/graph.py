"""
graph.py — Full LangGraph pipeline wiring all 6 agents.

Agent execution order:
  1. Research Agent       → state["research"]
  2. Behavior Agent       → state["behavior"]
  3. Company Fit Agent    → state["company_fit"]
  4. Qualification Agent  → state["qualification"]
  5. Lead Score Agent     → state["lead_score"]
  6. Recommendation Agent → state["recommendation"]
"""
import logging
from langgraph.graph import StateGraph, START, END

from ai.graph.state import GraphState
from ai.agents.research.node import research_node
from ai.agents.behavior.node import behavior_node
from ai.agents.company_fit.node import company_fit_node
from ai.agents.qualification_agent.node import qualification_node
from ai.agents.lead_score_agent.node import lead_score_node
from ai.agents.recommendation_agent.node import recommendation_node

logger = logging.getLogger(__name__)


def build_graph() -> StateGraph:
    """
    Build and compile the full 6-agent Lead Intelligence LangGraph pipeline.
    Returns a compiled graph ready to be invoked.
    """
    workflow = StateGraph(GraphState)

    # Register all 6 agent nodes
    workflow.add_node("research",       research_node)
    workflow.add_node("behavior",       behavior_node)
    workflow.add_node("company_fit",    company_fit_node)
    workflow.add_node("qualification",  qualification_node)
    workflow.add_node("lead_score",     lead_score_node)
    workflow.add_node("recommendation", recommendation_node)

    # Sequential edges: each agent feeds the next
    workflow.add_edge(START,            "research")
    workflow.add_edge("research",       "behavior")
    workflow.add_edge("behavior",       "company_fit")
    workflow.add_edge("company_fit",    "qualification")
    workflow.add_edge("qualification",  "lead_score")
    workflow.add_edge("lead_score",     "recommendation")
    workflow.add_edge("recommendation", END)

    logger.info("LangGraph pipeline compiled with 6 agents.")
    return workflow.compile()


# Singleton compiled graph — import this in your FastAPI backend
compiled_graph = build_graph()
