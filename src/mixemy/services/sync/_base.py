from abc import ABC

from sqlalchemy.orm import Session

from mixemy.repositories.sync import BaseSyncRepository
from mixemy.services._base import BaseService
from mixemy.types import (
    BaseModelType,
    CreateSchemaType,
    FilterSchemaType,
    OutputSchemaType,
    PaginationSchemaType,
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

    def __init__(self) -> None:
        super().__init__()
        self.repository = self.repository_type()
        self.model = self.repository.model

    def create(self, db_session: Session, object_in: CreateSchemaType) -> BaseModelType:
        return self.repository.create(
            db_session=db_session, db_object=self._to_model(schema=object_in)
        )

    def read_multi(
        self,
        db_session: Session,
        filters: FilterSchemaType | None = None,
        pagination: PaginationSchemaType | None = None,
    ) -> list[OutputSchemaType]:
        return [
            self._to_schema(model=model)
            for model in self.repository.read_multi(
                db_session=db_session, before_filter=filters, after_filter=pagination
            )
        ]
