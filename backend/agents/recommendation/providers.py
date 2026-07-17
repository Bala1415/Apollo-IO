"""
backend.agents.recommendation.providers

Defines abstract base classes (interfaces) for data providers used by the 
Recommendation Agent.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

@dataclass
class RecommendationResult:
    """Standardized representation of lead recommendation data."""
    priority: Optional[str] = None
    recommendation: Optional[str] = None
    recommendation_reason: Optional[str] = None
    next_action: Optional[str] = None
    sales_pitch: Optional[str] = None
    sales_notes: Optional[str] = None
    executive_summary: Optional[str] = None
    business_reasoning: Optional[str] = None
    recommended_followup: Optional[str] = None
    estimated_business_value: Optional[float] = None
    estimated_conversion_probability: Optional[float] = None


class BaseProvider(ABC):
    """
    Base interface for all Recommendation providers.
    """
    
    @abstractmethod
    def get_name(self) -> str:
        """Returns the name of the provider."""
        pass


class RecommendationStrategyProvider(BaseProvider):
    """
    Interface for a provider that formulates business priority, sales pitch,
    and recommended next actions based on upstream firmographics and scores.
    """
    
    @abstractmethod
    def generate_recommendation(
        self,
        profile: Dict[str, Any],
        industry: Dict[str, Any],
        qualification: Dict[str, Any],
        score: Dict[str, Any],
        interests: Dict[str, Any],
        browser_signals: List[str]
    ) -> RecommendationResult:
        """
        Formulates the comprehensive business recommendation, including
        priority assignment and executive summaries.
        """
        pass
