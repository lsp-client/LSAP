import uuid


def generate_short_id(length: int = 6) -> str:
    """Generate a short ID from a UUID4 (default to first 6 characters)."""
    return str(uuid.uuid4())[:length]
