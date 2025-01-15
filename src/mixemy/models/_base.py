from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase


class BaseModel(DeclarativeBase):
    __abstract__ = True

    @declared_attr  # pyright: ignore[reportArgumentType]
    @classmethod
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.__dict__}>"
