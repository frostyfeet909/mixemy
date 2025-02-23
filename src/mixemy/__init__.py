"""mixemy package.

This package provides a set of base models, repositories, and services for building applications.
It includes both asynchronous and synchronous versions of repositories and services.
Modules:
    models: Contains the base models used in the application.
    repositories: Contains the base repository classes for database operations.
    schemas: Contains the schemas used for data validation and serialization.
    utils: Contains utility functions and classes.
Classes:
    BaseModel: The base model class for all database models.
    IdAuditModel: A base model class that includes ID and audit fields.
    BaseAsyncRepository: The base class for asynchronous repository operations.
    BaseSyncRepository: The base class for synchronous repository operations.
    BaseAsyncService: The base class for asynchronous service operations.
    BaseSyncService: The base class for synchronous service operations.
Attributes:
    __all__: A list of public objects of this package.
    __version__: The version of the mixemy package.
"""

from importlib import metadata

from . import exceptions, models, repositories, schemas, utils
from .models import BaseModel, IdAuditModel
from .repositories import (
    BaseAsyncRepository,
    BaseSyncRepository,
    PermissionAsyncRepository,
    PermissionSyncRepository,
)
from .services import (
    BaseAsyncService,
    BaseSyncService,
    PermissionAsyncService,
    PermissionSyncService,
)

__all__ = [
    "BaseAsyncRepository",
    "BaseAsyncService",
    "BaseModel",
    "BaseSyncRepository",
    "BaseSyncService",
    "IdAuditModel",
    "PermissionAsyncRepository",
    "PermissionAsyncService",
    "PermissionSyncRepository",
    "PermissionSyncService",
    "exceptions",
    "models",
    "repositories",
    "schemas",
    "utils",
]
__version__ = metadata.version("mixemy")
