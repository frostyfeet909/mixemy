from asyncio import current_task
from collections.abc import AsyncGenerator, Generator
from uuid import UUID

import pytest
import pytest_asyncio
from sqlalchemy import UUID as SQLAUUID
from sqlalchemy import Engine, ForeignKey, String, create_engine, make_url
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import (
    Mapped,
    Session,
    mapped_column,
    relationship,
    scoped_session,
    sessionmaker,
)
from testcontainers.postgres import PostgresContainer

from mixemy import models


class AsyncItemModel(models.IdAuditModel):
    __table_args__ = {"extend_existing": True}  # noqa: RUF012
    value: Mapped[str] = mapped_column(String)


class ItemModel(models.IdAuditModel):
    __table_args__ = {"extend_existing": True}  # noqa: RUF012
    value: Mapped[str] = mapped_column(String)
    nullable_value: Mapped[str | None] = mapped_column(String, nullable=True)


class RecursiveItemModel(models.IdAuditModel):
    __table_args__ = {"extend_existing": True}  # noqa: RUF012

    sub_items: Mapped[list["SubItemModel"]] = relationship(
        "SubItemModel", back_populates="item"
    )
    singular_sub_item: Mapped["SingularSubItemModel"] = relationship(
        "SingularSubItemModel", back_populates="item"
    )


class SubItemModel(models.IdAuditModel):
    __table_args__ = {"extend_existing": True}  # noqa: RUF012
    value: Mapped[str] = mapped_column(String)
    item_id: Mapped[UUID] = mapped_column(SQLAUUID, ForeignKey("recursive_item.id"))

    item: Mapped["RecursiveItemModel"] = relationship(
        "RecursiveItemModel", back_populates="sub_items"
    )


class SingularSubItemModel(models.IdAuditModel):
    __table_args__ = {"extend_existing": True}  # noqa: RUF012
    value: Mapped[str] = mapped_column(String)
    item_id: Mapped[UUID] = mapped_column(SQLAUUID, ForeignKey("recursive_item.id"))

    item: Mapped["RecursiveItemModel"] = relationship(
        "RecursiveItemModel", back_populates="singular_sub_item"
    )


class UserModel(models.IdAuditModel):
    __table_args__ = {"extend_existing": True}  # noqa: RUF012

    items: Mapped[list["PermissionItemModel"]] = relationship(
        "PermissionItemModel", back_populates="user"
    )


class PermissionItemModel(models.IdAuditModel):
    __table_args__ = {"extend_existing": True}  # noqa: RUF012
    value: Mapped[str] = mapped_column(String)
    user_id: Mapped[UUID] = mapped_column(SQLAUUID, ForeignKey("user.id"))

    user: Mapped["UserModel"] = relationship("UserModel", back_populates="items")


@pytest.fixture(scope="module")
def item_model() -> type[ItemModel]:
    return ItemModel


@pytest.fixture(scope="module")
def async_item_model() -> type[AsyncItemModel]:
    return AsyncItemModel


@pytest.fixture(scope="module")
def recursive_item_model() -> type[RecursiveItemModel]:
    return RecursiveItemModel


@pytest.fixture(scope="module")
def sub_item_model() -> type[SubItemModel]:
    return SubItemModel


@pytest.fixture(scope="module")
def singular_sub_item_model() -> type[SingularSubItemModel]:
    return SingularSubItemModel


@pytest.fixture(scope="module")
def user_model() -> type[UserModel]:
    return UserModel


@pytest.fixture(scope="module")
def permission_item_model() -> type[PermissionItemModel]:
    return PermissionItemModel


@pytest.fixture(scope="module")
def db_container() -> Generator[PostgresContainer, None, None]:
    with PostgresContainer("postgres:latest") as postgres:
        yield postgres


@pytest.fixture(scope="module")
def engine(db_container: PostgresContainer) -> Engine:
    return create_engine(make_url(db_container.get_connection_url()))


@pytest.fixture(scope="module")
def scoped_session_maker(engine: Engine) -> scoped_session[Session]:
    return scoped_session(sessionmaker(bind=engine))


@pytest.fixture(scope="module")
def async_engine(db_container: PostgresContainer) -> AsyncEngine:
    return create_async_engine(
        make_url(db_container.get_connection_url(driver="asyncpg"))
    )


@pytest.fixture(scope="module")
def async_scoped_session_maker(
    async_engine: AsyncEngine,
) -> async_scoped_session[AsyncSession]:
    return async_scoped_session(
        async_sessionmaker(bind=async_engine, expire_on_commit=False),
        scopefunc=current_task,
    )


@pytest.fixture
def session(
    scoped_session_maker: scoped_session[Session],
) -> Generator[Session]:
    session = scoped_session_maker()
    try:
        yield session
    finally:
        session.close()


@pytest_asyncio.fixture(scope="function")  # pyright: ignore[reportUntypedFunctionDecorator,reportUnknownMemberType]
async def async_session(
    async_scoped_session_maker: async_scoped_session[AsyncSession],
) -> AsyncGenerator[AsyncSession]:
    session = async_scoped_session_maker()
    try:
        yield session
    finally:
        await session.close()


@pytest.fixture(scope="module")
def init_db(
    engine: Engine,
) -> None:
    ItemModel.__table__.create(bind=engine)  # type: ignore - Only for testing
    AsyncItemModel.__table__.create(bind=engine)  # type: ignore - Only for testing
    RecursiveItemModel.__table__.create(bind=engine)  # type: ignore - Only for testing
    SubItemModel.__table__.create(bind=engine)  # type: ignore - Only for testing
    SingularSubItemModel.__table__.create(bind=engine)  # type: ignore - Only for testing
    UserModel.__table__.create(bind=engine)  # type: ignore - Only for testing
    PermissionItemModel.__table__.create(bind=engine)  # type: ignore - Only for testing
