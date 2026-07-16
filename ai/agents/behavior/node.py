"""
node.py — LangGraph node for the Intent Analysis Agent (Behavior).

Pipeline:
  1. Read browser_data, interest_profile, email, company_domain from GraphState
  2. Normalize browser_data → canonical dict
  3. Normalize interest_profile → canonical dict
  4. Compute visit frequency ranking
  5. Detect decision signals from visited URLs
  6. Merge all signals into structured LLM context
  7. Invoke LLM with behavioral analysis prompt
  8. Parse and validate output with Pydantic (3-tier fallback)
  9. Write result to state["behavior"]
  10. Return updated state

ONLY state["behavior"] is written. All other state keys are untouched.
"""
import logging
import time
from typing import Any, Dict, Optional

from langchain_groq import ChatGroq
from langchain_core.runnables import RunnableConfig
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

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

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# LLM factory
# ---------------------------------------------------------------------------

def _build_llm() -> ChatGroq:
    """
    Instantiates the Groq LLM used by the Behavior Agent.
    Swap model name here or read from environment if needed.
    """
    return ChatGroq(model="llama-3.3-70b-versatile", temperature=0)


# ---------------------------------------------------------------------------
# Retryable LLM call
# ---------------------------------------------------------------------------

@retry(
    retry=retry_if_exception_type(Exception),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    reraise=True,
)
def _invoke_llm(chain, inputs: Dict[str, Any]) -> Any:
    """Invoke the LLM chain with exponential backoff retry on transient failures."""
    return chain.invoke(inputs)


# ---------------------------------------------------------------------------
# LangGraph node
# ---------------------------------------------------------------------------

def behavior_node(state: Dict[str, Any], config: RunnableConfig = None) -> Dict[str, Any]:
    """
    LangGraph node — Intent Analysis Agent.

    Reads behavioral signals from GraphState, runs preprocessing and LLM
    analysis, and returns only {"behavior": <BehaviorAnalysis dict>}.

    Never raises — always returns a valid dict (empty on total failure).
    """
    start_time = time.time()
    logger.info("=" * 60)
    logger.info("Intent Analysis Agent — Starting pipeline")

    # ------------------------------------------------------------------
    # 1. Extract inputs from GraphState
    # ------------------------------------------------------------------
    browser_data: Any = state.get("browser_data")
    interest_profile: Any = state.get("interest_profile")
    email: Optional[str] = state.get("email", "")
    company_domain: Optional[str] = state.get("company_domain", "")

    if not browser_data and not interest_profile:
        logger.warning("No browser_data or interest_profile in state. Returning empty behavior.")
        return {"behavior": {}}

    # ------------------------------------------------------------------
    # 2. Normalize browser_data
    # ------------------------------------------------------------------
    logger.info("Step 2: Normalizing browser data...")
    normalized_browser: Dict[str, Any] = {}
    try:
        normalized_browser = normalize_browser_data(browser_data)
        logger.info(
            f"Normalized browser_data: "
            f"{len(normalized_browser.get('visited_domains', []))} domains, "
            f"{len(normalized_browser.get('raw_urls', []))} URLs"
        )
    except Exception as e:
        logger.error(f"browser_data normalization failed: {e}")

    # ------------------------------------------------------------------
    # 3. Normalize interest_profile
    # ------------------------------------------------------------------
    logger.info("Step 3: Normalizing interest profile...")
    normalized_profile: Dict[str, Any] = {}
    try:
        normalized_profile = normalize_interest_profile(interest_profile)
        logger.info(f"Normalized interest_profile: {list(normalized_profile.keys())}")
    except Exception as e:
        logger.error(f"interest_profile normalization failed: {e}")

    # ------------------------------------------------------------------
    # 4. Visit frequency analysis
    # ------------------------------------------------------------------
    logger.info("Step 4: Computing visit frequency...")
    visit_frequency = []
    try:
        visited_domains = normalized_browser.get("visited_domains", [])
        visit_frequency = compute_visit_frequency(visited_domains)
        logger.info(f"Top domain: {visit_frequency[0]['domain'] if visit_frequency else 'none'}")
    except Exception as e:
        logger.warning(f"Visit frequency computation failed: {e}")

    # ------------------------------------------------------------------
    # 5. Detect decision signals
    # ------------------------------------------------------------------
    logger.info("Step 5: Detecting decision signals...")
    decision_signals = []
    try:
        raw_urls = normalized_browser.get("raw_urls", [])
        visited_domains = normalized_browser.get("visited_domains", [])
        decision_signals = detect_decision_signals(raw_urls, visited_domains)
        logger.info(f"{len(decision_signals)} decision signal(s) detected")
    except Exception as e:
        logger.warning(f"Decision signal detection failed: {e}")

    # ------------------------------------------------------------------
    # 6. Build LLM context
    # ------------------------------------------------------------------
    logger.info("Step 6: Building behavior context for LLM...")
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
        logger.info(f"Behavior context size: {len(behavior_context)} chars")
    except Exception as e:
        logger.error(f"Context building failed: {e}")

    if not behavior_context.strip():
        logger.error("Empty behavior context. Cannot invoke LLM. Returning empty behavior.")
        return {"behavior": {}}

    # ------------------------------------------------------------------
    # 7. LLM invocation
    # ------------------------------------------------------------------
    logger.info("Step 7: Invoking LLM for behavioral analysis...")
    llm = _build_llm()
    parser = get_behavior_parser()
    prompt = get_behavior_prompt()
    chain = prompt | llm

    raw_output: Optional[str] = None
    try:
        response = _invoke_llm(
            chain,
            {
                "behavior_context": behavior_context,
                "format_instructions": parser.get_format_instructions(),
            },
        )
        raw_output = response.content if hasattr(response, "content") else str(response)
        logger.info("LLM response received")
    except Exception as e:
        logger.error(f"LLM invocation failed after retries: {e}")
        return {"behavior": {}}

    # ------------------------------------------------------------------
    # 8. Parse and validate
    # ------------------------------------------------------------------
    logger.info("Step 8: Parsing and validating LLM output...")
    result: Optional[BehaviorAnalysis] = None
    try:
        result = parse_behavior_with_fallback(raw_output, parser, BehaviorAnalysis)
    except Exception as e:
        logger.error(f"Parsing failed unexpectedly: {e}")

    # ------------------------------------------------------------------
    # 9. Build and return state update
    # ------------------------------------------------------------------
    elapsed = round(time.time() - start_time, 2)
    logger.info(f"Intent Analysis Agent complete in {elapsed}s")
    logger.info("=" * 60)

    if result:
        logger.info(
            f"Intent: {result.commercial_intent} | "
            f"Stage: {result.research_stage} | "
            f"Confidence: {result.confidence} | "
            f"Primary: {result.primary_interest}"
        )
        return {"behavior": result.model_dump()}

    logger.error("All parsing attempts failed. Returning empty behavior.")
    return {"behavior": {}}
