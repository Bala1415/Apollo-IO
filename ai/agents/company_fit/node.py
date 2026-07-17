"""
node.py — LangGraph node for the Company Fit Agent.

Orchestrates the full hybrid two-layer pipeline:
  Layer 1 — Deterministic Rule Engine (no LLM) -> rule_engine/company_fit_rules.py
  Layer 2 — LLM Reasoning -> Uses llm_service
"""
import logging
import time
from typing import Any, Dict, Optional

from langchain_core.runnables import RunnableConfig

from .icp import load_icp, ICP
from ai.rule_engine.company_fit_rules import calculate_company_fit
from .tools import compute_fit_score, detect_missing_fields, build_fit_context
from .prompt import get_company_fit_prompt
from .parser import get_company_fit_parser, parse_company_fit_with_fallback
from .schemas import CompanyFit, RuleEngineResult
from .similarity import score_to_fit_label
from ai.services.llm_service import llm_service

logger = logging.getLogger(__name__)

def _build_partial_result(
    rule_result: RuleEngineResult,
    fit_score: float,
    missing: list,
) -> Dict[str, Any]:
    return CompanyFit(
        overall_fit=score_to_fit_label(fit_score),
        fit_score=fit_score,
        rule_engine=rule_result,
        alignment=None,
        strengths=[],
        risks=["LLM reasoning stage failed — qualitative analysis unavailable"],
        missing_information=missing,
        reasoning="LLM reasoning could not be completed. Fit score is based on deterministic rule engine only.",
        confidence=0.4,
    ).model_dump()

def company_fit_node(
    state: Dict[str, Any],
    config: RunnableConfig = None,
    icp: Optional[ICP] = None,
) -> Dict[str, Any]:
    start_time = time.time()
    logger.info("=" * 60)
    logger.info("Company Fit Agent — Starting hybrid pipeline")

    research = state.get("research") or {}
    behavior = state.get("behavior") or {}

    if not research and not behavior:
        return {"company_fit": {}}

    active_icp = load_icp(icp)
    from .icp import icp_to_dict
    state["icp_rules"] = icp_to_dict(active_icp)

    # Layer 1: Rule Engine
    scores_dict = calculate_company_fit(state)
    rule_result = RuleEngineResult(
        industry_match=scores_dict["industry_match"],
        technology_match=scores_dict["technology_match"],
        persona_match=scores_dict["persona_match"],
        market_match=scores_dict["market_match"],
        business_model_match=scores_dict["business_model_match"],
        intent_match=scores_dict["intent_match"],
    )

    fit_score = compute_fit_score(rule_result)
    missing_info = detect_missing_fields(research, behavior)
    fit_context = build_fit_context(research, behavior, rule_result, active_icp, fit_score)

    # Layer 2: LLM (Reasoning only)
    parser = get_company_fit_parser()
    prompt = get_company_fit_prompt()
    chain = prompt | llm_service._client

    try:
        response = llm_service.invoke(chain, {
            "fit_context": fit_context,
            "format_instructions": parser.get_format_instructions()
        })
        raw_output = response.content if hasattr(response, "content") else str(response)
        result = parse_company_fit_with_fallback(raw_output, parser, CompanyFit)
    except Exception as e:
        logger.error(f"LLM/Parse failed: {e}")
        return {"company_fit": _build_partial_result(rule_result, fit_score, missing_info)}

    if result:
        result.rule_engine = rule_result
        if result.fit_score is None or abs((result.fit_score or 0) - fit_score) > 10:
            result.fit_score = fit_score
        if not result.missing_information:
            result.missing_information = missing_info
        result.overall_fit = score_to_fit_label(result.fit_score)
        
        elapsed = round(time.time() - start_time, 2)
        logger.info(f"Company Fit Agent complete in {elapsed}s")
        return {"company_fit": result.model_dump()}

    return {"company_fit": _build_partial_result(rule_result, fit_score, missing_info)}
