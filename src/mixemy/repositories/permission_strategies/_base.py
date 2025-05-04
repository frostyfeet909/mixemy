from abc import ABC, abstractmethod
from typing import Any

from sqlalchemy import Select

from mixemy.types import BaseModelT, SelectT


class PermissionStrategy(ABC):
    def __init__(
        self,
        model: type[BaseModelT],
        user_id_attribute: str,
        user_joined_table: str | None,
    ) -> None:
        self.model = model
        self.user_id_attribute = user_id_attribute
        self.user_joined_table = user_joined_table

    @abstractmethod
    def add_permission_filter(
        self,
        statement: Select[SelectT],
        user_id: Any,
    ) -> Select[SelectT]: ...

    @abstractmethod
    def check_permission_on_db_oject(
        self,
        db_object: BaseModelT | None,  # type: ignore no
        user_id: Any,
    ) -> tuple[bool, Any]: ...
