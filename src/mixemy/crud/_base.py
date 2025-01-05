from collections.abc import Sequence
from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from mixemy.models import BaseModel
from mixemy.schemas import BaseSchema
from mixemy.schemas.filters import Filter

ModelType = TypeVar("ModelType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseSchema)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseSchema)


class BaseCRUD(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: type[ModelType]) -> None:
        self.model = model

    def read_multi(
        self, db_session: Session, *, filter: Filter | None = None
    ) -> Sequence[ModelType]:
        if filter is None:
            statement = select(self.model)
        else:
            statement = select(self.model).offset(filter.offset).limit(filter.limit)

        return db_session.execute(statement=statement).scalars().all()

    def create(self, db_session: Session, *, object_in: CreateSchemaType) -> ModelType:
        db_object = self.model(**object_in.model_dump(mode="json"))

        db_session.add(db_object)
        db_session.commit()

        db_session.refresh(db_object)
        return db_object

    def update(
        self,
        db_session: Session,
        *,
        db_object: ModelType,
        object_in: UpdateSchemaType,
    ) -> ModelType:
        update_data = object_in.model_dump(exclude_unset=True, mode="json")
        for field, value in update_data.items():
            setattr(db_object, field, value)

        db_session.add(db_object)
        db_session.commit()
        db_session.refresh(db_object)

        return db_object
