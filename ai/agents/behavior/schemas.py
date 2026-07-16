"""
schemas.py — Pydantic models for the Intent Analysis Agent (Behavior).

Defines the final BehaviorAnalysis output stored in state["behavior"].
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class DecisionSignal(BaseModel):
    """A high-intent behavioral signal detected from browsing activity."""
    signal_type: Optional[str] = Field(
        default=None,
        description=(
            "Type of decision signal. Examples: pricing_page, demo_request, "
            "contact_sales, comparison_page, documentation, product_page, "
            "free_trial, case_study, checkout"
        ),
    )
    domain: Optional[str] = Field(
        default=None, description="Domain where the signal was detected"
    )
    weight: Optional[float] = Field(
        default=None,
        description="Relative importance weight of this signal (0.0 – 1.0)",
    )


class BehaviorAnalysis(BaseModel):
    """
    Structured behavioral intelligence produced by the Intent Analysis Agent.
    Stored in GraphState['behavior'].
    """

    primary_interest: Optional[str] = Field(
        default=None,
        description=(
            "The single most dominant topic of interest inferred from browsing behavior. "
            "Examples: AI Developer Tools, Cloud Infrastructure, CRM Software."
        ),
    )
    secondary_interests: Optional[List[str]] = Field(
        default_factory=list,
        description=(
            "Supporting topics of interest, ordered by relevance. "
            "Examples: ['MLOps', 'API Management', 'Team Collaboration']."
        ),
    )
    technology_interests: Optional[List[str]] = Field(
        default_factory=list,
        description=(
            "Specific technologies or platforms the user is interested in. "
            "Examples: ['LangChain', 'OpenAI', 'AWS', 'PostgreSQL']."
        ),
    )
    business_functions: Optional[List[str]] = Field(
        default_factory=list,
        description=(
            "Business functions or departments the interests relate to. "
            "Examples: ['Engineering', 'DevOps', 'Sales', 'Marketing', 'Finance']."
        ),
    )
    industries: Optional[List[str]] = Field(
        default_factory=list,
        description=(
            "Industries inferred from browsing patterns. "
            "Examples: ['Software', 'Healthcare', 'Finance', 'Education']."
        ),
    )
    commercial_intent: Optional[str] = Field(
        default=None,
        description=(
            "Overall commercial intent level. "
            "Must be one of: low, medium, high, very_high."
        ),
    )
    research_stage: Optional[str] = Field(
        default=None,
        description=(
            "Stage in the buyer journey. "
            "Must be one of: awareness, consideration, decision, unknown."
        ),
    )
    decision_signals: Optional[List[DecisionSignal]] = Field(
        default_factory=list,
        description="Specific high-intent behavioral signals detected.",
    )
    behavior_summary: Optional[str] = Field(
        default=None,
        description=(
            "A concise 3-5 sentence narrative summarizing the user's behavior, "
            "inferred intent, and likely business context. "
            "No scoring, qualification, or recommendations."
        ),
    )
    confidence: Optional[float] = Field(
        default=None,
        description=(
            "Model confidence in the analysis (0.0 – 1.0) based on "
            "signal richness and consistency."
        ),
    )
