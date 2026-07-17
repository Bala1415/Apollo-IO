"""
backend.agents.lead_score

Package containing the Lead Score Agent and its provider interfaces.
"""

from .agent import LeadScoreAgent
from .providers import (
    BaseProvider,
    ScoreResult,
    ScoringStrategyProvider,
    WeightConfigurationProvider
)

__all__ = [
    "LeadScoreAgent",
    "BaseProvider",
    "ScoreResult",
    "ScoringStrategyProvider",
    "WeightConfigurationProvider"
]
