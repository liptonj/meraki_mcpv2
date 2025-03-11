"""Knowledge Base module for Meraki MCP.

This package provides access to knowledge bases, best practices, and troubleshooting guides
for Meraki wireless networks.
"""

from meraki_mcp.knowledge.wifi_kb import WifiKnowledgeBase
from meraki_mcp.knowledge.base import KnowledgeBase, KnowledgeBaseError

__all__ = ["KnowledgeBase", "KnowledgeBaseError", "WifiKnowledgeBase"]
