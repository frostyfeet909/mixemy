import pytest
from sqlalchemy import String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column


@pytest.mark.database
@pytest.mark.integration
@pytest.mark.asyncio
async def test_main(async_session: AsyncSession, init_db: None) -> None:
    from mixemy import models, repositories, schemas, services

    class AsyncItemModel(models.IdAuditModel):
        __table_args__ = {"extend_existing": True}  # noqa: RUF012
        value: Mapped[str] = mapped_column(String)

    class ItemInput(schemas.InputSchema):
        value: str

    class ItemOutput(schemas.IdAuditOutputSchema):
        value: str

    class ItemRepository(repositories.BaseAsyncRepository[AsyncItemModel]):
        model_type = AsyncItemModel

    class ItemService(
        services.BaseAsyncService[
            AsyncItemModel, ItemRepository, ItemInput, ItemInput, ItemInput, ItemOutput
        ]
    ):
        repository_type = ItemRepository
        output_schema_type = ItemOutput

    item_service = ItemService(db_session=async_session)

    test_one = ItemInput(value="test_one")
    test_two = ItemInput(value="test_two")

    item_one = await item_service.create(object_in=test_one)
    item_two = await item_service.create(object_in=test_two)

    assert item_one.value == "test_one"
    assert item_two.value == "test_two"

    item_one = await item_service.read(id=item_one.id)
    item_two = await item_service.read(id=item_two.id)

    assert item_one is not None
    assert item_two is not None
    assert item_one.value == "test_one"
    assert item_two.value == "test_two"

    item_one = await item_service.update(id=item_one.id, object_in=test_two)

    assert item_one is not None
    assert item_one.value == "test_two"

    await item_service.delete(id=item_one.id)

    item_one = await item_service.read(id=item_one.id)
    item_two = await item_service.read(id=item_two.id)

    assert item_one is None
    assert item_two is not None
    assert item_two.value == "test_two"

    await item_service.delete(id=item_two.id)

    item_two = await item_service.read(id=item_two.id)

    assert item_two is None
