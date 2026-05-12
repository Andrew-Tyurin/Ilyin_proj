import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.infrastructure.sqlalchemy_db import async_drop_table, async_create_table, async_truncate_tables
from app.main import app


@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database():
    await async_drop_table()
    await async_create_table()
    yield
    await async_drop_table()


@pytest_asyncio.fixture(scope="function", autouse=True)
async def clear_database():
    yield
    await async_truncate_tables()


@pytest_asyncio.fixture
async def client(scope="function") -> AsyncClient:
    async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
    ) as async_client:
        yield async_client
