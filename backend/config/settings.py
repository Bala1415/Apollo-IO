from typing import Optional, List, Any
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
import logging

from backend.config.environment import Environment, LogLevel
from backend.config.validators import validate_cors_origins, validate_database_url, validate_api_key

logger = logging.getLogger(__name__)

class AppSettings(BaseSettings):
    """
    Core application configuration.
    """
    name: str = Field("Apollo-IO", description="Application Name")
    version: str = Field("1.0.0", description="Application Version")
    environment: Environment = Field(Environment.DEVELOPMENT, description="Execution Environment")
    debug: bool = Field(False, description="Enable Debug Mode")
    host: str = Field("0.0.0.0", description="Server Host")
    port: int = Field(8000, description="Server Port")

class DatabaseSettings(BaseSettings):
    """
    Database configuration.
    """
    url: str = Field("sqlite:///./apollo.db", description="Database Connection URL")
    pool_size: int = Field(20, description="Connection Pool Size")
    connection_timeout: int = Field(30, description="Connection Timeout in seconds")
    ssl_options: Optional[str] = Field(None, description="Database SSL Options")

    @field_validator("url")
    def check_database_url(cls, v: str) -> str:
        return validate_database_url(v)

class LLMSettings(BaseSettings):
    """
    Configuration for LLM Providers.
    """
    openai_api_key: Optional[str] = Field(None, description="OpenAI API Key")
    gemini_api_key: Optional[str] = Field(None, description="Google Gemini API Key")
    anthropic_api_key: Optional[str] = Field(None, description="Anthropic API Key")

class ResearchSettings(BaseSettings):
    """
    Configuration for external research providers.
    """
    firecrawl_api_key: Optional[str] = Field(None, description="Firecrawl API Key")
    serper_api_key: Optional[str] = Field(None, description="Serper API Key")
    apollo_api_key: Optional[str] = Field(None, description="Apollo API Key")
    clearbit_api_key: Optional[str] = Field(None, description="Clearbit API Key")
    hunter_api_key: Optional[str] = Field(None, description="Hunter API Key")

class NotificationSettings(BaseSettings):
    """
    Configuration for notification dispatchers.
    """
    smtp_host: Optional[str] = Field(None, description="SMTP Server Host")
    smtp_port: Optional[int] = Field(None, description="SMTP Server Port")
    smtp_user: Optional[str] = Field(None, description="SMTP Username")
    smtp_password: Optional[str] = Field(None, description="SMTP Password")
    resend_api_key: Optional[str] = Field(None, description="Resend API Key")
    slack_webhook_url: Optional[str] = Field(None, description="Slack Webhook URL")

class SecuritySettings(BaseSettings):
    """
    Configuration for Application Security, CORS and JWT.
    """
    jwt_secret: str = Field("SUPER_SECRET_KEY_CHANGE_IN_PRODUCTION", description="Secret key for JWT generation")
    jwt_expiry_minutes: int = Field(60, description="JWT Expiration Time")
    allowed_origins: List[str] = Field(["*"], description="CORS Allowed Origins")

    @field_validator("allowed_origins", mode="before")
    def check_cors_origins(cls, v: Any) -> List[str]:
        return validate_cors_origins(v)
    
    @field_validator("jwt_secret")
    def check_jwt_secret(cls, v: str) -> str:
        return validate_api_key(v)

class LoggingSettings(BaseSettings):
    """
    Configuration for structured logging.
    """
    level: LogLevel = Field(LogLevel.INFO, description="Global Logging Level")
    format: str = Field(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
        description="Global Log Format"
    )

class Settings(BaseSettings):
    """
    Aggregated Configuration Model utilizing nested pydantic-settings.
    """
    app: AppSettings = AppSettings()
    db: DatabaseSettings = DatabaseSettings()
    llm: LLMSettings = LLMSettings()
    research: ResearchSettings = ResearchSettings()
    notifications: NotificationSettings = NotificationSettings()
    security: SecuritySettings = SecuritySettings()
    logging: LoggingSettings = LoggingSettings()

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore"
    )

@lru_cache()
def get_settings() -> Settings:
    """
    Singleton Dependency Injector for Application Settings.
    Ensures settings are instantiated only once during the application lifecycle.
    """
    try:
        settings = Settings()
        logger.info(f"Loaded Configuration for Environment: {settings.app.environment}")
        return settings
    except Exception as e:
        logger.critical(f"Failed to load application settings: {e}")
        raise
