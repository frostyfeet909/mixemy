from typing import Any, TypeVar

from mixemy.models import BaseModel
from mixemy.schemas import BaseSchema

TO_MODEL = TypeVar("TO_MODEL", bound=BaseModel)
TO_SCHEMA = TypeVar("TO_SCHEMA", bound=BaseSchema)


def unpack_schema(
    schema: BaseSchema,
    exclude_unset: bool = True,
    exclude: set[str] | None = None,
) -> dict[str, Any]:
    return schema.model_dump(exclude_unset=exclude_unset, exclude=exclude)


def to_model(model: type[TO_MODEL], schema: BaseSchema) -> TO_MODEL:
    return model(**unpack_schema(schema=schema))


def to_schema(model: BaseModel, schema: type[TO_SCHEMA]) -> TO_SCHEMA:
    return schema.model_validate(model)
