from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from mixemy.models._base import BaseModel


class IdModel(BaseModel):
    __abstract__ = True

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
