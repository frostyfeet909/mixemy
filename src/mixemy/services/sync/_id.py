from abc import ABC

from mixemy.repositories.sync import IdSyncRepository
from mixemy.services.sync._base import BaseSyncService
from mixemy.types import (
    CreateSchemaType,
    FilterSchemaType,
    IdModelType,
    OutputSchemaType,
    UpdateSchemaType,
)


class IdSyncService(
    BaseSyncService[
        IdModelType,
        CreateSchemaType,
        UpdateSchemaType,
        FilterSchemaType,
        OutputSchemaType,
    ],
    ABC,
):
    repository_type: type[IdSyncRepository[IdModelType]]  # pyright: ignore[reportIncompatibleVariableOverride] - https://github.com/python/typing/issues/548
    repository: IdSyncRepository[IdModelType]
