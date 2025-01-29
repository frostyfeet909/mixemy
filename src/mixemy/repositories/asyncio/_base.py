from abc import ABC
from collections.abc import Sequence
from typing import Any

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.strategy_options import (
    _AbstractLoad,  # pyright: ignore[reportPrivateUsage]
)
from sqlalchemy.util import EMPTY_DICT

from mixemy.repositories._base import BaseRepository
from mixemy.schemas import InputSchema
from mixemy.types import BaseModelType, ResultT, SelectT


class BaseAsyncRepository(BaseRepository[BaseModelType], ABC):
    async def create(
        self,
        db_session: AsyncSession,
        db_object: BaseModelType,
        *,
        auto_commit: bool | None = None,
        auto_expunge: bool | None = None,
        auto_refresh: bool | None = None,
    ) -> BaseModelType:
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
    ) -> BaseModelType | None:
        return await self._get(
            db_session=db_session,
            id=id,
            loader_options=loader_options,
            execution_options=execution_options,
            auto_expunge=auto_expunge,
            auto_commit=auto_commit,
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
    ) -> Sequence[BaseModelType]:
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
    ) -> BaseModelType | None:
        db_object = await self._get(
            db_session=db_session,
            id=id,
            loader_options=loader_options,
            execution_options=execution_options,
            auto_expunge=auto_expunge,
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

        return db_object

    async def update_db_object(
        self,
        db_session: AsyncSession,
        db_object: BaseModelType,
        object_in: InputSchema,
        *,
        auto_commit: bool | None = None,
        auto_expunge: bool | None = None,
        auto_refresh: bool | None = None,
    ) -> BaseModelType | None:
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
    ) -> None:
        db_object = await self._get(
            db_session=db_session,
            id=id,
            loader_options=loader_options,
            execution_options=execution_options,
            auto_expunge=auto_expunge,
        )
        if db_object is not None:
            await self.delete_db_object(
                db_session=db_session,
                db_object=db_object,
                auto_commit=auto_commit,
                auto_expunge=auto_expunge,
            )

    async def delete_db_object(
        self,
        db_session: AsyncSession,
        db_object: BaseModelType,
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
        db_object: BaseModelType,
        *,
        auto_commit: bool | None,
        auto_expunge: bool | None,
        auto_refresh: bool | None,
    ) -> BaseModelType:
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
        db_object: BaseModelType,
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
        auto_commit: bool | None = False,
    ) -> BaseModelType | None:
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
    ) -> Sequence[Any]:
        statement = self._prepare_statement(
            statement=statement,
            loader_options=loader_options,
            execution_options=execution_options,
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
    ) -> Any:
        statement = self._prepare_statement(
            statement=statement,
            loader_options=loader_options,
            execution_options=execution_options,
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
