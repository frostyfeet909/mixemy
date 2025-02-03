from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from mixemy.repositories import BaseAsyncRepository, BaseSyncRepository
    from mixemy.services import BaseAsyncService, BaseSyncService


class MixemyError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class MixemySetupError(MixemyError):
    def __init__(
        self,
        component: object,
        component_name: str,
        undefined_field: str,
        message: str | None = None,
    ) -> None:
        if message is None:
            message = f"{component_name.capitalize()} {component} has undefined field '{undefined_field}'.\nThis probably needs to be defined as a class attribute."
        self.component = component
        self.component_name = component_name
        self.undefined_field = undefined_field
        super().__init__(message=message)


class MixemyRepositorySetupError(MixemySetupError):
    def __init__(
        self,
        repository: "BaseSyncRepository[Any] | BaseAsyncRepository[Any]",
        undefined_field: str,
        message: str | None = None,
    ) -> None:
        self.repository = repository
        super().__init__(
            message=message,
            component=repository,
            undefined_field=undefined_field,
            component_name="repository",
        )


class MixemyServiceSetupError(MixemySetupError):
    def __init__(
        self,
        service: "BaseSyncService[Any, Any, Any, Any, Any, Any] | BaseAsyncService[Any, Any, Any, Any, Any, Any]",
        undefined_field: str,
        message: str | None = None,
    ) -> None:
        self.service = service
        super().__init__(
            message=message,
            component=service,
            undefined_field=undefined_field,
            component_name="service",
        )
