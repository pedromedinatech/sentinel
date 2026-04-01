from collections import deque
from statistics import mean, stdev
from shared.config import WINDOW_SIZE, ZSCORE_THRESHOLD
from shared.logger import get_logger

logger = get_logger(__name__)

class ZScoreDetector:
    """
    Third stage of the processing pipeline.
    Flags readings that deviate significantly from the sensor's recent history
    using a sliding window Z-score calculation.
    """

    def __init__(self):

        self._windows: dict[str, deque] = {}

    def check(self, message: dict) -> tuple[bool, str]:
        """
        Check if the reading is statistically consistent with recent history.
        Returns (True, "") if normal, or (False, reason) if anomalous.
        At least 2 readings are required before Z-score can be calculated.
        """

        sensor_id = message["sensor_id"]
        value = message["value"]

        if sensor_id not in self._windows:
            self._windows[sensor_id] = deque(maxlen=WINDOW_SIZE)

        window = self._windows[sensor_id]

        if len(window) < 2:
            window.append(value)
            logger.debug(f"'{sensor_id}' building history ({len(window)}/{WINDOW_SIZE})")
            return True, ""
        
        # calculate Z-score
        mu = mean(window)
        sigma = stdev(window)

        if sigma == 0:
            window.append(value)
            return True, ""
        
        z = abs((value - mu) / sigma)

        if z > ZSCORE_THRESHOLD:
            reason = f"statistical anomaly on '{sensor_id}': value={value}, z={z:.2f}"
            logger.warning(reason)
            return False, reason
        
        window.append(value)
        logger.debug(f"'{sensor_id}' z={z:.2f} — normal")
        return True, ""