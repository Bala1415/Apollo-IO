"""
backend.agents.lead_qualification.providers

Defines abstract base classes (interfaces) for data providers used by the 
Lead Qualification Agent.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

@dataclass
class QualificationResult:
    """Standardized representation of lead qualification data."""
    qualification: Optional[str] = None
    qualification_status: Optional[str] = None
    qualification_reason: Optional[str] = None
    qualification_confidence: Optional[float] = None
    icp_match: Optional[bool] = None
    industry_fit: Optional[str] = None
    technology_fit: Optional[str] = None
    company_size_fit: Optional[str] = None
    growth_fit: Optional[str] = None
    budget_fit: Optional[str] = None
    need_analysis: Optional[str] = None
    decision_factors: List[str] = field(default_factory=list)
    risk_flags: List[str] = field(default_factory=list)


class BaseProvider(ABC):
    """
    Base interface for all Lead Qualification providers.
    """
    
    @abstractmethod
    def get_name(self) -> str:
        """Returns the name of the provider."""
        pass


class ICPProvider(BaseProvider):
    """
    Interface for a provider that evaluates Ideal Customer Profile (ICP) match.
    """
    
    @abstractmethod
    def evaluate_icp_match(self, profile: Dict[str, Any], industry: Dict[str, Any], interests: Dict[str, Any]) -> QualificationResult:
        """
        Evaluates various fit dimensions based on the defined ICP.
        """
        pass


class QualificationRulesProvider(BaseProvider):
    """
    Interface for a provider that executes business rules to determine final 
    qualification status based on ICP match, risk flags, and browser signals.
    """
    
    @abstractmethod
    def evaluate_qualification(self, icp_result: QualificationResult, browser_signals: List[str]) -> QualificationResult:
        """
        Executes rules to yield the final qualification status and reasoning.
        """
        pass
