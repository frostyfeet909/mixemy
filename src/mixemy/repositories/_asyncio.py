from abc import ABC
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Literal, overload

from sqlalchemy import (
    CursorResult,
    Delete,
    Result,
    Row,
    ScalarResult,
    Select,
    Update,
    func,
    select,
)
from sqlalchemy.orm.strategy_options import (
    _AbstractLoad,  # pyright: ignore[reportPrivateUsage]
)
from sqlalchemy.util import EMPTY_DICT

from mixemy.exceptions import (
    MixemyRepositoryPermissionError,
    MixemyRepositoryReadOnlyError,
    MixemyRepositorySetupError,
)
from mixemy.repositories.permission_strategies import PermissionStrategyFactory
from mixemy.schemas import InputSchema
from mixemy.schemas.paginations import PaginationFields, PaginationFilter
from mixemy.types import BaseModelT, SelectT, permission_strategies
from mixemy.utils import pack_sequence, unpack_schema

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from mixemy.models import BaseModel


class BaseAsyncRepository[BaseModelT: BaseModel](ABC):
    """Base asynchronous repository class providing CRUD operations for a given SQLAlchemy model.

    Attributes:
        model (type[BaseModelT]): The SQLAlchemy model type.
        default_loader_options (tuple[_AbstractLoad] | None): Default loader options for SQLAlchemy queries.
        default_execution_options (dict[str, Any] | None): Default execution options for SQLAlchemy queries.
        default_auto_expunge (bool): Whether to automatically expunge objects from the session after operations. Defaults to False.
        default_auto_refresh (bool): Whether to automatically refresh objects after operations. Defaults to True.
        default_auto_commit (bool): Whether to automatically commit the session after operations. Defaults to False.
        default_is_read_only (bool): Whether the repository is in read-only mode. Defaults to False.
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
        async execute_returning_all(self, db_session, statement, *, loader_options, execution_options, auto_commit, auto_expunge, auto_refresh, with_for_update=False):
            Helper method to execute a statement and return all results.
        async execute_returning_one(self, db_session, statement, *, loader_options, execution_options, auto_commit, auto_expunge, auto_refresh, with_for_update=False):
            Helper method to execute a statement and return a single result.
        def add_pagination(self, statement, filters):
            Helper method to add pagination to a SQLAlchemy statement.
        def add_filters(self, statement, filters):
            Helper method to add filters to a SQLAlchemy statement.
        def _prepare_statement(self, statement, *, loader_options, execution_options, with_for_update):
            Helper method to prepare a SQLAlchemy statement with options and execution settings.
        def _update_db_object(db_object, object_in):
            Helper method to update a database object with new values.
        def handle_read_only(self, is_read_only=None):
            Helper method to handle read-only mode for the repository.
        def _verify_init(self):
            Helper method to verify that required attributes are set during initialization.
    """

    model: type[BaseModelT]

    default_loader_options: tuple[_AbstractLoad] | None = None
    default_execution_options: dict[str, Any] | None = None
    default_auto_expunge: bool = False
    default_auto_refresh: bool = True
    default_auto_commit: bool = False
    default_is_read_only: bool = False

    def __init__(
        self,
        *,
        loader_options: tuple[_AbstractLoad] | None = None,
        execution_options: dict[str, Any] | None = None,
        auto_expunge: bool | None = None,
        auto_refresh: bool | None = None,
        auto_commit: bool | None = None,
        is_read_only: bool | None = None,
    ) -> None:
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
        self.is_read_only = (
            is_read_only if is_read_only is not None else self.default_is_read_only
        )
        self._verify_init()

    async def create(
        self,
        db_session: "AsyncSession",
        db_object: BaseModelT,
        *,
        auto_commit: bool | None = None,
        auto_expunge: bool | None = None,
        auto_refresh: bool | None = None,
        is_read_only: bool | None = None,
    ) -> BaseModelT:
        self.handle_read_only(is_read_only=is_read_only)
        return await self._add(
            db_session=db_session,
            db_object=db_object,
            auto_commit=auto_commit,
            auto_expunge=auto_expunge,
            auto_refresh=auto_refresh,
        )

    async def read(
        self,
        db_session: "AsyncSession",
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
        db_session: "AsyncSession",
        filters: InputSchema | None = None,
        *,
        loader_options: tuple[_AbstractLoad] | None = None,
        execution_options: dict[str, Any] | None = None,
        auto_commit: bool | None = False,
        auto_expunge: bool | None = None,
        with_for_update: bool = False,
    ) -> Sequence[BaseModelT]:
        statement = select(self.model)
        statement = self.add_filters(statement=statement, filters=filters)
        statement = self.add_pagination(statement=statement, filters=filters)
        return await self.execute_returning_all(
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
        db_session: "AsyncSession",
        id: Any,
        object_in: InputSchema,
        *,
        loader_options: tuple[_AbstractLoad] | None = None,
        execution_options: dict[str, Any] | None = None,
        auto_commit: bool | None = None,
        auto_expunge: bool | None = None,
        auto_refresh: bool | None = None,
        with_for_update: bool = True,
        is_read_only: bool | None = None,
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

        return await self.update_db_object(
            db_session=db_session,
            db_object=db_object,
            object_in=object_in,
            auto_commit=auto_commit,
            auto_expunge=auto_expunge,
            auto_refresh=auto_refresh,
            is_read_only=is_read_only,
        )

    async def update_db_object(
        self,
        db_session: "AsyncSession",
        db_object: BaseModelT | None,
        object_in: InputSchema,
        *,
        auto_commit: bool | None = None,
        auto_expunge: bool | None = None,
        auto_refresh: bool | None = None,
        is_read_only: bool | None = None,
    ) -> BaseModelT | None:
        self.handle_read_only(is_read_only=is_read_only)
        if db_object is not None:
            self._update_db_object(db_object=db_object, object_in=object_in)
            return await self._add(
                db_session=db_session,
                db_object=db_object,
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

        return None

    async def delete(
        self,
        db_session: "AsyncSession",
        id: Any,
        *,
        loader_options: tuple[_AbstractLoad] | None = None,
        execution_options: dict[str, Any] | None = None,
        auto_commit: bool | None = None,
        auto_expunge: bool | None = None,
        with_for_update: bool = False,
        is_read_only: bool | None = None,
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
        await self.delete_db_object(
            db_session=db_session,
            db_object=db_object,
            auto_commit=auto_commit,
            auto_expunge=auto_expunge,
            is_read_only=is_read_only,
        )

    async def delete_db_object(
        self,
        db_session: "AsyncSession",
        db_object: BaseModelT | None,
        *,
        auto_commit: bool | None = None,
        auto_expunge: bool | None = None,
        is_read_only: bool | None = None,
    ) -> None:
        self.handle_read_only(is_read_only=is_read_only)
        if db_object is not None:
            await self._delete(
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

    async def count(
        self,
        db_session: "AsyncSession",
        filters: InputSchema | None = None,
        *,
        loader_options: tuple[_AbstractLoad] | None = None,
        execution_options: dict[str, Any] | None = None,
        auto_commit: bool | None = False,
    ) -> int:
        statement = select(func.count()).select_from(self.model)
        statement = self.add_filters(statement=statement, filters=filters)
        return await self.execute_returning_one(
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
        db_session: "AsyncSession",
        db_object: Sequence[object] | object | None,
        *,
        auto_commit: bool | None = None,
        auto_expunge: bool | None = None,
        auto_refresh: bool | None = None,
        refresh_columns: list[str] | None = None,
    ) -> None:
        if auto_commit is True or (auto_commit is None and self.auto_commit):
            await db_session.commit()
        else:
            await db_session.flush()

        if db_object is not None:
            instances = pack_sequence(db_object)
            if auto_refresh is True or (auto_refresh is None and self.auto_refresh):
                for instance in instances:
                    await db_session.refresh(instance, attribute_names=refresh_columns)
            if auto_expunge is True or (auto_expunge is None and self.auto_expunge):
                for instance in instances:
                    db_session.expunge(instance)

    async def _add(
        self,
        db_session: "AsyncSession",
        db_object: BaseModelT,
        *,
        auto_commit: bool | None = None,
        auto_expunge: bool | None = None,
        auto_refresh: bool | None = None,
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
        db_session: "AsyncSession",
        db_object: BaseModelT,
        *,
        auto_commit: bool | None = None,
        auto_expunge: bool | None = None,
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
        db_session: "AsyncSession",
        id: Any,
        *,
        loader_options: tuple[_AbstractLoad] | None = None,
        execution_options: dict[str, Any] | None = None,
        auto_expunge: bool | None = None,
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

    @overload
    async def _execute(
        self,
        db_session: "AsyncSession",
        statement: Select[SelectT],
        *,
        loader_options: tuple[_AbstractLoad] | None,
        execution_options: dict[str, Any] | None,
        with_for_update: bool,
        is_scalar: Literal[False],
        auto_commit: bool | None,
    ) -> Result[SelectT]: ...

    @overload
    async def _execute(
        self,
        db_session: "AsyncSession",
        statement: Select[SelectT] | Delete | Update,
        *,
        loader_options: tuple[_AbstractLoad] | None,
        execution_options: dict[str, Any] | None,
        with_for_update: bool,
        is_scalar: Literal[True] = True,
        auto_commit: bool | None,
    ) -> ScalarResult[Any]: ...

    @overload
    async def _execute(
        self,
        db_session: "AsyncSession",
        statement: Delete | Update,
        *,
        loader_options: tuple[_AbstractLoad] | None,
        execution_options: dict[str, Any] | None,
        with_for_update: bool,
        is_scalar: Literal[False],
        auto_commit: bool | None,
    ) -> CursorResult[Any]: ...

    async def _execute(
        self,
        db_session: "AsyncSession",
        statement: Select[SelectT] | Delete | Update,
        *,
        loader_options: tuple[_AbstractLoad] | None = None,
        execution_options: dict[str, Any] | None = None,
        with_for_update: bool = False,
        is_scalar: bool = True,
        auto_commit: bool | None = False,
    ) -> Result[SelectT] | ScalarResult[Any] | CursorResult[Any]:
        statement = self._prepare_statement(
            statement=statement,
            loader_options=loader_options,
            execution_options=execution_options,
            with_for_update=with_for_update,
        )
        res = await db_session.execute(statement)

        await self._maybe_commit_or_flush_or_refresh_or_expunge(
            db_session=db_session,
            db_object=None,
            auto_commit=auto_commit,
            auto_expunge=False,
            auto_refresh=False,
        )

        return res if not is_scalar else res.scalars()

    @overload
    async def execute_returning_all(
        self,
        db_session: "AsyncSession",
        statement: Select[SelectT],
        *,
        loader_options: tuple[_AbstractLoad] | None,
        execution_options: dict[str, Any] | None,
        auto_commit: bool | None,
        auto_expunge: bool | None,
        auto_refresh: bool | None,
        with_for_update: bool,
        is_scalar: Literal[False],
    ) -> Sequence[SelectT]: ...

    @overload
    async def execute_returning_all(
        self,
        db_session: "AsyncSession",
        statement: Select[SelectT] | Update | Delete,
        *,
        loader_options: tuple[_AbstractLoad] | None,
        execution_options: dict[str, Any] | None,
        auto_commit: bool | None,
        auto_expunge: bool | None,
        auto_refresh: bool | None,
        with_for_update: bool,
        is_scalar: Literal[True] = True,
    ) -> Sequence[Any]: ...

    @overload
    async def execute_returning_all(
        self,
        db_session: "AsyncSession",
        statement: Update | Delete,
        *,
        loader_options: tuple[_AbstractLoad] | None,
        execution_options: dict[str, Any] | None,
        auto_commit: bool | None,
        auto_expunge: bool | None,
        auto_refresh: bool | None,
        with_for_update: bool,
        is_scalar: Literal[False],
    ) -> Sequence[Row[Any]]: ...

    async def execute_returning_all(
        self,
        db_session: "AsyncSession",
        statement: Select[SelectT] | Update | Delete,
        *,
        loader_options: tuple[_AbstractLoad] | None = None,
        execution_options: dict[str, Any] | None = None,
        auto_commit: bool | None = None,
        auto_expunge: bool | None = None,
        auto_refresh: bool | None = None,
        with_for_update: bool = False,
        is_scalar: bool = True,
    ) -> Sequence[SelectT] | Sequence[Any] | Sequence[Row[Any]]:
        res = await self._execute(
            db_session=db_session,
            statement=statement,
            loader_options=loader_options,
            execution_options=execution_options,
            with_for_update=with_for_update,
            is_scalar=is_scalar,
            auto_commit=False,
        )
        db_objects = res.all()
        await self._maybe_commit_or_flush_or_refresh_or_expunge(
            db_session=db_session,
            db_object=db_objects,
            auto_commit=auto_commit,
            auto_expunge=auto_expunge,
            auto_refresh=auto_refresh,
        )
        return db_objects

    @overload
    async def execute_returning_one(
        self,
        db_session: "AsyncSession",
        statement: Select[SelectT] | Update | Delete,
        *,
        loader_options: tuple[_AbstractLoad] | None,
        execution_options: dict[str, Any] | None,
        auto_commit: bool | None,
        auto_expunge: bool | None,
        auto_refresh: bool | None,
        with_for_update: bool,
        is_scalar: Literal[True] = True,
    ) -> Any: ...

    @overload
    async def execute_returning_one(
        self,
        db_session: "AsyncSession",
        statement: Select[SelectT],
        *,
        loader_options: tuple[_AbstractLoad] | None,
        execution_options: dict[str, Any] | None,
        auto_commit: bool | None,
        auto_expunge: bool | None,
        auto_refresh: bool | None,
        with_for_update: bool,
        is_scalar: Literal[False],
    ) -> Row[SelectT]: ...

    @overload
    async def execute_returning_one(
        self,
        db_session: "AsyncSession",
        statement: Update | Delete,
        *,
        loader_options: tuple[_AbstractLoad] | None,
        execution_options: dict[str, Any] | None,
        auto_commit: bool | None,
        auto_expunge: bool | None,
        auto_refresh: bool | None,
        with_for_update: bool,
        is_scalar: Literal[False],
    ) -> Row[Any]: ...

    async def execute_returning_one(
        self,
        db_session: "AsyncSession",
        statement: Select[SelectT] | Update | Delete,
        *,
        loader_options: tuple[_AbstractLoad] | None = None,
        execution_options: dict[str, Any] | None = None,
        auto_commit: bool | None = None,
        auto_expunge: bool | None = None,
        auto_refresh: bool | None = None,
        with_for_update: bool = False,
        is_scalar: bool = True,
    ) -> Any | Row[SelectT] | Row[Any]:
        res = await self._execute(
            db_session=db_session,
            statement=statement,
            loader_options=loader_options,
            execution_options=execution_options,
            with_for_update=with_for_update,
            is_scalar=is_scalar,
            auto_commit=False,
        )
        db_object = res.one()
        await self._maybe_commit_or_flush_or_refresh_or_expunge(
            db_session=db_session,
            db_object=db_object,
            auto_commit=auto_commit,
            auto_expunge=auto_expunge,
            auto_refresh=auto_refresh,
        )
        return db_object

    @overload
    async def execute_returning_one_or_none(
        self,
        db_session: "AsyncSession",
        statement: Select[SelectT] | Update | Delete,
        *,
        loader_options: tuple[_AbstractLoad] | None,
        execution_options: dict[str, Any] | None,
        auto_commit: bool | None,
        auto_expunge: bool | None,
        auto_refresh: bool | None,
        with_for_update: bool,
        is_scalar: Literal[True] = True,
    ) -> Any | None: ...

    @overload
    async def execute_returning_one_or_none(
        self,
        db_session: "AsyncSession",
        statement: Select[SelectT],
        *,
        loader_options: tuple[_AbstractLoad] | None,
        execution_options: dict[str, Any] | None,
        auto_commit: bool | None,
        auto_expunge: bool | None,
        auto_refresh: bool | None,
        with_for_update: bool = False,
        is_scalar: Literal[False],
    ) -> Row[SelectT] | None: ...

    @overload
    async def execute_returning_one_or_none(
        self,
        db_session: "AsyncSession",
        statement: Update | Delete,
        *,
        loader_options: tuple[_AbstractLoad] | None,
        execution_options: dict[str, Any] | None,
        auto_commit: bool | None,
        auto_expunge: bool | None,
        auto_refresh: bool | None,
        with_for_update: bool = False,
        is_scalar: Literal[False],
    ) -> Row[Any] | None: ...

    async def execute_returning_one_or_none(
        self,
        db_session: "AsyncSession",
        statement: Select[SelectT] | Update | Delete,
        *,
        loader_options: tuple[_AbstractLoad] | None = None,
        execution_options: dict[str, Any] | None = None,
        auto_commit: bool | None = None,
        auto_expunge: bool | None = None,
        auto_refresh: bool | None = None,
        with_for_update: bool = False,
        is_scalar: bool = True,
    ) -> Row[SelectT] | Row[Any] | Any | None:
        res = await self._execute(
            db_session=db_session,
            statement=statement,
            loader_options=loader_options,
            execution_options=execution_options,
            with_for_update=with_for_update,
            is_scalar=is_scalar,
            auto_commit=False,
        )
        db_object = res.one_or_none()
        await self._maybe_commit_or_flush_or_refresh_or_expunge(
            db_session=db_session,
            db_object=db_object,
            auto_commit=auto_commit,
            auto_expunge=auto_expunge,
            auto_refresh=auto_refresh,
        )
        return db_object

    def add_pagination(
        self, statement: Select[SelectT], filters: InputSchema | None
    ) -> Select[SelectT]:
        if isinstance(filters, PaginationFilter):
            statement = statement.offset(filters.offset).limit(filters.limit)

        return statement

    @overload
    def add_filters(
        self, statement: Select[SelectT], filters: InputSchema | None
    ) -> Select[SelectT]: ...

    @overload
    def add_filters(self, statement: Update, filters: InputSchema | None) -> Update: ...

    @overload
    def add_filters(self, statement: Delete, filters: InputSchema | None) -> Delete: ...

    def add_filters(
        self, statement: Select[SelectT] | Update | Delete, filters: InputSchema | None
    ) -> Select[SelectT] | Update | Delete:
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

    def handle_read_only(
        self,
        is_read_only: bool | None = None,
    ) -> None:
        """Handle read-only mode for the repository.

        This method checks if the repository is in read-only mode and raises an error if necessary.
        This is to be called on editing operations like create, update, or delete.
        """
        if is_read_only is True or (is_read_only is None and self.is_read_only):
            raise MixemyRepositoryReadOnlyError(
                repository=self,
                model=self.model,
            )

    @overload
    def _prepare_statement(
        self,
        statement: Select[SelectT],
        *,
        loader_options: tuple[_AbstractLoad] | None,
        execution_options: dict[str, Any] | None,
        with_for_update: bool,
    ) -> Select[SelectT]: ...

    @overload
    def _prepare_statement(
        self,
        statement: Update,
        *,
        loader_options: tuple[_AbstractLoad] | None,
        execution_options: dict[str, Any] | None,
        with_for_update: bool,
    ) -> Update: ...

    @overload
    def _prepare_statement(
        self,
        statement: Delete,
        *,
        loader_options: tuple[_AbstractLoad] | None,
        execution_options: dict[str, Any] | None,
        with_for_update: bool,
    ) -> Delete: ...

    def _prepare_statement(
        self,
        statement: Select[SelectT] | Update | Delete,
        *,
        loader_options: tuple[_AbstractLoad] | None = None,
        execution_options: dict[str, Any] | None = None,
        with_for_update: bool = False,
    ) -> Select[SelectT] | Update | Delete:
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

        if with_for_update and isinstance(statement, Select):
            statement = statement.with_for_update()

        return statement

    @staticmethod
    def _update_db_object(db_object: BaseModelT, object_in: InputSchema) -> None:
        for field, value in unpack_schema(schema=object_in).items():
            if hasattr(db_object, field):
                setattr(db_object, field, value)

    def _verify_init(self) -> None:
        for field in ["model"]:
            if not hasattr(self, field):
                raise MixemyRepositorySetupError(repository=self, undefined_field=field)


class PermissionAsyncRepository(BaseAsyncRepository[BaseModelT], ABC):
    """PermissionAsyncRepository is an abstract base class that provides asynchronous methods for handling database operations with user permission checks.

    Attributes:
        user_id_attribute (str): The attribute representing the user ID.
        user_joined_table (str | None): The attribute representing the joined table for user permissions.
        default_raise_permission_error (bool): Default flag to raise permission error.
    Methods:
        __init__(self, *, loader_options: tuple[_AbstractLoad] | None = None, execution_options: dict[str, Any] | None = None, auto_expunge: bool | None = False, auto_refresh: bool | None = True, auto_commit: bool | None = False, raise_permission_error: bool | None = True) -> None:
            Initializes the repository with the given options.
        async read_with_permission(self, db_session: "AsyncSession", id: Any, user_id: Any, *, loader_options: tuple[_AbstractLoad] | None = None, execution_options: dict[str, Any] | None = None, auto_expunge: bool | None = None, auto_commit: bool | None = False, with_for_update: bool = False, raise_permission_error: bool | None = False) -> BaseModelT | None:
            Reads a single database object with permission checks.
        async read_multiple_with_permission(self, db_session: "AsyncSession", user_id: Any, filters: InputSchema | None = None, *, loader_options: tuple[_AbstractLoad] | None = None, execution_options: dict[str, Any] | None = None, auto_commit: bool | None = False, auto_expunge: bool | None = None, with_for_update: bool = False) -> Sequence[BaseModelT]:
            Reads multiple database objects with permission checks.
        async update_with_permission(self, db_session: "AsyncSession", id: Any, object_in: InputSchema, user_id: Any, *, loader_options: tuple[_AbstractLoad] | None = None, execution_options: dict[str, Any] | None = None, auto_commit: bool | None = None, auto_expunge: bool | None = None, auto_refresh: bool | None = None, with_for_update: bool = True, raise_permission_error: bool | None = None) -> BaseModelT | None:
            Updates a database object with permission checks.
        async update_db_object_with_permission(self, db_session: "AsyncSession", db_object: BaseModelT | None, object_in: InputSchema, user_id: Any, *, auto_commit: bool | None = None, auto_expunge: bool | None = None, auto_refresh: bool | None = None, raise_permission_error: bool | None = None) -> BaseModelT | None:
            Updates a database object with permission checks.
        async delete_with_permission(self, db_session: "AsyncSession", id: Any, user_id: Any, *, loader_options: tuple[_AbstractLoad] | None = None, execution_options: dict[str, Any] | None = None, auto_commit: bool | None = None, auto_expunge: bool | None = None, with_for_update: bool = False, raise_permission_error: bool | None = None) -> None:
            Deletes a database object with permission checks.
        async delete_db_object_with_permission(self, db_session: "AsyncSession", db_object: BaseModelT | None, user_id: Any, *, auto_commit: bool | None = None, auto_expunge: bool | None = None, raise_permission_error: bool | None = None) -> None:
            Deletes a database object with permission checks.
        async count_with_permission(self, db_session: "AsyncSession", user_id: Any, filters: InputSchema | None = None, *, loader_options: tuple[_AbstractLoad] | None = None, execution_options: dict[str, Any] | None = None, auto_commit: bool | None = False) -> int:
            Counts the number of database objects with permission checks.
        add_permission_filter(self, statement: Select[SelectT], user_id: Any) -> Select[SelectT]:
            Adds a permission filter to the SQL statement.
        handle_permission_on_db_oject(self, db_object: BaseModelT | None, user_id: Any, raise_permission_error: bool | None = None) -> BaseModelT | None:
            Checks if the user has permission on the database object.
        _verify_init(self) -> None:
            Verifies the initialization of the repository.
    """

    user_id_attribute: str = "user_id"
    user_joined_table: str | None = None

    default_raise_permission_error: bool = True
    default_permission_strategy: permission_strategies = "strict"

    def __init__(
        self,
        *,
        loader_options: tuple[_AbstractLoad] | None = None,
        execution_options: dict[str, Any] | None = None,
        auto_expunge: bool | None = None,
        auto_refresh: bool | None = None,
        auto_commit: bool | None = None,
        is_read_only: bool | None = None,
        raise_permission_error: bool | None = None,
        permission_strategy: permission_strategies | None = None,
    ) -> None:
        self.raise_permission_error = (
            raise_permission_error
            if raise_permission_error is not None
            else self.default_raise_permission_error
        )
        super().__init__(
            loader_options=loader_options,
            execution_options=execution_options,
            auto_expunge=auto_expunge,
            auto_refresh=auto_refresh,
            auto_commit=auto_commit,
            is_read_only=is_read_only,
        )
        self.permission_strategy = PermissionStrategyFactory.create_permission_strategy(
            strategy=(
                permission_strategy
                if permission_strategy is not None
                else self.default_permission_strategy
            ),
            model=self.model,
            user_id_attribute=self.user_id_attribute,
            user_joined_table=self.user_joined_table,
        )

    async def read_with_permission(
        self,
        db_session: "AsyncSession",
        id: Any,
        user_id: Any,
        *,
        loader_options: tuple[_AbstractLoad] | None = None,
        execution_options: dict[str, Any] | None = None,
        auto_expunge: bool | None = None,
        auto_commit: bool | None = False,
        with_for_update: bool = False,
        raise_permission_error: bool | None = False,
    ) -> BaseModelT | None:
        db_object = await self._get(
            db_session=db_session,
            id=id,
            loader_options=loader_options,
            execution_options=execution_options,
            auto_expunge=auto_expunge,
            auto_commit=auto_commit,
            with_for_update=with_for_update,
        )

        if not self.handle_permission_on_db_oject(
            db_object=db_object,
            user_id=user_id,
            raise_permission_error=raise_permission_error,
        ):
            return None

        return db_object

    async def read_multiple_with_permission(
        self,
        db_session: "AsyncSession",
        user_id: Any,
        filters: InputSchema | None = None,
        *,
        loader_options: tuple[_AbstractLoad] | None = None,
        execution_options: dict[str, Any] | None = None,
        auto_commit: bool | None = False,
        auto_expunge: bool | None = None,
        with_for_update: bool = False,
    ) -> Sequence[BaseModelT]:
        statement = select(self.model)
        statement = self.add_filters(statement=statement, filters=filters)
        statement = self.add_pagination(statement=statement, filters=filters)
        statement = self.add_permission_filter(statement=statement, user_id=user_id)
        return await self.execute_returning_all(
            db_session=db_session,
            statement=statement,
            loader_options=loader_options,
            execution_options=execution_options,
            auto_commit=auto_commit,
            auto_expunge=auto_expunge,
            auto_refresh=False,
            with_for_update=with_for_update,
        )

    async def update_with_permission(
        self,
        db_session: "AsyncSession",
        id: Any,
        object_in: InputSchema,
        user_id: Any,
        *,
        loader_options: tuple[_AbstractLoad] | None = None,
        execution_options: dict[str, Any] | None = None,
        auto_commit: bool | None = None,
        auto_expunge: bool | None = None,
        auto_refresh: bool | None = None,
        with_for_update: bool = True,
        is_read_only: bool | None = None,
        raise_permission_error: bool | None = None,
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

        return await self.update_db_object_with_permission(
            db_session=db_session,
            user_id=user_id,
            db_object=db_object,
            object_in=object_in,
            auto_commit=auto_commit,
            auto_expunge=auto_expunge,
            auto_refresh=auto_refresh,
            is_read_only=is_read_only,
            raise_permission_error=raise_permission_error,
        )

    async def update_db_object_with_permission(
        self,
        db_session: "AsyncSession",
        db_object: BaseModelT | None,
        object_in: InputSchema,
        user_id: Any,
        *,
        auto_commit: bool | None = None,
        auto_expunge: bool | None = None,
        auto_refresh: bool | None = None,
        is_read_only: bool | None = None,
        raise_permission_error: bool | None = None,
    ) -> BaseModelT | None:
        if not self.handle_permission_on_db_oject(
            db_object=db_object,
            user_id=user_id,
            raise_permission_error=raise_permission_error,
        ):
            return None

        return await self.update_db_object(
            db_session=db_session,
            db_object=db_object,
            object_in=object_in,
            auto_commit=auto_commit,
            auto_expunge=auto_expunge,
            auto_refresh=auto_refresh,
            is_read_only=is_read_only,
        )

    async def delete_with_permission(
        self,
        db_session: "AsyncSession",
        id: Any,
        user_id: Any,
        *,
        loader_options: tuple[_AbstractLoad] | None = None,
        execution_options: dict[str, Any] | None = None,
        auto_commit: bool | None = None,
        auto_expunge: bool | None = None,
        with_for_update: bool = False,
        is_read_only: bool | None = None,
        raise_permission_error: bool | None = None,
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

        await self.delete_db_object_with_permission(
            db_session=db_session,
            db_object=db_object,
            user_id=user_id,
            auto_commit=auto_commit,
            auto_expunge=auto_expunge,
            is_read_only=is_read_only,
            raise_permission_error=raise_permission_error,
        )

    async def delete_db_object_with_permission(
        self,
        db_session: "AsyncSession",
        db_object: BaseModelT | None,
        user_id: Any,
        *,
        auto_commit: bool | None = None,
        auto_expunge: bool | None = None,
        is_read_only: bool | None = None,
        raise_permission_error: bool | None = None,
    ) -> None:
        if not self.handle_permission_on_db_oject(
            db_object=db_object,
            user_id=user_id,
            raise_permission_error=raise_permission_error,
        ):
            return None

        return await self.delete_db_object(
            db_session=db_session,
            db_object=db_object,
            auto_commit=auto_commit,
            auto_expunge=auto_expunge,
            is_read_only=is_read_only,
        )

    async def count_with_permission(
        self,
        db_session: "AsyncSession",
        user_id: Any,
        filters: InputSchema | None = None,
        *,
        loader_options: tuple[_AbstractLoad] | None = None,
        execution_options: dict[str, Any] | None = None,
        auto_commit: bool | None = False,
    ) -> int:
        statement = select(func.count()).select_from(self.model)
        statement = self.add_filters(statement=statement, filters=filters)
        statement = self.add_permission_filter(statement=statement, user_id=user_id)
        return await self.execute_returning_one(
            db_session=db_session,
            statement=statement,
            loader_options=loader_options,
            execution_options=execution_options,
            auto_commit=auto_commit,
            auto_expunge=False,
            auto_refresh=False,
            with_for_update=False,
        )

    def add_permission_filter(
        self,
        statement: Select[SelectT],
        user_id: Any,
    ) -> Select[SelectT]:
        return self.permission_strategy.add_permission_filter(
            statement=statement,
            user_id=user_id,
        )

    def handle_permission_on_db_oject(
        self,
        db_object: BaseModelT | None,
        user_id: Any,
        raise_permission_error: bool | None = None,
    ) -> bool:
        """Check if the user has permission on the database object.

        If the user does not have permission, it raises a MixemyRepositoryPermissionError or return false.
        If the user has permission, it returns true.
        """
        authenticated, object_id = (
            self.permission_strategy.check_permission_on_db_oject(
                db_object=db_object,
                user_id=user_id,
            )
        )

        if authenticated:
            return True

        if raise_permission_error is False or (
            raise_permission_error is None and self.raise_permission_error is False
        ):
            return False

        raise MixemyRepositoryPermissionError(
            repository=self, object_id=object_id, user_id=user_id
        )

    def _verify_init(self) -> None:
        for field in ["model", "user_id_attribute"]:
            if not hasattr(self, field):
                raise MixemyRepositorySetupError(repository=self, undefined_field=field)

        if self.user_joined_table is None and not hasattr(
            self.model, self.user_id_attribute
        ):
            raise MixemyRepositorySetupError(
                repository=self,
                undefined_field=str(self.user_id_attribute),
                message=f"User ID attribute {self.user_id_attribute} not found on model",
            )

        if self.user_joined_table is not None:
            if not hasattr(self.model, self.user_joined_table):
                raise MixemyRepositorySetupError(
                    repository=self,
                    undefined_field=str(self.user_joined_table),
                    message=f"User joined table {self.user_joined_table} not found on model",
                )
            if not hasattr(
                getattr(self.model, self.user_joined_table), self.user_id_attribute
            ):
                raise MixemyRepositorySetupError(
                    repository=self,
                    undefined_field=str(self.user_id_attribute),
                    message=f"User ID attribute {self.user_id_attribute} not found on joined table",
                )
