from mixemy.schemas._audit_output import AuditOutputSchema
from mixemy.schemas._id_output import IdOutputSchema


class IdAuditOutputSchema(IdOutputSchema, AuditOutputSchema):
    pass
