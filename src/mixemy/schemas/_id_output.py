from uuid_utils.compat import UUID

from mixemy.schemas._output import OutputSchema


class IdOutputSchema(OutputSchema):
    id: UUID
