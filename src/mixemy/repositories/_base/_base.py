from abc import ABC
from typing import Any, Generic

from sqlalchemy import Select, select

from mixemy._exceptions import MixemyRepositorySetupError
from mixemy.schemas import InputSchema
from mixemy.schemas.paginations import PaginationFields, PaginationFilter
from mixemy.types import BaseModelType
from mixemy.utils import unpack_schema


class BaseRepository(Generic[BaseModelType], ABC):
    model_type: type[BaseModelType]

    def __init__(self) -> None:
        self._verify_init()
        self.model = self.model_type

    def _add_after_filter(
        self, statement: Select[Any], filters: InputSchema | None
    ) -> Select[Any]:
        if isinstance(filters, PaginationFilter):
            statement = statement.offset(filters.offset).limit(filters.limit)

        return statement

    def _add_before_filter(
        self, statement: Select[Any], filters: InputSchema | None
    ) -> Select[Any]:
        if filters is not None:
            for item, value in unpack_schema(
                schema=filters, exclude=PaginationFields
            ).items():
                if hasattr(self.model, item):
                    if isinstance(value, list):
                        statement = statement.where(
                            getattr(self.model, item).in_(value)
                        )
                    else:
                        statement = statement.where(getattr(self.model, item) == value)

        return statement

    def _add_filters(
        self, statement: Select[Any] | None, filters: InputSchema | None
    ) -> Select[Any]:
        if statement is None:
            statement = select(self.model)
        return self._add_after_filter(
            statement=self._add_before_filter(statement=statement, filters=filters),
            filters=filters,
        )

    @staticmethod
    def _update_db_object(db_object: BaseModelType, object_in: InputSchema) -> None:
        for field, value in unpack_schema(schema=object_in).items():
            if hasattr(db_object, field):
                setattr(db_object, field, value)

    def _verify_init(self) -> None:
        for field in ["model_type"]:
            if not hasattr(self, field):
                raise MixemyRepositorySetupError(repository=self, undefined_field=field)
