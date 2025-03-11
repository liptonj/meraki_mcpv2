"""
Wireless-related MCP tools for the Meraki dashboard API.

This module contains MCP tools for interacting with Meraki wireless networks,
focusing on SSID management, troubleshooting, and RF visualization.
"""

import logging
import re
from typing import Any, Dict, List, Optional, Tuple, Set

from meraki_mcp.tools.base import ToolBase

logger = logging.getLogger(__name__)


class WirelessTools(ToolBase):
    """Wireless-related MCP tools for Meraki dashboard API."""

    def __init__(self, server_instance):
        """Initialize WirelessTools.
        
        Args:
            server_instance: The MerakiMCPServer instance that this tool class is associated with
        """
        super().__init__(server_instance)
        
    def get_capabilities(self):
        """Get the list of capabilities provided by this wireless tool class.
        
        Returns:
            List[str]: A list of capability names as strings
        """
        return [
            "get_wireless_ssids",
            "get_ssid_details",
            "verify_ssid_status",
            "get_wireless_status",
            "get_wireless_clients",
            "get_wireless_rf_profiles",
            "troubleshoot_ssid_connectivity",
            "analyze_wireless_spectrum",
            "get_wireless_latency_stats",
            "get_wireless_air_quality",
            "analyze_wifi_description",
            "troubleshoot_wifi_issue"
        ]
        
    def _register_resources(self):
        """Register wireless-related resources with the MCP server."""
        # Define any wireless-specific resources here
        @self._mcp.resource("wireless://schema")
        def wireless_schema():
            """Schema for wireless data."""
            return {
                "type": "object",
                "properties": {
                    "ssid": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "enabled": {"type": "boolean"},
                            "authMode": {"type": "string"},
                            "encryptionMode": {"type": "string"},
                            "broadcasting": {"type": "boolean"},
                            "clientCount": {"type": "integer"}
                        }
                    },
                    "rf_profile": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "bandSelectionType": {"type": "string"},
                            "minBitrateType": {"type": "string"},
                            "channelWidth": {"type": "string"}
                        }
                    }
                }
            }
    
    def _register_tools(self):
        """Register wireless-related tools with the MCP server."""
        
        @self._mcp.tool()
        async def get_wireless_ssids(request: Dict[str, Any]) -> Dict[str, Any]:
            """Get SSIDs configured in a Meraki network.
            
            Args:
                request: A dictionary containing:
                    - network_id (str): Network ID
            
            Returns:
                Dict containing SSIDs in the network
            
            Raises:
                Exception: If Meraki client is not initialized or required parameters are missing
            """
            return await self.get_wireless_ssids(request)
            
        @self._mcp.tool()
        async def get_ssid_details(request: Dict[str, Any]) -> Dict[str, Any]:
            """Get detailed information about a specific SSID in a Meraki network.
            
            Args:
                request: A dictionary containing:
                    - network_id (str): Network ID
                    - ssid_number (int): SSID number (0-14)
            
            Returns:
                Dict containing SSID details
            
            Raises:
                Exception: If Meraki client is not initialized or required parameters are missing
            """
            return await self.get_ssid_details(request)
            
        @self._mcp.tool()
        async def verify_ssid_status(request: Dict[str, Any]) -> Dict[str, Any]:
            """Verify if an SSID is broadcasting and accessible.
            
            This tool checks if an SSID is correctly configured, enabled, and broadcasting
            across all access points in the network. It can detect issues with specific
            access points not broadcasting the SSID correctly.
            
            Args:
                request: A dictionary containing:
                    - network_id (str, optional): Network ID
                    - organization_id (str, optional): Organization ID to search in
                    - ssid_number (int, optional): SSID number (0-14)
                    - ssid_name (str, optional): SSID name to verify
                    
                    Note: Either (network_id and ssid_number) OR ssid_name must be provided.
                    If only ssid_name is provided, the tool will search across available networks.
            
            Returns:
                Dict containing SSID broadcasting status across all access points
            
            Raises:
                Exception: If Meraki client is not initialized or required parameters are missing
            """
            return await self.verify_ssid_status(request)
            
        @self._mcp.tool()
        async def troubleshoot_ssid_connectivity(request: Dict[str, Any]) -> Dict[str, Any]:
            """Troubleshoot connectivity issues with a specific SSID.
            
            This tool performs comprehensive troubleshooting on an SSID, checking for common
            issues like incorrect authentication settings, channel interference, AP coverage gaps,
            and client compatibility problems.
            
            Args:
                request: A dictionary containing:
                    - network_id (str): Network ID
                    - ssid_number (int): SSID number (0-14)
                    - client_mac (str, optional): MAC address of a specific client having issues
            
            Returns:
                Dict containing troubleshooting results with detected issues and recommendations
            
            Raises:
                Exception: If Meraki client is not initialized or required parameters are missing
            """
            return await self.troubleshoot_ssid_connectivity(request)
            
        @self._mcp.tool()
        async def get_wireless_status(request: Dict[str, Any]) -> Dict[str, Any]:
            """Get wireless status for all access points in a network.
            
            Args:
                request: A dictionary containing:
                    - network_id (str): Network ID
            
            Returns:
                Dict containing wireless status for all access points
            
            Raises:
                Exception: If Meraki client is not initialized or required parameters are missing
            """
            return await self.get_wireless_status(request)
            
        @self._mcp.tool()
        async def analyze_wifi_description(request: Dict[str, Any]) -> Dict[str, Any]:
            """Analyze a natural language description of a WiFi issue.
            
            This tool uses natural language processing to extract key information from
            a user's description of a WiFi issue and identify potential causes.
            
            Args:
                request: A dictionary containing:
                    - description (str): Natural language description of the WiFi issue
                    - network_id (str, optional): Network ID if available
                    
            Returns:
                Dict containing analysis results with detected issues and recommendations
                
            Raises:
                Exception: If required parameters are missing
            """
            return await self.analyze_wifi_description(request)
            
        @self._mcp.tool()
        async def troubleshoot_wifi_issue(request: Dict[str, Any]) -> Dict[str, Any]:
            """Troubleshoot a WiFi issue based on natural language description.
            
            This tool analyzes a natural language description of a WiFi issue, extracts
            key information, and attempts to diagnose and resolve the issue by integrating
            with the WiFi knowledge base.
            
            Args:
                request: A dictionary containing:
                    - description (str): Natural language description of the WiFi issue
                    - network_id (str, optional): Network ID if available
                    - ssid_name (str, optional): SSID name if known
                    - client_mac (str, optional): Client MAC address if issue is specific to a client
                    
            Returns:
                Dict containing troubleshooting results with detected issues and recommendations
                
            Raises:
                Exception: If required parameters are missing
            """
            return await self.troubleshoot_wifi_issue(request)

    async def get_wireless_ssids(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Get SSIDs configured in a Meraki network.
        
        Args:
            request: A dictionary containing:
                - network_id (str): Network ID
        
        Returns:
            Dict containing SSIDs in the network
        
        Raises:
            Exception: If Meraki client is not initialized or required parameters are missing
        """
        error_response = self._check_meraki_client()
        if error_response:
            return error_response
            
        # Extract required parameters
        network_id = request.get("network_id")
        
        if not network_id:
            return {
                "status": "error",
                "message": "network_id is required"
            }
        
        try:
            # Get SSIDs for the network
            # Use pagination to retrieve all wireless SSIDs if supported
            ssids = self._meraki_client.get_network_wireless_ssids(network_id)
            
            return {
                "status": "success",
                "ssid_count": len(ssids),
                "ssids": ssids
            }
            
        except Exception as e:
            logger.error(f"Error getting wireless SSIDs: {e}")
            return {
                "status": "error",
                "message": f"Error getting wireless SSIDs: {str(e)}"
            }
            
    async def get_ssid_details(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed information about a specific SSID in a Meraki network.
        
        Args:
            request: A dictionary containing:
                - network_id (str): Network ID
                - ssid_number (int): SSID number (0-14)
        
        Returns:
            Dict containing SSID details
        
        Raises:
            Exception: If Meraki client is not initialized or required parameters are missing
        """
        error_response = self._check_meraki_client()
        if error_response:
            return error_response
            
        # Extract required parameters
        network_id = request.get("network_id")
        ssid_number = request.get("ssid_number")
        
        if not network_id:
            return {
                "status": "error",
                "message": "network_id is required"
            }
            
        if ssid_number is None:
            return {
                "status": "error",
                "message": "ssid_number is required"
            }
            
        try:
            # Get SSID details
            
            ssid = self._meraki_client.get_network_wireless_ssid(
                network_id, 
                ssid_number
            )
            
            return {
                "status": "success",
                "ssid": ssid
            }
            
        except Exception as e:
            logger.error(f"Error getting SSID details: {e}")
            return {
                "status": "error",
                "message": f"Error getting SSID details: {str(e)}"
            }
            
    async def verify_ssid_status(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Verify if an SSID is broadcasting and accessible.
        
        This tool checks if an SSID is correctly configured, enabled, and broadcasting
        across all access points in the network. It can detect issues with specific
        access points not broadcasting the SSID correctly.
        
        Args:
            request: A dictionary containing:
                - network_id (str, optional): Network ID
                - organization_id (str, optional): Organization ID to search in
                - ssid_number (int, optional): SSID number (0-14)
                - ssid_name (str, optional): SSID name to verify
                
                Note: Either (network_id and ssid_number) OR ssid_name must be provided.
                If only ssid_name is provided, the tool will search across available networks.
        
        Returns:
            Dict containing SSID broadcasting status across all access points
        
        Raises:
            Exception: If Meraki client is not initialized or required parameters are missing
        """
        error_response = self._check_meraki_client()
        if error_response:
            return error_response
            
        # Extract parameters
        network_id = request.get("network_id")
        organization_id = request.get("organization_id")
        ssid_number = request.get("ssid_number")
        ssid_name = request.get("ssid_name")
        
        # Check if we have enough information to proceed
        if not ssid_name and (not network_id or ssid_number is None):
            return {
                "status": "error",
                "message": "Either (network_id and ssid_number) OR ssid_name must be provided"
            }
        
        # If we only have ssid_name, we need to find the network and SSID number
        if ssid_name and (not network_id or ssid_number is None):
            logger.info(f"Searching for SSID with name: {ssid_name}")
            
            try:
                # First, get list of organizations if organization_id not provided
                if not organization_id:
                    try:
                        organizations = self._meraki_client.get_organizations()
                        if not organizations:
                            return {
                                "status": "error",
                                "message": "No organizations found. Please provide an organization_id."
                            }
                    except Exception as e:
                        logger.error(f"Error getting organizations: {e}")
                        return {
                            "status": "error",
                            "message": f"Error retrieving organizations: {str(e)}"
                        }
                else:
                    # Use the provided organization_id
                    organizations = [{'id': organization_id}]
                
                # For each organization, get networks and search for the SSID
                found_networks = []
                
                for org in organizations:
                    try:
                        org_id = org.get('id')
                        networks = self._meraki_client.get_organization_networks(org_id)
                        
                        # For each network, get SSIDs and check for a match
                        for net in networks:
                            try:
                                net_id = net.get('id')
                                if not net.get('productTypes') or 'wireless' not in net.get('productTypes'):
                                    continue
                                    
                                ssids = self._meraki_client.get_network_wireless_ssids(net_id)
                                
                                for ssid in ssids:
                                    if ssid.get('name') == ssid_name:
                                        found_networks.append({
                                            'organization_id': org_id,
                                            'network_id': net_id,
                                            'network_name': net.get('name'),
                                            'ssid_number': ssid.get('number'),
                                            'ssid_config': ssid
                                        })
                            except Exception as net_err:
                                logger.warning(f"Error checking network {net.get('name', net.get('id'))}: {net_err}")
                                continue
                    except Exception as org_err:
                        logger.warning(f"Error checking organization {org.get('id')}: {org_err}")
                        continue
                
                if not found_networks:
                    return {
                        "status": "error",
                        "message": f"SSID with name '{ssid_name}' not found in any accessible network"
                    }
                
                # If we found exactly one network with this SSID, use it
                if len(found_networks) == 1:
                    network_id = found_networks[0]['network_id']
                    ssid_number = found_networks[0]['ssid_number']
                    logger.info(f"Found SSID '{ssid_name}' in network '{found_networks[0]['network_name']}' (ID: {network_id})")
                else:
                    # If multiple networks have this SSID, return the list for selection
                    return {
                        "status": "selection_required",
                        "message": f"Found SSID '{ssid_name}' in multiple networks. Please specify which network to check.",
                        "found_networks": found_networks
                    }
                    
            except Exception as search_err:
                logger.error(f"Error searching for SSID '{ssid_name}': {search_err}")
                return {
                    "status": "error",
                    "message": f"Error searching for SSID '{ssid_name}': {str(search_err)}"
                }
            
        try:
            # Get SSID configuration details
            ssid_config = None
            try:
                ssid_config = self._meraki_client.get_network_wireless_ssid(
                    network_id, 
                    ssid_number
                )
            except Exception as ssid_err:
                logger.warning(f"Could not retrieve SSID configuration: {ssid_err}")
                return {
                    "status": "error",
                    "message": f"SSID with number {ssid_number} not found or inaccessible: {str(ssid_err)}"
                }
                
            # Verify SSID name if provided
            if ssid_name and ssid_config.get("name") != ssid_name:
                return {
                    "status": "error",
                    "message": f"SSID name mismatch. Expected '{ssid_name}' but found '{ssid_config.get('name')}'",
                    "ssid_config": ssid_config
                }
                
            # Check if SSID is enabled in configuration
            if not ssid_config.get("enabled", False):
                return {
                    "status": "warning",
                    "message": f"SSID '{ssid_config.get('name')}' is disabled in configuration",
                    "broadcasting": False,
                    "ssid_config": ssid_config,
                    "recommendations": [
                        "Enable the SSID in the Meraki dashboard"
                    ]
                }
                
            # Get all wireless devices in the network
            devices = []
            try:
                # Retrieve all network devices
                devices = self._meraki_client.get_network_devices(
                    network_id
                )
                # Filter to get only wireless access points
                devices = [d for d in devices if d.get("model", "").startswith("MR")]
            except Exception as devices_err:
                logger.warning(f"Could not retrieve network devices: {devices_err}")
            
            if not devices:
                return {
                    "status": "warning",
                    "message": "No wireless access points found in the network",
                    "broadcasting": ssid_config.get("enabled", False),
                    "ssid_config": ssid_config
                }
            
            # Check the status of each access point
            ap_status = []
            broadcasting_aps = 0
            non_broadcasting_aps = 0
            
            for device in devices:
                device_serial = device.get("serial")
                
                if not device_serial:
                    continue
                    
                # Get the device wireless status
                device_status = None
                try:
    
                    device_status = self._meraki_client.get_device_wireless_status(device_serial)
                except Exception as status_err:
                    logger.warning(f"Could not retrieve wireless status for device {device_serial}: {status_err}")
                    ap_status.append({
                        "serial": device_serial,
                        "name": device.get("name"),
                        "model": device.get("model"),
                        "status": "Error retrieving status",
                        "broadcasting_ssid": False,
                        "error": str(status_err)
                    })
                    non_broadcasting_aps += 1
                    continue
                
                # Check if the SSID is broadcasting on this AP
                broadcasting_this_ssid = False
                ssids_status = device_status.get("ssids", [])
                
                for ssid_status in ssids_status:
                    if ssid_status.get("number") == ssid_number:
                        broadcasting_this_ssid = ssid_status.get("enabled", False) and ssid_status.get("broadcasting", False)
                        break
                
                ap_status.append({
                    "serial": device_serial,
                    "name": device.get("name"),
                    "model": device.get("model"),
                    "status": device_status.get("status", "Unknown"),
                    "broadcasting_ssid": broadcasting_this_ssid
                })
                
                if broadcasting_this_ssid:
                    broadcasting_aps += 1
                else:
                    non_broadcasting_aps += 1
            
            # Generate recommendations based on findings
            recommendations = []
            if broadcasting_aps == 0 and non_broadcasting_aps > 0:
                recommendations.append("SSID is not broadcasting on any access points despite being enabled")
                recommendations.append("Check RF profiles and channel settings")
                recommendations.append("Verify that access points have connectivity to the Meraki cloud")
            elif broadcasting_aps > 0 and non_broadcasting_aps > 0:
                recommendations.append("SSID is broadcasting on some access points but not all")
                recommendations.append("Check configuration synchronization across access points")
                recommendations.append("Verify that all access points have the same RF profile")
            
            # Determine overall broadcasting status
            overall_broadcasting = broadcasting_aps > 0
            
            return {
                "status": "success",
                "ssid_name": ssid_config.get("name"),
                "broadcasting": overall_broadcasting,
                "ssid_config": ssid_config,
                "ap_count": len(devices),
                "broadcasting_aps": broadcasting_aps,
                "non_broadcasting_aps": non_broadcasting_aps,
                "ap_status": ap_status,
                "recommendations": recommendations
            }
            
        except Exception as e:
            logger.error(f"Error verifying SSID status: {e}")
            return {
                "status": "error",
                "message": f"Error verifying SSID status: {str(e)}"
            }
            
    async def analyze_wifi_description(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a natural language description of a WiFi issue.
        
        This tool uses natural language processing to extract key information from
        a user's description of a WiFi issue and identify potential causes.
        
        Args:
            request: A dictionary containing:
                - description (str): Natural language description of the WiFi issue
                - network_id (str, optional): Network ID if available
                - max_issues (int, optional): Maximum number of issues to return (default: 10)
                - max_recommendations (int, optional): Maximum number of recommendations to return (default: 10)
                
        Returns:
            Dict containing analysis results with detected issues and recommendations
            
        Raises:
            Exception: If required parameters are missing
        """
        description = request.get("description")
        network_id = request.get("network_id")
        max_issues = request.get("max_issues", 10)
        max_recommendations = request.get("max_recommendations", 10)
        
        if not description:
            return {
                "status": "error",
                "message": "description is required"
            }
            
        try:
            # Import the troubleshooter if we haven't already
            if not hasattr(self, "_wifi_troubleshooter"):
                from meraki_mcp.wifi.wifi_troubleshooter import WifiTroubleshooter, WifiTroubleshootingError
                self._wifi_troubleshooter = WifiTroubleshooter()
                await self._wifi_troubleshooter.initialize_knowledge_base()
            
            # Use the WiFi troubleshooter to analyze the issue description
            result = await self._wifi_troubleshooter.troubleshoot_from_description(
                issue_description=description,
                network_id=network_id
            )
            
            # Check for large result sets and apply limits if needed
            issues = result.issues
            recommendations = result.recommendations
            knowledge_refs = result.knowledge_references
            
            # Log warning if we've exceeded limits and need to truncate
            if len(issues) > max_issues:
                logger.warning(f"Truncating issues from {len(issues)} to {max_issues}")
                issues = issues[:max_issues]
                
            if len(recommendations) > max_recommendations:
                logger.warning(f"Truncating recommendations from {len(recommendations)} to {max_recommendations}")
                recommendations = recommendations[:max_recommendations]
                
            # Convert troubleshooting result to API response
            response = {
                "status": "success",
                "description": description,
                "issues": [issue.to_dict() for issue in issues],
                "primary_issue": result.primary_issue.to_dict() if result.primary_issue else None,
                "confidence": result.confidence,
                "recommendations": recommendations,
                "knowledge_references": knowledge_refs[:5]  # Limit knowledge references to 5
            }
            
            # Add metadata about truncation if needed
            if len(result.issues) > max_issues or len(result.recommendations) > max_recommendations:
                response["truncated"] = True
                response["original_counts"] = {
                    "issues": len(result.issues),
                    "recommendations": len(result.recommendations)
                }
            
            return response
            
        except Exception as e:
            logger.error(f"Error analyzing WiFi description: {e}")
            return {
                "status": "error",
                "message": f"Error analyzing WiFi description: {str(e)}"
            }
            
    async def troubleshoot_wifi_issue(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Troubleshoot a WiFi issue based on natural language description.
        
        This tool analyzes a natural language description of a WiFi issue, extracts
        key information, and attempts to diagnose and resolve the issue by integrating
        with the WiFi knowledge base.
        
        The tool uses advanced text analysis to identify location references (e.g., room numbers,
        building names), device information, network identifiers, and other contextual data
        that might be helpful for troubleshooting.
        
        Args:
            request: A dictionary containing:
                - description (str): Natural language description of the WiFi issue
                - network_id (str, optional): Network ID if available
                - ssid_name (str, optional): SSID name if known
                - client_mac (str, optional): Client MAC address if issue is specific to a client
                - max_issues (int, optional): Maximum number of issues to return (default: 10)
                - max_recommendations (int, optional): Maximum number of recommendations to return (default: 10)
                - max_references (int, optional): Maximum number of knowledge references to return (default: 5)
                - include_all (bool, optional): Whether to include all results regardless of size (default: False)
                
        Returns:
            Dict containing troubleshooting results with detected issues and recommendations
            
        Raises:
            Exception: If required parameters are missing
        """
        description = request.get("description")
        network_id = request.get("network_id")
        ssid_name = request.get("ssid_name")
        client_mac = request.get("client_mac")
        
        # Extract contextual information from the description
        from meraki_mcp.utils.text_analysis import extract_context_from_query, detect_ambiguities, generate_clarification_questions
        query_context = None
        
        if description:
            query_context = extract_context_from_query(description)
            logger.info(f"Extracted context from query: {query_context.to_dict()}")
            
            # Check for ambiguities in the extracted context
            ambiguities = detect_ambiguities(query_context)
            if any(ambiguities.values()):
                # Generate clarification questions for ambiguous terms
                clarification_questions = generate_clarification_questions(ambiguities)
                
                # Add clarification questions to the response
                response["clarification_needed"] = True
                response["clarification_questions"] = clarification_questions
                logger.info(f"Requesting clarification for ambiguous terms: {ambiguities}")
            
            # Use extracted SSID if not provided explicitly
            if not ssid_name and query_context.ssid_names:
                ssid_name = query_context.ssid_names[0]
                logger.info(f"Using extracted SSID name: {ssid_name}")
        
        # Extract parameters for handling large result sets
        max_issues = request.get("max_issues", 10)
        max_recommendations = request.get("max_recommendations", 10)
        max_references = request.get("max_references", 5)
        include_all = request.get("include_all", False)
        
        if not description:
            return {
                "status": "error",
                "message": "description is required"
            }
            
        try:
            # Import the troubleshooter if we haven't already
            if not hasattr(self, "_wifi_troubleshooter"):
                from meraki_mcp.wifi.wifi_troubleshooter import WifiTroubleshooter, WifiTroubleshootingError
                self._wifi_troubleshooter = WifiTroubleshooter()
                await self._wifi_troubleshooter.initialize_knowledge_base()
            
            # If network_id and SSID name are provided, try to find the SSID number
            ssid_number = None
            ssid_data = {}
            
            if network_id and ssid_name:
                error_response = self._check_meraki_client()
                if not error_response:
                    try:
                        ssids = await self.get_wireless_ssids({"network_id": network_id})
                        if ssids.get("status") == "success":
                            for ssid in ssids.get("ssids", []):
                                if ssid.get("name") == ssid_name:
                                    ssid_number = ssid.get("number")
                                    ssid_data = ssid
                                    break
                    except Exception as e:
                        logger.warning(f"Could not retrieve SSID information: {e}")
            
            # If we have network_id and ssid_number, use the more comprehensive troubleshooting
            # Adding parameters to control result set size
            if network_id and ssid_number is not None:
                return await self.troubleshoot_ssid_connectivity({
                    "network_id": network_id,
                    "ssid_number": ssid_number,
                    "client_mac": client_mac,
                    "issue_description": description,
                    "max_issues": max_issues,
                    "max_recommendations": max_recommendations,
                    "include_all": include_all
                })
            
            # Extract potential SSID name from description if not provided
            if not ssid_name:
                import re
                ssid_match = re.search(r'(?:ssid|network|wifi)[:\s]+["\']?([A-Za-z0-9_-]+)["\']?', description.lower())
                if ssid_match:
                    extracted_ssid = ssid_match.group(1)
                    if network_id:
                        # Try to find this SSID in the network with pagination support
                        try:
                            ssids = await self.get_wireless_ssids({"network_id": network_id})
                            
                            # Log the number of SSIDs for troubleshooting large networks
                            if ssids.get("status") == "success" and len(ssids.get("ssids", [])) > 30:
                                logger.info(f"Large network with {len(ssids.get('ssids', []))} SSIDs")
                                
                            if ssids.get("status") == "success":
                                for ssid in ssids.get("ssids", []):
                                    if ssid.get("name", "").lower() == extracted_ssid.lower():
                                        return await self.troubleshoot_ssid_connectivity({
                                            "network_id": network_id,
                                            "ssid_number": ssid.get("number"),
                                            "client_mac": client_mac,
                                            "issue_description": description,
                                            "max_issues": max_issues,
                                            "max_recommendations": max_recommendations,
                                            "include_all": include_all
                                        })
                        except Exception as e:
                            logger.warning(f"Could not retrieve SSID information: {e}")
            
            # Before falling back to general analysis, check for relevant device information based on location
            # This helps identify potential APs in the area of concern (room, building, etc.)
            relevant_devices = []
            location_info = {}
            
            if network_id and query_context and (query_context.location_identifiers or 
                                              query_context.ap_identifiers or 
                                              query_context.building_identifiers):
                try:
                    # Get devices from this network
                    devices = self._meraki_client.get_network_devices(
                        network_id
                    )
                    
                    # Use our text analysis utility to find matching devices
                    from meraki_mcp.utils.text_analysis import find_matching_devices
                    
                    relevant_devices = find_matching_devices(
                        query_context,
                        devices,
                        match_device_types=True,
                        match_ap_identifiers=True
                    )
                    
                    if relevant_devices:
                        # Add location information to the response
                        location_info = {
                            "location_matches": [
                                {
                                    "device_name": device.get("name"),
                                    "device_serial": device.get("serial"),
                                    "device_model": device.get("model"),
                                    "matches": [
                                        {"type": "location", "value": loc_id}
                                        for loc_id in query_context.location_identifiers
                                    ] if query_context.location_identifiers else []
                                }
                                for device in relevant_devices[:5]  # Limit to 5 devices
                            ],
                            "search_criteria": {
                                "locations": query_context.location_identifiers,
                                "buildings": query_context.building_identifiers,
                                "aps": query_context.ap_identifiers
                            }
                        }
                        
                        response["location_info"] = location_info
                except Exception as e:
                    logger.warning(f"Could not retrieve device information for location analysis: {e}")
            
            # Check for client connectivity history if client_mac is provided
            if client_mac and network_id:
                try:
                    # Check client history to verify if there were actual connection attempts
                    timespan = request.get("timespan", 86400)  # Default to last 24 hours
                    client_history = self._meraki_client.get_network_wireless_client_connection_history(
                        network_id,
                        client_mac,
                        timespan=timespan
                    )
                    
                    # If no connection history is found, we need more information about timing
                    if not client_history:
                        return {
                            "status": "need_more_info",
                            "message": "No connection history found for this client. Please provide a specific time range when the connectivity issue occurred.",
                            "recommendations": [
                                "Specify a date and time when the connectivity issue was reported",
                                "Provide error messages or screenshots from the client device",
                                "Check if the client's WiFi is enabled and not in airplane mode"
                            ]
                        }
                except Exception as client_err:
                    logger.warning(f"Could not retrieve client connection history: {client_err}")
            
            # If we don't have enough information for detailed troubleshooting,
            # fall back to description-based analysis with the same limits for result set size
            return await self.analyze_wifi_description({
                "description": description,
                "network_id": network_id,
                "client_mac": client_mac,  # Pass client_mac for history verification
                "timespan": request.get("timespan", 86400),  # Default to last 24 hours
                "max_issues": max_issues,
                "max_recommendations": max_recommendations,
                "max_references": max_references
            })
            
        except Exception as e:
            logger.error(f"Error troubleshooting WiFi issue: {e}", exc_info=True)
            return {
                "status": "error",
                "message": f"Error troubleshooting WiFi issue: {str(e)}"
            }
    
    async def get_failed_connections(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Get failed wireless connection attempts and security logs.
        
        Retrieves a list of all failed client connection events on a network with details
        about the failure type, AP, client, and timestamp. Helps troubleshoot why clients
        might be failing to connect to the network.
        
        Args:
            request (Dict[str, Any]): Request containing:
                - network_id: The network ID
                - timespan (optional): Timespan in seconds (max 7 days)
                - t0 (optional): Start time (ISO 8601 format)
                - t1 (optional): End time (ISO 8601 format) 
                - band (optional): Filter by band (2.4, 5, or 6)
                - ssid (optional): Filter by SSID number
                - vlan (optional): Filter by VLAN
                - ap_tag (optional): Filter by AP tag
                - serial (optional): Filter by AP serial
                - client_id (optional): Filter by client MAC
        
        Returns:
            Dict[str, Any]: Failed connections with details about failure types and timestamps
        """
        network_id = request.get("network_id")
        if not network_id:
            return {
                "status": "error",
                "message": "network_id is required"
            }
        
        # Extract optional parameters
        timespan = request.get("timespan")
        t0 = request.get("t0")
        t1 = request.get("t1")
        band = request.get("band")
        ssid = request.get("ssid")
        vlan = request.get("vlan")
        ap_tag = request.get("ap_tag")
        serial = request.get("serial")
        client_id = request.get("client_id")
        
        try:
            # Build parameters dict, excluding None values
            params = {}
            if timespan is not None:
                params['timespan'] = timespan
            if t0 is not None:
                params['t0'] = t0
            if t1 is not None:
                params['t1'] = t1
            if band is not None:
                params['band'] = band
            if ssid is not None:
                params['ssid'] = ssid
            if vlan is not None:
                params['vlan'] = vlan
            if ap_tag is not None:
                params['apTag'] = ap_tag
            if serial is not None:
                params['serial'] = serial
            if client_id is not None:
                params['clientId'] = client_id
                
            logger.info(f"Getting failed connections for network {network_id} with parameters: {params}")
            
            # Use the wireless namespace to access the failedConnections endpoint
            # Note: pagination is handled internally by the SDK
            
            failed_connections = self._meraki_client.get_network_wireless_failed_connections(
                network_id,
                **params
            )
            
            total_connections = len(failed_connections)
            logger.info(f"Retrieved {total_connections} failed connection records")
            
            # Process and categorize the failed connections
            failure_types = {}
            failure_steps = {}
            
            for conn in failed_connections:
                failure_step = conn.get('failureStep', 'unknown')
                failure_type = conn.get('type', 'unknown')
                
                if failure_step not in failure_steps:
                    failure_steps[failure_step] = []
                failure_steps[failure_step].append(conn)
                
                if failure_type not in failure_types:
                    failure_types[failure_type] = []
                failure_types[failure_type].append(conn)
            
            return {
                "status": "success",
                "failed_connections": failed_connections,
                "failure_types": failure_types,
                "failure_steps": failure_steps,
                "total_count": total_connections
            }
            
        except Exception as e:
            logger.error(f"Error retrieving failed connections: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to retrieve connection logs: {str(e)}"
            }
    
    async def get_client_connectivity_events(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed wireless connectivity events for a specific client.
        
        Retrieves connection and disconnection events for a specific client, including
        reasons for disconnection, signal strength, and other connectivity metrics.
        
        Args:
            request (Dict[str, Any]): Request containing:
                - network_id: The network ID
                - client_id: Client MAC address
                - timespan (optional): Timespan in seconds
                - t0 (optional): Start time (ISO 8601 format)
                - t1 (optional): End time (ISO 8601 format)
                - per_page (optional): Results per page (default: 100)
                - total_pages (optional): Total pages to retrieve (-1 for all, default)
        
        Returns:
            Dict[str, Any]: Client connectivity events with connection/disconnection details
        """
        network_id = request.get("network_id")
        client_id = request.get("client_id")
        
        if not network_id or not client_id:
            return {
                "status": "error",
                "message": "Both network_id and client_id are required"
            }
        
        # Extract optional parameters
        timespan = request.get("timespan")
        t0 = request.get("t0")
        t1 = request.get("t1")
        per_page = request.get("per_page", 100)
        total_pages = request.get("total_pages", -1)  # Default to all pages
        
        try:
            # Build parameters dict, excluding None values
            params = {}
            if timespan is not None:
                params['timespan'] = timespan
            if t0 is not None:
                params['t0'] = t0
            if t1 is not None:
                params['t1'] = t1
            
            logger.info(f"Getting connectivity events for client {client_id} in network {network_id}")
            
            # Use the wireless namespace to access the client connectivity events endpoint
            # Note: pagination is handled internally by the SDK
            connectivity_events = self._meraki_client.get_network_wireless_client_connectivity_events(
                network_id,
                client_id,
                **params
            )
            
            total_events = len(connectivity_events)
            logger.info(f"Retrieved {total_events} connectivity events for client {client_id}")
            
            # Process events into categories for easier analysis
            connection_events = []
            disconnection_events = []
            roaming_events = []
            
            for event in connectivity_events:
                event_type = event.get('type')
                if event_type == 'connected':
                    connection_events.append(event)
                elif event_type == 'disconnected':
                    disconnection_events.append(event)
                elif event_type == 'roaming':
                    roaming_events.append(event)
            
            return {
                "status": "success",
                "connectivity_events": connectivity_events,
                "connection_events": connection_events,
                "disconnection_events": disconnection_events,
                "roaming_events": roaming_events,
                "total_count": total_events
            }
            
        except Exception as e:
            logger.error(f"Error retrieving client connectivity events: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to retrieve client connectivity events: {str(e)}"
            }
            
    async def troubleshoot_ssid_connectivity(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Troubleshoot connectivity issues with a specific SSID.
        
        This tool performs comprehensive troubleshooting on an SSID, checking for common
        issues like incorrect authentication settings, channel interference, AP coverage gaps,
        and client compatibility problems.
        
        Args:
            request: A dictionary containing:
                - network_id (str): Network ID
                - ssid_number (int): SSID number (0-14)
                - client_mac (str, optional): MAC address of a specific client having issues
                - issue_description (str, optional): Natural language description of the issue
        
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
        ssid_number = request.get("ssid_number")
        client_mac = request.get("client_mac")
        issue_description = request.get("issue_description")
        
        if not network_id:
            return {
                "status": "error",
                "message": "network_id is required"
            }
            
        if ssid_number is None:
            return {
                "status": "error",
                "message": "ssid_number is required"
            }
        
        try:
            # Support finding SSID by name if provided
            ssid_name = request.get("ssid_name")
            if ssid_name and not ssid_number:
                try:
                    ssids_response = await self.get_wireless_ssids({
                        "network_id": network_id
                    })
                    
                    if ssids_response.get("status") == "success":
                        ssids = ssids_response.get("ssids", [])
                        # Find the SSID number by name
                        for ssid in ssids:
                            if ssid.get("name") == ssid_name:
                                ssid_number = ssid.get("number")
                                break
                        
                        if not ssid_number:
                            return {
                                "status": "error",
                                "message": f"Could not find SSID with name: {ssid_name}"
                            }
                except Exception as e:
                    logger.error(f"Error finding SSID by name: {e}")
                    return {
                        "status": "error",
                        "message": f"Error finding SSID by name: {e}"
                    }
            
            # First, verify the SSID broadcasting status
            verification_result = await self.verify_ssid_status({
                "network_id": network_id,
                "ssid_number": ssid_number
            })
            
            if verification_result.get("status") == "error":
                return verification_result
            
            # Get SSID configuration details
            ssid_config = verification_result.get("ssid_config")
            ssid_name = ssid_config.get("name")
            
            # Check if we should use the WiFi troubleshooter for more comprehensive analysis
            if hasattr(self, "_wifi_troubleshooter") or issue_description:
                try:
                    # Import and initialize the troubleshooter if we haven't already
                    if not hasattr(self, "_wifi_troubleshooter"):
                        from meraki_mcp.wifi.wifi_troubleshooter import WifiTroubleshooter, WifiTroubleshootingError
                        self._wifi_troubleshooter = WifiTroubleshooter()
                        await self._wifi_troubleshooter.initialize_knowledge_base()
                    
                    # Gather client data if client_mac is provided
                    client_data = {}
                    if client_mac:
                        try:
                            # Get client connection history
                            client_history = self._meraki_client.get_network_wireless_client_connection_history(
                                network_id,
                                client_mac
                            )
                            client_data = {
                                "mac": client_mac,
                                "connection_history": client_history
                            }
                        except Exception as client_err:
                            logger.warning(f"Could not retrieve client connection history: {client_err}")
                    
                    # Use the troubleshooter to analyze the issue
                    troubleshooting_result = await self._wifi_troubleshooter.troubleshoot(
                        network_id=network_id,
                        ssid_data=ssid_config,
                        client_data=client_data,
                        issue_description=issue_description
                    )
                    
                    # If the troubleshooter found issues, return its results
                    if troubleshooting_result.issues:
                        return {
                            "status": "success",
                            "ssid_name": ssid_name,
                            "broadcasting": verification_result.get("broadcasting", False),
                            "issues": [issue.to_dict() for issue in troubleshooting_result.issues],
                            "primary_issue": troubleshooting_result.primary_issue.to_dict() if troubleshooting_result.primary_issue else None,
                            "confidence": troubleshooting_result.confidence,
                            "recommendations": troubleshooting_result.recommendations,
                            "knowledge_references": troubleshooting_result.knowledge_references,
                            "verification_result": verification_result
                        }
                except Exception as trouble_err:
                    logger.warning(f"Error using WiFi troubleshooter: {trouble_err}. Falling back to standard troubleshooting.")
            
            # If the SSID is not broadcasting, that's the first issue to fix
            if not verification_result.get("broadcasting", False):
                return {
                    "status": "warning",
                    "message": f"SSID '{verification_result.get('ssid_name')}' is not broadcasting",
                    "issues": ["SSID is not broadcasting"],
                    "recommendations": verification_result.get("recommendations", [
                        "Enable the SSID in the Meraki dashboard",
                        "Ensure access points are online and properly configured"
                    ]),
                    "verification_result": verification_result
                }
            
            # Initialize troubleshooting results
            issues = []
            recommendations = []
            detailed_checks = {}
            
            # 1. Check SSID Configuration - Focus on public OSD-Open setting issues
            ssid_enabled = ssid_config.get("enabled", False)
            if not ssid_enabled:
                issues.append("SSID is disabled")
                recommendations.append("Enable the SSID in the Meraki dashboard")
            
            # Store SSID name for reference
            ssid_name = ssid_config.get("name", "")
            detailed_checks["ssid_name"] = ssid_name
            
            # Check authentication settings
            auth_mode = ssid_config.get("authMode", "")
            detailed_checks["auth_mode"] = auth_mode
            
            # Check for Protected Management Frames (PMF) setting
            pmf_mode = ssid_config.get("pmf", "")
            detailed_checks["pmf_mode"] = pmf_mode
            
            # Check AP tag settings
            available_on_all_aps = ssid_config.get("availableOnAllAps", True)
            ap_tags = ssid_config.get("apTagsAndVirtualMacs", [])
            detailed_checks["available_on_all_aps"] = available_on_all_aps
            detailed_checks["ap_tags"] = ap_tags
            
            # Special handling for OSD-Open or other public SSIDs
            is_open_network = "OSD-Open" in ssid_name or "OPEN" in ssid_name or request.get("is_open_network", False)
            detailed_checks["is_open_network"] = is_open_network
            
            # Check authentication mode and PMF for public networks
            if is_open_network:
                # First check - is auth mode appropriate for an open network?
                if auth_mode not in ["open", "open-enhanced"]:
                    issues.append(f"SSID is named as open/public network but configured with {auth_mode} authentication")
                    recommendations.append("Change authentication mode to 'open' or 'open-enhanced' for public access points")
                
                # Second check - if using open-enhanced, is it causing compatibility issues?
                if auth_mode == "open-enhanced":
                    # Note: We should never recommend disabling open-enhanced as it's a critical security feature
                    # Instead, check if required PMF might be causing issues
                    if pmf_mode == "required":
                        issues.append("SSID is configured with required PMF which may cause issues with older clients")
                        recommendations.append("Consider changing PMF setting to 'optional' while maintaining 'open-enhanced' authentication")
                        detailed_checks["pmf_issue"] = True
                
                # Third check - is captive portal causing issues?
                splash_page = ssid_config.get("splashPage", "None")
                detailed_checks["splash_page"] = splash_page
                
                if splash_page != "None":
                    issues.append(f"SSID has a captive portal ({splash_page}) which might be causing connection issues")
                    recommendations.append("Review captive portal settings or temporarily disable to test connectivity")
                
                # Fourth check - AP tag verification for specific locations
                if not available_on_all_aps:
                    # Extract location from request if available (e.g., W23)
                    location_hint = None
                    if issue_description:
                        # Try to extract location information from the issue description
                        location_keywords = re.findall(r'\b[A-Z]\d+\b', issue_description)  # Pattern like W23, B45, etc.
                        if location_keywords:
                            location_hint = location_keywords[0]
                            detailed_checks["location_hint"] = location_hint
                    
                    # Get AP status information
                    ap_status_list = verification_result.get("ap_status", [])
                    detailed_checks["ap_count"] = len(ap_status_list)
                    
                    # First, check if we have AP tags that might match this location
                    location_tag_found = False
                    matching_tags = []
                    
                    for tag_entry in ap_tags:
                        tags = tag_entry.get("tags", [])
                        # Check for location-specific tags
                        if location_hint and any(location_hint in t for t in tags):
                            location_tag_found = True
                            matching_tags.append(tags)
                        # Check for OPEN tag which should be used for public SSIDs
                        if any("OPEN" in t.upper() for t in tags):
                            location_tag_found = True
                            matching_tags.append(tags)
                    
                    detailed_checks["matching_ap_tags"] = matching_tags
                    
                    # Second, verify if we have actual APs in the specified location
                    location_aps = []
                    if location_hint:
                        for ap in ap_status_list:
                            # Check if AP name or description contains the location hint
                            ap_name = ap.get("name", "")
                            ap_description = ap.get("description", "")
                            if location_hint in ap_name or location_hint in ap_description:
                                location_aps.append(ap)
                    
                    detailed_checks["location_aps"] = [ap.get("name") for ap in location_aps]
                    
                    # Third, check if any APs in the location are broadcasting this SSID
                    broadcasting_aps_in_location = [ap for ap in location_aps if ap.get("broadcasting_ssid", False)]
                    detailed_checks["broadcasting_aps_in_location"] = [ap.get("name") for ap in broadcasting_aps_in_location]
                    
                    # Now determine if there's an issue with AP tagging
                    if location_hint:
                        if not location_tag_found:
                            issues.append(f"SSID is not tagged for location {location_hint}")
                            recommendations.append(f"Add AP tag for {location_hint} to this SSID's configuration")
                            detailed_checks["ap_tag_missing"] = True
                        
                        if not location_aps:
                            issues.append(f"No access points found in location {location_hint}")
                            recommendations.append(f"Verify AP installation and network connection in {location_hint}")
                            detailed_checks["no_aps_in_location"] = True
                        
                        if location_aps and not broadcasting_aps_in_location:
                            issues.append(f"APs in {location_hint} are not broadcasting this SSID")
                            recommendations.append(f"Verify that APs in {location_hint} have the correct tags and are online")
                            detailed_checks["aps_not_broadcasting"] = True
            
            # 2. Check VLAN Assignment - Important for public networks
            vlan_id = ssid_config.get("defaultVlanId", None)
            detailed_checks["vlan_id"] = vlan_id
            
            if vlan_id is not None:
                # For public networks, verify proper VLAN configuration
                detailed_checks["vlan_check"] = "VLAN configuration present, but can't verify full VLAN setup via API"
                
                if is_open_network:
                    recommendations.append(f"Verify VLAN {vlan_id} is properly configured and has appropriate access restrictions for a public network")
                    recommendations.append("Check that VLAN {vlan_id} has proper routing and firewall rules")
            elif is_open_network:
                issues.append("Public network doesn't have a specific VLAN assigned")
                recommendations.append("Consider assigning a dedicated VLAN for public access to isolate from internal networks")
            
            # 3. Check DHCP Configuration - Critical for immediate connection failures
            ip_assignment_mode = ssid_config.get("ipAssignmentMode", "")
            detailed_checks["ip_assignment_mode"] = ip_assignment_mode
            
            dhcp_enabled = ip_assignment_mode in ["NAT mode", "Bridge mode", "Layer 3 roaming"]
            detailed_checks["dhcp_enabled"] = dhcp_enabled
            
            if not dhcp_enabled:
                issues.append("DHCP may not be properly configured for this SSID")
                recommendations.append("Verify DHCP is enabled and properly configured for this SSID")
            
            # For bridge mode, check if external DHCP is properly configured
            if ip_assignment_mode == "Bridge mode":
                issues.append("SSID is in Bridge mode - relies on external DHCP server")
                recommendations.append("Verify external DHCP server is properly configured and has available IP addresses")
                recommendations.append("Check DHCP server logs for any errors or capacity issues")
            
            # 4. Check AP Tags - Verify the AP has the correct tags for this SSID
            ap_tags_enabled = ssid_config.get("availableOnAllAps", True) is False
            detailed_checks["ap_tags_enabled"] = ap_tags_enabled
            
            if ap_tags_enabled:
                # If SSID is using tags, verify the specified AP has the correct tag
                ap_tags = ssid_config.get("apTagsAndVirtualMacs", [])
                detailed_checks["ap_tags"] = ap_tags
                
                # This would require checking the specific AP configuration
                issues.append("SSID is restricted to specific AP tags - verify AP has correct tag")
                recommendations.append("Confirm the AP is properly tagged for this SSID")
                
            # Check for recent failed connections
            try:
                # Get failed connections in the last 24 hours with proper pagination
                timespan = 86400
                failed_conn_response = await self.get_failed_connections({
                    "network_id": network_id,
                    "ssid": ssid_number,
                    "timespan": timespan
                })
                
                if failed_conn_response.get("status") == "success":
                    failures = failed_conn_response.get("failed_connections", [])
                    failure_steps = failed_conn_response.get("failure_steps", {})
                    detailed_checks["total_failures_24h"] = len(failures)
                    
                    # Check for DHCP failures - most common for immediate connection issues
                    if "dhcp" in failure_steps and len(failure_steps["dhcp"]) > 0:
                        dhcp_failures = len(failure_steps["dhcp"])
                        issues.append(f"Detected {dhcp_failures} DHCP failures in the last 24 hours")
                        recommendations.append("Check DHCP server configuration and capacity")
                        recommendations.append("Verify DHCP scope has available IP addresses")
                        detailed_checks["dhcp_failures"] = dhcp_failures
                    
                    # Check for authentication failures
                    if "auth" in failure_steps and len(failure_steps["auth"]) > 0:
                        auth_failures = len(failure_steps["auth"])
                        issues.append(f"Detected {auth_failures} authentication failures in the last 24 hours")
                        detailed_checks["auth_failures"] = auth_failures
                        
                        if auth_mode == "open":
                            recommendations.append("Verify that no captive portal or other authentication is inadvertently enabled")
                            if splash_page != "None":
                                recommendations.append("Check captive portal configuration or temporarily disable it")
                        else:
                            recommendations.append("Check authentication settings and credentials")
                    
                    # Check for association failures
                    if "assoc" in failure_steps and len(failure_steps["assoc"]) > 0:
                        assoc_failures = len(failure_steps["assoc"])
                        issues.append(f"Detected {assoc_failures} association failures in the last 24 hours")
                        detailed_checks["assoc_failures"] = assoc_failures
                        recommendations.append("Check AP radio settings and verify no MAC filtering is blocking clients")
                        
                    # Check for DNS failures (common after successful connection)
                    if "dns" in failure_steps and len(failure_steps["dns"]) > 0:
                        dns_failures = len(failure_steps["dns"])
                        issues.append(f"Detected {dns_failures} DNS failures in the last 24 hours")
                        detailed_checks["dns_failures"] = dns_failures
                        recommendations.append("Check DNS server configuration and verify it's accessible from the VLAN")
                        
            except Exception as e:
                logger.warning(f"Could not check for failed connections: {e}")
            
            # Check authentication settings
            if auth_mode in ["psk", "8021x-meraki"]:
                # Check if a specific client is having issues
                if client_mac:
                    # Try to find client connection history
                    client_history = None
                    try:
                        # Get client connection history
                    
                        client_history = self._meraki_client.wireless.getNetworkWirelessClientConnectionHistory(
                            network_id,
                            client_mac
                        )
                    except Exception as client_err:
                        logger.warning(f"Could not retrieve client connection history: {client_err}")
                    
                    if client_history:
                        auth_failures = [conn for conn in client_history if conn.get("failureReason") == "AUTHENTICATION_FAILURE"]
                        if auth_failures:
                            issues.append("Client has failed authentication attempts")
                            recommendations.append("Verify correct password/credentials are being used")
                            recommendations.append("Check client's supplicant configuration")
            
            # Check RF interference and channel utilization
            rf_profiles = None
            try:
                # Retrieve all RF profiles
                rf_profiles = self._meraki_client.get_network_wireless_rf_profiles(
                    network_id
                )
            except Exception as rf_err:
                logger.warning(f"Could not retrieve RF profiles: {rf_err}")
            
            if rf_profiles:
                # Check band selection settings
                for profile in rf_profiles:
                    if profile.get("bandSelectionType") == "5GHz only":
                        issues.append("Network is using 5GHz only band selection")
                        recommendations.append("Ensure client devices support 5GHz band")
            
            # Check for channel utilization issues
            for ap in verification_result.get("ap_status", []):
                if ap.get("broadcasting_ssid"):
                    try:
                        # Get channel utilization with proper timespan
                        utilization = self._meraki_client.get_device_wireless_channel_utilization(
                            ap.get("serial"),
                            timespan=3600  # Look at last hour
                        )
                        
                        # Look for high utilization
                        for channel_util in utilization:
                            if channel_util.get("utilization", {}).get("total", 0) > 70:
                                issues.append(f"High channel utilization on AP {ap.get('name')}")
                                recommendations.append("Consider changing channel width or channel selection")
                                recommendations.append("Add additional APs to distribute client load")
                                break
                    except Exception as util_err:
                        logger.warning(f"Could not retrieve channel utilization: {util_err}")
            
            # Check for client count and possible capacity issues
            client_counts = []
            for ap in verification_result.get("ap_status", []):
                if ap.get("broadcasting_ssid"):
                    try:
                        # Get wireless clients for this device
                        clients = self._meraki_client.get_device_wireless_clients(
                            ap.get("serial")
                        )
                        client_count = len(clients)
                        client_counts.append((ap.get("name"), client_count))
                        
                        if client_count > 25:  # Threshold for potential capacity issues
                            issues.append(f"High client count ({client_count}) on AP {ap.get('name')}")
                            recommendations.append("Consider adding additional APs to distribute client load")
                    except Exception as clients_err:
                        logger.warning(f"Could not retrieve clients for AP: {clients_err}")
            
            # If no specific issues found, provide general recommendations
            if not issues and verification_result.get("broadcasting"):
                recommendations.append("SSID appears to be broadcasting correctly and no common issues detected")
                recommendations.append("Check individual client device settings and compatibility")
                recommendations.append("Verify network firewall and DHCP settings")
            
            return {
                "status": "success",
                "ssid_name": ssid_config.get("name"),
                "broadcasting": verification_result.get("broadcasting"),
                "troubleshooting": {
                    "issues_found": len(issues) > 0,
                    "issues": issues,
                    "recommendations": recommendations
                },
                "ap_status": verification_result.get("ap_status"),
                "client_counts": client_counts if "client_counts" in locals() else [],
                "detailed_checks": detailed_checks,
                "ssid_config": ssid_config,
                "client_history": client_history if "client_history" in locals() else None
            }
            
        except Exception as e:
            logger.error(f"Error troubleshooting SSID connectivity: {e}")
            return {
                "status": "error",
                "message": f"Error troubleshooting SSID connectivity: {str(e)}"
            }
            
    async def get_wireless_status(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Get wireless status for all access points in a network.
        
        Args:
            request: A dictionary containing:
                - network_id (str): Network ID
        
        Returns:
            Dict containing wireless status for all access points
        
        Raises:
            Exception: If Meraki client is not initialized or required parameters are missing
        """
        error_response = self._check_meraki_client()
        if error_response:
            return error_response
            
        # Extract required parameters
        network_id = request.get("network_id")
        
        if not network_id:
            return {
                "status": "error",
                "message": "network_id is required"
            }
        
        try:
            # Get all wireless devices in the network
            devices = []
            try:
                # Retrieve all network devices
                devices = self._meraki_client.get_network_devices(
                    network_id
                )
                # Filter to get only wireless access points
                devices = [d for d in devices if d.get("model", "").startswith("MR")]
            except Exception as devices_err:
                logger.warning(f"Could not retrieve network devices: {devices_err}")
                return {
                    "status": "error",
                    "message": f"Could not retrieve network devices: {str(devices_err)}"
                }
            
            if not devices:
                return {
                    "status": "warning",
                    "message": "No wireless access points found in the network",
                    "devices": []
                }
            
            # Get the status of each access point
            ap_status = []
            
            for device in devices:
                device_serial = device.get("serial")
                
                if not device_serial:
                    continue
                    
                # Get the device wireless status
                device_status = None
                try:
                    device_status = self._meraki_client.get_device_wireless_status(device_serial)
                    ap_status.append({
                        "serial": device_serial,
                        "name": device.get("name"),
                        "model": device.get("model"),
                        "status": device_status.get("status", "Unknown"),
                        "ssids": device_status.get("ssids", []),
                        "clients": device_status.get("clients", {})
                    })
                except Exception as status_err:
                    logger.warning(f"Could not retrieve wireless status for device {device_serial}: {status_err}")
                    ap_status.append({
                        "serial": device_serial,
                        "name": device.get("name"),
                        "model": device.get("model"),
                        "status": "Error retrieving status",
                        "error": str(status_err)
                    })
            
            return {
                "status": "success",
                "ap_count": len(devices),
                "ap_status": ap_status
            }
            
        except Exception as e:
            logger.error(f"Error getting wireless status: {e}")
            return {
                "status": "error",
                "message": f"Error getting wireless status: {str(e)}"
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
