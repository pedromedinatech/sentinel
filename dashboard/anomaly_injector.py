import asyncio
import random
from shared.logger import get_logger
from client.simulation_client import SimulationClient

logger = get_logger(__name__)

SENSOR_TYPES = ["cpu", "ram", "disk"]
MIN_INTERVAL = 15
MAX_INTERVAL = 45
MIN_BURST = 3
MAX_BURST = 7

class AnomalyInjector:
    """
    Autonomously injects anomalous sensor readings at random intervals.
    Runs as a background asyncio task alongside the main server.
    """

    def __init__(self):
        self._running = False

    async def run(self) -> None:
        """Main loop. Inject anomaly bursts at random intervals indefinitely."""

        self._running = True
        logger.info("Anomaly injector started")

        while self._running:
            wait = random.uniform(MIN_INTERVAL, MAX_INTERVAL)
            logger.debug(f"Next anomaly injection in {wait:.1f}s")
            await asyncio.sleep(wait)

            sensor_type = random.choice(SENSOR_TYPES)
            burst = random.randint(MIN_BURST, MAX_BURST)
            sensor_id = f"{sensor_type}_injector"

            logger.debug(f"Injecting {burst} anomalous readings on '{sensor_id}'")
            await self._inject_burst(sensor_id, sensor_type, burst)

    async def _inject_burst(self, sensor_id: str, sensor_type: str, count: int) -> None:
        """
        Connect a simulation client in inject mode, send a burst of anomalous
        readings, then disconnect.
        """

        client = SimulationClient(
            sensor_id=sensor_id,
            sensor_type=sensor_type,
            interval=1.0,
            inject_anomaly=True
        )

        connected = await client.connect()
        if not connected:
            logger.warning(f"Injector could not connect for '{sensor_id}'")
            return

        for _ in range(count):
            value = client.collect()
            await client.send_reading(value)
            await asyncio.sleep(1.0)

        if client._writer:
            client._writer.close()
            await client._writer.wait_closed()
            logger.info(f"Injection burst complete for '{sensor_id}'")

    def stop(self) -> None:
        """Stop the injector loop."""

        self._running = False