from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase


class BaseModel(DeclarativeBase):
    """
    BaseModel is an abstract base class for SQLAlchemy declarative models.

    Methods:
        __tablename__(cls) -> str:
            Generates a table name for the model by converting the class name from CamelCase to snake_case.
            Removes the suffix "_model" from the generated table name.
        __repr__(self) -> str:
            Returns a string representation of the model instance, including the class name and its attributes.
    """

    __abstract__ = True

    @declared_attr  # pyright: ignore[reportArgumentType]
    @classmethod
    def __tablename__(cls) -> str:
        return "".join(
            (letter if letter.islower() else "_" + letter.lower())
            for letter in (cls.__name__[0].lower() + cls.__name__[1:])
        ).removesuffix("_model")

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.__dict__}>"
