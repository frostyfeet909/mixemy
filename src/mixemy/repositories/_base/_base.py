from abc import ABC
from typing import Any, Generic

from sqlalchemy import Select

from mixemy._exceptions import MixemyRepositorySetupError
from mixemy.schemas import InputSchema
from mixemy.types import (
    BaseModelType,
    PaginationSchemaType,
)
from mixemy.utils import unpack_schema


class BaseRepository(Generic[BaseModelType], ABC):
    model_type: type[BaseModelType]

    def __init__(self) -> None:
        self._verify_init()
        self.model = self.model_type

    @staticmethod
    def _add_after_filter(
        statement: Select[Any], filter: PaginationSchemaType | None
    ) -> Select[Any]:
        if filter is not None:
            statement = statement.offset(filter.offset).limit(filter.limit)

        return statement

    def _add_before_filter(
        self, statement: Select[Any], filter: InputSchema | None
    ) -> Select[Any]:
        if filter is not None:
            for item, value in unpack_schema(schema=filter).items():
                if isinstance(value, list):
                    statement = statement.where(getattr(self.model, item).in_(value))
                else:
                    statement = statement.where(getattr(self.model, item) == value)

        return statement

    @staticmethod
    def _update_db_object(db_object: BaseModelType, object_in: InputSchema) -> None:
        for field, value in unpack_schema(schema=object_in).items():
            if hasattr(db_object, field):
                setattr(db_object, field, value)

    def _verify_init(self) -> None:
        for field in ["model_type"]:
            if not hasattr(self, field):
                raise MixemyRepositorySetupError(repository=self, undefined_field=field)
