"""Meraki MCP Server implementation.

This module provides a Model Context Protocol (MCP) server implementation for the 
Meraki RF Analysis and Troubleshooting services, enabling standardized communication
with Claude and other MCP-compatible clients.

The server requires the MCP Python SDK to be installed.

Example usage:
    server = MerakiMCPServer()
    server.run(host="0.0.0.0", port=8000)
"""
import argparse
import asyncio
import logging
import os
from pathlib import Path
import time
from typing import Any, Dict

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Load environment variables from .env file
dotenv_path = Path(__file__).parent.parent.parent / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path=str(dotenv_path))
    logger = logging.getLogger(__name__)
    logger.info(f"Loaded environment variables from {dotenv_path}")

# Ensure MERAKI_API_KEY is set
if not os.environ.get("MERAKI_API_KEY"):
    logger.warning("MERAKI_API_KEY environment variable is not set. Meraki API functionality may not work properly.")

# Configure logging
logger = logging.getLogger(__name__)

# Import Meraki client for API interactions
from meraki_mcp.core.meraki_client import MerakiClient

# Import tool discovery function
from meraki_mcp.tools import discover_tool_classes


class MerakiMCPServer:
    """Meraki MCP Server for RF analysis and troubleshooting.
    
    This class implements a Model Context Protocol (MCP) server for
    Meraki RF Analysis and Troubleshooting services, providing tools
    for analyzing RF spectrum data and troubleshooting RF issues.
    
    Note: This implementation requires the MCP Python SDK to be installed.
    """
    
    def __init__(
        self,
        name: str = "Meraki RF Analysis",
        description: str = "Provides RF analysis and troubleshooting for Meraki wireless networks",
        version: str = "0.1.0",
        port: int = 8000,
    ) -> None:
        """Initialize the MCP server.
        
        Args:
            name: The name of the server
            description: A description of the server's purpose
            version: The server version
            port: The port to listen on (default: 8000)
        """
        self.name = name
        self.description = description
        self.version = version
        self.port = port
        self.initialization_complete = False
        
        # Initialize the MCP server with the server name and port
        self.mcp = FastMCP(name, port=port)
        
        # Initialize Meraki client first
        self._meraki_client = None
        try:
            self._meraki_client = MerakiClient()
            logger.info("Meraki client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Meraki client: {e}")
            logger.warning("Some Meraki API functionality will be unavailable. Check your MERAKI_API_KEY.")
        
        # Dynamically discover and initialize tool classes
        self._tools = {}
        tool_classes = discover_tool_classes()
        for class_name, tool_class in tool_classes.items():
            # Convert class name to attribute name (e.g., OrganizationTools -> _organization_tools)
            tool_attr_name = f"_{class_name[0].lower() + class_name[1:]}"
            # Initialize the tool class
            tool_instance = tool_class(self)
            # Store in tools dictionary
            self._tools[class_name] = tool_instance
            # Also set as instance attribute for backward compatibility
            setattr(self, tool_attr_name, tool_instance)
            logger.info(f"Initialized {class_name}")
        
        # Register only server-specific resources and tools
        self._register_server_resources()
        self._register_custom_tools()
        
        logger.info(f"Initialized {self.name} MCP server version {self.version}")
    
    # Server implementation methods
    
    def _register_server_resources(self) -> None:
        """Register server-specific MCP resources."""
        # Server info resource
        @self.mcp.resource("server://info")
        def get_server_info() -> Dict[str, Any]:
            """Get server information and capabilities.
            
            Returns:
                Server metadata including version and capabilities
            """
            
            # Collect capabilities from all tool classes
            capabilities = []
            # Add default server capabilities
            capabilities.append("verify_meraki_connection")
            
            # Get capability lists from each tool class
            for tool_name, tool_instance in self._tools.items():
                if hasattr(tool_instance, 'get_capabilities'):
                    tool_capabilities = tool_instance.get_capabilities()
                    if tool_capabilities:
                        capabilities.extend(tool_instance.get_capabilities())
            
            return {
                "name": self.name,
                "version": self.version,
                "description": self.description,
                "capabilities": capabilities
            }
    
    def _register_custom_tools(self) -> None:
        """Register any server-specific tools that don't belong to a specific tool class."""
        
        @self.mcp.tool()
        async def verify_meraki_connection(request: Dict[str, Any]) -> Dict[str, Any]:
            """Verify connection to the Meraki Dashboard API.
            
            Returns:
                A status message indicating whether the connection was successful
                
            Raises:
                Exception: If the API request fails or Meraki client is not initialized
            """
            if self._meraki_client:
                try:
                    # Try to list organizations as a basic connection test
                    orgs = await self._organization_tools.list_organizations({})                    
                    return {
                        "status": "success",
                        "message": "Successfully connected to Meraki dashboard API",
                        "organization_count": len(orgs.get("organizations", []))
                    }
                except Exception as e:
                    logger.error(f"Failed to verify Meraki connection: {e}")
                    return {
                        "status": "error",
                        "message": f"Failed to connect to Meraki dashboard API: {str(e)}"
                    }
            else:
                return {
                    "status": "error",
                    "message": "Meraki client not initialized. Check your MERAKI_API_KEY."
                }
        
    # RF analysis stream methods have been moved to rf_tools.py
    
    # RF troubleshooting stream methods have been moved to rf_tools.py
    
    def run(self, host: str = "0.0.0.0", port: int = None) -> None:
        """Run the MCP server.
        
        Args:
            host: The host to bind to (not used by FastMCP directly)
            port: The port to listen on (overrides the port set in constructor if provided)
            
        Raises:
            OSError: If the port is already in use and the alternative port is also unavailable
        """
        # Use port parameter if provided, otherwise use the port set in constructor
        if port is not None and port != self.port:
            # Need to recreate the MCP server with new port
            self.port = port
            self.mcp = FastMCP(self.name, port=port)
        
        logger.info(f"Starting {self.name} MCP server on {host}:{self.port}")
        try:
            # Give more time for initialization to complete before accepting connections
            logger.info("Allowing time for server initialization...")
            time.sleep(5)  # Increased delay to ensure initialization completes
            
            # Set initialization flag to true
            self.initialization_complete = True
            logger.info("Server initialization complete, ready to handle requests")
            
            # FastMCP.run() only takes a transport parameter
            self.mcp.run(transport='sse')
        except OSError as e:
            if "address already in use" in str(e).lower():
                # Port is already in use, try an alternative port
                alt_port = self.port + 1
                logger.warning(f"Port {self.port} already in use. Trying port {alt_port}...")
                print(f"Port {self.port} already in use. Trying port {alt_port}...")
                try:
                    # Recreate with new port
                    self.port = alt_port
                    self.mcp = FastMCP(self.name, port=alt_port)
                    logger.info(f"Starting {self.name} MCP server on {host}:{alt_port}")
                    
                    # Give more time for initialization to complete before accepting connections
                    logger.info("Allowing time for server initialization...")
                    time.sleep(5)  # Increased delay to ensure initialization completes
                    
                    # Set initialization flag to true
                    self.initialization_complete = True
                    logger.info("Server initialization complete, ready to handle requests")
                    
                    self.mcp.run(transport='sse')
                except Exception as e2:
                    logger.error(f"Failed to start server on alternative port: {e2}")
                    raise
            else:
                logger.error(f"Failed to start server: {e}")
                raise


# This allows the server module to be run directly
if __name__ == "__main__":
    import argparse
    import os

    from dotenv import load_dotenv

    # Load environment variables from .env file
    load_dotenv()
    
    # Configure logging with enhanced format including line numbers and file paths
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(pathname)s:%(lineno)d:%(funcName)s - %(message)s",
    )
    
    # Disable verbose DEBUG logs from SSE modules
    logging.getLogger("mcp.server.sse").setLevel(logging.INFO)
    logging.getLogger("sse_starlette.sse").setLevel(logging.INFO)
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Meraki MCP Server")
    parser.add_argument(
        "--host",
        type=str, 
        default="0.0.0.0",
        help="Host to bind the server to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind the server to (default: 8000)"
    )
    parser.add_argument(
        "--transport",
        type=str,
        choices=["stdio", "sse"],
        default="sse",
        help="Transport protocol to use (default: sse)"
    )
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Logging level (default: INFO)"
    )
    # Add FastAPI/Uvicorn-style arguments (ignored but accepted for compatibility)
    parser.add_argument(
        "--reload",
        action="store_true",
        help="[Ignored] Enable auto-reload (FastAPI/Uvicorn compatibility)"
    )
    parser.add_argument(
        "--env-file",
        type=str,
        help="[Ignored] Path to .env file (FastAPI/Uvicorn compatibility)"
    )
    args = parser.parse_args()
    
    # Set log level
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    # Start the server
    server = MerakiMCPServer(port=args.port)
    try:
        server.run(host=args.host, port=args.port)
    except KeyboardInterrupt:
        print("\nShutting down server...")
    except Exception as e:
        logger.error(f"Error running server: {e}")
        raise
