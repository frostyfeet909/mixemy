"""This package provides base repository classes for both asynchronous and synchronous operations.

Modules:
    _asyncio: Contains the BaseAsyncRepository class for asynchronous database operations.
    _sync: Contains the BaseSyncRepository class for synchronous database operations.
Classes:
    BaseAsyncRepository: A base class for creating asynchronous repositories.
    BaseSyncRepository: A base class for creating synchronous repositories.
"""

from ._asyncio import BaseAsyncRepository
from ._sync import BaseSyncRepository

__all__ = [
    "BaseAsyncRepository",
    "BaseSyncRepository",
]
