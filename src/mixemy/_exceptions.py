from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mixemy.repositories import BaseRepository
    from mixemy.services import BaseService
    from mixemy.types import (
        BaseModelType,
        CreateSchemaType,
        FilterSchemaType,
        OutputSchemaType,
        UpdateSchemaType,
    )


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
        repository: "BaseRepository[BaseModelType]",
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
        service: "BaseService[BaseModelType, CreateSchemaType, UpdateSchemaType, FilterSchemaType, OutputSchemaType]",
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
