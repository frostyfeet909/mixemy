from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column


def test_main() -> None:
    from mixemy import crud, models, schemas

    class ItemModel(models.IdAuditModel):
        value: Mapped[str] = mapped_column(String)

    class ItemInput(schemas.InputSchema):
        value: str

    class ItemUpdate(schemas.InputSchema):
        value: str

    class ItemCRUD(crud.IdAuditCRUD[ItemModel, ItemInput, ItemUpdate]):
        pass

    ItemCRUD(ItemModel)
