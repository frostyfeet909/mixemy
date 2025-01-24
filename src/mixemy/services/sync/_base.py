from abc import ABC

from sqlalchemy.orm import Session

from mixemy.repositories.sync import BaseSyncRepository
from mixemy.services._base import BaseService
from mixemy.types import (
    BaseModelType,
    CreateSchemaType,
    FilterSchemaType,
    OutputSchemaType,
    UpdateSchemaType,
)


class BaseSyncService(
    BaseService[
        BaseModelType,
        CreateSchemaType,
        UpdateSchemaType,
        FilterSchemaType,
        OutputSchemaType,
    ],
    ABC,
):
    repository_type: type[BaseSyncRepository[BaseModelType]]

    def __init__(self, db_session: Session) -> None:
        super().__init__()
        self.repository = self.repository_type()
        self.model = self.repository.model
        self.db_session = db_session

    def create(self, object_in: CreateSchemaType) -> OutputSchemaType:
        return self._to_schema(
            model=self.repository.create(
                db_session=self.db_session, db_object=self._to_model(schema=object_in)
            )
        )

    def read_multi(
        self,
        filters: FilterSchemaType | None = None,
    ) -> list[OutputSchemaType]:
        return [
            self._to_schema(model=model)
            for model in self.repository.read_multi(
                db_session=self.db_session,
                filters=filters,
            )
        ]
