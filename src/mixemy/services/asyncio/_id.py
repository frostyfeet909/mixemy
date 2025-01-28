from abc import ABC

from mixemy.repositories.asyncio import IdAsyncRepository
from mixemy.services.asyncio._base import BaseAsyncService
from mixemy.types import (
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
