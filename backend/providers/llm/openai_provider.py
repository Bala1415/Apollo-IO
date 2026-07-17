import json
from typing import Dict, Any, List
from openai import AsyncOpenAI
from backend.config import get_settings
from backend.providers.common.logger import log_provider_execution

from backend.agents.company_profile.providers import LLMProvider as CompanyProfileLLM
from backend.agents.industry_classification.providers import LLMClassificationProvider, IndustryData

settings = get_settings()

class OpenAIProvider(CompanyProfileLLM, LLMClassificationProvider):
    """
    OpenAI Implementation for all LLM interfaces across the Apollo-IO backend.
    """
    def __init__(self, model: str = "gpt-4-turbo"):
        self.model = model
        self.client = AsyncOpenAI(api_key=settings.llm.openai_api_key)

    def get_name(self) -> str:
        return "OpenAI"

    async def _call_llm(self, prompt: str, system: str = "You are an AI assistant.", json_mode: bool = False) -> str:
        """Internal helper to call the OpenAI API."""
        kwargs = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ]
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        response = await self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content

    # --- Company Profile Interfaces ---
    
    @log_provider_execution("OpenAI")
    async def extract_organization_type(self, description: str) -> str:
        prompt = f"Extract the organization type (Public, Private, Non-profit) from this text:\n\n{description}"
        response = await self._call_llm(prompt)
        return response.strip()

    @log_provider_execution("OpenAI")
    async def estimate_company_metrics(self, data: Dict[str, Any]) -> Dict[str, str]:
        prompt = f"Estimate the revenue_estimate, growth_stage, and company_size for this company based on data:\n{json.dumps(data)}\nReturn ONLY a JSON object."
        response = await self._call_llm(prompt, json_mode=True)
        try:
            return json.loads(response)
        except:
            return {"revenue_estimate": "Unknown", "growth_stage": "Unknown", "company_size": "Unknown"}

    # --- Industry Classification Interfaces ---

    @log_provider_execution("OpenAI")
    async def infer_taxonomy(self, profile_data: Dict[str, Any]) -> IndustryData:
        prompt = f"Infer the industry, sector, sub_industry, naics, sic, and confidence (0.0 to 1.0) from this data:\n{json.dumps(profile_data)}\nReturn ONLY a JSON object with these keys."
        response = await self._call_llm(prompt, json_mode=True)
        try:
            parsed = json.loads(response)
            return IndustryData(**parsed)
        except:
            return IndustryData(industry="Unknown", confidence=0.0)

    @log_provider_execution("OpenAI")
    async def generate_reasoning(self, profile_data: Dict[str, Any], taxonomy: IndustryData) -> str:
        prompt = f"Explain why this company was classified as {taxonomy.industry} based on:\n{json.dumps(profile_data)}"
        response = await self._call_llm(prompt)
        return response.strip()
