from abc import ABC

from mixemy.repositories._base import IdRepository
from mixemy.repositories.sync._base import BaseSyncRepository
from mixemy.types import IdModelType


class IdSyncRepository(BaseSyncRepository[IdModelType], IdRepository[IdModelType], ABC):
    pass
