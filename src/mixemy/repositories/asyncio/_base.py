from abc import ABC
from collections.abc import Sequence
from typing import Any

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from mixemy.repositories._base import BaseRepository
from mixemy.schemas import InputSchema
from mixemy.types import (
    BaseModelType,
)


class BaseAsyncRepository(BaseRepository[BaseModelType], ABC):
    async def create(
        self, db_session: AsyncSession, db_object: BaseModelType
    ) -> BaseModelType:
        return await self._add_refreshing(db_session=db_session, db_object=db_object)

    async def read_multi(
        self,
        db_session: AsyncSession,
        filters: InputSchema | None = None,
    ) -> Sequence[BaseModelType]:
        return await self._execute_returning_all(
            db_session=db_session,
            statement=self._add_filters(statement=None, filters=filters),
        )

    async def update(
        self,
        db_session: AsyncSession,
        db_object: BaseModelType,
        object_in: InputSchema,
    ) -> BaseModelType:
        self._update_db_object(db_object=db_object, object_in=object_in)
        return await self._add_refreshing(db_session=db_session, db_object=db_object)

    async def delete(self, db_session: AsyncSession, db_object: BaseModelType) -> None:
        await self._delete_refreshing(db_session=db_session, db_object=db_object)

    async def count(
        self,
        db_session: AsyncSession,
        before_filter: InputSchema | None = None,
    ) -> int:
        return await self._execute_returning_one(
            db_session=db_session,
            statement=self._add_before_filter(
                statement=select(func.count()).select_from(self.model),
                filters=before_filter,
            ),
        )

    @staticmethod
    async def _execute_returning_all(
        db_session: AsyncSession, statement: Select[Any]
    ) -> Sequence[BaseModelType]:
        res = await db_session.execute(statement)
        return res.scalars().all()

    @staticmethod
    async def _execute_returning_one(
        db_session: AsyncSession, statement: Select[Any]
    ) -> Any:
        res = await db_session.execute(statement=statement)
        return res.scalar_one()

    @staticmethod
    async def _add_refreshing(
        db_session: AsyncSession, db_object: BaseModelType
    ) -> BaseModelType:
        db_session.add(db_object)
        await db_session.commit()
        await db_session.refresh(db_object)

        return db_object

    @staticmethod
    async def _delete_refreshing(
        db_session: AsyncSession, db_object: BaseModelType
    ) -> None:
        await db_session.delete(db_object)
        await db_session.commit()
        await db_session.refresh(db_object)
