from typing import TypeVar

from mixemy.crud._audit import AuditCRUD
from mixemy.crud._id import IdCRUD
from mixemy.models import IdAuditModel
from mixemy.schemas import BaseSchema

ModelType = TypeVar("ModelType", bound=IdAuditModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseSchema)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseSchema)


class IdAuditCRUD(
    IdCRUD[ModelType, CreateSchemaType, UpdateSchemaType],
    AuditCRUD[ModelType, CreateSchemaType, UpdateSchemaType],
):
    def __init__(self, model: type[ModelType]) -> None:
        self.model = model
