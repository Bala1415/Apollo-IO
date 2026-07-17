import json
from typing import Dict, Any, List
from anthropic import AsyncAnthropic
from backend.config import get_settings
from backend.providers.common.logger import log_provider_execution

from backend.agents.company_profile.providers import LLMProvider as CompanyProfileLLM
from backend.agents.industry_classification.providers import LLMClassificationProvider, IndustryData

settings = get_settings()

class AnthropicProvider(CompanyProfileLLM, LLMClassificationProvider):
    """
    Anthropic Implementation for all LLM interfaces across the Apollo-IO backend.
    """
    def __init__(self, model: str = "claude-3-5-sonnet-20240620"):
        self.model = model
        self.client = AsyncAnthropic(api_key=settings.llm.anthropic_api_key)

    def get_name(self) -> str:
        return "Anthropic"

    async def _call_llm(self, prompt: str, system: str = "You are an AI assistant.", json_mode: bool = False) -> str:
        """Internal helper to call the Anthropic API."""
        if json_mode:
            prompt += "\n\nRespond ONLY with a valid JSON object."
            
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=system,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.content[0].text

    # --- Company Profile Interfaces ---
    
    @log_provider_execution("Anthropic")
    async def extract_organization_type(self, description: str) -> str:
        prompt = f"Extract the organization type (Public, Private, Non-profit) from this text:\n\n{description}"
        response = await self._call_llm(prompt)
        return response.strip()

    @log_provider_execution("Anthropic")
    async def estimate_company_metrics(self, data: Dict[str, Any]) -> Dict[str, str]:
        prompt = f"Estimate the revenue_estimate, growth_stage, and company_size for this company based on data:\n{json.dumps(data)}\nReturn ONLY a JSON object."
        response = await self._call_llm(prompt, json_mode=True)
        try:
            return json.loads(response)
        except:
            return {"revenue_estimate": "Unknown", "growth_stage": "Unknown", "company_size": "Unknown"}

    # --- Industry Classification Interfaces ---

    @log_provider_execution("Anthropic")
    async def infer_taxonomy(self, profile_data: Dict[str, Any]) -> IndustryData:
        prompt = f"Infer the industry, sector, sub_industry, naics, sic, and confidence (0.0 to 1.0) from this data:\n{json.dumps(profile_data)}\nReturn ONLY a JSON object with these keys."
        response = await self._call_llm(prompt, json_mode=True)
        try:
            parsed = json.loads(response)
            return IndustryData(**parsed)
        except:
            return IndustryData(industry="Unknown", confidence=0.0)

    @log_provider_execution("Anthropic")
    async def generate_reasoning(self, profile_data: Dict[str, Any], taxonomy: IndustryData) -> str:
        prompt = f"Explain why this company was classified as {taxonomy.industry} based on:\n{json.dumps(profile_data)}"
        response = await self._call_llm(prompt)
        return response.strip()
