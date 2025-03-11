"""RF Troubleshooter module for Meraki MCP.

This module provides integration between RF analysis and knowledge base systems
to automatically diagnose wireless issues and suggest remediation steps based on
RF spectrum data and expert knowledge.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple, Union
import asyncio

from meraki_mcp.rf.analyzer import RFAnalyzer, RFAnalysisError
from meraki_mcp.rf.spectrum import SpectrumData, SpectrumAnalysis, InterferenceSource
from meraki_mcp.knowledge.base import KnowledgeBaseError
from meraki_mcp.knowledge.wifi_kb import WifiKnowledgeBase

# Set up logging
logger = logging.getLogger(__name__)


class RFTroubleshootingError(Exception):
    """Exception raised for errors during RF troubleshooting."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Initialize RFTroubleshootingError.
        
        Args:
            message: Error message
            details: Additional details about the error
        """
        self.message = message
        self.details = details or {}
        super().__init__(message)


class TroubleshootingResult:
    """Class representing the results of RF troubleshooting.
    
    Attributes:
        spectrum_analysis: The RF spectrum analysis results
        issue_type: The identified type of wireless issue
        issue_description: Detailed description of the issue
        confidence: Confidence score (0-100) for the diagnosis
        recommendations: Recommended actions to resolve the issue
        knowledge_references: References to knowledge base articles
    """
    
    def __init__(
        self,
        spectrum_analysis: SpectrumAnalysis,
        issue_type: str,
        issue_description: str,
        confidence: int,
        recommendations: List[str],
        knowledge_references: List[Dict[str, str]]
    ):
        """Initialize TroubleshootingResult.
        
        Args:
            spectrum_analysis: RF spectrum analysis results
            issue_type: Identified type of wireless issue
            issue_description: Detailed description of the issue
            confidence: Confidence score (0-100) for the diagnosis
            recommendations: Recommended actions to resolve the issue
            knowledge_references: References to knowledge base articles
        """
        self.spectrum_analysis = spectrum_analysis
        self.issue_type = issue_type
        self.issue_description = issue_description
        self.confidence = confidence
        self.recommendations = recommendations
        self.knowledge_references = knowledge_references
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert the troubleshooting result to a dictionary.
        
        Returns:
            Dictionary representation of the troubleshooting result
        """
        return {
            "issue_type": self.issue_type,
            "issue_description": self.issue_description,
            "confidence": self.confidence,
            "recommendations": self.recommendations,
            "knowledge_references": self.knowledge_references,
            "analysis_summary": self.spectrum_analysis.summary,
            "interference_sources": [
                {
                    "type": source.type,
                    "frequency_range": source.frequency_range,
                    "avg_power": source.avg_power,
                    "impact_level": source.impact_level,
                    "confidence": source.confidence,
                    "description": source.description
                }
                for source in self.spectrum_analysis.interference_sources
            ],
            "channel_quality": self.spectrum_analysis.channel_quality
        }


class RFTroubleshooter:
    """Class for troubleshooting wireless issues using RF analysis and knowledge base.
    
    This class integrates the RF analyzer with the knowledge base to automatically
    diagnose wireless issues and recommend remediation steps based on spectrum data
    and expert knowledge.
    """
    
    def __init__(
        self, 
        analyzer_config: Optional[Dict[str, Any]] = None,
        kb_config: Optional[Dict[str, Any]] = None
    ):
        """Initialize the RF Troubleshooter.
        
        Args:
            analyzer_config: Optional configuration for the RF analyzer
            kb_config: Optional configuration for the knowledge base
        """
        self.analyzer = RFAnalyzer(config=analyzer_config)
        self.knowledge_base = WifiKnowledgeBase(config=kb_config)
        self._kb_initialized = False
        logger.debug(
            "Initialized RFTroubleshooter with analyzer_config: %s, kb_config: %s",
            analyzer_config,
            kb_config
        )
    
    async def initialize_knowledge_base(self) -> None:
        """Initialize the knowledge base.
        
        This method must be called before using the troubleshooter.
        
        Returns:
            None
            
        Raises:
            RFTroubleshootingError: If knowledge base initialization fails
        """
        if self._kb_initialized:
            return
            
        try:
            await self.knowledge_base.initialize()
            self._kb_initialized = True
            logger.info("Knowledge base initialized successfully")
        except KnowledgeBaseError as e:
            logger.error("Failed to initialize knowledge base: %s", str(e))
            raise RFTroubleshootingError(
                f"Failed to initialize knowledge base: {str(e)}"
            )
    
    async def troubleshoot(self, spectrum_data: SpectrumData) -> TroubleshootingResult:
        """Perform RF troubleshooting based on spectrum data.
        
        This method analyzes the RF spectrum data, identifies potential issues,
        and generates recommended solutions by combining RF analysis with knowledge
        base information.
        
        Args:
            spectrum_data: SpectrumData object containing the RF data points
            
        Returns:
            TroubleshootingResult with the troubleshooting results
            
        Raises:
            RFTroubleshootingError: If troubleshooting fails
        """
        if not self._kb_initialized:
            await self.initialize_knowledge_base()
            
        try:
            # Step 1: Analyze the spectrum data
            logger.info(
                "Starting RF troubleshooting for AP %s on %s band, channel %d",
                spectrum_data.access_point_serial,
                spectrum_data.band.value,
                spectrum_data.channel
            )
            
            spectrum_analysis = self.analyzer.analyze_spectrum(spectrum_data)
            
            # Step 2: Match analysis with knowledge base topics
            issue_type, issue_details = await self._identify_issue_type(spectrum_analysis)
            
            # Step 3: Get detailed recommendations from knowledge base
            knowledge_refs, recommendations = await self._get_recommendations(
                issue_type, spectrum_analysis
            )
            
            # Step 4: Calculate confidence score based on severity and knowledge base match
            confidence = self._calculate_confidence(spectrum_analysis, issue_type)
            
            return TroubleshootingResult(
                spectrum_analysis=spectrum_analysis,
                issue_type=issue_type,
                issue_description=issue_details,
                confidence=confidence,
                recommendations=recommendations,
                knowledge_references=knowledge_refs
            )
            
        except RFAnalysisError as e:
            logger.error("RF analysis failed during troubleshooting: %s", str(e))
            raise RFTroubleshootingError(
                f"RF analysis failed during troubleshooting: {str(e)}"
            )
        except KnowledgeBaseError as e:
            logger.error("Knowledge base query failed during troubleshooting: %s", str(e))
            raise RFTroubleshootingError(
                f"Knowledge base query failed during troubleshooting: {str(e)}"
            )
        except Exception as e:
            logger.error("Unexpected error during RF troubleshooting: %s", str(e), exc_info=True)
            raise RFTroubleshootingError(
                f"Unexpected error during RF troubleshooting: {str(e)}"
            )
    
    async def batch_troubleshoot(
        self, spectrum_data_list: List[SpectrumData]
    ) -> Dict[str, TroubleshootingResult]:
        """Perform RF troubleshooting on multiple access points.
        
        Args:
            spectrum_data_list: List of SpectrumData objects to analyze
            
        Returns:
            Dictionary mapping access point serials to TroubleshootingResult objects
            
        Raises:
            RFTroubleshootingError: If batch troubleshooting fails
        """
        if not self._kb_initialized:
            await self.initialize_knowledge_base()
            
        results = {}
        
        try:
            # Process each spectrum data object sequentially
            # In a production environment, this could be parallelized for better performance
            for spectrum_data in spectrum_data_list:
                ap_serial = spectrum_data.access_point_serial
                try:
                    result = await self.troubleshoot(spectrum_data)
                    results[ap_serial] = result
                    logger.info(
                        "Completed troubleshooting for AP %s: %s (confidence: %d%%)",
                        ap_serial, result.issue_type, result.confidence
                    )
                except RFTroubleshootingError as e:
                    logger.warning(
                        "Troubleshooting failed for AP %s: %s", ap_serial, str(e)
                    )
                    # Continue with next AP instead of failing entire batch
            
            return results
            
        except Exception as e:
            logger.error("Batch troubleshooting failed: %s", str(e), exc_info=True)
            raise RFTroubleshootingError(f"Batch troubleshooting failed: {str(e)}")
    
    async def _identify_issue_type(
        self, spectrum_analysis: SpectrumAnalysis
    ) -> Tuple[str, str]:
        """Identify the type of wireless issue based on spectrum analysis.
        
        Args:
            spectrum_analysis: SpectrumAnalysis object
            
        Returns:
            Tuple of (issue_type, detailed_description)
        """
        # Determine the most likely issue type based on analysis results
        if not spectrum_analysis.interference_sources:
            if spectrum_analysis.channel_quality < 40:
                issue_type = "poor_channel_quality"
                description = (
                    "Poor channel quality detected with no specific interference source. "
                    f"Channel quality score: {spectrum_analysis.channel_quality}/100. "
                    f"Noise floor: {spectrum_analysis.noise_floor} dBm."
                )
            else:
                issue_type = "normal_operation"
                description = (
                    "No significant issues detected. "
                    f"Channel quality score: {spectrum_analysis.channel_quality}/100."
                )
        else:
            # Determine the most impactful interference source
            primary_interference = max(
                spectrum_analysis.interference_sources,
                key=lambda x: x.impact_level
            )
            
            if primary_interference.type in ("bluetooth", "zigbee", "microwave"):
                issue_type = f"{primary_interference.type}_interference"
                description = (
                    f"{primary_interference.type.capitalize()} interference detected "
                    f"with impact level {primary_interference.impact_level}/100. "
                    f"Affected frequency range: {primary_interference.frequency_range[0]} - "
                    f"{primary_interference.frequency_range[1]} MHz."
                )
            elif "radar" in primary_interference.type:
                issue_type = "radar_interference"
                description = (
                    f"Radar interference detected with impact level "
                    f"{primary_interference.impact_level}/100. "
                    f"This may cause DFS channels to be unavailable."
                )
            elif "rogue" in primary_interference.type:
                issue_type = "co_channel_interference"
                description = (
                    f"Co-channel interference from other WiFi networks detected "
                    f"with impact level {primary_interference.impact_level}/100. "
                    f"This may be causing contention on channel {spectrum_analysis.spectrum_data.channel}."
                )
            else:
                issue_type = "unknown_interference"
                description = (
                    f"Unknown interference detected with impact level "
                    f"{primary_interference.impact_level}/100. "
                    f"Affected frequency range: {primary_interference.frequency_range[0]} - "
                    f"{primary_interference.frequency_range[1]} MHz."
                )
        
        return issue_type, description
    
    async def _get_recommendations(
        self, issue_type: str, spectrum_analysis: SpectrumAnalysis
    ) -> Tuple[List[Dict[str, str]], List[str]]:
        """Get recommendations for resolving the identified issue.
        
        Args:
            issue_type: The type of wireless issue identified
            spectrum_analysis: SpectrumAnalysis object
            
        Returns:
            Tuple of (knowledge_references, recommendations)
        """
        # Start with the recommendations from the RF analyzer
        recommendations = list(spectrum_analysis.recommendations)
        
        # Map issue types to knowledge base topic IDs
        topic_mapping = {
            "poor_channel_quality": "troubleshooting_2",
            "normal_operation": "best_practices_1",
            "bluetooth_interference": "rf_analysis_1",
            "zigbee_interference": "rf_analysis_1",
            "microwave_interference": "rf_analysis_1",
            "radar_interference": "rf_analysis_1",
            "co_channel_interference": "troubleshooting_2",
            "unknown_interference": "troubleshooting_1"
        }
        
        # Get additional recommendations from knowledge base
        knowledge_refs = []
        
        # Get the appropriate topic content based on issue type
        topic_id = topic_mapping.get(issue_type, "troubleshooting_1")
        try:
            topic_content = await self.knowledge_base.get_topic_content(topic_id)
            
            # Add knowledge base topic as a reference
            if "references" in topic_content:
                knowledge_refs.extend(topic_content["references"])
            
            # Add specific recommendations based on issue type
            if issue_type == "bluetooth_interference":
                recommendations.append(
                    "Consider switching to 5 GHz channels to avoid Bluetooth interference"
                )
                recommendations.append(
                    "Increase distance between APs and Bluetooth devices"
                )
            elif issue_type == "microwave_interference":
                recommendations.append(
                    "Move the AP away from kitchen areas or microwave ovens"
                )
                recommendations.append(
                    "Switch affected APs to the 5 GHz band if possible"
                )
            elif issue_type == "co_channel_interference":
                recommendations.append(
                    "Adjust channel planning to minimize overlap with neighboring networks"
                )
                recommendations.append(
                    "Reduce transmit power to decrease the interference radius"
                )
            elif issue_type == "poor_channel_quality":
                recommendations.append(
                    "Consider performing a site survey to identify optimal AP placement"
                )
                
            # Query the knowledge base with a natural language question
            kb_query = f"How to resolve {issue_type.replace('_', ' ')} in Meraki wireless networks?"
            kb_results = await self.knowledge_base.query(kb_query)
            
            if "recommendations" in kb_results:
                recommendations.extend(kb_results["recommendations"])
                
            if "references" in kb_results:
                knowledge_refs.extend(kb_results["references"])
                
        except KnowledgeBaseError as e:
            logger.warning(
                "Failed to get recommendations from knowledge base: %s", str(e)
            )
            # Continue with existing recommendations
        
        # De-duplicate recommendations
        unique_recommendations = []
        for rec in recommendations:
            if rec not in unique_recommendations:
                unique_recommendations.append(rec)
        
        return knowledge_refs, unique_recommendations
    
    def _calculate_confidence(
        self, spectrum_analysis: SpectrumAnalysis, issue_type: str
    ) -> int:
        """Calculate the confidence score for the diagnosis.
        
        Args:
            spectrum_analysis: SpectrumAnalysis object
            issue_type: The type of wireless issue identified
            
        Returns:
            Confidence score (0-100)
        """
        # Base confidence on several factors
        if issue_type == "normal_operation":
            # Higher channel quality means more confidence that everything is normal
            base_confidence = spectrum_analysis.channel_quality
        elif not spectrum_analysis.interference_sources:
            # Poor channel quality but no identified interference sources
            # means less confident diagnosis
            base_confidence = 60
        else:
            # Average the confidence of identified interference sources
            interference_confidences = [
                source.confidence for source in spectrum_analysis.interference_sources
            ]
            base_confidence = sum(interference_confidences) // len(interference_confidences)
        
        # Additional factors that could adjust confidence
        # - Number of data points (more data = more confidence)
        data_points_factor = min(20, len(spectrum_analysis.spectrum_data.data_points) // 10)
        
        # Combine factors for final confidence score
        confidence = min(100, base_confidence + data_points_factor)
        
        return confidence
