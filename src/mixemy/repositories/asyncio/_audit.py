from abc import ABC

from mixemy.repositories._base import AuditRepository
from mixemy.repositories.asyncio._base import BaseAsyncRepository
from mixemy.types import AuditModelType


class AuditAsyncRepository(
    BaseAsyncRepository[AuditModelType], AuditRepository[AuditModelType], ABC
):
    pass
