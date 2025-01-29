from sqlalchemy import UUID
from sqlalchemy.orm import Mapped, mapped_column

from mixemy.models._base import BaseModel
from mixemy.types import ID
from mixemy.utils import generate_uuid


class IdModel(BaseModel):
    __abstract__ = True

    id: Mapped[ID] = mapped_column(UUID, primary_key=True, default=generate_uuid)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}>"
