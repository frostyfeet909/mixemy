from typing import overload
from uuid import UUID


@overload
def serialize_uuid(data: UUID) -> str: ...


@overload
def serialize_uuid(data: None) -> None: ...


def serialize_uuid(data: UUID | None) -> str | None:
    if data is None:
        return data

    return str(data)
