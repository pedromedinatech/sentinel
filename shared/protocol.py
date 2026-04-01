import json 

# Message types
MSG_REGISTER = "register"
MSG_READING = "reading"
MSG_ACK = "ack"
MSG_REJECTED = "rejected"

def encode(message: dict) -> bytes:
    """Serialize a message dict to a newline-terminated JSON bytes object."""

    return (json.dumps(message) + "\n").encode("utf-8")

def decode(raw: bytes) -> dict:
    """Serialize a message dict to a newline-terminated JSON bytes object."""

    return json.loads(raw.strip())

def make_register(sensor_id: str, secret: str) -> dict:
    """Build a registration handshake message."""

    return {
        "type": MSG_REGISTER,
        "sensor_id": sensor_id,
        "secret": secret,
    }

def make_reading(sensor_id: str, sensor_type: str, value: float, timestamp: float) -> dict:
    """Build a sensor reading message."""

    return {
        "type": MSG_READING,
        "sensor_id": sensor_id,
        "sensor_type": sensor_type,
        "value": value,
        "timestamp": timestamp,
    }

def make_ack(sensor_id: str) -> dict:
    """Build an acknowledgement message."""

    return {
        "type": MSG_ACK,
        "sensor_id": sensor_id,
    }

def make_rejected(reason: str) -> dict:
    """Build a rejection message."""
    
    return {
        "type": MSG_REJECTED,
        "reason": reason,
    }