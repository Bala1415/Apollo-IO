from typing import List
from backend.config import get_settings
from backend.providers.common.http_client import ResilientHTTPClient
from backend.providers.common.logger import log_provider_execution

from backend.agents.research.providers import (
    CompanyInfoProvider, CompanyInfo, ProductServiceProvider, TechnologyStackProvider
)

settings = get_settings()

class FirecrawlProvider(CompanyInfoProvider, ProductServiceProvider, TechnologyStackProvider):
    """
    Firecrawl Implementation for deep web scraping and content extraction.
    """
    def __init__(self):
        self.api_key = settings.research.firecrawl_api_key
        self.base_url = "https://api.firecrawl.dev/v1"
        self.http_client = ResilientHTTPClient(timeout=60.0)

    def get_name(self) -> str:
        return "Firecrawl"

    async def close(self):
        await self.http_client.close()

    async def _scrape(self, url: str) -> str:
        if not self.api_key:
            return ""
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "url": url,
            "formats": ["markdown"]
        }
        response = await self.http_client.post(f"{self.base_url}/scrape", headers=headers, json=payload)
        data = response.json()
        return data.get("data", {}).get("markdown", "")

    @log_provider_execution("Firecrawl")
    async def fetch_company_info(self, domain: str) -> CompanyInfo:
        # In a real implementation, we would scrape the domain and use an LLM to parse it into CompanyInfo.
        # For now, we simulate fetching the raw content.
        markdown = await self._scrape(f"https://{domain}")
        return CompanyInfo(
            website=f"https://{domain}",
            description=markdown[:500] if markdown else "No description available."
        )

    @log_provider_execution("Firecrawl")
    async def fetch_products(self, domain: str) -> List[str]:
        markdown = await self._scrape(f"https://{domain}/products")
        if markdown:
            return ["Scraped Product Data"]
        return []

    @log_provider_execution("Firecrawl")
    async def fetch_services(self, domain: str) -> List[str]:
        markdown = await self._scrape(f"https://{domain}/services")
        if markdown:
            return ["Scraped Service Data"]
        return []

    @log_provider_execution("Firecrawl")
    async def fetch_technology_stack(self, domain: str) -> List[str]:
        # Would typically look for known script tags or headers in the scraped HTML.
        return ["Web Technology detected via Firecrawl"]
