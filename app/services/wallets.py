from decimal import Decimal
from typing import Callable, Awaitable

from app.contracts.repository_wallets import AbstractRepositoryWallet
from app.custom_enum import CurrencyEnum


class ServiceWallet:
    def __init__(self, repo: AbstractRepositoryWallet, exchange_func: Callable[[str, str], Awaitable[Decimal]]):
        self._repo = repo
        self._exchange_func = exchange_func

    async def get_total_balance(self, user_id: int, currency: CurrencyEnum):
        return await self._repo.get_balance(user_id, currency=currency, exchange_func=self._exchange_func)

    async def get_wallet(self, user_id: int,  wallet_name: str):
        return await self._repo.get(user_id, wallet_name)

    async def get_wallets(self, user_id: int):
        return await self._repo.get_all(user_id)

    async def create_wallet(self, user_id: int, wallet: dict) -> dict:
        return await self._repo.add(user_id, wallet)
