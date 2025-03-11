"""Common models for Meraki MCP.

This module defines common models used throughout the Meraki MCP application.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class MCPRequest(BaseModel):
    """Model for a Meraki Command Processing request."""
    
    query: str = Field(..., description="The natural language query")
    context: Optional[Dict[str, Any]] = Field(None, description="Optional context information")


class MCPResponse(BaseModel):
    """Model for a Meraki Command Processing response."""
    
    query: str = Field(..., description="The original query")
    intent: str = Field(..., description="The detected intent")
    confidence: float = Field(..., description="Confidence in the intent detection")
    result: Any = Field(..., description="The result of the operation")
    raw_data: Optional[Any] = Field(None, description="Raw data from the API")
    explanation: Optional[str] = Field(None, description="Explanation of the result")
    error: Optional[str] = Field(None, description="Error message, if any")
