"""
Reusable validation utility functions.
"""
import re
import logging
from typing import Optional
from backend.utils.constants import PERSONAL_EMAIL_DOMAINS

logger = logging.getLogger(__name__)

# Basic email regex for format validation
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

def validate_email_format(email: str) -> bool:
    """Check if the string is a valid email format."""
    if not email:
        return False
    return bool(EMAIL_REGEX.match(email.strip()))

def extract_domain(email: str) -> Optional[str]:
    """Extract domain from an email address."""
    if not email or "@" not in email:
        return None
    return email.split("@")[-1].strip()

def is_business_email(email: str) -> bool:
    """Check if the email domain is not a known personal email domain."""
    domain = extract_domain(email)
    if not domain:
        return False
    return domain.lower() not in PERSONAL_EMAIL_DOMAINS

def normalize_domain(domain: str) -> str:
    """Normalize domain by stripping http/https/www."""
    if not domain:
        return ""
    
    # Convert to lowercase
    domain = domain.lower().strip()
    
    # Remove protocol
    if domain.startswith("http://"):
        domain = domain[7:]
    elif domain.startswith("https://"):
        domain = domain[8:]
        
    # Remove www.
    if domain.startswith("www."):
        domain = domain[4:]
        
    # Remove trailing slash if present
    if domain.endswith("/"):
        domain = domain[:-1]
        
    return domain
