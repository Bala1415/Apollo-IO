import os
import logging
from typing import Any, Dict
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self, temperature: float = 0):
        self.temperature = temperature
        
        # Try OpenRouter first, then fallback to Groq
        if os.environ.get("OPENROUTER_API_KEY"):
            self.model = "meta-llama/llama-3.3-70b-instruct:free"
            logger.info("Initializing LLMService with OpenRouter (llama-3.3-70b-instruct:free)")
            self._client = ChatOpenAI(
                api_key=os.environ.get("OPENROUTER_API_KEY"),
                base_url="https://openrouter.ai/api/v1",
                model=self.model,
                temperature=self.temperature
            )
        else:
            self.model = "llama-3.3-70b-versatile"
            logger.info("Initializing LLMService with Groq (llama-3.3-70b-versatile)")
            self._client = ChatGroq(
                api_key=os.environ.get("GROQ_API_KEY"),
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
