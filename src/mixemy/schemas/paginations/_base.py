from pydantic import Field

from mixemy.schemas._input import InputSchema


class PaginationFilter(InputSchema):
    limit: int = Field(100, gt=0, le=500)
    offset: int = Field(0, ge=0)
