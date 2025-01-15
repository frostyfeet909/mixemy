from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from mixemy.models._base import BaseModel
from mixemy.types import ID


class IdModel(BaseModel):
    __abstract__ = True

    id: Mapped[ID] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}>"
