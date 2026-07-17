"""
backend.agents.industry_classification.providers

Defines abstract base classes (interfaces) for data providers used by the 
Industry Classification Agent.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class IndustryData:
    """Standardized representation of industry classification data."""
    industry: Optional[str] = None
    sector: Optional[str] = None
    sub_industry: Optional[str] = None
    naics: Optional[str] = None
    sic: Optional[str] = None
    confidence: Optional[float] = None
    reasoning: Optional[str] = None


class BaseProvider(ABC):
    """
    Base interface for all Industry Classification providers.
    """
    
    @abstractmethod
    def get_name(self) -> str:
        """Returns the name of the provider."""
        pass


class IndustryClassificationProvider(BaseProvider):
    """
    Interface for a provider that directly assigns standard industry categories 
    based on profile data (e.g., using a dedicated B2B database).
    """
    
    @abstractmethod
    def classify(self, profile_data: Dict[str, Any]) -> IndustryData:
        """
        Classifies the company based on profile inputs.
        """
        pass


class NAICSLookupProvider(BaseProvider):
    """
    Interface for looking up NAICS codes based on industry keywords or descriptions.
    """
    
    @abstractmethod
    def get_naics_code(self, industry: str, sub_industry: str, description: str) -> Optional[str]:
        """Looks up the appropriate NAICS code."""
        pass


class SICLookupProvider(BaseProvider):
    """
    Interface for looking up SIC codes based on industry keywords or descriptions.
    """
    
    @abstractmethod
    def get_sic_code(self, industry: str, sub_industry: str, description: str) -> Optional[str]:
        """Looks up the appropriate SIC code."""
        pass


class LLMClassificationProvider(BaseProvider):
    """
    Interface for a Language Model provider used to infer industry taxonomies 
    and calculate confidence scores from unstructured or ambiguous data.
    """
    
    @abstractmethod
    def infer_taxonomy(self, profile_data: Dict[str, Any]) -> IndustryData:
        """
        Infers industry, sector, sub-industry, and assigns a confidence score.
        """
        pass
        
    @abstractmethod
    def generate_reasoning(self, profile_data: Dict[str, Any], taxonomy: IndustryData) -> str:
        """
        Generates a human-readable explanation of why this classification was chosen.
        """
        pass
