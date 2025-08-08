from abc import ABC
from typing import TYPE_CHECKING, Any

from sqlalchemy.orm import Session

from mixemy.exceptions import MixemyServiceSetupError
from mixemy.models import BaseModel
from mixemy.schemas import InputSchema
from mixemy.types import (
    OutputSchemaT,
    PermissionSyncRepositoryT,
)
from mixemy.utils import to_model, to_schema

if TYPE_CHECKING:
    from mixemy.repositories import BaseSyncRepository
    from mixemy.schemas import OutputSchema


class BaseSyncService[
    RepositorySyncT: BaseSyncRepository[
        Any
    ],  # https://peps.python.org/pep-0695/#explicit-variance
    OutputSchemaT: OutputSchema,
](ABC):
    """Base class for synchronous services.

    This class provides a generic implementation for common CRUD operations
    (create, read, update, delete) using synchronous methods. It is designed
    to work with SQLAlchemy's Session and generic repository patterns.
    Type Parameters:
        RepositorySyncT: The type of the synchronous repository.
        OutputSchemaT: The type of the schema used for outputting objects.
    Attributes:
        repository_type (type[RepositorySyncT]): The type of the repository.
        output_schema_type (type[OutputSchemaT]): The type of the output schema.
        default_recursive_model_conversion (bool): Default value for recursive model conversion.
        default_exclude_unset (bool): Default value for excluding unset fields.
        default_exclude (set[str] | None): Default value for excluded fields.
        default_by_alias (bool): Default value for using field aliases.
    Methods:
        __init__(db_session: Session) -> None:
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

    default_recursive_model_conversion: bool = False
    default_exclude_unset: bool = True
    default_exclude: set[str] | None = None
    default_by_alias: bool = True

    def __init__(
        self,
        db_session: Session,
        *,
        recursive_model_conversion: bool | None = None,
        exclude_unset: bool | None = None,
        exclude: set[str] | None = None,
        by_alias: bool | None = None,
    ) -> None:
        self._verify_init()
        self.repository = self.repository_type()
        self.model = self.repository.model
        self.output_schema = self.output_schema_type
        self.db_session = db_session
        self.recursive_model_conversion = (
            recursive_model_conversion
            if recursive_model_conversion is not None
            else self.default_recursive_model_conversion
        )
        self.exclude_unset = (
            exclude_unset if exclude_unset is not None else self.default_exclude_unset
        )
        self.exclude = exclude if exclude is not None else self.default_exclude
        self.by_alias = by_alias if by_alias is not None else self.default_by_alias

    def create(
        self,
        object_in: InputSchema,
        *,
        recursive_model_conversion: bool | None = None,
        exclude_unset: bool | None = None,
        exclude: set[str] | None = None,
        by_alias: bool | None = None,
        **kwargs: Any,
    ) -> OutputSchemaT:
        return self.to_schema(
            model=self.repository.create(
                db_session=self.db_session,
                db_object=self.to_model(
                    schema=object_in,
                    recursive_model_conversion=recursive_model_conversion,
                    by_alias=by_alias,
                    exclude_unset=exclude_unset,
                    exclude=exclude,
                ),
                **kwargs,
            ),
        )

    def read(
        self,
        id: Any,
        **kwargs: Any,
    ) -> OutputSchemaT | None:
        return (
            self.to_schema(model=model)
            if (
                model := self.repository.read(
                    db_session=self.db_session,
                    id=id,
                    **kwargs,
                )
            )
            else None
        )

    def read_multiple(
        self,
        filters: InputSchema | None = None,
        **kwargs: Any,
    ) -> list[OutputSchemaT]:
        return [
            self.to_schema(model=model)
            for model in self.repository.read_multiple(
                db_session=self.db_session,
                filters=filters,
                **kwargs,
            )
        ]

    def update(
        self,
        id: Any,
        object_in: InputSchema,
        **kwargs: Any,
    ) -> OutputSchemaT | None:
        return (
            self.to_schema(model)
            if (
                model := self.repository.update(
                    db_session=self.db_session,
                    id=id,
                    object_in=object_in,
                    **kwargs,
                )
            )
            else None
        )

    def delete(
        self,
        id: Any,
        **kwargs: Any,
    ) -> None:
        self.repository.delete(
            db_session=self.db_session,
            id=id,
            **kwargs,
        )

    def to_model(
        self,
        schema: InputSchema,
        *,
        recursive_model_conversion: bool | None = None,
        exclude_unset: bool | None = None,
        exclude: set[str] | None = None,
        by_alias: bool | None = None,
    ) -> BaseModel:
        current_recursive_model_conversion = (
            recursive_model_conversion
            if recursive_model_conversion is not None
            else self.recursive_model_conversion
        )
        current_exclude_unset = (
            exclude_unset if exclude_unset is not None else self.exclude_unset
        )
        current_exclude = exclude if exclude is not None else self.exclude
        current_by_alias = by_alias if by_alias is not None else self.by_alias
        return to_model(
            schema=schema,
            model=self.model,
            recursive_conversion=current_recursive_model_conversion,
            exclude_unset=current_exclude_unset,
            exclude=current_exclude,
            by_alias=current_by_alias,
        )

    def to_schema(self, model: BaseModel) -> OutputSchemaT:
        return to_schema(model=model, schema=self.output_schema)

    def _verify_init(self) -> None:
        for field in ["output_schema_type", "repository_type"]:
            if not hasattr(self, field):
                raise MixemyServiceSetupError(service=self, undefined_field=field)


class PermissionSyncService(BaseSyncService[PermissionSyncRepositoryT, OutputSchemaT]):
    """Service for performing synchronous operations on Permission objects.

    This class provides methods for creating, reading, updating, and deleting
    Permission objects using synchronous methods. It is designed to work with
    SQLAlchemy's Session and the PermissionSyncRepository.
    Methods:
        __init__(db_session: Session) -> None:
            Initializes the service with the given database session.
    """

    repository_type: type[PermissionSyncRepositoryT]

    def __init__(
        self,
        db_session: Session,
        *,
        recursive_model_conversion: bool | None = None,
        exclude_unset: bool | None = None,
        exclude: set[str] | None = None,
        by_alias: bool | None = None,
    ) -> None:
        super().__init__(
            db_session=db_session,
            recursive_model_conversion=recursive_model_conversion,
            exclude_unset=exclude_unset,
            exclude=exclude,
            by_alias=by_alias,
        )

    def read_with_permission(
        self,
        id: Any,
        user_id: Any,
        **kwargs: Any,
    ) -> OutputSchemaT | None:
        return (
            self.to_schema(model=model)
            if (
                model := self.repository.read_with_permission(
                    db_session=self.db_session,
                    id=id,
                    user_id=user_id,
                    **kwargs,
                )
            )
            else None
        )

    def read_multiple_with_permission(
        self,
        user_id: Any,
        filters: InputSchema | None = None,
        **kwargs: Any,
    ) -> list[OutputSchemaT]:
        return [
            self.to_schema(model=model)
            for model in self.repository.read_multiple_with_permission(
                db_session=self.db_session,
                user_id=user_id,
                filters=filters,
                **kwargs,
            )
        ]

    def update_with_permission(
        self,
        id: Any,
        object_in: InputSchema,
        user_id: Any,
        **kwargs: Any,
    ) -> OutputSchemaT | None:
        return (
            self.to_schema(model)
            if (
                model := self.repository.update_with_permission(
                    db_session=self.db_session,
                    id=id,
                    user_id=user_id,
                    object_in=object_in,
                    **kwargs,
                )
            )
            else None
        )

    def delete_with_permission(
        self,
        id: Any,
        user_id: Any,
        **kwargs: Any,
    ) -> None:
        self.repository.delete_with_permission(
            db_session=self.db_session,
            id=id,
            user_id=user_id,
            **kwargs,
        )
