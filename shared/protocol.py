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