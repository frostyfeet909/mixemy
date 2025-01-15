from abc import ABC
from typing import Any, override

from sqlalchemy import Select, asc, desc

from mixemy.repositories._base._base import BaseRepository
from mixemy.schemas.paginations import AuditPaginationFilter, OrderDirection
from mixemy.types import (
    AuditModelType,
    PaginationSchemaType,
)


class AuditRepository(BaseRepository[AuditModelType], ABC):
    @override
    @staticmethod
    def _add_after_filter(
        statement: Select[Any], filter: PaginationSchemaType | None
    ) -> Select[Any]:
        if filter is not None:
            statement = statement.offset(filter.offset).limit(filter.limit)
        if isinstance(filter, AuditPaginationFilter):
            match filter.order_direction:
                case OrderDirection.ASC:
                    statement = statement.order_by(asc(filter.order_by))
                case OrderDirection.DESC:
                    statement = statement.order_by(desc(filter.order_by))

        return statement
