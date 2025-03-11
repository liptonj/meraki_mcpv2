"""
Network-related MCP tools for the Meraki dashboard API.

This module contains MCP tools for interacting with Meraki networks.
"""

import logging
from typing import Any, Dict, List, Optional

from meraki_mcp.tools.base import ToolBase

logger = logging.getLogger(__name__)


class NetworkTools(ToolBase):
    """Network-related MCP tools for Meraki dashboard API."""
    
    def __init__(self, server_instance):
        """Initialize NetworkTools.

        Args:
            server_instance: The MerakiMCPServer instance that this tool class is associated with
        """
        super().__init__(server_instance)

    def get_capabilities(self):
        """Get the list of capabilities provided by this network tool class.
        
        Returns:
            List[str]: A list of capability names as strings
        """
        return [
            "list_networks",
            "get_network_health"
        ]
        
    def _register_resources(self):
        """Register network-related resources with the MCP server."""
        # Define any network-specific resources here
        @self._mcp.resource("networks://schema")
        def network_schema():
            """Schema for network data."""
            return {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string"},
                    "organizationId": {"type": "string"},
                    "type": {"type": "string"},
                    "timeZone": {"type": "string"},
                    "tags": {"type": "array", "items": {"type": "string"}},
                    "enrollmentString": {"type": "string"},
                    "url": {"type": "string"}
                }
            }
    
    def _register_tools(self):
        """Register network-related tools with the MCP server."""
        
        @self._mcp.tool()
        async def list_networks(request: Dict[str, Any]) -> Dict[str, Any]:
            """List all networks in an organization.
            
            Args:
                request: A dictionary containing:
                    - organization_id (str): Organization ID to list networks for
                    - configTemplateId (str, optional): Filter networks by configuration template
                    - tags (list, optional): Filter networks by tags
                    - tagsFilterType (str, optional): Type of tag filter ('and' or 'or')
                
            Returns:
                Dict containing networks information
                
            Raises:
                Exception: If Meraki client is not initialized or organization_id is missing
            """
            error_response = self._check_meraki_client()
            if error_response:
                return error_response
                
            # Extract request parameters
            organization_id = request.get("organization_id")
            if not organization_id:
                return {
                    "status": "error",
                    "message": "organization_id is required"
                }
            
            # Extract optional parameters
            optional_params = {}
            param_keys = ["configTemplateId", "tags", "tagsFilterType"]
            
            for key in param_keys:
                if key in request and request[key] is not None:
                    optional_params[key] = request[key]
            
            # Extract pagination parameters
            per_page = request.get("per_page", 100)  # Default to 100 items per page
            total_pages = request.get("total_pages", -1)  # Default to all pages
            
            # Add pagination parameters to optional_params
            optional_params["per_page"] = per_page
            optional_params["total_pages"] = total_pages
            
            try:
                # Use the correct namespace with the Meraki SDK
                networks = self._meraki_client.get_organization_networks(
                    organization_id, **optional_params
                )
                
                logger.info(f"Retrieved {len(networks)} networks from organization {organization_id}")
                
                return {
                    "status": "success",
                    "networks": networks
                }
                
            except Exception as e:
                logger.error(f"Error listing networks: {e}")
                return {
                    "status": "error",
                    "message": f"Error listing networks: {str(e)}"
                }

        @self._mcp.tool()
        async def get_network_health(request: Dict[str, Any]) -> Dict[str, Any]:
            """Get health information for a Meraki network.
            
            Args:
                request: A dictionary containing:
                    - network_id (str): Network ID
            
            Returns:
                Dict containing network health information
            
            Raises:
                Exception: If Meraki client is not initialized or required parameters are missing
            """
            error_response = self._check_meraki_client()
            if error_response:
                return error_response
                
            # Extract request parameters
            network_id = request.get("network_id")
            if not network_id:
                return {
                    "status": "error",
                    "message": "network_id is required"
                }
        
            try:
                # Use the correct namespace with the Meraki SDK
                network_health = self._meraki_client.get_network_health(network_id)
                
                logger.info(f"Retrieved health information for network {network_id}")
                
                # Extract components for clearer response
                components = network_health.get("components", [])
                wireless_component = next(
                    (comp for comp in components if comp.get("component") == "wireless"),
                    None
                )
                
                return {
                    "status": "success",
                    "health": network_health,
                    "wireless_status": wireless_component.get("status") if wireless_component else None,
                    "wireless_message": wireless_component.get("statusMessage") if wireless_component else None
                }
                
            except Exception as e:
                logger.error(f"Error getting network health: {e}")
                return {
                    "status": "error",
                    "message": f"Error getting network health: {str(e)}"
                }

        @self._mcp.tool()
        async def verify_meraki_connection(request: Dict[str, Any]) -> Dict[str, Any]:
            """Verify connection to Meraki API works with the configured API key.
            
            Args:
                request: A dictionary (not used in this method, but required by MCP)
                
            Returns:
                Dict containing connection status and organizations if successful
                
            Raises:
                Exception: If the API connection fails
            """
            error_response = self._check_meraki_client()
            if error_response:
                return error_response
                
            try:
                # Test the connection by listing organizations using the correct namespace
                organizations = self._meraki_client.get_organizations()
                
                logger.info(f"Successfully connected to Meraki API and retrieved {len(organizations)} organizations")
                
                # Mask API key in responses for security
                for org in organizations:
                    if "api" in org:
                        org["api"] = {"key": "************"}
                
                return {
                    "status": "success",
                    "message": "Connection to Meraki API is working correctly",
                    "organizations": organizations
                }
                
            except Exception as e:
                logger.error(f"Error verifying Meraki connection: {e}")
                return {
                    "status": "error",
                    "message": f"Failed to connect to Meraki API: {str(e)}"
                }
