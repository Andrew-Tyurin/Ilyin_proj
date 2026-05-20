from typing import AsyncGenerator

import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.api.v1.dependencies import InstanceJWTokenService, Token
from app.infrastructure.hashing import HashArgon2
from app.infrastructure.sqlalchemy_db import (
    async_drop_table,
    async_create_table,
    async_truncate_tables,
    AsyncSessionLocal
)
from app.infrastructure.sqlalchemy_models import UserORM, WalletORM
from app.main import app
from moc_data.valid_moc_data import create_user1, create_user2, user1_create_wallet1, user1_create_wallet2
from tests.moc_data.user_moc import CreateUserDataclassMoc
from tests.moc_data.wallet_moc import CreateWalletDataclassMoc


async def get_user_orm(user: CreateUserDataclassMoc, hash_argon2: HashArgon2) -> UserORM:
    password_hash = hash_argon2.hash(user.password)
    user_dict = user.model_dump()
    user_dict["password"] = password_hash
    return UserORM(**user_dict)


async def get_wallet_orm(user_id: int, wallet: CreateWalletDataclassMoc) -> WalletORM:
    wallet_dict = wallet.model_dump()
    wallet_dict["balance"] = wallet_dict.pop("initial_balance")
    return WalletORM(**wallet_dict, user_id=user_id)


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
async def hash_argon2() -> HashArgon2:
    return HashArgon2()


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
    ) as async_client:
        yield async_client


@pytest_asyncio.fixture
async def async_client_and_existing_users(
        async_client: AsyncClient,
        hash_argon2: HashArgon2
) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncSessionLocal() as session:
        for user in (create_user1, create_user2):
            user_orm = await get_user_orm(user, hash_argon2)
            session.add(user_orm)
        await session.commit()

    yield async_client


@pytest_asyncio.fixture
async def token_user(hash_argon2: HashArgon2) -> Token:
    async with AsyncSessionLocal() as session:
        user_orm = await get_user_orm(create_user1, hash_argon2)
        session.add(user_orm)
        await session.commit()
    data_for_payload = {"id": user_orm.id, "user_name": user_orm.user_name}
    return InstanceJWTokenService.encode_token(data_for_payload)


@pytest_asyncio.fixture
async def token_user_and_existing_wallets(token_user: Token) -> Token:
    payload = InstanceJWTokenService.decode_token(token_user)
    user_id = payload.get("sub")

    async with AsyncSessionLocal() as session:
        for wallet in (user1_create_wallet1, user1_create_wallet2):
            wallet_orm = await get_wallet_orm(user_id, wallet)
            session.add(wallet_orm)
        await session.commit()

    return token_user


@pytest_asyncio.fixture
async def async_client_and_authorized_user(
        async_client: AsyncClient,
        token_user_and_existing_wallets: Token,
) -> AsyncGenerator[AsyncClient, None]:
    async_client.headers.update(
        {"Authorization": f"Bearer {token_user_and_existing_wallets}"}
    )
    yield async_client
