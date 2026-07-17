"""
Schemas for Validation Service.
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List

@dataclass
class ValidationResult:
    """Structured result from the validation layer."""
    is_valid: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    errors: Optional[List[str]] = field(default_factory=list)
