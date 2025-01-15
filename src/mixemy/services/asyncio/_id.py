from abc import ABC

from mixemy.repositories.asyncio import IdAsyncRepository
from mixemy.services.asyncio._base import BaseAsyncService
from mixemy.types import (
    ID,
    CreateSchemaType,
    FilterSchemaType,
    IdModelType,
    OutputSchemaType,
    UpdateSchemaType,
)


class IdAsyncService(
    BaseAsyncService[
        IdModelType,
        CreateSchemaType,
        UpdateSchemaType,
        FilterSchemaType,
        OutputSchemaType,
    ],
    ABC,
):
    repository_type: type[IdAsyncRepository[IdModelType]]  # pyright: ignore[reportIncompatibleVariableOverride] - https://github.com/python/typing/issues/548
    repository: IdAsyncRepository[IdModelType]

    async def read(self, id: ID) -> OutputSchemaType | None:
        return (
            self._to_schema(model=model)
            if (
                model := await self.repository.read_by_id(
                    db_session=self.db_session, id=id, raise_on_empty=False
                )
            )
            else None
        )

    async def update(self, id: ID, object_in: UpdateSchemaType) -> OutputSchemaType:
        return self._to_schema(
            model=await self.repository.update_by_id(
                db_session=self.db_session,
                id=id,
                object_in=object_in,
            )
        )

    async def delete(self, id: ID) -> None:
        await self.repository.delete_by_id(
            db_session=self.db_session, id=id, raise_on_empty=False
        )
