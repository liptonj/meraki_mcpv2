"""Base Knowledge Base module for Meraki MCP.

This module provides the base abstract class for all knowledge base implementations
and defines the common interface for interacting with knowledge sources.
"""

from abc import ABC, abstractmethod
import logging
from typing import Dict, List, Optional, Any, Union

# Set up logging
logger = logging.getLogger(__name__)


class KnowledgeBaseError(Exception):
    """Exception raised for errors in Knowledge Base operations."""
    
    pass


class KnowledgeBase(ABC):
    """Abstract base class for knowledge base implementations.
    
    This class defines the interface that all knowledge base implementations
    must follow, providing a consistent API for retrieving and querying
    knowledge across different domains.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the knowledge base.
        
        Args:
            config: Optional configuration dictionary for the knowledge base
                
        Raises:
            KnowledgeBaseError: If initialization fails
        """
        self.config = config or {}
        self._initialized = False
        
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the knowledge base.
        
        This method should perform any necessary setup, such as loading data files,
        connecting to external knowledge sources, or initializing search indexes.
        
        Returns:
            None
            
        Raises:
            KnowledgeBaseError: If initialization fails
        """
        self._initialized = True
    
    @abstractmethod
    async def query(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Query the knowledge base with a natural language question.
        
        Args:
            query: The natural language query string
            context: Optional context information to help refine the query
                
        Returns:
            A dictionary containing the query results
                
        Raises:
            KnowledgeBaseError: If the query operation fails
        """
        if not self._initialized:
            raise KnowledgeBaseError("Knowledge base not initialized")
        
        pass
    
    @abstractmethod
    async def get_categories(self) -> List[str]:
        """Get the list of available knowledge categories.
        
        Returns:
            A list of category names
                
        Raises:
            KnowledgeBaseError: If the operation fails
        """
        if not self._initialized:
            raise KnowledgeBaseError("Knowledge base not initialized")
        
        pass
    
    @abstractmethod
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
        
        pass
    
    @abstractmethod
    async def get_topic_content(self, topic_id: str) -> Dict[str, Any]:
        """Get the content for a specific topic.
        
        Args:
            topic_id: The ID of the topic to retrieve
                
        Returns:
            A dictionary containing the topic content
                
        Raises:
            KnowledgeBaseError: If the topic is not found or the operation fails
        """
        if not self._initialized:
            raise KnowledgeBaseError("Knowledge base not initialized")
        
        pass
