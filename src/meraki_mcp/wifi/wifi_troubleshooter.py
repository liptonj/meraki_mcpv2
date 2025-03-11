"""WiFi Troubleshooter module for Meraki MCP.

This module provides integration between WiFi troubleshooting and knowledge base systems
to automatically diagnose wireless issues and suggest remediation steps based on
WiFi network data and expert knowledge.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple, Union
import asyncio
import re

from meraki_mcp.knowledge.base import KnowledgeBaseError
from meraki_mcp.knowledge.wifi_kb import WifiKnowledgeBase

# Set up logging
logger = logging.getLogger(__name__)


class WifiTroubleshootingError(Exception):
    """Exception raised for errors during WiFi troubleshooting."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Initialize WifiTroubleshootingError.
        
        Args:
            message: Error message
            details: Additional details about the error
        """
        self.message = message
        self.details = details or {}
        super().__init__(message)


class WifiIssue:
    """Class representing a WiFi issue.
    
    Attributes:
        issue_type: Type of WiFi issue (e.g., "connectivity", "performance")
        issue_subtype: More specific issue type (e.g., "auth_failure", "channel_interference")
        severity: Issue severity (0-100)
        description: Detailed description of the issue
        affected_components: Components affected by the issue (e.g., "ssid", "client")
    """
    
    def __init__(
        self,
        issue_type: str,
        issue_subtype: str,
        severity: int,
        description: str,
        affected_components: List[str],
        validation_details: Optional[Dict[str, Any]] = None
    ):
        """Initialize WifiIssue.
        
        Args:
            issue_type: Type of WiFi issue
            issue_subtype: More specific issue type
            severity: Issue severity (0-100)
            description: Detailed description of the issue
            affected_components: Components affected by the issue
        """
        self.issue_type = issue_type
        self.issue_subtype = issue_subtype
        self.severity = severity
        self.description = description
        self.affected_components = affected_components
        self.validation_details = validation_details or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert the WiFi issue to a dictionary.
        
        Returns:
            Dictionary representation of the WiFi issue
        """
        return {
            "issue_type": self.issue_type,
            "issue_subtype": self.issue_subtype,
            "severity": self.severity,
            "description": self.description,
            "affected_components": self.affected_components,
            "validation_details": self.validation_details
        }


class TroubleshootingResult:
    """Class representing the results of WiFi troubleshooting.
    
    Attributes:
        issues: List of identified WiFi issues
        primary_issue: The most severe WiFi issue
        confidence: Confidence score (0-100) for the diagnosis
        recommendations: Recommended actions to resolve the issue
        knowledge_references: References to knowledge base articles
    """
    
    def __init__(
        self,
        issues: List[WifiIssue],
        confidence: int,
        recommendations: List[str],
        knowledge_references: List[Dict[str, str]],
        network_data: Optional[Dict[str, Any]] = None
    ):
        """Initialize TroubleshootingResult.
        
        Args:
            issues: List of identified WiFi issues
            confidence: Confidence score (0-100) for the diagnosis
            recommendations: Recommended actions to resolve the issue
            knowledge_references: References to knowledge base articles
            network_data: Optional raw network data used for diagnosis
        """
        self.issues = issues
        self.primary_issue = max(issues, key=lambda x: x.severity) if issues else None
        self.confidence = confidence
        self.recommendations = recommendations
        self.knowledge_references = knowledge_references
        self.network_data = network_data
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert the troubleshooting result to a dictionary.
        
        Returns:
            Dictionary representation of the troubleshooting result
        """
        return {
            "issues": [issue.to_dict() for issue in self.issues],
            "primary_issue": self.primary_issue.to_dict() if self.primary_issue else None,
            "confidence": self.confidence,
            "recommendations": self.recommendations,
            "knowledge_references": self.knowledge_references
        }


class WifiTroubleshooter:
    """Class for troubleshooting wireless issues using WiFi data and knowledge base.
    
    This class integrates diagnostic functionality with the WiFi knowledge base to
    automatically diagnose wireless issues and recommend remediation steps.
    """
    
    def __init__(self, kb_config: Optional[Dict[str, Any]] = None):
        """Initialize the WiFi Troubleshooter.
        
        Args:
            kb_config: Optional configuration for the knowledge base
        """
        self.knowledge_base = WifiKnowledgeBase(config=kb_config)
        self._kb_initialized = False
        logger.debug(
            "Initialized WifiTroubleshooter with kb_config: %s",
            kb_config
        )
    
    async def initialize_knowledge_base(self) -> None:
        """Initialize the knowledge base.
        
        This method must be called before using the troubleshooter.
        
        Returns:
            None
            
        Raises:
            WifiTroubleshootingError: If knowledge base initialization fails
        """
        if self._kb_initialized:
            return
            
        try:
            await self.knowledge_base.initialize()
            self._kb_initialized = True
            logger.info("Knowledge base initialized successfully")
        except KnowledgeBaseError as e:
            logger.error("Failed to initialize knowledge base: %s", str(e))
            raise WifiTroubleshootingError(
                f"Failed to initialize knowledge base: {str(e)}"
            )
    
    async def troubleshoot(
        self, 
        network_id: str, 
        ssid_data: Optional[Dict[str, Any]] = None,
        client_data: Optional[Dict[str, Any]] = None,
        issue_description: Optional[str] = None,
        meraki_client = None
    ) -> TroubleshootingResult:
        """Perform WiFi troubleshooting based on network, SSID, and client data.
        
        This method analyzes WiFi network data, identifies potential issues,
        and generates recommended solutions by combining analysis with knowledge
        base information.
        
        Args:
            network_id: Meraki network ID
            ssid_data: Optional SSID configuration and status data
            client_data: Optional client connection data
            issue_description: Optional natural language description of the issue
            
        Returns:
            TroubleshootingResult with the troubleshooting results
            
        Raises:
            WifiTroubleshootingError: If troubleshooting fails
        """
        if not self._kb_initialized:
            await self.initialize_knowledge_base()
            
        try:
            issues = []
            
            # Combine all data for analysis
            network_data = {
                "network_id": network_id,
                "ssid_data": ssid_data or {},
                "client_data": client_data or {},
                "issue_description": issue_description
            }
            
            # Step 1: Extract key information from the data
            logger.info(
                "Starting WiFi troubleshooting for network %s",
                network_id
            )
            
            # Step 2: Check for SSID-related issues
            ssid_issues = await self._check_ssid_issues(network_data)
            issues.extend(ssid_issues)
            
            # Step 3: Check for client-related issues
            client_issues = await self._check_client_issues(network_data)
            issues.extend(client_issues)
            
            # Step 4: Check access point configurations (if we have API access)
            if meraki_client:
                logger.info("Checking access point configurations")
                ap_issues = await self._check_ap_configurations(network_id, meraki_client, ssid_data)
                if ap_issues:
                    issues.extend(ap_issues)
                    logger.info(f"Found {len(ap_issues)} access point configuration issues")
                else:
                    logger.info("No AP configuration issues detected")
                
                # Step 5: Check connected clients (if we have API access)
                logger.info("Checking connected client details")
                client_connection_issues = await self._check_connected_clients(network_id, meraki_client, ssid_data)
                if client_connection_issues:
                    issues.extend(client_connection_issues)
                    logger.info(f"Found {len(client_connection_issues)} client connection issues")
                else:
                    logger.info("No client connection issues detected")
            
            # Step 6: If no specific issues found but we have a description, analyze it
            if not issues and issue_description:
                nlp_issues, extracted_context = await self._analyze_issue_description(issue_description)
                issues.extend(nlp_issues)
                network_data["extracted_context"] = extracted_context
                
            # Step 7: Validate detected issues with API calls if possible
            if meraki_client:
                logger.info(f"Validating {len(issues)} issues with API checks")
                validated_issues = []
                
                for issue in issues:
                    # Perform API validation
                    validation_result = await self._validate_with_api(issue, network_id, ssid_data, meraki_client)
                    
                    if validation_result["validated"]:
                        # Store validation details with the issue
                        issue.validation_details = validation_result["validation_details"]
                        
                        # Adjust issue severity based on API validation results
                        if "ssid_enabled" in validation_result["validation_details"]:
                            if issue.issue_subtype == "ssid_disabled" and validation_result["validation_details"]["ssid_enabled"]:
                                # If we thought SSID was disabled but API shows it's enabled, lower severity
                                issue.severity -= 30
                                logger.info(f"Reduced severity of issue {issue.issue_subtype} - API shows SSID is enabled")
                                
                        if "failed_connections" in validation_result["validation_details"]:
                            failed_conns = validation_result["validation_details"]["failed_connections"]
                            if failed_conns and len(failed_conns) > 0:
                                # If API confirms failed connections, increase severity
                                issue.severity += 10
                                issue.description += f" (Confirmed: {len(failed_conns)} failed connection attempts)"
                                logger.info(f"Increased severity of issue {issue.issue_subtype} - API confirmed {len(failed_conns)} failed connections")
                    
                    validated_issues.append(issue)
                
                # Replace original issues with validated ones
                issues = [issue for issue in validated_issues if issue.severity > 0]
                logger.info(f"After validation: {len(issues)} issues remain")
            
            # Step 6: Get recommendations from knowledge base
            knowledge_refs, recommendations = await self._get_recommendations(
                issues, network_data
            )
            
            # Step 6: Calculate confidence score
            confidence = self._calculate_confidence(issues, network_data)
            
            return TroubleshootingResult(
                issues=issues,
                confidence=confidence,
                recommendations=recommendations,
                knowledge_references=knowledge_refs,
                network_data=network_data
            )
            
        except KnowledgeBaseError as e:
            logger.error("Knowledge base query failed during troubleshooting: %s", str(e))
            raise WifiTroubleshootingError(
                f"Knowledge base query failed during troubleshooting: {str(e)}"
            )
        except Exception as e:
            logger.error("Unexpected error during WiFi troubleshooting: %s", str(e), exc_info=True)
            raise WifiTroubleshootingError(
                f"Unexpected error during WiFi troubleshooting: {str(e)}"
            )
    
    async def troubleshoot_from_description(
        self, 
        issue_description: str,
        network_id: Optional[str] = None
    ) -> TroubleshootingResult:
        """Perform WiFi troubleshooting based on a natural language description.
        
        This method is a convenience wrapper around the standard troubleshoot method
        that focuses on parsing the natural language description to identify issues.
        
        Args:
            issue_description: Natural language description of the issue
            network_id: Optional Meraki network ID
            
        Returns:
            TroubleshootingResult with the troubleshooting results
            
        Raises:
            WifiTroubleshootingError: If troubleshooting fails
        """
        return await self.troubleshoot(
            network_id=network_id or "unknown",
            issue_description=issue_description
        )
    
    async def _check_ssid_issues(self, network_data: Dict[str, Any]) -> List[WifiIssue]:
        """Check for SSID-related issues in the network data.
        
        Args:
            network_data: Network data including SSID information
            
        Returns:
            List of identified SSID-related issues
        """
        issues = []
        ssid_data = network_data.get("ssid_data", {})
        
        # Check if the SSID is enabled
        if not ssid_data.get("enabled", True):
            issues.append(WifiIssue(
                issue_type="configuration",
                issue_subtype="ssid_disabled",
                severity=90,
                description="The SSID is disabled in the network configuration",
                affected_components=["ssid"]
            ))
            return issues  # If SSID is disabled, that's the primary issue
        
        # Check if SSID is broadcasting
        if ssid_data.get("enabled", True) and not ssid_data.get("broadcasting", True):
            issues.append(WifiIssue(
                issue_type="connectivity",
                issue_subtype="ssid_not_broadcasting",
                severity=80,
                description="The SSID is enabled but not broadcasting",
                affected_components=["ssid", "access_points"]
            ))
        
        # Check for authentication issues (if available)
        auth_mode = ssid_data.get("authMode")
        
        # Safely handle potential None value for issue_description when checking open network issues
        issue_desc = network_data.get("issue_description")
        issue_desc_lower = issue_desc.lower() if issue_desc else ""
        
        # Check for Protected Management Frames (PMF) settings
        pmf_setting = ssid_data.get("dot11w", {})
        pmf_enabled = pmf_setting.get("enabled", False)
        pmf_required = pmf_setting.get("required", False)
        
        # Check for client compatibility issues mentioned in the description
        client_issues_mentioned = any(term in issue_desc_lower for term in 
                                     ["can't connect", "cannot connect", "unable to connect", 
                                      "compatibility", "older device", "legacy device"])
                                      
        # Check if auth mode is open-enhanced (which we should never disable, per user memory)
        is_open_enhanced = auth_mode == "open-enhanced"
        
        # If PMF is required and there are client connectivity issues
        if pmf_required and client_issues_mentioned:
            issues.append(WifiIssue(
                issue_type="compatibility",
                issue_subtype="pmf_required_compatibility",
                severity=75,
                description="Required Protected Management Frames (PMF) may cause compatibility issues with some clients",
                affected_components=["ssid", "clients", "security"],
                details={
                    "pmf_enabled": pmf_enabled,
                    "pmf_required": pmf_required,
                    "auth_mode": auth_mode
                }
            ))
        
        # If the SSID is using open-enhanced (which we should maintain) but reporting connectivity issues
        if is_open_enhanced and client_issues_mentioned:
            # We don't flag Open-Enhanced as an issue, but note that if there are client issues,
            # they might benefit from PMF being optional instead of required
            if pmf_required:
                issues.append(WifiIssue(
                    issue_type="compatibility",
                    issue_subtype="open_enhanced_pmf_config",
                    severity=70,
                    description="Open-Enhanced is correctly enabled (critical security feature), but PMF being required might cause compatibility issues",
                    affected_components=["ssid", "clients", "security"],
                    details={
                        "auth_mode": "open-enhanced",  # We explicitly note the correct mode
                        "pmf_required": True
                    }
                ))
        
        # Check availability tag restrictions
        availability_tags = ssid_data.get("availabilityTags", [])
        is_available_on_all_aps = ssid_data.get("availableOnAllAps", True)
        
        if availability_tags and not is_available_on_all_aps:
            issues.append(WifiIssue(
                issue_type="configuration",
                issue_subtype="restricted_ap_availability",
                severity=80,
                description=f"SSID is restricted to APs with tags: {', '.join(availability_tags)}",
                affected_components=["ssid", "access_points"],
                details={
                    "availability_tags": availability_tags,
                    "available_on_all_aps": False
                }
            ))
        
        # Check for WPA3-only configuration which might not be supported by all clients
        wpa_config = ssid_data.get("wpaConfig", {})
        encryption_mode = wpa_config.get("encryption", "")
        
        if auth_mode in ["wpa3", "wpa3-enterprise"] and client_issues_mentioned:
            issues.append(WifiIssue(
                issue_type="compatibility",
                issue_subtype="wpa3_only_compatibility",
                severity=70,
                description="WPA3-only mode may not be supported by all client devices",
                affected_components=["ssid", "clients", "security"],
                details={
                    "auth_mode": auth_mode,
                    "encryption": encryption_mode
                }
            ))
        
        # If using open authentication with client issues (not open-enhanced)
        if auth_mode == "open" and "open" in issue_desc_lower:
            issues.append(WifiIssue(
                issue_type="security",
                issue_subtype="open_network_issues",
                severity=60,
                description="Open network (not Open-Enhanced) may be causing connection issues with some client devices",
                affected_components=["ssid", "clients"]
            ))
        
        return issues
    
    async def _check_client_issues(self, network_data: Dict[str, Any]) -> List[WifiIssue]:
        """Check for client-related issues in the network data.
        
        Args:
            network_data: Network data including client information
            
        Returns:
            List of identified client-related issues
        """
        issues = []
        client_data = network_data.get("client_data", {})
        # Safely handle potential None value for issue_description
        issue_description_raw = network_data.get("issue_description")
        issue_description = issue_description_raw.lower() if issue_description_raw else ""
        
        # Check client connection status
        if client_data.get("status") == "failed":
            reason = client_data.get("failureReason", "unknown")
            
            if reason == "auth_failure":
                issues.append(WifiIssue(
                    issue_type="connectivity",
                    issue_subtype="authentication_failure",
                    severity=85,
                    description="Client failed to authenticate to the network",
                    affected_components=["client", "ssid"]
                ))
            elif reason == "dhcp_failure":
                issues.append(WifiIssue(
                    issue_type="connectivity",
                    issue_subtype="dhcp_failure",
                    severity=75,
                    description="Client failed to obtain an IP address via DHCP",
                    affected_components=["client", "dhcp"]
                ))
            else:
                issues.append(WifiIssue(
                    issue_type="connectivity",
                    issue_subtype="connection_failure",
                    severity=70,
                    description=f"Client connection failed with reason: {reason}",
                    affected_components=["client", "ssid"]
                ))
        
        # Check for signal strength issues
        if "signal" in client_data:
            signal_strength = client_data.get("signal")
            if signal_strength < -70:
                issues.append(WifiIssue(
                    issue_type="performance",
                    issue_subtype="low_signal_strength",
                    severity=60,
                    description=f"Client has poor signal strength: {signal_strength} dBm",
                    affected_components=["client", "access_points"]
                ))
        
        # Check for device compatibility issues based on description
        if ("mac" in issue_description and "windows" in issue_description) or "multiple devices" in issue_description:
            issues.append(WifiIssue(
                issue_type="compatibility",
                issue_subtype="cross_platform_issues",
                severity=65,
                description="Issue affects multiple device types, suggesting SSID configuration incompatibility",
                affected_components=["ssid", "clients"]
            ))
        
        return issues
    
    async def _analyze_issue_description(self, description: Optional[str]) -> Tuple[List[WifiIssue], Dict[str, Any]]:
        """Analyze natural language description to identify potential issues and extract key information.
        
        This method parses the description to identify WiFi issues and also extracts important
        contextual information such as location identifiers, device types, and network names.
        
        Args:
            description: Natural language description of the issue
            
        Returns:
            Tuple containing:
                - List of identified issues based on text analysis
                - Dictionary of extracted context information (locations, devices, etc.)
        """
        issues = []
        
        # Handle case where description might be None
        if description is None:
            description = ""
            
        description_lower = description.lower()
        
        # Initialize context extraction dictionary
        extracted_context = {
            "location_identifiers": [],
            "network_identifiers": [],
            "device_types": [],
            "ssid_names": [],
            "error_messages": [],
            "urgency_indicators": []
        }
        
        # Check for common connectivity issues
        if any(term in description_lower for term in ["can't connect", "cannot connect", "unable to connect", "unable to join"]):
            severity = 80
            issue_type = "connectivity"
            issue_subtype = "connection_failure"
            
            # Look for specific client indicators
            client_indicators = ["client", "device", "phone", "laptop", "computer", "user", 
                                "iphone", "android", "mac", "windows", "ios", "specific"]
            has_client_indicator = any(term in description_lower for term in client_indicators)
            
            # Refine based on additional context, prioritizing client issues
            if "password" in description_lower or "credentials" in description_lower:
                issue_subtype = "authentication_failure"
                description = "Specific clients are experiencing authentication failures when connecting" if has_client_indicator else "Clients are unable to connect due to possible authentication issues"
            elif "see the network" in description_lower or "find the network" in description_lower:
                issue_subtype = "ssid_not_visible"
                description = "Specific clients cannot see or find the wireless network" if has_client_indicator else "Clients cannot see or find the wireless network"
            elif "immediately" in description_lower and "error" in description_lower:
                issue_subtype = "immediate_connection_failure"
                description = "Specific clients immediately receive an error when trying to connect" if has_client_indicator else "Clients immediately receive an error when trying to connect"
                severity = 85
            elif has_client_indicator:
                issue_subtype = "client_specific_connection_failure"
                description = "Specific clients are unable to connect while others may be connecting successfully"
                severity = 82  # Slightly higher priority as it's client-specific
            else:
                description = "Clients are unable to connect to the wireless network"
            
            issues.append(WifiIssue(
                issue_type=issue_type,
                issue_subtype=issue_subtype,
                severity=severity,
                description=description,
                affected_components=["clients", "ssid"]
            ))
        
        # Check for performance issues
        elif any(term in description_lower for term in ["slow", "performance", "dropping", "intermittent"]):
            issues.append(WifiIssue(
                issue_type="performance",
                issue_subtype="poor_performance",
                severity=60,
                description="Network performance issues affecting client experience",
                affected_components=["clients", "access_points", "network"]
            ))
        
        # Check for specific SSID mention
        ssid_match = re.search(r'connect to ([A-Za-z0-9_-]+)', description_lower)
        if ssid_match:
            ssid_name = ssid_match.group(1)
            issues.append(WifiIssue(
                issue_type="connectivity",
                issue_subtype="ssid_specific_issue",
                severity=75,
                description=f"Issue specifically affects the '{ssid_name}' SSID",
                affected_components=["ssid"]
            ))
        
        # Extract specific device information
        if "mac" in description_lower:
            issues.append(WifiIssue(
                issue_type="compatibility",
                issue_subtype="mac_specific_issue",
                severity=50,
                description="Issue may be specific to Mac devices",
                affected_components=["clients"]
            ))
        if "windows" in description_lower:
            issues.append(WifiIssue(
                issue_type="compatibility",
                issue_subtype="windows_specific_issue",
                severity=50,
                description="Issue may be specific to Windows devices",
                affected_components=["clients"]
            ))
        
        # If multiple devices are affected, increase severity
        if "multiple devices" in description_lower or ("both" in description_lower and ("mac" in description_lower and "windows" in description_lower)):
            if issues:
                for issue in issues:
                    if issue.severity < 90:
                        issue.severity += 10
                    issue.description += " (affects multiple device types)"
        
        return issues
    
    async def _get_recommendations(
        self, 
        issues: List[WifiIssue],
        network_data: Dict[str, Any]
    ) -> Tuple[List[Dict[str, str]], List[str]]:
        """Get recommendations for resolving the identified issues.
        
        Args:
            issues: List of identified issues
            network_data: Network data used for analysis
            
        Returns:
            Tuple of (knowledge_references, recommendations)
        """
        recommendations = []
        knowledge_refs = []
        
        if not issues:
            # No specific issues found, provide general guidance
            recommendations.append(
                "No specific issues were identified. Consider checking the following:"
            )
            recommendations.append(
                "- Verify that the SSID is properly configured and enabled"
            )
            recommendations.append(
                "- Check that all access points are online and broadcasting the SSID"
            )
            recommendations.append(
                "- Ensure client devices have the correct security settings and credentials"
            )
            
            # Get general troubleshooting guidance from knowledge base
            topic_id = "troubleshooting_1"
            try:
                topic_content = await self.knowledge_base.get_topic_content(topic_id)
                if "references" in topic_content:
                    knowledge_refs.extend(topic_content["references"])
            except Exception as e:
                logger.warning(f"Error getting topic content: {str(e)}")
            
            return knowledge_refs, recommendations
        
        # Map issue subtypes to knowledge base topic IDs
        topic_mapping = {
            "ssid_disabled": "troubleshooting_1",
            "ssid_not_broadcasting": "troubleshooting_1",
            "authentication_failure": "troubleshooting_3",
            "dhcp_failure": "troubleshooting_3",
            "connection_failure": "troubleshooting_1",
            "low_signal_strength": "troubleshooting_2",
            "poor_performance": "troubleshooting_2",
            "cross_platform_issues": "troubleshooting_3",
            "open_network_issues": "best_practices_3"
        }
        
        # Critical configuration guidance - never recommend disabling Open-Enhanced
        # Open-Enhanced is a critical security feature that should always remain enabled
        open_enhanced_protected = True
        
        # Check if we're dealing with an open-enhanced network with connection issues
        ssid_data = network_data.get("ssid_data", {})
        auth_mode = ssid_data.get("authMode", "")
        is_open_enhanced = auth_mode == "open-enhanced"
        
        # Get recommendations for primary issue - handle case where no issues were found
        primary_issue = max(issues, key=lambda x: x.severity) if issues else None
        
        # Exit early if no issues were found
        if not primary_issue:
            return "No issues found that would require recommendations"
        
        # Add specific recommendations based on issue subtype
        if primary_issue.issue_subtype == "ssid_disabled":
            recommendations.append(
                "Enable the SSID in the Meraki dashboard"
            )
        elif primary_issue.issue_subtype == "ssid_not_broadcasting" or primary_issue.issue_subtype == "ssid_not_visible":
            # Check if it's a client-specific issue based on the description
            # Safely handle potential None value for description
            description = getattr(primary_issue, 'description', '')
            is_client_specific = "specific client" in description.lower() if description else False
            
            if is_client_specific:
                recommendations.append(
                    "Verify that the affected clients are within range of at least one access point"
                )
                recommendations.append(
                    "Check if the affected clients have the correct band capabilities (2.4GHz/5GHz/6GHz) for this SSID"
                )
                recommendations.append(
                    "Verify that client WiFi radios are enabled and not in airplane mode"
                )
                recommendations.append(
                    "Examine client WiFi scan logs to see what networks are visible to them"
                )
            else:
                recommendations.append(
                    "Verify that the SSID is configured to broadcast"
                )
                recommendations.append(
                    "Check that access points are online and properly configured"
                )
                recommendations.append(
                    "Verify that the SSID is configured on all expected access points"
                )
        elif primary_issue.issue_subtype == "authentication_failure" or primary_issue.issue_subtype == "client_specific_connection_failure":
            # Check if it's a client-specific issue based on the description
            # Safely handle potential None value for description
            description = getattr(primary_issue, 'description', '')
            is_client_specific = "specific client" in description.lower() if description else False
            
            if is_client_specific:
                recommendations.append(
                    "Verify that the affected clients have the correct credentials and are using the proper authentication method"
                )
                recommendations.append(
                    "Check if the affected clients have updated WiFi drivers and operating systems"
                )
                recommendations.append(
                    "Verify that the affected clients support the security protocols used by the SSID (e.g., WPA3, 802.1X)"
                )
                recommendations.append(
                    "Examine client device logs for WiFi-related errors during connection attempts"
                )
            else:
                recommendations.append(
                    "Verify that clients are using the correct password and authentication method"
                )
                recommendations.append(
                    "Ensure the SSID security settings are compatible with client devices"
                )
                recommendations.append(
                    "Check for RADIUS server issues if using enterprise authentication"
                )
        elif primary_issue.issue_subtype == "dhcp_failure":
            recommendations.append(
                "Verify that DHCP server is functioning properly"
            )
            recommendations.append(
                "Check that the DHCP scope is not exhausted"
            )
            recommendations.append(
                "Ensure that there are no IP conflicts on the network"
            )
        elif primary_issue.issue_subtype == "open_network_issues":
            # Note: We should never recommend disabling Open-Enhanced as it's a critical security feature
            # Instead, focus on AP verification and PMF settings
            
            recommendations.append(
                "First verify that access points in the client's location are properly tagged for this SSID"
            )
            
            if is_open_enhanced:
                recommendations.append(
                    "For client compatibility issues, consider changing PMF setting to 'optional' while maintaining 'open-enhanced' authentication"
                )
            else:
                recommendations.append(
                    "Check if the client device has any security policies that block connections to public networks"
                )
                
            recommendations.append(
                "Verify that the client's MAC address is not blocked by any firewall or access control rules"
            )
        elif primary_issue.issue_subtype == "immediate_connection_failure":
            # Check if it's a client-specific issue based on the description
            # Safely handle potential None value for description
            description = getattr(primary_issue, 'description', '')
            is_client_specific = "specific client" in description.lower() if description else False
            
            if is_client_specific:
                recommendations.append(
                    "Check the affected client's ability to connect to other WiFi networks"
                )
                recommendations.append(
                    "Verify the affected client is not blocked by MAC filtering or firewall rules"
                )
                recommendations.append(
                    "Try resetting the WiFi network adapter on the affected device(s)"
                )
                recommendations.append(
                    "Examine client device logs for detailed error messages during connection attempts"
                )
                recommendations.append(
                    "Verify client device supports the WiFi standards used by this SSID (e.g., 802.11ac/ax)"
                )
            else:
                recommendations.append(
                    "Verify the SSID broadcast is enabled and access points are online"
                )
                recommendations.append(
                    "Check for MAC address filtering or other access control settings"
                )
                recommendations.append(
                    "Ensure client devices support the SSID security type and WiFi standards"
                )
        
        # Get additional recommendations from knowledge base
        try:
            # Get the appropriate topic content based on issue subtype
            topic_id = topic_mapping.get(primary_issue.issue_subtype, "troubleshooting_1")
            topic_content = await self.knowledge_base.get_topic_content(topic_id)
            
            # Add knowledge base topic as a reference
            if "references" in topic_content:
                knowledge_refs.extend(topic_content["references"])
            
            # Query the knowledge base with a natural language question
            issue_description = primary_issue.description
            kb_query = f"How to resolve issue where {issue_description} in Meraki wireless networks?"
            kb_results = await self.knowledge_base.query(kb_query)
            
            if kb_results and "answer" in kb_results and kb_results["answer"]:
                answer = kb_results["answer"]
                # Safety check for Open-Enhanced in knowledge base answers
                if any(term in answer.lower() for term in ["disable open-enhanced", "turn off open-enhanced", 
                                                      "disable open enhanced", "turn off open enhanced",
                                                      "removing open-enhanced", "removing open enhanced"]):
                    logger.warning(f"Filtered out knowledge base answer recommending to disable Open-Enhanced")
                    # Replace with safe guidance
                    modified_answer = "Ensure that Open-Enhanced is enabled on the wireless network. This is a critical feature that should always remain enabled."
                    recommendations.append(modified_answer)
                else:
                    recommendations.append(answer)
            
            if kb_results and "topics" in kb_results:
                for topic in kb_results["topics"]:
                    if "id" in topic:
                        try:
                            additional_content = await self.knowledge_base.get_topic_content(topic["id"])
                            if "references" in additional_content:
                                for ref in additional_content["references"]:
                                    if ref not in knowledge_refs:
                                        knowledge_refs.append(ref)
                        except Exception as e:
                            logger.warning(f"Error getting additional topic content: {str(e)}")
                            
        except Exception as e:
            logger.warning(f"Error querying knowledge base: {str(e)}")
        
        # De-duplicate recommendations
        unique_recommendations = []
        for rec in recommendations:
            if rec not in unique_recommendations:
                unique_recommendations.append(rec)
        
        # CRITICAL PROTECTION: Filter out any recommendations related to disabling Open-Enhanced
        safe_recommendations = []
        for rec in unique_recommendations:
            # Skip any recommendation suggesting to disable Open-Enhanced
            if any(term in rec.lower() for term in ["disable open-enhanced", "turn off open-enhanced", 
                                                  "disable open enhanced", "turn off open enhanced",
                                                  "removing open-enhanced", "removing open enhanced"]):
                logger.warning(f"Filtered out recommendation to disable Open-Enhanced: {rec}")
                continue
            # If recommendation relates to Open-Enhanced configuration but doesn't suggest disabling it
            elif any(term in rec.lower() for term in ["open-enhanced", "open enhanced"]):
                # Add explicit statement to always keep it enabled
                modified_rec = f"{rec} (Note: Open-Enhanced should always remain enabled)"
                safe_recommendations.append(modified_rec)
            else:
                safe_recommendations.append(rec)
        
        # Add a positive recommendation about Open-Enhanced if any recommendations were filtered
        if len(safe_recommendations) < len(unique_recommendations):
            safe_recommendations.append("Maintain Open-Enhanced configuration as enabled - this is a critical feature that should always remain active")
            
        return knowledge_refs, safe_recommendations
    
    async def _check_ap_configurations(self, network_id: str, meraki_client, ssid_data: Optional[Dict[str, Any]] = None) -> List[WifiIssue]:
        """Check access point configurations for potential issues.
        
        This method examines access points in the network to identify configuration issues
        that might affect connectivity, such as:
        - APs with the wrong tags for SSID availability
        - APs that are offline or in a problematic state
        - APs with firmware issues
        - APs with incorrect radio settings
        
        Args:
            network_id: Meraki network ID
            meraki_client: Initialized Meraki API client
            ssid_data: Optional SSID configuration data
            
        Returns:
            List of identified AP-related issues
        """
        issues = []
        
        if not meraki_client:
            logger.warning("No Meraki client provided for AP configuration check")
            return issues
            
        try:
            # Get all devices in the network
            aps = await meraki_client.get_network_devices(network_id)
            wireless_aps = [ap for ap in aps if ap.get("model", "").startswith("MR")]
            
            if not wireless_aps:
                # No wireless APs found in the network
                issues.append(WifiIssue(
                    issue_type="configuration",
                    issue_subtype="no_wireless_aps",
                    severity=90,
                    description="No wireless access points detected in the network",
                    affected_components=["access_points", "network"]
                ))
                return issues
                
            # Check for offline APs
            offline_aps = [ap for ap in wireless_aps if ap.get("status") != "online"]
            if offline_aps:
                issues.append(WifiIssue(
                    issue_type="connectivity",
                    issue_subtype="offline_access_points",
                    severity=85,
                    description=f"{len(offline_aps)} access points are offline or in problematic state",
                    affected_components=["access_points"],
                    details={"offline_aps": [ap.get("name", ap.get("serial", "Unknown")) for ap in offline_aps]}
                ))
            
            # If SSID data is provided, check AP availability tags
            if ssid_data:
                # Check if SSID is restricted to specific AP tags
                ap_tags_required = ssid_data.get("availabilityTags", [])
                is_available_on_all_aps = ssid_data.get("availableOnAllAps", True)
                
                if ap_tags_required and not is_available_on_all_aps:
                    # Count APs with each required tag
                    aps_with_required_tags = 0
                    missing_tag_aps = []
                    
                    for ap in wireless_aps:
                        ap_tags = ap.get("tags", [])
                        # Check if this AP has any of the required tags
                        if not any(tag in ap_tags for tag in ap_tags_required):
                            missing_tag_aps.append(ap.get("name", ap.get("serial", "Unknown")))
                        else:
                            aps_with_required_tags += 1
                    
                    # If no APs have the required tags
                    if aps_with_required_tags == 0:
                        issues.append(WifiIssue(
                            issue_type="configuration",
                            issue_subtype="no_aps_with_required_tags",
                            severity=90,
                            description=f"SSID requires APs with tags {ap_tags_required}, but no APs have these tags",
                            affected_components=["access_points", "ssid"],
                            details={"required_tags": ap_tags_required}
                        ))
                    # If some APs are missing required tags
                    elif missing_tag_aps and aps_with_required_tags < len(wireless_aps):
                        issues.append(WifiIssue(
                            issue_type="configuration",
                            issue_subtype="some_aps_missing_required_tags",
                            severity=75,
                            description=f"Some APs are missing the required tags {ap_tags_required} for SSID availability",
                            affected_components=["access_points", "ssid"],
                            details={
                                "required_tags": ap_tags_required,
                                "aps_without_tags": missing_tag_aps,
                                "aps_with_tags": aps_with_required_tags,
                                "total_aps": len(wireless_aps)
                            }
                        ))
                        
            # For at least one AP, get detailed radio status
            if wireless_aps:
                try:
                    sample_ap = wireless_aps[0]
                    ap_wireless_status = await meraki_client.get_device_wireless_status(sample_ap["serial"])
                    
                    # Check for channel utilization issues
                    for radio in ap_wireless_status.get("radios", []):
                        if radio.get("status") != "normal":
                            issues.append(WifiIssue(
                                issue_type="performance",
                                issue_subtype="radio_status_issue",
                                severity=70,
                                description=f"AP radio ({radio.get('band', 'unknown')}) status is {radio.get('status', 'abnormal')}",
                                affected_components=["access_points", "radio"]
                            ))
                            
                        # Check utilization (if available)
                        utilization = radio.get("channelUtilization")
                        if utilization and utilization > 70:  # High utilization threshold
                            issues.append(WifiIssue(
                                issue_type="performance",
                                issue_subtype="high_channel_utilization",
                                severity=65,
                                description=f"High channel utilization ({utilization}%) on {radio.get('band', 'unknown')} radio",
                                affected_components=["access_points", "radio", "channel"]
                            ))
                except Exception as e:
                    logger.warning(f"Error checking AP radio status: {e}")
                    
        except Exception as e:
            logger.error(f"Error checking AP configurations: {e}")
            
        return issues
        
    async def _check_connected_clients(self, network_id: str, meraki_client, ssid_data: Optional[Dict[str, Any]] = None) -> List[WifiIssue]:
        """Check connected clients for potential issues.
        
        This method examines clients connected to the wireless network to identify
        connection issues, performance problems, or other client-related issues.
        
        Args:
            network_id: Meraki network ID
            meraki_client: Initialized Meraki API client
            ssid_data: Optional SSID configuration data
            
        Returns:
            List of identified client-related issues
        """
        issues = []
        
        if not meraki_client:
            logger.warning("No Meraki client provided for connected clients check")
            return issues
        
        try:
            # Get connected clients
            clients = await meraki_client.get_network_clients(network_id)
            
            # Filter to only wireless clients if possible
            wireless_clients = [c for c in clients if c.get("ssid") is not None]
            
            # If no wireless clients found
            if not wireless_clients and ssid_data:
                # This might indicate clients can't connect to this SSID
                ssid_name = ssid_data.get("name", "Unknown SSID")
                issues.append(WifiIssue(
                    issue_type="connectivity",
                    issue_subtype="no_connected_clients",
                    severity=80,
                    description=f"No clients are connected to the '{ssid_name}' SSID",
                    affected_components=["ssid", "clients"]
                ))
                
                # Check failed connections to see if clients tried to connect but failed
                try:
                    failed_connections = await meraki_client.get_network_wireless_failed_connections(network_id)
                    if failed_connections and len(failed_connections) > 0:
                        # Analyze failure reasons
                        auth_failures = [fc for fc in failed_connections if "auth" in fc.get("failureReason", "").lower()]
                        dhcp_failures = [fc for fc in failed_connections if "dhcp" in fc.get("failureReason", "").lower()]
                        assoc_failures = [fc for fc in failed_connections if "association" in fc.get("failureReason", "").lower()]
                        
                        if auth_failures:
                            issues.append(WifiIssue(
                                issue_type="connectivity",
                                issue_subtype="authentication_failures",
                                severity=85,
                                description=f"{len(auth_failures)} clients failed to authenticate to the network",
                                affected_components=["ssid", "clients", "authentication"],
                                details={"count": len(auth_failures)}
                            ))
                            
                        if dhcp_failures:
                            issues.append(WifiIssue(
                                issue_type="connectivity",
                                issue_subtype="dhcp_failures",
                                severity=80,
                                description=f"{len(dhcp_failures)} clients failed to obtain IP addresses via DHCP",
                                affected_components=["ssid", "clients", "dhcp"],
                                details={"count": len(dhcp_failures)}
                            ))
                            
                        if assoc_failures:
                            issues.append(WifiIssue(
                                issue_type="connectivity",
                                issue_subtype="association_failures",
                                severity=75,
                                description=f"{len(assoc_failures)} clients failed to associate with the wireless network",
                                affected_components=["ssid", "clients", "radio"],
                                details={"count": len(assoc_failures)}
                            ))
                except Exception as e:
                    logger.warning(f"Error checking failed connections: {e}")
            
            # If we have wireless clients, analyze them
            elif wireless_clients:
                # Check for clients with poor signal strength
                poor_signal_clients = [c for c in wireless_clients if c.get("signal", 0) < -70]
                if poor_signal_clients and len(poor_signal_clients) > 0:
                    issues.append(WifiIssue(
                        issue_type="performance",
                        issue_subtype="poor_signal_strength",
                        severity=65,
                        description=f"{len(poor_signal_clients)} clients have poor signal strength (< -70 dBm)",
                        affected_components=["clients", "access_points", "signal"],
                        details={"count": len(poor_signal_clients)}
                    ))
                
                # Check for clients on older data rates or standards
                legacy_clients = [c for c in wireless_clients if c.get("protocol") in ["802.11b", "802.11g", "802.11a"]]
                if legacy_clients and len(legacy_clients) > 0:
                    issues.append(WifiIssue(
                        issue_type="performance",
                        issue_subtype="legacy_clients",
                        severity=60,
                        description=f"{len(legacy_clients)} clients are using older 802.11 standards",
                        affected_components=["clients", "performance"],
                        details={"count": len(legacy_clients)}
                    ))
                    
                # If SSID data available, check if clients are using the specific SSID
                if ssid_data and "name" in ssid_data:
                    ssid_name = ssid_data["name"]
                    ssid_clients = [c for c in wireless_clients if c.get("ssid") == ssid_name]
                    
                    if not ssid_clients:
                        # No clients on this specific SSID
                        issues.append(WifiIssue(
                            issue_type="connectivity",
                            issue_subtype="no_clients_on_ssid",
                            severity=75,
                            description=f"No clients are connected to the '{ssid_name}' SSID specifically",
                            affected_components=["ssid", "clients"]
                        ))
        
        except Exception as e:
            logger.error(f"Error checking connected clients: {e}")
            
        return issues

    async def _validate_with_api(
        self, 
        issue: WifiIssue,
        network_id: str,
        ssid_data: Optional[Dict[str, Any]],
        meraki_client
    ) -> Dict[str, Any]:
        """Validate troubleshooting issues with API calls to confirm the diagnosis.
        
        Args:
            issue: The issue to validate
            network_id: Meraki network ID
            ssid_data: SSID configuration and status data
            meraki_client: Initialized Meraki API client
            
        Returns:
            Dictionary with validation results
        """
        validation_results = {
            "validated": False,
            "validation_details": {}
        }
        
        if not meraki_client:
            logger.warning("No Meraki client provided for API validation")
            return validation_results
            
        try:
            # Validate different issues with specific API calls
            if issue.issue_subtype == "ssid_disabled" or issue.issue_subtype == "ssid_not_broadcasting":
                # Check if SSID is actually disabled or not broadcasting
                if ssid_data and "number" in ssid_data:
                    ssid_number = ssid_data.get("number")
                    # Get current SSID configuration
                    ssid_details = await meraki_client.get_network_wireless_ssid(network_id, ssid_number)
                    validation_results["validation_details"]["ssid_enabled"] = ssid_details.get("enabled", False)
                    validation_results["validation_details"]["ssid_visible"] = not ssid_details.get("hidden", False)
                    validation_results["validated"] = True
            
            elif issue.issue_subtype == "authentication_failure":
                # Validate authentication settings
                if ssid_data and "number" in ssid_data:
                    ssid_number = ssid_data.get("number")
                    # Get current SSID configuration
                    ssid_details = await meraki_client.get_network_wireless_ssid(network_id, ssid_number)
                    validation_results["validation_details"]["auth_type"] = ssid_details.get("authMode")
                    if "radiusServers" in ssid_details:
                        validation_results["validation_details"]["radius_configured"] = True
                    validation_results["validated"] = True
            
            elif "performance" in issue.issue_type:
                # Check AP performance data
                try:
                    aps = await meraki_client.get_network_devices(network_id)
                    wireless_aps = [ap for ap in aps if ap.get("model", "").startswith("MR")]
                    if wireless_aps:
                        # Get utilization data for a sample AP
                        sample_ap = wireless_aps[0]
                        ap_status = await meraki_client.get_device_wireless_status(sample_ap["serial"])
                        validation_results["validation_details"]["ap_status"] = ap_status
                        validation_results["validated"] = True
                except Exception as e:
                    logger.warning(f"Error validating AP performance: {e}")
            
            elif issue.issue_subtype == "client_specific_connection_failure":
                # Check for failed client connections
                try:
                    # Get failed connections
                    failed_connections = await meraki_client.get_network_wireless_failed_connections(network_id)
                    validation_results["validation_details"]["failed_connections"] = failed_connections
                    validation_results["validated"] = True
                except Exception as e:
                    logger.warning(f"Error checking failed connections: {e}")
        
        except Exception as e:
            logger.error(f"Error during API validation: {e}")
        
        return validation_results
    
    def _calculate_confidence(
        self, 
        issues: List[WifiIssue],
        network_data: Dict[str, Any]
    ) -> int:
        """Calculate confidence score for the troubleshooting results.
        
        Args:
            issues: List of identified issues
            network_data: Network data used for analysis
            
        Returns:
            Confidence score (0-100)
        """
        if not issues:
            # No issues identified, lower confidence
            return 50
        
        # Base confidence on the highest severity issue
        max_severity = max(issue.severity for issue in issues)
        
        # Adjust confidence based on available data
        data_completeness = 0
        if network_data.get("ssid_data"):
            data_completeness += 30
        if network_data.get("client_data"):
            data_completeness += 30
        if network_data.get("issue_description"):
            data_completeness += 20
        
        # Calculate final confidence score
        confidence = int((max_severity * 0.6) + (data_completeness * 0.4))
        
        # Cap at 100
        return min(confidence, 100)
