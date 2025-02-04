from typing import TYPE_CHECKING

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

if TYPE_CHECKING:
    from mixemy.models import IdAuditModel


@pytest.mark.database
@pytest.mark.integration
@pytest.mark.asyncio
async def test_main(
    async_session: AsyncSession, async_item_model: "type[IdAuditModel]", init_db: None
) -> None:
    from mixemy import repositories, schemas, services

    AsyncItemModel = async_item_model

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
