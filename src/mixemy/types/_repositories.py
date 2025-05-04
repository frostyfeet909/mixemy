from typing import Any, Literal, TypeVar

SelectT = TypeVar("SelectT", bound=tuple[Any, ...])
permission_strategies = Literal["loose", "strict"]
