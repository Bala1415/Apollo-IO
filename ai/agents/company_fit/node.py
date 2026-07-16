"""
node.py — LangGraph node for the Company Fit Agent.

Orchestrates the full hybrid two-layer pipeline:

  Layer 1 — Deterministic Rule Engine (no LLM)
    1.  Read state["research"] and state["behavior"]
    2.  Load ICP
    3.  Run Rule Engine → RuleEngineResult
    4.  Compute weighted fit_score
    5.  Detect missing information

  Layer 2 — LLM Reasoning
    6.  Build structured LLM context
    7.  Invoke LLM with Company Fit prompt
    8.  Parse and validate output (3-tier fallback)
    9.  Inject RuleEngineResult into validated output
    10. Write state["company_fit"]
    11. Return state

ONLY state["company_fit"] is written.
"""
import logging
import time
from typing import Any, Dict, Optional

from langchain_groq import ChatGroq
from langchain_core.runnables import RunnableConfig
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from .icp import load_icp, ICP
from .rule_engine import run_rule_engine
from .tools import compute_fit_score, detect_missing_fields, build_fit_context
from .prompt import get_company_fit_prompt
from .parser import get_company_fit_parser, parse_company_fit_with_fallback
from .schemas import CompanyFit, RuleEngineResult
from .similarity import score_to_fit_label

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# LLM factory
# ---------------------------------------------------------------------------

def _build_llm() -> ChatGroq:
    """Instantiate the Groq LLM. Swap model here or read from env."""
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
    """Invoke LLM chain with exponential backoff retry."""
    return chain.invoke(inputs)


# ---------------------------------------------------------------------------
# Graceful degradation — build partial output from rule engine only
# ---------------------------------------------------------------------------

def _build_partial_result(
    rule_result: RuleEngineResult,
    fit_score: float,
    missing: list,
) -> Dict[str, Any]:
    """
    If LLM fails entirely, return a deterministic-only partial result
    so downstream agents still receive meaningful data.
    """
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


# ---------------------------------------------------------------------------
# LangGraph Node
# ---------------------------------------------------------------------------

def company_fit_node(
    state: Dict[str, Any],
    config: RunnableConfig = None,
    icp: Optional[ICP] = None,
) -> Dict[str, Any]:
    """
    LangGraph node — Company Fit Agent.

    Accepts an optional `icp` parameter for dependency injection.
    If not provided, the default ICP is loaded automatically.

    Returns only {"company_fit": <CompanyFit dict>}.
    Never raises — always returns a valid dict.
    """
    start_time = time.time()
    logger.info("=" * 60)
    logger.info("Company Fit Agent — Starting hybrid pipeline")

    # ------------------------------------------------------------------
    # 1. Extract state inputs
    # ------------------------------------------------------------------
    research: Dict[str, Any] = state.get("research") or {}
    behavior: Dict[str, Any] = state.get("behavior") or {}

    if not research and not behavior:
        logger.warning("Both research and behavior are empty. Returning empty company_fit.")
        return {"company_fit": {}}

    if not research:
        logger.warning("state['research'] is empty — rule engine results will be limited.")
    if not behavior:
        logger.warning("state['behavior'] is empty — intent scoring will be 0.")

    # ------------------------------------------------------------------
    # 2. Load ICP
    # ------------------------------------------------------------------
    logger.info("Step 2: Loading ICP...")
    active_icp = load_icp(icp)
    logger.info(f"ICP loaded: '{active_icp.name}'")

    # ------------------------------------------------------------------
    # 3. Layer 1 — Deterministic Rule Engine
    # ------------------------------------------------------------------
    logger.info("Step 3: Running deterministic Rule Engine (Layer 1)...")
    rule_result: RuleEngineResult = RuleEngineResult()
    try:
        rule_result = run_rule_engine(research, behavior, active_icp)
    except Exception as e:
        logger.error(f"Rule Engine failed: {e}. Using zero scores.")

    # ------------------------------------------------------------------
    # 4. Compute overall fit_score
    # ------------------------------------------------------------------
    logger.info("Step 4: Computing overall fit_score...")
    fit_score = 0.0
    try:
        fit_score = compute_fit_score(rule_result)
        logger.info(f"Fit score: {fit_score}/100 ({score_to_fit_label(fit_score)})")
    except Exception as e:
        logger.error(f"fit_score computation failed: {e}")

    # ------------------------------------------------------------------
    # 5. Detect missing information
    # ------------------------------------------------------------------
    logger.info("Step 5: Detecting missing information fields...")
    missing_info = []
    try:
        missing_info = detect_missing_fields(research, behavior)
        logger.info(f"{len(missing_info)} missing field(s) detected")
    except Exception as e:
        logger.warning(f"Missing field detection failed: {e}")

    # ------------------------------------------------------------------
    # 6. Build LLM context
    # ------------------------------------------------------------------
    logger.info("Step 6: Building LLM context...")
    fit_context = ""
    try:
        fit_context = build_fit_context(research, behavior, rule_result, active_icp, fit_score)
        logger.info(f"LLM context size: {len(fit_context)} chars")
    except Exception as e:
        logger.error(f"Context building failed: {e}")

    if not fit_context.strip():
        logger.error("Empty LLM context. Returning deterministic-only partial result.")
        return {"company_fit": _build_partial_result(rule_result, fit_score, missing_info)}

    # ------------------------------------------------------------------
    # 7. Layer 2 — LLM Reasoning
    # ------------------------------------------------------------------
    logger.info("Step 7: Invoking LLM for compatibility reasoning (Layer 2)...")
    llm    = _build_llm()
    parser = get_company_fit_parser()
    prompt = get_company_fit_prompt()
    chain  = prompt | llm

    raw_output: Optional[str] = None
    try:
        response = _invoke_llm(
            chain,
            {
                "fit_context": fit_context,
                "format_instructions": parser.get_format_instructions(),
            },
        )
        raw_output = response.content if hasattr(response, "content") else str(response)
        logger.info("LLM response received")
    except Exception as e:
        logger.error(f"LLM invocation failed after retries: {e}")
        return {"company_fit": _build_partial_result(rule_result, fit_score, missing_info)}

    # ------------------------------------------------------------------
    # 8. Parse and validate LLM output
    # ------------------------------------------------------------------
    logger.info("Step 8: Parsing and validating LLM output...")
    result: Optional[CompanyFit] = None
    try:
        result = parse_company_fit_with_fallback(raw_output, parser, CompanyFit)
    except Exception as e:
        logger.error(f"Parsing failed: {e}")

    # ------------------------------------------------------------------
    # 9. Inject deterministic scores (always override LLM-computed scores)
    # ------------------------------------------------------------------
    if result:
        # Rule engine scores are ground truth — override whatever LLM returned
        result.rule_engine = rule_result
        # If LLM fit_score drifted significantly, anchor it to rule engine
        if result.fit_score is None or abs((result.fit_score or 0) - fit_score) > 10:
            logger.warning(
                f"LLM fit_score ({result.fit_score}) deviates from rule engine ({fit_score}). "
                "Anchoring to rule engine score."
            )
            result.fit_score = fit_score
        # Ensure missing_info always reflects reality
        if not result.missing_information:
            result.missing_information = missing_info
        # Ensure overall_fit label is consistent with fit_score
        result.overall_fit = score_to_fit_label(result.fit_score)

    # ------------------------------------------------------------------
    # 10. Return result
    # ------------------------------------------------------------------
    elapsed = round(time.time() - start_time, 2)
    logger.info(f"Company Fit Agent complete in {elapsed}s")
    logger.info("=" * 60)

    if result:
        logger.info(
            f"Result — Fit: {result.overall_fit} | Score: {result.fit_score} | "
            f"Confidence: {result.confidence}"
        )
        return {"company_fit": result.model_dump()}

    logger.error("All parsing attempts failed. Returning deterministic-only partial result.")
    return {"company_fit": _build_partial_result(rule_result, fit_score, missing_info)}
