from typing import TYPE_CHECKING, TypeVar

# from mixemy.schemas import InputSchema
# from mixemy.schemas.paginations import AuditPaginationFilter, PaginationFilter

if TYPE_CHECKING:
    from mixemy.schemas import InputSchema, OutputSchema
    from mixemy.schemas.paginations import AuditPaginationFilter, PaginationFilter

CreateSchemaType = TypeVar("CreateSchemaType", bound="InputSchema")
UpdateSchemaType = TypeVar("UpdateSchemaType", bound="InputSchema")
OutputSchemaType = TypeVar("OutputSchemaType", bound="OutputSchema")

FilterSchemaType = TypeVar("FilterSchemaType", bound="InputSchema")

# PaginationSchemaType = TypeVar("PaginationSchemaType", bound=PaginationFilter)
# type FilterSchemaType = "InputSchema"
type PaginationSchemaType = "PaginationFilter"
type AuditPaginationSchemaType = "AuditPaginationFilter"
