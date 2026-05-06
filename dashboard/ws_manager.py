import asyncio
import json
from shared.logger import get_logger

logger = get_logger(__name__)

class WebSocketManager:
    """
    Bridge between the server's EventBus and connected browser clients.
    Manages active WebSocket connections and forwards events in real time.
    """

    def __init__(self):
        self._connections: set = set()

    async def register(self, websocket) -> None:
        """Add a new browser connection and keep it alive until it closes."""

        self._connections.add(websocket)
        logger.info(f"Dashboard client connected, total: {len(self._connections)}")

        try:
            await websocket.wait_closed()
        finally:
            self._connections.discard(websocket)
            logger.info(f"Dashboard client disconnected, total: {len(self._connections)}")

    async def _broadcast(self, payload: dict) -> None:
        """Send a JSON payload to all connected browser clients simultaneously."""

        if not self._connections:
            return

        message = json.dumps(payload)
        await asyncio.gather(
            *[ws.send(message) for ws in self._connections],
            return_exceptions=True
        )

    # EventBus Callbacks

    async def on_reading(self, data: dict) -> None:
        """Forward a normal sensor reading to the dashboard."""

        await self._broadcast({"event": "reading", **data})

    async def on_anomaly(self, data: dict) -> None:
        """Forward an anomaly event to the dashboard."""

        await self._broadcast({"event": "anomaly", **data})

    async def on_connection(self, data: dict) -> None:
        """Forward a sensor connection or disconnection event to the dashboard."""

        await self._broadcast({"event": "connection", **data})