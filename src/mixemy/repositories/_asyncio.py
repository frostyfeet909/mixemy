from abc import ABC
from collections.abc import Sequence
from typing import Any, Generic

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy.orm.strategy_options import (
    _AbstractLoad,  # pyright: ignore[reportPrivateUsage]
)
from sqlalchemy.util import EMPTY_DICT

from mixemy._exceptions import MixemyRepositorySetupError
from mixemy.schemas import InputSchema
from mixemy.schemas.paginations import PaginationFields, PaginationFilter
from mixemy.types import BaseModelT, ResultT, SelectT
from mixemy.utils import unpack_schema


class BaseAsyncRepository(Generic[BaseModelT], ABC):
    """
    Base asynchronous repository class providing CRUD operations for a given SQLAlchemy model.
    Attributes:
        model_type (type[BaseModelT]): The SQLAlchemy model type.
        id_attribute (str | InstrumentedAttribute[Any]): The attribute used as the primary key. Defaults to "id".
        default_loader_options (tuple[_AbstractLoad] | None): Default loader options for SQLAlchemy queries.
        default_execution_options (dict[str, Any] | None): Default execution options for SQLAlchemy queries.
        default_auto_expunge (bool): Whether to automatically expunge objects from the session after operations. Defaults to False.
        default_auto_refresh (bool): Whether to automatically refresh objects after operations. Defaults to True.
        default_auto_commit (bool): Whether to automatically commit the session after operations. Defaults to False.
    Methods:
        __init__(self, *, loader_options=None, execution_options=None, auto_expunge=False, auto_refresh=True, auto_commit=False):
            Initializes the repository with optional custom settings.
        async create(self, db_session, db_object, *, auto_commit=None, auto_expunge=None, auto_refresh=None):
            Asynchronously creates a new object in the database.
        async read(self, db_session, id, *, loader_options=None, execution_options=None, auto_expunge=None, auto_commit=False, with_for_update=False):
            Asynchronously reads an object from the database by its ID.
        async read_multiple(self, db_session, filters=None, *, loader_options=None, execution_options=None, auto_commit=False, auto_expunge=None, with_for_update=False):
            Asynchronously reads multiple objects from the database based on filters.
        async update(self, db_session, id, object_in, *, loader_options=None, execution_options=None, auto_commit=None, auto_expunge=None, auto_refresh=None, with_for_update=True):
            Asynchronously updates an object in the database by its ID.
        async update_db_object(self, db_session, db_object, object_in, *, auto_commit=None, auto_expunge=None, auto_refresh=None):
            Asynchronously updates an existing database object.
        async delete(self, db_session, id, *, loader_options=None, execution_options=None, auto_commit=None, auto_expunge=None, with_for_update=False):
            Asynchronously deletes an object from the database by its ID.
        async delete_db_object(self, db_session, db_object, *, auto_commit=None, auto_expunge=None):
            Asynchronously deletes an existing database object.
        async count(self, db_session, filters=None, *, loader_options=None, execution_options=None, auto_commit=False):
            Asynchronously counts the number of objects in the database based on filters.
        async _maybe_commit_or_flush_or_refresh_or_expunge(self, db_session, db_object, *, auto_commit, auto_expunge, auto_refresh):
            Helper method to commit, flush, refresh, or expunge objects from the session based on settings.
        async _add(self, db_session, db_object, *, auto_commit, auto_expunge, auto_refresh):
            Helper method to add an object to the session and handle post-add operations.
        async _delete(self, db_session, db_object, *, auto_commit, auto_expunge):
            Helper method to delete an object from the session and handle post-delete operations.
        async _get(self, db_session, id, *, loader_options, execution_options, auto_expunge, with_for_update, auto_commit=False):
            Helper method to get an object from the database by its ID.
        async _execute_returning_all(self, db_session, statement, *, loader_options, execution_options, auto_commit, auto_expunge, auto_refresh, with_for_update=False):
            Helper method to execute a statement and return all results.
        async _execute_returning_one(self, db_session, statement, *, loader_options, execution_options, auto_commit, auto_expunge, auto_refresh, with_for_update=False):
            Helper method to execute a statement and return a single result.
        def _add_pagination(self, statement, filters):
            Helper method to add pagination to a SQLAlchemy statement.
        def _add_filters(self, statement, filters):
            Helper method to add filters to a SQLAlchemy statement.
        def _prepare_statement(self, statement, *, loader_options, execution_options, with_for_update):
            Helper method to prepare a SQLAlchemy statement with options and execution settings.
        def _update_db_object(db_object, object_in):
            Helper method to update a database object with new values.
        def _verify_init(self):
            Helper method to verify that required attributes are set during initialization.
        def _set_id_field(self, id_field):
            Helper method to set the ID field for the model.
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

    async def create(
        self,
        db_session: AsyncSession,
        db_object: BaseModelT,
        *,
        auto_commit: bool | None = None,
        auto_expunge: bool | None = None,
        auto_refresh: bool | None = None,
    ) -> BaseModelT:
        return await self._add(
            db_session=db_session,
            db_object=db_object,
            auto_commit=auto_commit,
            auto_expunge=auto_expunge,
            auto_refresh=auto_refresh,
        )

    async def read(
        self,
        db_session: AsyncSession,
        id: Any,
        *,
        loader_options: tuple[_AbstractLoad] | None = None,
        execution_options: dict[str, Any] | None = None,
        auto_expunge: bool | None = None,
        auto_commit: bool | None = False,
        with_for_update: bool = False,
    ) -> BaseModelT | None:
        return await self._get(
            db_session=db_session,
            id=id,
            loader_options=loader_options,
            execution_options=execution_options,
            auto_expunge=auto_expunge,
            auto_commit=auto_commit,
            with_for_update=with_for_update,
        )

    async def read_multiple(
        self,
        db_session: AsyncSession,
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
        return await self._execute_returning_all(
            db_session=db_session,
            statement=statement,
            loader_options=loader_options,
            execution_options=execution_options,
            auto_commit=auto_commit,
            auto_expunge=auto_expunge,
            auto_refresh=False,
            with_for_update=with_for_update,
        )

    async def update(
        self,
        db_session: AsyncSession,
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
        db_object = await self._get(
            db_session=db_session,
            id=id,
            loader_options=loader_options,
            execution_options=execution_options,
            auto_expunge=False,
            with_for_update=with_for_update,
            auto_commit=False,
        )
        if db_object is not None:
            return await self.update_db_object(
                db_session=db_session,
                db_object=db_object,
                object_in=object_in,
                auto_commit=auto_commit,
                auto_expunge=auto_expunge,
                auto_refresh=auto_refresh,
            )

        await self._maybe_commit_or_flush_or_refresh_or_expunge(
            db_session=db_session,
            db_object=db_object,
            auto_commit=auto_commit,
            auto_expunge=auto_expunge,
            auto_refresh=auto_refresh,
        )

        return db_object

    async def update_db_object(
        self,
        db_session: AsyncSession,
        db_object: BaseModelT,
        object_in: InputSchema,
        *,
        auto_commit: bool | None = None,
        auto_expunge: bool | None = None,
        auto_refresh: bool | None = None,
    ) -> BaseModelT | None:
        self._update_db_object(db_object=db_object, object_in=object_in)
        return await self._add(
            db_session=db_session,
            db_object=db_object,
            auto_commit=auto_commit,
            auto_expunge=auto_expunge,
            auto_refresh=auto_refresh,
        )

    async def delete(
        self,
        db_session: AsyncSession,
        id: Any,
        *,
        loader_options: tuple[_AbstractLoad] | None = None,
        execution_options: dict[str, Any] | None = None,
        auto_commit: bool | None = None,
        auto_expunge: bool | None = None,
        with_for_update: bool = False,
    ) -> None:
        db_object = await self._get(
            db_session=db_session,
            id=id,
            loader_options=loader_options,
            execution_options=execution_options,
            auto_expunge=False,
            auto_commit=False,
            with_for_update=with_for_update,
        )
        if db_object is not None:
            await self.delete_db_object(
                db_session=db_session,
                db_object=db_object,
                auto_commit=auto_commit,
                auto_expunge=auto_expunge,
            )
        else:
            await self._maybe_commit_or_flush_or_refresh_or_expunge(
                db_session=db_session,
                db_object=db_object,
                auto_commit=auto_commit,
                auto_expunge=auto_expunge,
                auto_refresh=False,
            )

    async def delete_db_object(
        self,
        db_session: AsyncSession,
        db_object: BaseModelT,
        *,
        auto_commit: bool | None = None,
        auto_expunge: bool | None = None,
    ) -> None:
        await self._delete(
            db_session=db_session,
            db_object=db_object,
            auto_commit=auto_commit,
            auto_expunge=auto_expunge,
        )

    async def count(
        self,
        db_session: AsyncSession,
        filters: InputSchema | None = None,
        *,
        loader_options: tuple[_AbstractLoad] | None = None,
        execution_options: dict[str, Any] | None = None,
        auto_commit: bool | None = False,
    ) -> int:
        statement = select(func.count()).select_from(self.model)
        statement = self._add_filters(statement=statement, filters=filters)
        return await self._execute_returning_one(
            db_session=db_session,
            statement=statement,
            loader_options=loader_options,
            execution_options=execution_options,
            auto_commit=auto_commit,
            auto_expunge=False,
            auto_refresh=False,
            with_for_update=False,
        )

    async def _maybe_commit_or_flush_or_refresh_or_expunge(
        self,
        db_session: AsyncSession,
        db_object: ResultT | Sequence[ResultT] | None,
        *,
        auto_commit: bool | None,
        auto_expunge: bool | None,
        auto_refresh: bool | None,
    ) -> None:
        if auto_commit is True or (auto_commit is None and self.auto_commit):
            await db_session.commit()
        else:
            await db_session.flush()

        if db_object is not None:
            instances: Sequence[ResultT] = (
                db_object if isinstance(db_object, Sequence) else [db_object]
            )
            if auto_refresh is True or (auto_refresh is None and self.auto_refresh):
                for instance in instances:
                    await db_session.refresh(instance)
            if auto_expunge is True or (auto_expunge is None and self.auto_expunge):
                for instance in instances:
                    db_session.expunge(instance)

    async def _add(
        self,
        db_session: AsyncSession,
        db_object: BaseModelT,
        *,
        auto_commit: bool | None,
        auto_expunge: bool | None,
        auto_refresh: bool | None,
    ) -> BaseModelT:
        db_session.add(db_object)
        await self._maybe_commit_or_flush_or_refresh_or_expunge(
            db_session=db_session,
            db_object=db_object,
            auto_commit=auto_commit,
            auto_expunge=auto_expunge,
            auto_refresh=auto_refresh,
        )

        return db_object

    async def _delete(
        self,
        db_session: AsyncSession,
        db_object: BaseModelT,
        *,
        auto_commit: bool | None,
        auto_expunge: bool | None,
    ) -> None:
        await db_session.delete(db_object)
        await self._maybe_commit_or_flush_or_refresh_or_expunge(
            db_session=db_session,
            db_object=db_object,
            auto_commit=auto_commit,
            auto_expunge=auto_expunge,
            auto_refresh=False,
        )

    async def _get(
        self,
        db_session: AsyncSession,
        id: Any,
        *,
        loader_options: tuple[_AbstractLoad] | None,
        execution_options: dict[str, Any] | None,
        auto_expunge: bool | None,
        with_for_update: bool = False,
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
        db_object = await db_session.get(
            self.model,
            id,
            options=current_loader_options,
            execution_options=current_execution_options or EMPTY_DICT,
            with_for_update=with_for_update,
        )
        await self._maybe_commit_or_flush_or_refresh_or_expunge(
            db_session=db_session,
            db_object=db_object,
            auto_commit=auto_commit,
            auto_expunge=auto_expunge,
            auto_refresh=False,
        )

        return db_object

    async def _execute_returning_all(
        self,
        db_session: AsyncSession,
        statement: Select[SelectT],
        *,
        loader_options: tuple[_AbstractLoad] | None,
        execution_options: dict[str, Any] | None,
        auto_commit: bool | None,
        auto_expunge: bool | None,
        auto_refresh: bool | None,
        with_for_update: bool = False,
    ) -> Sequence[Any]:
        statement = self._prepare_statement(
            statement=statement,
            loader_options=loader_options,
            execution_options=execution_options,
            with_for_update=with_for_update,
        )
        res = await db_session.execute(statement)
        db_objects: Sequence[Any] = res.scalars().all()
        await self._maybe_commit_or_flush_or_refresh_or_expunge(
            db_session=db_session,
            db_object=db_objects,
            auto_commit=auto_commit,
            auto_expunge=auto_expunge,
            auto_refresh=auto_refresh,
        )
        return db_objects

    async def _execute_returning_one(
        self,
        db_session: AsyncSession,
        statement: Select[SelectT],
        *,
        loader_options: tuple[_AbstractLoad] | None,
        execution_options: dict[str, Any] | None,
        auto_commit: bool | None,
        auto_expunge: bool | None,
        auto_refresh: bool | None,
        with_for_update: bool = False,
    ) -> Any:
        statement = self._prepare_statement(
            statement=statement,
            loader_options=loader_options,
            execution_options=execution_options,
            with_for_update=with_for_update,
        )
        res = await db_session.execute(statement)
        db_object = res.scalar_one()
        await self._maybe_commit_or_flush_or_refresh_or_expunge(
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
