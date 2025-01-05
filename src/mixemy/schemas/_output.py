from pydantic import ConfigDict

from mixemy.schemas._base import BaseSchema


class OutputSchema(BaseSchema):
    model_config = ConfigDict(from_attributes=True)
