"""This package initializes and exports various schema modules used in the application.

Modules:
    paginations: Handles pagination schemas.
    serializers: Handles serialization schemas.
    AuditOutputSchema: Schema for audit output.
    BaseSchema: Base schema class.
    IdAuditOutputSchema: Schema for ID audit output.
    IdOutputSchema: Schema for ID output.
    InputSchema: Schema for input data.
    OutputSchema: Schema for output data.
Exports:
    AuditOutputSchema
    BaseSchema
    IdAuditOutputSchema
    IdOutputSchema
    InputSchema
    OutputSchema
    paginations
    serializers
"""

from . import paginations
from ._audit_output import AuditOutputSchema
from ._base import BaseSchema
from ._id_audit_output import IdAuditOutputSchema
from ._id_output import IdOutputSchema
from ._input import InputSchema
from ._output import OutputSchema

__all__ = [
    "AuditOutputSchema",
    "BaseSchema",
    "IdAuditOutputSchema",
    "IdOutputSchema",
    "InputSchema",
    "OutputSchema",
    "paginations",
]
