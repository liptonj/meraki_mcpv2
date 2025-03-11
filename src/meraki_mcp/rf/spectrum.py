"""RF Spectrum Analysis module for Meraki MCP.

This module provides data structures and utilities for representing and
analyzing RF spectrum data from Meraki wireless networks.
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Tuple

# Set up logging
logger = logging.getLogger(__name__)


class FrequencyBand(Enum):
    """Enum representing WiFi frequency bands."""
    
    BAND_2_4GHZ = "2.4GHz"
    BAND_5GHZ = "5GHz"
    BAND_6GHZ = "6GHz"


class ChannelWidth(Enum):
    """Enum representing WiFi channel widths."""
    
    WIDTH_20MHZ = 20
    WIDTH_40MHZ = 40
    WIDTH_80MHZ = 80
    WIDTH_160MHZ = 160


@dataclass
class SpectrumDataPoint:
    """Data class representing a single point in RF spectrum data.
    
    Attributes:
        frequency: Frequency in MHz
        power: Signal power in dBm
        utilization: Channel utilization percentage (0-100)
        timestamp: Unix timestamp when the measurement was taken
    """
    
    frequency: float
    power: float
    utilization: float
    timestamp: int


@dataclass
class SpectrumData:
    """Data class representing a collection of RF spectrum data points.
    
    Attributes:
        access_point_serial: Serial number of the access point
        band: Frequency band (2.4GHz, 5GHz, or 6GHz)
        channel: Current operating channel
        channel_width: Channel width in MHz
        data_points: List of SpectrumDataPoint objects
        start_time: Start time of the data collection (Unix timestamp)
        end_time: End time of the data collection (Unix timestamp)
        metadata: Additional metadata about the spectrum data
    """
    
    access_point_serial: str
    band: FrequencyBand
    channel: int
    channel_width: ChannelWidth
    data_points: List[SpectrumDataPoint] = field(default_factory=list)
    start_time: int = 0
    end_time: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_data_point(self, data_point: SpectrumDataPoint) -> None:
        """Add a data point to the spectrum data.
        
        Args:
            data_point: The SpectrumDataPoint to add
        """
        self.data_points.append(data_point)
        
        # Update start and end times if needed
        if self.start_time == 0 or data_point.timestamp < self.start_time:
            self.start_time = data_point.timestamp
        if data_point.timestamp > self.end_time:
            self.end_time = data_point.timestamp
    
    def get_average_power(self) -> float:
        """Calculate the average power across all data points.
        
        Returns:
            Average power in dBm, or 0 if no data points exist
        """
        if not self.data_points:
            return 0
        
        total_power = sum(dp.power for dp in self.data_points)
        return total_power / len(self.data_points)
    
    def get_average_utilization(self) -> float:
        """Calculate the average channel utilization across all data points.
        
        Returns:
            Average utilization percentage (0-100), or 0 if no data points exist
        """
        if not self.data_points:
            return 0
        
        total_utilization = sum(dp.utilization for dp in self.data_points)
        return total_utilization / len(self.data_points)
    
    def get_frequency_range(self) -> Tuple[float, float]:
        """Get the frequency range covered by the data points.
        
        Returns:
            Tuple of (min_frequency, max_frequency) in MHz, or (0, 0) if no data points exist
        """
        if not self.data_points:
            return (0, 0)
        
        min_freq = min(dp.frequency for dp in self.data_points)
        max_freq = max(dp.frequency for dp in self.data_points)
        return (min_freq, max_freq)


@dataclass
class InterferenceSource:
    """Data class representing an identified interference source.
    
    Attributes:
        type: Type of interference (e.g., "bluetooth", "microwave", "rogue_ap")
        frequency_range: Tuple of (min_frequency, max_frequency) in MHz
        avg_power: Average power level in dBm
        impact_level: Estimated impact level (0-100, where 100 is highest impact)
        confidence: Confidence in the interference identification (0-100)
        description: Human-readable description of the interference
    """
    
    type: str
    frequency_range: Tuple[float, float]
    avg_power: float
    impact_level: int
    confidence: int
    description: str


@dataclass
class SpectrumAnalysis:
    """Data class representing the results of RF spectrum analysis.
    
    Attributes:
        spectrum_data: The SpectrumData that was analyzed
        noise_floor: Estimated noise floor in dBm
        interference_sources: List of identified interference sources
        channel_quality: Overall channel quality score (0-100)
        recommendations: List of recommendations based on the analysis
        summary: Human-readable summary of the analysis
    """
    
    spectrum_data: SpectrumData
    noise_floor: float
    interference_sources: List[InterferenceSource] = field(default_factory=list)
    channel_quality: int = 0
    recommendations: List[str] = field(default_factory=list)
    summary: str = ""
