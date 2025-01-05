from enum import StrEnum


class OrderBy(StrEnum):
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"


class OrderDirection(StrEnum):
    ASC = "asc"
    DESC = "desc"
