import logging
import json
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableConfig

from ai.tools.web_search import search_web, search_company_news, extract_website_content
from ai.prompts.research_prompt import get_research_prompt
from ai.output.parser import get_research_parser

logger = logging.getLogger(__name__)

def research_node(state: Dict[str, Any], config: RunnableConfig = None) -> Dict[str, Any]:
    """
    LangGraph node for the Research Agent.
    
    Responsibilities:
    1. Extract company_domain from state.
    2. Imperatively call research tools to gather raw context.
    3. Invoke the LLM to extract structured metadata.
    4. Parse and validate the output using Pydantic.
    5. Return the updated state with the 'research' key.
    """
    logger.info("Starting Research Agent node")
    
    company_domain = state.get("company_domain")
    if not company_domain:
        logger.warning("No company_domain provided in state.")
        return {"research": {}}

    # 1. Discover official website and extract content
    # For a simple baseline, we assume the domain is the website.
    # In a more advanced setup, you'd use the search tool to find the exact official URL.
    website_url = f"https://{company_domain}"
    website_content = extract_website_content(website_url)
    
    # 2. Collect recent company news
    news_results = search_company_news(company_domain)
    news_content = json.dumps(news_results, indent=2)

    # 3. Setup LLM, Parser, and Prompt
    # Note: Using standard ChatOpenAI. You can swap this with ChatAnthropic or others.
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    parser = get_research_parser()
    prompt = get_research_prompt()
    
    # 4. Create the Langchain pipeline (RunnableSequence)
    chain = prompt | llm | parser
    
    logger.info(f"Invoking LLM for domain: {company_domain}")
    try:
        # 5. Invoke the chain
        result = chain.invoke({
            "format_instructions": parser.get_format_instructions(),
            "company_domain": company_domain,
            "website_content": website_content,
            "news_content": news_content
        })
        
        # 6. Update GraphState["research"]
        # Convert the Pydantic model to a dict for the state
        return {"research": result.model_dump()}
        
    except Exception as e:
        logger.error(f"Failed to extract research for {company_domain}: {e}")
        # Return an empty dict or handle the error gracefully based on graph requirements
        return {"research": {}}
