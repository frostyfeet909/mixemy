from abc import ABC
from typing import Any, Generic

from sqlalchemy import Select
from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy.orm.strategy_options import (
    _AbstractLoad,  # pyright: ignore[reportPrivateUsage]
)

from mixemy._exceptions import MixemyRepositorySetupError
from mixemy.schemas import InputSchema
from mixemy.schemas.paginations import PaginationFields, PaginationFilter
from mixemy.types import BaseModelType, SelectT
from mixemy.utils import unpack_schema


class BaseRepository(Generic[BaseModelType], ABC):
    model_type: type[BaseModelType]
    id_attribute: str | InstrumentedAttribute[Any]

    default_loader_options: tuple[_AbstractLoad] | None = None
    default_execution_options: dict[str, Any] | None = None
    default_auto_expunge: bool = False
    default_auto_refresh: bool = True
    default_auto_commit: bool = False

    def __init__(
        self,
        *,
        loader_options: tuple[_AbstractLoad] | None = None,
        execution_options: dict[str, Any] | None = None,
        auto_expunge: bool | None = False,
        auto_refresh: bool | None = True,
        auto_commit: bool | None = False,
    ) -> None:
        self._verify_init()
        self.model = self.model_type
        self.id_field = self._set_id_field(id_field=self.id_attribute)
        self.loader_options = (
            loader_options
            if loader_options is not None
            else self.default_loader_options
        )
        self.execution_options = (
            execution_options
            if execution_options is not None
            else self.default_execution_options
        )
        self.auto_expunge = (
            auto_expunge if auto_expunge is not None else self.default_auto_expunge
        )
        self.auto_refresh = (
            auto_refresh if auto_refresh is not None else self.default_auto_refresh
        )
        self.auto_commit = (
            auto_commit if auto_commit is not None else self.default_auto_commit
        )

    def _add_pagination(
        self, statement: Select[SelectT], filters: InputSchema | None
    ) -> Select[SelectT]:
        if isinstance(filters, PaginationFilter):
            statement = statement.offset(filters.offset).limit(filters.limit)

        return statement

    def _add_filters(
        self, statement: Select[SelectT], filters: InputSchema | None
    ) -> Select[SelectT]:
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

    def _prepare_statement(
        self,
        statement: Select[SelectT],
        *,
        loader_options: tuple[_AbstractLoad] | None,
        execution_options: dict[str, Any] | None,
        with_for_update: bool,
    ) -> Select[SelectT]:
        current_loader_options = (
            loader_options if loader_options is not None else self.loader_options
        )
        if current_loader_options is not None:
            statement = statement.options(*current_loader_options)

        current_execution_options = (
            execution_options
            if execution_options is not None
            else self.execution_options
        )
        if current_execution_options is not None:
            statement = statement.execution_options(**current_execution_options)

        if with_for_update:
            statement = statement.with_for_update()

        return statement

    @staticmethod
    def _update_db_object(db_object: BaseModelType, object_in: InputSchema) -> None:
        for field, value in unpack_schema(schema=object_in).items():
            if hasattr(db_object, field):
                setattr(db_object, field, value)

    def _verify_init(self) -> None:
        for field in ["model_type", "id_attribute"]:
            if not hasattr(self, field):
                raise MixemyRepositorySetupError(repository=self, undefined_field=field)

    def _set_id_field(
        self, id_field: str | InstrumentedAttribute[Any]
    ) -> InstrumentedAttribute[Any]:
        try:
            return (
                getattr(self.model, id_field) if isinstance(id_field, str) else id_field
            )
        except AttributeError as ex:
            raise MixemyRepositorySetupError(
                repository=self,
                undefined_field=str(id_field),
                message=f"ID attribute {id_field} not found on model",
            ) from ex
