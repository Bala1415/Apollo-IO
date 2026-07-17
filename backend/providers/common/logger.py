import logging
import uuid
import time
import asyncio
from typing import Any, Callable, Dict
from functools import wraps

logger = logging.getLogger("apollo.providers")

def log_provider_execution(provider_name: str):
    """
    Decorator to log provider execution with trace ID, duration, and standardized structured logs.
    """
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            trace_id = str(uuid.uuid4())
            start_time = time.time()
            logger.info(f"[{trace_id}] Provider Started: {provider_name} | Method: {func.__name__}")
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(f"[{trace_id}] Provider Success: {provider_name} | Duration: {duration:.2f}s")
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"[{trace_id}] Provider Failed: {provider_name} | Error: {str(e)} | Duration: {duration:.2f}s")
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            trace_id = str(uuid.uuid4())
            start_time = time.time()
            logger.info(f"[{trace_id}] Provider Started: {provider_name} | Method: {func.__name__}")
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(f"[{trace_id}] Provider Success: {provider_name} | Duration: {duration:.2f}s")
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"[{trace_id}] Provider Failed: {provider_name} | Error: {str(e)} | Duration: {duration:.2f}s")
                raise
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    return decorator
