"""
Appliance-related MCP tools for the Meraki dashboard API.

This module contains MCP tools for interacting with Meraki security appliances,
including firewall, VPN, and security configurations.
"""

import logging
from typing import Any, Dict, List, Optional

from meraki_mcp.tools.base import ToolBase

logger = logging.getLogger(__name__)


class ApplianceTools(ToolBase):
    """Appliance-related MCP tools for Meraki dashboard API."""
    
    def __init__(self, server_instance):
        """Initialize ApplianceTools.

        Args:
            server_instance: The MerakiMCPServer instance that this tool class is associated with
        """
        super().__init__(server_instance)

    def get_capabilities(self):
        """Get the list of capabilities provided by this appliance tool class.
        
        Returns:
            List[str]: A list of capability names as strings
        """
        return [
            "get_firewall_rules",
            "get_vpn_status",
            "get_security_events",
            "get_content_filtering",
            "get_intrusion_settings",
            "get_appliance_uplinks",
            "get_appliance_performance",
            "get_site_to_site_vpn",
            "troubleshoot_vpn_connectivity"
        ]
        
    def _register_resources(self):
        """Register appliance-related resources with the MCP server."""
        # Define any appliance-specific resources here
        @self._mcp.resource("appliances://firewall-schema")
        def firewall_rule_schema():
            """Schema for firewall rule data."""
            return {
                "type": "object",
                "properties": {
                    "comment": {"type": "string"},
                    "policy": {"type": "string", "enum": ["allow", "deny"]},
                    "protocol": {"type": "string", "enum": ["tcp", "udp", "icmp", "icmp6", "any"]},
                    "srcPort": {"type": "string"},
                    "srcCidr": {"type": "string"},
                    "destPort": {"type": "string"},
                    "destCidr": {"type": "string"},
                    "syslogEnabled": {"type": "boolean"}
                }
            }
            
        @self._mcp.resource("appliances://vpn-status-schema")
        def vpn_status_schema():
            """Schema for VPN status data."""
            return {
                "type": "object",
                "properties": {
                    "vpnMode": {"type": "string", "enum": ["none", "hub", "spoke"]},
                    "tunnels": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "networkId": {"type": "string"},
                                "networkName": {"type": "string"},
                                "remotePublicIp": {"type": "string"},
                                "remotePrivateSubnets": {"type": "array", "items": {"type": "string"}},
                                "state": {"type": "string", "enum": ["active", "down", "transient"]},
                                "lastStatusChange": {"type": "string", "format": "date-time"}
                            }
                        }
                    }
                }
            }
    
    def _register_tools(self):
        """Register appliance-related tools with the MCP server."""
        
        @self._mcp.tool()
        async def get_firewall_rules(request: Dict[str, Any]) -> Dict[str, Any]:
            """Get firewall rules for a network.
            
            Args:
                request: A dictionary containing:
                    - network_id (str): Network ID
                    
            Returns:
                Dict containing firewall rules
                
            Raises:
                Exception: If Meraki client is not initialized or network_id is missing
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
                # Use the MerakiClient wrapper methods for better error handling and logging
                l3_rules = self._meraki_client.get_network_appliance_firewall_l3_rules(network_id)
                l7_rules = self._meraki_client.get_network_appliance_firewall_l7_rules(network_id)
                return {
                    "status": "success",
                    "firewall_rules": {
                        "l3_rules": l3_rules,
                        "l7_rules": l7_rules
                    }
                }
            except Exception as e:
                logger.error(f"Error getting firewall rules: {e}")
                return {
                    "status": "error",
                    "message": f"Error getting firewall rules: {str(e)}"
                }
                
        @self._mcp.tool()
        async def get_vpn_status(request: Dict[str, Any]) -> Dict[str, Any]:
            """Get VPN status for a network.
            
            Args:
                request: A dictionary containing:
                    - network_id (str): Network ID
                    
            Returns:
                Dict containing VPN status
                
            Raises:
                Exception: If Meraki client is not initialized or network_id is missing
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
                # Use the MerakiClient wrapper methods for better error handling and pagination support
                vpn_status = self._meraki_client.get_site_to_site_vpn(network_id)
                vpn_stats = self._meraki_client.get_network_appliance_vpn_stats(
                    network_id, 
                    per_page=100,
                    total_pages=-1  # Get all pages
                )
                
                return {
                    "status": "success",
                    "vpn": {
                        "configuration": vpn_status,
                        "statistics": vpn_stats
                    }
                }
            except Exception as e:
                logger.error(f"Error getting VPN status: {e}")
                return {
                    "status": "error",
                    "message": f"Error getting VPN status: {str(e)}"
                }
                
        @self._mcp.tool()
        async def get_security_events(request: Dict[str, Any]) -> Dict[str, Any]:
            """Get security events for a network.
            
            Args:
                request: A dictionary containing:
                    - network_id (str): Network ID
                    - timespan (int, optional): Timespan in seconds (default: 86400 - 1 day)
                    
            Returns:
                Dict containing security events
                
            Raises:
                Exception: If Meraki client is not initialized or network_id is missing
            """
            error_response = self._check_meraki_client()
            if error_response:
                return error_response
                
            # Extract request parameters
            network_id = request.get("network_id")
            timespan = request.get("timespan", 86400)  # Default to 1 day
            
            if not network_id:
                return {
                    "status": "error",
                    "message": "network_id is required"
                }
            
            try:
                # Use the MerakiClient wrapper method with pagination support
                security_events = self._meraki_client.get_network_appliance_security_events(
                    network_id, 
                    timespan=timespan,
                    per_page=100,
                    total_pages=-1  # Get all pages
                )
                
                return {
                    "status": "success",
                    "security_events": security_events
                }
            except Exception as e:
                logger.error(f"Error getting security events: {e}")
                return {
                    "status": "error",
                    "message": f"Error getting security events: {str(e)}"
                }
                
        @self._mcp.tool()
        async def get_content_filtering(request: Dict[str, Any]) -> Dict[str, Any]:
            """Get content filtering settings for a network.
            
            Args:
                request: A dictionary containing:
                    - network_id (str): Network ID
                    
            Returns:
                Dict containing content filtering settings
                
            Raises:
                Exception: If Meraki client is not initialized or network_id is missing
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
                # Use the MerakiClient wrapper method for better error handling and logging
                categories = self._meraki_client.get_network_appliance_content_filtering(network_id)
                return {
                    "status": "success",
                    "content_filtering": categories
                }
            except Exception as e:
                logger.error(f"Error getting content filtering settings: {e}")
                return {
                    "status": "error",
                    "message": f"Error getting content filtering settings: {str(e)}"
                }
                
        @self._mcp.tool()
        async def get_intrusion_settings(request: Dict[str, Any]) -> Dict[str, Any]:
            """Get intrusion prevention settings for a network.
            
            Args:
                request: A dictionary containing:
                    - network_id (str): Network ID
                    
            Returns:
                Dict containing intrusion prevention settings
                
            Raises:
                Exception: If Meraki client is not initialized or network_id is missing
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
                # Use the MerakiClient wrapper method for better error handling and logging
                settings = self._meraki_client.get_network_appliance_security_intrusion(network_id)
                return {
                    "status": "success",
                    "intrusion_settings": settings
                }
            except Exception as e:
                logger.error(f"Error getting intrusion settings: {e}")
                return {
                    "status": "error",
                    "message": f"Error getting intrusion settings: {str(e)}"
                }
                
        @self._mcp.tool()
        async def get_appliance_uplinks(request: Dict[str, Any]) -> Dict[str, Any]:
            """Get uplink status and configuration for a Meraki appliance.
            
            Args:
                request: A dictionary containing:
                    - serial (str): Serial number of the appliance
                    
            Returns:
                Dict containing uplink status and configuration
                
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
                uplink_status = self._meraki_client.devices.getDeviceUplink(serial)
                
                # Get device details to get network ID
                device = self._meraki_client.devices.getDevice(serial)
                network_id = device.get("networkId")
                
                # Get uplink configuration
                uplink_config = None
                if network_id:
                    try:
                        # Use the MerakiClient wrapper method for better error handling and logging
                        uplink_config = self._meraki_client.get_network_appliance_uplinks_usages(
                            network_id,
                            timespan=86400  # Last 24 hours
                        )
                    except Exception as uplink_err:
                        logger.warning(f"Error getting uplink usage: {uplink_err}")
                
                return {
                    "status": "success",
                    "uplinks": {
                        "status": uplink_status,
                        "usage": uplink_config
                    }
                }
            except Exception as e:
                logger.error(f"Error getting appliance uplinks: {e}")
                return {
                    "status": "error",
                    "message": f"Error getting appliance uplinks: {str(e)}"
                }
                
        @self._mcp.tool()
        async def get_appliance_performance(request: Dict[str, Any]) -> Dict[str, Any]:
            """Get performance statistics for a Meraki appliance.
            
            Args:
                request: A dictionary containing:
                    - serial (str): Serial number of the appliance
                    - timespan (int, optional): Timespan in seconds (default: 86400 - 1 day)
                    
            Returns:
                Dict containing performance statistics
                
            Raises:
                Exception: If Meraki client is not initialized or serial is missing
            """
            error_response = self._check_meraki_client()
            if error_response:
                return error_response
                
            # Extract request parameters
            serial = request.get("serial")
            timespan = request.get("timespan", 86400)  # Default to 1 day
            
            if not serial:
                return {
                    "status": "error",
                    "message": "serial is required"
                }
            
            try:
                # Get device details to get network ID
                device = self._meraki_client.devices.getDevice(serial)
                network_id = device.get("networkId")
                
                performance_stats = {}
                
                # Get various performance metrics
                if network_id:
                    try:
                        # Get client counts
                        client_stats = self._meraki_client.get_network_clients(
                            network_id,
                            timespan=timespan,
                            per_page=1000
                        )
                        performance_stats["client_count"] = len(client_stats)
                        
                        # Get connection stats
                        connection_stats = self._meraki_client.appliance.getNetworkApplianceConnectivityMonitoringDestinations(
                            network_id
                        )
                        performance_stats["connectivity"] = connection_stats
                        
                        # Get VPN performance
                        vpn_stats = self._meraki_client.appliance.getNetworkApplianceVpnStats(
                            network_id,
                            timespan=timespan
                        )
                        performance_stats["vpn_performance"] = vpn_stats
                        
                    except Exception as stat_err:
                        logger.warning(f"Error getting some performance stats: {stat_err}")
                
                # Get appliance status
                device_status = self._meraki_client.organizations.getOrganizationDevicesStatuses(
                    device.get("organizationId"),
                    serials=[serial]
                )
                if device_status and len(device_status) > 0:
                    performance_stats["device_status"] = device_status[0]
                
                return {
                    "status": "success",
                    "performance": performance_stats
                }
            except Exception as e:
                logger.error(f"Error getting appliance performance: {e}")
                return {
                    "status": "error",
                    "message": f"Error getting appliance performance: {str(e)}"
                }
                
        @self._mcp.tool()
        async def get_site_to_site_vpn(request: Dict[str, Any]) -> Dict[str, Any]:
            """Get site-to-site VPN configuration for a network.
            
            Args:
                request: A dictionary containing:
                    - network_id (str): Network ID
                    
            Returns:
                Dict containing site-to-site VPN configuration
                
            Raises:
                Exception: If Meraki client is not initialized or network_id is missing
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
                # Use the MerakiClient wrapper method for better error handling and logging
                vpn_config = self._meraki_client.get_site_to_site_vpn(network_id)
                return {
                    "status": "success",
                    "site_to_site_vpn": vpn_config
                }
            except Exception as e:
                logger.error(f"Error getting site-to-site VPN: {e}")
                return {
                    "status": "error",
                    "message": f"Error getting site-to-site VPN: {str(e)}"
                }
                
        @self._mcp.tool()
        async def troubleshoot_vpn_connectivity(request: Dict[str, Any]) -> Dict[str, Any]:
            """Troubleshoot VPN connectivity issues between networks.
            
            Args:
                request: A dictionary containing:
                    - organization_id (str): Organization ID 
                    - source_network_id (str): Source network ID
                    - destination_network_id (str): Destination network ID
                    
            Returns:
                Dict containing troubleshooting results
                
            Raises:
                Exception: If Meraki client is not initialized or required parameters are missing
            """
            error_response = self._check_meraki_client()
            if error_response:
                return error_response
                
            # Extract request parameters
            organization_id = request.get("organization_id")
            source_network_id = request.get("source_network_id")
            destination_network_id = request.get("destination_network_id")
            
            if not organization_id:
                return {
                    "status": "error",
                    "message": "organization_id is required"
                }
                
            if not source_network_id:
                return {
                    "status": "error",
                    "message": "source_network_id is required"
                }
                
            if not destination_network_id:
                return {
                    "status": "error",
                    "message": "destination_network_id is required"
                }
            
            try:
                # Get information about both networks using pagination-supported method
                networks = self._meraki_client.get_organization_networks(organization_id)
                source_network = next((n for n in networks if n.get("id") == source_network_id), None)
                destination_network = next((n for n in networks if n.get("id") == destination_network_id), None)
                
                if not source_network:
                    return {
                        "status": "error",
                        "message": f"Source network not found: {source_network_id}"
                    }
                    
                if not destination_network:
                    return {
                        "status": "error",
                        "message": f"Destination network not found: {destination_network_id}"
                    }
                
                # Get VPN status for both networks using wrapper methods
                source_vpn = self._meraki_client.get_site_to_site_vpn(source_network_id)
                destination_vpn = self._meraki_client.get_site_to_site_vpn(destination_network_id)
                
                # Get VPN stats to check if tunnels are active with pagination support
                source_stats = self._meraki_client.get_network_appliance_vpn_stats(source_network_id)
                
                # Analyze VPN configuration for issues
                issues = []
                recommendations = []
                
                # Check if VPN is enabled on both sides
                if source_vpn.get("mode") == "none":
                    issues.append("VPN is disabled on source network")
                    recommendations.append("Enable VPN on source network")
                    
                if destination_vpn.get("mode") == "none":
                    issues.append("VPN is disabled on destination network")
                    recommendations.append("Enable VPN on destination network")
                    
                # Check hub/spoke configuration compatibility
                if source_vpn.get("mode") == "spoke" and destination_vpn.get("mode") == "spoke":
                    issues.append("Both networks are configured as spokes, which cannot establish direct VPN tunnels")
                    recommendations.append("Change one network to hub mode, or connect both to a common hub")
                
                # Check subnet configuration
                source_subnets = []
                destination_subnets = []
                
                if "subnets" in source_vpn:
                    source_subnets = [subnet.get("localSubnet") for subnet in source_vpn.get("subnets", [])]
                    
                if "subnets" in destination_vpn:
                    destination_subnets = [subnet.get("localSubnet") for subnet in destination_vpn.get("subnets", [])]
                
                if not source_subnets:
                    issues.append("No local subnets configured for VPN on source network")
                    recommendations.append("Configure local subnets for VPN on source network")
                    
                if not destination_subnets:
                    issues.append("No local subnets configured for VPN on destination network")
                    recommendations.append("Configure local subnets for VPN on destination network")
                
                # Check if networks are part of the same VPN topology
                source_peers = [hub.get("hubId") for hub in source_vpn.get("hubs", [])]
                destination_peers = [hub.get("hubId") for hub in destination_vpn.get("hubs", [])]
                
                # If source is hub, check if destination is included in its topology
                if source_vpn.get("mode") == "hub":
                    destination_in_source = any(
                        subnet.get("useVpn") and 
                        any(net.get("networkId") == destination_network_id for net in subnet.get("networkIds", []))
                        for subnet in source_vpn.get("subnets", [])
                    )
                    if not destination_in_source:
                        issues.append("Destination network not included in source network's VPN topology")
                        recommendations.append("Add destination network to source network's VPN topology")
                
                # If destination is hub, check if source is included in its topology
                if destination_vpn.get("mode") == "hub":
                    source_in_destination = any(
                        subnet.get("useVpn") and 
                        any(net.get("networkId") == source_network_id for net in subnet.get("networkIds", []))
                        for subnet in destination_vpn.get("subnets", [])
                    )
                    if not source_in_destination:
                        issues.append("Source network not included in destination network's VPN topology")
                        recommendations.append("Add source network to destination network's VPN topology")
                
                # Check for active tunnels
                tunnel_status = "unknown"
                for tunnel in source_stats.get("merakiVpnPeers", []):
                    if tunnel.get("networkId") == destination_network_id:
                        tunnel_status = "active" if tunnel.get("status") == "active" else "down"
                        if tunnel_status == "down":
                            issues.append("VPN tunnel is down")
                            recommendations.append("Check firewall rules allowing IKE and IPsec (UDP 500, UDP 4500, ESP)")
                            recommendations.append("Verify WAN IP connectivity between appliances")
                            recommendations.append("Ensure pre-shared keys match if using PSK authentication")
                
                # Compile troubleshooting results
                result = {
                    "status": "success",
                    "vpn_troubleshooting": {
                        "source_network": {
                            "id": source_network_id,
                            "name": source_network.get("name"),
                            "vpn_configuration": source_vpn
                        },
                        "destination_network": {
                            "id": destination_network_id,
                            "name": destination_network.get("name"),
                            "vpn_configuration": destination_vpn
                        },
                        "tunnel_status": tunnel_status,
                        "issues_found": len(issues) > 0,
                        "issues": issues,
                        "recommendations": recommendations
                    }
                }
                
                return result
                
            except Exception as e:
                logger.error(f"Error troubleshooting VPN connectivity: {e}")
                return {
                    "status": "error",
                    "message": f"Error troubleshooting VPN connectivity: {str(e)}"
                }
