"""
parser.py — Shared output parsers for the Lead Intelligence Pipeline.

Updated to import from the correct agent module paths.
"""
from langchain_core.output_parsers import PydanticOutputParser

from ai.agents.research.schemas import CompanyResearch
from ai.agents.qualification_agent.schemas import LeadQualification
from ai.agents.lead_score_agent.schemas import LeadScore
from ai.agents.recommendation_agent.schemas import Recommendation


def get_research_parser() -> PydanticOutputParser:
    return PydanticOutputParser(pydantic_object=CompanyResearch)

def get_qualification_parser() -> PydanticOutputParser:
    return PydanticOutputParser(pydantic_object=LeadQualification)

def get_lead_score_parser() -> PydanticOutputParser:
    return PydanticOutputParser(pydantic_object=LeadScore)

def get_recommendation_parser() -> PydanticOutputParser:
    return PydanticOutputParser(pydantic_object=Recommendation)
