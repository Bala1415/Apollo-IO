import logging
import json
from typing import Dict, Any
# pyrefly: ignore [missing-import]
from langchain_groq import ChatGroq
# pyrefly: ignore [missing-import]
from langchain_core.runnables import RunnableConfig

from ai.prompts.recommendation_prompt import get_recommendation_prompt
from ai.output.parser import get_recommendation_parser

logger = logging.getLogger(__name__)

def recommendation_node(state: Dict[str, Any], config: RunnableConfig = None) -> Dict[str, Any]:
    """
    LangGraph node for the Recommendation Agent.
    
    Responsibilities:
    1. Extract relevant context from state.
    2. Invoke the LLM to generate the final business recommendation based on the combined intelligence.
    3. Parse and validate the output using Pydantic.
    4. Return the updated state with the 'recommendation' key.
    """
    logger.info("Starting Recommendation Agent node")
    
    company_domain = state.get("company_domain", "")
    industry = state.get("industry", "")
    lead_score = state.get("lead_score", {})
    qualification_result = state.get("qualification", {})
    research_result = state.get("research", {})
    
    # company_profile or company_fit (whichever exists)
    company_profile_or_fit = state.get("company_fit", state.get("company_profile", {}))
    
    interest_profile = state.get("browser_interest_profile", {})
    
    if not lead_score:
        logger.warning("Lead Score Missing")

    # Convert complex dicts to strings for the prompt
    lead_score_str = json.dumps(lead_score, indent=2) if isinstance(lead_score, dict) else str(lead_score)
    qualification_str = json.dumps(qualification_result, indent=2) if isinstance(qualification_result, dict) else str(qualification_result)
    research_str = json.dumps(research_result, indent=2) if isinstance(research_result, dict) else str(research_result)
    company_profile_str = json.dumps(company_profile_or_fit, indent=2) if isinstance(company_profile_or_fit, dict) else str(company_profile_or_fit)
    interest_str = json.dumps(interest_profile, indent=2) if isinstance(interest_profile, dict) else str(interest_profile)

    # Setup LLM, Parser, and Prompt
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
    parser = get_recommendation_parser()
    prompt = get_recommendation_prompt()
    
    # Create the Langchain pipeline (RunnableSequence)
    chain = prompt | llm | parser
    
    logger.info(f"Invoking LLM for recommendation: {company_domain}")
    try:
        # Invoke the chain
        result = chain.invoke({
            "format_instructions": parser.get_format_instructions(),
            "company_domain": company_domain,
            "industry": industry,
            "lead_score": lead_score_str,
            "qualification_result": qualification_str,
            "research_result": research_str,
            "company_profile_or_fit": company_profile_str,
            "interest_profile": interest_str
        })
        
        logger.info("Recommendation Generated Successfully")
        
        # Update GraphState["recommendation"]
        # Return only the 'recommendation' key as a dict
        return {"recommendation": result.model_dump()}
        
    except Exception as e:
        logger.error(f"Recommendation Generation Failed for {company_domain}: {e}")
        # Return an empty dict or handle the error gracefully based on graph requirements
        return {"recommendation": {}}
