"""RF Analysis module for Meraki MCP.

This package provides tools and utilities for analyzing RF spectrum data,
diagnosing wireless issues, and optimizing wireless network performance.
"""

from meraki_mcp.rf.analyzer import RFAnalyzer, RFAnalysisError
from meraki_mcp.rf.spectrum import SpectrumData, SpectrumAnalysis
from meraki_mcp.rf.rf_troubleshooter import (
    RFTroubleshooter,
    RFTroubleshootingError,
    TroubleshootingResult
)

__all__ = ["RFAnalyzer", "RFAnalysisError", "SpectrumData", "SpectrumAnalysis", "RFTroubleshooter", "RFTroubleshootingError", "TroubleshootingResult"]
