from enum import Enum, auto
from typing import Literal, TypeVar, overload

from sqlalchemy import delete
from sqlalchemy.orm import Session

from mixemy.crud._base import BaseCRUD
from mixemy.models import IdModel
from mixemy.schemas import BaseSchema

ModelType = TypeVar("ModelType", bound=IdModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseSchema)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseSchema)


class ReturnOrRaise(Enum):
    DONT_RETURN_OR_RAISE = auto()
    ONLY_RETURN = auto()
    RETURN_AND_RAISE = auto()


class IdCRUD(BaseCRUD[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: type[ModelType]) -> None:
        self.model = model

    @overload
    def read_by_id(
        self, db_session: Session, id: int, raise_on_empty: Literal[True]
    ) -> ModelType: ...

    @overload
    def read_by_id(
        self, db_session: Session, id: int, raise_on_empty: Literal[False]
    ) -> ModelType | None: ...

    @overload
    def read_by_id(
        self, db_session: Session, id: int, raise_on_empty: bool
    ) -> ModelType | None: ...

    def read_by_id(
        self, db_session: Session, id: int, raise_on_empty: bool = False
    ) -> ModelType | None:
        db_object = db_session.get(self.model, id)

        if db_object is None and raise_on_empty:
            msg = f"Could not find {self.model} of id {id}"
            raise ValueError(msg)

        return db_object

    def update_by_id(
        self,
        db_session: Session,
        *,
        id: int,
        object_in: UpdateSchemaType,
    ) -> ModelType:
        db_object = self.read_by_id(db_session=db_session, id=id, raise_on_empty=True)
        update_data = object_in.model_dump(exclude_unset=True, mode="json")

        for field, value in update_data.items():
            setattr(db_object, field, value)

        db_session.add(db_object)
        db_session.commit()
        db_session.refresh(db_object)

        return db_object

    @overload
    def delete_by_id(
        self,
        db_session: Session,
        *,
        id: int,
        return_or_raise: Literal[ReturnOrRaise.DONT_RETURN_OR_RAISE],
    ) -> None: ...

    @overload
    def delete_by_id(
        self,
        db_session: Session,
        *,
        id: int,
        return_or_raise: Literal[ReturnOrRaise.ONLY_RETURN],
    ) -> ModelType | None: ...

    @overload
    def delete_by_id(
        self,
        db_session: Session,
        *,
        id: int,
        return_or_raise: Literal[ReturnOrRaise.RETURN_AND_RAISE],
    ) -> ModelType: ...

    @overload
    def delete_by_id(
        self,
        db_session: Session,
        *,
        id: int,
        return_or_raise: ReturnOrRaise,
    ) -> ModelType | None: ...

    def delete_by_id(
        self,
        db_session: Session,
        *,
        id: int,
        return_or_raise: ReturnOrRaise = ReturnOrRaise.DONT_RETURN_OR_RAISE,
    ) -> ModelType | None:
        obj = None

        if return_or_raise in {
            ReturnOrRaise.RETURN_AND_RAISE,
            ReturnOrRaise.ONLY_RETURN,
        }:
            if (
                obj := self.read_by_id(
                    db_session=db_session,
                    id=id,
                    raise_on_empty=(return_or_raise == ReturnOrRaise.RETURN_AND_RAISE),
                )
            ) is not None:
                db_session.delete(obj)
        else:
            statemenet = delete(self.model).where(self.model.id == id)
            db_session.execute(statemenet)

        db_session.commit()

        return obj
