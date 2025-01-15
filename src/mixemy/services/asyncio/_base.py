from abc import ABC

from sqlalchemy.ext.asyncio import AsyncSession

from mixemy.repositories.asyncio import BaseAsyncRepository
from mixemy.services._base import BaseService
from mixemy.types import (
    BaseModelType,
    CreateSchemaType,
    FilterSchemaType,
    OutputSchemaType,
    PaginationSchemaType,
    UpdateSchemaType,
)


class BaseAsyncService(
    BaseService[
        BaseModelType,
        CreateSchemaType,
        UpdateSchemaType,
        FilterSchemaType,
        OutputSchemaType,
    ],
    ABC,
):
    repository_type: type[BaseAsyncRepository[BaseModelType]]

    def __init__(self) -> None:
        super().__init__()
        self.repository = self.repository_type()
        self.model = self.repository.model

    async def create(
        self, db_session: AsyncSession, object_in: CreateSchemaType
    ) -> BaseModelType:
        return await self.repository.create(
            db_session=db_session, db_object=self._to_model(schema=object_in)
        )

    async def read_multi(
        self,
        db_session: AsyncSession,
        filters: FilterSchemaType | None = None,
        pagination: PaginationSchemaType | None = None,
    ) -> list[OutputSchemaType]:
        return [
            self._to_schema(model=model)
            for model in await self.repository.read_multi(
                db_session=db_session, before_filter=filters, after_filter=pagination
            )
        ]
