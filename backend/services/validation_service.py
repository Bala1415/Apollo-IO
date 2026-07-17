"""
Validation Service Layer
Sits immediately after the Lead API and before Company Intelligence.
"""
import logging
import socket
from datetime import datetime, timezone
from typing import Dict, Any

from backend.utils.validators import (
    validate_email_format,
    is_business_email as check_business_email,
    extract_domain as util_extract_domain,
    normalize_domain as util_normalize_domain
)
from backend.exceptions import (
    ValidationError,
    InvalidEmailError,
    NonBusinessEmailError,
    InvalidDomainError
)
from backend.schemas.validation import ValidationResult

logger = logging.getLogger(__name__)

class ValidationService:
    """
    Validation Service for incoming Browser Packages.
    Ensures that incoming data meets business rules before proceeding to Company Intelligence.
    """
    
    @staticmethod
    def validate_email(email: str) -> str:
        """Validate email format."""
        if not email:
            raise InvalidEmailError("Email cannot be empty.")
        if not validate_email_format(email):
            raise InvalidEmailError(f"Invalid email format: {email}")
        return email.strip()

    @staticmethod
    def is_business_email(email: str) -> bool:
        """Validate if email belongs to a business domain."""
        if not check_business_email(email):
            raise NonBusinessEmailError(f"Personal email domains are rejected: {email}")
        return True

    @staticmethod
    def extract_domain(email: str) -> str:
        """Extract domain from email."""
        domain = util_extract_domain(email)
        if not domain:
            raise InvalidEmailError(f"Cannot extract domain from email: {email}")
        return domain

    @staticmethod
    def validate_domain(domain: str) -> bool:
        """Validate domain format."""
        if not domain or "." not in domain:
            raise InvalidDomainError(f"Invalid domain format: {domain}")
        return True

    @staticmethod
    def dns_lookup(domain: str) -> bool:
        """Perform a basic DNS lookup to see if the domain exists."""
        try:
            # We'll just check if it resolves to an IP
            socket.gethostbyname(domain)
            return True
        except socket.gaierror:
            logger.warning(f"DNS lookup failed for domain: {domain}")
            raise InvalidDomainError(f"Domain does not exist or DNS failed: {domain}")

    @staticmethod
    def normalize_domain(domain: str) -> str:
        """Normalize domain string by stripping http/https/www."""
        return util_normalize_domain(domain)

    @staticmethod
    def validate_timestamp(timestamp: Any) -> bool:
        """Validate timestamp format."""
        if not timestamp:
            raise ValidationError("Timestamp is required.")
        
        try:
            if isinstance(timestamp, (int, float)):
                # Assume unix timestamp
                datetime.fromtimestamp(timestamp, tz=timezone.utc)
            elif isinstance(timestamp, str):
                # Attempt to parse ISO string
                datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            else:
                raise ValueError
        except ValueError:
            raise ValidationError(f"Invalid timestamp format: {timestamp}")
            
        return True

    @staticmethod
    def validate_required_fields(payload: Dict[str, Any]) -> bool:
        """Ensure the browser payload has necessary fields."""
        required = ["email", "timestamp"]
        missing = [field for field in required if field not in payload]
        
        if missing:
            raise ValidationError(f"Missing required fields: {', '.join(missing)}")
        return True

    @staticmethod
    def validate_interest_profile(profile: Any) -> bool:
        """Validate interest profile structure."""
        if not isinstance(profile, dict):
            raise ValidationError("Interest profile must be a dictionary.")
        return True

    @staticmethod
    def sanitize_input(data: Any) -> Any:
        """Recursively sanitize string inputs to prevent injection or invalid spacing."""
        if isinstance(data, dict):
            return {k: ValidationService.sanitize_input(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [ValidationService.sanitize_input(i) for i in data]
        elif isinstance(data, str):
            return data.strip()
        return data

    @classmethod
    def validate_browser_package(cls, payload: Dict[str, Any]) -> ValidationResult:
        """
        Main entrypoint for the Validation Layer.
        Orchestrates all validations and returns a structured result.
        """
        try:
            logger.info("Starting validation for browser package.")
            
            # Sanitize the incoming payload first
            clean_payload = cls.sanitize_input(payload)
            
            # Validate required fields
            cls.validate_required_fields(clean_payload)
            
            # Validate timestamp
            cls.validate_timestamp(clean_payload.get("timestamp"))
            
            email = clean_payload.get("email")
            
            # Validate email format
            cls.validate_email(email)
            
            # Check if it's a business email
            cls.is_business_email(email)
            
            # Extract and normalize domain
            raw_domain = cls.extract_domain(email)
            clean_domain = cls.normalize_domain(raw_domain)
            
            # Validate domain structure
            cls.validate_domain(clean_domain)
            
            # DNS verification
            cls.dns_lookup(clean_domain)
            
            # Optional: Validate interest profile if present
            if "interest_profile" in clean_payload:
                cls.validate_interest_profile(clean_payload["interest_profile"])
                
            clean_payload["domain"] = clean_domain
            
            logger.info(f"Browser package validated successfully for {email}")
            return ValidationResult(
                is_valid=True,
                message="Validation successful.",
                data=clean_payload
            )
            
        except ValidationError as e:
            logger.error(f"Validation failed: {str(e)}")
            return ValidationResult(
                is_valid=False,
                message=str(e),
                errors=[str(e)]
            )
        except Exception as e:
            logger.exception("Unexpected error during validation.")
            return ValidationResult(
                is_valid=False,
                message="Internal validation error.",
                errors=[str(e)]
            )
