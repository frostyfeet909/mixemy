from typing import TYPE_CHECKING, TypeVar

# from mixemy.models import AuditModel, BaseModel, IdAuditModel, IdModel

if TYPE_CHECKING:
    from mixemy.models import AuditModel, BaseModel, IdAuditModel, IdModel

BaseModelT = TypeVar("BaseModelT", bound="BaseModel")
IdModelT = TypeVar("IdModelT", bound="IdModel")
AuditModelT = TypeVar("AuditModelT", bound="AuditModel")
IdAuditModelT = TypeVar("IdAuditModelT", bound="IdAuditModel")
