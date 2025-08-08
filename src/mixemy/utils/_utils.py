from collections.abc import Sequence


def pack_sequence[T](value: T | Sequence[T]) -> Sequence[T]:
    """Pack a value or a sequence into a sequence."""
    if isinstance(value, Sequence):
        return value  # pyright: ignore[reportUnknownVariableType] WTF

    return [value]
