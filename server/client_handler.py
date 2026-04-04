import asyncio
from shared import protocol
from shared.logger import get_logger
from server.registry import Registry
from server.event_bus import EventBus
from server.pipeline.validator import Validator
from server.pipeline.threshold import ThresholdDetector
from server.pipeline.zscore import ZScoreDetector

logger = get_logger(__name__)

class ClientHandler:
    """
    Handles the full lifecycle of a single client connection:
    authentication, message parsing, pipeline execution and event publishing.
    """

    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter,
                 registry: Registry, event_bus: EventBus):
        
        self._reader = reader
        self._writer = writer
        self._registry = registry
        self._event_bus = event_bus
        self._sensor_id = None

        # pipeline stages
        self._validator = Validator()
        self._threshold = ThresholdDetector()
        self._zscore = ZScoreDetector()

        addr = writer.get_extra_info("peername")
        logger.info(f"New connection from {addr}")

    async def handle(self) -> None:
        """Main entry point — authenticate then process incoming messages."""

        authenticated = await self._authenticate()
        if not authenticated:
            self._writer.close()
            return

        await self._process_messages()

    async def _authenticate(self) -> bool:
        """
        Wait for a registration handshake and validate the shared secret.
        Returns True if authentication succeeds, False otherwise.
        """

        try:
            raw = await asyncio.wait_for(self._reader.readline(), timeout=10.0)
            message = protocol.decode(raw.decode("utf-8"))

            if message.get("type") != protocol.MSG_REGISTER:
                logger.warning("First message was not a register — rejecting")
                self._writer.write(protocol.encode(
                    protocol.make_rejected("first message must be a registration")
                ))
                await self._writer.drain()
                return False

            sensor_id = message.get("sensor_id", "")
            secret = message.get("secret", "")

            if not self._registry.authenticate(sensor_id, secret):
                self._writer.write(protocol.encode(
                    protocol.make_rejected("invalid secret")
                ))
                await self._writer.drain()
                return False

            self._sensor_id = sensor_id
            self._writer.write(protocol.encode(
                protocol.make_ack(sensor_id)
            ))
            await self._writer.drain()
            return True

        except asyncio.TimeoutError:
            logger.warning("authentication timed out")
            return False
        except Exception as e:
            logger.error(f"authentication error: {e}")
            return False

    async def _process_messages(self) -> None:
        """Read and process incoming sensor readings until the client disconnects."""
        logger.info(f"'{self._sensor_id}' ready, waiting for readings")

        try:
            while True:
                raw = await self._reader.readline()

                # Empty bytes means the client disconnected
                if not raw:
                    logger.info(f"'{self._sensor_id}' disconnected")
                    self._registry.remove(self._sensor_id)
                    break

                message = protocol.decode(raw.decode("utf-8"))

                if message.get("type") != protocol.MSG_READING:
                    logger.warning(f"'{self._sensor_id}' sent unexpected message type: {message.get('type')}")
                    continue

                await self._run_pipeline(message)

        except Exception as e:
            logger.error(f"error handling '{self._sensor_id}': {e}")
            self._registry.remove(self._sensor_id)

    async def _run_pipeline(self, message: dict) -> None:
        """
        Run the message through the three pipeline stages.
        Publishes an anomaly event if any stage flags the reading.
        """

        # stage 1: schema and physical limits
        valid, reason = self._validator.validate(message)
        if not valid:
            logger.warning(f"Validation failed for '{self._sensor_id}': {reason}")
            self._event_bus.publish("anomaly", {**message, "reason": reason, "stage": "validator"})
            return

        # stage 2: alert thresholds
        normal, reason = self._threshold.check(message)
        if not normal:
            self._event_bus.publish("anomaly", {**message, "reason": reason, "stage": "threshold"})
            return

        # stage 3: statistical Z-score
        normal, reason = self._zscore.check(message)
        if not normal:
            self._event_bus.publish("anomaly", {**message, "reason": reason, "stage": "zscore"})
            return

        logger.debug(f"'{self._sensor_id}' reading OK: {message['value']}")