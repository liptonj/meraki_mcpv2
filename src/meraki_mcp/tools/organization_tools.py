"""
Organization-related MCP tools for the Meraki dashboard API.

This module contains MCP tools for interacting with Meraki organizations.
"""

import logging
from typing import Any, Dict, List, Optional

from meraki_mcp.tools.base import ToolBase

logger = logging.getLogger(__name__)


class OrganizationTools(ToolBase):
    """Organization-related MCP tools for Meraki dashboard API."""
    
    def __init__(self, server_instance):
        """Initialize OrganizationTools.

        Args:
            server_instance: The MerakiMCPServer instance that this tool class is associated with
        """
        super().__init__(server_instance)

    def get_capabilities(self):
        """Get the list of capabilities provided by this organization tool class.
        
        Returns:
            List[str]: A list of capability names as strings
        """
        return [
            "list_organizations",
            "get_organization_device_statuses",
            "get_organization_alerts"
        ]
        
    def _register_resources(self):
        """Register organization-related resources with the MCP server."""
        # Define any organization-specific resources here
        @self._mcp.resource("organizations://schema")
        def organization_schema():
            """Schema for organization data."""
            return {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string"},
                    "url": {"type": "string"},
                    "api": {
                        "type": "object",
                        "properties": {
                            "enabled": {"type": "boolean"}
                        }
                    }
                }
            }
    
    def _register_tools(self):
        """Register organization-related tools with the MCP server."""
        
        @self._mcp.tool()
        async def list_organizations(request: Dict[str, Any]) -> Dict[str, Any]:
            """List all organizations accessible with the configured API key.
            
            Args:
                request: A dictionary (not used in this method, but required by MCP)
                
            Returns:
                Dict containing organization information
                
            Raises:
                Exception: If Meraki client is not initialized
            """
            error_response = self._check_meraki_client()
            if error_response:
                return error_response
                
            try:
                organizations = self._meraki_client.get_organizations()
                
                # Mask API key in responses for security
                for org in organizations:
                    if "api" in org:
                        org["api"] = {"key": "************"}
                
                return {
                    "status": "success",
                    "organizations": organizations
                }
                
            except Exception as e:
                logger.error(f"Error listing organizations: {e}")
                return {
                    "status": "error",
                    "message": f"Error listing organizations: {str(e)}"
                }

        @self._mcp.tool()
        async def get_organization_device_statuses(request: Dict[str, Any]) -> Dict[str, Any]:
            """Get statuses for all devices in an organization.
            
            Args:
                request: A dictionary containing:
                    - organization_id (str): Organization ID
                    - per_page (int, optional): Number of entries per page
                    - startingAfter (str, optional): Token to start after for pagination
                    - endingBefore (str, optional): Token to end before for pagination
                    - networkIds (list, optional): List of network IDs to filter by
                    - productTypes (list, optional): List of product types to filter by
                    - models (list, optional): List of device models to filter by
                    - tags (list, optional): List of tags to filter by
                    - statuses (list, optional): List of statuses to filter by
            
            Returns:
                Dict containing device statuses for the organization
            
            Raises:
                Exception: If Meraki client is not initialized or required parameters are missing
            """
            error_response = self._check_meraki_client()
            if error_response:
                return error_response
                
            # Extract required parameters
            organization_id = request.get("organization_id")
            if not organization_id:
                return {
                    "status": "error",
                    "message": "organization_id is required"
                }
            
            # Extract optional parameters
            optional_params = {}
            param_keys = [
                "per_page", "startingAfter", "endingBefore", 
                "networkIds", "productTypes", "models", "tags", "statuses"
            ]
            
            for key in param_keys:
                if key in request and request[key] is not None:
                    optional_params[key] = request[key]
            
            try:
                device_statuses = self._meraki_client.get_organization_device_statuses(
                    organization_id, **optional_params
                )
                
                return {
                    "status": "success",
                    "device_count": len(device_statuses),
                    "devices": device_statuses
                }
                
            except Exception as e:
                logger.error(f"Error getting organization device statuses: {e}")
                return {
                    "status": "error",
                    "message": f"Error getting organization device statuses: {str(e)}"
                }

        @self._mcp.tool()
        async def get_organization_alerts(request: Dict[str, Any]) -> Dict[str, Any]:
            """Get alerts for a Meraki organization.
            
            Args:
                request: A dictionary containing:
                    - organization_id (str): Organization ID
            
            Returns:
                Dict containing organization alerts
            
            Raises:
                Exception: If Meraki client is not initialized or required parameters are missing
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
            
            try:
                alerts = self._meraki_client.get_organization_alerts(organization_id)
                
                return {
                    "status": "success",
                    "alert_count": len(alerts),
                    "alerts": alerts
                }
                
            except Exception as e:
                logger.error(f"Error getting organization alerts: {e}")
                return {
                    "status": "error",
                    "message": f"Error getting organization alerts: {str(e)}"
                }
