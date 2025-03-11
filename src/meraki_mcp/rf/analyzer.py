"""RF Analyzer module for Meraki MCP.

This module provides the main interface for analyzing RF spectrum data,
identifying issues, and generating recommendations for wireless optimization.
"""

import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass

from meraki_mcp.rf.spectrum import (
    SpectrumData,
    SpectrumAnalysis,
    InterferenceSource,
    FrequencyBand,
    ChannelWidth
)

# Set up logging
logger = logging.getLogger(__name__)


class RFAnalysisError(Exception):
    """Exception raised for errors in the RF analysis process."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Initialize RFAnalysisError.
        
        Args:
            message: Error message
            details: Additional details about the error
        """
        self.message = message
        self.details = details or {}
        super().__init__(message)


class RFAnalyzer:
    """Class for analyzing RF spectrum data and providing recommendations.
    
    This class is responsible for analyzing RF spectrum data from Meraki
    access points, identifying interference sources, and generating
    actionable recommendations to optimize wireless performance.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the RF Analyzer.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        logger.debug("Initialized RFAnalyzer with config: %s", self.config)
    
    def analyze_spectrum(self, spectrum_data: SpectrumData) -> SpectrumAnalysis:
        """Analyze RF spectrum data and generate insights.
        
        Args:
            spectrum_data: SpectrumData object containing the RF data points
            
        Returns:
            SpectrumAnalysis object with analysis results
            
        Raises:
            RFAnalysisError: If analysis fails
        """
        try:
            logger.info(
                "Analyzing spectrum data for AP %s on %s band, channel %d",
                spectrum_data.access_point_serial,
                spectrum_data.band.value,
                spectrum_data.channel
            )
            
            # Calculate noise floor (simplified algorithm for illustration)
            noise_floor = self._calculate_noise_floor(spectrum_data)
            
            # Identify interference sources
            interference_sources = self._identify_interference(spectrum_data, noise_floor)
            
            # Calculate channel quality
            channel_quality = self._evaluate_channel_quality(
                spectrum_data, noise_floor, interference_sources
            )
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                spectrum_data, noise_floor, interference_sources, channel_quality
            )
            
            # Create analysis summary
            summary = self._create_analysis_summary(
                spectrum_data, noise_floor, interference_sources, 
                channel_quality, recommendations
            )
            
            return SpectrumAnalysis(
                spectrum_data=spectrum_data,
                noise_floor=noise_floor,
                interference_sources=interference_sources,
                channel_quality=channel_quality,
                recommendations=recommendations,
                summary=summary
            )
        
        except Exception as e:
            logger.error("RF analysis failed: %s", str(e), exc_info=True)
            raise RFAnalysisError(f"Failed to analyze spectrum data: {str(e)}")
    
    def _calculate_noise_floor(self, spectrum_data: SpectrumData) -> float:
        """Calculate the noise floor from spectrum data.
        
        Args:
            spectrum_data: SpectrumData object
            
        Returns:
            Estimated noise floor in dBm
        """
        if not spectrum_data.data_points:
            return -95.0  # Default noise floor estimation
        
        # Simple algorithm: take the 10th percentile of power readings
        # In a real implementation, this would be more sophisticated
        powers = sorted(dp.power for dp in spectrum_data.data_points)
        index = max(0, int(len(powers) * 0.1) - 1)
        return powers[index]
    
    def _identify_interference(
        self, spectrum_data: SpectrumData, noise_floor: float
    ) -> List[InterferenceSource]:
        """Identify interference sources in the spectrum data.
        
        Args:
            spectrum_data: SpectrumData object
            noise_floor: Calculated noise floor in dBm
            
        Returns:
            List of identified InterferenceSource objects
        """
        interference_sources = []
        
        # Implementation would include complex pattern recognition algorithms
        # This is a simplified example
        
        # Check for common interference patterns based on frequency and power
        if spectrum_data.band == FrequencyBand.BAND_2_4GHZ:
            interference_sources.extend(self._check_for_2_4ghz_interference(
                spectrum_data, noise_floor
            ))
        elif spectrum_data.band == FrequencyBand.BAND_5GHZ:
            interference_sources.extend(self._check_for_5ghz_interference(
                spectrum_data, noise_floor
            ))
        elif spectrum_data.band == FrequencyBand.BAND_6GHZ:
            interference_sources.extend(self._check_for_6ghz_interference(
                spectrum_data, noise_floor
            ))
        
        return interference_sources
    
    def _check_for_2_4ghz_interference(
        self, spectrum_data: SpectrumData, noise_floor: float
    ) -> List[InterferenceSource]:
        """Check for common 2.4 GHz interference patterns.
        
        Args:
            spectrum_data: SpectrumData object
            noise_floor: Calculated noise floor in dBm
            
        Returns:
            List of identified InterferenceSource objects
        """
        interference_sources = []
        
        # Example: Check for microwave oven interference (simplified)
        # Microwave ovens typically affect frequencies around 2.45 GHz
        microwave_affected_data_points = [
            dp for dp in spectrum_data.data_points
            if 2445 <= dp.frequency <= 2465 and dp.power > noise_floor + 10
        ]
        
        if microwave_affected_data_points and len(microwave_affected_data_points) > 5:
            avg_power = sum(dp.power for dp in microwave_affected_data_points) / len(microwave_affected_data_points)
            impact_level = min(100, int((avg_power - noise_floor) * 5))
            
            interference_sources.append(InterferenceSource(
                type="microwave",
                frequency_range=(2445, 2465),
                avg_power=avg_power,
                impact_level=impact_level,
                confidence=75,
                description="Possible microwave oven interference detected"
            ))
        
        # Example: Check for Bluetooth interference
        bluetooth_affected_data_points = [
            dp for dp in spectrum_data.data_points
            if 2402 <= dp.frequency <= 2480 and dp.power > noise_floor + 5
        ]
        
        if bluetooth_affected_data_points and len(bluetooth_affected_data_points) > 10:
            avg_power = sum(dp.power for dp in bluetooth_affected_data_points) / len(bluetooth_affected_data_points)
            impact_level = min(100, int((avg_power - noise_floor) * 3))
            
            interference_sources.append(InterferenceSource(
                type="bluetooth",
                frequency_range=(2402, 2480),
                avg_power=avg_power,
                impact_level=impact_level,
                confidence=65,
                description="Bluetooth device interference detected"
            ))
        
        return interference_sources
    
    def _check_for_5ghz_interference(
        self, spectrum_data: SpectrumData, noise_floor: float
    ) -> List[InterferenceSource]:
        """Check for common 5 GHz interference patterns.
        
        Args:
            spectrum_data: SpectrumData object
            noise_floor: Calculated noise floor in dBm
            
        Returns:
            List of identified InterferenceSource objects
        """
        interference_sources = []
        
        # Example: Check for radar interference (simplified)
        radar_affected_data_points = [
            dp for dp in spectrum_data.data_points
            if 5250 <= dp.frequency <= 5350 and dp.power > noise_floor + 15
        ]
        
        if radar_affected_data_points and len(radar_affected_data_points) > 3:
            avg_power = sum(dp.power for dp in radar_affected_data_points) / len(radar_affected_data_points)
            impact_level = min(100, int((avg_power - noise_floor) * 4))
            
            interference_sources.append(InterferenceSource(
                type="radar",
                frequency_range=(5250, 5350),
                avg_power=avg_power,
                impact_level=impact_level,
                confidence=80,
                description="Possible radar/DFS interference detected"
            ))
        
        return interference_sources
    
    def _check_for_6ghz_interference(
        self, spectrum_data: SpectrumData, noise_floor: float
    ) -> List[InterferenceSource]:
        """Check for common 6 GHz interference patterns.
        
        Args:
            spectrum_data: SpectrumData object
            noise_floor: Calculated noise floor in dBm
            
        Returns:
            List of identified InterferenceSource objects
        """
        # 6 GHz is a newer band with potentially fewer interference sources
        # This would be expanded with more patterns as they are identified
        return []
    
    def _evaluate_channel_quality(
        self, 
        spectrum_data: SpectrumData, 
        noise_floor: float,
        interference_sources: List[InterferenceSource]
    ) -> int:
        """Evaluate overall channel quality.
        
        Args:
            spectrum_data: SpectrumData object
            noise_floor: Calculated noise floor in dBm
            interference_sources: List of identified interference sources
            
        Returns:
            Channel quality score (0-100, where 100 is best)
        """
        # Start with max score
        quality_score = 100
        
        # Deduct points based on noise floor
        # Higher noise floor = lower quality
        if noise_floor > -85:
            quality_score -= min(30, int((noise_floor + 85) * 3))
        
        # Deduct points based on average utilization
        avg_utilization = spectrum_data.get_average_utilization()
        if avg_utilization > 20:
            quality_score -= min(40, int(avg_utilization / 2))
        
        # Deduct points for each interference source based on impact
        for source in interference_sources:
            quality_score -= min(30, int(source.impact_level / 3))
        
        # Ensure score stays in valid range
        return max(0, min(100, quality_score))
    
    def _generate_recommendations(
        self,
        spectrum_data: SpectrumData,
        noise_floor: float,
        interference_sources: List[InterferenceSource],
        channel_quality: int
    ) -> List[str]:
        """Generate actionable recommendations based on analysis.
        
        Args:
            spectrum_data: SpectrumData object
            noise_floor: Calculated noise floor in dBm
            interference_sources: List of identified interference sources
            channel_quality: Channel quality score
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        # Poor channel quality recommendations
        if channel_quality < 40:
            recommendations.append(
                f"Consider changing the channel. Current channel {spectrum_data.channel} "
                f"has poor quality ({channel_quality}/100)."
            )
        
        # High noise floor recommendations
        if noise_floor > -80:
            recommendations.append(
                f"High noise floor detected ({noise_floor} dBm). "
                "Consider identifying and removing nearby interference sources."
            )
        
        # Interference-specific recommendations
        for source in interference_sources:
            if source.type == "microwave":
                recommendations.append(
                    "Microwave oven interference detected. Consider moving the AP "
                    "further from kitchen areas or switching to 5 GHz operations."
                )
            elif source.type == "bluetooth":
                recommendations.append(
                    "Bluetooth interference detected. Consider moving Bluetooth devices "
                    "away from the AP or switching to 5 GHz operations."
                )
            elif source.type == "radar":
                recommendations.append(
                    "Radar/DFS interference detected. Consider using a non-DFS channel "
                    "if stable operation is required."
                )
        
        # Channel width recommendations
        if spectrum_data.channel_width == ChannelWidth.WIDTH_80MHZ and channel_quality < 60:
            recommendations.append(
                "Consider reducing channel width from 80 MHz to 40 MHz to "
                "reduce susceptibility to interference."
            )
        elif spectrum_data.channel_width == ChannelWidth.WIDTH_160MHZ and channel_quality < 70:
            recommendations.append(
                "Consider reducing channel width from 160 MHz to 80 MHz or 40 MHz to "
                "reduce susceptibility to interference."
            )
        
        # Band steering recommendations
        if spectrum_data.band == FrequencyBand.BAND_2_4GHZ and channel_quality < 50:
            recommendations.append(
                "Poor 2.4 GHz performance detected. Consider enabling band steering "
                "to encourage clients to use 5 GHz when possible."
            )
        
        return recommendations
    
    def _create_analysis_summary(
        self,
        spectrum_data: SpectrumData,
        noise_floor: float,
        interference_sources: List[InterferenceSource],
        channel_quality: int,
        recommendations: List[str]
    ) -> str:
        """Create a human-readable summary of the analysis.
        
        Args:
            spectrum_data: SpectrumData object
            noise_floor: Calculated noise floor in dBm
            interference_sources: List of identified interference sources
            channel_quality: Channel quality score
            recommendations: List of recommendations
            
        Returns:
            Summary string
        """
        ap_info = (
            f"AP {spectrum_data.access_point_serial} operating on "
            f"{spectrum_data.band.value} band, channel {spectrum_data.channel}, "
            f"{spectrum_data.channel_width.value} MHz width"
        )
        
        quality_rating = "Excellent" if channel_quality >= 80 else (
            "Good" if channel_quality >= 60 else (
                "Fair" if channel_quality >= 40 else "Poor"
            )
        )
        
        interference_summary = (
            f"Detected {len(interference_sources)} interference sources." 
            if interference_sources else "No significant interference detected."
        )
        
        summary_parts = [
            f"RF Analysis Summary for {ap_info}",
            f"Channel Quality: {channel_quality}/100 ({quality_rating})",
            f"Noise Floor: {noise_floor} dBm",
            f"Average Utilization: {spectrum_data.get_average_utilization():.1f}%",
            interference_summary
        ]
        
        # Add interference details if present
        if interference_sources:
            summary_parts.append("Interference Sources:")
            for i, source in enumerate(interference_sources, 1):
                summary_parts.append(
                    f"  {i}. {source.description} "
                    f"(Impact: {source.impact_level}/100, "
                    f"Confidence: {source.confidence}%)"
                )
        
        # Add recommendations if present
        if recommendations:
            summary_parts.append("Recommendations:")
            for i, rec in enumerate(recommendations, 1):
                summary_parts.append(f"  {i}. {rec}")
        
        return "\n".join(summary_parts)
    
    def batch_analyze(
        self, spectrum_data_list: List[SpectrumData]
    ) -> Dict[str, SpectrumAnalysis]:
        """Analyze multiple spectrum data sets in batch.
        
        Args:
            spectrum_data_list: List of SpectrumData objects
            
        Returns:
            Dictionary mapping access point serials to their analysis results
            
        Raises:
            RFAnalysisError: If analysis fails
        """
        results = {}
        errors = []
        
        for spectrum_data in spectrum_data_list:
            try:
                results[spectrum_data.access_point_serial] = self.analyze_spectrum(spectrum_data)
            except RFAnalysisError as e:
                errors.append(f"Error analyzing AP {spectrum_data.access_point_serial}: {str(e)}")
                logger.error(
                    "Error analyzing AP %s: %s", 
                    spectrum_data.access_point_serial, 
                    str(e),
                    exc_info=True
                )
        
        if errors and not results:
            raise RFAnalysisError(
                f"Batch analysis failed for all {len(spectrum_data_list)} access points",
                {"errors": errors}
            )
        
        return results
