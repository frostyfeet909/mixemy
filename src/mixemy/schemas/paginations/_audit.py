from mixemy.schemas.paginations._base import PaginationFilter
from mixemy.schemas.paginations._order_enums import OrderBy, OrderDirection


class AuditPaginationFilter(PaginationFilter):
    order_by: OrderBy = OrderBy.CREATED_AT
    order_direction: OrderDirection = OrderDirection.DESC
