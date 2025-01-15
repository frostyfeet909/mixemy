from abc import ABC
from typing import Literal, overload

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from mixemy.repositories._base import IdRepository
from mixemy.repositories.asyncio._base import BaseAsyncRepository
from mixemy.schemas import InputSchema
from mixemy.types import ID, IdModelType


class IdAsyncRepository(
    BaseAsyncRepository[IdModelType], IdRepository[IdModelType], ABC
):
    async def update_by_id(
        self,
        db_session: AsyncSession,
        id: ID,
        object_in: InputSchema,
    ) -> IdModelType:
        return await self.update(
            db_session=db_session,
            db_object=await self.read_by_id(
                db_session=db_session, id=id, raise_on_empty=True
            ),
            object_in=object_in,
        )

    @overload
    async def read_by_id(
        self, db_session: AsyncSession, id: ID, raise_on_empty: Literal[True]
    ) -> IdModelType: ...

    @overload
    async def read_by_id(
        self, db_session: AsyncSession, id: ID, raise_on_empty: Literal[False]
    ) -> IdModelType | None: ...

    @overload
    async def read_by_id(
        self, db_session: AsyncSession, id: ID, raise_on_empty: bool
    ) -> IdModelType | None: ...

    async def read_by_id(
        self, db_session: AsyncSession, id: ID, raise_on_empty: bool = False
    ) -> IdModelType | None:
        db_object = await db_session.get(self.model, id)

        if db_object is None and raise_on_empty:
            msg = f"Could not find {self.model} of id {id}"
            raise ValueError(msg)

        return db_object

    async def delete_by_id(
        self,
        db_session: AsyncSession,
        id: ID,
        raise_on_empty: bool,
    ) -> None:
        if raise_on_empty:
            await self._delete_refreshing(
                db_session=db_session,
                db_object=await self.read_by_id(
                    db_session=db_session,
                    id=id,
                    raise_on_empty=raise_on_empty,
                ),
            )
        else:
            statement = delete(self.model).where(self.model.id == id)
            await db_session.execute(statement)
            await db_session.commit()
