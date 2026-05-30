from decimal import Decimal
from typing import Callable

from app.contracts.repository_wallets import AbstractRepositoryWallet
from app.custom_enum import CurrencyEnum


class ServiceWallet:
    def __init__(self, repo: AbstractRepositoryWallet, exchange_func: Callable[[str, str], Decimal]):
        self._repo = repo
        self._exchange_func = exchange_func

    async def get_balance(
            self,
            user_id: int,
            wallet_name: str | None = None,
            show_total_balance_in_currency: CurrencyEnum | None = None
    ) -> dict:
        currency = CurrencyEnum.RUB if show_total_balance_in_currency is None else show_total_balance_in_currency
        return await self._repo.get(
            user_id,
            wallet_name,
            currency=currency,
            exchange_func=self._exchange_func
        )

    async def get_wallets(self, user_id: int):
        return await self._repo.get_all(user_id)

    async def create_wallet(self, user_id: int, wallet: dict) -> dict:
        return await self._repo.add(user_id, wallet)
