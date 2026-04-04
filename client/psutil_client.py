# client/psutil_client.py
import asyncio
import psutil
from client.base_client import BaseClient
from shared.logger import get_logger

logger = get_logger(__name__)

class PsutilClient(BaseClient):
    """
    Sensor client that collects real system metrics using psutil.
    Each instance monitors a single metric type.
    """

    COLLECTORS = {
        "cpu": lambda: psutil.cpu_percent(interval=None),
        "ram": lambda: psutil.virtual_memory().percent,
        "disk": lambda: psutil.disk_usage("/").percent,
        "network": lambda: psutil.net_io_counters().bytes_sent,
    }

    def __init__(self, sensor_id: str, sensor_type: str, interval: float = 2.0):

        super().__init__(sensor_id, sensor_type, interval)

        if sensor_type not in self.COLLECTORS:
            raise ValueError(f"Unsupported sensor type: '{sensor_type}'. "
                             f"Valid types: {list(self.COLLECTORS.keys())}")

        self._collector = self.COLLECTORS[sensor_type]
        logger.info(f"'{sensor_id}' initialized as {sensor_type} sensor")

    def collect(self) -> float:
        """Collect a real system metric using psutil."""

        return self._collector()


if __name__ == "__main__":
    
    client = PsutilClient(sensor_id="cpu_01", sensor_type="cpu", interval=2.0)
    asyncio.run(client.run())