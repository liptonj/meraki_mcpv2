"""WiFi Knowledge Base module for Meraki MCP.

This module provides access to WiFi best practices and troubleshooting guides
for Meraki wireless networks based on official Meraki documentation.
"""

import json
import logging
import os
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

from meraki_mcp.knowledge.base import KnowledgeBase, KnowledgeBaseError

# Set up logging
logger = logging.getLogger(__name__)


class WifiKnowledgeBase(KnowledgeBase):
    """Knowledge base for WiFi best practices and troubleshooting.
    
    This class provides access to knowledge about WiFi best practices,
    troubleshooting guides, and resolution steps for common WiFi issues
    based on Meraki's official documentation.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the WiFi knowledge base.
        
        Args:
            config: Optional configuration dictionary with the following keys:
                - data_path: Path to the knowledge base data files
                - embedding_model: Name of the embedding model to use for semantic search
                - enable_remote_sources: Whether to query remote documentation sources
                
        Raises:
            KnowledgeBaseError: If initialization fails
        """
        super().__init__(config)
        self.knowledge_data: Dict[str, Any] = {}
        self.categories: List[str] = []
        self.topics: Dict[str, List[Dict[str, Any]]] = {}
        
        # Default configurations
        self.data_path = self.config.get("data_path", "data/knowledge")
        self.embedding_model = self.config.get("embedding_model", "all-mpnet-base-v2")
        self.enable_remote_sources = self.config.get("enable_remote_sources", False)
    
    async def initialize(self) -> None:
        """Initialize the WiFi knowledge base.
        
        This method loads knowledge base data from files and sets up the
        search indexes for querying the knowledge base.
        
        Returns:
            None
            
        Raises:
            KnowledgeBaseError: If initialization fails
        """
        try:
            # In a real implementation, this would load data from files or databases
            # For this example, we'll hard-code the knowledge structure based on
            # the Meraki documentation URLs provided
            
            # Define the knowledge categories
            self.categories = [
                "wifi_basics",
                "best_practices",
                "troubleshooting",
                "rf_analysis"
            ]
            
            # Define topics for each category
            self.topics = {
                "wifi_basics": [
                    {
                        "id": "wifi_basics_1",
                        "title": "Understanding WiFi Fundamentals",
                        "description": "Basic concepts of WiFi networking and wireless communication",
                        "category": "wifi_basics"
                    },
                    {
                        "id": "wifi_basics_2",
                        "title": "802.11 Standards and Protocols",
                        "description": "Overview of WiFi standards and protocols (802.11a/b/g/n/ac/ax)",
                        "category": "wifi_basics"
                    }
                ],
                "best_practices": [
                    {
                        "id": "best_practices_1",
                        "title": "WiFi Network Design Best Practices",
                        "description": "Guidelines for designing optimal WiFi networks",
                        "category": "best_practices",
                        "source_url": "https://documentation.meraki.com/MR/Wi-Fi_Basics_and_Best_Practices"
                    },
                    {
                        "id": "best_practices_2",
                        "title": "Channel Planning and Radio Settings",
                        "description": "Best practices for channel selection and radio configuration",
                        "category": "best_practices",
                        "source_url": "https://documentation.meraki.com/MR/Wi-Fi_Basics_and_Best_Practices"
                    },
                    {
                        "id": "best_practices_3",
                        "title": "Security Recommendations",
                        "description": "WiFi security best practices for Meraki networks",
                        "category": "best_practices",
                        "source_url": "https://documentation.meraki.com/MR/Wi-Fi_Basics_and_Best_Practices"
                    }
                ],
                "troubleshooting": [
                    {
                        "id": "troubleshooting_1",
                        "title": "Wireless Issue Resolution Guide",
                        "description": "Comprehensive guide for resolving common wireless issues",
                        "category": "troubleshooting",
                        "source_url": "https://documentation.meraki.com/MR/Wireless_Troubleshooting/Wireless_Issue_Resolution_Guide"
                    },
                    {
                        "id": "troubleshooting_2",
                        "title": "Tools for Troubleshooting Poor Wireless Performance",
                        "description": "Meraki tools and approaches for diagnosing wireless performance issues",
                        "category": "troubleshooting",
                        "source_url": "https://documentation.meraki.com/MR/Wi-Fi_Basics_and_Best_Practices/Tools_for_Troubleshooting_Poor_Wireless_Performance"
                    },
                    {
                        "id": "troubleshooting_3",
                        "title": "Client Connectivity Issues",
                        "description": "Diagnosing and resolving client connection problems",
                        "category": "troubleshooting",
                        "source_url": "https://documentation.meraki.com/MR/Wireless_Troubleshooting/Wireless_Issue_Resolution_Guide"
                    }
                ],
                "rf_analysis": [
                    {
                        "id": "rf_analysis_1",
                        "title": "Understanding RF Spectrum Analysis",
                        "description": "Basics of RF spectrum analysis and interpretation",
                        "category": "rf_analysis"
                    },
                    {
                        "id": "rf_analysis_2",
                        "title": "Using Meraki RF Spectrum Analyzer",
                        "description": "Guide to using the built-in RF spectrum analysis tools",
                        "category": "rf_analysis"
                    }
                ]
            }
            
            # Sample content for each topic would be stored in a database or files
            # Here we define a basic structure for demonstration
            self.knowledge_data = {
                "wifi_basics_1": {
                    "content": "WiFi Fundamentals content would go here...",
                    "references": []
                },
                "best_practices_1": {
                    "content": """
                    # WiFi Network Design Best Practices
                    
                    ## Access Point Placement
                    - Mount APs at ceiling height when possible
                    - Avoid mounting APs near metal objects or concrete walls
                    - For optimal coverage, place APs centrally in the intended coverage area
                    - Maintain 30-40 foot spacing between APs in typical office environments
                    
                    ## Channel Configuration
                    - Use auto channel configuration where possible
                    - For manual configuration, use non-overlapping channels (1, 6, 11) on 2.4 GHz
                    - For 5 GHz, maximize channel separation and utilize DFS channels when allowed
                    
                    ## Power Settings
                    - Avoid maximum power settings in dense environments
                    - Target -65 to -70 dBm as the minimum signal strength at the edge of the coverage area
                    - Adjust power evenly across all APs in the same area
                    """,
                    "references": [
                        {
                            "title": "WiFi Basics and Best Practices",
                            "url": "https://documentation.meraki.com/MR/Wi-Fi_Basics_and_Best_Practices"
                        }
                    ]
                },
                "troubleshooting_1": {
                    "content": """
                    # Wireless Issue Resolution Guide
                    
                    ## Common Wireless Issues and Resolutions
                    
                    ### Connectivity Issues
                    1. **Client Cannot Connect to SSID**
                       - Verify the SSID is broadcasting
                       - Check client compatibility with the security type
                       - Ensure the passphrase is correct
                       - Verify the client is within range of an AP
                       
                    2. **Intermittent Connectivity**
                       - Check for RF interference
                       - Verify adequate signal strength (-67 dBm or better)
                       - Check for overlapping channels
                       - Ensure adequate AP density for the environment
                       
                    3. **Poor Performance**
                       - Identify potential sources of interference
                       - Check for channel utilization above 50%
                       - Verify appropriate bandwidth settings
                       - Check for outdated clients or drivers
                    """,
                    "references": [
                        {
                            "title": "Wireless Issue Resolution Guide",
                            "url": "https://documentation.meraki.com/MR/Wireless_Troubleshooting/Wireless_Issue_Resolution_Guide"
                        }
                    ]
                },
                "troubleshooting_2": {
                    "content": """
                    # Tools for Troubleshooting Poor Wireless Performance
                    
                    ## Meraki Dashboard Tools
                    
                    ### Wireless Health
                    - **Connection Stats**: Monitors connection success rate and failures
                    - **Latency Stats**: Tracks latency between clients, APs, and gateways
                    - **Performance Stats**: Shows throughput and signal quality metrics
                    
                    ### Air Marshal
                    - Detects and locates rogue APs and potential security threats
                    - Identifies interfering networks
                    
                    ### Channel Utilization
                    - Shows channel usage and interference levels
                    - Helps identify congested channels
                    
                    ## Client-Side Tools
                    - **Wireless Diagnostics** (macOS): Built-in tool for analyzing WiFi connections
                    - **NetSpot**: WiFi analyzer for site surveys
                    - **WiFi Analyzer** (Android): Mobile app for checking signal strength and channels
                    """,
                    "references": [
                        {
                            "title": "Tools for Troubleshooting Poor Wireless Performance",
                            "url": "https://documentation.meraki.com/MR/Wi-Fi_Basics_and_Best_Practices/Tools_for_Troubleshooting_Poor_Wireless_Performance"
                        }
                    ]
                },
                "troubleshooting_3": {
                    "content": """
                    # Client Connectivity Issues
                    
                    ## Common Client Connectivity Problems
                    
                    ### Authentication Failures
                    - **WPA/WPA2 Authentication Failures**
                      - Verify the correct passphrase is being used
                      - Check for special characters that might be misinterpreted
                      - Ensure client supports the chosen encryption method
                    
                    - **802.1X Authentication Issues**
                      - Verify RADIUS server configuration
                      - Check client certificates and EAP methods
                      - Confirm user credentials are valid
                    
                    ### Association Problems
                    - **Client Cannot See SSID**
                      - Verify SSID broadcasting is enabled
                      - Check client is in range of the AP
                      - Ensure client supports the frequency band (2.4 GHz vs 5 GHz)
                    
                    - **Client Can See SSID But Cannot Connect**
                      - Check signal strength (should be -70 dBm or better)
                      - Verify client is not on a blocklist
                      - Check for MAC filtering rules
                    
                    ### Post-Connection Issues
                    - **Client Disconnects Frequently**
                      - Look for roaming issues between APs
                      - Check for interference sources
                      - Verify adequate signal strength throughout coverage area
                    
                    - **Client Gets IP But Cannot Access Resources**
                      - Check VLAN configuration
                      - Verify firewall and traffic shaping rules
                      - Confirm DNS services are working properly
                    """,
                    "references": [
                        {
                            "title": "Wireless Issue Resolution Guide",
                            "url": "https://documentation.meraki.com/MR/Wireless_Troubleshooting/Wireless_Issue_Resolution_Guide"
                        },
                        {
                            "title": "Troubleshooting Client Connectivity",
                            "url": "https://documentation.meraki.com/MR/Client_Addressing_and_Bridging/Troubleshooting_Client_Connectivity"
                        }
                    ]
                },
                "rf_analysis_1": {
                    "content": "RF Spectrum Analysis content would go here...",
                    "references": []
                }
            }
            
            self._initialized = True
            logger.info("WiFi knowledge base initialized successfully")
        
        except Exception as e:
            logger.error(f"Failed to initialize WiFi knowledge base: {str(e)}")
            raise KnowledgeBaseError(f"Failed to initialize WiFi knowledge base: {str(e)}")
    
    async def query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Query the WiFi knowledge base with a natural language question.
        
        Args:
            query: The natural language query string
            context: Optional context information to help refine the query
                
        Returns:
            A dictionary containing the query results with the following structure:
                {
                    "answer": str,            # The direct answer to the query
                    "topics": List[Dict],     # Relevant topics related to the query
                    "references": List[Dict]  # Reference sources for the answer
                }
                
        Raises:
            KnowledgeBaseError: If the query operation fails
        """
        if not self._initialized:
            raise KnowledgeBaseError("Knowledge base not initialized")
        
        try:
            # In a real implementation, this would use semantic search or an LLM
            # to find the most relevant topics and generate an answer
            
            # For this example, we'll use a very simple keyword matching approach
            context = context or {}
            query = query.lower()
            
            # Initialize response structure
            response = {
                "answer": "",
                "topics": [],
                "references": []
            }
            
            # Simple keyword matching logic
            if "best practice" in query or "design" in query:
                topic_id = "best_practices_1"
                topic_data = self.knowledge_data.get(topic_id, {})
                response["answer"] = "Based on Meraki's best practices for WiFi network design, you should consider proper AP placement, channel configuration, and power settings."
                response["topics"] = [next((t for t in self.topics["best_practices"] if t["id"] == topic_id), {})]
                response["references"] = topic_data.get("references", [])
                
            elif "troubleshoot" in query or "issue" in query or "problem" in query:
                topic_id = "troubleshooting_1"
                topic_data = self.knowledge_data.get(topic_id, {})
                response["answer"] = "For troubleshooting wireless issues, start by checking connectivity, signal strength, and potential interference sources."
                response["topics"] = [next((t for t in self.topics["troubleshooting"] if t["id"] == topic_id), {})]
                response["references"] = topic_data.get("references", [])
                
            elif "performance" in query or "slow" in query:
                topic_id = "troubleshooting_2"
                topic_data = self.knowledge_data.get(topic_id, {})
                response["answer"] = "To troubleshoot poor wireless performance, use Meraki Dashboard tools like Wireless Health, Air Marshal, and Channel Utilization."
                response["topics"] = [next((t for t in self.topics["troubleshooting"] if t["id"] == topic_id), {})]
                response["references"] = topic_data.get("references", [])
                
            elif "rf" in query or "spectrum" in query or "interference" in query:
                topic_id = "rf_analysis_1"
                topic_data = self.knowledge_data.get(topic_id, {})
                response["answer"] = "RF spectrum analysis helps identify interference sources and optimize wireless performance."
                response["topics"] = [next((t for t in self.topics["rf_analysis"] if t["id"] == topic_id), {})]
                response["references"] = topic_data.get("references", [])
                
            else:
                # Default response if no specific match is found
                response["answer"] = "I don't have specific information about that query. Try asking about WiFi best practices, troubleshooting, or RF analysis."
            
            return response
            
        except Exception as e:
            logger.error(f"Error querying WiFi knowledge base: {str(e)}")
            raise KnowledgeBaseError(f"Error querying WiFi knowledge base: {str(e)}")
    
    async def get_categories(self) -> List[str]:
        """Get the list of available knowledge categories.
        
        Returns:
            A list of category names
                
        Raises:
            KnowledgeBaseError: If the operation fails
        """
        if not self._initialized:
            raise KnowledgeBaseError("Knowledge base not initialized")
        
        return self.categories
    
    async def get_topics(self, category: Optional[str] = None) -> List[Dict[str, str]]:
        """Get the list of available topics, optionally filtered by category.
        
        Args:
            category: Optional category to filter topics by
                
        Returns:
            A list of topic dictionaries, each containing at minimum 'id' and 'title' keys
                
        Raises:
            KnowledgeBaseError: If the operation fails
        """
        if not self._initialized:
            raise KnowledgeBaseError("Knowledge base not initialized")
        
        try:
            if category and category not in self.categories:
                raise KnowledgeBaseError(f"Unknown category: {category}")
            
            if category:
                return self.topics.get(category, [])
            else:
                # Return all topics across all categories
                all_topics = []
                for category_topics in self.topics.values():
                    all_topics.extend(category_topics)
                return all_topics
                
        except Exception as e:
            logger.error(f"Error getting topics: {str(e)}")
            raise KnowledgeBaseError(f"Error getting topics: {str(e)}")
    
    async def get_topic_content(self, topic_id: str) -> Dict[str, Any]:
        """Get the content for a specific topic.
        
        Args:
            topic_id: The ID of the topic to retrieve
                
        Returns:
            A dictionary containing the topic content and metadata
                
        Raises:
            KnowledgeBaseError: If the topic is not found or the operation fails
        """
        if not self._initialized:
            raise KnowledgeBaseError("Knowledge base not initialized")
        
        try:
            # Find the topic metadata across all categories
            topic_metadata = None
            for category_topics in self.topics.values():
                for topic in category_topics:
                    if topic["id"] == topic_id:
                        topic_metadata = topic
                        break
                if topic_metadata:
                    break
            
            if not topic_metadata:
                raise KnowledgeBaseError(f"Topic not found: {topic_id}")
            
            # Get the topic content
            topic_content = self.knowledge_data.get(topic_id, {})
            if not topic_content:
                raise KnowledgeBaseError(f"Content not found for topic: {topic_id}")
            
            # Combine metadata and content
            result = {
                **topic_metadata,
                "content": topic_content.get("content", ""),
                "references": topic_content.get("references", [])
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting topic content: {str(e)}")
            raise KnowledgeBaseError(f"Error getting topic content: {str(e)}")
