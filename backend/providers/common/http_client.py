import httpx
import logging
from typing import Any, Optional, Dict
from backoff import on_exception, expo
import asyncio

logger = logging.getLogger(__name__)

class ResilientHTTPClient:
    """
    A resilient HTTP client wrapper using httpx with automatic retries, backoff, and timeouts.
    """
    def __init__(self, timeout: float = 30.0, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries
        self.client = httpx.AsyncClient(timeout=timeout)

    async def close(self):
        await self.client.aclose()

    @on_exception(expo, (httpx.RequestError, httpx.HTTPStatusError), max_tries=3)
    async def request(
        self, method: str, url: str, **kwargs
    ) -> httpx.Response:
        """
        Executes an HTTP request with retry logic.
        """
        logger.debug(f"Executing {method} request to {url}")
        try:
            response = await self.client.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP Status Error ({e.response.status_code}) on {method} {url}: {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request Error on {method} {url}: {str(e)}")
            raise

    async def get(self, url: str, **kwargs) -> httpx.Response:
        return await self.request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs) -> httpx.Response:
        return await self.request("POST", url, **kwargs)
