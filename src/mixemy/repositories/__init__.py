"""This package provides base repository classes for both asynchronous and synchronous operations.

Modules:
    _asyncio: Contains the BaseAsyncRepository class for asynchronous database operations.
    _sync: Contains the BaseSyncRepository class for synchronous database operations.
Classes:
    BaseAsyncRepository: A base class for creating asynchronous repositories.
    PermissionAsyncRepository: A base class for creating asynchronous repositories with permission
    BaseSyncRepository: A base class for creating synchronous repositories.
    PermissionSyncRepository: A base class for creating synchronous repositories with permission
"""

from ._asyncio import BaseAsyncRepository, PermissionAsyncRepository
from ._sync import BaseSyncRepository, PermissionSyncRepository

__all__ = [
    "BaseAsyncRepository",
    "BaseSyncRepository",
    "PermissionAsyncRepository",
    "PermissionSyncRepository",
]
