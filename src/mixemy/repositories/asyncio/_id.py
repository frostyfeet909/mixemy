from abc import ABC

from mixemy.repositories._base import IdRepository
from mixemy.repositories.asyncio._base import BaseAsyncRepository
from mixemy.types import IdModelType


class IdAsyncRepository(
    BaseAsyncRepository[IdModelType], IdRepository[IdModelType], ABC
):
    pass
