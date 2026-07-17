"""
backend.agents.company_profile.providers

Defines abstract base classes (interfaces) for data providers used by the Company Profile Agent.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

@dataclass
class TechnologyStack:
    """Standardized representation of a technology stack."""
    cloud_platforms: List[str] = field(default_factory=list)
    frontend_stack: List[str] = field(default_factory=list)
    backend_stack: List[str] = field(default_factory=list)
    databases: List[str] = field(default_factory=list)
    ai_ml: List[str] = field(default_factory=list)
    devops: List[str] = field(default_factory=list)
    security: List[str] = field(default_factory=list)
    
    def get_all(self) -> List[str]:
        """Returns a flat list of all detected technologies."""
        all_tech = (self.cloud_platforms + self.frontend_stack + self.backend_stack + 
                   self.databases + self.ai_ml + self.devops + self.security)
        return list(set(all_tech))


class BaseProvider(ABC):
    """
    Base interface for all Company Profile providers.
    """
    
    @abstractmethod
    def get_name(self) -> str:
        """Returns the name of the provider."""
        pass


class TechnologyDetectionProvider(BaseProvider):
    """
    Interface for a provider that detects technology stacks from a domain.
    """
    
    @abstractmethod
    def detect_technology(self, domain: str) -> TechnologyStack:
        """
        Detects technology stack used by the company.
        """
        pass


class WebsiteAnalysisProvider(BaseProvider):
    """
    Interface for a provider that analyzes website content for business metrics.
    """
    
    @abstractmethod
    def analyze_business_model(self, description: str, products: List[str], services: List[str]) -> str:
        """Analyzes inputs to determine the business model (e.g., B2B SaaS, E-commerce)."""
        pass
        
    @abstractmethod
    def analyze_target_market(self, description: str) -> str:
        """Analyzes description to determine target market segment."""
        pass


class LLMProvider(BaseProvider):
    """
    Interface for a Language Model provider used for unstructured data extraction.
    """
    
    @abstractmethod
    def extract_organization_type(self, description: str) -> str:
        """Extracts organization type (e.g., Public, Private, Non-profit)."""
        pass
        
    @abstractmethod
    def estimate_company_metrics(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Estimates metrics based on raw research.
        Returns a dict containing 'revenue_estimate', 'growth_stage', 'company_size'.
        """
        pass
