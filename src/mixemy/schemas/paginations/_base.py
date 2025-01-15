from pydantic import Field

from mixemy.schemas._base import BaseSchema


class PaginationFilter(BaseSchema):
    limit: int = Field(100, gt=0, le=500)
    offset: int = Field(0, ge=0)
