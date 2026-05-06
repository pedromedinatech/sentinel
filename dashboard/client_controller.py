import asyncio
from shared.logger import get_logger
from client.simulation_client import SimulationClient

logger = get_logger(__name__)

class ClientController:
    """
    Manages simulated sensor clients launched from the dashboard.
    Handles start and stop commands received via WebSocket.
    """

    def __init__(self):
        self._tasks: dict[str, asyncio.Task] = {}
        self._counter: dict[str, int] = {}

    async def handle_command(self, command: dict) -> None:
        """Route an incoming dashboard command to the appropriate handler."""

        cmd = command.get("command")

        if cmd == "start_client":
            await self._start_client(
                sensor_type=command.get("sensor_type", "cpu"),
                inject=command.get("inject", False)
            )
        elif cmd == "stop_client":
            await self._stop_client(command.get("sensor_id", ""))
        else:
            logger.warning(f"Unknown command: {cmd}")

    async def _start_client(self, sensor_type: str, inject: bool) -> None:
        """Launch a new simulated sensor client as an asyncio task."""

        self._counter[sensor_type] = self._counter.get(sensor_type, 0) + 1
        sensor_id = f"{sensor_type}_sim_{self._counter[sensor_type]}"

        client = SimulationClient(
            sensor_id=sensor_id,
            sensor_type=sensor_type,
            interval=2.0,
            inject_anomaly=inject
        )

        task = asyncio.create_task(client.run())
        self._tasks[sensor_id] = task
        logger.info(f"Started simulated client '{sensor_id}' (inject={inject})")

    async def _stop_client(self, sensor_id: str) -> None:
        """Cancel a running simulated client task."""

        task = self._tasks.pop(sensor_id, None)
        if task:
            task.cancel()
            logger.info(f"Stopped simulated client '{sensor_id}'")
        else:
            logger.warning(f"No active client found with id '{sensor_id}'")

    def active_clients(self) -> list[str]:
        """Return a list of currently active simulated client IDs."""
        
        return list(self._tasks.keys())