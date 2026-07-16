import logging
import json
from typing import Dict, Any
# pyrefly: ignore [missing-import]
from langchain_groq import ChatGroq
# pyrefly: ignore [missing-import]
from langchain_core.runnables import RunnableConfig

from ai.prompts.qualification_prompt import get_qualification_prompt
from ai.output.parser import get_qualification_parser

logger = logging.getLogger(__name__)

def qualification_node(state: Dict[str, Any], config: RunnableConfig = None) -> Dict[str, Any]:
    """
    LangGraph node for the Lead Qualification Agent.
    
    Responsibilities:
    1. Extract relevant context from state.
    2. Invoke the LLM to determine qualification based on criteria.
    3. Parse and validate the output using Pydantic.
    4. Return the updated state with the 'qualification' key.
    """
    logger.info("Starting Lead Qualification Agent node")
    
    company_domain = state.get("company_domain", "")
    industry = state.get("industry", "")
    research = state.get("research", {})
    
    # company_profile or company_fit (whichever exists)
    company_profile_or_fit = state.get("company_fit", state.get("company_profile", {}))
    
    browser_interest_profile = state.get("browser_interest_profile", {})

    # Convert complex dicts to strings for the prompt
    research_str = json.dumps(research, indent=2) if isinstance(research, dict) else str(research)
    company_profile_str = json.dumps(company_profile_or_fit, indent=2) if isinstance(company_profile_or_fit, dict) else str(company_profile_or_fit)
    browser_interest_str = json.dumps(browser_interest_profile, indent=2) if isinstance(browser_interest_profile, dict) else str(browser_interest_profile)

    # Setup LLM, Parser, and Prompt
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
    parser = get_qualification_parser()
    prompt = get_qualification_prompt()
    
    # Create the Langchain pipeline (RunnableSequence)
    chain = prompt | llm | parser
    
    logger.info(f"Invoking LLM for lead qualification: {company_domain}")
    try:
        # Invoke the chain
        result = chain.invoke({
            "format_instructions": parser.get_format_instructions(),
            "company_domain": company_domain,
            "industry": industry,
            "research": research_str,
            "company_profile_or_fit": company_profile_str,
            "browser_interest_profile": browser_interest_str
        })
        
        # Update GraphState["qualification"]
        # Return only the 'qualification' key as a dict
        return {"qualification": result.model_dump()}
        
    except Exception as e:
        logger.error(f"Failed to extract qualification for {company_domain}: {e}")
        # Return an empty dict or handle the error gracefully based on graph requirements
        return {"qualification": {}}
