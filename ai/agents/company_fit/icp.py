"""
icp.py — Ideal Customer Profile (ICP) configuration for the Lead Intelligence Platform.

The ICP is fully configurable and NOT hardcoded inside any prompt.
It is loaded once and passed as a dependency into the rule engine and LLM context.

To customise: edit the DEFAULT_ICP dict below, or load from a YAML/JSON file.
The ICP is reusable across Company Fit, Qualification, and Lead Score agents.
"""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ICP:
    """
    Ideal Customer Profile.

    Describes the characteristics of a perfect customer for this platform.
    All fields are lists of accepted values (case-insensitive matching at runtime).
    """

    # --- Company Characteristics ---
    preferred_industries: List[str] = field(default_factory=list)
    preferred_company_sizes: List[str] = field(default_factory=list)   # e.g. "1-50", "51-200", "201-1000", "1000+"
    preferred_business_models: List[str] = field(default_factory=list) # e.g. "SaaS", "Marketplace", "Consulting"
    preferred_markets: List[str] = field(default_factory=list)         # e.g. "Enterprise", "SMB", "Developer"
    preferred_customer_segments: List[str] = field(default_factory=list)

    # --- Technology ---
    preferred_technologies: List[str] = field(default_factory=list)
    disqualifying_technologies: List[str] = field(default_factory=list)

    # --- Buyer Persona ---
    preferred_personas: List[str] = field(default_factory=list)        # e.g. "CTO", "Engineering Lead", "DevOps"
    preferred_business_functions: List[str] = field(default_factory=list)

    # --- Intent ---
    preferred_commercial_intent: List[str] = field(default_factory=list)  # e.g. "high", "very_high"
    preferred_research_stages: List[str] = field(default_factory=list)    # e.g. "consideration", "decision"
    min_decision_signals: int = 0

    # --- Metadata ---
    name: str = "Default ICP"
    description: Optional[str] = None


# ---------------------------------------------------------------------------
# Default ICP — AI-Powered B2B SaaS Platform
# ---------------------------------------------------------------------------

DEFAULT_ICP = ICP(
    name="AI Developer Tools Platform ICP",
    description=(
        "Targets B2B software companies and developer teams actively adopting "
        "AI/ML tooling, LLM orchestration, or cloud infrastructure. "
        "Ideal buyers are engineering leaders evaluating AI agent frameworks."
    ),

    # Company fit
    preferred_industries=[
        "Software", "Technology", "Artificial Intelligence", "SaaS",
        "Cloud Computing", "Developer Tools", "Data & Analytics",
        "FinTech", "HealthTech", "EdTech", "Cybersecurity",
    ],
    preferred_company_sizes=["1-50", "51-200", "201-1000"],
    preferred_business_models=[
        "SaaS", "PaaS", "API", "Open Source", "Developer Platform",
        "Subscription", "Usage-based", "Freemium",
    ],
    preferred_markets=["Developer", "SMB", "Mid-Market", "Enterprise"],
    preferred_customer_segments=[
        "Developers", "Engineering Teams", "AI Teams", "ML Engineers",
        "DevOps", "Platform Teams", "Data Scientists",
    ],

    # Technology
    preferred_technologies=[
        "LangChain", "LangGraph", "OpenAI", "Anthropic", "Hugging Face",
        "Python", "FastAPI", "AWS", "GCP", "Azure",
        "Docker", "Kubernetes", "PostgreSQL", "MongoDB",
        "React", "TypeScript", "Node.js", "Go",
    ],
    disqualifying_technologies=[],

    # Persona
    preferred_personas=[
        "CTO", "VP Engineering", "Engineering Manager", "Tech Lead",
        "Software Engineer", "ML Engineer", "AI Engineer",
        "DevOps Engineer", "Platform Engineer", "Architect",
    ],
    preferred_business_functions=[
        "Engineering", "DevOps", "Product", "Data Science", "AI/ML",
    ],

    # Intent
    preferred_commercial_intent=["high", "very_high"],
    preferred_research_stages=["consideration", "decision"],
    min_decision_signals=1,
)


def load_icp(custom_icp: Optional[ICP] = None) -> ICP:
    """
    Load and return the ICP to use for this evaluation.

    Args:
        custom_icp: Optional custom ICP to override the default.
                    Useful for multi-tenant or per-campaign configurations.

    Returns:
        ICP instance to be injected into the rule engine and LLM context.
    """
    return custom_icp if custom_icp is not None else DEFAULT_ICP


def icp_to_dict(icp: ICP) -> dict:
    """Serialise the ICP to a plain dict for LLM prompt injection."""
    return {
        "name": icp.name,
        "description": icp.description,
        "preferred_industries": icp.preferred_industries,
        "preferred_company_sizes": icp.preferred_company_sizes,
        "preferred_business_models": icp.preferred_business_models,
        "preferred_markets": icp.preferred_markets,
        "preferred_customer_segments": icp.preferred_customer_segments,
        "preferred_technologies": icp.preferred_technologies,
        "preferred_personas": icp.preferred_personas,
        "preferred_business_functions": icp.preferred_business_functions,
        "preferred_commercial_intent": icp.preferred_commercial_intent,
        "preferred_research_stages": icp.preferred_research_stages,
        "min_decision_signals": icp.min_decision_signals,
    }
