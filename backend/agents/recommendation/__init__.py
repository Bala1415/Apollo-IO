"""
backend.agents.recommendation

Package containing the Recommendation Agent and its provider interfaces.
"""

from .agent import RecommendationAgent
from .providers import (
    BaseProvider,
    RecommendationResult,
    RecommendationStrategyProvider
)

__all__ = [
    "RecommendationAgent",
    "BaseProvider",
    "RecommendationResult",
    "RecommendationStrategyProvider"
]
