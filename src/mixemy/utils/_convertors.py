from typing import Any

from mixemy.models import BaseModel
from mixemy.schemas import BaseSchema
from mixemy.types import BaseModelT, BaseSchemaT


def unpack_schema(
    schema: BaseSchema,
    *,
    exclude_unset: bool = True,
    exclude: set[str] | None = None,
    by_alias: bool = True,
) -> dict[str, Any]:
    return schema.model_dump(
        exclude_unset=exclude_unset, exclude=exclude, by_alias=by_alias
    )


def to_model(model: type[BaseModelT], schema: BaseSchema) -> BaseModelT:
    return model(**unpack_schema(schema=schema))


def to_schema(model: BaseModel, schema: type[BaseSchemaT]) -> BaseSchemaT:
    return schema.model_validate(model)
