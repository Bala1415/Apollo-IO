"""
backend.services.notifications

Package containing the Notification Service and its provider interfaces.
"""

from .service import NotificationService
from .providers import (
    BaseProvider,
    NotificationPayload,
    NotificationResult,
    NotificationProvider,
    EmailProvider,
    WebhookProvider,
    SlackProvider,
    NotificationTemplateProvider,
    RetryPolicyProvider,
    DeliveryTracker
)

__all__ = [
    "NotificationService",
    "BaseProvider",
    "NotificationPayload",
    "NotificationResult",
    "NotificationProvider",
    "EmailProvider",
    "WebhookProvider",
    "SlackProvider",
    "NotificationTemplateProvider",
    "RetryPolicyProvider",
    "DeliveryTracker"
]
