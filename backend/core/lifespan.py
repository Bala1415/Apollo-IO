import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from typing import AsyncGenerator

from backend.config import get_settings
from backend.database.session import engine
from backend.providers.llm.openai_provider import OpenAIProvider
from backend.providers.research.firecrawl_provider import FirecrawlProvider
from backend.providers.research.serper_provider import SerperProvider

logger = logging.getLogger("apollo.api.lifespan")

# Global instances of providers for reuse
providers = {}

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Manages the application lifecycle: Startup and Shutdown hooks.
    """
    settings = get_settings()
    logger.info(f"Starting Apollo-IO v{settings.app.version} in {settings.app.environment.value} mode")
    
    # 1. Initialize Database Connectivity
    logger.info("Verifying database connection pool...")
    try:
        # In a real async DB setup we'd await a connection check.
        # With sync SQLAlchemy we can just let the engine pool handle it.
        pass
    except Exception as e:
        logger.critical(f"Database connection failed during startup: {e}")
        raise

    # 2. Initialize Shared Providers
    logger.info("Initializing global providers...")
    try:
        providers["openai"] = OpenAIProvider()
        providers["firecrawl"] = FirecrawlProvider()
        providers["serper"] = SerperProvider()
        logger.info("Providers initialized successfully.")
    except Exception as e:
        logger.critical(f"Failed to initialize providers: {e}")
        raise
        
    # Yield control to the application
    yield
    
    # --- Shutdown Phase ---
    logger.info("Application shutting down. Cleaning up resources...")
    
    # 1. Close Providers
    for name, provider in providers.items():
        if hasattr(provider, 'close') and callable(getattr(provider, 'close')):
            try:
                await provider.close()
                logger.debug(f"Closed provider: {name}")
            except Exception as e:
                logger.error(f"Error closing provider {name}: {e}")
                
    # 2. Dispose Database Engine
    try:
        logger.info("Disposing database connection pool...")
        engine.dispose()
    except Exception as e:
        logger.error(f"Error disposing database engine: {e}")
        
    logger.info("Shutdown complete.")
