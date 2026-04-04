import asyncio
import time
from shared import protocol
from shared.config import HOST, PORT, SECRET
from shared.logger import get_logger

logger = get_logger(__name__)

class BaseClient:
    """
    Base class for all sensor clients.
    Handles connection, authentication handshake and message sending.
    Subclasses must implement the collect() method to provide sensor readings.
    """

    def __init__(self, sensor_id: str, sensor_type: str, interval: float = 2.0):

        self._sensor_id = sensor_id
        self_sensor_type = sensor_type
        self._interval = interval
        self._reader = None
        self._writer = None 

    async def connect(self) -> bool:
        """
        Open a TCP connection to the server and perform the authentication handshake.
        Returns True if authentication succeeds, False otherwise.
        """

        try:
            self._reader, self._writer = await asyncio.open_connection(HOST, PORT)
            logger.info(f"'{self._sensor_id}' connected to {HOST}:{PORT}")

            # send registration handshake
            self._writer.write(protocol.encode(
                protocol.make_register(self._sensor_id, SECRET)
            ))
            await self._writer.drain()

            # wait for server response
            raw = await asyncio.wait_for(self._reader.readline(), timeout=10.0)
            response = protocol.decode(raw.decode("utf-8"))

            if response.get("type") == protocol.MSG_ACK:
                logger.info(f"'{self._sensor_id}' authenticated successfully")
                return True

            reason = response.get("reason", "unknown")
            logger.error(f"'{self._sensor_id}' rejected by server: {reason}")
            return False

        except asyncio.TimeoutError:
            logger.error(f"'{self._sensor_id}' authentication timed out")
            return False
        except Exception as e:
            logger.error(f"'{self._sensor_id}' connection error: {e}")
            return False
        

    async def send_reading(self, value: float) -> None:
        """Send a single sensor reading to the server."""

        message = protocol.make_reading(
            sensor_id=self._sensor_id,
            sensor_type=self._sensor_type,
            value=value,
            timestamp=time.time()
        )
        self._writer.write(protocol.encode(message))
        await self._writer.drain()
        logger.debug(f"'{self._sensor_id}' sent reading: {value}")


    async def run(self) -> None:
        """
        Main loop: connect, authenticate, then send readings at regular intervals.
        """

        connected = await self.connect()
        if not connected:
            return

        try:
            while True:
                value = self.collect()
                await self.send_reading(value)
                await asyncio.sleep(self._interval)
        except KeyboardInterrupt:
            logger.info(f"'{self._sensor_id}' stopped by user")
        except Exception as e:
            logger.error(f"'{self._sensor_id}' error: {e}")
        finally:
            if self._writer:
                self._writer.close()
                await self._writer.wait_closed()
                logger.info(f"'{self._sensor_id}' connection closed")


    def collect(self) -> float:
        """
        Collect a sensor reading. Must be implemented by subclasses.
        """

        raise NotImplementedError("subclasses must implement collect method")
