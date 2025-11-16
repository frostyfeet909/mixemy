# Mixemy

[![CI](https://github.com/frostyfeet909/mixemy/actions/workflows/ci.yml/badge.svg)](https://github.com/frostyfeet909/mixemy/actions/workflows/ci.yml)
[![CD](https://github.com/frostyfeet909/mixemy/actions/workflows/cd.yml/badge.svg)](https://github.com/frostyfeet909/mixemy/actions/workflows/cd.yml)
[![CodeQL](https://github.com/frostyfeet909/mixemy/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/frostyfeet909/mixemy/actions/workflows/github-code-scanning/codeql)

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with pyright](https://microsoft.github.io/pyright/img/pyright_badge.svg)](https://microsoft.github.io/pyright/)
[![Packaged with Poetry](https://img.shields.io/badge/packaging-poetry-cyan.svg)](https://python-poetry.org/)

![Tests](./badges/tests.svg)
![Coverage](./badges/coverage.svg)

**Mixemy** is a small library providing a set of mixins for [SQLAlchemy](https://www.sqlalchemy.org/) and [Pydantic](https://docs.pydantic.dev/) to simplify common create/read/update/delete (CRUD) operations, validation, and schema management using a _service and repository_ pattern. **Both synchronous and asynchronous modes** are supported.

---

## Mixemy

Mixemy provides a repository and service abstraction layer for managing database operations with SQLAlchemy. By leveraging mixemy, you can easily implement CRUD operations in both asynchronous and synchronous contexts, as well as support complex nested (recursive) models with minimal boilerplate.

## Features

- **CRUD Abstraction:** Simplify database operations with pre-built repository and service classes.
- **Async & Sync Support:** Work with both asynchronous (AsyncSession) and synchronous (Session) SQLAlchemy sessions.
- **Recursive Model Conversion:** Automatically convert nested models for complex data structures.
- **Type-Safe Schemas:** Define input and output schemas using Pydantic-style models for data validation and serialization.

## Installation

Install mixemy using pip:

```bash
pip install mixemy
```

_(Adjust the installation command based on your environment and package source.)_

To enable async support, ensure you have the required dependencies installed:

```bash
pip install mixemy[asyncio]
```

## Getting Started

Mixemy revolves around three core components:
- **Schemas:** Define your data structures for input and output.
- **Repositories:** Implement CRUD operations on your SQLAlchemy models.
- **Services:** Build business logic on top of repositories with additional validation or transformation.

Below are usage examples for different contexts.

---

## Asynchronous CRUD Example

When working with asynchronous applications, use `AsyncSession` along with mixemy’s asynchronous base classes.

```python
from sqlalchemy.ext.asyncio import AsyncSession
from mixemy import repositories, schemas, services

# Assume AsyncItemModel is your SQLAlchemy model.

# Define the input and output schemas.
class ItemInput(schemas.InputSchema):
    value: str

class ItemOutput(schemas.IdAuditOutputSchema):
    value: str

# Create an asynchronous repository by extending the base async repository.
class ItemRepository(repositories.BaseAsyncRepository[AsyncItemModel]):
    model_type = AsyncItemModel

# Create a service that uses the repository and output schema.
class ItemService(services.BaseAsyncService[ItemRepository, ItemOutput]):
    repository_type = ItemRepository
    output_schema_type = ItemOutput

# Example usage in an async context.
async def main(async_session: AsyncSession):
    item_service = ItemService(db_session=async_session)

    # Create a new item.
    item_input = ItemInput(value="example")
    new_item = await item_service.create(object_in=item_input)

    # Read the newly created item.
    read_item = await item_service.read(id=new_item.id)

    # Update the item.
    updated_item = await item_service.update(
        id=new_item.id, object_in=ItemInput(value="updated")
    )

    # Delete the item.
    await item_service.delete(id=updated_item.id)
```

---

## Synchronous CRUD Example

For synchronous operations, mixemy provides base classes that work with SQLAlchemy’s `Session`.

```python
from sqlalchemy.orm import Session
from mixemy import repositories, schemas, services

# Assume ItemModel is your SQLAlchemy model.

# Define your input schema and an extended update schema.
class ItemInput(schemas.InputSchema):
    value: str

class ItemUpdate(ItemInput):
    nullable_value: str | None

# Define the output schema.
class ItemOutput(schemas.IdAuditOutputSchema):
    value: str
    nullable_value: str | None

# Create a synchronous repository by extending the base sync repository.
class ItemRepository(repositories.BaseSyncRepository[ItemModel]):
    model_type = ItemModel

# Create a service that uses the repository and output schema.
class ItemService(services.BaseSyncService[ItemRepository, ItemOutput]):
    repository_type = ItemRepository
    output_schema_type = ItemOutput

# Example usage in a synchronous context.
def main(session: Session):
    item_service = ItemService(db_session=session)

    # Create a new item.
    item_input = ItemInput(value="example")
    new_item = item_service.create(object_in=item_input)

    # Read the newly created item.
    read_item = item_service.read(id=new_item.id)

    # Update the item.
    updated_item = item_service.update(
        id=new_item.id,
        object_in=ItemUpdate(value="updated", nullable_value="new_value")
    )

    # Delete the item.
    item_service.delete(id=updated_item.id)
```

---

## Recursive Model Example

Mixemy also supports recursive (nested) models, automatically converting nested structures when reading or writing data.

```python
from sqlalchemy.orm import Session
from mixemy import repositories, schemas, services

# Assume RecursiveItemModel is your SQLAlchemy model with nested relationships.

# Define schemas for sub-items.
class SubItemInput(schemas.InputSchema):
    value: str

class SingularSubItemInput(schemas.InputSchema):
    value: str

class SubItemOutput(schemas.IdAuditOutputSchema):
    value: str

class SingularSubItemOutput(schemas.IdAuditOutputSchema):
    value: str

# Define the main item schemas with nested sub-items.
class ItemInput(schemas.InputSchema):
    sub_items: list[SubItemInput]
    singular_sub_item: SingularSubItemInput

class ItemOutput(schemas.IdAuditOutputSchema):
    sub_items: list[SubItemOutput]
    singular_sub_item: SingularSubItemOutput

# Create a repository for the recursive model.
class ItemRepository(repositories.BaseSyncRepository[RecursiveItemModel]):
    model_type = RecursiveItemModel

# Create a service with recursive model conversion enabled.
class ItemService(services.BaseSyncService[ItemRepository, ItemOutput]):
    repository_type = ItemRepository
    output_schema_type = ItemOutput
    default_model_recursive_model_conversion = True

# Example usage.
def main(session: Session):
    item_service = ItemService(db_session=session)

    # Define an item with nested sub-items.
    item_input = ItemInput(
        sub_items=[SubItemInput(value="subitem1"), SubItemInput(value="subitem2")],
        singular_sub_item=SingularSubItemInput(value="main_item")
    )

    # Create the item.
    new_item = item_service.create(object_in=item_input)

    # Retrieve the item with nested models automatically converted.
    read_item = item_service.read(id=new_item.id)
```

---

## Additional Information

- **Schema Definitions:** Mixemy uses schema classes (e.g., `InputSchema` and `IdAuditOutputSchema`) to validate and serialize data. You can customize these schemas according to your domain requirements.
- **Extensibility:** The repository and service classes can be extended to add custom query logic or additional business rules.
- **Integration:** Mixemy is designed to integrate seamlessly with SQLAlchemy, ensuring you can work with your existing models without significant modifications.

---

## Why Use Mixemy?

- **Speed up development** by reducing boilerplate for common operations.
- **Stay type-safe** with Pydantic schemas and typed repositories/services.
- **Choose sync or async** to fit your application architecture.
- **Extensible**—override or extend base repositories and services to customize or add new functionality.
- **Built for maintainability** with consistent code structure and naming.

## License

This project is licensed under the [MIT License](LICENSE).

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on [GitHub](https://github.com/frostyfeet909/mixemy) if you have suggestions or feature requests.

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes.
4. Push to your branch and open a pull request.

### CI/CD

This project uses GitHub Actions for continuous integration (CI) and continuous deployment (CD). The CI workflow runs tests, linters, and type checkers on every push to the main branch. We also use CodeRabbit for code quality analysis.

To run this locally use the following command:

```bash
poetry run install pre-commit
poetry run pre-commit run --all-files
```

You will need to have [Docker](https://www.docker.com/) installed to run the CI workflow locally.

---

Happy coding with **Mixemy**! If you find this library helpful, feel free to star it on GitHub or contribute.
