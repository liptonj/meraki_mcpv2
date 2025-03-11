#!/usr/bin/env python3
"""
NLP Test Tool

This script tests the NLP capabilities of the text analysis module.
It can be run as a standalone script to verify that NLTK is properly installed
and that the context extraction is working correctly.
"""

import logging
import sys
from text_analysis import extract_context_from_query, NLTK_AVAILABLE, detect_ambiguities

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

def main():
    """Run NLP tests with sample queries."""
    print(f"NLTK available: {NLTK_AVAILABLE}")
    
    test_queries = [
        "Users report problems connecting to Home at Home",
        "The WiFi in Building 3 is not working properly",
        "My MacBook can't connect to the Guest network",
        "There's an issue with the Home SSID in the west wing",
        "Experiencing poor signal strength on my phone at the Office network"
    ]
    
    print("\nTesting context extraction with sample queries:")
    for query in test_queries:
        print(f"\n=== Query: {query} ===")
        context = extract_context_from_query(query)
        print(f"SSID names: {context.ssid_names}")
        print(f"Network identifiers: {context.network_identifiers}")
        print(f"Device types: {context.device_types}")
        print(f"Location identifiers: {context.location_identifiers}")
        print(f"Building identifiers: {context.building_identifiers}")
        
        # Check for ambiguities
        ambiguities = detect_ambiguities(context)
        if any(ambiguities.values()):
            print(f"Detected ambiguities: {ambiguities}")

if __name__ == "__main__":
    main()
