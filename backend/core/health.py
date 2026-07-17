import logging
import psutil
from sqlalchemy import text
from typing import Dict, Any

from backend.database.session import SessionLocal

logger = logging.getLogger("apollo.api.health")

class DatabaseHealthCheck:
    """Infrastructure logic to verify database connectivity."""
    
    @staticmethod
    def check() -> Dict[str, Any]:
        """Executes a simple query to ensure the DB pool is healthy."""
        try:
            db = SessionLocal()
            db.execute(text("SELECT 1"))
            db.close()
            return {"status": "ok", "component": "database"}
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {"status": "failed", "component": "database", "error": str(e)}

class SystemHealthCheck:
    """Infrastructure logic to monitor system resource thresholds."""
    
    @staticmethod
    def check() -> Dict[str, Any]:
        """Checks CPU and Memory utilization."""
        try:
            cpu_usage = psutil.cpu_percent(interval=0.1)
            memory_info = psutil.virtual_memory()
            
            # Arbitrary thresholds for degraded status
            status = "ok"
            if cpu_usage > 90.0 or memory_info.percent > 90.0:
                status = "degraded"
                
            return {
                "status": status,
                "component": "system",
                "metrics": {
                    "cpu_percent": cpu_usage,
                    "memory_percent": memory_info.percent,
                    "memory_available_mb": memory_info.available // (1024 * 1024)
                }
            }
        except Exception as e:
            logger.error(f"System health check failed: {e}")
            return {"status": "unknown", "component": "system", "error": str(e)}

class ProviderHealthCheck:
    """Infrastructure logic to verify external provider APIs."""
    
    @staticmethod
    def check() -> Dict[str, Any]:
        """
        Stub for checking provider connectivity.
        In a production system, this could ping the provider APIs.
        """
        # Since providers are external, we generally assume they are 'ok' 
        # unless they return continuous 5xx errors which would trip a circuit breaker.
        return {"status": "ok", "component": "providers"}


def run_comprehensive_health_check() -> Dict[str, Any]:
    """Aggregates all health checks for readiness and liveness probes."""
    db_health = DatabaseHealthCheck.check()
    provider_health = ProviderHealthCheck.check()
    system_health = SystemHealthCheck.check()
    
    # If any essential component is not ok, the system is degraded
    overall_status = "ok"
    if db_health["status"] != "ok" or system_health["status"] == "degraded":
        overall_status = "degraded"
    
    return {
        "status": overall_status,
        "checks": [db_health, provider_health, system_health]
    }
