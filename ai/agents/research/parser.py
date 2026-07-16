from langchain_core.output_parsers import PydanticOutputParser
from .schemas import CompanyResearch

def get_research_parser() -> PydanticOutputParser:
    """
    Returns the PydanticOutputParser configured with the CompanyResearch schema.
    This parser is responsible for validating that the LLM output conforms to our expectations.
    """
    return PydanticOutputParser(pydantic_object=CompanyResearch)
