from mixemy.models._audit import AuditModel
from mixemy.models._id import IdModel


class IdAuditModel(IdModel, AuditModel):
    __abstract__ = True

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id} created_at={self.created_at} updated_at={self.updated_at}>"
