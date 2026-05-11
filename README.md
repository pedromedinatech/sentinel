# Sentinel

Sentinel is a concurrent sensor monitoring system built in Python. It demonstrates
how classical software engineering concepts, event-driven architecture, the Observer
pattern, and a multi-stage processing pipeline all come together in a real networked
application.

The system accepts connections from multiple sensor clients simultaneously, processes
each reading through a validation pipeline, and notifies subscribers in real time
when anomalies are detected.

--- 

## Architecture
```
[Sensor Client A] ─┐
[Sensor Client B] ─┼──► [TCP Server] ──► [Pipeline] ──► [EventBus] ──► [Monitor]
[Sensor Client C] ─┘
```

**Server** - manages concurrent client connections using Python's `asyncio` event loop.
Each client runs in its own coroutine, allowing the server to handle multiple sensors
simultaneously without threads.

**Pipeline** - every incoming reading passes through three sequential stages:
1. `Validator`: rejects malformed messages and physically impossible values
2. `ThresholdDetector`: flags values that exceed configurable alert thresholds
3. `ZScoreDetector`: detects statistical anomalies using a sliding window Z-score

**EventBus** - implements the Observer pattern. When the pipeline flags an anomaly,
the server publishes an event to the bus. Any number of subscribers can react to it
independently, without the server knowing who they are.

**Monitor** - a subscriber that receives anomaly events and logs structured alerts.

---

## Design decisions

**Why asyncio over threads?**
Sensor clients spend most of their time waiting between readings. asyncio handles
this efficiently with a single-threaded event loop with no thread overhead, no shared
state issues, no race conditions.

**Why a multi-stage pipeline?**
Each stage has a single responsibility and a different failure mode. Physical
impossibilities (CPU at 150% usage) are caught by the Validator before they reach the
statistical detector. Alert thresholds are configurable independently of physical
limits. Stages can be added, removed or reordered without touching each other.

**Why separate PHYSICAL_LIMITS from ALERT_THRESHOLDS?**
Physical limits define what is impossible in the real world. Alert thresholds define
what is considered abnormal in this deployment. Mixing them would couple hardware
constraints with operational configuration, two concerns that change for different
reasons.

**Why hash the shared secret?**
Even in a non-production context, storing plain text secrets in source code is poor
practice. The server stores a SHA-256 hash of the secret and compares hashes at
authentication time. The plain text secret never touches the server's comparison logic.

**Why WebSockets for the dashboard?**
The dashboard needs to receive data continuously without polling. WebSockets provide
a persistent bidirectional connection, because the server pushes events to the browser the
moment they occur, with no request-response overhead. The WebSocket manager is simply
another EventBus subscriber, requiring no changes to the server or pipeline.

---

## Project Structure
```
sentinel/
├── server/
│   ├── server.py           # entry point, asyncio event loop
│   ├── client_handler.py   # per-client lifecycle management
│   ├── registry.py         # in-memory authenticated sensor registry
│   ├── event_bus.py        # observer pattern implementation
│   └── pipeline/
│       ├── validator.py    # stage 1 - schema and physical limits
│       ├── threshold.py    # stage 2 - configurable alert thresholds
│       └── zscore.py       # stage 3 - sliding window Z-score
├── client/
│   ├── base_client.py      # shared connection and handshake logic
│   ├── psutil_client.py    # real system metrics via psutil
│   └── simulation_client.py # configurable simulated readings
├── monitor/
│   └── monitor.py          # anomaly event subscriber
├── dashboard/
│   ├── dashboard.html      # real-time web dashboard
│   ├── ws_manager.py       # WebSocket manager, EventBus subscriber
│   ├── ws_server.py        # WebSocket server on port 8765
│   ├── http_server.py      # static HTTP server on port 8080
│   ├── client_controller.py # manages simulated clients from dashboard
│   └── anomaly_injector.py  # automatic anomaly injection at random intervals
└── shared/
    ├── config.py           # central configuration
    ├── protocol.py         # message definitions and serialization
    └── logger.py           # shared logging setup
```
--- 

## Getting Started

**Requirements:** Python 3.10+
```bash
# Clone the repository
git clone https://github.com/pedromedinatech/sentinel.git
cd sentinel

# Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # macOS / Linux

# Install dependencies
pip install -r requirements.txt
```

---

## Running the system

A single command starts everything, the TCP server, WebSocket server, HTTP server,
four real sensor clients and the automatic anomaly injector:

```bash
python -m server.server
```
Once running, open the dashboard in your browser:

http://localhost:8080

The dashboard connects automatically via WebSocket and begins displaying live data.
No additional setup is required.

---

## Dashboard

The dashboard provides a real-time view of the system with no page reloads:

**NODES view** - live telemetry charts per sensor with a 30-point sliding window.
Anomalous readings appear as red dots on the chart. The left panel shows all connected
sensors and their current values, colour-coded by threshold proximity.

**ALERTS view** - full-screen anomaly feed showing every detection in real time,
with timestamp, sensor ID, value, pipeline stage and reason. Colour-coded by stage:
red for Validator, orange for ThresholdDetector, yellow for ZScoreDetector.

**Sensor control** - start and stop simulated sensor clients directly from the
dashboard without touching the terminal. Supports all four sensor types and anomaly
injection mode.

---

## Manual sensor clients

Additional clients can be launched from the terminal or from the dashboard:

```bash
# Real system metrics
python -m client.psutil_client

# Simulated normal readings
python -m client.simulation_client <sensor_id> <sensor_type>

# Simulated anomalous readings
python -m client.simulation_client <sensor_id> <sensor_type> inject

# Examples
python -m client.simulation_client cpu_sim cpu
python -m client.simulation_client ram_sim ram inject
```

**Available sensor types:** `cpu`, `ram`, `disk`, `network`

---

## Configuration

All tuneable parameters live in `shared/config.py`:

| Parameter | Default | Description |
|---|---|---|
| `HOST` | `127.0.0.1` | Server host |
| `PORT` | `9999` | TCP server port |
| `WS_PORT` | `8765` | WebSocket server port |
| `HTTP_PORT` | `8080` | Dashboard HTTP port |
| `WINDOW_SIZE` | `10` | Readings in the Z-score sliding window |
| `ZSCORE_THRESHOLD` | `3` | Standard deviations to flag a statistical anomaly |
| `ALERT_THRESHOLDS` | see config | Per-sensor alert ranges |
| `PHYSICAL_LIMITS` | see config | Per-sensor physical boundaries |
| `ZSCORE_EXCLUDED` | `["network"]` | Sensor types excluded from Z-score detection |

---

## What this project includes

- Concurrent server architecture with `asyncio` coroutines
- Observer pattern via a decoupled `EventBus`
- Multi-stage processing pipeline with single-responsibility stages
- Strategy pattern, anomaly detectors are interchangeable pipeline components
- Shared secret authentication with SHA-256 hashing
- Clean separation between transport, domain and notification layers
- Structured logging across all modules
- Real-time browser dashboard via WebSocket