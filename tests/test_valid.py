from datetime import date
from unittest.mock import patch

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
    user1_create_wallet_rub,
    user1_result_create_wallet1,
    user1_read_balance_zero_wallets,
    user1_result_wallet1,
    user1_result_wallet2,
    user1_update_wallet1_add_income,
    user1_update_wallet1_add_expense,
    user1_result_update_wallet1_add_income,
    user1_result_update_wallet1_add_expense,
    user1_read_balance_not_zero_wallets,
    user1_transfer_between,
    user1_result_transfer_between_from_wallet2,
    user1_result_transfer_between_to_wallet1,
    user1_result_read_operation_income_wallet1,
    user1_result_read_operation_income_wallet2,
)
from tests.substitute_functions import get_exchange_rate_replacement


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
    async def test_get_token_info(self, async_client_and_authorized_user_and_wallets: AsyncClient):
        response = await async_client_and_authorized_user_and_wallets.get(
            "/api/v1/users/authorization/my/token-info"
        )
        data = response.json()
        expected_result = user1_read_payload_jwt.model_dump()
        await self.type_value_check(expected_result, data)
        assert response.status_code == status_code_200


class TestValidWallet:
    @pytest.mark.asyncio
    async def test_create_wallet(self, async_client: AsyncClient, token_user: str):
        response = await async_client.post(
            "/api/v1/my/wallets",
            json=user1_create_wallet_rub.model_dump(),
            headers={"Authorization": f"Bearer {token_user}"}
        )
        data = response.json()
        expected_result = user1_result_create_wallet1.model_dump()
        assert expected_result == data
        assert response.status_code == status_code_201

    @pytest.mark.asyncio
    async def test_read_wallet(self, async_client_and_authorized_user_and_wallets: AsyncClient):
        response = await async_client_and_authorized_user_and_wallets.get(
            f"/api/v1/my/wallets/one/{user1_result_wallet1.name}"
        )
        data = response.json()
        assert data == user1_result_wallet1.model_dump()
        assert response.status_code == status_code_200

    @pytest.mark.asyncio
    async def test_read_wallets_balance(self, async_client_and_authorized_user_and_wallets: AsyncClient):
        with patch("app.api.v1.dependencies.get_exchange_rate", new=get_exchange_rate_replacement):
            response = await async_client_and_authorized_user_and_wallets.get("/api/v1/my/wallets/balances")
            data = response.json()
            assert data == user1_read_balance_zero_wallets.model_dump()
            assert response.status_code == status_code_200

    @pytest.mark.asyncio
    async def test_read_wallets_balance_not_zero(self, async_client_and_authorized_user_and_full_wallets: AsyncClient):
        with patch("app.api.v1.dependencies.get_exchange_rate", new=get_exchange_rate_replacement):
            response = await async_client_and_authorized_user_and_full_wallets.get("/api/v1/my/wallets/balances")
            data = response.json()
            assert data == user1_read_balance_not_zero_wallets.model_dump()
            assert response.status_code == status_code_200

    @pytest.mark.asyncio
    async def test_read_wallets_all(self, async_client_and_authorized_user_and_wallets: AsyncClient):
        response = await async_client_and_authorized_user_and_wallets.get("/api/v1/my/wallets/all")
        data = response.json()
        assert data == [user1_result_wallet1.model_dump(), user1_result_wallet2.model_dump()]
        assert response.status_code == status_code_200


class TestValidWalletOperations:
    @pytest.mark.asyncio
    async def test_wallet1_add_income(self, async_client_and_authorized_user_and_wallets: AsyncClient):
        response = await async_client_and_authorized_user_and_wallets.patch(
            "/api/v1/my/wallets/operations/income",
            json=user1_update_wallet1_add_income.model_dump()
        )
        data = response.json()
        expected_result = user1_result_update_wallet1_add_income.model_dump()
        create_at_data = data['operation'].pop('created_at', None)
        create_at_expected_result = str(expected_result['operation'].pop('created_at', None))
        assert type(create_at_data) == type(create_at_expected_result)
        assert data == expected_result
        assert response.status_code == status_code_200

    @pytest.mark.asyncio
    async def test_wallet1_add_expense(self, async_client_and_authorized_user_and_full_wallets: AsyncClient):
        response = await async_client_and_authorized_user_and_full_wallets.patch(
            "/api/v1/my/wallets/operations/expense",
            json=user1_update_wallet1_add_expense.model_dump()
        )
        data = response.json()
        expected_result = user1_result_update_wallet1_add_expense.model_dump()
        create_at_data = data['operation'].pop('created_at', None)
        create_at_expected_result = str(expected_result['operation'].pop('created_at', None))
        assert type(create_at_data) == type(create_at_expected_result)
        assert data == expected_result
        assert response.status_code == status_code_200

    @pytest.mark.asyncio
    async def test_transfer_between_wallets(self, async_client_and_authorized_user_and_full_wallets: AsyncClient):
        with patch("app.api.v1.dependencies.get_exchange_rate", new=get_exchange_rate_replacement):
            response = await async_client_and_authorized_user_and_full_wallets.patch(
                "/api/v1/my/wallets/operations/transfer",
                json=user1_transfer_between.model_dump()
            )
            data = response.json()
            expected_result = {
                "from_wallet": user1_result_transfer_between_from_wallet2.model_dump(),
                "to_wallet": user1_result_transfer_between_to_wallet1.model_dump(),
            }
            assert response.status_code == status_code_200
            for came_data, expected_data in zip(data.values(), expected_result.values()):
                create_at_data = came_data['operation'].pop('created_at', None)
                create_at_expected = str(expected_data['operation'].pop('created_at', None))
                assert type(create_at_data) == type(create_at_expected)
                assert came_data == expected_data

    @pytest.mark.asyncio
    async def test_get_operations_decrease(self, async_client_and_authorized_user_and_full_wallets: AsyncClient):
        response = await async_client_and_authorized_user_and_full_wallets.get(
            "/api/v1/my/wallets/operations/history"
        )
        data = response.json()
        expected_data_tuple = (
            user1_result_read_operation_income_wallet2.model_dump(),
            user1_result_read_operation_income_wallet1.model_dump()
        )

        assert response.status_code == status_code_200
        for came_data, expected_data in zip(data, expected_data_tuple):
            create_at_data = came_data['operation'].pop('created_at', None)
            create_at_expected = str(expected_data['operation'].pop('created_at', None))
            assert type(create_at_data) == type(create_at_expected)
            assert came_data == expected_data

    @pytest.mark.asyncio
    async def test_get_operations_increase(self, async_client_and_authorized_user_and_full_wallets: AsyncClient):
        response = await async_client_and_authorized_user_and_full_wallets.get(
            "/api/v1/my/wallets/operations/history?order_by_data=increase"
        )
        data = response.json()
        expected_data_tuple = (
            user1_result_read_operation_income_wallet1.model_dump(),
            user1_result_read_operation_income_wallet2.model_dump()
        )

        assert response.status_code == status_code_200
        for came_data, expected_data in zip(data, expected_data_tuple):
            create_at_data = came_data['operation'].pop('created_at', None)
            create_at_expected = str(expected_data['operation'].pop('created_at', None))
            assert type(create_at_data) == type(create_at_expected)
            assert came_data == expected_data

    @pytest.mark.asyncio
    async def test_get_operation_wallet_usd(self, async_client_and_authorized_user_and_full_wallets: AsyncClient):
        response = await async_client_and_authorized_user_and_full_wallets.get(
            "/api/v1/my/wallets/operations/history?wallet_id=2"
        )
        data = response.json()
        expected_data_tuple = (user1_result_read_operation_income_wallet2.model_dump(),)

        assert response.status_code == status_code_200
        for came_data, expected_data in zip(data, expected_data_tuple):
            create_at_data = came_data['operation'].pop('created_at', None)
            create_at_expected = str(expected_data['operation'].pop('created_at', None))
            assert type(create_at_data) == type(create_at_expected)
            assert came_data == expected_data

    @pytest.mark.asyncio
    async def test_download_operations_pdf(self, async_client_and_authorized_user_and_full_wallets: AsyncClient):
        date_from = date.today()
        date_to = date.today()
        timezone = "Europe/Moscow"
        response = await async_client_and_authorized_user_and_full_wallets.get(
            "/api/v1/my/wallets/operations/download",
            params={"date_from": date_from, "date_to": date_to, "timezone": timezone}
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert "attachment" in response.headers["content-disposition"]
        assert response.content.startswith(b"%PDF")
