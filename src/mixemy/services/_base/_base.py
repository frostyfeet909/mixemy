from abc import ABC
from typing import Generic

from mixemy._exceptions import MixemyServiceSetupError
from mixemy.types import (
    BaseModelType,
    CreateSchemaType,
    FilterSchemaType,
    OutputSchemaType,
    UpdateSchemaType,
)
from mixemy.utils import to_model, to_schema


class BaseService(
    Generic[
        BaseModelType,
        CreateSchemaType,
        UpdateSchemaType,
        FilterSchemaType,
        OutputSchemaType,
    ],
    ABC,
):
    output_schema_type: type[OutputSchemaType]
    model: type[BaseModelType]

    def __init__(self) -> None:
        self._verify_init()
        self.output_schema = self.output_schema_type

    def _to_model(self, schema: CreateSchemaType | UpdateSchemaType) -> BaseModelType:
        return to_model(schema=schema, model=self.model)

    def _to_schema(self, model: BaseModelType) -> OutputSchemaType:
        return to_schema(model=model, schema=self.output_schema)

    def _verify_init(self) -> None:
        for field in ["output_schema_type", "repository_type"]:
            if not hasattr(self, field):
                raise MixemyServiceSetupError(service=self, undefined_field=field)
