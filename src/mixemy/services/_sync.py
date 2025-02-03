from abc import ABC
from typing import Any, Generic

from sqlalchemy.orm import Session
from sqlalchemy.orm.strategy_options import (
    _AbstractLoad,  # pyright: ignore[reportPrivateUsage]
)

from mixemy._exceptions import MixemyServiceSetupError
from mixemy.types import (
    BaseModelT,
    CreateSchemaT,
    FilterSchemaT,
    OutputSchemaT,
    RepositorySyncT,
    UpdateSchemaT,
)
from mixemy.utils import to_model, to_schema


class BaseSyncService(
    Generic[
        BaseModelT,
        RepositorySyncT,
        CreateSchemaT,
        UpdateSchemaT,
        FilterSchemaT,
        OutputSchemaT,
    ],
    ABC,
):
    """
    Base class for synchronous services.
    This class provides a generic implementation for common CRUD operations
    (create, read, update, delete) using synchronous methods. It is designed
    to work with SQLAlchemy's SyncSession and generic repository patterns.
    Type Parameters:
        BaseModelT: The type of the base model.
        RepositorySyncT: The type of the synchronous repository.
        CreateSchemaT: The type of the schema used for creating objects.
        UpdateSchemaT: The type of the schema used for updating objects.
        FilterSchemaT: The type of the schema used for filtering objects.
        OutputSchemaT: The type of the schema used for outputting objects.
    Attributes:
        repository_type (type[RepositorySyncT]): The type of the repository.
        output_schema_type (type[OutputSchemaT]): The type of the output schema.
    Methods:
        __init__(db_session: SyncSession) -> None:
            Initializes the service with the given database session.
        create(object_in: CreateSchemaT, *, auto_expunge: bool | None = None, auto_refresh: bool | None = None, auto_commit: bool | None = None) -> OutputSchemaT:
            Synchronously creates a new object in the database.
        read(id: Any, *, loader_options: tuple[_AbstractLoad] | None = None, execution_options: dict[str, Any] | None = None, auto_expunge: bool | None = None, auto_commit: bool | None = None) -> OutputSchemaT | None:
            Synchronously reads an object from the database by its ID.
        read_multiple(filters: FilterSchemaT | None = None, *, loader_options: tuple[_AbstractLoad] | None = None, execution_options: dict[str, Any] | None = None, auto_expunge: bool | None = None, auto_commit: bool | None = None) -> list[OutputSchemaT]:
            Synchronously reads multiple objects from the database based on filters.
        update(id: Any, object_in: UpdateSchemaT, *, loader_options: tuple[_AbstractLoad] | None = None, execution_options: dict[str, Any] | None = None, auto_expunge: bool | None = None, auto_refresh: bool | None = None, auto_commit: bool | None = None) -> OutputSchemaT | None:
            Synchronously updates an object in the database by its ID.
        delete(id: Any, *, loader_options: tuple[_AbstractLoad] | None = None, execution_options: dict[str, Any] | None = None, auto_expunge: bool | None = None, auto_commit: bool | None = None) -> None:
            Synchronously deletes an object from the database by its ID.
        _to_model(schema: CreateSchemaT | UpdateSchemaT) -> BaseModelT:
            Converts a schema to a model instance.
        _to_schema(model: BaseModelT) -> OutputSchemaT:
            Converts a model instance to a schema.
        _verify_init() -> None:
            Verifies that the required attributes are set during initialization.
    """

    repository_type: type[RepositorySyncT]
    output_schema_type: type[OutputSchemaT]

    def __init__(self, db_session: Session) -> None:
        self._verify_init()
        self.output_schema = self.output_schema_type
        self.repository = self.repository_type()
        self.model = self.repository.model
        self.db_session = db_session

    def create(
        self,
        object_in: CreateSchemaT,
        *,
        auto_expunge: bool | None = None,
        auto_refresh: bool | None = None,
        auto_commit: bool | None = None,
    ) -> OutputSchemaT:
        return self._to_schema(
            model=self.repository.create(
                db_session=self.db_session,
                db_object=self._to_model(schema=object_in),
                auto_expunge=auto_expunge,
                auto_refresh=auto_refresh,
                auto_commit=auto_commit,
            )
        )

    def read(
        self,
        id: Any,
        *,
        loader_options: tuple[_AbstractLoad] | None = None,
        execution_options: dict[str, Any] | None = None,
        auto_expunge: bool | None = None,
        auto_commit: bool | None = None,
    ) -> OutputSchemaT | None:
        return (
            self._to_schema(model=model)
            if (
                model := self.repository.read(
                    db_session=self.db_session,
                    id=id,
                    loader_options=loader_options,
                    execution_options=execution_options,
                    auto_expunge=auto_expunge,
                    auto_commit=auto_commit,
                )
            )
            else None
        )

    def read_multiple(
        self,
        filters: FilterSchemaT | None = None,
        *,
        loader_options: tuple[_AbstractLoad] | None = None,
        execution_options: dict[str, Any] | None = None,
        auto_expunge: bool | None = None,
        auto_commit: bool | None = None,
    ) -> list[OutputSchemaT]:
        return [
            self._to_schema(model=model)
            for model in self.repository.read_multiple(
                db_session=self.db_session,
                filters=filters,
                loader_options=loader_options,
                execution_options=execution_options,
                auto_expunge=auto_expunge,
                auto_commit=auto_commit,
            )
        ]

    def update(
        self,
        id: Any,
        object_in: UpdateSchemaT,
        *,
        loader_options: tuple[_AbstractLoad] | None = None,
        execution_options: dict[str, Any] | None = None,
        auto_expunge: bool | None = None,
        auto_refresh: bool | None = None,
        auto_commit: bool | None = None,
    ) -> OutputSchemaT | None:
        return (
            self._to_schema(model)
            if (
                model := self.repository.update(
                    db_session=self.db_session,
                    id=id,
                    object_in=object_in,
                    loader_options=loader_options,
                    execution_options=execution_options,
                    auto_expunge=auto_expunge,
                    auto_refresh=auto_refresh,
                    auto_commit=auto_commit,
                )
            )
            else None
        )

    def delete(
        self,
        id: Any,
        *,
        loader_options: tuple[_AbstractLoad] | None = None,
        execution_options: dict[str, Any] | None = None,
        auto_expunge: bool | None = None,
        auto_commit: bool | None = None,
    ) -> None:
        self.repository.delete(
            db_session=self.db_session,
            id=id,
            auto_expunge=auto_expunge,
            auto_commit=auto_commit,
            loader_options=loader_options,
            execution_options=execution_options,
        )

    def _to_model(self, schema: CreateSchemaT | UpdateSchemaT) -> BaseModelT:
        return to_model(schema=schema, model=self.model)

    def _to_schema(self, model: BaseModelT) -> OutputSchemaT:
        return to_schema(model=model, schema=self.output_schema)

    def _verify_init(self) -> None:
        for field in ["output_schema_type", "repository_type"]:
            if not hasattr(self, field):
                raise MixemyServiceSetupError(service=self, undefined_field=field)
