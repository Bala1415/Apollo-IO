import os
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self, cache_file: str = "research_cache.json"):
        self.cache_file = cache_file
        self._cache: Dict[str, Any] = {}
        self._load_cache()

    def _load_cache(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r") as f:
                    self._cache = json.load(f)
                logger.info(f"Loaded {len(self._cache)} items from cache.")
            except Exception as e:
                logger.warning(f"Failed to load cache from {self.cache_file}: {e}")
                self._cache = {}

    def _save_cache(self):
        try:
            with open(self.cache_file, "w") as f:
                json.dump(self._cache, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save cache to {self.cache_file}: {e}")

    def get_research(self, domain: str) -> Optional[Dict[str, Any]]:
        domain = domain.lower().strip()
        if domain in self._cache:
            logger.info(f"Cache hit for domain: {domain}")
            return self._cache[domain]
        return None

    def set_research(self, domain: str, data: Dict[str, Any]):
        domain = domain.lower().strip()
        self._cache[domain] = data
        self._save_cache()
        logger.info(f"Cached research for domain: {domain}")

cache_service = CacheService()
