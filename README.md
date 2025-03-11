# Meraki MCP Server

## Overview

This project implements a standards-compliant Model Context Protocol (MCP) server that integrates with Cisco Meraki's Networks API. It serves as a context provider in the MCP ecosystem, transforming network infrastructure data into structured context that can be efficiently consumed by AI models and other context consumers.

The implementation utilizes Server-Sent Events (SSE) for real-time streaming of context data, following the MCP framework specifications.

## Features

- Full integration with Cisco Meraki's Dashboard API using the official Python library
- Real-time context updates via Server-Sent Events (SSE)
- Support for multiple query types (network status, device info, client data, alerts)
- JWT-based authentication and authorization
- Caching support for improved performance
- Comprehensive error handling with detailed error messages
- Fully typed code with Pydantic models
- Extensive logging for debugging and monitoring
- Advanced RF spectrum analysis for wireless network optimization
- Interference detection and channel quality assessment
- Data-driven recommendations for wireless improvements
- WiFi troubleshooting with knowledge base integration
- Specialized tools for managing various Meraki components (networks, clients, devices, etc.)

## Project Structure

```plaintext
meraki_mcpv2/
├── README.md                 # This file
├── pyproject.toml            # Python project configuration
├── requirements.txt          # Project dependencies
├── src/                      # Source code
│   └── meraki_mcp/           # Main package
│       ├── __init__.py       # Package initialization
│       ├── core/             # Core functionality
│       │   ├── __init__.py   # Core package initialization
│       │   └── meraki_client.py  # Meraki API client wrapper
│       ├── knowledge/        # Knowledge base modules
│       │   ├── __init__.py   # Knowledge base package initialization
│       │   ├── base.py       # Base knowledge base class
│       │   └── wifi_kb.py    # WiFi knowledge base implementation
│       ├── rf/               # RF Analysis modules
│       │   ├── __init__.py   # RF package initialization
│       │   ├── analyzer.py   # RF Analyzer implementation
│       │   ├── models.py     # RF data models
│       │   ├── rf_troubleshooter.py  # RF Troubleshooter implementation
│       │   └── spectrum.py   # Spectrum data structures
│       ├── services/         # Service modules
│       │   ├── __init__.py   # Services package initialization
│       │   ├── context_service.py  # Context generation service
│       │   └── sse_service.py  # Server-Sent Events service
│       ├── tools/            # Specialized tool modules
│       │   ├── __init__.py   # Tools package initialization
│       │   ├── appliance_tools.py   # Appliance management tools
│       │   ├── base.py       # Base tools functionality
│       │   ├── client_tools.py  # Client management tools
│       │   ├── device_tools.py   # Device management tools
│       │   ├── network_tools.py  # Network management tools
│       │   ├── organization_tools.py # Organization management tools
│       │   ├── rf_tools.py   # RF tools
│       │   ├── switch_tools.py  # Switch management tools
│       │   └── wireless_tools.py  # Wireless management tools
│       ├── utils/            # Utility functions
│       │   └── __init__.py   # Utils package initialization
│       ├── wifi/             # WiFi modules
│       │   ├── __init__.py   # WiFi package initialization
│       │   └── wifi_troubleshooter.py  # WiFi troubleshooting
│       └── server.py         # Main server application
└── tests/                    # Test directory
    ├── __init__.py           # Test package initialization
    ├── test_api.py           # API tests
    └── test_services.py      # Service tests
```

## Installation

### Prerequisites

- Python 3.8 or higher
- Cisco Meraki API key
- Redis (optional, for caching)

### Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/meraki_mcp.git
   cd meraki_mcp
   ```

2. Create a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -e .
   ```

4. Create a `.env` file in the project root directory:

   ```plaintext
   MERAKI_API_KEY=your_meraki_api_key
   ```

## Usage

### Start the server

```bash
uvicorn src.meraki_mcp.main:app --reload
```

The server will be available at <http://localhost:8000/sse>.


## Server-Sent Events (SSE) Implementation

The Meraki MCP system utilizes Server-Sent Events (SSE) as a key technology for delivering real-time network context data to clients. This section provides an overview of our SSE implementation.

### Architecture Overview

The SSE service architecture consists of the following components:

1. **SSE Service** (`src/meraki_mcp/services/sse_service.py`): Core service responsible for managing event streams and client connections
2. **Context Service** (`src/meraki_mcp/services/context_service.py`): Generates contextualized data from Meraki networks
3. **Server** (`src/meraki_mcp/server.py`): Exposes HTTP endpoints for clients to establish SSE connections
4. **Client Handlers**: Manage individual client connections and event delivery

```plaintext
┌──────────────┐        ┌───────────────┐        ┌─────────────┐
│              │        │               │        │             │
│  Meraki API  │◄──────►│ Context       │◄──────►│ SSE Service │
│              │        │ Service       │        │             │
└──────────────┘        └───────────────┘        └─────┬───────┘
                                                       │
                                                       ▼
                                               ┌───────────────┐
                                               │               │
                                               │   Server      │
                                               │   Endpoints   │
                                               │               │
                                               └───────┬───────┘
                                                       │
                                                       ▼
                                               ┌───────────────┐
                                               │               │
                                               │ SSE Clients   │
                                               │               │
                                               └───────────────┘
```

### How SSE Works in MCP

1. **Connection Establishment**:
   - Client makes an HTTP request to the SSE endpoint (`/mcp/stream`)
   - Server responds with `Content-Type: text/event-stream` and keeps the connection open
   - Connection remains open until explicitly closed by either party

2. **Event Generation**:
   - The Context Service continuously monitors Meraki network data
   - When relevant changes occur (e.g., device status changes, alerts, client connectivity events), new context data is generated
   - Events are formatted according to the SSE specification with a `data:` prefix and mandatory newlines

3. **Data Delivery**:
   - Events are pushed to connected clients in real-time
   - Each event contains a JSON payload with the updated context information
   - Clients receive data without needing to make additional requests

### Event Types

The MCP system emits several types of events through the SSE stream:

- **context_created**: Initial context creation complete
- **context_updated**: Incremental context updates
- **network_alert**: Critical network alerts
- **device_status_change**: Device state changes
- **client_connect**: New client connections
- **client_disconnect**: Client disconnection events

### Client Reconnection

The SSE implementation includes robust reconnection handling:

- Events include an `id:` field to track delivery state
- Clients can reconnect with a `Last-Event-ID` header to resume from where they left off
- Exponential backoff retry logic is recommended for client implementations

### Example Client Implementation

```javascript
// JavaScript SSE client example
const eventSource = new EventSource('/mcp/stream', {
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN'
  }
});

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received update:', data);
};

eventSource.onerror = (error) => {
  console.error('SSE connection error:', error);
  eventSource.close();
  // Implement reconnection logic here
};

// Listen for specific event types
eventSource.addEventListener('network_alert', (event) => {
  const alertData = JSON.parse(event.data);
  console.log('Network alert received:', alertData);
});
```

### Performance Considerations

- The SSE implementation supports thousands of concurrent connections
- Redis is used for event buffering to handle connection interruptions
- Event batching is available for high-frequency updates
- Server utilizes asynchronous I/O for optimal performance
- Connection monitoring ensures stale connections are cleaned up

### SSE API Examples

#### 1. Establishing an SSE Connection

**Request:**

```http
GET /mcp/stream HTTP/1.1
Host: localhost:8000
Accept: text/event-stream
Cache-Control: no-cache
```

**Response Headers:**

```http
HTTP/1.1 200 OK
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
Access-Control-Allow-Origin: *
X-Accel-Buffering: no
```

#### 2. Event Data Formats

##### Initial Context Creation Event

```
id: 1
event: context_created
data: {
  "context_id": "ctx_12345",
  "timestamp": "2025-03-11T19:44:12Z",
  "provider": "meraki",
  "data": {
    "network": {
      "id": "N_123456789",
      "name": "San Francisco Office",
      "status": "active",
      "timezone": "America/Los_Angeles"
    },
    "devices": [
      {
        "serial": "Q2XX-XXXX-XXXX",
        "model": "MR46",
        "name": "AP-3rd-Floor-1",
        "status": "online",
        "lastReportedAt": "2025-03-11T19:43:55Z"
      },
      {
        "serial": "Q2XX-XXXX-XXXY",
        "model": "MR46",
        "name": "AP-3rd-Floor-2",
        "status": "online",
        "lastReportedAt": "2025-03-11T19:44:02Z"
      }
    ],
    "clients": [...],
    "alerts": []
  }
}

```

##### Device Status Change Event

```
id: 2
event: device_status_change
data: {
  "context_id": "ctx_12345",
  "timestamp": "2025-03-11T19:46:32Z",
  "provider": "meraki",
  "device": {
    "serial": "Q2XX-XXXX-XXXY",
    "name": "AP-3rd-Floor-2",
    "previous_status": "online",
    "current_status": "offline",
    "lastReportedAt": "2025-03-11T19:46:31Z"
  }
}

```

##### Network Alert Event

```
id: 3
event: network_alert
data: {
  "context_id": "ctx_12345",
  "timestamp": "2025-03-11T19:48:16Z",
  "provider": "meraki",
  "alert": {
    "id": "alert_789123",
    "type": "access_point_down",
    "severity": "warning",
    "network_id": "N_123456789",
    "device_serial": "Q2XX-XXXX-XXXY",
    "details": {
      "message": "Access point AP-3rd-Floor-2 is offline",
      "occurred_at": "2025-03-11T19:46:32Z"
    },
    "recommended_action": "Check power and network connectivity to the device"
  }
}

```

##### Client Connection Event

```
id: 4
event: client_connect
data: {
  "context_id": "ctx_12345",
  "timestamp": "2025-03-11T19:50:44Z",
  "provider": "meraki",
  "client": {
    "id": "k1f892dfc",
    "mac": "00:11:22:33:44:55",
    "description": "Employee Laptop",
    "ip": "10.0.1.101",
    "user": "john.doe",
    "device_serial": "Q2XX-XXXX-XXXX",
    "ssid": "Corporate-Secure",
    "connected_at": "2025-03-11T19:50:44Z",
    "vlan": 10,
    "connection_history": {
      "successful_connections": 153,
      "failed_connections": 2,
      "last_connection_status": "success"
    },
    "connection_stats": {
      "signal": -65,
      "rssi": 65,
      "quality": 85,
      "band": "5GHz",
      "channel": 44
    }
  }
}

```

##### Context Updated Event

```
id: 5
event: context_updated
data: {
  "context_id": "ctx_12345",
  "timestamp": "2025-03-11T19:51:15Z",
  "provider": "meraki",
  "sequence": 5,
  "updates": {
    "devices": [
      {
        "serial": "Q2XX-XXXX-XXXX",
        "status": "online",
        "clients": 12,
        "lastReportedAt": "2025-03-11T19:51:10Z",
        "metrics": {
          "cpu": 24,
          "memory": 38,
          "wireless": {
            "channel_utilization": {
              "2.4GHz": 21,
              "5GHz": 35
            }
          }
        }
      }
    ],
    "clients_connected": 1,
    "clients_disconnected": 0
  }
}

```

#### 3. Natural Language Interaction Examples

##### Example 1: User Request and LLM Response

This example demonstrates how a network administrator would interact with the system using natural language and how the LLM provides insights based on real-time data from the SSE stream:

**User Request:**

```
Our employees in the east wing are complaining about slow Wi-Fi and frequent disconnections, especially during meetings. What could be causing this and how can we fix it?
```

**LLM Response:**

```
I've analyzed the network data for the east wing and identified the likely cause of the Wi-Fi issues. Here's what I found:

**Root Cause**: Channel congestion on the 2.4GHz band is affecting two access points in the east wing (AP-East-1 and AP-East-2). The current configuration is problematic for several reasons:

1. Both access points are using overlapping channels (channels 1 and 2)
2. The channel width is set to 40MHz, which is too wide for the crowded 2.4GHz spectrum in your environment
3. Only 32% of capable devices are connecting to the less congested 5GHz band
4. There's significant interference from nearby Bluetooth devices and non-WiFi equipment

**Recommended Solutions**:

1. **Channel Reassignment**: Move AP-East-1 to channel 6 and AP-East-2 to channel 11. This will eliminate co-channel interference.
   
2. **Optimize Channel Width**: Reduce the channel width from 40MHz to 20MHz on both access points. This will decrease throughput slightly but significantly reduce interference.
   
3. **Enable Band Steering**: Configure your network to encourage 5GHz-capable clients to connect to the less congested 5GHz band.

4. **Maintain Critical Features**: I've ensured that Open-Enhanced remains enabled, as this is a critical security feature that must always be maintained.

I can implement these changes for you automatically, or provide step-by-step instructions if you prefer to make them manually. Would you like me to proceed with the automatic implementation?
```

##### Example 2: Automated RF Analysis Request

**User Request:**

```
I've been getting complaints about poor coverage in our new conference room. Can you analyze the spectrum and tell me if there are any issues?
```

**LLM Response:**

```
I'll analyze the RF spectrum for your conference room area. Let me check the access points serving that location and examine their performance.

**Analysis Results**:

I've completed the RF analysis for the access points covering your new conference room, and I've found several issues that are likely causing the poor coverage:

1. **Signal Strength Issue**: The primary access point (AP-Conf-1) is operating at a lower power level than optimal. The 5GHz radio is currently set to only 8dBm, which is insufficient for the room size and wall materials.

2. **Interference Detected**: I've identified non-WiFi interference on channels 1-3 of the 2.4GHz band, likely coming from Bluetooth devices in the adjacent rooms. The interference has a duty cycle of approximately 35%, which significantly impacts performance.

3. **Channel Utilization**: The 5GHz channels currently in use have high utilization rates from neighboring access points, particularly channels 36-48.

4. **Client Distribution**: During meetings, up to 25 devices are connecting to a single access point, exceeding its optimal capacity.

**Recommended Optimizations**:

1. **Increase Power**: Adjust the 5GHz radio power on AP-Conf-1 from 8dBm to 15dBm to improve coverage throughout the conference room.

2. **Channel Reassignment**: Move the 2.4GHz radio from channel 1 to channel 11 to avoid the detected Bluetooth interference.

3. **Add Capacity**: Consider installing a secondary access point on the opposite side of the conference room to better distribute client load during large meetings.

4. **5GHz Channel Optimization**: Switch the 5GHz radio to use channels 149-161, which have shown much lower utilization in your environment.

Would you like me to implement the power and channel changes immediately, or would you prefer to schedule these changes for off-hours?
```

#### 4. Common Use Case Examples

##### Monitoring Device Health

1. Client establishes SSE connection with filter for device_status_change events
2. Client receives real-time notifications when device status changes occur
3. Client application can immediately update dashboards, send alerts, or trigger workflows

##### Network Troubleshooting

1. When a user reports connectivity issues, support staff establishes SSE connection for specific network
2. Stream provides real-time client connection/disconnection events and signal quality metrics
3. Support staff can observe patterns and diagnose issues without repeatedly polling the API

##### Security Monitoring

1. Security system establishes persistent SSE connection to monitor client activity
2. Unexpected client connections trigger alerts for security investigation
3. Connection patterns are analyzed in real-time to detect potential security threats

### LLM Integration Examples

The Meraki MCP system can be integrated with Large Language Models (LLMs) to provide natural language understanding of network status and generate human-readable insights. Here's an example of how an LLM would interact with the system:

#### Example Request to LLM

```http
POST /mcp/llm/analyze HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "network_id": "N_123456789",
  "query": "What's causing the performance issues in the east wing?",
  "context": {
    "timeframe": "24h",
    "specific_location": "East Wing, 3rd Floor"
  }
}
```

#### Example LLM Response

```json
{
  "response": {
    "answer": "The performance issues in the east wing appear to be caused by channel congestion on the 2.4GHz band affecting two access points (AP-East-1 and AP-East-2). Analysis of the past 24 hours shows high utilization (68% and 72%) on channels 1 and 2, primarily due to interference from nearby Bluetooth devices and non-WiFi equipment.\n\nThe affected access points are currently configured with 40MHz channel width, which contributes to the congestion in this already crowded spectrum. Additionally, only 32% of capable client devices are connecting to the less congested 5GHz band.\n\nI recommend the following actions to resolve these issues:\n\n1. Reconfigure AP-East-1 to use channel 6 and AP-East-2 to use channel 11\n2. Reduce channel width from 40MHz to 20MHz on both access points\n3. Enable band steering to encourage more clients to connect to 5GHz\n4. Keep the Open-Enhanced feature enabled as it's critical for security\n\nThese changes should reduce the congestion and improve performance by approximately 35-40% based on current usage patterns.",
    "confidence_score": 87,
    "data_sources": [
      "rf_analysis_456",
      "wifi_ts_789",
      "client_connection_logs",
      "spectrum_analyzer_data"
    ]
  },
  "supporting_data": {
    "visualizations": [
      "/api/visualizations/network_N_123456789/channel_utilization",
      "/api/visualizations/network_N_123456789/interference_heatmap"
    ],
    "related_devices": [
      {
        "serial": "Q2XX-XXXX-AAA1",
        "name": "AP-East-1",
        "details_url": "/api/devices/Q2XX-XXXX-AAA1"
      },
      {
        "serial": "Q2XX-XXXX-AAA2",
        "name": "AP-East-2",
        "details_url": "/api/devices/Q2XX-XXXX-AAA2"
      }
    ],
    "recommendations": {
      "immediate_actions": [
        {
          "description": "Change AP-East-1 channel to 6",
          "api_endpoint": "/api/devices/Q2XX-XXXX-AAA1/radio/settings",
          "settings": {
            "band": "2.4GHz",
            "channel": 6,
            "width": 20
          }
        },
        {
          "description": "Change AP-East-2 channel to 11",
          "api_endpoint": "/api/devices/Q2XX-XXXX-AAA2/radio/settings",
          "settings": {
            "band": "2.4GHz",
            "channel": 11,
            "width": 20
          }
        }
      ],
      "additional_suggestions": {
        "policy_changes": [
          "Enable band steering for all east wing SSIDs"
        ],
        "hardware_changes": [
          "Consider additional 5GHz coverage in conference rooms"
        ]
      }
    }
  },
  "conversation_id": "conv_12345678",
  "timestamp": "2025-03-11T19:50:25Z"
}
```

This example shows how the LLM contextualizes network data, identifies the root cause of issues, and provides detailed recommendations while respecting critical constraints (like maintaining the Open-Enhanced feature).

## WiFi Configuration Best Practices

### Critical WiFi Features

- **Open-Enhanced**: This is a critical feature in Meraki wireless configurations that must always remain enabled. The system is designed to never recommend disabling this feature in any wireless troubleshooting or optimization recommendations. Open-Enhanced provides essential functionality for proper wireless network operation and security.

## RF Analysis Module

The MCP server includes a comprehensive RF analysis module for wireless network optimization:

### Features

- Spectrum data analysis for 2.4 GHz, 5 GHz, and 6 GHz frequency bands
- Identification of common interference sources (microwave ovens, Bluetooth devices, radar systems)
- Channel quality assessment with scoring system (0-100)
- Intelligent recommendations for channel selection and width
- Detailed analysis summaries with actionable insights
- Support for batch analysis of multiple access points
- Automated troubleshooting with knowledge base integration
- Issue detection and remediation recommendations

### RF Analyzer Example

```python
from meraki_mcp.rf.analyzer import RFAnalyzer
from meraki_mcp.rf.spectrum import SpectrumData, FrequencyBand, ChannelWidth, SpectrumDataPoint

# Create spectrum data
spectrum_data = SpectrumData(
    access_point_serial="Q2XX-XXXX-XXXX",
    band=FrequencyBand.BAND_5GHZ,
    channel=36,
    channel_width=ChannelWidth.WIDTH_40MHZ
)

# Add data points
spectrum_data.add_data_point(SpectrumDataPoint(
    frequency=5180.0,
    power=-75.0,
    utilization=15.0,
    timestamp=1709652000
))

# Create analyzer and run analysis
analyzer = RFAnalyzer()
analysis = analyzer.analyze_spectrum(spectrum_data)

# Print recommendations
for recommendation in analysis.recommendations:
    print(f"- {recommendation}")
```

### RF Troubleshooter

The RF Troubleshooter integrates RF spectrum analysis with the knowledge base to automatically diagnose wireless issues and provide detailed remediation steps:

#### Features

- Automated issue identification and troubleshooting
- Integration with WiFi knowledge base for expert recommendations
- Confidence scoring for diagnosis reliability
- Detailed troubleshooting reports with references to knowledge articles
- Support for batch troubleshooting across multiple access points
- Async support for efficient processing

#### Example Usage

```python
import asyncio
from meraki_mcp.rf.rf_troubleshooter import RFTroubleshooter
from meraki_mcp.rf.spectrum import SpectrumData, FrequencyBand, ChannelWidth, SpectrumDataPoint

async def troubleshoot_wireless_issue():
    # Create spectrum data
    spectrum_data = SpectrumData(
        access_point_serial="Q2XX-XXXX-XXXX",
        band=FrequencyBand.BAND_5GHZ,
        channel=36,
        channel_width=ChannelWidth.WIDTH_40MHZ
    )
    
    # Add data points (simplified for example)
    spectrum_data.add_data_point(SpectrumDataPoint(
        frequency=5180.0,
        power=-75.0,
        utilization=15.0,
        timestamp=1709652000
    ))
    
    # Create troubleshooter
    troubleshooter = RFTroubleshooter()
    
    # Initialize knowledge base (required before troubleshooting)
    await troubleshooter.initialize_knowledge_base()
    
    # Perform troubleshooting
    result = await troubleshooter.troubleshoot(spectrum_data)
    
    # Print troubleshooting results
    print(f"Issue: {result.issue_type} (Confidence: {result.confidence}%)")
    print(f"Description: {result.issue_description}")
    print("\nRecommendations:")
    for recommendation in result.recommendations:
        print(f"- {recommendation}")
    
    # Access knowledge base references
    print("\nKnowledge Base References:")
    for ref in result.knowledge_references:
        print(f"- {ref['title']}: {ref['url']}")

# Run the async function
asyncio.run(troubleshoot_wireless_issue())
```

## Development

### Testing

```bash
pytest
```

### Code Formatting

```bash
black src tests
isort src tests
```

### Type Checking

```bash
mypy src
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
