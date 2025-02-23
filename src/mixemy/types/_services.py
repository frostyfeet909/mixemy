from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from typing import Any

    from mixemy.repositories import BaseAsyncRepository, BaseSyncRepository

RepositorySyncT = TypeVar("RepositorySyncT", bound="BaseSyncRepository[Any]")
RepositoryAsyncT = TypeVar("RepositoryAsyncT", bound="BaseAsyncRepository[Any]")
