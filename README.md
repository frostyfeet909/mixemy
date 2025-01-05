# Mixemy

**Mixemy** is a small library providing a set of mixins for [SQLAlchemy](https://www.sqlalchemy.org/) and [Pydantic](https://docs.pydantic.dev/) to simplify common CRUD operations, validation, and schema management.

## Features

- **Models**: Base classes and mixins that extend SQLAlchemy `declarative_base()` models with useful fields like IDs and timestamps.
- **Schemas**: Pydantic schemas for input validation, serialization, and more.
- **CRUD**: Generic CRUD classes that can be extended to handle common database interactions—create, read, update, and delete.

## Installation

```bash
pip install mixemy
```

*or*, if you prefer [Poetry](https://python-poetry.org/):

```bash
poetry add mixemy
```

## Quick Start

Below is a minimal example demonstrating how to use `mixemy` to create a SQLAlchemy model, corresponding Pydantic schemas, and a CRUD class:

```python
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

from mixemy import crud, models, schemas

# Define a SQLAlchemy model with some default fields (e.g., id, created_at, updated_at)
class ItemModel(models.IdAuditModel):
    value: Mapped[str] = mapped_column(String)

# Define Pydantic schemas for input and updates
class ItemInput(schemas.InputSchema):
    value: str

class ItemUpdate(schemas.InputSchema):
    value: str

# Extend the generic CRUD class to specify the model and schemas
class ItemCRUD(crud.IdAuditCRUD[ItemModel, ItemInput, ItemUpdate]):
    pass

# Instantiate the CRUD class with the model
item_crud = ItemCRUD(ItemModel)
```

### Explanation

- **`ItemModel`**  
  Inherits from `models.IdAuditModel`, which provides default columns such as `id`, `created_at`, and `updated_at`. We add our own `value` field as a `String`.

- **`ItemInput`** & **`ItemUpdate`**  
  These are Pydantic schemas that extend `schemas.InputSchema`. Use these for type-safe request inputs in create and update operations.

- **`ItemCRUD`**  
  Extends `crud.IdAuditCRUD`, which already implements generic CRUD operations (like `create`, `read`, `update`, `delete`) for our model and schemas. You can override these methods if you need custom behavior.

## Why Use Mixemy?

- **Speed up development** by reducing boilerplate for common operations.
- **Stay type-safe** with Pydantic schemas and generics in CRUD classes.
- **Extensible**—override base classes or methods to customize or add new functionality.
- **Built for maintainability** with consistent code structure and naming.

## License

This project is licensed under the [MIT License](LICENSE).

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on [GitHub](https://github.com/frostyfeet909/mixemy) if you have suggestions or feature requests.

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes.
4. Push to your branch and open a pull request.

---

Happy coding with **Mixemy**! If you find this library helpful, feel free to star it on GitHub or contribute.
