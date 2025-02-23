from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from typing import Any

    from mixemy.repositories import (
        BaseAsyncRepository,
        BaseSyncRepository,
        PermissionAsyncRepository,
        PermissionSyncRepository,
    )

RepositorySyncT = TypeVar("RepositorySyncT", bound="BaseSyncRepository[Any]")
RepositoryAsyncT = TypeVar("RepositoryAsyncT", bound="BaseAsyncRepository[Any]")
PermissionSyncRepositoryT = TypeVar(
    "PermissionSyncRepositoryT", bound="PermissionSyncRepository[Any]"
)
PermissionAsyncRepositoryT = TypeVar(
    "PermissionAsyncRepositoryT", bound="PermissionAsyncRepository[Any]"
)
