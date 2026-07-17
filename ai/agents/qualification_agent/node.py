"""
node.py — LangGraph node for the Qualification Agent.

Reads:  state["company_fit"], state["behavior"]
Writes: state["qualification"]

Determines whether a company is a qualified sales lead using a Deterministic Rule Engine.
0 LLM Calls.
"""
import logging
import time
from typing import Any, Dict

from langchain_core.runnables import RunnableConfig
from ai.rule_engine.qualification_rules import evaluate_qualification

logger = logging.getLogger(__name__)

def qualification_node(
    state: Dict[str, Any], config: RunnableConfig = None
) -> Dict[str, Any]:
    """
    LangGraph node — Qualification Agent.
    Evaluates whether the lead meets qualification criteria deterministically.
    Returns only {"qualification": <LeadQualification dict>}.
    """
    start_time = time.time()
    logger.info("=" * 60)
    logger.info("Qualification Agent (Rule Engine) — Starting")

    company_domain = state.get("company_domain", "")
    
    try:
        result = evaluate_qualification(state)
        
        elapsed = round(time.time() - start_time, 2)
        logger.info(f"Qualification Agent complete in {elapsed}s — qualified={result.get('qualified', False)}")
        logger.info("=" * 60)

        return {"qualification": result}

    except Exception as e:
        logger.error(f"Qualification Agent failed for {company_domain}: {e}")
        return {"qualification": {}}
