from typing import List, Dict
from backend.config import get_settings
from backend.providers.common.http_client import ResilientHTTPClient
from backend.providers.common.logger import log_provider_execution

from backend.agents.research.providers import (
    NewsProvider, CustomerProvider, SocialMediaProvider
)

settings = get_settings()

class SerperProvider(NewsProvider, CustomerProvider, SocialMediaProvider):
    """
    Serper Implementation for Google Search extraction (News, Socials, Case Studies).
    """
    def __init__(self):
        self.api_key = settings.research.serper_api_key
        self.base_url = "https://google.serper.dev"
        self.http_client = ResilientHTTPClient(timeout=30.0)

    def get_name(self) -> str:
        return "Serper"

    async def close(self):
        await self.http_client.close()

    async def _search(self, query: str, type: str = "search") -> Dict:
        if not self.api_key:
            return {}
            
        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
        payload = {"q": query}
        response = await self.http_client.post(f"{self.base_url}/{type}", headers=headers, json=payload)
        return response.json()

    @log_provider_execution("Serper")
    async def fetch_latest_news(self, domain: str) -> List[str]:
        results = await self._search(f"site:{domain} OR \"{domain}\"", type="news")
        news_items = results.get("news", [])
        return [item.get("title", "") for item in news_items[:5] if item.get("title")]

    @log_provider_execution("Serper")
    async def fetch_customers(self, domain: str) -> List[str]:
        # Search for case studies or customer pages
        results = await self._search(f"site:{domain} \"case studies\" OR \"our customers\"")
        organic = results.get("organic", [])
        return [item.get("title", "") for item in organic[:5] if item.get("title")]

    @log_provider_execution("Serper")
    async def fetch_social_links(self, domain: str) -> Dict[str, str]:
        results = await self._search(f"\"{domain}\" linkedin OR twitter OR facebook")
        organic = results.get("organic", [])
        
        socials = {}
        for item in organic:
            link = item.get("link", "")
            if "linkedin.com/company" in link:
                socials["linkedin"] = link
            elif "twitter.com" in link or "x.com" in link:
                socials["twitter"] = link
                
        return socials
