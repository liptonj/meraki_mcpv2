"""RF Analysis and Troubleshooting Models.

This module contains Pydantic models for RF analysis and troubleshooting.
Used for spectrum data representation, analysis results, and troubleshooting requests/responses.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


class SpectrumDataPoint(BaseModel):
    """Model representing a single point of RF spectrum data."""

    frequency: float = Field(..., description="Frequency in MHz")
    power: float = Field(..., description="Power level in dBm")
    timestamp: Optional[datetime] = Field(None, description="Timestamp when the data was collected")
    channel: Optional[int] = Field(None, description="WiFi channel corresponding to this frequency")


class InterferenceSource(BaseModel):
    """Model representing an identified source of interference."""

    id: str = Field(..., description="Unique identifier for this interference source")
    type: str = Field(..., description="Type of interference (e.g., 'bluetooth', 'microwave', 'adjacent_network')")
    confidence: float = Field(..., description="Confidence score for the interference identification")
    affected_channels: List[int] = Field(..., description="List of WiFi channels affected by this interference")
    frequency_range: List[float] = Field(..., description="Frequency range affected [start_MHz, end_MHz]")
    severity: str = Field(..., description="Severity level ('low', 'medium', 'high', 'critical')")
    description: Optional[str] = Field(None, description="Human-readable description of the interference")


class SpectrumData(BaseModel):
    """Model representing RF spectrum data for analysis."""

    device_id: str = Field(..., description="Identifier of the device that collected the data")
    access_point_name: Optional[str] = Field(None, description="Name of the access point")
    network_id: Optional[str] = Field(None, description="Identifier of the network the device belongs to")
    data_points: List[SpectrumDataPoint] = Field(..., description="List of spectrum data points")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the data was collected")
    band: str = Field(..., description="Frequency band ('2.4GHz', '5GHz', '6GHz')")
    channel_width: Optional[int] = Field(None, description="Channel width in MHz")

    @validator('band')
    def validate_band(cls, v):
        """Validate that the band is one of the expected values."""
        allowed_bands = ["2.4GHz", "5GHz", "6GHz"]
        if v not in allowed_bands:
            raise ValueError(f"Band must be one of {allowed_bands}")
        return v


class ChannelAssessment(BaseModel):
    """Model representing assessment information for a WiFi channel."""

    channel: int = Field(..., description="WiFi channel number")
    utilization: float = Field(..., description="Channel utilization percentage (0-100)")
    noise_floor: float = Field(..., description="Noise floor in dBm")
    interference_level: str = Field(..., description="Level of interference ('low', 'medium', 'high', 'critical')")
    recommendation: str = Field(..., description="Recommendation for this channel ('good', 'acceptable', 'avoid')")
    co_channel_networks: Optional[int] = Field(None, description="Number of co-channel networks detected")
    adjacent_channel_networks: Optional[int] = Field(None, description="Number of adjacent channel networks detected")


class SpectrumAnalysis(BaseModel):
    """Model representing the result of an RF spectrum analysis."""

    device_id: str = Field(..., description="Identifier of the device that the analysis is for")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the analysis was performed")
    band: str = Field(..., description="Frequency band analyzed ('2.4GHz', '5GHz', '6GHz')")
    noise_floor: float = Field(..., description="Average noise floor in dBm")
    interference_sources: List[InterferenceSource] = Field(default_factory=list, description="Detected sources of interference")
    channel_assessments: List[ChannelAssessment] = Field(default_factory=list, description="Assessment of each channel")
    recommended_channels: List[int] = Field(..., description="List of recommended channels in order of preference")
    summary: str = Field(..., description="Human-readable summary of the analysis")


class TroubleshootingItem(BaseModel):
    """Model representing a single troubleshooting item or recommendation."""

    issue_type: str = Field(..., description="Type of issue identified")
    severity: str = Field(..., description="Severity level ('low', 'medium', 'high', 'critical')")
    description: str = Field(..., description="Description of the issue")
    recommendation: str = Field(..., description="Recommended action to resolve the issue")
    confidence: float = Field(..., description="Confidence score for this troubleshooting item")
    additional_info: Optional[Dict[str, Any]] = Field(None, description="Additional context or information related to the issue")


class TroubleshootingResult(BaseModel):
    """Model representing the result of an RF troubleshooting analysis."""

    device_id: str = Field(..., description="Identifier of the device that was analyzed")
    network_id: Optional[str] = Field(None, description="Identifier of the network the device belongs to")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the troubleshooting was performed")
    issues_found: bool = Field(..., description="Whether any issues were found")
    items: List[TroubleshootingItem] = Field(default_factory=list, description="List of troubleshooting items")
    summary: str = Field(..., description="Human-readable summary of the troubleshooting results")
    analysis: Optional[SpectrumAnalysis] = Field(None, description="The full spectrum analysis if available")


class RFAnalysisRequest(BaseModel):
    """Request model for RF spectrum analysis."""

    spectrum_data: SpectrumData = Field(..., description="Spectrum data to analyze")


class RFTroubleshootRequest(BaseModel):
    """Request model for RF troubleshooting."""

    spectrum_data: SpectrumData = Field(..., description="Spectrum data for troubleshooting")
    include_analysis: bool = Field(False, description="Whether to include the full spectrum analysis in the result")


class BatchRFTroubleshootRequest(BaseModel):
    """Request model for batch RF troubleshooting of multiple access points."""

    spectrum_data_list: List[SpectrumData] = Field(..., description="List of spectrum data for multiple access points")
    include_analysis: bool = Field(False, description="Whether to include the full spectrum analysis in the results")


class BatchTroubleshootingResult(BaseModel):
    """Response model for batch RF troubleshooting."""

    results: List[TroubleshootingResult] = Field(..., description="List of troubleshooting results for each access point")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the batch troubleshooting was performed")
    summary: str = Field(..., description="Overall summary of the batch troubleshooting results")


class RequestOptions(BaseModel):
    """Options for RF analysis and troubleshooting requests."""

    include_raw_data: Optional[bool] = False
    stream: Optional[bool] = False
    update_frequency: Optional[str] = "onchange"
    update_interval_seconds: Optional[int] = None
