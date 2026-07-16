# pyrefly: ignore [missing-import]
from langchain_core.output_parsers import PydanticOutputParser
from ai.agents.research_agent.schemas import CompanyResearch
from ai.agents.qualification_agent.schemas import LeadQualification
from ai.agents.lead_score_agent.schemas import LeadScore
from ai.agents.recommendation_agent.schemas import Recommendation

def get_research_parser() -> PydanticOutputParser:
    """
    Returns a configured PydanticOutputParser for the CompanyResearch schema.
    This parser is used to instruct the LLM on the expected JSON format 
    and to parse the resulting JSON string into a Python object.
    """
    return PydanticOutputParser(pydantic_object=CompanyResearch)

def get_qualification_parser() -> PydanticOutputParser:
    """
    Returns a configured PydanticOutputParser for the LeadQualification schema.
    """
    return PydanticOutputParser(pydantic_object=LeadQualification)

def get_lead_score_parser() -> PydanticOutputParser:
    """
    Returns a configured PydanticOutputParser for the LeadScore schema.
    """
    return PydanticOutputParser(pydantic_object=LeadScore)

def get_recommendation_parser() -> PydanticOutputParser:
    """
    Returns a configured PydanticOutputParser for the Recommendation schema.
    """
    return PydanticOutputParser(pydantic_object=Recommendation)
