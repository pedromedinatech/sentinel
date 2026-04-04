from shared.logger import get_logger

logger = get_logger(__name__)

class Monitor:
    """
    Observer that subscribes to the EventBus and reacts to anomaly events.
    Decoupled from the server, it only knows about the EventBus interface.
    """

    def on_anomaly(self, data: dict) -> None:
        """
        Callback invoked by the EventBus when an anomaly is detected.
        Logs a structured alert with all relevant information.
        """

        sensor_id = data.get("sensor_id", "unknown")
        sensor_type = data.get("sensor_type", "unknown")
        value = data.get("value", "unknown")
        reason = data.get("reason", "unknown")
        stage = data.get("stage", "unknown")

        logger.warning(
            f"anomaly detected | "
            f"sensor={sensor_id} | "
            f"type={sensor_type} | "
            f"value={value} | "
            f"stage={stage} | "
            f"reason={reason}"
        )