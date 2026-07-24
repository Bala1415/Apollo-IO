import os
import logging
from typing import Any, Dict
from dotenv import load_dotenv

load_dotenv()
from langchain_openai import ChatOpenAI
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self, temperature: float = 0):
        self.temperature = temperature
        
        self.model = os.environ.get("LLM_MODEL", "meta-llama/llama-3.1-8b-instruct")
        logger.info(f"Initializing LLMService with OpenRouter ({self.model})")
        
        api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("LLM__OPENAI_API_KEY") or os.environ.get("OPENROUTER_API_KEY")
        base_url = os.environ.get("OPENAI_API_BASE", "https://openrouter.ai/api/v1")
        
        self._client = ChatOpenAI(
            api_key=api_key,
            base_url=base_url,
            model=self.model,
            temperature=self.temperature
        )

    @retry(
        retry=retry_if_exception_type(Exception),
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1.5, min=2, max=60),
        reraise=True,
    )
    def invoke(self, chain, inputs: Dict[str, Any]) -> Any:
        """
        Invoke an LLM chain with centralized exponential backoff.
        Handles HTTP 429, timeouts, and network failures.
        """
        logger.debug(f"Invoking LLM chain with model: {self.model}")
        try:
            return chain.invoke(inputs)
        except Exception as e:
            logger.warning(f"LLM invocation failed (will retry if possible): {e}")
            raise

llm_service = LLMService()

from langchain_core.prompts import PromptTemplate

def intelligently_resolve_domain(company_name: str) -> str:
    """
    Uses the LLM to intelligently discover the canonical domain for a company name.
    """
    logger.info(f"Intelligently resolving domain for: {company_name}")
    prompt = PromptTemplate.from_template(
        "What is the official canonical website domain for the company or organization named '{company_name}'?\n"
        "Reply with ONLY the exact domain name (e.g. apple.com, openai.com, zuntra.ai) and absolutely nothing else.\n"
        "Do not include http://, www., or any explanation."
    )
    chain = prompt | llm_service._client
    try:
        response = llm_service.invoke(chain, {"company_name": company_name})
        domain = response.content.strip().lower()
        # Basic validation to ensure it looks like a domain
        if " " not in domain and "." in domain and len(domain) < 100:
            logger.info(f"LLM resolved domain to: {domain}")
            return domain
    except Exception as e:
        logger.warning(f"Failed to intelligently resolve domain: {e}")
        
    # Fallback if LLM fails
    fallback = f"{company_name}.com"
    logger.info(f"Using fallback domain: {fallback}")
    return fallback
