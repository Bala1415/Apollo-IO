import os
import logging
from typing import Any, Dict
from langchain_openai import ChatOpenAI
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self, temperature: float = 0):
        self.temperature = temperature
        
        self.model = os.environ.get("LLM_MODEL", "nvidia/nemotron-4-340b-instruct")
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
