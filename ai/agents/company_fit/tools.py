"""
tools.py — Feature extraction and context preparation utilities for the Company Fit Agent.

Responsibilities:
  - Safely extract and normalise fields from research/behavior dicts
  - Compute the overall fit_score from RuleEngineResult
  - Build the structured LLM context string
  - Detect missing information fields
"""
import json
import logging
from typing import Any, Dict, List, Optional

from .icp import ICP, icp_to_dict
from .schemas import RuleEngineResult
from .similarity import weighted_average, score_to_fit_label

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Dimension weights for overall fit_score calculation
# ---------------------------------------------------------------------------

FIT_SCORE_WEIGHTS = {
    "intent_match":        0.30,  # Highest — signals active buying intent
    "technology_match":    0.25,  # Strong differentiator for tech platform
    "industry_match":      0.20,  # Core ICP qualifier
    "persona_match":       0.12,  # Buyer role fit
    "market_match":        0.08,  # Confirms right segment
    "business_model_match": 0.05, # Sanity check
}


# ---------------------------------------------------------------------------
# 1. Compute overall fit_score from rule engine results
# ---------------------------------------------------------------------------

def compute_fit_score(rule_result: RuleEngineResult) -> float:
    """
    Compute overall fit_score (0–100) as a weighted average of all dimension scores.
    Weights reflect business importance, not equal averaging.
    """
    scores  = [
        rule_result.intent_match,
        rule_result.technology_match,
        rule_result.industry_match,
        rule_result.persona_match,
        rule_result.market_match,
        rule_result.business_model_match,
    ]
    weights = list(FIT_SCORE_WEIGHTS.values())
    score = weighted_average(scores, weights)
    logger.debug(f"Computed overall fit_score: {round(score, 1)}")
    return round(score, 1)


# ---------------------------------------------------------------------------
# 2. Detect missing information fields
# ---------------------------------------------------------------------------

def detect_missing_fields(research: Dict[str, Any], behavior: Dict[str, Any]) -> List[str]:
    """
    Identify fields absent from research or behavior that reduce assessment confidence.
    Returns a plain-English list of missing field descriptions.
    """
    missing: List[str] = []

    company = research.get("company") or {}
    biz     = research.get("business") or {}

    if not company.get("employee_count"):
        missing.append("Company employee count")
    if not company.get("funding"):
        missing.append("Funding information")
    if not company.get("founded_year"):
        missing.append("Company founding year")
    if not biz.get("revenue_model"):
        missing.append("Revenue model")
    if not biz.get("pricing_model"):
        missing.append("Pricing model")
    if not biz.get("sales_strategy"):
        missing.append("Sales strategy / GTM motion")
    if not research.get("customers") or not (research.get("customers") or {}).get("target_customers"):
        missing.append("Target customer details")
    if not research.get("competitors"):
        missing.append("Competitor information")
    if not behavior.get("industries"):
        missing.append("User's industry context")
    if not behavior.get("technology_interests"):
        missing.append("User's technology interests")

    logger.debug(f"Missing fields detected: {missing}")
    return missing


# ---------------------------------------------------------------------------
# 3. Build structured LLM context
# ---------------------------------------------------------------------------

def build_fit_context(
    research: Dict[str, Any],
    behavior: Dict[str, Any],
    rule_result: RuleEngineResult,
    icp: ICP,
    fit_score: float,
) -> str:
    """
    Merge research summary, behavior summary, rule engine scores, and ICP
    into a structured text block for the LLM reasoning prompt.
    """
    sections: List[str] = []

    # --- ICP ---
    icp_dict = icp_to_dict(icp)
    sections.append(
        "=== IDEAL CUSTOMER PROFILE (ICP) ===\n"
        + json.dumps(icp_dict, indent=2)
    )

    # --- Company summary ---
    company = research.get("company") or {}
    biz     = research.get("business") or {}
    comp_lines = [
        f"  Name:            {company.get('name', 'Unknown')}",
        f"  Website:         {company.get('website', 'Unknown')}",
        f"  Description:     {company.get('description', 'N/A')}",
        f"  Industry:        {biz.get('industry', 'N/A')}",
        f"  Sector:          {biz.get('sector', 'N/A')}",
        f"  Business Model:  {biz.get('business_model', 'N/A')}",
        f"  Revenue Model:   {biz.get('revenue_model', 'N/A')}",
        f"  Target Market:   {biz.get('target_market', 'N/A')}",
        f"  Employees:       {company.get('employee_count', 'Unknown')}",
        f"  Headquarters:    {company.get('headquarters', 'Unknown')}",
        f"  Funding:         {company.get('funding', 'Unknown')}",
    ]
    sections.append("=== COMPANY PROFILE ===\n" + "\n".join(comp_lines))

    # Technologies
    tech = research.get("technology") or {}
    all_tech = []
    if isinstance(tech, dict):
        for v in tech.values():
            if isinstance(v, list):
                all_tech.extend(v)
    if all_tech:
        sections.append(f"=== COMPANY TECHNOLOGIES ===\n  {', '.join(all_tech)}")

    # Executive summary from research
    exec_summary = research.get("executive_summary")
    if exec_summary:
        sections.append(f"=== RESEARCH EXECUTIVE SUMMARY ===\n  {exec_summary}")

    # --- Behavior summary ---
    beh_lines = [
        f"  Primary Interest:   {behavior.get('primary_interest', 'N/A')}",
        f"  Secondary:          {', '.join(behavior.get('secondary_interests') or [])}",
        f"  Technology:         {', '.join(behavior.get('technology_interests') or [])}",
        f"  Business Functions: {', '.join(behavior.get('business_functions') or [])}",
        f"  Commercial Intent:  {behavior.get('commercial_intent', 'N/A')}",
        f"  Research Stage:     {behavior.get('research_stage', 'N/A')}",
        f"  Confidence:         {behavior.get('confidence', 'N/A')}",
    ]
    sections.append("=== BUYER BEHAVIOR PROFILE ===\n" + "\n".join(beh_lines))

    signals = behavior.get("decision_signals") or []
    if signals:
        sig_lines = [
            f"  [{s.get('signal_type', '').upper()}] on {s.get('domain', '')} (weight: {s.get('weight', '')})"
            for s in signals
        ]
        sections.append("=== DECISION SIGNALS ===\n" + "\n".join(sig_lines))

    beh_summary = behavior.get("behavior_summary")
    if beh_summary:
        sections.append(f"=== BEHAVIOR SUMMARY ===\n  {beh_summary}")

    # --- Rule Engine Results ---
    re_lines = [
        f"  Industry Match:       {rule_result.industry_match}/100",
        f"  Technology Match:     {rule_result.technology_match}/100",
        f"  Persona Match:        {rule_result.persona_match}/100",
        f"  Market Match:         {rule_result.market_match}/100",
        f"  Business Model Match: {rule_result.business_model_match}/100",
        f"  Intent Match:         {rule_result.intent_match}/100",
        f"  --- Overall Fit Score: {fit_score}/100 ({score_to_fit_label(fit_score)}) ---",
    ]
    sections.append("=== RULE ENGINE SCORES (Deterministic) ===\n" + "\n".join(re_lines))

    return "\n\n".join(sections)
