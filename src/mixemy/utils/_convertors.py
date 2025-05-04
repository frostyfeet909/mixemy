from typing import Any

from pydantic import ValidationError
from sqlalchemy.exc import ArgumentError
from sqlalchemy.inspection import inspect

from mixemy.exceptions import MixemyConversionError
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


def to_model(
    model: type[BaseModelT],
    schema: BaseSchema,
    *,
    recursive_conversion: bool = False,
    exclude_unset: bool = True,
    exclude: set[str] | None = None,
    by_alias: bool = True,
) -> BaseModelT:
    sub_models: dict[str, list[BaseModel] | BaseModel] = {}
    if recursive_conversion:
        if exclude is None:
            exclude = set()
        relationships = inspect(model).relationships
        for relationship in relationships:
            if hasattr(schema, relationship.key):
                sub_models[relationship.key] = (
                    [
                        to_model(
                            model=relationship.mapper.class_,
                            schema=item,
                            recursive_conversion=recursive_conversion,
                            exclude_unset=exclude_unset,
                            exclude=exclude,
                            by_alias=by_alias,
                        )
                        for item in getattr(schema, relationship.key)
                    ]
                    if relationship.uselist
                    else to_model(
                        model=relationship.mapper.class_,
                        schema=getattr(schema, relationship.key),
                        recursive_conversion=recursive_conversion,
                        exclude_unset=exclude_unset,
                        exclude=exclude,
                        by_alias=by_alias,
                    )
                )

                exclude.add(relationship.key)

    unpacked_schema = unpack_schema(
        schema=schema,
        exclude_unset=exclude_unset,
        exclude=exclude,
        by_alias=by_alias,
    )

    try:
        return model(**unpacked_schema, **sub_models)
    except AttributeError as ex:
        message = (
            f"Error converting {type(schema)} to {model}.\nThis is likely as there is a nested model in {type(schema)} and `recursive_conversion` is false"
            if not recursive_conversion
            else None
        )
        raise MixemyConversionError(
            model=model, schema=type(schema), is_model_to_schema=False, message=message
        ) from ex
    except ArgumentError as ex:
        raise MixemyConversionError(
            model=model, schema=type(schema), is_model_to_schema=False
        ) from ex


def to_schema(model: BaseModel, schema: type[BaseSchemaT]) -> BaseSchemaT:
    try:
        return schema.model_validate(model)
    except ValidationError as ex:
        raise MixemyConversionError(
            model=model, schema=schema, is_model_to_schema=True
        ) from ex
