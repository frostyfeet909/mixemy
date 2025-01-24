from abc import ABC
from typing import Any, override

from sqlalchemy import Select, asc, desc

from mixemy.repositories._base._base import BaseRepository
from mixemy.schemas import InputSchema
from mixemy.schemas.paginations import AuditPaginationFilter, OrderDirection
from mixemy.types import (
    AuditModelType,
)


class AuditRepository(BaseRepository[AuditModelType], ABC):
    @override
    def _add_after_filter(
        self, statement: Select[Any], filters: InputSchema | None
    ) -> Select[Any]:
        statement = super()._add_after_filter(statement=statement, filters=filters)
        if isinstance(filters, AuditPaginationFilter):
            match filters.order_direction:
                case OrderDirection.ASC:
                    statement = statement.order_by(asc(filters.order_by))
                case OrderDirection.DESC:
                    statement = statement.order_by(desc(filters.order_by))

        return statement
