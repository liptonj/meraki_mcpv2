"""
Device-related MCP tools for the Meraki dashboard API.

This module contains MCP tools for interacting with Meraki network devices.
"""

import logging
from typing import Any, Dict, List, Optional

from meraki_mcp.tools.base import ToolBase

logger = logging.getLogger(__name__)


class DeviceTools(ToolBase):
    """Device-related MCP tools for Meraki dashboard API."""
    
    def __init__(self, server_instance):
        """Initialize DeviceTools.

        Args:
            server_instance: The MerakiMCPServer instance that this tool class is associated with
        """
        super().__init__(server_instance)

    def get_capabilities(self):
        """Get the list of capabilities provided by this device tool class.
        
        Returns:
            List[str]: A list of capability names as strings
        """
        return [
            "get_device_details",
            "get_device_clients",
            "get_device_status"
        ]
        
    def _register_resources(self):
        """Register device-related resources with the MCP server."""
        # Define any device-specific resources here
        @self._mcp.resource("devices://schema")
        def device_schema():
            """Schema for device data."""
            return {
                "type": "object",
                "properties": {
                    "serial": {"type": "string"},
                    "model": {"type": "string"},
                    "networkId": {"type": "string"},
                    "name": {"type": "string"},
                    "address": {"type": "string"},
                    "notes": {"type": "string"},
                    "tags": {"type": "array", "items": {"type": "string"}},
                    "lat": {"type": "number"},
                    "lng": {"type": "number"},
                    "firmware": {"type": "string"},
                    "url": {"type": "string"}
                }
            }
    
    def _register_tools(self):
        """Register device-related tools with the MCP server."""
        
        @self._mcp.tool()
        async def get_network_devices(request: Dict[str, Any]) -> Dict[str, Any]:
            """Get all devices in a Meraki network.
            
            Args:
                request: A dictionary containing:
                    - network_id (str): Network ID
            
            Returns:
                Dict containing devices in the network
            
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
        
            # Extract pagination parameters
            per_page = request.get("per_page", 100)  # Default to 100 items per page
            total_pages = request.get("total_pages", -1)  # Default to all pages

            try:
                # getNetworkDevices doesn't support pagination parameters, so we're not using them
                # Call the API without pagination parameters
                devices = self._meraki_client.networks.getNetworkDevices(network_id)
                
                logger.info(f"Retrieved {len(devices)} devices from network {network_id}")
                
                return {
                    "status": "success",
                    "device_count": len(devices),
                    "devices": devices
                }
                
            except Exception as e:
                logger.error(f"Error getting network devices: {e}")
                return {
                    "status": "error",
                    "message": f"Error getting network devices: {str(e)}"
                }

        @self._mcp.tool()
        async def get_device_status(request: Dict[str, Any]) -> Dict[str, Any]:
            """Get status information for a specific device.
            
            Args:
                request: A dictionary containing:
                    - serial (str): Device serial number
            
            Returns:
                Dict containing device status information
            
            Raises:
                Exception: If Meraki client is not initialized or required parameters are missing
            """
            error_response = self._check_meraki_client()
            if error_response:
                return error_response
                
            # Extract required parameters
            serial = request.get("serial")
            
            if not serial:
                return {
                    "status": "error",
                    "message": "serial is required"
                }
        
            try:
                # For now, we need to get the organization ID and network ID first
                # Future iterations of the API might provide direct device status endpoints
                organizations = self._meraki_client.get_organizations()
                
                for org in organizations:
                    org_id = org.get("id")
                    try:
                        device_statuses = self._meraki_client.get_organization_device_statuses(org_id)
                        device_status = next(
                            (status for status in device_statuses if status.get("serial") == serial),
                            None
                        )
                        
                        if device_status:
                            return {
                                "status": "success",
                                "device": device_status
                            }
                    except Exception:
                        # Continue to next organization if there's an error
                        continue
                
                return {
                    "status": "error",
                    "message": f"Device with serial {serial} not found in any organization"
                }
                
            except Exception as e:
                logger.error(f"Error getting device status: {e}")
                return {
                    "status": "error",
                    "message": f"Error getting device status: {str(e)}"
                }
