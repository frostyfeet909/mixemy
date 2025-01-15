from typing import TYPE_CHECKING, TypeVar

# from mixemy.models import AuditModel, BaseModel, IdAuditModel, IdModel

if TYPE_CHECKING:
    from mixemy.models import AuditModel, BaseModel, IdAuditModel, IdModel

BaseModelType = TypeVar("BaseModelType", bound="BaseModel")
IdModelType = TypeVar("IdModelType", bound="IdModel")
AuditModelType = TypeVar("AuditModelType", bound="AuditModel")
IdAuditModelType = TypeVar("IdAuditModelType", bound="IdAuditModel")
