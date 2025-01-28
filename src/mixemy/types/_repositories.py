from typing import Any, TypeVar

SelectT = TypeVar("SelectT", bound=tuple[Any, ...])
ResultT = TypeVar("ResultT", bound=Any)
