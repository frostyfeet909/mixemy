from abc import ABC

from mixemy.repositories._base import AuditRepository
from mixemy.repositories.sync._base import BaseSyncRepository
from mixemy.types import AuditModelType


class AuditSyncRepository(
    BaseSyncRepository[AuditModelType], AuditRepository[AuditModelType], ABC
):
    pass
