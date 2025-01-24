from abc import ABC
from collections.abc import Sequence
from typing import Any

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from mixemy.repositories._base import BaseRepository
from mixemy.schemas import InputSchema
from mixemy.types import (
    BaseModelType,
)


class BaseSyncRepository(BaseRepository[BaseModelType], ABC):
    def create(self, db_session: Session, db_object: BaseModelType) -> BaseModelType:
        return self._add_refreshing(db_session=db_session, db_object=db_object)

    def read_multi(
        self,
        db_session: Session,
        filters: InputSchema | None = None,
    ) -> Sequence[BaseModelType]:
        return self._execute_returning_all(
            db_session=db_session,
            statement=self._add_filters(statement=None, filters=filters),
        )

    def update(
        self,
        db_session: Session,
        db_object: BaseModelType,
        object_in: InputSchema,
    ) -> BaseModelType:
        self._update_db_object(db_object=db_object, object_in=object_in)
        return self._add_refreshing(db_session=db_session, db_object=db_object)

    def delete(self, db_session: Session, db_object: BaseModelType) -> None:
        self._delete_refreshing(db_session=db_session, db_object=db_object)

    def count(
        self,
        db_session: Session,
        before_filter: InputSchema | None = None,
    ) -> int:
        return self._execute_returning_one(
            db_session=db_session,
            statement=self._add_before_filter(
                statement=select(func.count()).select_from(self.model),
                filters=before_filter,
            ),
        )

    @staticmethod
    def _execute_returning_all(
        db_session: Session, statement: Select[Any]
    ) -> Sequence[BaseModelType]:
        return db_session.execute(statement=statement).scalars().all()

    @staticmethod
    def _execute_returning_one(db_session: Session, statement: Select[Any]) -> Any:
        return db_session.execute(statement=statement).scalar_one()

    @staticmethod
    def _add_refreshing(db_session: Session, db_object: BaseModelType) -> BaseModelType:
        db_session.add(db_object)
        db_session.commit()
        db_session.refresh(db_object)

        return db_object

    @staticmethod
    def _delete_refreshing(db_session: Session, db_object: BaseModelType) -> None:
        db_session.delete(db_object)
        db_session.commit()
        db_session.refresh(db_object)
