from abc import ABC
from typing import Literal, overload

from sqlalchemy import delete
from sqlalchemy.orm import Session

from mixemy.repositories._base import IdRepository
from mixemy.repositories.sync._base import BaseSyncRepository
from mixemy.schemas import InputSchema
from mixemy.types import ID, IdModelType


class IdSyncRepository(BaseSyncRepository[IdModelType], IdRepository[IdModelType], ABC):
    def update_by_id(
        self,
        db_session: Session,
        id: ID,
        object_in: InputSchema,
    ) -> IdModelType:
        return self.update(
            db_session=db_session,
            db_object=self.read_by_id(
                db_session=db_session, id=id, raise_on_empty=True
            ),
            object_in=object_in,
        )

    @overload
    def read_by_id(
        self, db_session: Session, id: ID, raise_on_empty: Literal[True]
    ) -> IdModelType: ...

    @overload
    def read_by_id(
        self, db_session: Session, id: ID, raise_on_empty: Literal[False]
    ) -> IdModelType | None: ...

    @overload
    def read_by_id(
        self, db_session: Session, id: ID, raise_on_empty: bool
    ) -> IdModelType | None: ...

    @overload
    def read_by_id(
        self, db_session: Session, id: ID, raise_on_empty: bool = False
    ) -> IdModelType | None: ...

    def read_by_id(
        self, db_session: Session, id: ID, raise_on_empty: bool = False
    ) -> IdModelType | None:
        db_object = db_session.get(self.model, id)

        if db_object is None and raise_on_empty:
            msg = f"Could not find {self.model} of id {id}"
            raise ValueError(msg)

        return db_object

    def delete_by_id(
        self,
        db_session: Session,
        id: ID,
        raise_on_empty: bool,
    ) -> None:
        if raise_on_empty:
            self._delete_refreshing(
                db_session=db_session,
                db_object=self.read_by_id(
                    db_session=db_session,
                    id=id,
                    raise_on_empty=raise_on_empty,
                ),
            )
        else:
            statement = delete(self.model).where(self.model.id == id)
            db_session.execute(statement)
            db_session.commit()
