from abc import ABC

from mixemy.repositories._base._base import BaseRepository
from mixemy.types import (
    IdModelType,
)


class IdRepository(BaseRepository[IdModelType], ABC):
    id_attribute = "id"
