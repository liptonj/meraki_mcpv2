"""Base module for all Meraki MCP tool classes.

This module provides a base class for tool classes to inherit from,
ensuring consistent initialization and tool registration patterns.
"""

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

class ToolBase:
    """Base class for all Meraki MCP tool classes.
    
    This class provides common functionality for all tool classes,
    including initialization with a Meraki client and MCP server instance,
    and a template method for registering tools.
    
    Attributes:
        _meraki_client: The Meraki API client instance
        _mcp: The MCP server instance from parent MerakiMCPServer
    """
    
    def __init__(self, server_instance):
        """Initialize the tool class.
        
        Args:
            server_instance: The MerakiMCPServer instance that this tool class is associated with
        """
        # Extract required components from the server instance
        self._server = server_instance
        self._meraki_client = server_instance._meraki_client
        self._mcp = server_instance.mcp
        # Register resources and tools for this class
        self._register_resources()
        self._register_tools()
    
    def _register_resources(self):
        """Register all resources specific to this class.
        
        This is a template method that should be overridden by subclasses
        to register their specific resource schemas with the MCP server.
        """
        pass
        
    def _register_tools(self):
        """Register all tools specific to this class.
        
        This is a template method that should be overridden by subclasses
        to register their specific tools with the MCP server.
        """
        pass
        
    def get_capabilities(self):
        """Get the list of capabilities provided by this tool class.
        
        Returns:
            List[str]: A list of capability names as strings
        """
        # Default implementation returns an empty list
        # Should be overridden by subclasses
        return []
    
    def _check_meraki_client(self) -> Optional[Dict[str, Any]]:
        """Check if the Meraki client is initialized.
        
        Returns:
            None if the client is initialized, or an error response dict if not
        """
        if not self._meraki_client:
            return {
                "status": "error",
                "message": "Meraki client not initialized. Check your MERAKI_API_KEY."
            }
        return None
