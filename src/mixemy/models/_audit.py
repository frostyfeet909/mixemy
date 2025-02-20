from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from mixemy.models._base import BaseModel


class AuditModel(BaseModel):
    """AuditModel is an abstract base class that provides automatic timestamping for created and updated records.

    Attributes:
        created_at (datetime): The timestamp when the record was created. This is
            automatically set to the current time when the record is created.
        updated_at (datetime): The timestamp when the record was last updated. This
            is automatically updated to the current time whenever the record is
            updated.
    """

    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} created_at={self.created_at} updated_at={self.updated_at}>"
