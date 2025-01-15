from collections.abc import Callable
from typing import overload

from pydantic import SecretStr


@overload
def serialize_secretstr(
    data: SecretStr | str,
    convert_secret: Callable[[str], str] | None,
) -> str: ...


@overload
def serialize_secretstr(
    data: SecretStr | str,
    convert_secret: Callable[[str], str | None],
) -> str | None: ...


@overload
def serialize_secretstr(
    data: None,
    convert_secret: Callable[[str], str | None] | Callable[[str], str] | None,
) -> None: ...


@overload
def serialize_secretstr(
    data: SecretStr | str | None,
    convert_secret: Callable[[str], str | None] | Callable[[str], str] | None = None,
) -> str | None: ...


def serialize_secretstr(
    data: SecretStr | str | None,
    convert_secret: Callable[[str], str | None] | Callable[[str], str] | None = None,
) -> str | None:
    if data is None:
        return None

    if isinstance(data, SecretStr):
        data = data.get_secret_value()

    return convert_secret(data) if convert_secret is not None else data
