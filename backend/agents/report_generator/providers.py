"""
backend.agents.report_generator.providers

Defines abstract base classes (interfaces) for data providers used by the 
AI Report Generator Agent.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

@dataclass
class ReportData:
    """Standardized representation of the generated report."""
    final_report: Optional[str] = None
    report_metadata: Dict[str, Any] = field(default_factory=dict)
    report_version: str = "1.0"
    report_generated_at: Optional[str] = None
    report_summary: Optional[str] = None
    report_sections: List[str] = field(default_factory=list)
    report_status: str = "COMPLETED"
    report_format: str = "MARKDOWN"


class BaseProvider(ABC):
    """
    Base interface for all Report providers.
    """
    
    @abstractmethod
    def get_name(self) -> str:
        """Returns the name of the provider."""
        pass


class ReportTemplateProvider(BaseProvider):
    """
    Interface for providing structural templates for report sections.
    """
    
    @abstractmethod
    def get_template(self, format_type: str = "MARKDOWN") -> str:
        """
        Returns a formatting template to be used by the Formatter.
        """
        pass


class ReportFormatterProvider(BaseProvider):
    """
    Interface for a provider that assembles disparate state variables 
    into a cohesive, readable document.
    """
    
    @abstractmethod
    def assemble_report(
        self,
        research: Dict[str, Any],
        profile: Dict[str, Any],
        industry: Dict[str, Any],
        qualification: Dict[str, Any],
        score: Dict[str, Any],
        recommendation: Dict[str, Any],
        template: str
    ) -> ReportData:
        """
        Formats all the intelligence into a final ReportData object.
        """
        pass
