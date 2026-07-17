"""
backend.services.notifications.service

Implements the Notification Service, responsible for asynchronously routing
the final intelligence report and recommendations to configured channels.
"""

import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from backend.graph.state import GraphState
from backend.services.notifications.providers import (
    NotificationProvider,
    NotificationTemplateProvider,
    RetryPolicyProvider,
    DeliveryTracker,
    NotificationPayload,
    NotificationResult
)

logger = logging.getLogger(__name__)

class NotificationService:
    """
    Consumes outputs from the AI Report Generator and dispatches them 
    to interested systems or users.
    
    This service operates outside the AI graph logic and NEVER mutates GraphState.
    """
    
    def __init__(
        self,
        providers: Optional[Dict[str, NotificationProvider]] = None,
        template_provider: Optional[NotificationTemplateProvider] = None,
        retry_policy: Optional[RetryPolicyProvider] = None,
        delivery_tracker: Optional[DeliveryTracker] = None
    ):
        # providers dict maps channel names (e.g. 'EMAIL', 'SLACK') to actual providers
        self.providers = providers or {}
        self.template_provider = template_provider
        self.retry_policy = retry_policy
        self.delivery_tracker = delivery_tracker
        self.name = "NotificationService"

    def execute(self, state: GraphState) -> NotificationResult:
        """
        Executes the notification dispatch sequence.
        Returns a structured Result dataclass, explicitly avoiding state mutation.
        """
        start_time = time.time()
        logger.info(f"[{self.name}] Service started.")
        
        result = NotificationResult()
        
        if not self.validate_input(state):
            msg = "Input validation failed. Missing required final_report."
            logger.warning(f"[{self.name}] {msg}")
            result.notification_logs.append(msg)
            result.notification_status = "SKIPPED"
            return result
            
        report, recommendation, _, _ = self._extract_inputs(state)
        recipients = self.extract_recipients(state)
        
        if not recipients:
            msg = "No notification recipients configured."
            logger.info(f"[{self.name}] {msg}")
            result.notification_logs.append(msg)
            result.notification_status = "SKIPPED"
            return result

        # For simplicity, pick the first configured recipient mapping
        # E.g. {"channel": "EMAIL", "address": "user@example.com"}
        target = recipients[0]
        channel = target.get("channel", "UNKNOWN").upper()
        address = target.get("address", "")
        
        result.delivery_channel = channel
        
        # 1. Build Payload
        payload = self.build_notification(report, recommendation, channel, address)
        if not payload:
            msg = "Failed to construct notification payload."
            logger.error(f"[{self.name}] {msg}")
            result.notification_logs.append(msg)
            return result
            
        logger.info(f"[{self.name}] Payload Prepared for channel {channel}.")
        
        # 2. Select Channel Provider
        provider = self.select_channel(channel)
        if not provider:
            msg = f"No provider configured for channel: {channel}"
            logger.error(f"[{self.name}] {msg}")
            result.notification_logs.append(msg)
            result.delivery_result = "UNSUPPORTED_CHANNEL"
            return result
            
        logger.info(f"[{self.name}] Channel Selected: {provider.get_name()}")
        
        # 3. Dispatch with Retries
        success = self._dispatch_with_retry(provider, payload, result)
        
        # 4. Finalize
        result.delivery_timestamp = datetime.now(timezone.utc).isoformat()
        if success:
            result.notification_status = "SUCCESS"
            result.delivery_result = "DELIVERED"
            logger.info(f"[{self.name}] Notification Sent Successfully.")
        else:
            result.notification_status = "FAILED"
            result.delivery_result = "FAILED_AFTER_RETRIES"
            logger.error(f"[{self.name}] Notification Failed.")
            
        self.track_delivery(result)
        
        duration = time.time() - start_time
        logger.info(f"[{self.name}] Execution completed in {duration:.2f}s.")
        
        return self.normalize_output(result)

    def validate_input(self, state: GraphState) -> bool:
        """Validates minimum inputs required to dispatch a notification."""
        return bool(state.get("final_report"))

    def _extract_inputs(self, state: GraphState) -> tuple:
        """Extracts required objects from GraphState without mutating it."""
        report = {
            "final_report": state.get("final_report"),
            "report_summary": state.get("report_summary")
        }
        recommendation = {
            "priority": state.get("priority"),
            "recommendation": state.get("recommendation"),
            "executive_summary": state.get("executive_summary")
        }
        score = state.get("lead_score")
        qual = state.get("qualification")
        
        return report, recommendation, score, qual

    def extract_report(self, state: GraphState) -> Dict[str, Any]:
        report, _, _, _ = self._extract_inputs(state)
        return report

    def extract_recipients(self, state: GraphState) -> List[Dict[str, str]]:
        """
        Retrieves recipients from configuration or state.
        For this implementation, returning a mock configuration unless passed via state.
        """
        # Example structure: [{"channel": "EMAIL", "address": "admin@apollo.io"}]
        return [{"channel": "EMAIL", "address": "sales@apollo.io"}]

    def build_notification(self, report: Dict[str, Any], recommendation: Dict[str, Any], channel: str, address: str) -> Optional[NotificationPayload]:
        """Constructs the payload using the template provider."""
        if self.template_provider:
            try:
                payload = self.template_provider.build_payload(report, recommendation, channel)
                payload.recipient = address
                return payload
            except Exception as e:
                logger.error(f"[{self.name}] TemplateProvider error: {e}")
                
        # Fallback raw text build
        return NotificationPayload(
            target_channel=channel,
            recipient=address,
            subject=f"Lead Intelligence Report - Priority: {recommendation.get('priority', 'UNKNOWN')}",
            body=report.get("report_summary") or "Automated report generated."
        )

    def select_channel(self, channel: str) -> Optional[NotificationProvider]:
        """Resolves the injected provider for the target channel."""
        return self.providers.get(channel)

    def send_email(self, provider: NotificationProvider, payload: NotificationPayload) -> bool:
        """Wraps email dispatch."""
        return provider.dispatch(payload)

    def send_webhook(self, provider: NotificationProvider, payload: NotificationPayload) -> bool:
        """Wraps webhook dispatch."""
        return provider.dispatch(payload)

    def send_slack(self, provider: NotificationProvider, payload: NotificationPayload) -> bool:
        """Wraps slack dispatch."""
        return provider.dispatch(payload)

    def _dispatch_with_retry(self, provider: NotificationProvider, payload: NotificationPayload, result: NotificationResult) -> bool:
        """Executes the dispatch with retry policy."""
        attempt = 1
        while True:
            try:
                success = provider.dispatch(payload)
                if success:
                    return True
                raise Exception("Provider returned False")
            except Exception as e:
                msg = f"Attempt {attempt} failed: {e}"
                logger.warning(f"[{self.name}] {msg}")
                result.notification_logs.append(msg)
                
                if self.retry_policy and self.retry_policy.should_retry(attempt, e):
                    delay = self.retry_policy.get_backoff_seconds(attempt)
                    logger.info(f"[{self.name}] Retrying in {delay} seconds...")
                    time.sleep(delay)
                    attempt += 1
                else:
                    logger.error(f"[{self.name}] Retries exhausted.")
                    return False

    def track_delivery(self, result: NotificationResult) -> None:
        """Saves telemetry via the tracker."""
        if self.delivery_tracker:
            try:
                self.delivery_tracker.record_delivery(result)
            except Exception as e:
                logger.error(f"[{self.name}] DeliveryTracker error: {e}")

    def generate_metadata(self, result: NotificationResult) -> Dict[str, Any]:
        if not result.notification_metadata:
            result.notification_metadata = {
                "service": self.name,
                "version": "1.0"
            }
        return result.notification_metadata

    def normalize_output(self, result: NotificationResult) -> NotificationResult:
        """Normalizes and returns the final Result object."""
        self.generate_metadata(result)
        return result
