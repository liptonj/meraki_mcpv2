"""
Client-related MCP tools for the Meraki dashboard API.

This module contains MCP tools for interacting with Meraki network clients.
"""

import logging
from typing import Any, Dict, List, Optional

from meraki_mcp.tools.base import ToolBase

logger = logging.getLogger(__name__)


class ClientTools(ToolBase):
    """Client-related MCP tools for Meraki dashboard API."""

    def __init__(self, server_instance):
        """Initialize ClientTools.
        
        Args:
            server_instance: The MerakiMCPServer instance that this tool class is associated with
        """
        super().__init__(server_instance)
        
    def get_capabilities(self):
        """Get the list of capabilities provided by this client tool class.
        
        Returns:
            List[str]: A list of capability names as strings
        """
        return [
            "get_network_clients",
            "get_network_client",
            "get_network_client_usage_history",
            "get_network_client_connectivity",
            "troubleshoot_client_connectivity",
            "analyze_client_traffic_history",
            "get_client_latency_stats",
            "get_client_application_usage",
            "get_client_security_events"
        ]
        
    def _register_resources(self):
        """Register client-related resources with the MCP server."""
        # Define any client-specific resources here
        @self._mcp.resource("clients://schema")
        def client_schema():
            """Schema for client data."""
            return {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "mac": {"type": "string"},
                    "description": {"type": "string"},
                    "ip": {"type": "string"},
                    "ip6": {"type": "string"},
                    "user": {"type": "string"},
                    "firstSeen": {"type": "string", "format": "date-time"},
                    "lastSeen": {"type": "string", "format": "date-time"},
                    "manufacturer": {"type": "string"},
                    "os": {"type": "string"},
                    "status": {"type": "string", "enum": ["Online", "Offline"]},
                    "ssid": {"type": "string"},
                    "vlan": {"type": "integer"},
                    "switchport": {"type": "string"},
                    "wirelessCapabilities": {"type": "string"}
                }
            }
    
    def _register_tools(self):
        """Register client-related tools with the MCP server."""
        
        @self._mcp.tool()
        async def get_network_clients(request: Dict[str, Any]) -> Dict[str, Any]:
            """Get clients in a Meraki network.
            
            Args:
                request: A dictionary containing:
                    - network_id (str): Network ID
                    - timespan (int, optional): Timespan in seconds for which clients are fetched
            
            Returns:
                Dict containing clients in the network
            
            Raises:
                Exception: If Meraki client is not initialized or required parameters are missing
            """
            return await self.get_network_clients(request)
            
        @self._mcp.tool()
        async def get_network_client(request: Dict[str, Any]) -> Dict[str, Any]:
            """Get information about a specific client in a Meraki network.
            
            Args:
                request: A dictionary containing:
                    - network_id (str): Network ID
                    - client_id (str): Client ID or MAC address
            
            Returns:
                Dict containing client information
            
            Raises:
                Exception: If Meraki client is not initialized or required parameters are missing
            """
            return await self.get_network_client(request)
            
        @self._mcp.tool()
        async def get_network_client_usage_history(request: Dict[str, Any]) -> Dict[str, Any]:
            """Get usage history for a specific client in a Meraki network.
            
            Args:
                request: A dictionary containing:
                    - network_id (str): Network ID
                    - client_id (str): Client ID or MAC address
            
            Returns:
                Dict containing client usage history
            
            Raises:
                Exception: If Meraki client is not initialized or required parameters are missing
            """
            return await self.get_network_client_usage_history(request)
            
        @self._mcp.tool()
        async def get_network_client_connectivity(request: Dict[str, Any]) -> Dict[str, Any]:
            """Get connectivity information for a specific client in a Meraki network.
            
            Args:
                request: A dictionary containing:
                    - network_id (str): Network ID
                    - client_id (str): Client ID or MAC address
                    - timespan (int): Timespan in seconds
            
            Returns:
                Dict containing client connectivity information
            
            Raises:
                Exception: If Meraki client is not initialized or required parameters are missing
            """
            return await self.get_network_client_connectivity(request)
            
        @self._mcp.tool()
        async def troubleshoot_client_connectivity(request: Dict[str, Any]) -> Dict[str, Any]:
            """Troubleshoot client connectivity issues.
            
            This tool performs comprehensive connectivity troubleshooting for a client,
            analyzing signal quality, association status, authentication issues,
            IP addressing, and network path problems.
            
            Args:
                request: A dictionary containing:
                    - network_id (str): Network ID
                    - client_id (str): Client ID or MAC address
                    - timespan (int, optional): Timespan in seconds for analysis (default: 3600)
            
            Returns:
                Dict containing troubleshooting results with detected issues and recommendations
            
            Raises:
                Exception: If Meraki client is not initialized or required parameters are missing
            """
            return await self.troubleshoot_client_connectivity(request)
            
        @self._mcp.tool()
        async def analyze_client_traffic_history(request: Dict[str, Any]) -> Dict[str, Any]:
            """Analyze client traffic history and patterns.
            
            This tool analyzes client traffic patterns over time to identify unusual behavior,
            bandwidth usage trends, and potential application issues.
            
            Args:
                request: A dictionary containing:
                    - network_id (str): Network ID
                    - client_id (str): Client ID or MAC address
                    - timespan (int, optional): Timespan in seconds for analysis (default: 86400 - 1 day)
            
            Returns:
                Dict containing traffic analysis with patterns, anomalies, and recommendations
            
            Raises:
                Exception: If Meraki client is not initialized or required parameters are missing
            """
            return await self.analyze_client_traffic_history(request)
            
        @self._mcp.tool()
        async def get_client_latency_stats(request: Dict[str, Any]) -> Dict[str, Any]:
            """Get detailed latency statistics for a client.
            
            This tool retrieves and analyzes detailed latency statistics for a client,
            providing insights into network performance issues.
            
            Args:
                request: A dictionary containing:
                    - network_id (str): Network ID
                    - client_id (str): Client ID or MAC address
                    - timespan (int, optional): Timespan in seconds (default: 3600 - 1 hour)
            
            Returns:
                Dict containing detailed latency statistics and analysis
            
            Raises:
                Exception: If Meraki client is not initialized or required parameters are missing
            """
            return await self.get_client_latency_stats(request)
            
        @self._mcp.tool()
        async def get_client_application_usage(request: Dict[str, Any]) -> Dict[str, Any]:
            """Get detailed application usage for a client.
            
            This tool retrieves and analyzes application usage patterns for a specific client,
            providing insights into bandwidth consumption by application type.
            
            Args:
                request: A dictionary containing:
                    - network_id (str): Network ID
                    - client_id (str): Client ID or MAC address
                    - timespan (int, optional): Timespan in seconds (default: 86400 - 1 day)
            
            Returns:
                Dict containing detailed application usage statistics and analysis
            
            Raises:
                Exception: If Meraki client is not initialized or required parameters are missing
            """
            return await self.get_client_application_usage(request)
            
        @self._mcp.tool()
        async def get_client_security_events(request: Dict[str, Any]) -> Dict[str, Any]:
            """Get security events associated with a specific client.
            
            This tool retrieves and analyzes security events related to a specific client,
            providing insights into potential security issues.
            
            Args:
                request: A dictionary containing:
                    - network_id (str): Network ID
                    - client_id (str): Client ID or MAC address
                    - timespan (int, optional): Timespan in seconds (default: 86400 - 1 day)
                    - per_page (int, optional): Number of results per page (default: 100)
            
            Returns:
                Dict containing security events and analysis
            
            Raises:
                Exception: If Meraki client is not initialized or required parameters are missing
            """
            return await self.get_client_security_events(request)

    async def get_network_clients(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Get clients in a Meraki network.
        
        Args:
            request: A dictionary containing:
                - network_id (str): Network ID
                - timespan (int, optional): Timespan in seconds for which clients are fetched
                - per_page (int, optional): Number of clients per page (default: 100)
                - total_pages (int, optional): Total number of pages to retrieve, -1 for all (default: -1)
        
        Returns:
            Dict containing clients in the network
        
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
        
        # Optional parameters
        timespan = request.get("timespan")
        per_page = request.get("per_page", 100)  # Default to 100 items per page
        total_pages = request.get("total_pages", -1)  # Default to all pages
        
        try:
            # The wrapper method now handles pagination internally
            clients = self._meraki_client.get_network_clients(
                network_id, 
                timespan=timespan,
                per_page=per_page,
                total_pages=total_pages
            )
            
            logger.info(f"Retrieved {len(clients)} clients from network {network_id}")
            
            return {
                "status": "success",
                "client_count": len(clients),
                "clients": clients
            }
            
        except Exception as e:
            logger.error(f"Error getting network clients: {e}")
            return {
                "status": "error",
                "message": f"Error getting network clients: {str(e)}"
            }

    async def get_network_client(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Get information about a specific client in a Meraki network.
        
        Args:
            request: A dictionary containing:
                - network_id (str): Network ID
                - client_id (str): Client ID or MAC address
        
        Returns:
            Dict containing client information
        
        Raises:
            Exception: If Meraki client is not initialized or required parameters are missing
        """
        if not self._meraki_client:
            return {
                "status": "error",
                "message": "Meraki client not initialized. Check your MERAKI_API_KEY."
            }
            
        # Extract required parameters
        network_id = request.get("network_id")
        client_id = request.get("client_id")
        
        if not network_id:
            return {
                "status": "error",
                "message": "network_id is required"
            }
            
        if not client_id:
            return {
                "status": "error",
                "message": "client_id is required"
            }
        
        try:
            # Use the MerakiClient wrapper method
            client_info = self._meraki_client.get_network_client(network_id, client_id)
            
            logger.info(f"Retrieved client information for {client_id} in network {network_id}")
            
            return {
                "status": "success",
                "client": client_info
            }
            
        except Exception as e:
            logger.error(f"Error getting client information: {e}")
            return {
                "status": "error",
                "message": f"Error getting client information: {str(e)}"
            }

    async def get_network_client_usage_history(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Get usage history for a specific client in a Meraki network.
        
        Args:
            request: A dictionary containing:
                - network_id (str): Network ID
                - client_id (str): Client ID or MAC address
                - per_page (int, optional): Number of records per page (default: 100)
                - total_pages (int, optional): Total number of pages to retrieve, -1 for all (default: -1)
        
        Returns:
            Dict containing client usage history
        
        Raises:
            Exception: If Meraki client is not initialized or required parameters are missing
        """
        error_response = self._check_meraki_client()
        if error_response:
            return error_response
            
        # Extract required parameters
        network_id = request.get("network_id")
        client_id = request.get("client_id")
        
        if not network_id:
            return {
                "status": "error",
                "message": "network_id is required"
            }
            
        if not client_id:
            return {
                "status": "error",
                "message": "client_id is required"
            }
        
        # Extract pagination parameters
        per_page = request.get("per_page", 100)  # Default to 100 items per page
        total_pages = request.get("total_pages", -1)  # Default to all pages
        
        try:
            # Configure pagination parameters
            # The wrapper method now handles pagination internally
            usage_history = self._meraki_client.get_network_client_usage_history(
                network_id,
                client_id,
                per_page=per_page,
                total_pages=total_pages
            )
            
            logger.info(f"Retrieved {len(usage_history)} usage history records for client {client_id} in network {network_id}")
            
            return {
                "status": "success",
                "history_count": len(usage_history),
                "usage_history": usage_history
            }
            
        except Exception as e:
            logger.error(f"Error getting client usage history: {e}")
            return {
                "status": "error",
                "message": f"Error getting client usage history: {str(e)}"
            }

    async def get_network_client_connectivity(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Get connectivity information for a specific client in a Meraki network.
        
        Args:
            request: A dictionary containing:
                - network_id (str): Network ID
                - client_id (str): Client ID or MAC address
                - timespan (int): Timespan in seconds
                - per_page (int, optional): Number of records per page (default: 100)
                - total_pages (int, optional): Total number of pages to retrieve, -1 for all (default: -1)
        
        Returns:
            Dict containing client connectivity information
        
        Raises:
            Exception: If Meraki client is not initialized or required parameters are missing
        """
        error_response = self._check_meraki_client()
        if error_response:
            return error_response
            
        # Extract required parameters
        network_id = request.get("network_id")
        client_id = request.get("client_id")
        timespan = request.get("timespan")
        per_page = request.get("per_page", 100)  # Default to 100 items per page
        total_pages = request.get("total_pages", -1)  # Default to all pages
        
        if not network_id:
            return {
                "status": "error",
                "message": "network_id is required"
            }
            
        if not client_id:
            return {
                "status": "error",
                "message": "client_id is required"
            }
            
        if not timespan:
            return {
                "status": "error",
                "message": "timespan is required"
            }
        
        try:
            # The wrapper method now handles pagination internally
            connectivity = self._meraki_client.get_network_client_connectivity(
                network_id,
                client_id,
                timespan=timespan,
                per_page=per_page,
                total_pages=total_pages
            )
            
            logger.info(f"Retrieved connectivity data for client {client_id} in network {network_id}")
            
            return {
                "status": "success",
                "connectivity": connectivity
            }
            
        except Exception as e:
            logger.error(f"Error getting client connectivity: {e}")
            return {
                "status": "error",
                "message": f"Error getting client connectivity: {str(e)}"
            }
            
    async def troubleshoot_client_connectivity(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Troubleshoot client connectivity issues.
        
        This tool performs comprehensive connectivity troubleshooting for a client,
        analyzing signal quality, association status, authentication issues,
        IP addressing, and network path problems.
        
        Args:
            request: A dictionary containing:
                - network_id (str): Network ID
                - client_id (str): Client ID or MAC address
                - timespan (int, optional): Timespan in seconds for analysis (default: 3600)
        
        Returns:
            Dict containing troubleshooting results with detected issues and recommendations
        
        Raises:
            Exception: If Meraki client is not initialized or required parameters are missing
        """
        error_response = self._check_meraki_client()
        if error_response:
            return error_response
            
        # Extract required parameters
        network_id = request.get("network_id")
        client_id = request.get("client_id")
        timespan = request.get("timespan", 3600)  # Default to 1 hour
        
        if not network_id:
            return {
                "status": "error",
                "message": "network_id is required"
            }
            
        if not client_id:
            return {
                "status": "error",
                "message": "client_id is required"
            }
        
        try:
            # Get current client details
            client_details = None
            try:
                client_details = self._meraki_client.get_network_client(
                    network_id, client_id
                )
            except Exception as client_err:
                logger.warning(f"Could not retrieve client details: {client_err}")
                
            # Get connectivity info
            connectivity = None
            try:
                connectivity = self._meraki_client.get_network_client_connectivity(
                    network_id, client_id, timespan=timespan
                )
            except Exception as conn_err:
                logger.warning(f"Could not retrieve connectivity details: {conn_err}")
            
            # Get device info if client is connected to an access point
            device_serial = None
            device_details = None
            if client_details and client_details.get("recentDeviceSerial"):
                device_serial = client_details.get("recentDeviceSerial")
                try:
                    device_details = self._meraki_client.get_device(device_serial)
                except Exception as device_err:
                    logger.warning(f"Could not retrieve device details: {device_err}")
            
            # Initialize troubleshooting results
            issues = []
            recommendations = []
            
            # Analyze client status
            if client_details:
                # Check connection status
                if client_details.get("status") != "Online":
                    issues.append("Client is currently offline")
                    recommendations.append("Verify the client device is powered on and within range")
                
                # Check for device association
                if not client_details.get("recentDeviceSerial"):
                    issues.append("Client is not associated with any Meraki device")
                    recommendations.append("Check if client is in range of a Meraki AP")
                    recommendations.append("Verify client wireless settings match network configuration")
                
                # Check for VLAN assignment
                if client_details.get("vlan") is None:
                    issues.append("Client does not have a VLAN assignment")
                    recommendations.append("Check network VLAN configuration")
                
                # Check for IP address
                if not client_details.get("ip"):
                    issues.append("Client does not have an IP address")
                    recommendations.append("Check DHCP service functionality")
                    recommendations.append("Verify client is not blocking DHCP")
            
            # Analyze connectivity data
            if connectivity:
                # Check for recent connection failures
                if connectivity.get("connectionStats", {}).get("failedConnections", 0) > 0:
                    issues.append(f"Client has {connectivity.get('connectionStats', {}).get('failedConnections', 0)} failed connection attempts")
                    recommendations.append("Check authentication credentials")
                    recommendations.append("Verify client is authorized on the network")
                
                # Check for signal quality issues
                if connectivity.get("connectionStats", {}).get("averageSignalQuality", 0) < 30:
                    issues.append("Poor signal quality detected")
                    recommendations.append("Move client closer to access point")
                    recommendations.append("Check for interference sources")
                    recommendations.append("Consider adding additional access points to improve coverage")
                
                # Check for latency issues
                if connectivity.get("latencyStats", {}).get("averageLatencyMs", 0) > 100:
                    issues.append(f"High average latency: {connectivity.get('latencyStats', {}).get('averageLatencyMs', 0)}ms")
                    recommendations.append("Check for network congestion")
                    recommendations.append("Prioritize client traffic via QoS settings")
            
            # Get network wireless settings to cross-check client compatibility
            wireless_settings = None
            try:
                wireless_settings = self._meraki_client.get_network_wireless_settings(network_id)
            except Exception as wireless_err:
                logger.warning(f"Could not retrieve wireless settings: {wireless_err}")
            
            if wireless_settings:
                # Check for band steering that might affect connection
                if wireless_settings.get("bandSelection", "Dual band operation") != "Dual band operation":
                    issues.append(f"Network uses band selection: {wireless_settings.get('bandSelection')}")
                    recommendations.append("Verify client device supports the selected wireless band")
            
            # Compile comprehensive troubleshooting results
            result = {
                "status": "success",
                "client": {
                    "id": client_id,
                    "details": client_details
                },
                "device": {
                    "serial": device_serial,
                    "details": device_details
                },
                "connectivity": connectivity,
                "troubleshooting": {
                    "issues_found": len(issues) > 0,
                    "issues": issues,
                    "recommendations": recommendations
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error troubleshooting client connectivity: {e}")
            return {
                "status": "error",
                "message": f"Error troubleshooting client connectivity: {str(e)}"
            }
            
    async def analyze_client_traffic_history(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze client traffic history and patterns.
        
        This tool analyzes client traffic patterns over time to identify unusual behavior,
        bandwidth usage trends, and potential application issues.
        
        Args:
            request: A dictionary containing:
                - network_id (str): Network ID
                - client_id (str): Client ID or MAC address
                - timespan (int, optional): Timespan in seconds for analysis (default: 86400 - 1 day)
        
        Returns:
            Dict containing traffic analysis with patterns, anomalies, and recommendations
        
        Raises:
            Exception: If Meraki client is not initialized or required parameters are missing
        """
        error_response = self._check_meraki_client()
        if error_response:
            return error_response
            
        # Extract required parameters
        network_id = request.get("network_id")
        client_id = request.get("client_id")
        timespan = request.get("timespan", 86400)  # Default to 1 day
        
        if not network_id:
            return {
                "status": "error",
                "message": "network_id is required"
            }
            
        if not client_id:
            return {
                "status": "error",
                "message": "client_id is required"
            }
        
        try:
            # Get client traffic history
            traffic_history = None
            try:
                traffic_history = self._meraki_client.get_network_client_traffic_history(
                    network_id, client_id
                )
            except Exception as traffic_err:
                logger.warning(f"Could not retrieve client traffic history: {traffic_err}")
                
            # Get client details for context
            client_details = None
            try:
                client_details = self._meraki_client.get_network_client(
                    network_id, client_id
                )
            except Exception as client_err:
                logger.warning(f"Could not retrieve client details: {client_err}")
            
            # Initialize analysis results
            patterns = []
            anomalies = []
            recommendations = []
            
            # Analyze traffic data if available
            if traffic_history:
                # Calculate basic statistics
                total_sent = 0
                total_received = 0
                app_usage = {}
                hourly_usage = [0] * 24  # Usage by hour of day
                
                for entry in traffic_history:
                    if "application" in entry and "sent" in entry and "received" in entry:
                        # Aggregate by application
                        app = entry.get("application", "Unknown")
                        sent = entry.get("sent", 0)
                        received = entry.get("received", 0)
                        
                        total_sent += sent
                        total_received += received
                        
                        if app not in app_usage:
                            app_usage[app] = {"sent": 0, "received": 0}
                        
                        app_usage[app]["sent"] += sent
                        app_usage[app]["received"] += received
                        
                        # Track hourly pattern if timestamp available
                        if "timestamp" in entry:
                            try:
                                # Extract hour from timestamp (assuming ISO format)
                                from datetime import datetime
                                timestamp = entry.get("timestamp")
                                hour = datetime.fromisoformat(timestamp.replace('Z', '+00:00')).hour
                                hourly_usage[hour] += (sent + received)
                            except Exception as time_err:
                                logger.warning(f"Could not parse timestamp: {time_err}")
                
                # Identify top applications by bandwidth usage
                top_apps = sorted(
                    [(app, data["sent"] + data["received"]) for app, data in app_usage.items()],
                    key=lambda x: x[1],
                    reverse=True
                )[:5]  # Top 5 applications
                
                if top_apps:
                    patterns.append(f"Top applications by bandwidth: {', '.join([app for app, _ in top_apps])}")
                
                # Identify peak usage hours
                peak_hours = sorted(
                    [(hour, usage) for hour, usage in enumerate(hourly_usage)],
                    key=lambda x: x[1],
                    reverse=True
                )[:3]  # Top 3 hours
                
                if peak_hours and peak_hours[0][1] > 0:
                    peak_hour_strings = [f"{hour}:00-{hour+1}:00" for hour, _ in peak_hours if _ > 0]
                    if peak_hour_strings:
                        patterns.append(f"Peak usage times: {', '.join(peak_hour_strings)}")
                
                # Check for bandwidth anomalies
                if total_sent > 10 * total_received:
                    anomalies.append("Unusually high upload bandwidth compared to download")
                    recommendations.append("Check for backup services, video uploading, or potential data exfiltration")
                
                if total_received > 20 * total_sent:
                    anomalies.append("Extremely high download bandwidth compared to upload")
                    recommendations.append("Check for media streaming, large downloads, or potential malware")
                
                # Look for suspicious application usage
                suspicious_apps = ["BitTorrent", "uTorrent", "Remote Desktop"]
                for app in suspicious_apps:
                    if any(app.lower() in a.lower() for a, _ in top_apps):
                        anomalies.append(f"Potentially concerning application usage: {app}")
                        recommendations.append(f"Review usage of {app} for policy compliance")
            
            # Add general recommendations if no specific issues found
            if not recommendations:
                if client_details and client_details.get("status") == "Online":
                    recommendations.append("Network usage appears normal, continue monitoring")
                    
                    # Add bandwidth optimization tips if usage is high
                    if total_sent + total_received > 1000000000:  # More than 1 GB
                        recommendations.append("Consider QoS policies for bandwidth management")
            
            # Compile analysis results
            result = {
                "status": "success",
                "client": {
                    "id": client_id,
                    "details": client_details
                },
                "traffic_analysis": {
                    "total_sent_bytes": total_sent,
                    "total_received_bytes": total_received,
                    "patterns_detected": patterns,
                    "anomalies_detected": anomalies,
                    "recommendations": recommendations,
                    "top_applications": [{
                        "name": app,
                        "bytes": usage
                    } for app, usage in top_apps] if 'top_apps' in locals() else []
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing client traffic history: {e}")
            return {
                "status": "error",
                "message": f"Error analyzing client traffic history: {str(e)}"
            }
            
    async def get_client_latency_stats(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed latency statistics for a client.
        
        This tool retrieves and analyzes detailed latency statistics for a client,
        providing insights into network performance issues.
        
        Args:
            request: A dictionary containing:
                - network_id (str): Network ID
                - client_id (str): Client ID or MAC address
                - timespan (int, optional): Timespan in seconds (default: 3600 - 1 hour)
        
        Returns:
            Dict containing detailed latency statistics and analysis
        
        Raises:
            Exception: If Meraki client is not initialized or required parameters are missing
        """
        error_response = self._check_meraki_client()
        if error_response:
            return error_response
            
        # Extract required parameters
        network_id = request.get("network_id")
        client_id = request.get("client_id")
        timespan = request.get("timespan", 3600)  # Default to 1 hour
        
        if not network_id:
            return {
                "status": "error",
                "message": "network_id is required"
            }
            
        if not client_id:
            return {
                "status": "error",
                "message": "client_id is required"
            }
        
        try:
            # Get client latency stats
            latency_stats = None
            try:
                latency_stats = self._meraki_client.get_network_client_latency_stats(
                    network_id, 
                    clientId=client_id,
                    timespan=timespan
                )
            except Exception as latency_err:
                logger.warning(f"Could not retrieve client latency stats: {latency_err}")
            
            if not latency_stats:
                return {
                    "status": "error",
                    "message": "No latency statistics available for this client"
                }
            
            # Analyze the latency statistics
            analysis = []
            recommendations = []
            
            # Check for high average latency
            if latency_stats.get("avgLatencyMs", 0) > 100:
                analysis.append(f"High average latency detected: {latency_stats.get('avgLatencyMs')}ms")
                recommendations.append("High latency may impact real-time applications like voice and video")
                recommendations.append("Check for network congestion or routing issues")
            
            # Check for jitter (if present in the stats)
            if latency_stats.get("jitter", 0) > 20:
                analysis.append(f"High jitter detected: {latency_stats.get('jitter')}ms")
                recommendations.append("High jitter can cause audio/video quality issues")
                recommendations.append("Implement QoS policies to prioritize real-time traffic")
            
            # Check for packet loss (if present in the stats)
            if latency_stats.get("lossPercent", 0) > 1:
                analysis.append(f"Packet loss detected: {latency_stats.get('lossPercent')}%")
                recommendations.append("Packet loss can lead to retransmissions and poor application performance")
                recommendations.append("Investigate potential wireless interference or link quality issues")
            
            # Compile latency analysis
            result = {
                "status": "success",
                "client_id": client_id,
                "latency_stats": latency_stats,
                "analysis": {
                    "findings": analysis,
                    "recommendations": recommendations
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting client latency stats: {e}")
            return {
                "status": "error",
                "message": f"Error getting client latency stats: {str(e)}"
            }
    
    async def get_client_application_usage(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed application usage for a client.
        
        This tool retrieves and analyzes application usage patterns for a specific client,
        providing insights into bandwidth consumption by application type.
        
        Args:
            request: A dictionary containing:
                - network_id (str): Network ID
                - client_id (str): Client ID or MAC address
                - timespan (int, optional): Timespan in seconds (default: 86400 - 1 day)
        
        Returns:
            Dict containing detailed application usage statistics and analysis
        
        Raises:
            Exception: If Meraki client is not initialized or required parameters are missing
        """
        error_response = self._check_meraki_client()
        if error_response:
            return error_response
            
        # Extract required parameters
        network_id = request.get("network_id")
        client_id = request.get("client_id")
        timespan = request.get("timespan", 86400)  # Default to 1 day
        
        if not network_id:
            return {
                "status": "error",
                "message": "network_id is required"
            }
            
        if not client_id:
            return {
                "status": "error",
                "message": "client_id is required"
            }
        
        try:
            # Get client application usage
            application_usage = None
            try:
                application_usage = self._meraki_client.get_network_client_application_usage(
                    network_id, client_id, timespan=timespan
                )
            except Exception as app_err:
                logger.warning(f"Could not retrieve client application usage: {app_err}")
            
            if not application_usage or not application_usage.get("applicationUsage"):
                return {
                    "status": "error",
                    "message": "No application usage data available for this client"
                }
            
            # Process application usage data
            apps = application_usage.get("applicationUsage", [])
            
            # Sort applications by total usage (sent + received)
            sorted_apps = sorted(
                apps,
                key=lambda x: (x.get("sent", 0) + x.get("received", 0)),
                reverse=True
            )
            
            # Calculate total usage
            total_sent = sum(app.get("sent", 0) for app in apps)
            total_received = sum(app.get("received", 0) for app in apps)
            total_usage = total_sent + total_received
            
            # Calculate percentage for each application
            for app in sorted_apps:
                app_total = app.get("sent", 0) + app.get("received", 0)
                app["percentage"] = round((app_total / total_usage * 100 if total_usage > 0 else 0), 2)
            
            # Generate insights based on application usage
            insights = []
            recommendations = []
            
            # Check for dominant applications
            if sorted_apps and sorted_apps[0].get("percentage", 0) > 50:
                dominant_app = sorted_apps[0].get("application", "Unknown")
                insights.append(f"{dominant_app} accounts for {sorted_apps[0].get('percentage')}% of total bandwidth")
                
                # Add application-specific recommendations
                if "video" in dominant_app.lower() or "streaming" in dominant_app.lower():
                    recommendations.append("Consider implementing QoS policies for video streaming")
                elif "backup" in dominant_app.lower() or "sync" in dominant_app.lower():
                    recommendations.append("Consider scheduling large backup operations during off-peak hours")
            
            # Check for unusual applications
            suspicious_apps = ["BitTorrent", "uTorrent", "Remote Desktop", "TeamViewer"]
            for app in sorted_apps:
                app_name = app.get("application", "")
                if any(susp_app.lower() in app_name.lower() for susp_app in suspicious_apps):
                    insights.append(f"Potentially concerning application detected: {app_name}")
                    recommendations.append(f"Review usage of {app_name} for policy compliance")
            
            # Compile application usage analysis
            result = {
                "status": "success",
                "client_id": client_id,
                "total_usage": {
                    "sent_bytes": total_sent,
                    "received_bytes": total_received,
                    "total_bytes": total_usage
                },
                "application_usage": sorted_apps[:10],  # Top 10 applications
                "analysis": {
                    "insights": insights,
                    "recommendations": recommendations
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting client application usage: {e}")
            return {
                "status": "error",
                "message": f"Error getting client application usage: {str(e)}"
            }
            
    async def get_client_security_events(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Get security events associated with a specific client.
        
        This tool retrieves and analyzes security events related to a specific client,
        providing insights into potential security issues.
        
        Args:
            request: A dictionary containing:
                - network_id (str): Network ID
                - client_id (str): Client ID or MAC address
                - timespan (int, optional): Timespan in seconds (default: 86400 - 1 day)
                - per_page (int, optional): Number of results per page (default: 100)
        
        Returns:
            Dict containing security events and analysis
        
        Raises:
            Exception: If Meraki client is not initialized or required parameters are missing
        """
        error_response = self._check_meraki_client()
        if error_response:
            return error_response
            
        # Extract required parameters
        network_id = request.get("network_id")
        client_id = request.get("client_id")
        timespan = request.get("timespan", 86400)  # Default to 1 day
        per_page = request.get("per_page", 100)
        
        if not network_id:
            return {
                "status": "error",
                "message": "network_id is required"
            }
            
        if not client_id:
            return {
                "status": "error",
                "message": "client_id is required"
            }
        
        try:
            # Get client security events
            security_events = None
            try:
                security_events = self._meraki_client.get_network_client_security_events(
                    network_id,
                    clientId=client_id,
                    timespan=timespan,
                    per_page=per_page
                )
            except Exception as sec_err:
                logger.warning(f"Could not retrieve client security events: {sec_err}")
            
            if not security_events:
                return {
                    "status": "success",
                    "client_id": client_id,
                    "message": "No security events found for this client",
                    "events": [],
                    "analysis": {
                        "risk_level": "Low",
                        "summary": "No security events detected for this client in the specified time period."
                    }
                }
            
            # Process and categorize security events
            events_by_type = {}
            high_severity_count = 0
            medium_severity_count = 0
            low_severity_count = 0
            
            for event in security_events:
                # Categorize by event type
                event_type = event.get("type", "Unknown")
                if event_type not in events_by_type:
                    events_by_type[event_type] = []
                
                events_by_type[event_type].append(event)
                
                # Count by severity
                severity = event.get("priority", "").lower()
                if severity == "high" or severity == "critical":
                    high_severity_count += 1
                elif severity == "medium":
                    medium_severity_count += 1
                else:
                    low_severity_count += 1
            
            # Determine overall risk level
            risk_level = "Low"
            if high_severity_count > 0:
                risk_level = "High"
            elif medium_severity_count > 0:
                risk_level = "Medium"
            
            # Generate summary and recommendations
            summary = f"Found {len(security_events)} security events for this client."
            if high_severity_count > 0:
                summary += f" {high_severity_count} high severity events detected."
            if medium_severity_count > 0:
                summary += f" {medium_severity_count} medium severity events detected."
            
            recommendations = []
            
            # Add type-specific recommendations
            if "Malware" in events_by_type:
                recommendations.append("Run an antivirus scan on the client device")
                recommendations.append("Check if client software is up to date")
            
            if "IDS Alert" in events_by_type or "IPS Alert" in events_by_type:
                recommendations.append("Investigate potential intrusion attempts")
                recommendations.append("Check client for unusual behavior or unauthorized access")
            
            if "Content Filtering" in events_by_type:
                recommendations.append("Review client's web access patterns")
                recommendations.append("Consider updating content filtering policies if needed")
            
            # Add general recommendations based on risk level
            if risk_level == "High":
                recommendations.append("Consider isolating the client from the network until issues are resolved")
                recommendations.append("Perform a detailed security audit of the client device")
            elif risk_level == "Medium":
                recommendations.append("Monitor the client closely for additional suspicious activity")
            
            # Compile security events analysis
            result = {
                "status": "success",
                "client_id": client_id,
                "events_count": len(security_events),
                "events": security_events[:20],  # Limit to first 20 events to avoid oversized response
                "analysis": {
                    "risk_level": risk_level,
                    "summary": summary,
                    "event_types": list(events_by_type.keys()),
                    "severity_counts": {
                        "high": high_severity_count,
                        "medium": medium_severity_count,
                        "low": low_severity_count
                    },
                    "recommendations": recommendations
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting client security events: {e}")
            return {
                "status": "error",
                "message": f"Error getting client security events: {str(e)}"
            }
    
    def _check_meraki_client(self):
        """Helper method to check if Meraki client is initialized.
        
        Returns:
            Dict or None: Error response dict if client is not initialized, None otherwise
        """
        if not self._meraki_client:
            return {
                "status": "error",
                "message": "Meraki client not initialized. Check your MERAKI_API_KEY."
            }
        return None
