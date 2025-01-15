from abc import ABC

from mixemy.repositories.asyncio import AuditAsyncRepository
from mixemy.services.asyncio._base import BaseAsyncService
from mixemy.types import (
    AuditModelType,
    CreateSchemaType,
    FilterSchemaType,
    OutputSchemaType,
    UpdateSchemaType,
)


class AuditAsyncService(
    BaseAsyncService[
        AuditModelType,
        CreateSchemaType,
        UpdateSchemaType,
        FilterSchemaType,
        OutputSchemaType,
    ],
    ABC,
):
    repository_type: type[AuditAsyncRepository[AuditModelType]]  # pyright: ignore[reportIncompatibleVariableOverride] - https://github.com/python/typing/issues/548
    repository: AuditAsyncRepository[AuditModelType]
