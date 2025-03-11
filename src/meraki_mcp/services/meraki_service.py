"""Meraki API Service.

This module provides a service layer for interacting with the Meraki Dashboard API.
It extends the base Service class and wraps the MerakiClient.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple, Union

from fastapi import HTTPException

from meraki_mcp.core.meraki_client import MerakiClient
from meraki_mcp.services.service import AsyncService, ServiceError, ServiceNotFoundError

logger = logging.getLogger(__name__)


class MerakiService(AsyncService):
    """Service for interacting with the Meraki Dashboard API.
    
    This service extends the AsyncService class and wraps the MerakiClient
    to provide high-level methods for interacting with the Meraki Dashboard API.
    It includes event publishing for significant operations and results.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the MerakiService.
        
        Args:
            config: Configuration parameters
        """
        super().__init__(config)
        self.client: Optional[MerakiClient] = None
        
    async def initialize(self) -> None:
        """Initialize the service by creating a MerakiClient instance.
        
        Raises:
            ServiceError: If initialization fails
        """
        try:
            api_key = self.config.get("api_key")
            self.client = MerakiClient(api_key=api_key)
            self.logger.info("MerakiService initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize MerakiService: {str(e)}")
            raise ServiceError(f"Failed to initialize MerakiService: {str(e)}") from e
    
    async def shutdown(self) -> None:
        """Shutdown the service.
        
        Raises:
            ServiceError: If shutdown fails
        """
        # No specific cleanup needed for MerakiClient
        self.logger.info("MerakiService shutdown")
    
    async def get_organizations(self) -> List[Dict[str, Any]]:
        """Get all organizations.
        
        Returns:
            List of organization dictionaries
            
        Raises:
            ServiceError: If the operation fails
        """
        try:
            if not self.client:
                raise ServiceError("MerakiService not initialized")
                
            organizations = self.client.get_organizations()
            await self.publish_event("organizations_retrieved", {"count": len(organizations)})
            return organizations
        except HTTPException as e:
            self.logger.error(f"HTTP error getting organizations: {str(e)}")
            raise ServiceError(f"Failed to get organizations: {str(e)}") from e
        except Exception as e:
            self.logger.error(f"Error getting organizations: {str(e)}")
            raise ServiceError(f"Failed to get organizations: {str(e)}") from e
    
    async def get_organization_by_name(self, name: str) -> Dict[str, Any]:
        """Get organization by name.
        
        Args:
            name: Organization name
            
        Returns:
            Organization dictionary
            
        Raises:
            ServiceNotFoundError: If organization not found
            ServiceError: If the operation fails
        """
        try:
            if not self.client:
                raise ServiceError("MerakiService not initialized")
                
            organizations = self.client.get_organizations()
            for org in organizations:
                if org["name"].lower() == name.lower():
                    await self.publish_event("organization_retrieved", {"id": org["id"], "name": org["name"]})
                    return org
                    
            raise ServiceNotFoundError(f"Organization with name '{name}' not found")
        except ServiceNotFoundError:
            raise
        except HTTPException as e:
            self.logger.error(f"HTTP error getting organization by name: {str(e)}")
            raise ServiceError(f"Failed to get organization by name: {str(e)}") from e
        except Exception as e:
            self.logger.error(f"Error getting organization by name: {str(e)}")
            raise ServiceError(f"Failed to get organization by name: {str(e)}") from e
    
    async def get_networks(self, org_id: str) -> List[Dict[str, Any]]:
        """Get all networks for an organization.
        
        Args:
            org_id: Organization ID
            
        Returns:
            List of network dictionaries
            
        Raises:
            ServiceError: If the operation fails
        """
        try:
            if not self.client:
                raise ServiceError("MerakiService not initialized")
                
            networks = self.client.get_organization_networks(org_id)
            await self.publish_event("networks_retrieved", {"org_id": org_id, "count": len(networks)})
            return networks
        except HTTPException as e:
            self.logger.error(f"HTTP error getting networks: {str(e)}")
            raise ServiceError(f"Failed to get networks: {str(e)}") from e
        except Exception as e:
            self.logger.error(f"Error getting networks: {str(e)}")
            raise ServiceError(f"Failed to get networks: {str(e)}") from e
    
    async def get_network_by_name(self, org_id: str, name: str) -> Dict[str, Any]:
        """Get network by name.
        
        Args:
            org_id: Organization ID
            name: Network name
            
        Returns:
            Network dictionary
            
        Raises:
            ServiceNotFoundError: If network not found
            ServiceError: If the operation fails
        """
        try:
            if not self.client:
                raise ServiceError("MerakiService not initialized")
                
            networks = self.client.get_organization_networks(org_id)
            for network in networks:
                if network["name"].lower() == name.lower():
                    await self.publish_event("network_retrieved", {"id": network["id"], "name": network["name"]})
                    return network
                    
            raise ServiceNotFoundError(f"Network with name '{name}' not found")
        except ServiceNotFoundError:
            raise
        except HTTPException as e:
            self.logger.error(f"HTTP error getting network by name: {str(e)}")
            raise ServiceError(f"Failed to get network by name: {str(e)}") from e
        except Exception as e:
            self.logger.error(f"Error getting network by name: {str(e)}")
            raise ServiceError(f"Failed to get network by name: {str(e)}") from e
    
    async def get_devices(self, network_id: str) -> List[Dict[str, Any]]:
        """Get all devices in a network.
        
        Args:
            network_id: Network ID
            
        Returns:
            List of device dictionaries
            
        Raises:
            ServiceError: If the operation fails
        """
        try:
            if not self.client:
                raise ServiceError("MerakiService not initialized")
                
            devices = self.client.get_network_devices(network_id)
            await self.publish_event("devices_retrieved", {"network_id": network_id, "count": len(devices)})
            return devices
        except HTTPException as e:
            self.logger.error(f"HTTP error getting devices: {str(e)}")
            raise ServiceError(f"Failed to get devices: {str(e)}") from e
        except Exception as e:
            self.logger.error(f"Error getting devices: {str(e)}")
            raise ServiceError(f"Failed to get devices: {str(e)}") from e
    
    async def get_device_by_name(self, network_id: str, name: str) -> Dict[str, Any]:
        """Get device by name.
        
        Args:
            network_id: Network ID
            name: Device name
            
        Returns:
            Device dictionary
            
        Raises:
            ServiceNotFoundError: If device not found
            ServiceError: If the operation fails
        """
        try:
            if not self.client:
                raise ServiceError("MerakiService not initialized")
                
            devices = self.client.get_network_devices(network_id)
            for device in devices:
                if device.get("name", "").lower() == name.lower():
                    await self.publish_event("device_retrieved", {"serial": device["serial"], "name": device.get("name")})
                    return device
                    
            raise ServiceNotFoundError(f"Device with name '{name}' not found")
        except ServiceNotFoundError:
            raise
        except HTTPException as e:
            self.logger.error(f"HTTP error getting device by name: {str(e)}")
            raise ServiceError(f"Failed to get device by name: {str(e)}") from e
        except Exception as e:
            self.logger.error(f"Error getting device by name: {str(e)}")
            raise ServiceError(f"Failed to get device by name: {str(e)}") from e
    
    async def get_clients(self, network_id: str, timespan: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all clients in a network.
        
        Args:
            network_id: Network ID
            timespan: Optional timespan in seconds
            
        Returns:
            List of client dictionaries
            
        Raises:
            ServiceError: If the operation fails
        """
        try:
            if not self.client:
                raise ServiceError("MerakiService not initialized")
                
            clients = self.client.get_network_clients(network_id, timespan=timespan)
            await self.publish_event("clients_retrieved", {"network_id": network_id, "count": len(clients)})
            return clients
        except HTTPException as e:
            self.logger.error(f"HTTP error getting clients: {str(e)}")
            raise ServiceError(f"Failed to get clients: {str(e)}") from e
        except Exception as e:
            self.logger.error(f"Error getting clients: {str(e)}")
            raise ServiceError(f"Failed to get clients: {str(e)}") from e
    
    async def get_device_statuses(self, org_id: str) -> List[Dict[str, Any]]:
        """Get statuses for all devices in an organization.
        
        Args:
            org_id: Organization ID
            
        Returns:
            List of device status dictionaries
            
        Raises:
            ServiceError: If the operation fails
        """
        try:
            if not self.client:
                raise ServiceError("MerakiService not initialized")
                
            statuses = self.client.get_organization_devices_statuses(org_id)
            await self.publish_event("device_statuses_retrieved", {"org_id": org_id, "count": len(statuses)})
            return statuses
        except HTTPException as e:
            self.logger.error(f"HTTP error getting device statuses: {str(e)}")
            raise ServiceError(f"Failed to get device statuses: {str(e)}") from e
        except Exception as e:
            self.logger.error(f"Error getting device statuses: {str(e)}")
            raise ServiceError(f"Failed to get device statuses: {str(e)}") from e
    
    async def get_network_health(self, network_id: str) -> Dict[str, Any]:
        """Get health information for a network.
        
        Args:
            network_id: Network ID
            
        Returns:
            Network health information
            
        Raises:
            ServiceError: If the operation fails
        """
        try:
            if not self.client:
                raise ServiceError("MerakiService not initialized")
                
            health = self.client.get_network_health(network_id)
            await self.publish_event("network_health_retrieved", {"network_id": network_id})
            return health
        except HTTPException as e:
            self.logger.error(f"HTTP error getting network health: {str(e)}")
            raise ServiceError(f"Failed to get network health: {str(e)}") from e
        except Exception as e:
            self.logger.error(f"Error getting network health: {str(e)}")
            raise ServiceError(f"Failed to get network health: {str(e)}") from e
    
    async def get_alerts(self, org_id: str) -> List[Dict[str, Any]]:
        """Get alerts for an organization.
        
        Args:
            org_id: Organization ID
            
        Returns:
            List of alert dictionaries
            
        Raises:
            ServiceError: If the operation fails
        """
        try:
            if not self.client:
                raise ServiceError("MerakiService not initialized")
                
            alerts = self.client.get_organization_alerts(org_id)
            await self.publish_event("alerts_retrieved", {"org_id": org_id, "count": len(alerts)})
            return alerts
        except HTTPException as e:
            self.logger.error(f"HTTP error getting alerts: {str(e)}")
            raise ServiceError(f"Failed to get alerts: {str(e)}") from e
        except Exception as e:
            self.logger.error(f"Error getting alerts: {str(e)}")
            raise ServiceError(f"Failed to get alerts: {str(e)}") from e
