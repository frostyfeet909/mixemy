from abc import ABC

from mixemy.repositories.asyncio import IdAuditAsyncRepository
from mixemy.services.asyncio._audit import AuditAsyncService
from mixemy.services.asyncio._id import IdAsyncService
from mixemy.types import (
    CreateSchemaType,
    FilterSchemaType,
    IdAuditModelType,
    OutputSchemaType,
    UpdateSchemaType,
)


class IdAuditAsyncService(
    IdAsyncService[
        IdAuditModelType,
        CreateSchemaType,
        UpdateSchemaType,
        FilterSchemaType,
        OutputSchemaType,
    ],
    AuditAsyncService[
        IdAuditModelType,
        CreateSchemaType,
        UpdateSchemaType,
        FilterSchemaType,
        OutputSchemaType,
    ],
    ABC,
):
    repository_type: type[IdAuditAsyncRepository[IdAuditModelType]]  # pyright: ignore[reportIncompatibleVariableOverride] - https://github.com/python/typing/issues/548
    repository: IdAuditAsyncRepository[IdAuditModelType]  # pyright: ignore[reportIncompatibleVariableOverride] - https://github.com/python/typing/issues/548
