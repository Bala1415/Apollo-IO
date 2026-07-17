"""
node.py — LangGraph node for the Recommendation Agent.

Reads:  state["research"], state["behavior"], state["company_fit"],
        state["qualification"], state["lead_score"]
Writes: state["recommendation"]

Generates the final actionable lead intelligence recommendation.
This is the LAST agent in the pipeline.
"""
import json
import logging
import time
from typing import Any, Dict, Optional

from langchain_core.runnables import RunnableConfig

from .schemas import Recommendation
from ai.prompts.recommendation_prompt import get_recommendation_prompt
from ai.services.llm_service import llm_service

logger = logging.getLogger(__name__)

def recommendation_node(
    state: Dict[str, Any], config: RunnableConfig = None
) -> Dict[str, Any]:
    start_time = time.time()
    logger.info("=" * 60)
    logger.info("Recommendation Agent — Starting")

    company_domain: str  = state.get("company_domain", "")
    research:       Dict = state.get("research") or {}
    behavior:       Dict = state.get("behavior") or {}
    company_fit:    Dict = state.get("company_fit") or {}
    qualification:  Dict = state.get("qualification") or {}
    lead_score:     Dict = state.get("lead_score") or {}

    industry = (research.get("business") or {}).get("industry", "Unknown")
    
    # CONTEXT COMPRESSION: Do not dump massive raw JSON. Extract only what Recommendation needs.
    compressed_research = {
        "company_name": (research.get("company") or {}).get("name", "Unknown"),
        "description": (research.get("company") or {}).get("description", ""),
        "executive_summary": research.get("executive_summary", ""),
        "business_model": (research.get("business") or {}).get("business_model", ""),
        "target_market": (research.get("business") or {}).get("target_market", ""),
    }
    
    compressed_company_fit = {
        "overall_fit": company_fit.get("overall_fit", ""),
        "fit_score": company_fit.get("fit_score", 0),
        "strengths": company_fit.get("strengths", []),
        "risks": company_fit.get("risks", []),
        "reasoning": company_fit.get("reasoning", ""),
    }
    
    compressed_behavior = {
        "primary_interest": behavior.get("primary_interest", ""),
        "commercial_intent": behavior.get("commercial_intent", ""),
        "decision_signals": behavior.get("decision_signals", []),
    }
    
    compressed_qual = {
        "qualified": qualification.get("qualified", False),
        "reason": qualification.get("qualification_reason", "")
    }

    parser = get_recommendation_prompt().output_parser if hasattr(get_recommendation_prompt(), "output_parser") else None
    if not parser:
        from langchain_core.output_parsers import PydanticOutputParser
        parser = PydanticOutputParser(pydantic_object=Recommendation)

    prompt = get_recommendation_prompt()
    chain  = prompt | llm_service._client

    logger.info(f"Invoking LLM for recommendation: {company_domain}")
    try:
        raw = llm_service.invoke(chain, {
            "format_instructions":   parser.get_format_instructions(),
            "company_domain":        company_domain,
            "industry":              industry,
            "lead_score":            json.dumps({"lead_score": lead_score.get("lead_score", 0)}, indent=2),
            "qualification_result":  json.dumps(compressed_qual, indent=2),
            "research_result":       json.dumps(compressed_research, indent=2),
            "company_profile_or_fit": json.dumps(compressed_company_fit, indent=2),
            "interest_profile":      json.dumps(compressed_behavior, indent=2),
        })
        text = raw.content if hasattr(raw, "content") else str(raw)

        result: Optional[Recommendation] = None
        try:
            result = parser.parse(text)
        except Exception:
            import re, json as _json
            m = re.search(r"\{.*\}", text, re.DOTALL)
            if m:
                result = Recommendation.model_validate(_json.loads(m.group()))

        elapsed = round(time.time() - start_time, 2)
        logger.info(f"Recommendation Agent complete in {elapsed}s — priority={getattr(result, 'priority', '?')}")
        logger.info("=" * 60)

        return {"recommendation": result.model_dump() if result else {}}

    except Exception as e:
        logger.error(f"Recommendation Agent failed for {company_domain}: {e}")
        return {"recommendation": {}}
