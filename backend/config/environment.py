from enum import Enum

class Environment(str, Enum):
    """
    Defines the valid environments for the application.
    """
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"

    @property
    def is_production(self) -> bool:
        return self == Environment.PRODUCTION

    @property
    def is_development(self) -> bool:
        return self == Environment.DEVELOPMENT

    @property
    def is_testing(self) -> bool:
        return self == Environment.TESTING

class LogLevel(str, Enum):
    """
    Defines the valid logging levels.
    """
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
