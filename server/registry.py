import hashlib
from shared.config import SECRET_HASH
from shared.logger import get_logger

logger = get_logger(__name__)

class Registry:
    """Keeps track of authenticated sensor clients."""

    def __init__(self):
        self._sensors: dict[str, dict] = {}

    def authenticate(self, sensor_id: str, secret: str) -> bool:
        """
        Verify the shared secret and register the sensor if valid.
        The incoming secret is hashed and compared against the stored hash —
        plain text secrets are never compared directly.
        """

        incoming_hash = hashlib.sha256(secret.encode()).hexdigest()

        if incoming_hash != SECRET_HASH:
            logger.warning(f"authentication failed for sensor '{sensor_id}' — invalid secret")
            return False
        
        self._sensors[sensor_id] = {"sensor_id": sensor_id}
        logger.info(f"sensor '{sensor_id}' registered successfully")
        return True
    
    def is_registered(self, sensor_id: str) -> bool:
        """Return True if the sensor has been authenticated."""

        return sensor_id in self._sensors
    
    def remove(self, sensor_id: str) -> None:
        """Remove a sensor from the registry, e.g. on disconnection."""

        self._sensors.pop(sensor_id, None)
        logger.info(f"sensor '{sensor_id}' removed from registry")

    def registered_sensors(self) -> list[str]:
        """Return a list of currently registered sensor IDs."""

        return list(self._sensors.keys())