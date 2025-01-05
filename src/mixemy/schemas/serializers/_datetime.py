from datetime import UTC, datetime
from typing import overload


@overload
def serialize_datetime(data: datetime) -> str: ...


@overload
def serialize_datetime(data: None) -> None: ...


def serialize_datetime(data: datetime | None) -> str | None:
    if data is None:
        return data

    if not data.tzinfo:
        data = data.replace(tzinfo=UTC)

    return data.isoformat()
