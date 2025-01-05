from datetime import datetime

from mixemy.schemas._output import OutputSchema


class AuditOutputSchema(OutputSchema):
    created_at: datetime
    updated_at: datetime | None
