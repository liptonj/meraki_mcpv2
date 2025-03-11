"""Meraki Dashboard API client.

This module provides a wrapper around the Meraki Dashboard API client.
"""

import inspect
import logging
import os
import traceback
from typing import Any, Dict, List, Optional, Union

import meraki
from dotenv import load_dotenv
from fastapi import HTTPException

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)


class MerakiClient:
    """Wrapper around the Meraki Dashboard API client.

    This class provides methods for interacting with the Meraki Dashboard API,
    with error handling and response processing.

    Attributes:
        dashboard: The Meraki Dashboard API client instance.
    """

    def __init__(self, api_key: Optional[str] = None) -> None:
        """Initialize the Meraki client.

        Args:
            api_key: The Meraki Dashboard API key. If not provided,
                it will be loaded from the MERAKI_API_KEY environment variable.

        Raises:
            ValueError: If no API key is provided and none is found in environment.
        """
        # Get API key from environment if not provided
        self.api_key = api_key or os.environ.get("MERAKI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Meraki API key not provided and not found in environment variables."
            )

        # Initialize dashboard API client
        self.dashboard = meraki.DashboardAPI(
            api_key=self.api_key,
            base_url="https://api.meraki.com/api/v1",
            output_log=False,
            print_console=False,
            suppress_logging=True,
            retry_4xx_error=True,
            retry_4xx_error_wait_time=1,
            maximum_retries=3,
        )
        logger.info("Meraki Dashboard API client initialized.")

    def get_organizations(self) -> List[Dict[str, Any]]:
        """Get list of organizations.

        Returns:
            List of organization dictionaries.

        Raises:
            HTTPException: On API error.
        """
        try:
            return self.dashboard.organizations.getOrganizations()
        except meraki.APIError as e:
            caller_info = inspect.getframeinfo(inspect.currentframe().f_back)
            logger.error(f"Error getting organizations at {caller_info.filename}:{caller_info.lineno}: {str(e)}")
            self._handle_api_error(e)

    def get_organization_networks(self, org_id: str) -> List[Dict[str, Any]]:
        """Get list of networks for an organization.

        Args:
            org_id: The organization ID.

        Returns:
            List of network dictionaries.

        Raises:
            HTTPException: On API error.
        """
        try:
            return self.dashboard.organizations.getOrganizationNetworks(org_id)
        except meraki.APIError as e:
            logger.error("Error getting networks for org %s: %s", org_id, str(e))
            self._handle_api_error(e, {"resource_type": "organization", "resource_id": org_id})

    def get_network(self, network_id: str) -> Dict[str, Any]:
        """Get information about a network.

        Args:
            network_id: The network ID.

        Returns:
            Network information.

        Raises:
            HTTPException: On API error.
        """
        try:
            return self.dashboard.networks.getNetwork(network_id)
        except meraki.APIError as e:
            logger.error("Error getting network %s: %s", network_id, str(e))
            self._handle_api_error(e, {"resource_type": "network", "resource_id": network_id})

    def get_network_devices(self, network_id: str, **kwargs) -> List[Dict[str, Any]]:
        """Get devices in a network.

        Args:
            network_id: The network ID.
            **kwargs: Additional optional parameters that might be supported by the API.
                Note: 'perPage' is not supported for getNetworkDevices and will be ignored.

        Returns:
            List of device dictionaries.

        Raises:
            HTTPException: On API error.
        """
        try:
            # The Meraki SDK's getNetworkDevices method doesn't support perPage parameter
            # Make sure we don't pass it even if provided in kwargs
            if 'perPage' in kwargs:
                logger.warning(f"'perPage' parameter is not supported by getNetworkDevices() and will be ignored")
                kwargs.pop('perPage')
            if 'per_page' in kwargs:
                logger.warning(f"'per_page' parameter is not supported by getNetworkDevices() and will be ignored")
                kwargs.pop('per_page')
                
            devices = self.dashboard.networks.getNetworkDevices(network_id, **kwargs)
            return devices
            
        except Exception as e:
            # Get the current stack trace
            stack_trace = traceback.format_exc()
            # Get caller information
            caller_frame = inspect.currentframe().f_back
            caller_info = inspect.getframeinfo(caller_frame)
            # Log detailed error with line numbers and file path
            logger.error(f"Error getting devices for network {network_id} at {caller_info.filename}:{caller_info.lineno}: {str(e)}")
            logger.error(f"Stack trace: {stack_trace}")
            # Re-raise as API error for consistent handling
            if isinstance(e, meraki.APIError):
                self._handle_api_error(e, {"resource_type": "network", "resource_id": network_id})
            else:
                raise

    def get_organization_devices_statuses(
        self, org_id: str, statuses: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Get statuses for all devices in an organization.

        Args:
            org_id: The organization ID.
            statuses: Optional list of statuses to filter by.

        Returns:
            List of device status dictionaries.

        Raises:
            HTTPException: On API error.
        """
        try:
            params = {}
            if statuses:
                params["statuses"] = statuses
            return self.dashboard.organizations.getOrganizationDevicesStatuses(
                org_id, **params
            )
        except meraki.APIError as e:
            logger.error("Error getting device statuses for org %s: %s", org_id, str(e))
            self._handle_api_error(e, {"resource_type": "organization", "resource_id": org_id})

    def get_network_clients(
        self, network_id: str, timespan: Optional[int] = None, per_page: int = 100, total_pages: int = -1
    ) -> List[Dict[str, Any]]:
        """Get clients in a network with pagination support.

        Args:
            network_id: The network ID.
            timespan: Optional timespan in seconds.
            per_page: Number of items per page (default: 100, max: 1000)
            total_pages: Total number of pages to retrieve, -1 for all (default: -1)

        Returns:
            List of client dictionaries.

        Raises:
            HTTPException: On API error.
        """
        try:
            params = {
                'perPage': per_page
            }
            if timespan:
                params["timespan"] = timespan
            
            # Handle pagination
            all_items = []
            page = 1
            starting_after = None
            
            while True:
                # Add startingAfter parameter for pagination if we have it
                if starting_after:
                    params['startingAfter'] = starting_after
                
                # Get current page of data
                current_items = self.dashboard.networks.getNetworkClients(network_id, **params)
                
                # Add items to our result list
                if current_items:
                    all_items.extend(current_items)
                    logger.info(f"Retrieved page {page} with {len(current_items)} clients for network {network_id}")
                
                # Check if we should continue pagination
                if not current_items or len(current_items) < per_page or (total_pages != -1 and page >= total_pages):
                    break
                
                # Move to next page
                page += 1
                if current_items and len(current_items) > 0 and 'id' in current_items[-1]:
                    starting_after = current_items[-1]['id']
                else:
                    break
            
            logger.info(f"Retrieved a total of {len(all_items)} clients from network {network_id}")
            return all_items
        except meraki.APIError as e:
            logger.error(f"Error getting clients for network {network_id}: {str(e)}")
            self._handle_api_error(e, {"resource_type": "network", "resource_id": network_id})
            
    def get_network_wireless_clients(
        self, network_id: str, timespan: Optional[int] = None, per_page: int = 100, total_pages: int = -1, include_connectivity_history: bool = False
    ) -> List[Dict[str, Any]]:
        """Get wireless clients in a network with pagination support and enhanced data.
        
        This method retrieves all wireless clients and optionally includes their recent connectivity
        history to provide a more comprehensive view of client connection status.

        Args:
            network_id: The network ID.
            timespan: Optional timespan in seconds (default: 3600 - 1 hour).
            per_page: Number of items per page (default: 100, max: 1000)
            total_pages: Total number of pages to retrieve, -1 for all (default: -1)
            include_connectivity_history: Whether to include recent connectivity history (default: False)

        Returns:
            List of wireless client dictionaries with enhanced data.

        Raises:
            HTTPException: On API error.
        """
        try:
            # Use default timespan of 1 hour if not specified
            if timespan is None:
                timespan = 3600  # 1 hour in seconds
                
            params = {
                'perPage': per_page,
                'timespan': timespan,
                'connectionType': 'wireless'  # Filter to only wireless clients
            }
            
            # Handle pagination
            all_clients = []
            page = 1
            starting_after = None
            
            while True:
                # Add startingAfter parameter for pagination if we have it
                if starting_after:
                    params['startingAfter'] = starting_after
                
                # Get current page of wireless clients
                current_clients = self.dashboard.networks.getNetworkClients(network_id, **params)
                
                # Process clients and add to list
                if current_clients:
                    all_clients.extend(current_clients)
                    logger.info(f"Retrieved page {page} with {len(current_clients)} wireless clients for network {network_id}")
                
                    # Check if we should continue pagination
                    if len(current_clients) < per_page or (total_pages != -1 and page >= total_pages):
                        break
                    
                    # Move to next page
                    page += 1
                    if 'id' in current_clients[-1]:
                        starting_after = current_clients[-1]['id']
                    else:
                        break
                else:
                    break
            
            # If requested, enhance client data with connectivity history
            if include_connectivity_history and all_clients:
                logger.info(f"Enhancing {len(all_clients)} wireless clients with connectivity history")
                
                for i, client in enumerate(all_clients):
                    if 'id' in client or 'mac' in client:
                        client_id = client.get('id') or client.get('mac')
                        try:
                            # Get recent connection history (last 10 events max for performance)
                            conn_history = self.get_network_wireless_client_connection_history(
                                network_id=network_id,
                                client_id=client_id,
                                per_page=10,
                                total_pages=1,
                                timespan=timespan
                            )
                            
                            # Add connectivity history to client data
                            client['connectivity_history'] = conn_history
                            
                            # Add last connection status for easy access
                            if conn_history and len(conn_history) > 0:
                                last_conn = conn_history[0]  # Most recent connection event
                                client['last_connection_status'] = {
                                    'success': last_conn.get('successful', False),
                                    'timestamp': last_conn.get('ts', ''),
                                    'failure_reason': last_conn.get('failureReason', None)
                                }
                        except Exception as e:
                            logger.warning(f"Could not retrieve connectivity history for client {client_id}: {e}")
            
            logger.info(f"Retrieved a total of {len(all_clients)} wireless clients from network {network_id}")
            return all_clients
            
        except meraki.APIError as e:
            logger.error(f"Error getting wireless clients for network {network_id}: {str(e)}")
            self._handle_api_error(e, {"resource_type": "network", "resource_id": network_id})

    def get_network_client(
        self, network_id: str, client_id: str
    ) -> Dict[str, Any]:
        """Get information about a client.

        Args:
            network_id: The network ID.
            client_id: The client ID or MAC address.

        Returns:
            Client information.

        Raises:
            HTTPException: On API error.
        """
        try:
            return self.dashboard.networks.getNetworkClient(
                networkId=network_id, clientId=client_id
            )
        except meraki.APIError as e:
            logger.error("Error getting client %s: %s", client_id, str(e))
            self._handle_api_error(e, {"resource_type": "client", "resource_id": client_id})

    def get_network_client_usage_history(
        self, network_id: str, client_id: str, per_page: int = 100, total_pages: int = -1
    ) -> List[Dict[str, Any]]:
        """Get usage history for a client with pagination support.

        Args:
            network_id: The network ID.
            client_id: The client ID or MAC address.
            per_page: Number of items per page (default: 100, max: 1000)
            total_pages: Total number of pages to retrieve, -1 for all (default: -1)

        Returns:
            List of usage history entries.

        Raises:
            HTTPException: On API error.
        """
        try:
            params = {
                'per_page': per_page
            }
            
            # Handle pagination
            all_items = []
            page = 1
            
            while True:
                # Get current page of data
                current_items = self.dashboard.networks.getNetworkClientUsageHistory(
                    networkId=network_id, clientId=client_id, **params
                )
                all_items.extend(current_items)
                logger.info(f"Retrieved page {page} with {len(current_items)} usage history records for client {client_id}")
                
                # Check if we should continue pagination
                if len(current_items) < per_page or (total_pages != -1 and page >= total_pages):
                    break
                    
                # Move to next page
                page += 1
                if current_items and len(current_items) > 0:
                    # Use the appropriate field for pagination - may need adjustment based on API response format
                    if 'startingAfter' in params:
                        params['startingAfter'] = current_items[-1]['id'] if 'id' in current_items[-1] else current_items[-1]['ts']
                    else:
                        params['startingAfter'] = current_items[-1]['id'] if 'id' in current_items[-1] else current_items[-1]['ts']
                else:
                    break
            
            logger.info(f"Retrieved a total of {len(all_items)} usage history records for client {client_id}")
            return all_items
            
        except meraki.APIError as e:
            logger.error(f"Error getting usage history for client {client_id}: {str(e)}")
            self._handle_api_error(e, {"resource_type": "client", "resource_id": client_id})

    def get_network_client_connectivity(
        self, network_id: str, client_id: str, timespan: int, per_page: int = 100, total_pages: int = -1
    ) -> Dict[str, Any]:
        """Get connectivity information for a client with pagination support.

        Args:
            network_id: The network ID.
            client_id: The client ID or MAC address.
            timespan: Timespan in seconds.
            per_page: Number of items per page (default: 100, max: 1000)
            total_pages: Total number of pages to retrieve, -1 for all (default: -1)

        Returns:
            Client connectivity information.

        Raises:
            HTTPException: On API error.
        """
        try:
            params = {
                'perPage': per_page,
                'timespan': timespan
            }
            
            # Handle pagination
            all_items = []
            page = 1
            
            while True:
                # Get current page of data
                current_items = self.dashboard.networks.getNetworkClientConnectivity(
                    networkId=network_id, clientId=client_id, **params
                )
                
                # Check response format - this API might return a dictionary instead of a list
                # If it's a dictionary, we don't need pagination
                if isinstance(current_items, dict):
                    logger.info(f"Retrieved connectivity data for client {client_id} (not paginated)")
                    return current_items
                
                all_items.extend(current_items)
                logger.info(f"Retrieved page {page} with {len(current_items)} connectivity records for client {client_id}")
                
                # Check if we should continue pagination
                if len(current_items) < per_page or (total_pages != -1 and page >= total_pages):
                    break
                    
                # Move to next page
                page += 1
                if current_items and len(current_items) > 0:
                    # Use the appropriate field for pagination
                    if 'startingAfter' in params:
                        params['startingAfter'] = current_items[-1]['id'] if 'id' in current_items[-1] else current_items[-1]['ts']
                    else:
                        params['startingAfter'] = current_items[-1]['id'] if 'id' in current_items[-1] else current_items[-1]['ts']
                else:
                    break
            
            logger.info(f"Retrieved a total of {len(all_items)} connectivity records for client {client_id}")
            return all_items
            
        except meraki.APIError as e:
            logger.error(f"Error getting connectivity for client {client_id}: {str(e)}")
            self._handle_api_error(e, {"resource_type": "client", "resource_id": client_id})

    def get_network_health(self, network_id: str) -> Dict[str, Any]:
        """Get health information for a network.

        Args:
            network_id: The network ID.

        Returns:
            Network health information.

        Raises:
            HTTPException: On API error.
        """
        try:
            return self.dashboard.networks.getNetworkHealth(network_id)
        except meraki.APIError as e:
            logger.error("Error getting health for network %s: %s", network_id, str(e))
            self._handle_api_error(e, {"resource_type": "network", "resource_id": network_id})

    def get_organization_alerts(self, org_id: str) -> List[Dict[str, Any]]:
        """Get alerts for an organization.

        Args:
            org_id: The organization ID.

        Returns:
            List of alert dictionaries.

        Raises:
            HTTPException: On API error.
        """
        try:
            return self.dashboard.organizations.getOrganizationAlerts(org_id)
        except meraki.APIError as e:
            logger.error("Error getting alerts for org %s: %s", org_id, str(e))
            self._handle_api_error(e, {"resource_type": "organization", "resource_id": org_id})

    def get_network_wireless_settings(self, network_id: str) -> Dict[str, Any]:
        """Get wireless settings for a network.

        Args:
            network_id: The network ID.

        Returns:
            Wireless settings information.

        Raises:
            HTTPException: On API error.
        """
        try:
            return self.dashboard.wireless.getNetworkWirelessSettings(network_id)
        except meraki.APIError as e:
            logger.error(f"Error getting wireless settings for network {network_id}: {str(e)}")
            self._handle_api_error(e, {"resource_type": "network", "resource_id": network_id})
    
    def get_device(self, serial: str) -> Dict[str, Any]:
        """Get information about a device.

        Args:
            serial: The device serial number.

        Returns:
            Device information.

        Raises:
            HTTPException: On API error.
        """
        try:
            return self.dashboard.devices.getDevice(serial)
        except meraki.APIError as e:
            logger.error(f"Error getting device {serial}: {str(e)}")
            self._handle_api_error(e, {"resource_type": "device", "resource_id": serial})
    
    def get_network_client_traffic_history(
        self, network_id: str, client_id: str, per_page: int = 100, total_pages: int = -1
    ) -> List[Dict[str, Any]]:
        """Get traffic history for a client with pagination support.

        Args:
            network_id: The network ID.
            client_id: The client ID or MAC address.
            per_page: Number of items per page (default: 100, max: 1000)
            total_pages: Total number of pages to retrieve, -1 for all (default: -1)

        Returns:
            List of traffic history entries.

        Raises:
            HTTPException: On API error.
        """
        try:
            params = {
                'per_page': per_page
            }
            
            # Handle pagination
            all_items = []
            page = 1
            
            while True:
                # Get current page of data
                current_items = self.dashboard.networks.getNetworkClientTrafficHistory(
                    networkId=network_id, clientId=client_id, **params
                )
                all_items.extend(current_items)
                logger.info(f"Retrieved page {page} with {len(current_items)} traffic history records for client {client_id}")
                
                # Check if we should continue pagination
                if len(current_items) < per_page or (total_pages != -1 and page >= total_pages):
                    break
                    
                # Move to next page
                page += 1
                if current_items and len(current_items) > 0:
                    # Use the appropriate field for pagination
                    if 'startingAfter' in params:
                        params['startingAfter'] = current_items[-1]['id'] if 'id' in current_items[-1] else current_items[-1]['ts']
                    else:
                        params['startingAfter'] = current_items[-1]['id'] if 'id' in current_items[-1] else current_items[-1]['ts']
                else:
                    break
            
            logger.info(f"Retrieved a total of {len(all_items)} traffic history records for client {client_id}")
            return all_items
            
        except meraki.APIError as e:
            logger.error(f"Error getting traffic history for client {client_id}: {str(e)}")
            self._handle_api_error(e, {"resource_type": "client", "resource_id": client_id})
    
    def get_network_client_latency_stats(
        self, network_id: str, client_id: str, timespan: int, per_page: int = 100, total_pages: int = -1
    ) -> Dict[str, Any]:
        """Get latency statistics for a client with pagination support.

        Args:
            network_id: The network ID.
            client_id: The client ID or MAC address.
            timespan: Timespan in seconds.
            per_page: Number of items per page (default: 100, max: 1000)
            total_pages: Total number of pages to retrieve, -1 for all (default: -1)

        Returns:
            Client latency statistics.

        Raises:
            HTTPException: On API error.
        """
        try:
            params = {
                'perPage': per_page,
                'timespan': timespan
            }
            
            # Handle pagination
            all_items = []
            page = 1
            
            while True:
                # Get current page of data
                current_items = self.dashboard.networks.getNetworkClientLatencyStats(
                    networkId=network_id, clientId=client_id, **params
                )
                
                # Check response format - this API might return a dictionary instead of a list
                # If it's a dictionary, we don't need pagination
                if isinstance(current_items, dict):
                    logger.info(f"Retrieved latency statistics for client {client_id} (not paginated)")
                    return current_items
                
                all_items.extend(current_items)
                logger.info(f"Retrieved page {page} with {len(current_items)} latency statistics records for client {client_id}")
                
                # Check if we should continue pagination
                if len(current_items) < per_page or (total_pages != -1 and page >= total_pages):
                    break
                    
                # Move to next page
                page += 1
                if current_items and len(current_items) > 0:
                    # Use the appropriate field for pagination
                    if 'startingAfter' in params:
                        params['startingAfter'] = current_items[-1]['id'] if 'id' in current_items[-1] else current_items[-1]['ts']
                    else:
                        params['startingAfter'] = current_items[-1]['id'] if 'id' in current_items[-1] else current_items[-1]['ts']
                else:
                    break
            
            logger.info(f"Retrieved a total of {len(all_items)} latency statistics records for client {client_id}")
            return all_items
            
        except meraki.APIError as e:
            logger.error(f"Error getting latency statistics for client {client_id}: {str(e)}")
            self._handle_api_error(e, {"resource_type": "client", "resource_id": client_id})
    
    def get_network_client_application_usage(
        self, network_id: str, client_id: str, timespan: int, per_page: int = 100, total_pages: int = -1
    ) -> Dict[str, Any]:
        """Get application usage for a client with pagination support.

        Args:
            network_id: The network ID.
            client_id: The client ID or MAC address.
            timespan: Timespan in seconds.
            per_page: Number of items per page (default: 100, max: 1000)
            total_pages: Total number of pages to retrieve, -1 for all (default: -1)

        Returns:
            Client application usage statistics.

        Raises:
            HTTPException: On API error.
        """
        try:
            params = {
                'perPage': per_page,
                'timespan': timespan
            }
            
            # Handle pagination
            all_items = []
            page = 1
            
            while True:
                # Get current page of data
                current_items = self.dashboard.networks.getNetworkClientApplicationUsage(
                    networkId=network_id, clientId=client_id, **params
                )
                
                # Check response format - this API might return a dictionary instead of a list
                # If it's a dictionary, we don't need pagination
                if isinstance(current_items, dict):
                    logger.info(f"Retrieved application usage for client {client_id} (not paginated)")
                    return current_items
                
                all_items.extend(current_items)
                logger.info(f"Retrieved page {page} with {len(current_items)} application usage records for client {client_id}")
                
                # Check if we should continue pagination
                if len(current_items) < per_page or (total_pages != -1 and page >= total_pages):
                    break
                    
                # Move to next page
                page += 1
                if current_items and len(current_items) > 0:
                    # Use the appropriate field for pagination
                    if 'startingAfter' in params:
                        params['startingAfter'] = current_items[-1]['id'] if 'id' in current_items[-1] else current_items[-1]['ts']
                    else:
                        params['startingAfter'] = current_items[-1]['id'] if 'id' in current_items[-1] else current_items[-1]['ts']
                else:
                    break
            
            logger.info(f"Retrieved a total of {len(all_items)} application usage records for client {client_id}")
            return all_items
            
        except meraki.APIError as e:
            logger.error(f"Error getting application usage for client {client_id}: {str(e)}")
            self._handle_api_error(e, {"resource_type": "client", "resource_id": client_id})
    
    def get_network_client_security_events(
        self, network_id: str, client_id: str, timespan: int, per_page: int = 100, total_pages: int = -1
    ) -> List[Dict[str, Any]]:
        """Get security events for a client with pagination support.

        Args:
            network_id: The network ID.
            client_id: The client ID or MAC address.
            timespan: Timespan in seconds.
            per_page: Number of items per page (default: 100, max: 1000)
            total_pages: Total number of pages to retrieve, -1 for all (default: -1)

        Returns:
            List of security events.

        Raises:
            HTTPException: On API error.
        """
        try:
            params = {
                'perPage': per_page,
                'timespan': timespan
            }
            
            # Handle pagination
            all_items = []
            page = 1
            
            while True:
                # Get current page of data
                current_items = self.dashboard.networks.getNetworkClientSecurityEvents(
                    networkId=network_id, clientId=client_id, **params
                )
                all_items.extend(current_items)
                logger.info(f"Retrieved page {page} with {len(current_items)} security events for client {client_id}")
                
                # Check if we should continue pagination
                if len(current_items) < per_page or (total_pages != -1 and page >= total_pages):
                    break
                    
                # Move to next page
                page += 1
                if current_items and len(current_items) > 0:
                    # Use the appropriate field for pagination
                    if 'startingAfter' in params:
                        params['startingAfter'] = current_items[-1]['id'] if 'id' in current_items[-1] else current_items[-1]['ts']
                    else:
                        params['startingAfter'] = current_items[-1]['id'] if 'id' in current_items[-1] else current_items[-1]['ts']
                else:
                    break
            
            logger.info(f"Retrieved a total of {len(all_items)} security events for client {client_id}")
            return all_items
            
        except meraki.APIError as e:
            logger.error(f"Error getting security events for client {client_id}: {str(e)}")
            self._handle_api_error(e, {"resource_type": "client", "resource_id": client_id})
    
    def get_device_switch_ports(self, serial: str, per_page: int = 100, total_pages: int = -1) -> List[Dict[str, Any]]:
        """Get switch ports for a device.

        Args:
            serial: The device serial number.
            per_page: Number of items per page (default: 100, max: 1000)
            total_pages: Total number of pages to retrieve, -1 for all (default: -1)

        Returns:
            List of switch port dictionaries.

        Raises:
            HTTPException: On API error.
        """
        try:
            params = {
                'per_page': per_page
            }
            
            # Handle pagination
            all_items = []
            page = 1
            
            while True:
                # Get current page of data
                current_items = self.dashboard.switch.getDeviceSwitchPorts(serial, **params)
                all_items.extend(current_items)
                logger.info(f"Retrieved page {page} with {len(current_items)} switch ports for device {serial}")
                
                # Check if we should continue pagination
                if len(current_items) < per_page or (total_pages != -1 and page >= total_pages):
                    break
                    
                # Move to next page
                page += 1
                if current_items and 'portId' in current_items[-1]:
                    params['startingAfter'] = current_items[-1]['portId']
                else:
                    break
            
            logger.info(f"Retrieved a total of {len(all_items)} switch ports from device {serial}")
            return all_items
        except meraki.APIError as e:
            logger.error(f"Error getting switch ports for device {serial}: {str(e)}")
            self._handle_api_error(e, {"resource_type": "device", "resource_id": serial})

    def get_device_switch_port(self, serial: str, port_id: str) -> Dict[str, Any]:
        """Get information about a specific switch port.

        Args:
            serial: The device serial number.
            port_id: The port ID.

        Returns:
            Switch port information.

        Raises:
            HTTPException: On API error.
        """
        try:
            return self.dashboard.switch.getDeviceSwitchPort(serial, port_id)
        except meraki.APIError as e:
            logger.error(f"Error getting switch port {port_id} for device {serial}: {str(e)}")
            self._handle_api_error(e, {"resource_type": "port", "resource_id": port_id})

    def update_device_switch_port(self, serial: str, port_id: str, **kwargs) -> Dict[str, Any]:
        """Update a switch port configuration.

        Args:
            serial: The device serial number.
            port_id: The port ID.
            **kwargs: Additional parameters for port configuration.

        Returns:
            Updated switch port information.

        Raises:
            HTTPException: On API error.
        """
        try:
            return self.dashboard.switch.updateDeviceSwitchPort(serial, port_id, **kwargs)
        except meraki.APIError as e:
            logger.error(f"Error updating switch port {port_id} for device {serial}: {str(e)}")
            self._handle_api_error(e, {"resource_type": "port", "resource_id": port_id})

    def get_device_switch_ports_statuses(self, serial: str, per_page: int = 100, total_pages: int = -1) -> List[Dict[str, Any]]:
        """Get switch port statuses for a device.

        Args:
            serial: The device serial number.
            per_page: Number of items per page (default: 100, max: 1000)
            total_pages: Total number of pages to retrieve, -1 for all (default: -1)

        Returns:
            List of switch port status dictionaries.

        Raises:
            HTTPException: On API error.
        """
        try:
            params = {
                'per_page': per_page
            }
            
            # Handle pagination
            all_items = []
            page = 1
            
            while True:
                # Get current page of data
                current_items = self.dashboard.switch.getDeviceSwitchPortsStatuses(serial, **params)
                all_items.extend(current_items)
                logger.info(f"Retrieved page {page} with {len(current_items)} switch port statuses for device {serial}")
                
                # Check if we should continue pagination
                if len(current_items) < per_page or (total_pages != -1 and page >= total_pages):
                    break
                    
                # Move to next page
                page += 1
                if current_items and 'portId' in current_items[-1]:
                    params['startingAfter'] = current_items[-1]['portId']
                else:
                    break
            
            logger.info(f"Retrieved a total of {len(all_items)} switch port statuses from device {serial}")
            return all_items
        except meraki.APIError as e:
            logger.error(f"Error getting switch port statuses for device {serial}: {str(e)}")
            self._handle_api_error(e, {"resource_type": "device", "resource_id": serial})

    def get_device_switch_routing_interfaces(self, serial: str, per_page: int = 100, total_pages: int = -1) -> List[Dict[str, Any]]:
        """Get routing interfaces for a switch.

        Args:
            serial: The device serial number.
            per_page: Number of items per page (default: 100, max: 1000)
            total_pages: Total number of pages to retrieve, -1 for all (default: -1)

        Returns:
            List of routing interface dictionaries.

        Raises:
            HTTPException: On API error.
        """
        try:
            params = {
                'per_page': per_page
            }
            
            # Handle pagination
            all_items = []
            page = 1
            
            while True:
                # Get current page of data
                current_items = self.dashboard.switch.getDeviceSwitchRoutingInterfaces(serial, **params)
                all_items.extend(current_items)
                logger.info(f"Retrieved page {page} with {len(current_items)} routing interfaces for device {serial}")
                
                # Check if we should continue pagination
                if len(current_items) < per_page or (total_pages != -1 and page >= total_pages):
                    break
                    
                # Move to next page
                page += 1
                if current_items and 'interfaceId' in current_items[-1]:
                    params['startingAfter'] = current_items[-1]['interfaceId']
                else:
                    break
            
            logger.info(f"Retrieved a total of {len(all_items)} routing interfaces from device {serial}")
            return all_items
        except meraki.APIError as e:
            logger.error(f"Error getting routing interfaces for device {serial}: {str(e)}")
            self._handle_api_error(e, {"resource_type": "device", "resource_id": serial})

    def get_device_switch_routing_static_routes(self, serial: str, per_page: int = 100, total_pages: int = -1) -> List[Dict[str, Any]]:
        """Get static routes for a switch.

        Args:
            serial: The device serial number.
            per_page: Number of items per page (default: 100, max: 1000)
            total_pages: Total number of pages to retrieve, -1 for all (default: -1)

        Returns:
            List of static route dictionaries.

        Raises:
            HTTPException: On API error.
        """
        try:
            params = {
                'per_page': per_page
            }
            
            # Handle pagination
            all_items = []
            page = 1
            
            while True:
                # Get current page of data
                current_items = self.dashboard.switch.getDeviceSwitchRoutingStaticRoutes(serial, **params)
                all_items.extend(current_items)
                logger.info(f"Retrieved page {page} with {len(current_items)} static routes for device {serial}")
                
                # Check if we should continue pagination
                if len(current_items) < per_page or (total_pages != -1 and page >= total_pages):
                    break
                    
                # Move to next page
                page += 1
                if current_items and 'staticRouteId' in current_items[-1]:
                    params['startingAfter'] = current_items[-1]['staticRouteId']
                else:
                    break
            
            logger.info(f"Retrieved a total of {len(all_items)} static routes from device {serial}")
            return all_items
        except meraki.APIError as e:
            logger.error(f"Error getting static routes for device {serial}: {str(e)}")
            self._handle_api_error(e, {"resource_type": "device", "resource_id": serial})

    def get_device_switch_dhcp_server_policy(self, serial: str) -> Dict[str, Any]:
        """Get DHCP server policy for a switch.

        Args:
            serial: The device serial number.

        Returns:
            DHCP server policy information.

        Raises:
            HTTPException: On API error.
        """
        try:
            return self.dashboard.switch.getDeviceSwitchDhcpServerPolicy(serial)
        except meraki.APIError as e:
            logger.error(f"Error getting DHCP server policy for device {serial}: {str(e)}")
            self._handle_api_error(e, {"resource_type": "device", "resource_id": serial})

    def get_device_switch_stp(self, serial: str) -> Dict[str, Any]:
        """Get STP configuration for a switch.

        Args:
            serial: The device serial number.

        Returns:
            STP configuration information.

        Raises:
            HTTPException: On API error.
        """
        try:
            return self.dashboard.switch.getDeviceSwitchStp(serial)
        except meraki.APIError as e:
            logger.error(f"Error getting STP configuration for device {serial}: {str(e)}")
            self._handle_api_error(e, {"resource_type": "device", "resource_id": serial})

    def get_network_appliance_security_events(
        self, network_id: str, timespan: int = 86400, per_page: int = 100, total_pages: int = -1
    ) -> List[Dict[str, Any]]:
        """Get security events for a network with pagination support.

        Args:
            network_id: The network ID.
            timespan: Timespan in seconds (default: 86400 - 1 day).
            per_page: Number of items per page (default: 100, max: 1000)
            total_pages: Total number of pages to retrieve, -1 for all (default: -1)

        Returns:
            List of security events.

        Raises:
            HTTPException: On API error.
        """
        try:
            params = {
                'perPage': per_page,
                'timespan': timespan
            }
            
            # Handle pagination
            all_events = []
            page_count = 0
            starting_after = None
            has_more_pages = True
            
            while has_more_pages and (total_pages == -1 or page_count < total_pages):
                current_params = params.copy()
                if starting_after:
                    current_params['startingAfter'] = starting_after
                
                logger.debug(
                    f"Getting security events for network {network_id} "
                    f"(page {page_count + 1}, per_page={per_page})"
                )
                
                events = self.dashboard.appliance.getNetworkApplianceSecurityEvents(
                    network_id, **current_params
                )
                
                if not events or len(events) == 0:
                    has_more_pages = False
                else:
                    all_events.extend(events)
                    page_count += 1
                    
                    if len(events) < per_page:
                        has_more_pages = False
                    else:
                        starting_after = events[-1].get('id')
            
            logger.info(
                f"Retrieved {len(all_events)} security events from {page_count} pages "
                f"for network {network_id}"
            )
            
            return all_events
            
        except Exception as e:
            logger.error(f"Error getting security events for network {network_id}: {str(e)}")
            raise
    
    def get_network_appliance_vpn_stats(
        self, network_id: str, timespan: int = 86400, per_page: int = 100, total_pages: int = -1
    ) -> List[Dict[str, Any]]:
        """Get VPN statistics for a network with pagination support.

        Args:
            network_id: The network ID.
            timespan: Timespan in seconds (default: 86400 - 1 day).
            per_page: Number of items per page (default: 100, max: 1000)
            total_pages: Total number of pages to retrieve, -1 for all (default: -1)

        Returns:
            VPN statistics for the network.

        Raises:
            HTTPException: On API error.
        """
        try:
            params = {
                'perPage': per_page,
                'timespan': timespan
            }
            
            # Handle pagination
            all_stats = []
            page_count = 0
            starting_after = None
            has_more_pages = True
            
            while has_more_pages and (total_pages == -1 or page_count < total_pages):
                current_params = params.copy()
                if starting_after:
                    current_params['startingAfter'] = starting_after
                
                logger.debug(
                    f"Getting VPN stats for network {network_id} "
                    f"(page {page_count + 1}, per_page={per_page})"
                )
                
                stats = self.dashboard.appliance.getNetworkApplianceVpnStats(
                    network_id, **current_params
                )
                
                # For nested lists in response
                if stats and 'merakiVpnPeers' in stats:
                    vpn_peers = stats.get('merakiVpnPeers', [])
                    if vpn_peers:
                        all_stats = stats  # Store the complete response structure
                        # When we have peers, we should check if we have more pages based on peer count
                        if len(vpn_peers) < per_page:
                            has_more_pages = False
                        else:
                            # Use the last peer ID as the starting_after cursor if possible
                            if vpn_peers and 'networkId' in vpn_peers[-1]:
                                starting_after = vpn_peers[-1].get('networkId')
                            else:
                                has_more_pages = False
                    else:
                        has_more_pages = False
                else:
                    has_more_pages = False
                
                page_count += 1
            
            logger.info(
                f"Retrieved VPN stats from {page_count} pages for network {network_id}"
            )
            
            return all_stats
            
        except Exception as e:
            logger.error(f"Error getting VPN stats for network {network_id}: {str(e)}")
            raise
            
    def get_organizations(self, per_page: int = 100, total_pages: int = -1) -> List[Dict[str, Any]]:
        """Get all organizations accessible by the API key.

        Args:
            per_page: Number of items per page (default: 100, max: 1000)
            total_pages: Total number of pages to retrieve, -1 for all (default: -1)

        Returns:
            List of organization dictionaries.

        Raises:
            HTTPException: On API error.
        """
        try:
            params = {
                'per_page': per_page
            }
            
            # Handle pagination
            all_items = []
            page = 1
            
            while True:
                # Get current page of data
                current_items = self.dashboard.organizations.getOrganizations(**params)
                all_items.extend(current_items)
                logger.info(f"Retrieved page {page} with {len(current_items)} organizations")
                
                # Check if we should continue pagination
                if len(current_items) < per_page or (total_pages != -1 and page >= total_pages):
                    break
                    
                # Move to next page
                page += 1
                if current_items and 'id' in current_items[-1]:
                    params['startingAfter'] = current_items[-1]['id']
                else:
                    break
            
            logger.info(f"Retrieved a total of {len(all_items)} organizations")
            return all_items
        except meraki.APIError as e:
            logger.error(f"Error getting organizations: {str(e)}")
            self._handle_api_error(e, {"resource_type": "organizations"})

    def get_organization_networks(self, org_id: str, per_page: int = 100, total_pages: int = -1, **kwargs) -> List[Dict[str, Any]]:
        """Get all networks in an organization.

        Args:
            org_id: Organization ID.
            per_page: Number of items per page (default: 100, max: 1000)
            total_pages: Total number of pages to retrieve, -1 for all (default: -1)
            **kwargs: Additional optional parameters for filtering.

        Returns:
            List of network dictionaries.

        Raises:
            HTTPException: If org_id is missing or invalid, or on API error.
        """
        # Validate required parameters before making the API call
        self.validate_parameters(
            params={"org_id": org_id},
            required_params=["org_id"],
            resource_type="organization"
        )
        
        try:
            params = {
                'per_page': per_page,  # Use snake_case for consistency
                **kwargs
            }
            
            # Handle pagination
            all_items = []
            page = 1
            
            while True:
                # Get current page of data
                try:
                    current_items = self.dashboard.organizations.getOrganizationNetworks(org_id, **params)
                    all_items.extend(current_items)
                    logger.info(f"Retrieved page {page} with {len(current_items)} networks for organization {org_id}")
                except meraki.APIError as inner_e:
                    # Handle specific 404 errors more gracefully with better messages
                    if '404' in str(inner_e) and 'Not Found' in str(inner_e):
                        error_msg = (f"Organization with ID '{org_id}' was not found or your API key "
                                   f"doesn't have access to it. Verify both the organization ID and API permissions.")
                        logger.error(error_msg)
                        raise HTTPException(status_code=404, detail={
                            "error": {
                                "code": "organization_access_error",
                                "message": error_msg,
                                "details": {
                                    "resource_type": "organization",
                                    "resource_id": org_id
                                }
                            }
                        })
                    else:
                        # Re-raise other API errors to be handled by the outer catch
                        raise
                
                # Check if we should continue pagination
                if len(current_items) < per_page or (total_pages != -1 and page >= total_pages):
                    break
                    
                # Move to next page
                page += 1
                if current_items and 'id' in current_items[-1]:
                    params['startingAfter'] = current_items[-1]['id']
                else:
                    break
            
            logger.info(f"Retrieved a total of {len(all_items)} networks for organization {org_id}")
            return all_items
        except meraki.APIError as e:
            logger.error(f"Error getting networks for organization {org_id}: {str(e)}")
            self._handle_api_error(e, {"resource_type": "organization", "resource_id": org_id})
    
    def get_network_health(self, network_id: str) -> Dict[str, Any]:
        """Get health information for a network.

        Args:
            network_id: Network ID.

        Returns:
            Network health information.

        Raises:
            HTTPException: On API error.
        """
        try:
            return self.dashboard.networks.getNetworkHealth(network_id)
        except meraki.APIError as e:
            logger.error(f"Error getting health for network {network_id}: {str(e)}")
            self._handle_api_error(e, {"resource_type": "network", "resource_id": network_id})

    # The duplicate get_network_devices method has been completely removed
    # Now using only the implementation at the top of this file

    def get_network_wireless_ssids(self, network_id: str) -> List[Dict[str, Any]]:
        """Get SSIDs in a wireless network.

        Note: The Meraki wireless SSID endpoint does not support pagination parameters.

        Args:
            network_id: Network ID.

        Returns:
            List of SSID dictionaries.

        Raises:
            HTTPException: On API error.
        """
        try:
            # Get SSIDs without pagination as this endpoint doesn't support it
            ssids = self.dashboard.wireless.getNetworkWirelessSsids(network_id)
            logger.info(f"Retrieved {len(ssids)} SSIDs for network {network_id}")
            return ssids
        except meraki.APIError as e:
            logger.error(f"Error getting SSIDs for network {network_id}: {str(e)}")
            self._handle_api_error(e, {"resource_type": "network", "resource_id": network_id})

    def get_network_wireless_ssid(self, network_id: str, ssid_number: int) -> Dict[str, Any]:
        """Get details for a specific SSID in a wireless network.

        Args:
            network_id: Network ID.
            ssid_number: SSID number.

        Returns:
            SSID configuration dictionary.

        Raises:
            HTTPException: If required parameters are missing or on API error.
        """
        # Validate required parameters before making the API call
        self.validate_parameters(
            params={"network_id": network_id, "ssid_number": ssid_number},
            required_params=["network_id", "ssid_number"],
            resource_type="wireless SSID"
        )
        
        try:
            return self.dashboard.wireless.getNetworkWirelessSsid(network_id, ssid_number)
        except meraki.APIError as e:
            logger.error(f"Error getting SSID {ssid_number} for network {network_id}: {str(e)}")
            self._handle_api_error(e, {"resource_type": "ssid", "resource_id": str(ssid_number)})

    def get_device_wireless_status(self, serial: str) -> Dict[str, Any]:
        """Get wireless status for a device.

        Args:
            serial: Device serial number.

        Returns:
            Wireless status dictionary.

        Raises:
            HTTPException: If serial is missing or on API error.
        """
        # Validate required parameters before making the API call
        self.validate_parameters(
            params={"serial": serial},
            required_params=["serial"],
            resource_type="wireless device"
        )
        
        try:
            return self.dashboard.wireless.getDeviceWirelessStatus(serial)
        except meraki.APIError as e:
            logger.error(f"Error getting wireless status for device {serial}: {str(e)}")
            self._handle_api_error(e, {"resource_type": "device", "resource_id": serial})

    def get_network_wireless_failed_connections(self, network_id: str, **kwargs) -> Dict[str, Any]:
        """Get failed connections for a wireless network.

        Args:
            network_id: Network ID.
            **kwargs: Additional optional parameters, such as timespan, band, ssid, vlan, etc.

        Returns:
            Failed connections data.

        Raises:
            HTTPException: On API error.
        """
        try:
            return self.dashboard.wireless.getNetworkWirelessFailedConnections(network_id, **kwargs)
        except meraki.APIError as e:
            logger.error(f"Error getting failed connections for network {network_id}: {str(e)}")
            self._handle_api_error(e, {"resource_type": "network", "resource_id": network_id})

    def get_network_wireless_client_connectivity_events(self, network_id: str, client_id: str, **kwargs) -> List[Dict[str, Any]]:
        """Get connectivity events for a wireless client.

        Args:
            network_id: Network ID.
            client_id: Client ID.
            **kwargs: Additional optional parameters, such as timespan, perPage, etc.

        Returns:
            List of connectivity event dictionaries.

        Raises:
            HTTPException: On API error.
        """
        try:
            return self.dashboard.wireless.getNetworkWirelessClientConnectivityEvents(network_id, client_id, **kwargs)
        except meraki.APIError as e:
            logger.error(f"Error getting connectivity events for client {client_id} in network {network_id}: {str(e)}")
            self._handle_api_error(e, {"resource_type": "client", "resource_id": client_id})

    def get_network_wireless_client_connection_history(self, network_id: str, client_id: str, per_page: int = 100, total_pages: int = -1, **kwargs) -> List[Dict[str, Any]]:
        """Get connection history for a wireless client with full pagination support.

        Args:
            network_id: Network ID.
            client_id: Client ID.
            per_page: Number of items per page (default: 100, max: 1000)
            total_pages: Total number of pages to retrieve, -1 for all (default: -1)
            **kwargs: Additional optional parameters, such as timespan, etc.

        Returns:
            List of connection history dictionaries.

        Raises:
            HTTPException: On API error.
        """
        try:
            params = {
                'perPage': per_page,
                **kwargs
            }
            
            # Handle pagination
            all_items = []
            page = 1
            starting_after = None
            
            while True:
                # Add startingAfter parameter for pagination if we have it
                if starting_after:
                    params['startingAfter'] = starting_after
                
                # Get current page of data
                current_items = self.dashboard.wireless.getNetworkWirelessClientConnectionHistory(
                    network_id, client_id, **params
                )
                
                # Add items to our result list
                if current_items:
                    all_items.extend(current_items)
                    logger.info(f"Retrieved page {page} with {len(current_items)} connection history events for client {client_id}")
                
                # Check if we should continue pagination
                if not current_items or len(current_items) < per_page or (total_pages != -1 and page >= total_pages):
                    break
                
                # Move to next page - use connectionId as the pagination key
                page += 1
                if current_items and len(current_items) > 0:
                    # Use the last item's connection identifier as the next starting point
                    if 'connectionId' in current_items[-1]:
                        starting_after = current_items[-1]['connectionId']
                    # If no connectionId is available, try to use timestamp
                    elif 'ts' in current_items[-1]:
                        starting_after = current_items[-1]['ts']
                    else:
                        # No identifiable pagination marker, have to stop
                        break
                else:
                    break
            
            logger.info(f"Retrieved a total of {len(all_items)} connection history events for client {client_id}")
            return all_items
            
        except meraki.APIError as e:
            logger.error(f"Error getting connection history for client {client_id} in network {network_id}: {str(e)}")
            self._handle_api_error(e, {"resource_type": "client", "resource_id": client_id})

    def get_network_wireless_rf_profiles(self, network_id: str, per_page: int = 100, total_pages: int = -1) -> List[Dict[str, Any]]:
        """Get RF profiles for a wireless network.

        Args:
            network_id: Network ID.
            per_page: Number of items per page (default: 100, max: 1000)
            total_pages: Total number of pages to retrieve, -1 for all (default: -1)

        Returns:
            List of RF profile dictionaries.

        Raises:
            HTTPException: On API error.
        """
        try:
            params = {
                'per_page': per_page
            }
            
            # Handle pagination
            all_items = []
            page = 1
            
            while True:
                # Get current page of data
                current_items = self.dashboard.wireless.getNetworkWirelessRfProfiles(network_id, **params)
                all_items.extend(current_items)
                logger.info(f"Retrieved page {page} with {len(current_items)} RF profiles for network {network_id}")
                
                # Check if we should continue pagination
                if len(current_items) < per_page or (total_pages != -1 and page >= total_pages):
                    break
                    
                # Move to next page
                page += 1
                if current_items and 'id' in current_items[-1]:
                    params['startingAfter'] = current_items[-1]['id']
                else:
                    break
            
            logger.info(f"Retrieved a total of {len(all_items)} RF profiles for network {network_id}")
            return all_items
        except meraki.APIError as e:
            logger.error(f"Error getting RF profiles for network {network_id}: {str(e)}")
            self._handle_api_error(e, {"resource_type": "network", "resource_id": network_id})

    def get_device_wireless_channel_utilization(self, serial: str, **kwargs) -> Dict[str, Any]:
        """Get channel utilization for a wireless device.

        Args:
            serial: Device serial number.
            **kwargs: Additional optional parameters, such as timespan, band, etc.

        Returns:
            Channel utilization data.

        Raises:
            HTTPException: On API error.
        """
        try:
            return self.dashboard.wireless.getDeviceWirelessChannelUtilization(serial, **kwargs)
        except meraki.APIError as e:
            logger.error(f"Error getting channel utilization for device {serial}: {str(e)}")
            self._handle_api_error(e, {"resource_type": "device", "resource_id": serial})

    def get_device_wireless_clients(self, serial: str, per_page: int = 100, total_pages: int = -1, **kwargs) -> List[Dict[str, Any]]:
        """Get wireless clients for a device.

        Args:
            serial: Device serial number.
            per_page: Number of items per page (default: 100, max: 1000)
            total_pages: Total number of pages to retrieve, -1 for all (default: -1)
            **kwargs: Additional optional parameters, such as timespan, etc.

        Returns:
            List of wireless client dictionaries.

        Raises:
            HTTPException: On API error.
        """
        try:
            params = {
                'perPage': per_page,
                **kwargs
            }
            
            # Handle pagination
            all_items = []
            page = 1
            
            while True:
                # Get current page of data
                current_items = self.dashboard.wireless.getDeviceWirelessClients(serial, **params)
                all_items.extend(current_items)
                logger.info(f"Retrieved page {page} with {len(current_items)} wireless clients for device {serial}")
                
                # Check if we should continue pagination
                if len(current_items) < per_page or (total_pages != -1 and page >= total_pages):
                    break
                    
                # Move to next page
                page += 1
                if current_items and 'id' in current_items[-1]:
                    params['startingAfter'] = current_items[-1]['id']
                else:
                    break
            
            logger.info(f"Retrieved a total of {len(all_items)} wireless clients for device {serial}")
            return all_items
        except meraki.APIError as e:
            logger.error(f"Error getting wireless clients for device {serial}: {str(e)}")
            self._handle_api_error(e, {"resource_type": "device", "resource_id": serial})

    def validate_parameters(self, params: Dict[str, Any], required_params: List[str], resource_type: str) -> None:
        """Validate that required parameters are present and not None.
        
        Args:
            params: Dictionary of parameter names and their values
            required_params: List of parameter names that are required
            resource_type: The type of resource being accessed (for error messages)
            
        Raises:
            HTTPException: If any required parameter is missing or None
        """
        missing_params = [param for param in required_params 
                        if param not in params or params[param] is None]
        
        if missing_params:
            error_msg = f"Missing required parameters for {resource_type}: {', '.join(missing_params)}"
            logger.error(error_msg)
            raise HTTPException(status_code=400, detail=error_msg)
    
    def _handle_api_error(
        self, error: meraki.APIError, details: Optional[Dict[str, str]] = None
    ) -> None:
        """Handle Meraki API errors by converting them to HTTP exceptions.

        Args:
            error: The Meraki API error.
            details: Optional additional details about the error.

        Raises:
            HTTPException: Always raised with appropriate status code and details.
        """
        status_code = error.status
        error_details = details or {}

        # Add status to details
        error_details["status"] = status_code

        # Add retry-after if available
        if hasattr(error, "retry_after") and error.retry_after:
            error_details["retry_after"] = error.retry_after

        if status_code == 404:
            error_code = "resource_not_found"
            message = f"Resource not found: {str(error)}"
        elif status_code == 429:
            error_code = "rate_limit_exceeded"
            message = "Meraki API rate limit exceeded"
        elif status_code == 401:
            error_code = "unauthorized"
            message = "Unauthorized access to Meraki API"
        elif status_code == 403:
            error_code = "forbidden"
            message = "Forbidden access to Meraki API"
        else:
            error_code = "api_error"
            message = str(error)

        raise HTTPException(
            status_code=status_code,
            detail={
                "error": {
                    "code": error_code,
                    "message": message,
                    "details": error_details,
                }
            },
        )
