from abc import ABC

from mixemy.services._base._base import BaseService
from mixemy.types import (
    AuditModelType,
    CreateSchemaType,
    FilterSchemaType,
    OutputSchemaType,
    UpdateSchemaType,
)


class IdService(
    BaseService[
        AuditModelType,
        CreateSchemaType,
        UpdateSchemaType,
        FilterSchemaType,
        OutputSchemaType,
    ],
    ABC,
):
    pass
