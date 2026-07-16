"""
rule_engine.py — Deterministic Layer 1 scoring engine for the Company Fit Agent.

All functions in this module are:
  - Pure / deterministic — same inputs always produce the same output.
  - LLM-free — no external API calls.
  - Independently testable.

Each dimension is scored 0–100. The final RuleEngineResult is the input for
the LLM Layer 2 reasoning stage.
"""
import logging
from typing import Any, Dict, List, Optional

from .icp import ICP
from .schemas import RuleEngineResult
from .similarity import (
    bidirectional_overlap_score,
    fuzzy_match,
    keyword_overlap_score,
    normalise,
    normalise_list,
    to_100,
    weighted_average,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Intent score lookup — commercial_intent string → numeric weight
# ---------------------------------------------------------------------------

INTENT_WEIGHTS: Dict[str, float] = {
    "very_high": 1.0,
    "high":      0.75,
    "medium":    0.45,
    "low":       0.15,
}

STAGE_WEIGHTS: Dict[str, float] = {
    "decision":     1.0,
    "consideration": 0.70,
    "awareness":    0.35,
    "unknown":      0.10,
}


# ---------------------------------------------------------------------------
# 1. Industry Alignment
# ---------------------------------------------------------------------------

def score_industry(
    company_industry: Optional[str],
    company_sector: Optional[str],
    icp: ICP,
) -> float:
    """
    Score 0–100 measuring how well the company's industry matches the ICP.

    Strategy:
    - Exact match on primary industry → 100
    - Fuzzy / partial match          → 60–80
    - Sector-only match              → 50
    - No match                       → 0
    """
    candidates = [c for c in [company_industry, company_sector] if c]
    if not candidates:
        logger.debug("Industry: no data available, score=0")
        return 0.0

    best = 0.0
    for candidate in candidates:
        score = fuzzy_match(candidate, icp.preferred_industries)
        best = max(best, score)

    result = to_100(best)
    logger.debug(f"Industry score: {result} (candidates={candidates})")
    return result


# ---------------------------------------------------------------------------
# 2. Technology Alignment
# ---------------------------------------------------------------------------

def score_technology(
    research_technologies: List[str],
    behavior_technologies: List[str],
    icp: ICP,
) -> float:
    """
    Score 0–100 measuring technology stack compatibility.

    Combines:
    - Research tech vs. ICP preferred tech (weight 0.5)
    - Behavior tech vs. ICP preferred tech (weight 0.3)
    - Bidirectional research↔behavior overlap (weight 0.2)

    Disqualifying technologies instantly floor the score to 10.
    """
    # Disqualification check
    if icp.disqualifying_technologies:
        all_tech = normalise_list(research_technologies + behavior_technologies)
        disqualified = normalise_list(icp.disqualifying_technologies)
        for tech in all_tech:
            if any(tech == d or d in tech for d in disqualified):
                logger.warning(f"Disqualifying technology detected: {tech}")
                return 10.0

    research_vs_icp = keyword_overlap_score(research_technologies, icp.preferred_technologies)
    behavior_vs_icp = keyword_overlap_score(behavior_technologies, icp.preferred_technologies)
    cross_overlap   = bidirectional_overlap_score(research_technologies, behavior_technologies)

    score = weighted_average(
        scores=[to_100(research_vs_icp), to_100(behavior_vs_icp), to_100(cross_overlap)],
        weights=[0.5, 0.3, 0.2],
    )
    logger.debug(
        f"Technology score: {round(score, 1)} "
        f"(research_vs_icp={research_vs_icp:.2f}, behavior_vs_icp={behavior_vs_icp:.2f})"
    )
    return round(score, 1)


# ---------------------------------------------------------------------------
# 3. Persona Alignment
# ---------------------------------------------------------------------------

def score_persona(
    business_functions: List[str],
    primary_interest: Optional[str],
    icp: ICP,
) -> float:
    """
    Score 0–100 measuring buyer persona fit.

    Strategy:
    - Business functions vs. ICP preferred personas/functions (weight 0.7)
    - Primary interest partial match on ICP personas           (weight 0.3)
    """
    func_score = keyword_overlap_score(
        business_functions,
        icp.preferred_personas + icp.preferred_business_functions,
    )

    interest_score = 0.0
    if primary_interest:
        interest_score = fuzzy_match(
            primary_interest,
            icp.preferred_personas + icp.preferred_business_functions,
        )

    score = weighted_average(
        scores=[to_100(func_score), to_100(interest_score)],
        weights=[0.7, 0.3],
    )
    logger.debug(f"Persona score: {round(score, 1)}")
    return round(score, 1)


# ---------------------------------------------------------------------------
# 4. Market Alignment
# ---------------------------------------------------------------------------

def score_market(
    company_target_market: Optional[str],
    company_customer_segment: Optional[str],
    behavior_interests: List[str],
    icp: ICP,
) -> float:
    """
    Score 0–100 measuring market alignment.

    Combines:
    - Company target market vs. ICP preferred markets    (weight 0.4)
    - Company customer segment vs. ICP segments          (weight 0.3)
    - Behavior interests vs. ICP customer segments       (weight 0.3)
    """
    mkt_score = fuzzy_match(company_target_market, icp.preferred_markets)
    seg_score = fuzzy_match(company_customer_segment, icp.preferred_customer_segments)
    behavior_score = keyword_overlap_score(behavior_interests, icp.preferred_customer_segments)

    score = weighted_average(
        scores=[to_100(mkt_score), to_100(seg_score), to_100(behavior_score)],
        weights=[0.4, 0.3, 0.3],
    )
    logger.debug(f"Market score: {round(score, 1)}")
    return round(score, 1)


# ---------------------------------------------------------------------------
# 5. Business Model Alignment
# ---------------------------------------------------------------------------

def score_business_model(
    company_business_model: Optional[str],
    company_revenue_model: Optional[str],
    icp: ICP,
) -> float:
    """
    Score 0–100 measuring business model compatibility.

    Combines:
    - Primary business model match (weight 0.6)
    - Revenue model match          (weight 0.4)
    """
    bm_score  = fuzzy_match(company_business_model, icp.preferred_business_models)
    rev_score = fuzzy_match(company_revenue_model,  icp.preferred_business_models)

    score = weighted_average(
        scores=[to_100(bm_score), to_100(rev_score)],
        weights=[0.6, 0.4],
    )
    logger.debug(f"Business model score: {round(score, 1)}")
    return round(score, 1)


# ---------------------------------------------------------------------------
# 6. Commercial Intent Alignment
# ---------------------------------------------------------------------------

def score_intent(
    commercial_intent: Optional[str],
    research_stage: Optional[str],
    decision_signals_count: int,
    icp: ICP,
) -> float:
    """
    Score 0–100 measuring how well the buyer's intent matches ICP expectations.

    Combines:
    - Commercial intent level vs. ICP preferred intents    (weight 0.45)
    - Research stage vs. ICP preferred stages              (weight 0.35)
    - Decision signal presence (≥ min threshold)           (weight 0.20)
    """
    intent_raw = INTENT_WEIGHTS.get(normalise(commercial_intent or ""), 0.0)
    icp_intent_weights = [INTENT_WEIGHTS.get(i, 0.0) for i in icp.preferred_commercial_intent]
    intent_score = intent_raw if not icp_intent_weights else (
        1.0 if intent_raw >= min(icp_intent_weights) else intent_raw / max(icp_intent_weights, default=1)
    )

    stage_raw = STAGE_WEIGHTS.get(normalise(research_stage or ""), 0.0)
    icp_stage_weights = [STAGE_WEIGHTS.get(s, 0.0) for s in icp.preferred_research_stages]
    stage_score = stage_raw if not icp_stage_weights else (
        1.0 if stage_raw >= min(icp_stage_weights) else stage_raw / max(icp_stage_weights, default=1)
    )

    signal_score = 1.0 if decision_signals_count >= max(icp.min_decision_signals, 1) else (
        decision_signals_count / icp.min_decision_signals if icp.min_decision_signals > 0 else 0.5
    )

    score = weighted_average(
        scores=[to_100(intent_score), to_100(stage_score), to_100(signal_score)],
        weights=[0.45, 0.35, 0.20],
    )
    logger.debug(
        f"Intent score: {round(score, 1)} "
        f"(intent={commercial_intent}, stage={research_stage}, signals={decision_signals_count})"
    )
    return round(score, 1)


# ---------------------------------------------------------------------------
# Orchestrator — run all dimensions
# ---------------------------------------------------------------------------

def run_rule_engine(
    research: Dict[str, Any],
    behavior: Dict[str, Any],
    icp: ICP,
) -> RuleEngineResult:
    """
    Execute all six deterministic scoring algorithms and return RuleEngineResult.

    Args:
        research: state["research"] dict from the Research Agent.
        behavior: state["behavior"] dict from the Behavior Agent.
        icp:      Loaded ICP instance.

    Returns:
        RuleEngineResult with all dimension scores populated.
    """
    logger.info("Rule Engine: Running deterministic compatibility scoring...")

    # --- Extract research fields ---
    company   = research.get("company") or {}
    biz       = research.get("business") or {}
    tech_dict = research.get("technology") or {}

    company_industry        = biz.get("industry")
    company_sector          = biz.get("sector")
    company_target_market   = biz.get("target_market")
    company_customer_segment = biz.get("customer_segment")
    company_business_model  = biz.get("business_model")
    company_revenue_model   = biz.get("revenue_model")

    # Flatten technology lists from TechnologyStack nested dict
    research_technologies: List[str] = []
    if isinstance(tech_dict, dict):
        for tech_list in tech_dict.values():
            if isinstance(tech_list, list):
                research_technologies.extend([t for t in tech_list if t])

    # --- Extract behavior fields ---
    commercial_intent     = behavior.get("commercial_intent")
    research_stage        = behavior.get("research_stage")
    behavior_technologies = behavior.get("technology_interests") or []
    business_functions    = behavior.get("business_functions") or []
    primary_interest      = behavior.get("primary_interest")
    secondary_interests   = behavior.get("secondary_interests") or []
    decision_signals      = behavior.get("decision_signals") or []
    decision_signals_count = len(decision_signals)

    # Combine secondary interests for market scoring
    behavior_interests = [primary_interest] + secondary_interests if primary_interest else secondary_interests

    # --- Score each dimension ---
    industry_score       = score_industry(company_industry, company_sector, icp)
    technology_score     = score_technology(research_technologies, behavior_technologies, icp)
    persona_score        = score_persona(business_functions, primary_interest, icp)
    market_score         = score_market(company_target_market, company_customer_segment, behavior_interests, icp)
    business_model_score = score_business_model(company_business_model, company_revenue_model, icp)
    intent_score         = score_intent(commercial_intent, research_stage, decision_signals_count, icp)

    result = RuleEngineResult(
        industry_match=industry_score,
        technology_match=technology_score,
        persona_match=persona_score,
        market_match=market_score,
        business_model_match=business_model_score,
        intent_match=intent_score,
    )

    logger.info(
        f"Rule Engine scores — "
        f"industry={industry_score}, tech={technology_score}, persona={persona_score}, "
        f"market={market_score}, biz_model={business_model_score}, intent={intent_score}"
    )
    return result
