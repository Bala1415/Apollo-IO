"""
state.py — Unified GraphState for the full Lead Intelligence Pipeline.

Shared across all 6 LangGraph agents. Each agent reads from this state
and writes ONLY its own designated key.

Agent → State Key mapping:
  Research Agent       → state["research"]
  Behavior Agent       → state["behavior"]
  Company Fit Agent    → state["company_fit"]
  Qualification Agent  → state["qualification"]
  Lead Score Agent     → state["lead_score"]
  Recommendation Agent → state["recommendation"]
"""
from typing import Any, Dict, List, Optional
from typing_extensions import TypedDict


class GraphState(TypedDict, total=False):
    # --- Input fields (set by Chrome Extension / Backend) ---
    lead_id:          str
    company_domain:   str
    email:            str
    browser_data:     Dict[str, Any]    # Raw browsing data from extension
    interest_profile: Dict[str, Any]    # Interest scores/topics from extension
    icp_rules:        Dict[str, Any]    # Optional custom ICP override

    # --- Agent outputs (each agent writes exactly one key) ---
    research:         Dict[str, Any]    # Research Agent output
    behavior:         Dict[str, Any]    # Behavior / Intent Analysis Agent output
    company_fit:      Dict[str, Any]    # Company Fit Agent output
    qualification:    Dict[str, Any]    # Qualification Agent output
    lead_score:       Dict[str, Any]    # Lead Score Agent output
    recommendation:   Dict[str, Any]    # Recommendation Agent output
