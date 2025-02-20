"""This module provides pagination-related classes and constants for the Mixemy application.

Classes:
    AuditPaginationFilter: A filter class for auditing pagination.
    PaginationFilter: A base class for pagination filters.
    OrderBy: An enumeration for specifying the field to order by.
    OrderDirection: An enumeration for specifying the direction of ordering.
Constants:
    PaginationFields: A set of fields used for pagination, including 'limit', 'offset', 'order_by', and 'order_direction'.
__all__:
    A list of public objects of this module, as interpreted by 'import *'.
"""

from ._audit import AuditPaginationFilter
from ._base import PaginationFilter
from ._order_enums import OrderBy, OrderDirection

PaginationFields = {"limit", "offset", "order_by", "order_direction"}

__all__ = [
    "AuditPaginationFilter",
    "OrderBy",
    "OrderDirection",
    "PaginationFields",
    "PaginationFilter",
]
