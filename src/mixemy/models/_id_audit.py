from mixemy.models._audit import AuditModel
from mixemy.models._id import IdModel


class IdAuditModel(IdModel, AuditModel):
    __abstract__ = True
