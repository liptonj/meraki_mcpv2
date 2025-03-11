"""Error classes for Meraki MCP.

This module defines common error classes used throughout the Meraki MCP application.
"""

from typing import Any, Dict, Optional


class MCPError(Exception):
    """Base exception for all MCP-related errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Initialize a new MCPError.

        Args:
            message: Human-readable error message
            details: Additional details about the error
        """
        self.message = message
        self.details = details or {}
        super().__init__(message)


class NotFoundError(MCPError):
    """Raised when a requested resource is not found."""
    pass


class AuthorizationError(MCPError):
    """Raised when authorization fails."""
    pass


class ValidationError(MCPError):
    """Raised when input validation fails."""
    pass


class TimeoutError(MCPError):
    """Raised when an operation times out."""
    pass
