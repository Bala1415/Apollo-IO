"""
backend.services.notifications.providers

Defines abstract base classes (interfaces) and dataclasses used by the 
Notification Service for multi-channel message delivery.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone

@dataclass
class NotificationPayload:
    """Standardized representation of a notification payload."""
    target_channel: str
    recipient: str
    subject: str
    body: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NotificationResult:
    """Standardized representation of the delivery result."""
    notification_status: str = "FAILED"
    notification_metadata: Dict[str, Any] = field(default_factory=dict)
    delivery_timestamp: Optional[str] = None
    delivery_channel: Optional[str] = None
    delivery_result: Optional[str] = None
    notification_logs: List[str] = field(default_factory=list)


class BaseProvider(ABC):
    """Base interface for all Notification providers."""
    
    @abstractmethod
    def get_name(self) -> str:
        """Returns the name of the provider."""
        pass


class NotificationProvider(BaseProvider):
    """
    Base interface for all notification channel dispatchers.
    """
    
    @abstractmethod
    def dispatch(self, payload: NotificationPayload) -> bool:
        """
        Dispatches the payload to the intended channel.
        Returns True if successful, False otherwise.
        """
        pass


class EmailProvider(NotificationProvider):
    """Marker interface for Email providers."""
    pass


class WebhookProvider(NotificationProvider):
    """Marker interface for Webhook providers."""
    pass


class SlackProvider(NotificationProvider):
    """Marker interface for Slack providers."""
    pass


class NotificationTemplateProvider(BaseProvider):
    """
    Interface for formatting reports into channel-specific layouts.
    """
    
    @abstractmethod
    def build_payload(self, report_data: Dict[str, Any], recommendation: Dict[str, Any], channel: str) -> NotificationPayload:
        """Constructs the final payload bound for a specific channel."""
        pass


class RetryPolicyProvider(BaseProvider):
    """
    Interface governing retry attempts and backoffs.
    """
    
    @abstractmethod
    def should_retry(self, attempt_count: int, error: Exception) -> bool:
        """Determines if the delivery should be retried."""
        pass

    @abstractmethod
    def get_backoff_seconds(self, attempt_count: int) -> int:
        """Returns the number of seconds to wait before the next retry."""
        pass


class DeliveryTracker(BaseProvider):
    """
    Interface for tracking metrics or saving logs externally.
    """
    
    @abstractmethod
    def record_delivery(self, result: NotificationResult) -> None:
        """Records the delivery result."""
        pass
