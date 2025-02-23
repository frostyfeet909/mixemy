from mixemy.models._audit import AuditModel
from mixemy.models._id import IdModel


class IdAuditModel(IdModel, AuditModel):
    """IdAuditModel is an abstract base class that combines the functionality of IdModel and AuditModel.

    Attributes:
        id (int): The unique identifier for the model instance.
        created_at (datetime): The timestamp when the model instance was created.
        updated_at (datetime): The timestamp when the model instance was last updated.
    """

    __abstract__ = True

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id} created_at={self.created_at} updated_at={self.updated_at}>"
