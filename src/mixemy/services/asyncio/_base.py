from abc import ABC
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.strategy_options import (
    _AbstractLoad,  # pyright: ignore[reportPrivateUsage]
)

from mixemy.repositories.asyncio import BaseAsyncRepository
from mixemy.services._base import BaseService
from mixemy.types import (
    BaseModelType,
    CreateSchemaType,
    FilterSchemaType,
    OutputSchemaType,
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

    def __init__(self, db_session: AsyncSession) -> None:
        super().__init__()
        self.repository = self.repository_type()
        self.model = self.repository.model
        self.db_session = db_session

    async def create(
        self,
        object_in: CreateSchemaType,
        *,
        auto_expunge: bool | None = None,
        auto_refresh: bool | None = None,
        auto_commit: bool | None = None,
    ) -> OutputSchemaType:
        return self._to_schema(
            model=await self.repository.create(
                db_session=self.db_session,
                db_object=self._to_model(schema=object_in),
                auto_expunge=auto_expunge,
                auto_refresh=auto_refresh,
                auto_commit=auto_commit,
            )
        )

    async def read(
        self,
        id: Any,
        *,
        loader_options: tuple[_AbstractLoad] | None = None,
        execution_options: dict[str, Any] | None = None,
        auto_expunge: bool | None = None,
        auto_commit: bool | None = None,
    ) -> OutputSchemaType | None:
        return (
            self._to_schema(model=model)
            if (
                model := await self.repository.read(
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

    async def read_multiple(
        self,
        filters: FilterSchemaType | None = None,
        *,
        loader_options: tuple[_AbstractLoad] | None = None,
        execution_options: dict[str, Any] | None = None,
        auto_expunge: bool | None = None,
        auto_commit: bool | None = None,
    ) -> list[OutputSchemaType]:
        return [
            self._to_schema(model=model)
            for model in await self.repository.read_multiple(
                db_session=self.db_session,
                filters=filters,
                loader_options=loader_options,
                execution_options=execution_options,
                auto_expunge=auto_expunge,
                auto_commit=auto_commit,
            )
        ]

    async def update(
        self,
        id: Any,
        object_in: UpdateSchemaType,
        *,
        loader_options: tuple[_AbstractLoad] | None = None,
        execution_options: dict[str, Any] | None = None,
        auto_expunge: bool | None = None,
        auto_refresh: bool | None = None,
        auto_commit: bool | None = None,
    ) -> OutputSchemaType | None:
        return (
            self._to_schema(model)
            if (
                model := await self.repository.update(
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

    async def delete(
        self,
        id: Any,
        *,
        loader_options: tuple[_AbstractLoad] | None = None,
        execution_options: dict[str, Any] | None = None,
        auto_expunge: bool | None = None,
        auto_commit: bool | None = None,
    ) -> None:
        await self.repository.delete(
            db_session=self.db_session,
            id=id,
            auto_expunge=auto_expunge,
            auto_commit=auto_commit,
            loader_options=loader_options,
            execution_options=execution_options,
        )
