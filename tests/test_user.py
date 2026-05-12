import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_users(client: AsyncClient):
    await client.post("/api/v1/users", json={"user_name": "test-1", "password": "1234"})
    response = await client.get("/api/v1/users")
    data = response.json()
    status_code = response.status_code
    assert data == [{"id": 1, "user_name": "test-1"},]
    assert status_code == 200


@pytest.mark.asyncio
async def test_not_valid_get_wallets(client: AsyncClient):
    client.headers.update({"Authorization": f"Bearer qqqwww"})
    response = await client.get("/api/v1/my/wallets/all")
    data = response.json()
    status_code = response.status_code
    assert data == {'detail': 'access-token expired or invalid'}
    assert status_code == 401
