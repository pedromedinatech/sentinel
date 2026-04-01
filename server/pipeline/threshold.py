from shared.config import ALERT_THRESHOLDS
from shared.logger import get_logger

logger = get_logger(__name__)

class ThresholdDetector:
    """
    Second stage of the processing pipeline.
    Flags readings that exceed the configured static thresholds.
    """

    def check(self, message: dict) -> tuple[bool, str]:
        """
        Check if the reading value is within the expected range.
        Returns (True, "") if normal, or (False, reason) if anomalous.
        """

        sensor_type = message["sensor_type"]
        value = message["value"]
        sensor_id = message["sensor_id"]

        min_val, max_val = ALERT_THRESHOLDS[sensor_type]

        if not (min_val <= value <= max_val):
            reason = f"threshold breach on '{sensor_id}': {value} out of [{min_val}, {max_val}]"
            logger.warning(reason)
            return False, reason
        
        logger.debug(f"'{sensor_id}' passed threshold check: {value}")
        return True, ""
