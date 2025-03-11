#!/usr/bin/env python
"""
Test script for the Meraki MCP server implementation.

This script demonstrates how to run the MCP server directly.
"""

import logging
from meraki_mcp.mcp import MerakiMCPServer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

def main():
    """Run the MCP server."""
    # Create the MCP server
    server = MerakiMCPServer(
        name="Meraki RF Analysis",
        version="0.1.0"
    )
    
    # Run the server on localhost:8000
    server.run(host="localhost", port=8000)

if __name__ == "__main__":
    main()
