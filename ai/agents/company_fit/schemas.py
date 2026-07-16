"""
schemas.py — Pydantic models for the Company Fit Agent.

Defines:
  - RuleEngineResult   : intermediate deterministic scores from Layer 1
  - AlignmentDimension : per-dimension compatibility object
  - CompanyFit         : final output stored in state["company_fit"]
"""
from typing import List, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Layer 1 — Rule Engine intermediate output
# ---------------------------------------------------------------------------

class RuleEngineResult(BaseModel):
    """
    Deterministic, reproducible compatibility scores produced by the Rule Engine.
    All values are 0–100. No LLM involved.
    """
    industry_match: float = Field(
        default=0.0, ge=0, le=100,
        description="Industry overlap score (0–100)"
    )
    technology_match: float = Field(
        default=0.0, ge=0, le=100,
        description="Technology stack compatibility score (0–100)"
    )
    persona_match: float = Field(
        default=0.0, ge=0, le=100,
        description="Buyer persona alignment score (0–100)"
    )
    market_match: float = Field(
        default=0.0, ge=0, le=100,
        description="Target market overlap score (0–100)"
    )
    business_model_match: float = Field(
        default=0.0, ge=0, le=100,
        description="Business model compatibility score (0–100)"
    )
    intent_match: float = Field(
        default=0.0, ge=0, le=100,
        description="Commercial intent and research stage alignment score (0–100)"
    )


# ---------------------------------------------------------------------------
# Layer 2 — Per-dimension alignment objects
# ---------------------------------------------------------------------------

class AlignmentDimension(BaseModel):
    """Structured explanation of a single compatibility dimension."""
    value: Optional[str] = Field(
        default=None,
        description="Qualitative label: Excellent / Strong / Moderate / Weak / Poor / Unknown"
    )
    confidence: Optional[float] = Field(
        default=None, ge=0.0, le=1.0,
        description="Model confidence in this dimension assessment (0.0–1.0)"
    )
    reason: Optional[str] = Field(
        default=None,
        description="One-sentence explanation of why this alignment value was assigned"
    )


class AlignmentSummary(BaseModel):
    """Full set of alignment dimensions produced by LLM reasoning."""
    industry: Optional[AlignmentDimension] = Field(default=None)
    technology: Optional[AlignmentDimension] = Field(default=None)
    persona: Optional[AlignmentDimension] = Field(default=None)
    market: Optional[AlignmentDimension] = Field(default=None)
    business_model: Optional[AlignmentDimension] = Field(default=None)
    commercial_intent: Optional[AlignmentDimension] = Field(default=None)


# ---------------------------------------------------------------------------
# Final output — CompanyFit
# ---------------------------------------------------------------------------

class CompanyFit(BaseModel):
    """
    Final structured output of the Company Fit Agent.
    Stored in GraphState['company_fit'].

    Represents compatibility analysis ONLY.
    Does NOT contain lead score, qualification, or recommendations.
    """
    overall_fit: Optional[str] = Field(
        default=None,
        description=(
            "Qualitative fit label. "
            "One of: Excellent Fit / Strong Fit / Moderate Fit / Poor Fit / Very Poor Fit"
        ),
    )
    fit_score: Optional[float] = Field(
        default=None, ge=0, le=100,
        description=(
            "Numeric compatibility score (0–100). "
            "NOT a lead score. Represents ICP alignment only."
        ),
    )
    rule_engine: Optional[RuleEngineResult] = Field(
        default=None,
        description="Deterministic intermediate scores from Layer 1 Rule Engine"
    )
    alignment: Optional[AlignmentSummary] = Field(
        default=None,
        description="Per-dimension alignment analysis from LLM reasoning"
    )
    strengths: Optional[List[str]] = Field(
        default_factory=list,
        description="Key compatibility strengths identified"
    )
    risks: Optional[List[str]] = Field(
        default_factory=list,
        description="Compatibility risks or weak signals"
    )
    missing_information: Optional[List[str]] = Field(
        default_factory=list,
        description="Data fields absent that reduce assessment confidence"
    )
    reasoning: Optional[str] = Field(
        default=None,
        description=(
            "Executive narrative explaining WHY this company achieved its fit score. "
            "Grounded only in supplied data."
        ),
    )
    confidence: Optional[float] = Field(
        default=None, ge=0.0, le=1.0,
        description="Overall confidence in the fit assessment (0.0–1.0)"
    )
