from sqlalchemy import UUID as SQLAUUID
from sqlalchemy.orm import Mapped, mapped_column
from uuid_utils.compat import UUID

from mixemy.models._base import BaseModel
from mixemy.utils import generate_uuid


class IdModel(BaseModel):
    """IdModel is an abstract base model that provides a UUID primary key for derived models.

    Attributes:
        id (UUID): The primary key for the model, automatically generated using the `generate_uuid` function.
    """

    __abstract__ = True

    id: Mapped[UUID] = mapped_column(SQLAUUID, primary_key=True, default=generate_uuid)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}>"
