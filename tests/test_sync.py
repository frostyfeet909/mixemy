from typing import TYPE_CHECKING

import pytest
from sqlalchemy.orm import Session
from uuid_utils.compat import UUID

if TYPE_CHECKING:
    from mixemy.models import IdAuditModel


@pytest.mark.database
@pytest.mark.integration
def test_main(
    session: Session, init_db: None, item_model: "type[IdAuditModel]"
) -> None:
    """Test the main functionality of the ItemService class.

    This test covers the following scenarios:
    1. Creating items.
    2. Reading items by ID.
    3. Updating an item.
    4. Reading multiple items with filters.
    5. Deleting items.

    Args:
        session (Session): The database session to use for the test.
        init_db (None): Fixture to initialize the database.
        item_model (type[IdAuditModel]): The model class to use for the items.

    Raises:
        - The created items have the correct values.
        - The read items are not None and have the correct values.
        - The updated item has the correct updated values.
        - The correct number of items are returned when filtering.
        - The deleted items are no longer present in the database.
    """
    from mixemy import repositories, schemas, services

    ItemModel = item_model

    class ItemInput(schemas.InputSchema):
        value: str

    class ItemUpdate(ItemInput):
        nullable_value: str | None

    class ItemFilter(schemas.InputSchema):
        value: list[str]

    class ItemOutput(schemas.IdAuditOutputSchema):
        value: str
        nullable_value: str | None

    class ItemRepository(repositories.BaseSyncRepository[ItemModel]):
        model = ItemModel

    class ItemService(services.BaseSyncService[ItemRepository, ItemOutput]):
        repository_type = ItemRepository
        output_schema_type = ItemOutput

    item_service = ItemService(db_session=session)

    test_one = ItemInput(value="test_one")
    test_two = ItemInput(value="test_two")
    test_three = ItemInput(value="test_one")
    test_one_update = ItemUpdate(value="test_one", nullable_value="test_one_updated")
    test_one_id = None

    item_one = item_service.create(object_in=test_one)
    item_two = item_service.create(object_in=test_two)
    item_service.create(object_in=test_three)

    test_one_id = item_one.id

    assert item_one.value == "test_one"
    assert item_two.value == "test_two"

    item_one = item_service.read(id=item_one.id)
    item_two = item_service.read(id=item_two.id)

    assert item_one is not None
    assert item_two is not None
    assert item_one.value == "test_one"
    assert item_one.nullable_value is None
    assert item_two.value == "test_two"
    assert item_two.nullable_value is None

    item_one = item_service.update(id=item_one.id, object_in=test_one_update)

    assert item_one is not None
    assert item_one.value == "test_one"
    assert item_one.nullable_value == "test_one_updated"
    assert item_one.id == test_one_id

    items = item_service.read_multiple(filters=ItemFilter(value=["test_one"]))

    assert len(items) == 2

    item_service.delete(id=item_one.id)

    item_one = item_service.read(id=item_one.id)
    item_two = item_service.read(id=item_two.id)

    assert item_one is None
    assert item_two is not None
    assert item_two.value == "test_two"

    item_service.delete(id=item_two.id)

    item_two = item_service.read(id=item_two.id)

    assert item_two is None


def test_recursive_model(
    session: Session, init_db: None, recursive_item_model: "type[IdAuditModel]"
) -> None:
    """Test the recursive model functionality.

    This test verifies the creation and retrieval of a recursive item model
    using the provided session and database initialization.

    Args:
        session (Session): The database session to use for the test.
        init_db (None): A fixture to initialize the database.
        recursive_item_model (type[IdAuditModel]): The recursive item model type.

    Raises:
        The created item is not None.
        The created item has two sub-items with the expected values.
        The created item has a singular sub-item with the expected value.
    """
    from mixemy import repositories, schemas, services

    RecursiveItemModel = recursive_item_model

    class SubItemInput(schemas.InputSchema):
        value: str

    class SingularSubItemInput(schemas.InputSchema):
        value: str

    class SubItemOutput(schemas.IdAuditOutputSchema):
        value: str

    class SingularSubItemOutput(schemas.IdAuditOutputSchema):
        value: str

    class ItemInput(schemas.InputSchema):
        sub_items: list[SubItemInput]
        singular_sub_item: SingularSubItemInput

    class ItemOutput(schemas.IdAuditOutputSchema):
        sub_items: list[SubItemOutput]
        singular_sub_item: SingularSubItemOutput

    class ItemRepository(repositories.BaseSyncRepository[RecursiveItemModel]):
        model = RecursiveItemModel

    class ItemService(
        services.BaseSyncService[
            ItemRepository,
            ItemOutput,
        ]
    ):
        repository_type = ItemRepository
        output_schema_type = ItemOutput
        default_recursive_model_conversion = True

    item_service = ItemService(db_session=session)

    test_item = ItemInput(
        sub_items=[
            SubItemInput(value="sub_item_one"),
            SubItemInput(value="sub_item_two"),
        ],
        singular_sub_item=SingularSubItemInput(value="singular_sub_item"),
    )

    item_id = item_service.create(object_in=test_item).id

    item = item_service.read(id=item_id)

    assert item is not None
    assert len(item.sub_items) == 2
    assert item.sub_items[0].value == "sub_item_one"
    assert item.sub_items[1].value == "sub_item_two"
    assert item.singular_sub_item.value == "singular_sub_item"


def test_permission_model(
    session: Session,
    init_db: None,
    permission_item_model: "type[IdAuditModel]",
    user_model: "type[IdAuditModel]",
) -> None:
    """Test the permission model functionality.

    This test verifies the creation and retrieval of permission items using the provided session
    and database initialization.

    Args:
        session (Session): The database session to use for the test.
        init_db (None): A fixture to initialize the database.
        permission_item_model (type[IdAuditModel]): The permission item model type.
        user_model (type[IdAuditModel]): The user model type.
    """
    from mixemy import exceptions, repositories, schemas, services

    PermissionItemModel = permission_item_model

    class ItemInput(schemas.InputSchema):
        value: str
        user_id: UUID

    class ItemOutput(schemas.IdAuditOutputSchema):
        value: str

    class UserRepository(repositories.BaseSyncRepository[user_model]):
        model = user_model

    class UserService(
        services.BaseSyncService[UserRepository, schemas.IdAuditOutputSchema]
    ):
        repository_type = UserRepository
        output_schema_type = schemas.IdAuditOutputSchema

    class ItemRepository(repositories.PermissionSyncRepository[PermissionItemModel]):
        model = PermissionItemModel

    class ItemService(services.PermissionSyncService[ItemRepository, ItemOutput]):
        repository_type = ItemRepository
        output_schema_type = ItemOutput

    item_service = ItemService(db_session=session)
    user_service = UserService(db_session=session)

    user_one = user_service.create(object_in=schemas.InputSchema())
    user_two = user_service.create(object_in=schemas.InputSchema())

    test_one = ItemInput(value="test_one", user_id=user_one.id)
    test_two = ItemInput(value="test_two", user_id=user_one.id)
    test_three = ItemInput(value="test_three", user_id=user_two.id)

    created_item_one = item_service.create(object_in=test_one)
    item_service.create(object_in=test_two)
    item_service.create(object_in=test_three)

    assert created_item_one.value == "test_one"

    all_created_items = item_service.read_multiple_with_permission(user_id=user_one.id)

    assert len(all_created_items) == 2

    with pytest.raises(exceptions.MixemyRepositoryPermissionError):
        item_service.delete_with_permission(
            id=created_item_one.id, user_id=test_three.user_id
        )

    with pytest.raises(exceptions.MixemyRepositoryPermissionError):
        item_service.update_with_permission(
            id=created_item_one.id, object_in=test_one, user_id=test_three.user_id
        )

    assert (
        item_service.read_with_permission(
            id=created_item_one.id, user_id=test_three.user_id
        )
        is None
    )

    assert (
        item_service.read_with_permission(
            id=created_item_one.id, user_id=test_one.user_id
        )
        == created_item_one
    )

    item_service.delete_with_permission(
        id=created_item_one.id, user_id=test_one.user_id
    )

    assert (
        item_service.read_with_permission(
            id=created_item_one.id, user_id=test_one.user_id
        )
        is None
    )


def test_read_only_repository(
    session: Session, init_db: None, item_model: "type[IdAuditModel]"
) -> None:
    """Test the read-only repository functionality.

    This test verifies that the read-only repository raises the appropriate error
    when attempting to perform write operations.
    """
    from mixemy import exceptions, repositories, schemas, services

    ItemModel = item_model

    class ItemInput(schemas.InputSchema):
        value: str

    class ItemUpdate(ItemInput):
        nullable_value: str | None

    class ItemOutput(schemas.IdAuditOutputSchema):
        value: str
        nullable_value: str | None

    class ItemRepository(repositories.BaseSyncRepository[ItemModel]):
        model = ItemModel

    class ItemService(services.BaseSyncService[ItemRepository, ItemOutput]):
        repository_type = ItemRepository
        output_schema_type = ItemOutput

    item_service = ItemService(db_session=session)

    test_one = ItemInput(value="test_one")
    test_two = ItemInput(value="test_two")
    test_one_update = ItemUpdate(value="test_one", nullable_value="test_one_updated")

    item_one = item_service.create(object_in=test_one)
    item_two = item_service.create(object_in=test_two)

    class NewItemRepository(repositories.BaseSyncRepository[ItemModel]):
        model = ItemModel
        default_is_read_only = True

    class NewItemService(services.BaseSyncService[NewItemRepository, ItemOutput]):
        repository_type = NewItemRepository
        output_schema_type = ItemOutput

    new_item_service = NewItemService(db_session=session)

    item_one = new_item_service.read(id=item_one.id)
    item_two = new_item_service.read(id=item_two.id)

    assert item_one is not None
    assert item_two is not None
    assert item_one.value == "test_one"
    assert item_one.nullable_value is None
    assert item_two.value == "test_two"
    assert item_two.nullable_value is None

    with pytest.raises(exceptions.MixemyRepositoryReadOnlyError):
        new_item_service.update(id=item_one.id, object_in=test_one_update)

    with pytest.raises(exceptions.MixemyRepositoryReadOnlyError):
        new_item_service.create(object_in=test_one)

    with pytest.raises(exceptions.MixemyRepositoryReadOnlyError):
        new_item_service.delete(id=item_one.id)
