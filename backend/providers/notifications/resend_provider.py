from backend.config import get_settings
from backend.providers.common.http_client import ResilientHTTPClient
from backend.providers.common.logger import log_provider_execution

from backend.services.notifications.providers import EmailProvider, NotificationPayload

settings = get_settings()

class ResendProvider(EmailProvider):
    """
    Resend Implementation for sending email notifications.
    """
    def __init__(self):
        self.api_key = settings.notifications.resend_api_key
        self.base_url = "https://api.resend.com/emails"
        self.http_client = ResilientHTTPClient(timeout=20.0)

    def get_name(self) -> str:
        return "Resend"

    async def close(self):
        await self.http_client.close()

    @log_provider_execution("Resend")
    async def dispatch(self, payload: NotificationPayload) -> bool:
        if not self.api_key:
            return False

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "from": "Apollo-IO <notifications@resend.dev>",
            "to": [payload.recipient],
            "subject": payload.subject,
            "text": payload.body
        }
        
        response = await self.http_client.post(self.base_url, headers=headers, json=data)
        return response.status_code == 200
