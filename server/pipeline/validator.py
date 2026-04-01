from shared.config import PHYSICAL_LIMITS

class Validator:
    """
    First stage of the processing pipeline.
    Rejects messages that are malformed or contain physically impossible values.
    """

    REQUIRED_FIELDS = {"sensor_id", "sensor_type", "value", "timestamp"}

    def validate(self, message: dict) -> tuple[bool, str]:
        """
        Validate a reading message.
        Returns (True, "") if valid, or (False, reason) if not.
        """

        missing = self.REQUIRED_FIELDS - message.keys()

        if missing:
            return False, f"missing fields: {missing}"
        
        sensor_type = message["sensor_type"]

        if sensor_type not in PHYSICAL_LIMITS:
            return False, f"unknown sensor type: {sensor_type}"
        
        value = message["value"]

        if not isinstance(value, (int, float)):
            return False, f"value must be a number, got: {type(value).__name__}"
        
        min_val, max_val = PHYSICAL_LIMITS[sensor_type]

        if not (min_val <= value <= max_val):
            return False, f"value {value} out of range [{min_val}, {max_val}]"
        
        return True, ""