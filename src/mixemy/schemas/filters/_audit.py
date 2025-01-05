from mixemy.schemas.filters._base import Filter
from mixemy.schemas.filters._order_enums import OrderBy, OrderDirection


class AuditFilter(Filter):
    order_by: OrderBy = OrderBy.CREATED_AT
    order_direction: OrderDirection = OrderDirection.DESC
