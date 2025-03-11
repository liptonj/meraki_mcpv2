"""Base Service module for Meraki MCP.

This module defines the base Service class for the Meraki MCP server.
The Service class serves as a base for all service implementations,
providing common functionality and interfaces.
"""

import abc
import asyncio
import logging
from typing import Any, Dict, List, Optional, TypeVar, Generic, Union, Awaitable

from pydantic import BaseModel

# Setup logging
logger = logging.getLogger(__name__)

T = TypeVar('T')


class ServiceError(Exception):
    """Base exception for all service-related errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Initialize a new ServiceError.

        Args:
            message: Human-readable error message
            details: Additional details about the error
        """
        self.message = message
        self.details = details or {}
        super().__init__(message)


class ServiceNotFoundError(ServiceError):
    """Raised when a requested resource is not found."""
    pass


class ServiceAuthorizationError(ServiceError):
    """Raised when service authorization fails."""
    pass


class ServiceValidationError(ServiceError):
    """Raised when input validation fails."""
    pass


class ServiceTimeoutError(ServiceError):
    """Raised when a service operation times out."""
    pass


class ServiceModel(BaseModel):
    """Base model for service data objects."""
    
    class Config:
        """Configuration for the service model."""
        arbitrary_types_allowed = True
        validate_assignment = True
        extra = "forbid"  # Disallow extra attributes


class Service(abc.ABC):
    """Base service class for Meraki MCP.
    
    This abstract class defines the interface and common functionality
    for all Meraki MCP services. Concrete service implementations should
    inherit from this class and implement the required methods.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize a new Service instance.
        
        Args:
            config: Configuration parameters for the service
        """
        self.config = config or {}
        self._setup_logging()
        
    def _setup_logging(self) -> None:
        """Configure logging for this service."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
    @abc.abstractmethod
    async def initialize(self) -> None:
        """Initialize the service.
        
        This method should be implemented by concrete service classes to
        perform any necessary initialization steps such as establishing
        connections, loading resources, etc.
        
        Raises:
            ServiceError: If initialization fails
        """
        pass
    
    @abc.abstractmethod
    async def shutdown(self) -> None:
        """Shutdown the service.
        
        This method should be implemented by concrete service classes to
        perform any necessary cleanup steps such as closing connections,
        releasing resources, etc.
        
        Raises:
            ServiceError: If shutdown fails
        """
        pass
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check on the service.
        
        Returns:
            Dict containing health check information
        
        Raises:
            ServiceError: If health check fails
        """
        return {
            "service": self.__class__.__name__,
            "status": "healthy",
        }
    
    async def execute_with_timeout(
        self, 
        coro: Awaitable[Any], 
        timeout_seconds: float = 30.0
    ) -> Any:
        """Execute a coroutine with a timeout.
        
        Args:
            coro: Coroutine to execute
            timeout_seconds: Timeout in seconds
            
        Returns:
            Result of the coroutine
            
        Raises:
            ServiceTimeoutError: If the coroutine execution times out
            ServiceError: If the coroutine execution fails
        """
        try:
            return await asyncio.wait_for(coro, timeout=timeout_seconds)
        except asyncio.TimeoutError as e:
            self.logger.error(f"Operation timed out after {timeout_seconds} seconds")
            raise ServiceTimeoutError(
                f"Operation timed out after {timeout_seconds} seconds"
            ) from e
        except Exception as e:
            self.logger.error(f"Operation failed: {str(e)}")
            raise ServiceError(f"Operation failed: {str(e)}") from e


class AsyncService(Service):
    """Base class for asynchronous services.
    
    This class extends the base Service class with additional functionality
    specific to asynchronous services such as event handling and streaming.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize a new AsyncService instance.
        
        Args:
            config: Configuration parameters for the service
        """
        super().__init__(config)
        self._event_queue: asyncio.Queue = asyncio.Queue()
        
    async def publish_event(self, event_type: str, data: Any) -> None:
        """Publish an event to the event queue.
        
        Args:
            event_type: Type of the event
            data: Event data
            
        Raises:
            ServiceError: If publishing the event fails
        """
        try:
            await self._event_queue.put({
                "type": event_type,
                "data": data,
                "timestamp": asyncio.get_running_loop().time()
            })
            self.logger.debug(f"Published event: {event_type}")
        except Exception as e:
            self.logger.error(f"Failed to publish event: {str(e)}")
            raise ServiceError(f"Failed to publish event: {str(e)}") from e
    
    async def subscribe_to_events(self) -> asyncio.Queue:
        """Subscribe to events from this service.
        
        Returns:
            An asyncio.Queue that will receive events
            
        Raises:
            ServiceError: If subscription fails
        """
        try:
            # Create a new queue for this subscriber
            subscriber_queue: asyncio.Queue = asyncio.Queue()
            
            # Start a task to forward events to this subscriber
            asyncio.create_task(self._forward_events(subscriber_queue))
            
            return subscriber_queue
        except Exception as e:
            self.logger.error(f"Failed to subscribe to events: {str(e)}")
            raise ServiceError(f"Failed to subscribe to events: {str(e)}") from e
    
    async def _forward_events(self, subscriber_queue: asyncio.Queue) -> None:
        """Forward events from the main queue to a subscriber queue.
        
        Args:
            subscriber_queue: Queue to forward events to
        """
        try:
            while True:
                # Get event from the main queue
                event = await self._event_queue.get()
                
                # Forward to subscriber
                await subscriber_queue.put(event)
                
                # Mark as done
                self._event_queue.task_done()
        except asyncio.CancelledError:
            self.logger.debug("Event forwarding task cancelled")
        except Exception as e:
            self.logger.error(f"Error forwarding events: {str(e)}")


class CachedService(Service, Generic[T]):
    """Base class for services that implement caching.
    
    This class extends the base Service class with caching functionality.
    The cache is implemented as an in-memory dictionary with optional TTL.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize a new CachedService instance.
        
        Args:
            config: Configuration parameters for the service
        """
        super().__init__(config)
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_ttl: float = self.config.get("cache_ttl", 300.0)  # 5 minutes default
        
    async def get_from_cache(self, key: str) -> Optional[T]:
        """Get a value from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        if key not in self._cache:
            return None
            
        cache_entry = self._cache[key]
        expire_time = cache_entry.get("expire_time")
        
        # Check if entry has expired
        if expire_time and asyncio.get_running_loop().time() > expire_time:
            # Remove expired entry
            del self._cache[key]
            return None
            
        return cache_entry.get("value")
        
    async def set_in_cache(
        self, 
        key: str, 
        value: T, 
        ttl: Optional[float] = None
    ) -> None:
        """Set a value in the cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds, or None for no expiration
        """
        expire_time = None
        if ttl is not None:
            expire_time = asyncio.get_running_loop().time() + ttl
        elif self._cache_ttl > 0:
            expire_time = asyncio.get_running_loop().time() + self._cache_ttl
            
        self._cache[key] = {
            "value": value,
            "expire_time": expire_time
        }
        
    async def remove_from_cache(self, key: str) -> None:
        """Remove a value from the cache.
        
        Args:
            key: Cache key
        """
        if key in self._cache:
            del self._cache[key]
    
    async def clear_cache(self) -> None:
        """Clear the entire cache."""
        self._cache.clear()
        
    async def get_or_create(
        self, 
        key: str, 
        creator_func: callable, 
        ttl: Optional[float] = None
    ) -> T:
        """Get a value from cache or create it if not present.
        
        Args:
            key: Cache key
            creator_func: Function to call to create the value if not in cache
            ttl: Time-to-live for the cached value
            
        Returns:
            Value from cache or newly created value
            
        Raises:
            ServiceError: If creating the value fails
        """
        # Try to get from cache first
        cached_value = await self.get_from_cache(key)
        if cached_value is not None:
            self.logger.debug(f"Cache hit for key: {key}")
            return cached_value
            
        # Not in cache, need to create
        self.logger.debug(f"Cache miss for key: {key}")
        try:
            value = await creator_func()
            await self.set_in_cache(key, value, ttl)
            return value
        except Exception as e:
            self.logger.error(f"Failed to create value for cache key {key}: {str(e)}")
            raise ServiceError(f"Failed to create value: {str(e)}") from e