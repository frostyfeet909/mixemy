from abc import ABC

from mixemy.repositories.sync import AuditSyncRepository
from mixemy.services.sync._base import BaseSyncService
from mixemy.types import (
    AuditModelType,
    CreateSchemaType,
    FilterSchemaType,
    OutputSchemaType,
    UpdateSchemaType,
)


class AuditSyncService(
    BaseSyncService[
        AuditModelType,
        CreateSchemaType,
        UpdateSchemaType,
        FilterSchemaType,
        OutputSchemaType,
    ],
    ABC,
):
    repository_type: type[AuditSyncRepository[AuditModelType]]  # pyright: ignore[reportIncompatibleVariableOverride] - https://github.com/python/typing/issues/548
    repository: AuditSyncRepository[AuditModelType]
