"""This module defines custom exception classes for the Mixemy application.

Classes:
    MixemyError: Base class for all custom exceptions in Mixemy.
    MixemyConversionError: Raised for errors in the conversion between a model and a schema.
    MixemyRepositoryError: Raised for errors that occur within a Mixemy repository.
    MixemyServiceError: Raised for errors that occur within a Mixemy service.
    MixemySetupError: Raised for errors in the setup of a Mixemy component.
    MixemyRepositorySetupError: Raised for errors in the setup of a Mixemy repository.
    MixemyServiceSetupError: Raised for errors in the setup of a Mixemy service.

"""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from mixemy.models import BaseModel
    from mixemy.repositories import BaseAsyncRepository, BaseSyncRepository
    from mixemy.schemas import BaseSchema
    from mixemy.services import BaseAsyncService, BaseSyncService


class MixemyError(Exception):
    """Custom exception class for Mixemy application.

    Attributes:
        message (str): The error message describing the exception.

    Args:
        message (str): The error message to be displayed.
    """

    def __init__(self, message: str) -> None:
        """Initialize the exception with a given message.

        Args:
            message (str): The error message to be associated with this exception.
        """
        self.message = message
        Exception.__init__(self, message)


class MixemyConversionError(MixemyError):
    """Exception raised for errors in the conversion between a model and a schema.

    Attributes:
        model (BaseModel | type[BaseModel]): The model involved in the conversion.
        schema (BaseSchema | type[BaseSchema]): The schema involved in the conversion.
        is_model_to_schema (bool): Indicates the direction of the conversion.
        message (str | None): Optional error message. If not provided, a default message is generated.

    Args:
        model (BaseModel | type[BaseModel]): The model involved in the conversion.
        schema (BaseSchema | type[BaseSchema]): The schema involved in the conversion.
        is_model_to_schema (bool): Indicates the direction of the conversion.
        message (str | None, optional): Optional error message. Defaults to None.
    """

    def __init__(
        self,
        model: "BaseModel | type[BaseModel]",
        schema: "BaseSchema | type[BaseSchema]",
        is_model_to_schema: bool,
        message: str | None = None,
    ) -> None:
        """Initialize the conversion error between model and schema.

        Args:
            model (BaseModel | type[BaseModel]): The model involved in the conversion.
            schema (BaseSchema | type[BaseSchema]): The schema involved in the conversion.
            is_model_to_schema (bool): Flag indicating the direction of conversion.
                                       True if converting from model to schema, False otherwise.
            message (str | None, optional): Custom error message. Defaults to None.
        """
        if message is None:
            if is_model_to_schema:
                message = f"Error converting {model} to {schema}.\nThis is likely due to a mismatch between the model and schema"
            else:
                message = f"Error converting {schema} to {model}.\nThis is likely due to a mismatch between the schema and model"
        self.model = model
        self.schema = schema
        MixemyError.__init__(self, message)


class MixemyRepositoryError(MixemyError):
    """Exception raised for errors that occur within a Mixemy repository.

    Attributes:
        repository (BaseSyncRepository[Any] | BaseAsyncRepository[Any]): The repository instance where the error occurred.
        message (str): Optional. The error message. If not provided, a default message is generated.

    Args:
        repository (BaseSyncRepository[Any] | BaseAsyncRepository[Any]): The repository instance where the error occurred.
        message (str, optional): The error message. Defaults to None.
    """

    def __init__(
        self,
        repository: "BaseSyncRepository[Any] | BaseAsyncRepository[Any]",
        message: str | None = None,
    ) -> None:
        """Initialize the exception with a repository and an optional message.

        Args:
            repository (BaseSyncRepository[Any] | BaseAsyncRepository[Any]): The repository instance where the error occurred.
            message (str | None, optional): An optional error message. Defaults to None.

        If no message is provided, a default message indicating an error with the repository will be used.
        """
        if message is None:
            message = f"Error with repository {repository}."
        self.repository = repository
        MixemyError.__init__(self, message)


class MixemyRepositoryPermissionError(MixemyRepositoryError):
    """Exception raised when a user does not have the necessary permissions.

    This exception is a subclass of MixemyRepositoryError and is raised when a user
    does not have the necessary permissions to perform an operation.

    Attributes:
        repository (BaseSyncRepository[Any] | BaseAsyncRepository[Any]): The repository instance where the error occurred.
        message (str): The error message.

    Args:
        repository (BaseSyncRepository[Any] | BaseAsyncRepository[Any]): The repository instance where the error occurred.
        message (str): The error message.
    """

    def __init__(
        self,
        repository: "BaseSyncRepository[Any] | BaseAsyncRepository[Any]",
        object_id: Any | None = None,
        user_id: Any | None = None,
        message: str | None = None,
    ) -> None:
        """Initialize the exception with the given repository and message.

        Args:
            repository (BaseSyncRepository[Any] | BaseAsyncRepository[Any]): The repository instance where the error occurred.
            message (str): The error message.
        """
        if message is None:
            message = f"User {user_id} does not have permission to access object {object_id} in repository {repository}."
        self.object_id = object_id
        self.user_id = user_id
        super().__init__(repository=repository, message=message)


class MixemyRepositoryReadOnlyError(MixemyRepositoryError):
    """Exception raised when a repository is in read-only mode.

    This exception is a subclass of MixemyRepositoryError and is raised when an
    operation is attempted on a repository that is in read-only mode.

    Attributes:
        repository (BaseSyncRepository[Any] | BaseAsyncRepository[Any]): The repository instance where the error occurred.
        message (str): The error message.

    Args:
        repository (BaseSyncRepository[Any] | BaseAsyncRepository[Any]): The repository instance where the error occurred.
        message (str): The error message.
    """

    def __init__(
        self,
        repository: "BaseSyncRepository[Any] | BaseAsyncRepository[Any]",
        model: "BaseModel | type[BaseModel] | None" = None,
        operation: str | None = None,
        message: str | None = None,
    ) -> None:
        """Initialize the exception with the given repository and message.

        Args:
            repository (BaseSyncRepository[Any] | BaseAsyncRepository[Any]): The repository instance where the error occurred.
            message (str): The error message.
        """
        if message is None:
            message = f"Repository {repository} is in read-only mode."
            if model is not None:
                message += f" On Model: {model}."
            if operation is not None:
                message += f" Using Operation: {operation}."
        super().__init__(repository=repository, message=message)


class MixemyServiceError(MixemyError):
    """Exception raised for errors that occur within a Mixemy service.

    Attributes:
        service (BaseSyncService[Any, Any] | BaseAsyncService[Any, Any]): The service instance where the error occurred.
        message (str): The error message. If not provided, a default message is generated.

    Args:
        service (BaseSyncService[Any, Any] | BaseAsyncService[Any, Any]): The service instance where the error occurred.
        message (str, optional): The error message. Defaults to None.
    """

    def __init__(
        self,
        service: "BaseSyncService[Any, Any] | BaseAsyncService[Any, Any]",
        message: str | None = None,
    ) -> None:
        """Initialize the exception with the given service and an optional message.

        Args:
            service (BaseSyncService[Any, Any] | BaseAsyncService[Any, Any]):
                The service instance that caused the exception.
            message (str, optional):
                An optional error message. If not provided, a default message
                indicating an error with the service will be used.

        """
        if message is None:
            message = f"Error with service {service}."
        self.service = service
        MixemyError.__init__(self, message)


class MixemySetupError(MixemyError):
    """Exception raised for errors in the setup of a Mixemy component.

    Attributes:
        component (object): The component instance where the error occurred.
        undefined_field (str): The name of the undefined field that caused the error.
        message (str, optional): An optional error message. If not provided, a default message is generated.

    Args:
        component (object): The component instance where the error occurred.
        undefined_field (str): The name of the undefined field that caused the error.
        message (str, optional): An optional error message. If not provided, a default message is generated.
    """

    def __init__(
        self,
        component: object,
        undefined_field: str,
        message: str | None = None,
    ) -> None:
        """Initialize the exception with the component, undefined field, and an optional message.

        Args:
            component (object): The component instance where the undefined field was encountered.
            undefined_field (str): The name of the field that is undefined.
            message (str | None, optional): Custom error message. If not provided, a default message is generated.

        Returns:
            None
        """
        if message is None:
            message = f"{component.__class__.__name__.capitalize()} {component} has undefined field '{undefined_field}'.\nThis probably needs to be defined as a class attribute."
        self.undefined_field = undefined_field
        MixemyError.__init__(self, message)


class MixemyRepositorySetupError(MixemySetupError, MixemyRepositoryError):
    """Exception raised for errors in the setup of a Mixemy repository.

    This exception is a combination of MixemySetupError and MixemyRepositoryError,
    indicating that there was an issue specifically related to the repository setup.

    Attributes:
        repository (BaseSyncRepository[Any] | BaseAsyncRepository[Any]): The repository instance where the error occurred.
        undefined_field (str): The field that was not defined correctly.
        message (str | None): Optional error message providing more details about the error.
    """

    def __init__(
        self,
        repository: "BaseSyncRepository[Any] | BaseAsyncRepository[Any]",
        undefined_field: str,
        message: str | None = None,
    ) -> None:
        """Initialize the exception with the given repository, undefined field, and optional message.

        Args:
            repository (BaseSyncRepository[Any] | BaseAsyncRepository[Any]): The repository instance where the error occurred.
            undefined_field (str): The name of the undefined field that caused the error.
            message (str, optional): An optional error message. Defaults to None.
        """
        MixemySetupError.__init__(
            self,
            component=repository,
            undefined_field=undefined_field,
            message=message,
        )
        MixemyRepositoryError.__init__(
            self, repository=repository, message=self.message
        )


class MixemyServiceSetupError(MixemySetupError, MixemyServiceError):
    """Exception raised for errors in the setup of a Mixemy service.

    This exception is a combination of MixemySetupError and MixemyServiceError,
    indicating that there was an issue with the setup of a service in the Mixemy
    framework.

    Attributes:
        service (BaseSyncService[Any, Any] | BaseAsyncService[Any, Any]): The service
            that encountered the setup error.
        undefined_field (str): The field that was not defined correctly.
        message (str | None): Optional error message providing more details about the
            setup error.

    Args:
        service (BaseSyncService[Any, Any] | BaseAsyncService[Any, Any]): The service
            that encountered the setup error.
        undefined_field (str): The field that was not defined correctly.
        message (str | None, optional): Optional error message providing more details
            about the setup error. Defaults to None.
    """

    def __init__(
        self,
        service: "BaseSyncService[Any, Any] | BaseAsyncService[Any, Any]",
        undefined_field: str,
        message: str | None = None,
    ) -> None:
        """Initialize the exception with the given service, undefined field, and optional message.

        Args:
            service (BaseSyncService[Any, Any] | BaseAsyncService[Any, Any]): The service where the error occurred.
            undefined_field (str): The name of the undefined field that caused the error.
            message (str | None, optional): An optional error message. Defaults to None.
        """
        MixemySetupError.__init__(
            self, component=service, undefined_field=undefined_field, message=message
        )
        MixemyServiceError.__init__(self, service=service, message=self.message)


__all__ = [
    "MixemyConversionError",
    "MixemyError",
    "MixemyRepositoryError",
    "MixemyRepositoryPermissionError",
    "MixemyRepositorySetupError",
    "MixemyServiceError",
    "MixemyServiceSetupError",
    "MixemySetupError",
]
