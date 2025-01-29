from abc import ABC
from collections.abc import Sequence
from typing import Any

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session
from sqlalchemy.orm.strategy_options import (
    _AbstractLoad,  # pyright: ignore[reportPrivateUsage]
)
from sqlalchemy.util import EMPTY_DICT

from mixemy.repositories._base import BaseRepository
from mixemy.schemas import InputSchema
from mixemy.types import BaseModelType, ResultT, SelectT


class BaseSyncRepository(BaseRepository[BaseModelType], ABC):
    def create(
        self,
        db_session: Session,
        db_object: BaseModelType,
        *,
        auto_commit: bool | None = None,
        auto_expunge: bool | None = None,
        auto_refresh: bool | None = None,
    ) -> BaseModelType:
        return self._add(
            db_session=db_session,
            db_object=db_object,
            auto_commit=auto_commit,
            auto_expunge=auto_expunge,
            auto_refresh=auto_refresh,
        )

    def read(
        self,
        db_session: Session,
        id: Any,
        *,
        loader_options: tuple[_AbstractLoad] | None = None,
        execution_options: dict[str, Any] | None = None,
        auto_expunge: bool | None = None,
        auto_commit: bool | None = False,
    ) -> BaseModelType | None:
        return self._get(
            db_session=db_session,
            id=id,
            loader_options=loader_options,
            execution_options=execution_options,
            auto_expunge=auto_expunge,
            auto_commit=auto_commit,
        )

    def read_multiple(
        self,
        db_session: Session,
        filters: InputSchema | None = None,
        *,
        loader_options: tuple[_AbstractLoad] | None = None,
        execution_options: dict[str, Any] | None = None,
        auto_commit: bool | None = False,
        auto_expunge: bool | None = None,
    ) -> Sequence[BaseModelType]:
        statement = select(self.model)
        statement = self._add_filters(statement=statement, filters=filters)
        statement = self._add_pagination(statement=statement, filters=filters)
        return self._execute_returning_all(
            db_session=db_session,
            statement=statement,
            loader_options=loader_options,
            execution_options=execution_options,
            auto_commit=auto_commit,
            auto_expunge=auto_expunge,
            auto_refresh=False,
        )

    def update(
        self,
        db_session: Session,
        id: Any,
        object_in: InputSchema,
        *,
        loader_options: tuple[_AbstractLoad] | None = None,
        execution_options: dict[str, Any] | None = None,
        auto_commit: bool | None = None,
        auto_expunge: bool | None = None,
        auto_refresh: bool | None = None,
    ) -> BaseModelType | None:
        db_object = self._get(
            db_session=db_session,
            id=id,
            loader_options=loader_options,
            execution_options=execution_options,
            auto_expunge=auto_expunge,
        )
        if db_object is not None:
            return self.update_db_object(
                db_session=db_session,
                db_object=db_object,
                object_in=object_in,
                auto_commit=auto_commit,
                auto_expunge=auto_expunge,
                auto_refresh=auto_refresh,
            )

        return db_object

    def update_db_object(
        self,
        db_session: Session,
        db_object: BaseModelType,
        object_in: InputSchema,
        *,
        auto_commit: bool | None = None,
        auto_expunge: bool | None = None,
        auto_refresh: bool | None = None,
    ) -> BaseModelType | None:
        self._update_db_object(db_object=db_object, object_in=object_in)
        return self._add(
            db_session=db_session,
            db_object=db_object,
            auto_commit=auto_commit,
            auto_expunge=auto_expunge,
            auto_refresh=auto_refresh,
        )

    def delete(
        self,
        db_session: Session,
        id: Any,
        *,
        loader_options: tuple[_AbstractLoad] | None = None,
        execution_options: dict[str, Any] | None = None,
        auto_commit: bool | None = None,
        auto_expunge: bool | None = None,
    ) -> None:
        db_object = self._get(
            db_session=db_session,
            id=id,
            loader_options=loader_options,
            execution_options=execution_options,
            auto_expunge=auto_expunge,
        )
        if db_object is not None:
            self.delete_db_object(
                db_session=db_session,
                db_object=db_object,
                auto_commit=auto_commit,
                auto_expunge=auto_expunge,
            )

    def delete_db_object(
        self,
        db_session: Session,
        db_object: BaseModelType,
        *,
        auto_commit: bool | None = None,
        auto_expunge: bool | None = None,
    ) -> None:
        self._delete(
            db_session=db_session,
            db_object=db_object,
            auto_commit=auto_commit,
            auto_expunge=auto_expunge,
        )

    def count(
        self,
        db_session: Session,
        filters: InputSchema | None = None,
        *,
        loader_options: tuple[_AbstractLoad] | None = None,
        execution_options: dict[str, Any] | None = None,
        auto_commit: bool | None = False,
    ) -> int:
        statement = select(func.count()).select_from(self.model)
        statement = self._add_filters(statement=statement, filters=filters)
        return self._execute_returning_one(
            db_session=db_session,
            statement=statement,
            loader_options=loader_options,
            execution_options=execution_options,
            auto_commit=auto_commit,
            auto_expunge=False,
            auto_refresh=False,
        )

    def _maybe_commit_or_flush_or_refresh_or_expunge(
        self,
        db_session: Session,
        db_object: ResultT | Sequence[ResultT] | None,
        *,
        auto_commit: bool | None,
        auto_expunge: bool | None,
        auto_refresh: bool | None,
    ) -> None:
        if auto_commit is True or (auto_commit is None and self.auto_commit):
            db_session.commit()
        else:
            db_session.flush()

        if db_object is not None:
            instances: Sequence[ResultT] = (
                db_object if isinstance(db_object, Sequence) else [db_object]
            )
            if auto_refresh is True or (auto_refresh is None and self.auto_refresh):
                for instance in instances:
                    db_session.refresh(instance)
            if auto_expunge is True or (auto_expunge is None and self.auto_expunge):
                for instance in instances:
                    db_session.expunge(instance)

    def _add(
        self,
        db_session: Session,
        db_object: BaseModelType,
        *,
        auto_commit: bool | None,
        auto_expunge: bool | None,
        auto_refresh: bool | None,
    ) -> BaseModelType:
        db_session.add(db_object)
        self._maybe_commit_or_flush_or_refresh_or_expunge(
            db_session=db_session,
            db_object=db_object,
            auto_commit=auto_commit,
            auto_expunge=auto_expunge,
            auto_refresh=auto_refresh,
        )

        return db_object

    def _delete(
        self,
        db_session: Session,
        db_object: BaseModelType,
        *,
        auto_commit: bool | None,
        auto_expunge: bool | None,
    ) -> None:
        db_session.delete(db_object)
        self._maybe_commit_or_flush_or_refresh_or_expunge(
            db_session=db_session,
            db_object=db_object,
            auto_commit=auto_commit,
            auto_expunge=auto_expunge,
            auto_refresh=False,
        )

    def _get(
        self,
        db_session: Session,
        id: Any,
        *,
        loader_options: tuple[_AbstractLoad] | None,
        execution_options: dict[str, Any] | None,
        auto_expunge: bool | None,
        auto_commit: bool | None = False,
    ) -> BaseModelType | None:
        current_loader_options = (
            loader_options if loader_options is not None else self.loader_options
        )
        current_execution_options = (
            execution_options
            if execution_options is not None
            else self.execution_options
        )
        db_object = db_session.get(
            self.model,
            id,
            options=current_loader_options,
            execution_options=current_execution_options or EMPTY_DICT,
        )
        self._maybe_commit_or_flush_or_refresh_or_expunge(
            db_session=db_session,
            db_object=db_object,
            auto_commit=auto_commit,
            auto_expunge=auto_expunge,
            auto_refresh=False,
        )

        return db_object

    def _execute_returning_all(
        self,
        db_session: Session,
        statement: Select[SelectT],
        *,
        loader_options: tuple[_AbstractLoad] | None,
        execution_options: dict[str, Any] | None,
        auto_commit: bool | None,
        auto_expunge: bool | None,
        auto_refresh: bool | None,
    ) -> Sequence[Any]:
        statement = self._prepare_statement(
            statement=statement,
            loader_options=loader_options,
            execution_options=execution_options,
        )
        res = db_session.execute(statement)
        db_objects: Sequence[Any] = res.scalars().all()
        self._maybe_commit_or_flush_or_refresh_or_expunge(
            db_session=db_session,
            db_object=db_objects,
            auto_commit=auto_commit,
            auto_expunge=auto_expunge,
            auto_refresh=auto_refresh,
        )
        return db_objects

    def _execute_returning_one(
        self,
        db_session: Session,
        statement: Select[SelectT],
        *,
        loader_options: tuple[_AbstractLoad] | None,
        execution_options: dict[str, Any] | None,
        auto_commit: bool | None,
        auto_expunge: bool | None,
        auto_refresh: bool | None,
    ) -> Any:
        statement = self._prepare_statement(
            statement=statement,
            loader_options=loader_options,
            execution_options=execution_options,
        )
        res = db_session.execute(statement)
        db_object = res.scalar_one()
        self._maybe_commit_or_flush_or_refresh_or_expunge(
            db_session=db_session,
            db_object=db_object,
            auto_commit=auto_commit,
            auto_expunge=auto_expunge,
            auto_refresh=auto_refresh,
        )
        return db_object
