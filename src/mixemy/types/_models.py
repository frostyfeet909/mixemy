from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from mixemy.models import BaseModel

BaseModelT = TypeVar("BaseModelT", bound="BaseModel")
