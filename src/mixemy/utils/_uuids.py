from uuid import UUID

from uuid_utils.compat import uuid7


def generate_uuid(timestamp: int | None = None) -> UUID:
    return uuid7(timestamp=timestamp)
