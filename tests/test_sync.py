from typing import TYPE_CHECKING

import pytest
from sqlalchemy.orm import Session

if TYPE_CHECKING:
    from mixemy.models import IdAuditModel


@pytest.mark.database
@pytest.mark.integration
def test_main(
    session: Session, init_db: None, item_model: "type[IdAuditModel]"
) -> None:
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
        model_type = ItemModel

    class ItemService(
        services.BaseSyncService[
            ItemModel, ItemRepository, ItemInput, ItemUpdate, ItemFilter, ItemOutput
        ]
    ):
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
    session: Session,
    init_db: None,
    recursive_item_model: "type[IdAuditModel]",
    sub_item_model: "type[IdAuditModel]",
) -> None:
    from mixemy import repositories, schemas, services

    RecursiveItemModel = recursive_item_model

    class SubItemInput(schemas.InputSchema):
        value: str

    class SubItemOutput(schemas.IdAuditOutputSchema):
        value: str

    class ItemInput(schemas.InputSchema):
        sub_items: list[SubItemInput]

    class ItemOutput(schemas.IdAuditOutputSchema):
        sub_items: list[SubItemOutput]

    class ItemRepository(repositories.BaseSyncRepository[RecursiveItemModel]):
        model_type = RecursiveItemModel

    class ItemService(
        services.BaseSyncService[
            RecursiveItemModel,
            ItemRepository,
            ItemInput,
            ItemInput,
            ItemInput,
            ItemOutput,
        ]
    ):
        repository_type = ItemRepository
        output_schema_type = ItemOutput
        default_model_recursive_model_conversion = True

    item_service = ItemService(db_session=session)

    test_item = ItemInput(
        sub_items=[
            SubItemInput(value="sub_item_one"),
            SubItemInput(value="sub_item_two"),
        ]
    )

    item_id = item_service.create(object_in=test_item).id

    item = item_service.read(id=item_id)

    assert item is not None
    assert len(item.sub_items) == 2
    assert item.sub_items[0].value == "sub_item_one"
    assert item.sub_items[1].value == "sub_item_two"
