"""
backend.graph.constants

Constants and Enums for the LangGraph workflows.
"""
from enum import Enum

class ProcessingStage(str, Enum):
    """Represents the current stage of the GraphState processing."""
    INITIALIZED = "initialized"
    VALIDATION = "validation"
    COMPANY_INTELLIGENCE = "company_intelligence"
    LEAD_SCORING = "lead_scoring"
    QUALIFICATION = "qualification"
    RECOMMENDATION = "recommendation"
    REPORT_GENERATION = "report_generation"
    COMPLETED = "completed"
    FAILED = "failed"

class AgentName(str, Enum):
    """Represents the known AI Agents in the system."""
    SUPERVISOR = "supervisor_agent"
    RESEARCH_AGENT = "research_agent"
    SCORING_AGENT = "scoring_agent"
    RECOMMENDATION_AGENT = "recommendation_agent"
    REPORT_AGENT = "report_agent"
    QUALIFICATION_AGENT = "qualification_agent"

class LeadPriority(str, Enum):
    """Represents the priority classification of a lead."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class QualificationStatus(str, Enum):
    """Represents the qualification status of a lead."""
    UNQUALIFIED = "unqualified"
    QUALIFIED = "qualified"
    DISQUALIFIED = "disqualified"
    NEEDS_REVIEW = "needs_review"
