from abc import ABC
from collections.abc import Sequence
from typing import Any, Generic

from sqlalchemy import Result, Select, func, select
from sqlalchemy.orm import InstrumentedAttribute, Session
from sqlalchemy.orm.strategy_options import (
    _AbstractLoad,  # pyright: ignore[reportPrivateUsage]
)
from sqlalchemy.util import EMPTY_DICT

from mixemy._exceptions import MixemyRepositorySetupError
from mixemy.schemas import InputSchema
from mixemy.schemas.paginations import PaginationFields, PaginationFilter
from mixemy.types import BaseModelT, ResultT, SelectT
from mixemy.utils import unpack_schema


class BaseSyncRepository(Generic[BaseModelT], ABC):
    """
    A base class for synchronous repositories that provides common CRUD operations.
    Attributes:
        model_type (type[BaseModelT]): The type of the model.
        id_attribute (str | InstrumentedAttribute[Any]): The attribute used as the ID field.
        default_loader_options (tuple[_AbstractLoad] | None): Default loader options for queries.
        default_execution_options (dict[str, Any] | None): Default execution options for queries.
        default_auto_expunge (bool): Whether to automatically expunge objects from the session.
        default_auto_refresh (bool): Whether to automatically refresh objects in the session.
        default_auto_commit (bool): Whether to automatically commit transactions.
    Methods:
        __init__(self, *, loader_options, execution_options, auto_expunge, auto_refresh, auto_commit):
            Initializes the repository with optional settings for loader options, execution options, auto expunge, auto refresh, and auto commit.
        create(self, db_session, db_object, *, auto_commit, auto_expunge, auto_refresh):
            Creates a new object in the database.
        read(self, db_session, id, *, loader_options, execution_options, auto_expunge, auto_commit, with_for_update):
            Reads an object from the database by its ID.
        read_multiple(self, db_session, filters, *, loader_options, execution_options, auto_commit, auto_expunge, with_for_update):
            Reads multiple objects from the database based on filters.
        update(self, db_session, id, object_in, *, loader_options, execution_options, auto_commit, auto_expunge, auto_refresh, with_for_update):
            Updates an existing object in the database.
        update_db_object(self, db_session, db_object, object_in, *, auto_commit, auto_expunge, auto_refresh):
            Updates an existing database object with new data.
        delete(self, db_session, id, *, loader_options, execution_options, auto_commit, auto_expunge, with_for_update):
            Deletes an object from the database by its ID.
        delete_db_object(self, db_session, db_object, *, auto_commit, auto_expunge):
            Deletes a database object.
        count(self, db_session, filters, *, loader_options, execution_options, auto_commit):
            Counts the number of objects in the database based on filters.
        _maybe_commit_or_flush_or_refresh_or_expunge(self, db_session, db_object, *, auto_commit, auto_expunge, auto_refresh):
            Commits, flushes, refreshes, or expunges the session based on the provided options.
        _add(self, db_session, db_object, *, auto_commit, auto_expunge, auto_refresh):
            Adds a new object to the session and handles commit, flush, refresh, or expunge.
        _delete(self, db_session, db_object, *, auto_commit, auto_expunge):
            Deletes an object from the session and handles commit, flush, refresh, or expunge.
        _get(self, db_session, id, *, loader_options, execution_options, auto_expunge, with_for_update, auto_commit):
            Retrieves an object from the database by its ID.
        _execute_returning_all(self, db_session, statement, *, loader_options, execution_options, auto_commit, auto_expunge, auto_refresh, with_for_update):
            Executes a statement and returns all results.
        _execute_returning_one(self, db_session, statement, *, loader_options, execution_options, auto_commit, auto_expunge, auto_refresh, with_for_update):
            Executes a statement and returns a single result.
        _add_pagination(self, statement, filters):
            Adds pagination to a statement based on filters.
        _add_filters(self, statement, filters):
            Adds filters to a statement based on the provided filters.
        _prepare_statement(self, statement, *, loader_options, execution_options, with_for_update):
            Prepares a statement with loader options, execution options, and for update options.
        _update_db_object(db_object, object_in):
            Updates a database object with new data.
        _verify_init(self):
            Verifies that the repository is properly initialized.
        _set_id_field(self, id_field):
            Sets the ID field for the repository.
    """

    model_type: type[BaseModelT]
    id_attribute: str | InstrumentedAttribute[Any] = "id"

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

    def create(
        self,
        db_session: Session,
        db_object: BaseModelT,
        *,
        auto_commit: bool | None = None,
        auto_expunge: bool | None = None,
        auto_refresh: bool | None = None,
    ) -> BaseModelT:
        return self._add(
            db_session=db_session,
            db_object=db_object,
            auto_commit=auto_commit,
            auto_expunge=auto_expunge,
            auto_refresh=auto_refresh,
        )

    def read(
        self,
        db_session: Session,
        id: Any,
        *,
        loader_options: tuple[_AbstractLoad] | None = None,
        execution_options: dict[str, Any] | None = None,
        auto_expunge: bool | None = None,
        auto_commit: bool | None = False,
        with_for_update: bool = False,
    ) -> BaseModelT | None:
        return self._get(
            db_session=db_session,
            id=id,
            loader_options=loader_options,
            execution_options=execution_options,
            auto_expunge=auto_expunge,
            auto_commit=auto_commit,
            with_for_update=with_for_update,
        )

    def read_multiple(
        self,
        db_session: Session,
        filters: InputSchema | None = None,
        *,
        loader_options: tuple[_AbstractLoad] | None = None,
        execution_options: dict[str, Any] | None = None,
        auto_commit: bool | None = False,
        auto_expunge: bool | None = None,
        with_for_update: bool = False,
    ) -> Sequence[BaseModelT]:
        statement = select(self.model)
        statement = self._add_filters(statement=statement, filters=filters)
        statement = self._add_pagination(statement=statement, filters=filters)
        return self._execute_returning_all(
            db_session=db_session,
            statement=statement,
            loader_options=loader_options,
            execution_options=execution_options,
            auto_commit=auto_commit,
            auto_expunge=auto_expunge,
            auto_refresh=False,
            with_for_update=with_for_update,
        )

    def update(
        self,
        db_session: Session,
        id: Any,
        object_in: InputSchema,
        *,
        loader_options: tuple[_AbstractLoad] | None = None,
        execution_options: dict[str, Any] | None = None,
        auto_commit: bool | None = None,
        auto_expunge: bool | None = None,
        auto_refresh: bool | None = None,
        with_for_update: bool = True,
    ) -> BaseModelT | None:
        db_object = self._get(
            db_session=db_session,
            id=id,
            loader_options=loader_options,
            execution_options=execution_options,
            auto_expunge=False,
            with_for_update=with_for_update,
            auto_commit=False,
        )
        if db_object is not None:
            return self.update_db_object(
                db_session=db_session,
                db_object=db_object,
                object_in=object_in,
                auto_commit=auto_commit,
                auto_expunge=auto_expunge,
                auto_refresh=auto_refresh,
            )

        self._maybe_commit_or_flush_or_refresh_or_expunge(
            db_session=db_session,
            db_object=db_object,
            auto_commit=auto_commit,
            auto_expunge=auto_expunge,
            auto_refresh=auto_refresh,
        )

        return db_object

    def update_db_object(
        self,
        db_session: Session,
        db_object: BaseModelT,
        object_in: InputSchema,
        *,
        auto_commit: bool | None = None,
        auto_expunge: bool | None = None,
        auto_refresh: bool | None = None,
    ) -> BaseModelT | None:
        self._update_db_object(db_object=db_object, object_in=object_in)
        return self._add(
            db_session=db_session,
            db_object=db_object,
            auto_commit=auto_commit,
            auto_expunge=auto_expunge,
            auto_refresh=auto_refresh,
        )

    def delete(
        self,
        db_session: Session,
        id: Any,
        *,
        loader_options: tuple[_AbstractLoad] | None = None,
        execution_options: dict[str, Any] | None = None,
        auto_commit: bool | None = None,
        auto_expunge: bool | None = None,
        with_for_update: bool = False,
    ) -> None:
        db_object = self._get(
            db_session=db_session,
            id=id,
            loader_options=loader_options,
            execution_options=execution_options,
            auto_expunge=False,
            auto_commit=False,
            with_for_update=with_for_update,
        )
        if db_object is not None:
            self.delete_db_object(
                db_session=db_session,
                db_object=db_object,
                auto_commit=auto_commit,
                auto_expunge=auto_expunge,
            )
        else:
            self._maybe_commit_or_flush_or_refresh_or_expunge(
                db_session=db_session,
                db_object=db_object,
                auto_commit=auto_commit,
                auto_expunge=auto_expunge,
                auto_refresh=False,
            )

    def delete_db_object(
        self,
        db_session: Session,
        db_object: BaseModelT,
        *,
        auto_commit: bool | None = None,
        auto_expunge: bool | None = None,
    ) -> None:
        self._delete(
            db_session=db_session,
            db_object=db_object,
            auto_commit=auto_commit,
            auto_expunge=auto_expunge,
        )

    def count(
        self,
        db_session: Session,
        filters: InputSchema | None = None,
        *,
        loader_options: tuple[_AbstractLoad] | None = None,
        execution_options: dict[str, Any] | None = None,
        auto_commit: bool | None = False,
    ) -> int:
        statement = select(func.count()).select_from(self.model)
        statement = self._add_filters(statement=statement, filters=filters)
        return self._execute_returning_one(
            db_session=db_session,
            statement=statement,
            loader_options=loader_options,
            execution_options=execution_options,
            auto_commit=auto_commit,
            auto_expunge=False,
            auto_refresh=False,
            with_for_update=False,
        )

    def _maybe_commit_or_flush_or_refresh_or_expunge(
        self,
        db_session: Session,
        db_object: ResultT | Sequence[ResultT] | None,
        *,
        auto_commit: bool | None,
        auto_expunge: bool | None,
        auto_refresh: bool | None,
        refresh_columns: list[str] | None = None,
    ) -> None:
        if auto_commit is True or (auto_commit is None and self.auto_commit):
            db_session.commit()
        else:
            db_session.flush()

        if db_object is not None:
            instances: Sequence[ResultT] = (
                db_object if isinstance(db_object, Sequence) else [db_object]
            )
            if auto_refresh is True or (auto_refresh is None and self.auto_refresh):
                for instance in instances:
                    db_session.refresh(instance, attribute_names=refresh_columns)
            if auto_expunge is True or (auto_expunge is None and self.auto_expunge):
                for instance in instances:
                    db_session.expunge(instance)

    def _add(
        self,
        db_session: Session,
        db_object: BaseModelT,
        *,
        auto_commit: bool | None,
        auto_expunge: bool | None,
        auto_refresh: bool | None,
    ) -> BaseModelT:
        db_session.add(db_object)
        self._maybe_commit_or_flush_or_refresh_or_expunge(
            db_session=db_session,
            db_object=db_object,
            auto_commit=auto_commit,
            auto_expunge=auto_expunge,
            auto_refresh=auto_refresh,
        )

        return db_object

    def _delete(
        self,
        db_session: Session,
        db_object: BaseModelT,
        *,
        auto_commit: bool | None,
        auto_expunge: bool | None,
    ) -> None:
        db_session.delete(db_object)
        self._maybe_commit_or_flush_or_refresh_or_expunge(
            db_session=db_session,
            db_object=db_object,
            auto_commit=auto_commit,
            auto_expunge=auto_expunge,
            auto_refresh=False,
        )

    def _get(
        self,
        db_session: Session,
        id: Any,
        *,
        loader_options: tuple[_AbstractLoad] | None,
        execution_options: dict[str, Any] | None,
        auto_expunge: bool | None,
        with_for_update: bool,
        auto_commit: bool | None = False,
    ) -> BaseModelT | None:
        current_loader_options = (
            loader_options if loader_options is not None else self.loader_options
        )
        current_execution_options = (
            execution_options
            if execution_options is not None
            else self.execution_options
        )
        db_object = db_session.get(
            self.model,
            id,
            options=current_loader_options,
            execution_options=current_execution_options or EMPTY_DICT,
            with_for_update=with_for_update,
        )
        self._maybe_commit_or_flush_or_refresh_or_expunge(
            db_session=db_session,
            db_object=db_object,
            auto_commit=auto_commit,
            auto_expunge=auto_expunge,
            auto_refresh=False,
        )

        return db_object

    def _execute(
        self,
        db_session: Session,
        statement: Select[SelectT],
        *,
        loader_options: tuple[_AbstractLoad] | None,
        execution_options: dict[str, Any] | None,
        with_for_update: bool = False,
    ) -> Result[SelectT]:
        statement = self._prepare_statement(
            statement=statement,
            loader_options=loader_options,
            execution_options=execution_options,
            with_for_update=with_for_update,
        )
        return db_session.execute(statement)

    def _execute_returning_all(
        self,
        db_session: Session,
        statement: Select[SelectT],
        *,
        loader_options: tuple[_AbstractLoad] | None,
        execution_options: dict[str, Any] | None,
        auto_commit: bool | None,
        auto_expunge: bool | None,
        auto_refresh: bool | None,
        with_for_update: bool,
    ) -> Sequence[Any]:
        res = self._execute(
            db_session=db_session,
            statement=statement,
            loader_options=loader_options,
            execution_options=execution_options,
            with_for_update=with_for_update,
        )
        db_objects: Sequence[Any] = res.scalars().all()
        self._maybe_commit_or_flush_or_refresh_or_expunge(
            db_session=db_session,
            db_object=db_objects,
            auto_commit=auto_commit,
            auto_expunge=auto_expunge,
            auto_refresh=auto_refresh,
        )
        return db_objects

    def _execute_returning_one(
        self,
        db_session: Session,
        statement: Select[SelectT],
        *,
        loader_options: tuple[_AbstractLoad] | None,
        execution_options: dict[str, Any] | None,
        auto_commit: bool | None,
        auto_expunge: bool | None,
        auto_refresh: bool | None,
        with_for_update: bool,
    ) -> Any:
        res = self._execute(
            db_session=db_session,
            statement=statement,
            loader_options=loader_options,
            execution_options=execution_options,
            with_for_update=with_for_update,
        )
        db_object = res.scalar_one()
        self._maybe_commit_or_flush_or_refresh_or_expunge(
            db_session=db_session,
            db_object=db_object,
            auto_commit=auto_commit,
            auto_expunge=auto_expunge,
            auto_refresh=auto_refresh,
        )
        return db_object

    def _execute_returning_one_or_none(
        self,
        db_session: Session,
        statement: Select[SelectT],
        *,
        loader_options: tuple[_AbstractLoad] | None,
        execution_options: dict[str, Any] | None,
        auto_commit: bool | None,
        auto_expunge: bool | None,
        auto_refresh: bool | None,
        with_for_update: bool = False,
    ) -> Any | None:
        res = self._execute(
            db_session=db_session,
            statement=statement,
            loader_options=loader_options,
            execution_options=execution_options,
            with_for_update=with_for_update,
        )
        db_object = res.scalar_one_or_none()
        self._maybe_commit_or_flush_or_refresh_or_expunge(
            db_session=db_session,
            db_object=db_object,
            auto_commit=auto_commit,
            auto_expunge=auto_expunge,
            auto_refresh=auto_refresh,
        )
        return db_object

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
    def _update_db_object(db_object: BaseModelT, object_in: InputSchema) -> None:
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
