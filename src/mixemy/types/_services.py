from typing import TYPE_CHECKING, Any, TypeVar

if TYPE_CHECKING:
    from mixemy.repositories import BaseAsyncRepository, BaseSyncRepository


RepositorySyncT = TypeVar("RepositorySyncT", bound="BaseSyncRepository[Any]")
RepositoryAsyncT = TypeVar("RepositoryAsyncT", bound="BaseAsyncRepository[Any]")
