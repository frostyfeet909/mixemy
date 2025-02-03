import pytest
from sqlalchemy import String
from sqlalchemy.orm import Mapped, Session, mapped_column


@pytest.mark.database
@pytest.mark.integration
def test_main(session: Session, init_db: None) -> None:
    from mixemy import models, repositories, schemas, services

    class ItemModel(models.IdAuditModel):
        __table_args__ = {"extend_existing": True}  # noqa: RUF012
        value: Mapped[str] = mapped_column(String)
        nullable_value: Mapped[str | None] = mapped_column(String, nullable=True)

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
