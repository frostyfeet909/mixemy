from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from mixemy.schemas import BaseSchema, InputSchema, OutputSchema

BaseSchemaT = TypeVar("BaseSchemaT", bound="BaseSchema")
CreateSchemaT = TypeVar("CreateSchemaT", bound="InputSchema")
UpdateSchemaT = TypeVar("UpdateSchemaT", bound="InputSchema")
OutputSchemaT = TypeVar("OutputSchemaT", bound="OutputSchema")

FilterSchemaT = TypeVar("FilterSchemaT", bound="InputSchema")
