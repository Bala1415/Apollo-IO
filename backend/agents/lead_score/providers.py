"""
backend.agents.lead_score.providers

Defines abstract base classes (interfaces) for data providers used by the 
Lead Score Agent.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from dataclasses import dataclass, field

@dataclass
class ScoreResult:
    """Standardized representation of lead score data."""
    intent_score: float = 0.0
    industry_score: float = 0.0
    company_size_score: float = 0.0
    technology_score: float = 0.0
    growth_score: float = 0.0
    icp_score: float = 0.0
    overall_score: float = 0.0
    confidence: float = 0.0
    reasoning: str = ""


class BaseProvider(ABC):
    """
    Base interface for all Lead Score providers.
    """
    
    @abstractmethod
    def get_name(self) -> str:
        """Returns the name of the provider."""
        pass


class WeightConfigurationProvider(BaseProvider):
    """
    Interface for providing weighting configuration to the scoring strategy.
    """
    
    @abstractmethod
    def get_weights(self) -> Dict[str, float]:
        """
        Returns a dictionary mapping sub-score names to their respective weights (0.0 to 1.0).
        Example: {'intent': 0.3, 'industry': 0.2, 'company_size': 0.15, ...}
        """
        pass


class ScoringStrategyProvider(BaseProvider):
    """
    Interface for a provider that executes a specific mathematical or ML strategy
    to determine raw scores and calculate the weighted final lead score.
    """
    
    @abstractmethod
    def calculate_scores(
        self,
        qualification: Dict[str, Any],
        profile: Dict[str, Any],
        industry: Dict[str, Any],
        interests: Dict[str, Any],
        browser_signals: list[str],
        weights: Dict[str, float]
    ) -> ScoreResult:
        """
        Computes all component scores, applies the provided weights,
        and generates the final confidence score and reasoning.
        """
        pass
