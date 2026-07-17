"""
backend.agents.research

Package containing the Research Agent and its provider interfaces.
"""

from .agent import ResearchAgent
from .providers import (
    BaseProvider,
    CompanyInfo,
    CompanyInfoProvider,
    ProductServiceProvider,
    CustomerProvider,
    NewsProvider,
    SocialMediaProvider,
    TechnologyStackProvider
)

__all__ = [
    "ResearchAgent",
    "BaseProvider",
    "CompanyInfo",
    "CompanyInfoProvider",
    "ProductServiceProvider",
    "CustomerProvider",
    "NewsProvider",
    "SocialMediaProvider",
    "TechnologyStackProvider"
]
