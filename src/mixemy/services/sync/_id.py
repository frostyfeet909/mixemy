from abc import ABC

from mixemy.repositories.sync import IdSyncRepository
from mixemy.services.sync._base import BaseSyncService
from mixemy.types import (
    ID,
    CreateSchemaType,
    FilterSchemaType,
    IdModelType,
    OutputSchemaType,
    UpdateSchemaType,
)


class IdSyncService(
    BaseSyncService[
        IdModelType,
        CreateSchemaType,
        UpdateSchemaType,
        FilterSchemaType,
        OutputSchemaType,
    ],
    ABC,
):
    repository_type: type[IdSyncRepository[IdModelType]]  # pyright: ignore[reportIncompatibleVariableOverride] - https://github.com/python/typing/issues/548
    repository: IdSyncRepository[IdModelType]

    def read(self, id: ID) -> OutputSchemaType | None:
        return (
            self._to_schema(model=model)
            if (
                model := self.repository.read_by_id(
                    db_session=self.db_session, id=id, raise_on_empty=False
                )
            )
            else None
        )

    def update(self, id: ID, object_in: UpdateSchemaType) -> OutputSchemaType:
        return self._to_schema(
            model=self.repository.update_by_id(
                db_session=self.db_session,
                id=id,
                object_in=object_in,
            )
        )

    def delete(self, id: ID) -> None:
        self.repository.delete_by_id(
            db_session=self.db_session, id=id, raise_on_empty=False
        )
