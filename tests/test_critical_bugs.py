"""
Дополнительные тесты поведения приложения: конкурентные запросы,
граничные случаи авторизации, устойчивость к недоступности внешнего API.

Каждый тест описывает ожидаемое КОРРЕКТНОЕ поведение системы.
Если тест красный — значит приложение в этом сценарии ведёт себя
неправильно. Разберись, что именно происходит и почему, прежде чем
что-то менять: у каждого падения есть конкретная причина в коде.

Подсказка общего характера: обрати внимание, что несколько запросов
могут выполняться ОДНОВРЕМЕННО, и подумай, что в этот момент видит
каждый из них.
"""
import asyncio
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from time import perf_counter
from typing import AsyncGenerator
from unittest.mock import patch

import jwt as pyjwt
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.api.v1.dependencies import InstanceJWToken, Token
from app.config_app import JWTokenSettings
from app.custom_enum import CurrencyEnum, ExchangeRateProviderEnum
from app.domain.rules import WalletRules
from app.infrastructure import exchange_rate
from app.infrastructure.sqlalchemy_db import AsyncSessionLocal
from app.infrastructure.sqlalchemy_models import WalletORM
from app.main import app
from tests.substitute_functions import slow_convert_one_to_one

TRANSFER_URL = "/api/v1/my/wallets/operations/transfer"
HISTORY_URL = "/api/v1/my/wallets/operations/history"
WALLETS_ALL_URL = "/api/v1/my/wallets/all"
WALLETS_URL = "/api/v1/my/wallets"
USERS_URL = "/api/v1/users"
TOKEN_INFO_URL = "/api/v1/users/authorization/my/token-info"

PATCH_EXCHANGE_TARGET = "app.api.v1.dependencies.convert_using_exchange_rate"


@pytest_asyncio.fixture
async def tolerant_client() -> AsyncGenerator[AsyncClient, None]:
    """
    Клиент, который возвращает ошибки приложения как HTTP-ответы
    (в том числе 500), а не пробрасывает исключения в тест.
    """
    async with AsyncClient(
            transport=ASGITransport(app=app, raise_app_exceptions=False),
            base_url="http://test"
    ) as client:
        yield client


@pytest_asyncio.fixture
async def seed_two_rub_wallets(token_user: Token):
    """Фабрика: создаёт пару RUB-кошельков с заданными балансами, возвращает их id."""
    payload = InstanceJWToken.decode_token(token_user)
    user_id = payload.sub

    async def _seed(balance_a: str, balance_b: str) -> tuple[int, int]:
        async with AsyncSessionLocal() as session:
            wallet_a = WalletORM(
                name="rub_a", currency=CurrencyEnum.RUB,
                balance=Decimal(balance_a), user_id=user_id,
            )
            wallet_b = WalletORM(
                name="rub_b", currency=CurrencyEnum.RUB,
                balance=Decimal(balance_b), user_id=user_id,
            )
            session.add_all([wallet_a, wallet_b])
            await session.commit()
        return wallet_a.id, wallet_b.id

    return token_user, _seed


async def get_balances(client: AsyncClient, headers: dict) -> dict[int, Decimal]:
    response = await client.get(WALLETS_ALL_URL, headers=headers)
    assert response.status_code == 200
    return {w["id"]: Decimal(w["balance"]) for w in response.json()}


class TestConcurrentTransfers:
    """На кошельке 100.00. Пять пользовательских вкладок одновременно
    отправляют перевод по 30.00. Сколько переводов ДОЛЖНО пройти?"""

    @pytest.mark.asyncio
    async def test_concurrent_transfers_preserve_money(
            self, tolerant_client: AsyncClient, seed_two_rub_wallets
    ):
        token, seed = seed_two_rub_wallets
        from_id, to_id = await seed("100.00", "0.00")
        headers = {"Authorization": f"Bearer {token}"}
        body = {"from_wallet_id": from_id, "to_wallet_id": to_id, "amount": "30.00"}

        with patch(PATCH_EXCHANGE_TARGET, new=slow_convert_one_to_one):
            responses = await asyncio.gather(*[
                tolerant_client.patch(TRANSFER_URL, json=body, headers=headers)
                for _ in range(5)
            ])

        ok_count = sum(1 for r in responses if r.status_code == 200)
        balances = await get_balances(tolerant_client, headers)

        assert all(r.status_code < 500 for r in responses), \
            [r.status_code for r in responses]
        assert ok_count <= 3, \
            f"успешных переводов по 30.00 при балансе 100.00: {ok_count}"
        assert balances[from_id] == Decimal("100.00") - Decimal("30.00") * ok_count, \
            f"итоговый баланс отправителя {balances[from_id]} не сходится с числом успешных переводов ({ok_count})"
        assert balances[to_id] == Decimal("30.00") * ok_count, \
            f"итоговый баланс получателя {balances[to_id]} не сходится с числом успешных переводов ({ok_count})"
        assert balances[from_id] >= 0

        # на каждый успешный перевод — ровно две записи истории (расход + доход)
        history = await tolerant_client.get(
            HISTORY_URL, params={"limit": 30}, headers=headers
        )
        assert len(history.json()) == 2 * ok_count


class TestCounterTransfers:
    """Два кошелька по 1000.00. Одновременно уходят встречные переводы
    по 10.00: A -> B и B -> A. Денег в избытке — есть ли хоть одна
    легитимная причина отклонить какой-то из этих переводов?"""

    @pytest.mark.asyncio
    async def test_counter_transfers_all_succeed(
            self, tolerant_client: AsyncClient, seed_two_rub_wallets
    ):
        token, seed = seed_two_rub_wallets
        wallet_a, wallet_b = await seed("1000.00", "1000.00")
        headers = {"Authorization": f"Bearer {token}"}
        a_to_b = {"from_wallet_id": wallet_a, "to_wallet_id": wallet_b, "amount": "10.00"}
        b_to_a = {"from_wallet_id": wallet_b, "to_wallet_id": wallet_a, "amount": "10.00"}

        status_codes = []
        with patch(PATCH_EXCHANGE_TARGET, new=slow_convert_one_to_one):
            for _ in range(5):
                responses = await asyncio.gather(
                    tolerant_client.patch(TRANSFER_URL, json=a_to_b, headers=headers),
                    tolerant_client.patch(TRANSFER_URL, json=b_to_a, headers=headers),
                )
                status_codes += [r.status_code for r in responses]

        assert all(code == 200 for code in status_codes), (
            f"часть встречных переводов отклонена, хотя средств достаточно: {status_codes}. "
            f"Присмотрись к тексту ошибки, которую получает клиент: она правдива? "
            f"И к тому, какие исключения и где перехватываются по пути."
        )

        # одинаковое число успешных переводов туда и обратно при курсе 1:1
        # обязано вернуть балансы к исходным значениям
        balances = await get_balances(tolerant_client, headers)
        assert balances[wallet_a] == Decimal("1000.00")
        assert balances[wallet_b] == Decimal("1000.00")


class TestConcurrentWalletCreation:
    """У пользователя занято 19 слотов из 20. Он делает 10 одновременных
    запросов на создание кошелька. Сколько кошельков у него должно быть
    в итоге?"""

    @pytest.mark.asyncio
    async def test_concurrent_wallet_creation_respects_limit(
            self, tolerant_client: AsyncClient, token_user: Token
    ):
        limit = WalletRules.max_amount_wallets
        payload = InstanceJWToken.decode_token(token_user)
        headers = {"Authorization": f"Bearer {token_user}"}

        async with AsyncSessionLocal() as session:
            session.add_all([
                WalletORM(
                    name=f"seeded_{i}", currency=CurrencyEnum.RUB,
                    balance=Decimal("0.00"), user_id=payload.sub,
                )
                for i in range(limit - 1)
            ])
            await session.commit()

        responses = await asyncio.gather(*[
            tolerant_client.post(
                WALLETS_URL, json={"name": f"racer_{i}", "currency": "rub"},
                headers=headers,
            )
            for i in range(10)
        ])

        created = sum(1 for r in responses if r.status_code == 201)
        balances = await get_balances(tolerant_client, headers)

        assert len(balances) <= limit, \
            f"у пользователя оказалось {len(balances)} кошельков при лимите {limit}"
        assert created <= 1, \
            f"создано {created} кошелька, хотя свободный слот был один"


class TestTokenRobustness:
    """Клиент может прислать какой угодно токен — в том числе корректно
    подписанный, но с неожиданным содержимым. Любой невалидный токен —
    это ошибка КЛИЕНТА. Каким статус-кодом отвечают на ошибки клиента,
    а каким — на ошибки сервера?"""

    @staticmethod
    def make_signed_token(sub: str) -> str:
        issued_at = datetime.now(timezone.utc)
        data = {
            "sub": sub,
            "user_name": "some_user",
            "iat": issued_at,
            "exp": issued_at + timedelta(minutes=5),
        }
        return pyjwt.encode(
            data, JWTokenSettings.secret_key, algorithm=JWTokenSettings.algorithm
        )

    @pytest.mark.asyncio
    async def test_unexpected_token_payload_returns_401(self, tolerant_client: AsyncClient):
        token = self.make_signed_token(sub="not-a-number")
        response = await tolerant_client.get(
            TOKEN_INFO_URL, headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 401, \
            f"ожидали 401, получили {response.status_code}"


class TestUsersEndpointAccess:
    """Какие данные приложения может видеть человек БЕЗ токена?
    Прикинь, как злоумышленник мог бы использовать каждый из открытых
    эндпоинтов."""

    @pytest.mark.asyncio
    async def test_users_list_requires_authorization(self, async_client: AsyncClient):
        response = await async_client.get(USERS_URL)
        assert response.status_code in (401, 403), \
            f"эндпоинт ответил анониму: {response.status_code}"

    @pytest.mark.asyncio
    async def test_user_by_id_requires_authorization(self, async_client: AsyncClient):
        response = await async_client.get(f"{USERS_URL}/1")
        assert response.status_code in (401, 403), \
            f"эндпоинт ответил анониму: {response.status_code}"


class TestExchangeRateCache:
    """В кэше курсов лежит свежая валидная запись USD -> RUB.
    Приложение запрашивает ДРУГУЮ пару (EUR -> RUB), а внешний API
    в этот момент недоступен. Что после этого должно остаться в кэше?"""

    @pytest.mark.asyncio
    async def test_api_failure_does_not_wipe_valid_cache(self, monkeypatch):
        valid_key = (CurrencyEnum.USD, CurrencyEnum.RUB)
        missing_key = (CurrencyEnum.EUR, CurrencyEnum.RUB)

        exchange_rate.CACHE_EXCHANGE_RATE_DICT.clear()
        exchange_rate.CACHE_EXCHANGE_RATE_DICT[valid_key] = (
            Decimal("90.00"), ExchangeRateProviderEnum.API, perf_counter()
        )
        exchange_rate.InstanceExchangeRateApiSettings.api_default_recovery_time()

        async def api_is_down(client, currency):
            raise ConnectionError

        monkeypatch.setattr(exchange_rate, "collect_cache_from_api", api_is_down)

        try:
            rate_and_provider = await exchange_rate.get_exchange_rate(*missing_key)

            assert rate_and_provider is not None
            assert valid_key in exchange_rate.CACHE_EXCHANGE_RATE_DICT, (
                "после неудачного похода в API за EUR->RUB из кэша пропала "
                "свежая валидная запись USD->RUB"
            )
        finally:
            exchange_rate.CACHE_EXCHANGE_RATE_DICT.clear()
            exchange_rate.InstanceExchangeRateApiSettings.api_default_recovery_time()
