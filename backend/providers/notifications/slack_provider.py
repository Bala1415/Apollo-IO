from backend.config import get_settings
from backend.providers.common.http_client import ResilientHTTPClient
from backend.providers.common.logger import log_provider_execution

from backend.services.notifications.providers import SlackProvider as SlackProviderInterface, NotificationPayload

settings = get_settings()

class SlackProvider(SlackProviderInterface):
    """
    Slack Implementation for sending messages via webhook.
    """
    def __init__(self):
        self.webhook_url = settings.notifications.slack_webhook_url
        self.http_client = ResilientHTTPClient(timeout=15.0)

    def get_name(self) -> str:
        return "Slack"

    async def close(self):
        await self.http_client.close()

    @log_provider_execution("Slack")
    async def dispatch(self, payload: NotificationPayload) -> bool:
        if not self.webhook_url:
            return False

        # Format as Slack Block Kit or simple message
        data = {
            "text": f"*{payload.subject}*\n\n{payload.body}"
        }
        
        response = await self.http_client.post(self.webhook_url, json=data)
        return response.status_code == 200
