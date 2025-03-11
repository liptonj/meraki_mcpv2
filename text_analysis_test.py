#!/usr/bin/env python
"""
Test script for the text_analysis module to verify it's working properly.
This script tests context extraction from sample queries.
"""

import logging
import sys
import os
from pprint import pprint

# Add the parent directory to the Python path to allow importing the module
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.insert(0, src_path)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d:%(funcName)s - %(message)s",
)
logger = logging.getLogger("text_analysis_test")

# Import the module we want to test
from meraki_mcp.utils.text_analysis import (
    extract_context_from_query,
    QueryContext,
    NLTK_AVAILABLE
)

def main():
    """Test text analysis functionality."""
    logger.info("Testing text analysis module")
    logger.info(f"NLTK available: {NLTK_AVAILABLE}")
    
    # Sample queries for testing
    test_queries = [
        "What's happening with the access point in Room 305?",
        "Check the status of wireless network 'Guest-WiFi' in Building B",
        "Show me all MR36 devices in the San Francisco office",
        "I'm experiencing slow network speeds on SSID Meraki-Corp",
        "List all offline devices in the New York network with serial number Q2XX-YYYY-ZZZZ"
    ]
    
    # Test each query
    for i, query in enumerate(test_queries):
        logger.info(f"\nTesting query {i+1}: '{query}'")
        
        # Extract context
        context = extract_context_from_query(query)
        
        # Display extracted context
        logger.info("Extracted context:")
        if context.location_identifiers:
            logger.info(f"  Locations: {context.location_identifiers}")
        if context.building_identifiers:
            logger.info(f"  Buildings: {context.building_identifiers}")
        if context.network_identifiers:
            logger.info(f"  Networks: {context.network_identifiers}")
        if context.device_identifiers:
            logger.info(f"  Device IDs: {context.device_identifiers}")
        if context.device_types:
            logger.info(f"  Device types: {context.device_types}")
        if context.ssid_names:
            logger.info(f"  SSIDs: {context.ssid_names}")
        if context.error_messages:
            logger.info(f"  Error messages: {context.error_messages}")
        
        # Additional context attributes (may be present depending on implementation)
        for attr in dir(context):
            if not attr.startswith("_") and not callable(getattr(context, attr)) and attr not in [
                'location_identifiers', 'building_identifiers', 'network_identifiers',
                'device_identifiers', 'device_types', 'ssid_names', 'error_messages'
            ]:
                value = getattr(context, attr)
                if value and isinstance(value, (list, set, dict)) and len(value) > 0:
                    logger.info(f"  {attr}: {value}")
    
    logger.info("\nText analysis module test complete!")

if __name__ == "__main__":
    main()
