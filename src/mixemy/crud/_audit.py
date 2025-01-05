from collections.abc import Sequence
from typing import TypeVar, override

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from mixemy.crud._base import BaseCRUD
from mixemy.models import AuditModel
from mixemy.schemas import BaseSchema
from mixemy.schemas.filters import AuditFilter

ModelType = TypeVar("ModelType", bound=AuditModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseSchema)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseSchema)


class AuditCRUD(BaseCRUD[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: type[ModelType]) -> None:
        self.model = model

    @override
    def read_multi(  # pyright: ignore[reportIncompatibleMethodOverride]
        self, db_session: Session, *, filter: AuditFilter | None = None
    ) -> Sequence[ModelType]:
        if filter is None:
            statement = select(self.model)
        else:
            statement = (
                select(self.model)
                .offset(filter.offset)
                .limit(filter.limit)
                .order_by(text(f"{filter.order_by} {filter.order_direction}"))
            )

        return db_session.execute(statement=statement).scalars().all()
