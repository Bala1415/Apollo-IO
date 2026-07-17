"""
node.py — LangGraph node for the Lead Score Agent.

Reads:  state["company_fit"], state["behavior"], state["qualification"]
Writes: state["lead_score"]

Calculates the final numerical lead score using a Deterministic Rule Engine.
0 LLM Calls.
"""
import logging
import time
from typing import Any, Dict

from langchain_core.runnables import RunnableConfig
from ai.rule_engine.lead_score_rules import calculate_lead_score

logger = logging.getLogger(__name__)

def lead_score_node(
    state: Dict[str, Any], config: RunnableConfig = None
) -> Dict[str, Any]:
    """
    LangGraph node — Lead Score Agent.
    Calculates the final numerical lead score (0–100) deterministically.
    Returns only {"lead_score": <LeadScore dict>}.
    """
    start_time = time.time()
    logger.info("=" * 60)
    logger.info("Lead Score Agent (Rule Engine) — Starting")

    company_domain = state.get("company_domain", "")
    
    try:
        result = calculate_lead_score(state)
        
        elapsed = round(time.time() - start_time, 2)
        logger.info(f"Lead Score Agent complete in {elapsed}s — score={result.get('lead_score', '?')}")
        logger.info("=" * 60)

        return {"lead_score": result}

    except Exception as e:
        logger.error(f"Lead Score Agent failed for {company_domain}: {e}")
        return {"lead_score": {}}

