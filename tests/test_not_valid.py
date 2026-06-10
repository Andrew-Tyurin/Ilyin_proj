from unittest.mock import patch

import pytest
from httpx import AsyncClient
from pygments.lexers import data

from tests.moc_data.not_valid_moc_data import (
    status_code_400,
    status_code_401,
    status_code_404,
    status_code_422,
    create_user_with_short_password,
    expected_short_password,
    create_user_with_empty_password,
    expected_empty_password,
    create_user_with_short_username,
    expected_short_username,
    create_user_with_empty_username,
    expected_empty_username,
    offset_negative_100,
    expected_offset_negative_100,
    expected_user_exist,
    non_user_existent_id,
    expected_user_by_non_existent_id,
    not_valid_user,
    expected_user_not_valid_data_authorization,
    user_without_password,
    expected_user_without_password,
    expected_not_valid_token,
    expected_without_token,
    non_existent_wallet_name,
    expected_without_wallet_name,
    not_valid_token,
    create_wallet_non_existent_currency,
    expected_wallet_non_existent_currency,
    expected_wallet_exist,
    wallet_add_negative_amount,
    expected_wallet_add_negative_amount,
    wallet_add_expense_greater_balance,
    wallet_add_income_greater_balance,
    expected_wallet_greater_or_less_balance,
    transfer_not_valid_between_wallets,
    expected_transfer_not_valid_between_wallets,
    transfer_wallets_insufficient_funds,
    expected_not_exist_wallet_id,
    non_existent_order_by_data,
    expected_non_existent_order_by_data,
)
from tests.moc_data.valid_moc_data import (
    create_user1,
    user1_create_wallet_rub,
)
from tests.substitute_functions import get_exchange_rate_replacement


class TestNotValidUser:
    @pytest.mark.asyncio
    async def test_create_user_with_short_password(self, async_client: AsyncClient):
        response = await async_client.post(
            "/api/v1/users",
            json=create_user_with_short_password,
        )
        data = response.json()
        assert response.status_code == status_code_422
        assert data["detail"][0] == expected_short_password

    @pytest.mark.asyncio
    async def test_create_user_with_empty_password(self, async_client: AsyncClient):
        response = await async_client.post(
            "/api/v1/users",
            json=create_user_with_empty_password,
        )
        data = response.json()
        assert response.status_code == status_code_422
        assert data["detail"][0] == expected_empty_password

    @pytest.mark.asyncio
    async def test_create_user_with_short_username(self, async_client: AsyncClient):
        response = await async_client.post(
            "/api/v1/users",
            json=create_user_with_short_username,
        )
        data = response.json()
        assert response.status_code == status_code_422
        assert data["detail"][0] == expected_short_username

    @pytest.mark.asyncio
    async def test_create_user_with_empty_username(self, async_client: AsyncClient):
        response = await async_client.post(
            "/api/v1/users",
            json=create_user_with_empty_username,
        )
        data = response.json()
        assert response.status_code == status_code_422
        assert data["detail"][0] == expected_empty_username

    @pytest.mark.asyncio
    async def test_create_user_exist(self, async_client_and_existing_users: AsyncClient):
        response = await async_client_and_existing_users.post(
            "/api/v1/users",
            json=create_user1.model_dump(),
        )
        data = response.json()
        assert response.status_code == status_code_400
        assert data["detail"] == expected_user_exist

    @pytest.mark.asyncio
    async def test_get_users_offset_negative_number(self, async_client_and_existing_users: AsyncClient):
        response = await async_client_and_existing_users.get(f"/api/v1/users?offset={offset_negative_100}")
        data = response.json()
        assert response.status_code == status_code_422
        assert data["detail"][0] == expected_offset_negative_100

    @pytest.mark.asyncio
    async def test_get_user_by_non_existent_id(self, async_client_and_existing_users: AsyncClient):
        response = await async_client_and_existing_users.get(f"/api/v1/users/{non_user_existent_id}")
        data = response.json()
        assert response.status_code == status_code_404
        assert data["detail"] == expected_user_by_non_existent_id

    @pytest.mark.asyncio
    async def test_authorization_not_valid_user(self, async_client: AsyncClient):
        response = await async_client.post(
            "/api/v1/users/authorization",
            json=not_valid_user,
        )
        data = response.json()
        assert response.status_code == status_code_400
        assert data["detail"] == expected_user_not_valid_data_authorization

    @pytest.mark.asyncio
    async def test_authorization_without_password(self, async_client: AsyncClient):
        response = await async_client.post(
            "/api/v1/users/authorization",
            json=user_without_password,
        )
        data = response.json()
        assert response.status_code == status_code_422
        assert data["detail"][0] == expected_user_without_password

    @pytest.mark.asyncio
    async def test_not_valid_token_verification(self, async_client: AsyncClient):
        response = await async_client.get(
            "/api/v1/users/authorization/my/token-info",
            headers={"Authorization": f"Bearer {not_valid_token}"},

        )
        data = response.json()
        assert response.status_code == status_code_401
        assert data["detail"] == expected_not_valid_token

    @pytest.mark.asyncio
    async def test_authorization_non_token(self, async_client: AsyncClient):
        response = await async_client.get("/api/v1/users/authorization/my/token-info")
        data = response.json()
        assert response.status_code == status_code_401
        assert data["detail"] == expected_without_token


class TestNotValidWallet:
    @pytest.mark.asyncio
    async def test_get_wallet(self, async_client_and_authorized_user_and_wallets: AsyncClient):
        response = await async_client_and_authorized_user_and_wallets.get(
            f"/api/v1/my/wallets/one/{non_existent_wallet_name}"
        )
        data = response.json()
        assert response.status_code == status_code_404
        assert data["detail"] == expected_without_wallet_name

    @pytest.mark.asyncio
    async def test_create_wallet_non_existent_currency(self, async_client: AsyncClient, token_user):
        response = await async_client.post(
            "/api/v1/my/wallets",
            json=create_wallet_non_existent_currency,
            headers={"Authorization": f"Bearer {token_user}"}
        )
        data = response.json()
        assert data["detail"][0] == expected_wallet_non_existent_currency
        assert response.status_code == status_code_422

    @pytest.mark.asyncio
    async def test_create_wallet_exist(self, async_client_and_authorized_user_and_wallets: AsyncClient):
        response = await async_client_and_authorized_user_and_wallets.post(
            "/api/v1/my/wallets",
            json=user1_create_wallet_rub.model_dump(),
        )
        data = response.json()
        assert response.status_code == status_code_400
        assert data["detail"] == expected_wallet_exist


class TestNotValidOperationsWallet:
    @pytest.mark.asyncio
    async def test_wallet_add_negative_income(self, async_client_and_authorized_user_and_wallets: AsyncClient):
        response = await async_client_and_authorized_user_and_wallets.patch(
            "/api/v1/my/wallets/operations/income",
            json=wallet_add_negative_amount,
        )
        data = response.json()
        assert response.status_code == status_code_422
        assert data["detail"][0] == expected_wallet_add_negative_amount

    @pytest.mark.asyncio
    async def test_wallet_add_negative_expense(self, async_client_and_authorized_user_and_wallets: AsyncClient):
        response = await async_client_and_authorized_user_and_wallets.patch(
            "/api/v1/my/wallets/operations/expense",
            json=wallet_add_negative_amount,
        )
        data = response.json()
        assert response.status_code == status_code_422
        assert data["detail"][0] == expected_wallet_add_negative_amount

    @pytest.mark.asyncio
    async def test_wallet_expense_not_walid(self, async_client_and_authorized_user_and_wallets: AsyncClient):
        response = await async_client_and_authorized_user_and_wallets.patch(
            "/api/v1/my/wallets/operations/expense",
            json=wallet_add_expense_greater_balance,
        )
        data = response.json()
        assert response.status_code == status_code_400
        assert data['detail'] == expected_wallet_greater_or_less_balance

    @pytest.mark.asyncio
    async def test_wallet_income_not_walid(self, async_client_and_authorized_user_and_wallets: AsyncClient):
        response = await async_client_and_authorized_user_and_wallets.patch(
            "/api/v1/my/wallets/operations/income",
            json=wallet_add_income_greater_balance,
        )
        data = response.json()
        assert response.status_code == status_code_400
        assert data['detail'] == expected_wallet_greater_or_less_balance

    @pytest.mark.asyncio
    async def test_transfer_wallets_insufficient_funds(self, async_client_and_authorized_user_and_wallets):
        with patch("app.api.v1.dependencies.get_exchange_rate", new=get_exchange_rate_replacement):
            response = await async_client_and_authorized_user_and_wallets.patch(
                "/api/v1/my/wallets/operations/transfer",
                json=transfer_wallets_insufficient_funds
            )
            data = response.json()
            assert response.status_code == status_code_400
            assert data["detail"] == expected_wallet_greater_or_less_balance

    @pytest.mark.asyncio
    async def test_transfer_from_identical_wallets(self, async_client_and_authorized_user_and_wallets):
        with patch("app.api.v1.dependencies.get_exchange_rate", new=get_exchange_rate_replacement):
            response = await async_client_and_authorized_user_and_wallets.patch(
                "/api/v1/my/wallets/operations/transfer",
                json=transfer_not_valid_between_wallets
            )
            data = response.json()
            assert response.status_code == status_code_422
            assert data["detail"][0] == expected_transfer_not_valid_between_wallets

    @pytest.mark.asyncio
    async def test_get_operation_non_existent_wallet(self, async_client_and_authorized_user_and_full_wallets: AsyncClient):
        response = await async_client_and_authorized_user_and_full_wallets.get(
            "/api/v1/my/wallets/operations/history?wallet_id=10"
        )
        data = response.json()
        assert response.status_code == status_code_404
        assert data['detail'] == expected_not_exist_wallet_id

    @pytest.mark.asyncio
    async def test_get_operation_non_existent_order_by(self, async_client_and_authorized_user_and_full_wallets: AsyncClient):
        response = await async_client_and_authorized_user_and_full_wallets.get(
            f"/api/v1/my/wallets/operations/history?order_by_data={non_existent_order_by_data}"
        )
        data = response.json()
        assert response.status_code == status_code_422
        assert data['detail'][0] == expected_non_existent_order_by_data
