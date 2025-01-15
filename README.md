# Mixemy

[![CI](https://github.com/frostyfeet909/mixemy/actions/workflows/ci.yml/badge.svg)](https://github.com/frostyfeet909/mixemy/actions/workflows/ci.yml)
[![CD](https://github.com/frostyfeet909/mixemy/actions/workflows/cd.yml/badge.svg)](https://github.com/frostyfeet909/mixemy/actions/workflows/cd.yml)

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with pyright](https://microsoft.github.io/pyright/img/pyright_badge.svg)](https://microsoft.github.io/pyright/)
[![Packaged with Poetry](https://img.shields.io/badge/packaging-poetry-cyan.svg)](https://python-poetry.org/)

**Mixemy** is a small library providing a set of mixins for [SQLAlchemy](https://www.sqlalchemy.org/) and [Pydantic](https://docs.pydantic.dev/) to simplify common create/read/update/delete (CRUD) operations, validation, and schema management using a _service and repository_ pattern. **Both synchronous and asynchronous modes** are supported.

## Features

- **Models**: Base classes and mixins that extend SQLAlchemy `declarative_base()` models with useful fields like IDs and timestamps.
- **Schemas**: Pydantic schemas for input validation, serialization, filtering, and more.
- **Repositories**: Classes that handle data persistence and database interactions, such as retrieving or storing model objects.
- **Services**: High-level classes that orchestrate CRUD operations, input validation, and output transformation (using repositories and schemas).
- **Async or Sync**: Out of the box, Mixemy offers both synchronous and asynchronous repositories/services.

## Installation

```bash
pip install mixemy
```

*or*, if you prefer [Poetry](https://python-poetry.org/):

```bash
poetry add mixemy
```

## Quick Start (Sync Example)

Below is a minimal synchronous example demonstrating how to use **Mixemy** to create:

- A SQLAlchemy model,
- Pydantic schemas for input, update, filter, and output, 
- A repository class for database operations,
- A service class that orchestrates create/read/update/delete operations.

```python
from sqlalchemy.orm import Mapped, mapped_column, Session
from sqlalchemy import String

from mixemy import models, repositories, schemas, services

# 1. Define a SQLAlchemy model with default fields (e.g., id, created_at, updated_at).
class ItemModel(models.IdAuditModel):
    __table_args__ = {"extend_existing": True}  # noqa: RUF012
    value: Mapped[str] = mapped_column(String)
    nullable_value: Mapped[str | None] = mapped_column(String, nullable=True)

# 2. Define Pydantic schemas for input, updates, filtering, and output.
class ItemInput(schemas.InputSchema):
    value: str

class ItemUpdate(ItemInput):
    nullable_value: str | None

class ItemFilter(schemas.InputSchema):
    value: list[str]

class ItemOutput(schemas.IdAuditOutputSchema):
    value: str
    nullable_value: str | None

# 3. Define a repository for database operations.
class ItemRepository(repositories.IdAuditSyncRepository[ItemModel]):
    model_type = ItemModel

# 4. Define a service that uses the repository and schemas to provide CRUD operations.
class ItemService(
    services.IdAuditSyncService[
        ItemModel, ItemInput, ItemUpdate, ItemFilter, ItemOutput
    ]
):
    repository_type = ItemRepository
    output_schema_type = ItemOutput

# 5. Instantiate the service class.
item_service = ItemService(db_session=...)

# 6. Example usage in a synchronous context:
def example_usage():
    test_one = ItemInput(value="test_one")
    test_two = ItemInput(value="test_two")
    test_three = ItemInput(value="test_one")
    test_one_update = ItemUpdate(value="test_one", nullable_value="test_one_updated")

    # Create items
    item_one = item_service.create(object_in=test_one)
    item_two = item_service.create(object_in=test_two)
    item_service.create(object_in=test_three)

    # Read items
    item_one = item_service.read(id=item_one.id)
    item_two = item_service.read(id=item_two.id)

    # Update an item
    item_one = item_service.update(
        id=item_one.id, object_in=test_one_update
    )

    # Read multiple items by filter
    items = item_service.read_multi(
        filters=ItemFilter(value=["test_one"])
    )

    # Delete an item
    item_service.delete(id=item_one.id)
```

### Explanation (Sync)

- **`ItemModel`**  
  Inherits from `models.IdAuditModel`, which provides common columns such as `id`, `created_at`, and `updated_at`. We add our own `value` and an optional `nullable_value`.

- **Pydantic Schemas**  
  - `ItemInput` for creating an item,  
  - `ItemUpdate` for updating existing items,  
  - `ItemFilter` for filtering when reading multiple items,  
  - `ItemOutput` for returning data (e.g., in a response).

- **`ItemRepository`**  
  Extends `repositories.IdAuditSyncRepository`, which handles database interactions for the given model.

- **`ItemService`**  
  Extends `services.IdAuditSyncService`, which implements the common operations (`create`, `read`, `update`, `delete`) using the repository. You can override these methods if you need custom behavior.

## Asynchronous Example

If you prefer to work with asynchronous database sessions (e.g., using `async_session`), Mixemy provides **async repositories** and **async services**:

```python
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

from mixemy import models, repositories, schemas, services

class AsyncItemModel(models.IdAuditModel):
    __table_args__ = {"extend_existing": True}  # noqa: RUF012
    value: Mapped[str] = mapped_column(String)

class ItemInput(schemas.InputSchema):
    value: str

class ItemOutput(schemas.IdAuditOutputSchema):
    value: str

class ItemRepository(repositories.IdAuditAsyncRepository[AsyncItemModel]):
    model_type = AsyncItemModel

class ItemService(
    services.IdAuditAsyncService[
        AsyncItemModel, ItemInput, ItemInput, ItemInput, ItemOutput
    ]
):
    repository_type = ItemRepository
    output_schema_type = ItemOutput

item_service = ItemService(db_session=...)

async def async_example_usage():
    test_one = ItemInput(value="test_one")
    test_two = ItemInput(value="test_two")

    # Create items
    item_one = await item_service.create(object_in=test_one)
    item_two = await item_service.create(object_in=test_two)

    assert item_one.value == "test_one"
    assert item_two.value == "test_two"

    # Read items
    item_one = await item_service.read(id=item_one.id)
    item_two = await item_service.read(id=item_two.id)

    assert item_one is not None
    assert item_two is not None
    assert item_one.value == "test_one"
    assert item_two.value == "test_two"

    # Update an item (using the same schema here for simplicity)
    item_one = await item_service.update(
        id=item_one.id, object_in=test_two
    )

    assert item_one.value == "test_two"

    # Delete an item
    await item_service.delete(id=item_one.id)
    item_one = await item_service.read(id=item_one.id)

    # Verify it was deleted
    assert item_one is None

    # Check the second item is still intact
    item_two = await item_service.read(id=item_two.id)
    assert item_two is not None
    assert item_two.value == "test_two"

    # Finally, delete the second item
    await item_service.delete(id=item_two.id)
    item_two = await item_service.read(id=item_two.id)
    assert item_two is None
```

### Explanation (Async)

- **`AsyncItemModel`**  
  Same as a typical SQLAlchemy model but used in conjunction with async sessions.

- **Pydantic Schemas**  
  Adjusted as needed for create and output. You can have distinct schemas for update/filter, too.

- **`ItemRepository`**  
  Extends `repositories.IdAuditAsyncRepository`, which is the async variant for database interactions.

- **`ItemService`**  
  Extends `services.IdAuditAsyncService`, which implements the common async operations (`create`, `read`, `update`, `delete`) using the async repository.  

With these async classes, you can integrate Mixemy into your async Python frameworks like **FastAPI** or **Quart** seamlessly.

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

This project uses GitHub Actions for continuous integration (CI) and continuous deployment (CD). The CI workflow runs tests, linters, and type checkers on every push to the main branch.

To run this locally use the following command:

```bash
poetry run install pre-commit
poetry run pre-commit run --all-files
```

You will need to have [Docker](https://www.docker.com/) installed to run the CI workflow locally.

---

Happy coding with **Mixemy**! If you find this library helpful, feel free to star it on GitHub or contribute.
