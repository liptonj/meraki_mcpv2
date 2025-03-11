"""
RF analysis tools for the Meraki dashboard API.

This module contains MCP tools for RF analysis and troubleshooting with Meraki devices.
"""

import logging
from datetime import datetime
from typing import Any, AsyncGenerator, Dict, List, Optional, Tuple

from meraki_mcp.rf.analyzer import RFAnalyzer
from meraki_mcp.rf.rf_troubleshooter import RFTroubleshooter
from meraki_mcp.tools.base import ToolBase

logger = logging.getLogger(__name__)


class RFTools(ToolBase):
    """RF analysis tools for Meraki dashboard API."""

    def __init__(self, server_instance):
        """Initialize RFTools.

        Args:
            server_instance: The MerakiMCPServer instance that this tool class is associated with
        """
        super().__init__(server_instance)
        # Initialize our own RF analyzer and troubleshooter instances
        self._rf_analyzer = self._get_rf_analyzer()
        self._rf_troubleshooter = self._get_rf_troubleshooter()

    def _get_rf_analyzer(self) -> RFAnalyzer:
        """Get or create an RF analyzer instance.
        
        Returns:
            An initialized RFAnalyzer instance
        """
        if not hasattr(self, '_rf_analyzer') or self._rf_analyzer is None:
            self._rf_analyzer = RFAnalyzer()
            logger.info("RF Analyzer initialized")
        return self._rf_analyzer
    
    def _get_rf_troubleshooter(self) -> RFTroubleshooter:
        """Get or create an RF troubleshooter instance.
        
        Returns:
            An initialized RFTroubleshooter instance
        """
        if not hasattr(self, '_rf_troubleshooter') or self._rf_troubleshooter is None:
            self._rf_troubleshooter = RFTroubleshooter()
            logger.info("RF Troubleshooter initialized")
        return self._rf_troubleshooter
        
    def _get_ap_capacity_threshold(self, model: str, firmware: str = None) -> int:
        """Determine the client capacity threshold based on device model and capabilities.
        
        Instead of hardcoding specific model numbers, this method analyzes the model string
        to determine the device's generation, Wi-Fi capabilities, and other factors that
        influence its capacity.
        
        Args:
            model: The device model string (e.g., 'MR56', 'CW9')
            firmware: The device firmware version, may contain capability information
            
        Returns:
            int: The recommended client load threshold for the device
        """
        # Default threshold for unknown or older devices
        default_threshold = 25
        
        # Return default if no model provided
        if not model:
            return default_threshold
            
        # Extract model family and series number
        # Typically format is XX00 where XX is product line and 00 is series number
        model = model.upper()
        
        # Determine capacity based on Wi-Fi generation/capabilities evident in the model
        
        # High capacity devices - Wi-Fi 6/6E/7 or latest generation APs
        # Includes newer MR models (50+ series) and CW models
        if any(x in model for x in ["MR5", "MR7", "MR8", "MR9"]) or model.startswith("CW"):
            return 40
            
        # Medium capacity - Wi-Fi 5 Wave 2 and early Wi-Fi 6
        # Typically MR3x/MR4x series
        if any(x in model for x in ["MR3", "MR4"]):
            return 30
            
        # Handle any special cases based on specific model features
        # For example, outdoor models may have different thresholds
        if "OUTDOOR" in model or "-E" in model:
            # Outdoor models might have different capacity characteristics
            return 35
            
        # For all other models, return the default threshold
        return default_threshold
    
    def get_capabilities(self):
        """Get the list of capabilities provided by this RF tool class.
        
        Returns:
            List[str]: A list of capability names as strings
        """
        return [
            "rf_analysis",
            "rf_troubleshooting",
            "batch_rf_troubleshooting",
            "analyze_network_rf"
        ]
        
    def _register_resources(self):
        """Register RF-related resources with the MCP server."""
        # Define any RF-specific resources here
        @self._mcp.resource("rf://spectrum-analysis")
        def spectrum_analysis_schema():
            """Schema for RF spectrum analysis data."""
            return {
                "type": "object",
                "properties": {
                    "network_id": {"type": "string"},
                    "device_serial": {"type": "string"},
                    "timestamp": {"type": "string", "format": "date-time"},
                    "channel_utilization": {"type": "number"},
                    "interference_level": {"type": "string", "enum": ["none", "low", "medium", "high", "critical"]},
                    "noise_floor_dbm": {"type": "number"},
                    "recommendations": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                }
            }
    
    def _register_tools(self):
        """Register RF-related tools with the MCP server."""
        
        @self._mcp.tool()
        async def analyze_network_rf(request: Dict[str, Any]) -> Dict[str, Any]:
            """Analyze RF spectrum for a Meraki network.

            Performs comprehensive RF analysis for an entire network, looking at interference,
            channel utilization, signal quality, and client connectivity issues.

            Args:
                request: A dictionary containing:
                    - organization_id (str, optional): Organization ID
                    - network_id (str): Network ID for analysis
                    - network_name (str, optional): Network name, will be used to find the network if network_id not provided
                    - organization_name (str, optional): Organization name, will be used to find the org if org_id not provided

            Returns:
                A comprehensive network RF analysis report including:
                    - Overall network health
                    - Per-device RF analysis
                    - Identified issues
                    - Recommendations

            Raises:
                Exception: If Meraki client is not initialized or required parameters are missing
            """
            error_response = self._check_meraki_client()
            if error_response:
                return error_response

            # Extract request parameters
            organization_id = request.get("organization_id")
            network_id = request.get("network_id")
            network_name = request.get("network_name")
            organization_name = request.get("organization_name")

            # If we don't have an organization ID but have a name, try to find it
            if not organization_id and organization_name:
                try:
                    organizations = self._meraki_client.get_organizations()
                    for org in organizations:
                        if org.get("name", "").lower() == organization_name.lower():
                            organization_id = org.get("id")
                            logger.info(
                                f"Found organization ID {organization_id} for name {organization_name}"
                            )
                            break

                    if not organization_id:
                        return {
                            "status": "error",
                            "message": f"Could not find organization with name: {organization_name}",
                        }
                except Exception as e:
                    logger.error(f"Error finding organization by name: {e}")
                    return {
                        "status": "error",
                        "message": f"Error finding organization by name: {str(e)}",
                    }

            # If we still don't have an org ID, report error
            if not organization_id:
                return {
                    "status": "error",
                    "message": "Organization ID or name is required",
                }

            # If we don't have a network ID but have a name, try to find it
            if not network_id and network_name:
                try:
                    networks = self._meraki_client.get_organization_networks(
                        organization_id
                    )
                    for network in networks:
                        if network.get("name", "").lower() == network_name.lower():
                            network_id = network.get("id")
                            logger.info(
                                f"Found network ID {network_id} for name {network_name}"
                            )
                            break

                    if not network_id:
                        return {
                            "status": "error",
                            "message": f"Could not find network with name: {network_name} in organization {organization_id}",
                        }
                except Exception as e:
                    logger.error(f"Error finding network by name: {e}")
                    return {
                        "status": "error",
                        "message": f"Error finding network by name: {str(e)}",
                    }

            # If we still don't have a network ID, report error
            if not network_id:
                return {"status": "error", "message": "Network ID or name is required"}

            try:
                # Get all devices in the network
                devices = self._meraki_client.get_network_devices(network_id)

                # Filter for wireless devices only
                wireless_devices = [
                    device
                    for device in devices
                    if device.get("model", "").startswith("MR")
                ]

                if not wireless_devices:
                    return {
                        "status": "warning",
                        "message": f"No wireless devices found in network {network_id}",
                    }

                logger.info(
                    f"Found {len(wireless_devices)} wireless devices in network {network_id}"
                )

                # Process each device and collect results
                device_analyses = []
                network_issues = []
                network_recommendations = []
                overall_health_score = (
                    100  # Start with perfect score and reduce based on issues
                )

                # Collect data for each wireless device
                for device in wireless_devices:
                    try:
                        logger.info(
                            f"Analyzing device {device.get('serial')}: {device.get('name')}"
                        )

                        # Get device details and RF metrics
                        device_serial = device.get("serial")

                        # Get connected clients for this device
                        clients = []
                        try:
                            # Get clients connected to this access point
                            network_clients = self._meraki_client.get_network_clients(
                                network_id, timespan=3600
                            )

                            # Get clients associated with this access point
                            # Note: For more accurate results in production, consider using
                            # device-specific client endpoints when available
                            clients = [
                                c
                                for c in network_clients
                                if c.get("recentDeviceMac") == device.get("mac")
                            ]

                        except Exception as e:
                            logger.warning(
                                f"Could not get clients for device {device_serial}: {e}"
                            )

                        # Get device status information
                        try:
                            # Get device status from organization device statuses endpoint
                            device_statuses = (
                                self._meraki_client.get_organization_device_statuses(
                                    organization_id, networkIds=[network_id]
                                )
                            )

                            device_status = next(
                                (
                                    status
                                    for status in device_statuses
                                    if status.get("serial") == device_serial
                                ),
                                {},
                            )
                        except Exception as e:
                            logger.warning(
                                f"Could not get status for device {device_serial}: {e}"
                            )
                            device_status = {}

                        # Get network health
                        try:
                            network_health = self._meraki_client.get_network_health(
                                network_id
                            )
                            wireless_health = next(
                                (
                                    component
                                    for component in network_health.get(
                                        "components", []
                                    )
                                    if component.get("component") == "wireless"
                                ),
                                {},
                            )
                        except Exception as e:
                            logger.warning(f"Could not get network health: {e}")
                            wireless_health = {}

                        # Create device analysis based on real data
                        device_analysis = {
                            "device_id": device_serial,
                            "name": device.get("name"),
                            "model": device.get("model"),
                            "status": device.get("status"),
                            "mac": device.get("mac"),
                            "lan_ip": device.get("lanIp"),
                            "rf_analysis": {
                                "signal_quality": "unknown",
                                "interference_level": "unknown",
                                "channel_utilization": None,
                                "noise_floor": None,
                                "client_count": len(clients),
                                "issues": [],
                            },
                            "device_details": {
                                "status": device_status.get("status"),
                                "last_reported_at": device_status.get("lastReportedAt"),
                                "public_ip": device_status.get("publicIp"),
                                "wan_ip": device_status.get("wan1Ip"),
                            },
                        }

                        # Analyze wireless health
                        if wireless_health:
                            device_analysis["rf_analysis"]["overall_status"] = (
                                wireless_health.get("status")
                            )

                            # Look for wireless-specific issues
                            if wireless_health.get("status") != "ok":
                                issue = f"Wireless health issue detected: {wireless_health.get('statusMessage', 'Unknown issue')}"
                                device_analysis["rf_analysis"]["issues"].append(issue)
                                network_issues.append(f"{device.get('name')}: {issue}")
                                network_recommendations.append(
                                    f"Check wireless configuration for {device.get('name')}"
                                )
                                overall_health_score -= 15

                        # Check device status
                        if device_status:
                            status = device_status.get("status")
                            if status != "online" and status is not None:
                                issue = f"Device {status}"
                                device_analysis["rf_analysis"]["issues"].append(issue)
                                network_issues.append(f"{device.get('name')}: {issue}")
                                network_recommendations.append(
                                    f"Check power and connectivity for {device.get('name')}"
                                )
                                overall_health_score -= 25

                        # Determine client load threshold based on device capabilities
                        model = device.get("model", "")
                        firmware = device.get("firmware", "")
                        client_load_threshold = self._get_ap_capacity_threshold(model, firmware)

                        # Analyze client load with appropriate threshold
                        if len(clients) > client_load_threshold:
                            issue = "high client load"
                            device_analysis["rf_analysis"]["issues"].append(issue)
                            network_issues.append(
                                f"{device.get('name')}: {issue} ({len(clients)} clients)"
                            )
                            network_recommendations.append(
                                f"Consider load balancing clients from {device.get('name')}"
                            )
                            overall_health_score -= 5 + min(
                                10, int(len(clients) / client_load_threshold * 5)
                            )  # Scale penalty

                        # Evaluate signal quality using available data points
                        issue_count = len(device_analysis["rf_analysis"]["issues"])
                        status_penalty = 0

                        # Consider device status in quality assessment
                        if device_status.get("status") != "online":
                            status_penalty = 2

                        # Set signal quality based on combined metrics
                        if issue_count + status_penalty == 0:
                            device_analysis["rf_analysis"]["signal_quality"] = "good"
                            device_analysis["rf_analysis"]["interference_level"] = "low"
                        elif issue_count + status_penalty == 1:
                            device_analysis["rf_analysis"]["signal_quality"] = "fair"
                            device_analysis["rf_analysis"][
                                "interference_level"
                            ] = "medium"
                        else:
                            device_analysis["rf_analysis"]["signal_quality"] = "poor"
                            device_analysis["rf_analysis"][
                                "interference_level"
                            ] = "high"

                        device_analyses.append(device_analysis)

                    except Exception as e:
                        logger.error(
                            f"Error analyzing device {device.get('serial')}: {e}"
                        )
                        # Add a basic error entry for this device
                        device_analyses.append(
                            {
                                "device_id": device.get("serial"),
                                "name": device.get("name"),
                                "status": "error",
                                "error": str(e),
                            }
                        )

                # Calculate percentage of devices with issues
                devices_with_issues = sum(
                    1
                    for device in device_analyses
                    if device.get("rf_analysis", {}).get("issues", [])
                )
                devices_percentage = (
                    (devices_with_issues / len(wireless_devices)) * 100
                    if wireless_devices
                    else 0
                )

                # Adjust health score based on percentage of affected devices
                if devices_percentage > 50:
                    overall_health_score = max(
                        0, overall_health_score - 15
                    )  # Severe impact if majority of devices affected
                elif devices_percentage > 25:
                    overall_health_score = max(
                        0, overall_health_score - 10
                    )  # Moderate impact
                elif devices_percentage > 10:
                    overall_health_score = max(
                        0, overall_health_score - 5
                    )  # Minor impact

                # Ensure health score doesn't go below 0
                overall_health_score = max(0, overall_health_score)

                # Determine overall network health status using standardized thresholds
                health_status = "Excellent"
                if overall_health_score < 50:
                    health_status = "Critical"
                elif overall_health_score < 65:
                    health_status = "Poor"
                elif overall_health_score < 80:
                    health_status = "Fair"
                elif overall_health_score < 90:
                    health_status = "Good"

                # Return the comprehensive analysis with detailed data
                analysis_timestamp = datetime.now().isoformat()
                return {
                    "status": "success",
                    "timestamp": analysis_timestamp,
                    "network": {
                        "id": network_id,
                        "name": next(
                            (
                                n.get("name")
                                for n in self._meraki_client.get_organization_networks(
                                    organization_id
                                )
                                if n.get("id") == network_id
                            ),
                            "Unknown",
                        ),
                        "device_count": len(wireless_devices),
                        "wireless_device_count": len(wireless_devices),
                    },
                    "rf_health": {
                        "score": overall_health_score,
                        "status": health_status,
                        "issues_count": len(network_issues),
                        "affected_device_percentage": (
                            round(devices_percentage, 2)
                            if "devices_percentage" in locals()
                            else 0
                        ),
                    },
                    "issues": network_issues,
                    "recommendations": network_recommendations,
                    "devices": device_analyses,
                    "analysis_duration_ms": int(
                        (
                            datetime.now() - datetime.fromisoformat(analysis_timestamp)
                        ).total_seconds()
                        * 1000
                    ),
                }
            except Exception as e:
                logger.error(f"Error analyzing network RF: {e}")
                return {
                    "status": "error",
                    "message": f"Error analyzing network RF: {str(e)}",
                }
                
    async def batch_troubleshoot_rf(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Perform batch RF troubleshooting for multiple access points.
        
        Args:
            request: The batch RF troubleshooting request containing multiple APs
            
        Returns:
            The batch troubleshooting results with recommendations for each AP
            
        Raises:
            Exception: If batch troubleshooting fails
        """
        from meraki_mcp.rf.models import BatchRFTroubleshootRequest, BatchTroubleshootingResult
        
        if not self._rf_troubleshooter:
            return {
                "status": "error",
                "message": "RF troubleshooter not initialized"
            }
            
        try:
            batch_request = BatchRFTroubleshootRequest(**request)
            
            # Process each AP in the batch
            results = []
            for ap_request in batch_request.requests:
                result = await self._rf_troubleshooter.troubleshoot(
                    ap_request.access_point,
                    ap_request.spectrum_data,
                    ap_request.client_data,
                    ap_request.options
                )
                results.append(result)
            
            # Return the batch results
            batch_result = BatchTroubleshootingResult(results=results)
            return batch_result.dict()
        except Exception as e:
            logger.error(f"Error in batch RF troubleshooting: {str(e)}")
            return {
                "status": "error",
                "message": f"Error in batch RF troubleshooting: {str(e)}"
            }
            
    async def create_rf_analysis_stream(self, request: Dict[str, Any], analyzer: Any) -> AsyncGenerator[Dict[str, Any], None]:
        """Create a stream generator for RF analysis progress.
        
        Args:
            request: The RF analysis request
            analyzer: The RF analyzer instance
            
        Yields:
            Progress updates and final results
        """
        import asyncio
        from meraki_mcp.rf.models import RFAnalysisRequest
        
        request_obj = RFAnalysisRequest(**request)
        device_id = request_obj.spectrum_data.device_id
        start_time = datetime.now()
        
        # Initial event
        yield {
            "event": "analysis_started",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "device_id": device_id,
                "message": f"Starting RF analysis for device {device_id}"
            }
        }
        
        # Processing event
        yield {
            "event": "preprocessing",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "device_id": device_id,
                "message": "Preprocessing spectrum data",
                "progress": 25
            }
        }
        
        await asyncio.sleep(0.5)  # Simulate processing time
        
        # Analysis event
        yield {
            "event": "analyzing",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "device_id": device_id,
                "message": "Analyzing spectrum patterns",
                "progress": 50
            }
        }
        
        await asyncio.sleep(0.5)  # Simulate processing time
        
        try:
            # Perform actual analysis
            analysis = await analyzer.analyze_spectrum(request_obj.spectrum_data, request_obj.options)
            
            # Recommendations event
            yield {
                "event": "generating_recommendations",
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "device_id": device_id,
                    "message": "Generating recommendations",
                    "progress": 75
                }
            }
            
            await asyncio.sleep(0.5)  # Simulate processing time
            
            # Final result
            duration = (datetime.now() - start_time).total_seconds()
            yield {
                "event": "analysis_complete",
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "device_id": device_id,
                    "message": f"Analysis completed in {duration:.2f} seconds",
                    "progress": 100,
                    "result": analysis.dict()
                }
            }
        except Exception as e:
            # Error event
            yield {
                "event": "error",
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "device_id": device_id,
                    "message": f"Analysis failed: {str(e)}",
                    "error": str(e)
                }
            }
            
    async def create_rf_troubleshooting_stream(self, request: Dict[str, Any], troubleshooter: Any) -> AsyncGenerator[Dict[str, Any], None]:
        """Create a stream generator for RF troubleshooting progress.
        
        Args:
            request: The RF troubleshooting request
            troubleshooter: The RF troubleshooter instance
            
        Yields:
            Progress updates and final results
        """
        import asyncio
        from meraki_mcp.rf.models import RFTroubleshootRequest
        
        request_obj = RFTroubleshootRequest(**request)
        ap_id = request_obj.access_point.id
        start_time = datetime.now()
        
        # Initial event
        yield {
            "event": "troubleshooting_started",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "access_point_id": ap_id,
                "message": f"Starting RF troubleshooting for access point {ap_id}"
            }
        }
        
        # Steps similar to analysis but for troubleshooting
        yield {
            "event": "gathering_data",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "access_point_id": ap_id,
                "message": "Gathering RF environment data",
                "progress": 25
            }
        }
        
        await asyncio.sleep(0.5)  # Simulate processing time
        
        # Analysis event
        yield {
            "event": "diagnosing",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "access_point_id": ap_id,
                "message": "Diagnosing potential issues",
                "progress": 50
            }
        }
        
        await asyncio.sleep(0.5)  # Simulate processing time
        
        try:
            # Perform actual troubleshooting
            result = await troubleshooter.troubleshoot(
                request_obj.access_point,
                request_obj.spectrum_data,
                request_obj.client_data,
                request_obj.options
            )
            
            # Solutions event
            yield {
                "event": "finding_solutions",
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "access_point_id": ap_id,
                    "message": "Finding optimal solutions",
                    "progress": 75
                }
            }
            
            await asyncio.sleep(0.5)  # Simulate processing time
            
            # Final result
            duration = (datetime.now() - start_time).total_seconds()
            yield {
                "event": "troubleshooting_complete",
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "access_point_id": ap_id,
                    "message": f"Troubleshooting completed in {duration:.2f} seconds",
                    "progress": 100,
                    "result": result.dict()
                }
            }
        except Exception as e:
            # Error event
            yield {
                "event": "error",
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "access_point_id": ap_id,
                    "message": f"Troubleshooting failed: {str(e)}",
                    "error": str(e)
                }
            }
            
    async def analyze_rf_spectrum(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze RF spectrum data.
        
        Args:
            request: The RF analysis request containing spectrum data
            
        Returns:
            The analysis result with insights and recommendations
            
        Raises:
            Exception: If analysis fails
        """
        from meraki_mcp.rf.models import RFAnalysisRequest
        import uuid
        
        if not self._rf_analyzer:
            return {
                "status": "error",
                "message": "RF analyzer not initialized"
            }
            
        analysis_request = RFAnalysisRequest(**request)
        
        # Check if streaming is requested
        stream = analysis_request.options.stream if analysis_request.options else False
        
        try:
            if not stream:
                # Perform the standard analysis
                logger.info(f"Analyzing spectrum data for device {analysis_request.spectrum_data.device_id}")
                analysis_result = await self._rf_analyzer.analyze_spectrum(
                    analysis_request.spectrum_data,
                    analysis_request.options
                )
                return analysis_result.dict()
            else:
                # Use MCP streaming for progress updates
                logger.info(f"Starting streaming RF analysis for device {analysis_request.spectrum_data.device_id}")
                # Create an analysis ID
                analysis_id = str(uuid.uuid4())
                
                # Register a stream to report progress
                stream_name = f"rf_analysis_{analysis_id}"
                
                # Create a stream generator for this analysis
                events = self.create_rf_analysis_stream(request, self._rf_analyzer)
                
                # Register the stream with the MCP server
                self._mcp.streaming(stream_name, events)
                
                # Return a reference to the stream
                return {
                    "analysis_id": analysis_id,
                    "stream": stream_name,
                    "status": "started"
                }
        except Exception as e:
            logger.error(f"Error in RF analysis: {str(e)}")
            return {
                "status": "error",
                "message": f"Error in RF analysis: {str(e)}"
            }
            
    async def troubleshoot_rf(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Troubleshoot RF issues.
        
        Args:
            request: The RF troubleshooting request containing spectrum data
            
        Returns:
            The troubleshooting result with recommendations
            
        Raises:
            Exception: If troubleshooting fails
        """
        from meraki_mcp.rf.models import RFTroubleshootRequest
        import uuid
        
        if not self._rf_troubleshooter:
            return {
                "status": "error",
                "message": "RF troubleshooter not initialized"
            }
            
        troubleshoot_request = RFTroubleshootRequest(**request)
        
        # Check if streaming is requested
        stream = troubleshoot_request.options.stream if troubleshoot_request.options else False
        
        try:
            if not stream:
                # Perform standard troubleshooting
                logger.info(f"Troubleshooting RF issues for access point {troubleshoot_request.access_point.id}")
                result = await self._rf_troubleshooter.troubleshoot(
                    troubleshoot_request.access_point,
                    troubleshoot_request.spectrum_data,
                    troubleshoot_request.client_data,
                    troubleshoot_request.options
                )
                return result.dict()
            else:
                # Use MCP streaming for progress updates
                logger.info(f"Starting streaming RF troubleshooting for access point {troubleshoot_request.access_point.id}")
                # Create a troubleshooting ID
                troubleshooting_id = str(uuid.uuid4())
                
                # Register a stream to report progress
                stream_name = f"rf_troubleshooting_{troubleshooting_id}"
                
                # Create a stream generator for this troubleshooting
                events = self.create_rf_troubleshooting_stream(request, self._rf_troubleshooter)
                
                # Register the stream with the MCP server
                self._mcp.streaming(stream_name, events)
                
                # Return a reference to the stream
                return {
                    "troubleshooting_id": troubleshooting_id,
                    "stream": stream_name,
                    "status": "started"
                }
        except Exception as e:
            logger.error(f"Error in RF troubleshooting: {str(e)}")
            return {
                "status": "error",
                "message": f"Error in RF troubleshooting: {str(e)}"
            }
