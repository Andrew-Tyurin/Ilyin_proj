import pytest
from httpx import AsyncClient

from tests.moc_data.valid_moc_data import (
    read_user1,
    read_user2,
    create_user1,
    result_create_user1,
    user1_read_authorization,
    user1_read_payload_jwt,
    status_code_200,
    status_code_201,
    user1_create_wallet1,
    user1_result_create_wallet1,
    user1_read_sum_balance_wallets,
    user1_result_wallet1,
    user1_read_wallets_moc,
    user1_update_wallet1_add_income,
    user1_update_wallet1_add_expense,
    user1_result_update_wallet1_add_income,
    user1_result_update_wallet1_add_expense,
    Wallet1User1,
)


class TestValidUser:
    async def type_value_check(self, expected: dict, data: dict):
        """
        Если не возможно сравнить два словаря, например: токен,
        который каждый раз создаётся новый и за мокировать его
        нельзя, тогда просто сравниваем тип значения ключа.
        """
        for expected_key_value, data_key_value in zip(expected.items(), data.items()):
            assert expected_key_value[0] == data_key_value[0]
            assert type(expected_key_value[1]) == type(data_key_value[1])

    @pytest.mark.asyncio
    async def test_get_users(self, async_client_and_existing_users: AsyncClient):
        response = await async_client_and_existing_users.get("/api/v1/users")
        data = response.json()
        assert data == [read_user1.model_dump(), read_user2.model_dump()]
        assert response.status_code == status_code_200

    @pytest.mark.asyncio
    async def test_get_user(self, async_client_and_existing_users: AsyncClient):
        response = await async_client_and_existing_users.get("/api/v1/users/1")
        data = response.json()
        assert data == read_user1.model_dump()
        assert response.status_code == status_code_200

    @pytest.mark.asyncio
    async def test_create_users(self, async_client: AsyncClient):
        response = await async_client.post(
            "/api/v1/users",
            json=create_user1.model_dump()
        )
        data = response.json()
        expected_result = result_create_user1.model_dump()
        await self.type_value_check(expected_result, data)
        assert response.status_code == status_code_201

    @pytest.mark.asyncio
    async def test_authorization(self, async_client_and_existing_users: AsyncClient):
        response = await async_client_and_existing_users.post(
            "/api/v1/users/authorization",
            json=create_user1.model_dump()
        )
        data = response.json()
        expected_result = user1_read_authorization.model_dump()
        await self.type_value_check(expected_result, data)
        assert response.status_code == status_code_200

    @pytest.mark.asyncio
    async def test_get_token_info(self, async_client_and_authorized_user: AsyncClient):
        response = await async_client_and_authorized_user.get(
            "/api/v1/users/authorization/my/token-info"
        )
        data = response.json()
        expected_result = user1_read_payload_jwt.model_dump()
        await self.type_value_check(expected_result, data)
        assert response.status_code == status_code_200


class TestValidWallet:
    @pytest.mark.asyncio
    async def test_create_wallet(self, async_client: AsyncClient, token_user):
        response = await async_client.post(
            "/api/v1/my/wallets",
            json=user1_create_wallet1.model_dump(),
            headers={"Authorization": f"Bearer {token_user}"}
        )
        data = response.json()
        expected_result = user1_result_create_wallet1.model_dump()
        assert expected_result == data
        assert response.status_code == status_code_201

    @pytest.mark.asyncio
    async def test_read_wallet(self, async_client_and_authorized_user: AsyncClient):
        response = await async_client_and_authorized_user.get(
            f"/api/v1/my/wallets/balances?wallet_name={Wallet1User1.name}"
        )
        data = response.json()
        assert data == user1_result_wallet1.model_dump()
        assert response.status_code == status_code_200

    @pytest.mark.asyncio
    async def test_read_wallets_balance(self, async_client_and_authorized_user: AsyncClient):
        response = await async_client_and_authorized_user.get("/api/v1/my/wallets/balances")
        data = response.json()
        assert data == user1_read_sum_balance_wallets.model_dump()
        assert response.status_code == status_code_200

    @pytest.mark.asyncio
    async def test_read_wallets_all(self, async_client_and_authorized_user: AsyncClient):
        response = await async_client_and_authorized_user.get("/api/v1/my/wallets/all")
        data = response.json()
        assert data == user1_read_wallets_moc.model_dump()
        assert response.status_code == status_code_200


class TestValidWalletOperations:
    @pytest.mark.asyncio
    async def test_wallet_add_income(self, async_client_and_authorized_user: AsyncClient):
        response = await async_client_and_authorized_user.patch(
            "/api/v1/my/wallets/operations/income",
            json=user1_update_wallet1_add_income.model_dump()
        )
        data = response.json()
        assert data == user1_result_update_wallet1_add_income.model_dump()
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_wallet_add_expense(self, async_client_and_authorized_user: AsyncClient):
        response = await async_client_and_authorized_user.patch(
            "/api/v1/my/wallets/operations/expense",
            json=user1_update_wallet1_add_expense.model_dump()
        )
        data = response.json()
        assert data == user1_result_update_wallet1_add_expense.model_dump()
        assert response.status_code == 200
