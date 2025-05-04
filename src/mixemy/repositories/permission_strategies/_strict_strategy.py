from typing import Any, override

from sqlalchemy import Select

from mixemy.repositories.permission_strategies._base import PermissionStrategy
from mixemy.types import BaseModelT, SelectT


class StrictPermissionStrategy(PermissionStrategy):
    @override
    def add_permission_filter(
        self,
        statement: Select[SelectT],
        user_id: Any,
    ) -> Select[SelectT]:
        if self.user_joined_table is None:
            statement = statement.where(
                getattr(self.model, self.user_id_attribute) == user_id
            )
        else:
            joined_table = getattr(self.model, self.user_joined_table)
            statement = statement.join(joined_table).where(
                getattr(joined_table, self.user_id_attribute) == user_id
            )

        return statement

    @override
    def check_permission_on_db_oject(
        self,
        db_object: BaseModelT | None,  # type: ignore no
        user_id: Any,
    ) -> tuple[bool, Any]:
        if db_object is None:
            return True, None

        object_id = (
            getattr(db_object, self.user_id_attribute)
            if self.user_joined_table is None
            else getattr(
                getattr(db_object, self.user_joined_table), self.user_id_attribute
            )
        )

        return user_id == object_id, object_id
