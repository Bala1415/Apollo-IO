"""
node.py — LangGraph node for the Intent Analysis Agent (Behavior).
"""
import logging
import time
from typing import Any, Dict, Optional

from langchain_core.runnables import RunnableConfig

from .tools import (
    normalize_browser_data,
    normalize_interest_profile,
    compute_visit_frequency,
    detect_decision_signals,
    build_behavior_context,
)
from .prompt import get_behavior_prompt
from .parser import get_behavior_parser, parse_behavior_with_fallback
from .schemas import BehaviorAnalysis
from ai.services.llm_service import llm_service

logger = logging.getLogger(__name__)


def behavior_node(state: Dict[str, Any], config: RunnableConfig = None) -> Dict[str, Any]:
    start_time = time.time()
    logger.info("=" * 60)
    logger.info("Intent Analysis Agent — Starting pipeline")

    browser_data: Any = state.get("browser_data")
    interest_profile: Any = state.get("interest_profile")
    email: Optional[str] = state.get("email", "")
    company_domain: Optional[str] = state.get("company_domain", "")

    if not browser_data and not interest_profile:
        return {"behavior": {}}

    normalized_browser: Dict[str, Any] = {}
    try:
        normalized_browser = normalize_browser_data(browser_data)
    except Exception as e:
        logger.error(f"browser_data normalization failed: {e}")

    normalized_profile: Dict[str, Any] = {}
    try:
        normalized_profile = normalize_interest_profile(interest_profile)
    except Exception as e:
        logger.error(f"interest_profile normalization failed: {e}")

    visit_frequency = []
    try:
        visited_domains = normalized_browser.get("visited_domains", [])
        visit_frequency = compute_visit_frequency(visited_domains)
    except Exception as e:
        logger.warning(f"Visit frequency computation failed: {e}")

    decision_signals = []
    try:
        raw_urls = normalized_browser.get("raw_urls", [])
        visited_domains = normalized_browser.get("visited_domains", [])
        decision_signals = detect_decision_signals(raw_urls, visited_domains)
    except Exception as e:
        logger.warning(f"Decision signal detection failed: {e}")

    behavior_context = ""
    try:
        behavior_context = build_behavior_context(
            normalized_browser=normalized_browser,
            normalized_profile=normalized_profile,
            visit_frequency=visit_frequency,
            decision_signals=decision_signals,
            email=email,
            domain=company_domain,
        )
    except Exception as e:
        logger.error(f"Context building failed: {e}")

    if not behavior_context.strip():
        return {"behavior": {}}

    parser = get_behavior_parser()
    prompt = get_behavior_prompt()
    chain = prompt | llm_service._client

    raw_output: Optional[str] = None
    try:
        response = llm_service.invoke(
            chain,
            {
                "behavior_context": behavior_context,
                "format_instructions": parser.get_format_instructions(),
            },
        )
        raw_output = response.content if hasattr(response, "content") else str(response)
    except Exception as e:
        logger.error(f"LLM invocation failed after retries: {e}")
        return {"behavior": {}}

    result: Optional[BehaviorAnalysis] = None
    try:
        result = parse_behavior_with_fallback(raw_output, parser, BehaviorAnalysis)
    except Exception as e:
        logger.error(f"Parsing failed unexpectedly: {e}")

    elapsed = round(time.time() - start_time, 2)
    logger.info(f"Intent Analysis Agent complete in {elapsed}s")
    logger.info("=" * 60)

    if result:
        return {"behavior": result.model_dump()}

    return {"behavior": {}}
