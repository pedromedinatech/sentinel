import asyncio
import json
import websockets
from shared.logger import get_logger

logger = get_logger(__name__)

class WebSocketServer:
    """
    Accepts WebSocket connections from browser clients.
    Forwards incoming commands to the client controller.
    """

    def __init__(self, ws_manager, client_controller, host: str = "localhost", port: int = 8765):
        self._ws_manager = ws_manager
        self._client_controller = client_controller
        self._host = host
        self._port = port

    async def _handle(self, websocket) -> None:
        """Handle a single browser connection."""

        await asyncio.gather(
            self._ws_manager.register(websocket),
            self._listen_commands(websocket)
        )

    async def _listen_commands(self, websocket) -> None:
        """Listen for commands sent from the dashboard."""
        
        try:
            async for raw in websocket:
                try:
                    command = json.loads(raw)
                    await self._client_controller.handle_command(command)
                except json.JSONDecodeError:
                    logger.warning(f"Invalid command received: {raw}")
        except Exception:
            pass

    async def start(self) -> None:
        """Start the WebSocket server."""

        async with websockets.serve(self._handle, self._host, self._port):
            logger.info(f"WebSocket server listening on ws://{self._host}:{self._port}")
            await asyncio.Future()