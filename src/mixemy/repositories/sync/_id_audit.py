from abc import ABC

from mixemy.repositories.sync._audit import AuditSyncRepository
from mixemy.repositories.sync._id import IdSyncRepository
from mixemy.types import IdAuditModelType


class IdAuditSyncRepository(
    IdSyncRepository[IdAuditModelType],
    AuditSyncRepository[IdAuditModelType],
    ABC,
):
    pass
