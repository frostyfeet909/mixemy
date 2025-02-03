from typing import TYPE_CHECKING, TypeVar

# from mixemy.schemas import InputSchema
# from mixemy.schemas.paginations import AuditPaginationFilter, PaginationFilter

if TYPE_CHECKING:
    from mixemy.schemas import BaseSchema, InputSchema, OutputSchema
    from mixemy.schemas.paginations import AuditPaginationFilter, PaginationFilter

BaseSchemaT = TypeVar("BaseSchemaT", bound="BaseSchema")
CreateSchemaT = TypeVar("CreateSchemaT", bound="InputSchema")
UpdateSchemaT = TypeVar("UpdateSchemaT", bound="InputSchema")
OutputSchemaT = TypeVar("OutputSchemaT", bound="OutputSchema")

FilterSchemaT = TypeVar("FilterSchemaT", bound="InputSchema")

# PaginationSchemaT = TypeVar("PaginationSchemaT", bound=PaginationFilter)
# type FilterSchemaT = "InputSchema"
type PaginationSchemaT = "PaginationFilter"
type AuditPaginationSchemaT = "AuditPaginationFilter"
