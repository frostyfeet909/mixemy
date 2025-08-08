"""This module provides utility functions for the mixemy package.

Functions:
    generate_uuid: Generates a unique identifier (UUID).
    to_model: Converts data to a model instance.
    to_schema: Converts data to a schema instance.
    unpack_schema: Unpacks a schema into its components.
    unpack_sequence: Unpacks a value or a sequence into a sequence.
"""

from ._convertors import to_model, to_schema, unpack_schema
from ._utils import pack_sequence
from ._uuids import generate_uuid

__all__ = ["generate_uuid", "pack_sequence", "to_model", "to_schema", "unpack_schema"]
