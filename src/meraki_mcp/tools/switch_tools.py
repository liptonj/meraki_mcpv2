"""
Switch-related MCP tools for the Meraki dashboard API.

This module contains MCP tools for interacting with Meraki switches,
including VLAN configuration, port settings, and switch troubleshooting.
"""

import logging
from typing import Any, Dict, List, Optional

from meraki_mcp.tools.base import ToolBase

logger = logging.getLogger(__name__)


class SwitchTools(ToolBase):
    """Switch-related MCP tools for Meraki dashboard API."""
    
    def __init__(self, server_instance):
        """Initialize SwitchTools.

        Args:
            server_instance: The MerakiMCPServer instance that this tool class is associated with
        """
        super().__init__(server_instance)

    def get_capabilities(self):
        """Get the list of capabilities provided by this switch tool class.
        
        Returns:
            List[str]: A list of capability names as strings
        """
        return [
            "get_switch_ports",
            "get_switch_port_details",
            "update_switch_port",
            "get_switch_port_statuses",
            "get_switch_vlans",
            "get_switch_routing",
            "get_switch_dhcp",
            "get_switch_stp",
            "troubleshoot_switch_port"
        ]
        
    def _register_resources(self):
        """Register switch-related resources with the MCP server."""
        # Define any switch-specific resources here
        @self._mcp.resource("switches://port-schema")
        def switch_port_schema():
            """Schema for switch port data."""
            return {
                "type": "object",
                "properties": {
                    "portId": {"type": "string"},
                    "name": {"type": "string"},
                    "tags": {"type": "array", "items": {"type": "string"}},
                    "enabled": {"type": "boolean"},
                    "type": {"type": "string", "enum": ["access", "trunk"]},
                    "vlan": {"type": "integer"},
                    "voiceVlan": {"type": "integer"},
                    "allowedVlans": {"type": "string"},
                    "poeEnabled": {"type": "boolean"},
                    "isolationEnabled": {"type": "boolean"},
                    "rstpEnabled": {"type": "boolean"},
                    "stpGuard": {"type": "string", "enum": ["disabled", "root guard", "bpdu guard", "loop guard"]},
                    "linkNegotiation": {"type": "string"},
                    "portScheduleId": {"type": "string"},
                    "udld": {"type": "string", "enum": ["Alert only", "Enforce"]},
                    "accessPolicyType": {"type": "string", "enum": ["Open", "Custom access policy", "MAC allow list", "Sticky MAC allow list"]},
                    "accessPolicyNumber": {"type": "integer"},
                    "macAllowList": {"type": "array", "items": {"type": "string"}},
                    "stickyMacAllowList": {"type": "array", "items": {"type": "string"}},
                    "stickyMacAllowListLimit": {"type": "integer"},
                    "stormControlEnabled": {"type": "boolean"}
                }
            }
            
        @self._mcp.resource("switches://vlan-schema")
        def switch_vlan_schema():
            """Schema for VLAN data."""
            return {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"},
                    "subnet": {"type": "string"},
                    "applianceIp": {"type": "string"},
                    "groupPolicyId": {"type": "string"},
                    "templateVlanType": {"type": "string", "enum": ["same", "unique", "update"]},
                    "cidr": {"type": "string"},
                    "mask": {"type": "integer"},
                    "dhcpHandling": {"type": "string", "enum": ["Do not respond to DHCP requests", "Relay DHCP to another server", "Respond to DHCP requests on this VLAN"]},
                    "dhcpRelayServerIps": {"type": "array", "items": {"type": "string"}},
                    "dhcpLeaseTime": {"type": "string", "enum": ["30 minutes", "1 hour", "4.5 hours", "1 day", "1 week"]},
                    "dhcpBootOptionsEnabled": {"type": "boolean"},
                    "dhcpBootNextServer": {"type": "string"},
                    "dhcpBootFilename": {"type": "string"},
                    "fixedIpAssignments": {"type": "object"},
                    "reservedIpRanges": {"type": "array", "items": {"type": "object", "properties": {
                        "start": {"type": "string"},
                        "end": {"type": "string"},
                        "comment": {"type": "string"}
                    }}},
                    "dnsNameservers": {"type": "string", "enum": ["upstream_dns", "google_dns", "opendns", "custom"]},
                    "dnsCustomNameservers": {"type": "array", "items": {"type": "string"}}
                }
            }
    
    def _register_tools(self):
        """Register switch-related tools with the MCP server."""
        
        @self._mcp.tool()
        async def get_switch_ports(request: Dict[str, Any]) -> Dict[str, Any]:
            """Get a list of all ports for a switch.
            
            Args:
                request: A dictionary containing:
                    - serial (str): Serial number of the switch
                    
            Returns:
                Dict containing a list of all ports on the switch
                
            Raises:
                Exception: If Meraki client is not initialized or serial is missing
            """
            error_response = self._check_meraki_client()
            if error_response:
                return error_response
                
            # Extract request parameters
            serial = request.get("serial")
            if not serial:
                return {
                    "status": "error",
                    "message": "serial is required"
                }
            
            try:
                ports = self._meraki_client.get_device_switch_ports(serial)
                return {
                    "status": "success",
                    "ports": ports
                }
            except Exception as e:
                logger.error(f"Error getting switch ports: {e}")
                return {
                    "status": "error",
                    "message": f"Error getting switch ports: {str(e)}"
                }
                
        @self._mcp.tool()
        async def get_switch_port_details(request: Dict[str, Any]) -> Dict[str, Any]:
            """Get details for a specific port on a switch.
            
            Args:
                request: A dictionary containing:
                    - serial (str): Serial number of the switch
                    - port_id (str): Port number or identifier
                    
            Returns:
                Dict containing port details
                
            Raises:
                Exception: If Meraki client is not initialized or required parameters are missing
            """
            error_response = self._check_meraki_client()
            if error_response:
                return error_response
                
            # Extract request parameters
            serial = request.get("serial")
            port_id = request.get("port_id")
            
            if not serial:
                return {
                    "status": "error",
                    "message": "serial is required"
                }
                
            if not port_id:
                return {
                    "status": "error",
                    "message": "port_id is required"
                }
            
            try:
                port_details = self._meraki_client.get_device_switch_port(serial, port_id)
                return {
                    "status": "success",
                    "port": port_details
                }
            except Exception as e:
                logger.error(f"Error getting switch port details: {e}")
                return {
                    "status": "error",
                    "message": f"Error getting switch port details: {str(e)}"
                }
                
        @self._mcp.tool()
        async def update_switch_port(request: Dict[str, Any]) -> Dict[str, Any]:
            """Update configuration for a specific port on a switch.
            
            Args:
                request: A dictionary containing:
                    - serial (str): Serial number of the switch
                    - port_id (str): Port number or identifier
                    - name (str, optional): Name of the port
                    - enabled (bool, optional): Whether the port is enabled
                    - type (str, optional): Port type (access or trunk)
                    - vlan (int, optional): VLAN number for access ports
                    - voiceVlan (int, optional): Voice VLAN number
                    - allowedVlans (str, optional): VLANs allowed on trunk ports
                    - poeEnabled (bool, optional): Enable/disable PoE
                    
            Returns:
                Dict containing updated port details
                
            Raises:
                Exception: If Meraki client is not initialized or required parameters are missing
            """
            error_response = self._check_meraki_client()
            if error_response:
                return error_response
                
            # Extract required parameters
            serial = request.get("serial")
            port_id = request.get("port_id")
            
            if not serial:
                return {
                    "status": "error",
                    "message": "serial is required"
                }
                
            if not port_id:
                return {
                    "status": "error",
                    "message": "port_id is required"
                }
            
            # Extract optional parameters for updating the port
            update_params = {}
            optional_params = [
                "name", "enabled", "type", "vlan", "voiceVlan", "allowedVlans", 
                "poeEnabled", "isolationEnabled", "rstpEnabled", "stpGuard", 
                "linkNegotiation", "udld", "accessPolicyType"
            ]
            
            for param in optional_params:
                if param in request:
                    update_params[param] = request[param]
            
            # At least one parameter to update is required
            if not update_params:
                return {
                    "status": "error",
                    "message": "At least one port parameter to update is required"
                }
                
            try:
                updated_port = self._meraki_client.update_device_switch_port(
                    serial, port_id, **update_params
                )
                return {
                    "status": "success",
                    "port": updated_port
                }
            except Exception as e:
                logger.error(f"Error updating switch port: {e}")
                return {
                    "status": "error",
                    "message": f"Error updating switch port: {str(e)}"
                }
                
        @self._mcp.tool()
        async def get_switch_port_statuses(request: Dict[str, Any]) -> Dict[str, Any]:
            """Get status information for all ports on a switch.
            
            Args:
                request: A dictionary containing:
                    - serial (str): Serial number of the switch
                    
            Returns:
                Dict containing status of all ports
                
            Raises:
                Exception: If Meraki client is not initialized or serial is missing
            """
            error_response = self._check_meraki_client()
            if error_response:
                return error_response
                
            # Extract request parameters
            serial = request.get("serial")
            if not serial:
                return {
                    "status": "error",
                    "message": "serial is required"
                }
            
            try:
                port_statuses = self._meraki_client.get_device_switch_ports_statuses(serial)
                return {
                    "status": "success",
                    "portStatuses": port_statuses
                }
            except Exception as e:
                logger.error(f"Error getting switch port statuses: {e}")
                return {
                    "status": "error",
                    "message": f"Error getting switch port statuses: {str(e)}"
                }
                
        @self._mcp.tool()
        async def get_switch_vlans(request: Dict[str, Any]) -> Dict[str, Any]:
            """Get a list of all VLANs for a switch.
            
            Args:
                request: A dictionary containing:
                    - serial (str): Serial number of the switch
                    
            Returns:
                Dict containing a list of all VLANs on the switch
                
            Raises:
                Exception: If Meraki client is not initialized or serial is missing
            """
            error_response = self._check_meraki_client()
            if error_response:
                return error_response
                
            # Extract request parameters
            serial = request.get("serial")
            if not serial:
                return {
                    "status": "error",
                    "message": "serial is required"
                }
            
            try:
                vlans = self._meraki_client.get_device_switch_routing_interfaces(serial)
                return {
                    "status": "success",
                    "vlans": vlans
                }
            except Exception as e:
                logger.error(f"Error getting switch VLANs: {e}")
                return {
                    "status": "error",
                    "message": f"Error getting switch VLANs: {str(e)}"
                }
                
        @self._mcp.tool()
        async def get_switch_routing(request: Dict[str, Any]) -> Dict[str, Any]:
            """Get layer 3 routing configuration for a switch.
            
            Args:
                request: A dictionary containing:
                    - serial (str): Serial number of the switch
                    
            Returns:
                Dict containing routing configuration
                
            Raises:
                Exception: If Meraki client is not initialized or serial is missing
            """
            error_response = self._check_meraki_client()
            if error_response:
                return error_response
                
            # Extract request parameters
            serial = request.get("serial")
            if not serial:
                return {
                    "status": "error",
                    "message": "serial is required"
                }
            
            try:
                routing_interfaces = self._meraki_client.get_device_switch_routing_interfaces(serial)
                static_routes = self._meraki_client.get_device_switch_routing_static_routes(serial)
                
                return {
                    "status": "success",
                    "routing": {
                        "interfaces": routing_interfaces,
                        "staticRoutes": static_routes
                    }
                }
            except Exception as e:
                logger.error(f"Error getting switch routing: {e}")
                return {
                    "status": "error",
                    "message": f"Error getting switch routing: {str(e)}"
                }
                
        @self._mcp.tool()
        async def get_switch_dhcp(request: Dict[str, Any]) -> Dict[str, Any]:
            """Get DHCP server configuration for a switch.
            
            Args:
                request: A dictionary containing:
                    - serial (str): Serial number of the switch
                    
            Returns:
                Dict containing DHCP configuration
                
            Raises:
                Exception: If Meraki client is not initialized or serial is missing
            """
            error_response = self._check_meraki_client()
            if error_response:
                return error_response
                
            # Extract request parameters
            serial = request.get("serial")
            if not serial:
                return {
                    "status": "error",
                    "message": "serial is required"
                }
            
            try:
                dhcp_config = self._meraki_client.get_device_switch_dhcp_server_policy(serial)
                return {
                    "status": "success",
                    "dhcpConfig": dhcp_config
                }
            except Exception as e:
                logger.error(f"Error getting switch DHCP configuration: {e}")
                return {
                    "status": "error",
                    "message": f"Error getting switch DHCP configuration: {str(e)}"
                }
                
        @self._mcp.tool()
        async def get_switch_stp(request: Dict[str, Any]) -> Dict[str, Any]:
            """Get Spanning Tree Protocol (STP) configuration for a switch.
            
            Args:
                request: A dictionary containing:
                    - serial (str): Serial number of the switch
                    
            Returns:
                Dict containing STP configuration
                
            Raises:
                Exception: If Meraki client is not initialized or serial is missing
            """
            error_response = self._check_meraki_client()
            if error_response:
                return error_response
                
            # Extract request parameters
            serial = request.get("serial")
            if not serial:
                return {
                    "status": "error",
                    "message": "serial is required"
                }
            
            try:
                stp_config = self._meraki_client.get_device_switch_stp(serial)
                return {
                    "status": "success",
                    "stpConfig": stp_config
                }
            except Exception as e:
                logger.error(f"Error getting switch STP configuration: {e}")
                return {
                    "status": "error",
                    "message": f"Error getting switch STP configuration: {str(e)}"
                }
                
        @self._mcp.tool()
        async def troubleshoot_switch_port(request: Dict[str, Any]) -> Dict[str, Any]:
            """Troubleshoot issues with a switch port.
            
            Args:
                request: A dictionary containing:
                    - serial (str): Serial number of the switch
                    - port_id (str): Port number or identifier
                    - client_mac (str, optional): MAC address of client to troubleshoot
                    
            Returns:
                Dict containing troubleshooting results
                
            Raises:
                Exception: If Meraki client is not initialized or required parameters are missing
            """
            error_response = self._check_meraki_client()
            if error_response:
                return error_response
                
            # Extract request parameters
            serial = request.get("serial")
            port_id = request.get("port_id")
            client_mac = request.get("client_mac")
            
            if not serial:
                return {
                    "status": "error",
                    "message": "serial is required"
                }
                
            if not port_id:
                return {
                    "status": "error",
                    "message": "port_id is required"
                }
            
            try:
                # Get port status
                port_status = None
                port_statuses = self._meraki_client.get_device_switch_ports_statuses(serial)
                for status in port_statuses:
                    if str(status.get("portId")) == str(port_id):
                        port_status = status
                        break
                
                # Get port configuration
                port_config = self._meraki_client.get_device_switch_port(serial, port_id)
                
                # Get related client information if MAC provided
                client_info = None
                if client_mac:
                    # Get network ID for the device
                    device_details = self._meraki_client.get_device(serial)
                    network_id = device_details.get("networkId")
                    
                    # Get client information
                    try:
                        clients = self._meraki_client.get_network_clients(
                            network_id, mac=client_mac
                        )
                        if clients and len(clients) > 0:
                            client_info = clients[0]
                    except Exception as client_err:
                        logger.warning(f"Error fetching client details: {client_err}")
                
                # Perform troubleshooting analysis
                issues = []
                recommendations = []
                
                # Check if port is enabled but status is down
                if port_config.get("enabled", True) and port_status and port_status.get("status") != "Connected":
                    issues.append("Port is enabled but not connected")
                    recommendations.append("Check physical cable connection")
                    recommendations.append("Verify that connected device is powered on")
                    recommendations.append("Try a different cable or port to isolate the issue")
                
                # Check if PoE is enabled but not delivering power
                if port_config.get("poeEnabled", False) and port_status and port_status.get("status") == "Connected" and port_status.get("isUplink") is False:
                    if port_status.get("powerUsageInWh", 0) == 0:
                        issues.append("PoE is enabled but not delivering power")
                        recommendations.append("Verify connected device supports PoE")
                        recommendations.append("Check if switch has enough power budget available")
                        recommendations.append("Confirm connected device is within PoE class limits")
                
                # Check VLAN mismatches
                if client_info and port_config.get("type") == "access":
                    if client_info.get("vlan") != port_config.get("vlan"):
                        issues.append(f"Client VLAN ({client_info.get('vlan')}) doesn't match port VLAN ({port_config.get('vlan')})")
                        recommendations.append("Update port VLAN configuration to match client requirements")
                
                # Check access policy restrictions
                if port_config.get("accessPolicyType") in ["MAC allow list", "Sticky MAC allow list"]:
                    if client_mac and port_status and port_status.get("status") != "Connected":
                        issues.append("Port may be blocking client due to MAC allow list restrictions")
                        recommendations.append("Add client MAC to port's allowed MAC list")
                
                # Compile troubleshooting results
                result = {
                    "status": "success",
                    "port": {
                        "id": port_id,
                        "config": port_config,
                        "status": port_status
                    },
                    "client": client_info,
                    "troubleshooting": {
                        "issues_found": len(issues) > 0,
                        "issues": issues,
                        "recommendations": recommendations
                    }
                }
                
                return result
                
            except Exception as e:
                logger.error(f"Error troubleshooting switch port: {e}")
                return {
                    "status": "error",
                    "message": f"Error troubleshooting switch port: {str(e)}"
                }
