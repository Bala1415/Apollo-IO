"""
Custom exceptions for the Apollo-IO backend.
"""

class ApolloBaseException(Exception):
    """Base exception for Apollo-IO backend."""
    pass

class ValidationError(ApolloBaseException):
    """Raised when general validation fails."""
    pass

class InvalidEmailError(ValidationError):
    """Raised when an email format is invalid."""
    pass

class NonBusinessEmailError(ValidationError):
    """Raised when an email belongs to a personal domain instead of a business."""
    pass

class InvalidDomainError(ValidationError):
    """Raised when a domain is invalid or fails DNS lookup."""
    pass
