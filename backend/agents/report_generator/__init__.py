"""
backend.agents.report_generator

Package containing the AI Report Generator Agent and its provider interfaces.
"""

from .agent import AIReportGenerator
from .providers import (
    BaseProvider,
    ReportData,
    ReportTemplateProvider,
    ReportFormatterProvider
)

__all__ = [
    "AIReportGenerator",
    "BaseProvider",
    "ReportData",
    "ReportTemplateProvider",
    "ReportFormatterProvider"
]
