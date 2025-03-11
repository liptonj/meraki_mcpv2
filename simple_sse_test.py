#!/usr/bin/env python
"""
Simple SSE client test for testing Meraki MCP SSE endpoints.
"""
import asyncio
import json
import sys
from sseclient import SSEClient

DISCOVERY_URL = "http://localhost:8000/sse"
TEST_URL = "http://localhost:8000/sse/test"

async def main():
    """Test SSE endpoints."""
    print(f"Testing SSE discovery endpoint: {DISCOVERY_URL}")
    
    try:
        # First try the discovery endpoint with regular HTTP
        import requests
        discovery_response = requests.get(DISCOVERY_URL)
        print(f"Discovery HTTP status: {discovery_response.status_code}")
        if discovery_response.status_code == 200:
            print(f"Discovery endpoints: {json.dumps(discovery_response.json()['streams'], indent=2)}")
        
        # Now try with SSE client
        print("\nConnecting to test SSE endpoint...")
        client = SSEClient(TEST_URL)
        
        # Process a few events
        for i, event in enumerate(client):
            event_data = json.loads(event.data)
            print(f"Received event {i+1}:")
            print(f"  Event type: {event.event}")
            print(f"  Data: {json.dumps(event_data, indent=2)}")
            
            # Exit after a few events
            if i >= 2:
                print("Successfully received events, exiting...")
                break
                
        print("\nSSE test successful!")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
