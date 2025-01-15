from asyncio import current_task
from collections.abc import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from sqlalchemy import Engine, String, create_engine, make_url
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Mapped, Session, mapped_column, scoped_session, sessionmaker
from testcontainers.postgres import PostgresContainer


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
def init_db(engine: Engine) -> None:
    from mixemy import models

    class AsyncItemModel(models.IdAuditModel):
        __table_args__ = {"extend_existing": True}  # noqa: RUF012
        value: Mapped[str] = mapped_column(String)

    class ItemModel(models.IdAuditModel):
        __table_args__ = {"extend_existing": True}  # noqa: RUF012
        value: Mapped[str] = mapped_column(String)
        nullable_value: Mapped[str | None] = mapped_column(String, nullable=True)

    ItemModel.__table__.create(bind=engine)  # type: ignore - Only for testing
    AsyncItemModel.__table__.create(bind=engine)  # type: ignore - Only for testing
