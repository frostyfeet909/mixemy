from abc import ABC

from mixemy.repositories.asyncio._audit import AuditAsyncRepository
from mixemy.repositories.asyncio._id import IdAsyncRepository
from mixemy.types import IdAuditModelType


class IdAuditAsyncRepository(
    IdAsyncRepository[IdAuditModelType],
    AuditAsyncRepository[IdAuditModelType],
    ABC,
):
    pass
