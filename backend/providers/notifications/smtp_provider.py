import smtplib
from email.message import EmailMessage
from backend.config import get_settings
from backend.providers.common.logger import log_provider_execution
import asyncio

from backend.services.notifications.providers import EmailProvider, NotificationPayload

settings = get_settings()

class SMTPProvider(EmailProvider):
    """
    SMTP Implementation for sending email notifications.
    """
    def __init__(self):
        self.host = settings.notifications.smtp_host
        self.port = settings.notifications.smtp_port or 587
        self.user = settings.notifications.smtp_user
        self.password = settings.notifications.smtp_password

    def get_name(self) -> str:
        return "SMTP"

    @log_provider_execution("SMTP")
    async def dispatch(self, payload: NotificationPayload) -> bool:
        if not all([self.host, self.port, self.user, self.password]):
            return False
            
        def _send():
            msg = EmailMessage()
            msg.set_content(payload.body)
            msg['Subject'] = payload.subject
            msg['From'] = self.user
            msg['To'] = payload.recipient
            
            with smtplib.SMTP(self.host, self.port) as server:
                server.starttls()
                server.login(self.user, self.password)
                server.send_message(msg)
                
        # Run blocking SMTP library call in an executor
        await asyncio.to_thread(_send)
        return True
