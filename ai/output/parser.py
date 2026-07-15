from langchain_core.output_parsers import PydanticOutputParser
from ai.agents.research_agent.schemas import CompanyResearch

def get_research_parser() -> PydanticOutputParser:
    """
    Returns a configured PydanticOutputParser for the CompanyResearch schema.
    This parser is used to instruct the LLM on the expected JSON format 
    and to parse the resulting JSON string into a Python object.
    """
    return PydanticOutputParser(pydantic_object=CompanyResearch)
