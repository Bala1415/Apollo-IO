"""
backend.agents.research.providers

Defines abstract base classes (interfaces) for data providers used by the Research Agent.
This ensures the Research Agent depends on abstractions, rather than concrete implementations
of scrapers or third-party APIs.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

@dataclass
class CompanyInfo:
    """Standardized representation of core company information."""
    website: Optional[str] = None
    headquarters: Optional[str] = None
    employees: Optional[int] = None
    funding: Optional[str] = None
    description: Optional[str] = None
    founding_year: Optional[int] = None
    locations: List[str] = field(default_factory=list)


class BaseProvider(ABC):
    """
    Base interface for all research providers.
    """
    
    @abstractmethod
    def get_name(self) -> str:
        """Returns the name of the provider."""
        pass


class CompanyInfoProvider(BaseProvider):
    """
    Interface for a provider that gathers core company information
    like employees, funding, locations, and descriptions.
    """
    
    @abstractmethod
    def fetch_company_info(self, domain: str) -> CompanyInfo:
        """
        Fetches core company information.
        
        Args:
            domain (str): The company's domain.
            
        Returns:
            CompanyInfo: A standardized dataclass containing company details.
        """
        pass


class ProductServiceProvider(BaseProvider):
    """
    Interface for a provider that researches a company's products and services.
    """
    
    @abstractmethod
    def fetch_products(self, domain: str) -> List[str]:
        """Fetches a list of the company's products."""
        pass
        
    @abstractmethod
    def fetch_services(self, domain: str) -> List[str]:
        """Fetches a list of the company's services."""
        pass


class CustomerProvider(BaseProvider):
    """
    Interface for a provider that researches a company's customers.
    """
    
    @abstractmethod
    def fetch_customers(self, domain: str) -> List[str]:
        """Fetches a list of the company's known customers or case studies."""
        pass


class NewsProvider(BaseProvider):
    """
    Interface for a provider that gathers latest news about a company.
    """
    
    @abstractmethod
    def fetch_latest_news(self, domain: str) -> List[str]:
        """Fetches recent news headlines or snippets for the company."""
        pass


class SocialMediaProvider(BaseProvider):
    """
    Interface for a provider that finds social media links.
    """
    
    @abstractmethod
    def fetch_social_links(self, domain: str) -> Dict[str, str]:
        """
        Fetches social media profiles.
        
        Returns:
            Dict[str, str]: A dictionary mapping platform names (e.g., 'linkedin') to URLs.
        """
        pass


class TechnologyStackProvider(BaseProvider):
    """
    Interface for a provider that detects the technology stack used by the company.
    """
    
    @abstractmethod
    def fetch_technology_stack(self, domain: str) -> List[str]:
        """Fetches the technologies (e.g., frameworks, tools, hosting) used by the company."""
        pass
