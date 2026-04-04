# client/simulation_client.py
import asyncio
import random
from client.base_client import BaseClient
from shared.config import ALERT_THRESHOLDS
from shared.logger import get_logger

logger = get_logger(__name__)

class SimulationClient(BaseClient):
    """
    Sensor client that generates simulated readings.
    Supports normal mode (values within expected range) and
    injection mode (values outside expected range to trigger anomaly detection).
    """

    def __init__(self, sensor_id: str, sensor_type: str,
                 interval: float = 2.0, inject_anomaly: bool = False):
        
        super().__init__(sensor_id, sensor_type, interval)
        self._inject_anomaly = inject_anomaly

        logger.info(
            f"'{sensor_id}' initialized as simulated {sensor_type} sensor "
            f"— anomaly injection: {'ON' if inject_anomaly else 'OFF'}"
        )

    def collect(self) -> float:
        """
        Generate a simulated reading.
        In normal mode, values stay within the alert threshold range.
        In injection mode, values exceed the alert threshold to trigger detection.
        """

        min_val, max_val = ALERT_THRESHOLDS[self._sensor_type]

        if self._inject_anomaly:
            # generate a value clearly outside the alert threshold
            anomalous_value = max_val + random.uniform(10.0, 30.0)
            logger.debug(f"'{self._sensor_id}' injecting anomalous value: {anomalous_value:.2f}")
            return round(anomalous_value, 2)

        # generate a normal value within 60-90% of the alert threshold max
        normal_value = random.uniform(min_val, max_val * 0.9)
        return round(normal_value, 2)


if __name__ == "__main__":

    import sys

    # Usage: python -m client.simulation_client <sensor_id> <sensor_type> [inject]
    # Example: python -m client.simulation_client cpu_sim cpu inject
    
    sensor_id   = sys.argv[1] if len(sys.argv) > 1 else "sim_01"
    sensor_type = sys.argv[2] if len(sys.argv) > 2 else "cpu"
    inject      = len(sys.argv) > 3 and sys.argv[3] == "inject"

    client = SimulationClient(
        sensor_id=sensor_id,
        sensor_type=sensor_type,
        interval=2.0,
        inject_anomaly=inject
    )
    asyncio.run(client.run())