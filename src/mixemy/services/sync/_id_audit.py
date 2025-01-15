from abc import ABC

from mixemy.repositories.sync import IdAuditSyncRepository
from mixemy.services.sync._audit import AuditSyncService
from mixemy.services.sync._id import IdSyncService
from mixemy.types import (
    CreateSchemaType,
    FilterSchemaType,
    IdAuditModelType,
    OutputSchemaType,
    UpdateSchemaType,
)


class IdAuditSyncService(
    IdSyncService[
        IdAuditModelType,
        CreateSchemaType,
        UpdateSchemaType,
        FilterSchemaType,
        OutputSchemaType,
    ],
    AuditSyncService[
        IdAuditModelType,
        CreateSchemaType,
        UpdateSchemaType,
        FilterSchemaType,
        OutputSchemaType,
    ],
    ABC,
):
    repository_type: type[IdAuditSyncRepository[IdAuditModelType]]  # pyright: ignore[reportIncompatibleVariableOverride] - https://github.com/python/typing/issues/548
    repository: IdAuditSyncRepository[IdAuditModelType]  # pyright: ignore[reportIncompatibleVariableOverride] - https://github.com/python/typing/issues/548
