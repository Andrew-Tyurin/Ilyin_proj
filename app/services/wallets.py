from decimal import Decimal
from typing import Callable, Awaitable

from app.contracts.repository_wallets import AbstractRepositoryWallet
from app.contracts.unit_of_work_interface import InterfaceUnitOfWork
from app.custom_enum import CurrencyEnum
from app.domain.dto import WalletsTotalBalanceDTO, WalletDTO
from app.domain.entities import Wallet


class ServiceWallet:
    def __init__(
            self,
            repo: AbstractRepositoryWallet,
            exchange_func: Callable[[str, str], Awaitable[Decimal]],
            uow: InterfaceUnitOfWork,
    ):
        self._repo = repo
        self._exchange_func = exchange_func
        self._uow = uow

    async def get_total_balance(self, user_id: int, currency: CurrencyEnum) -> WalletsTotalBalanceDTO:
        return await self._repo.get_balance(user_id, currency=currency, exchange_func=self._exchange_func)

    async def get_wallet(self, user_id: int, wallet_name: str) -> WalletDTO:
        return await self._repo.get(user_id, wallet_name)

    async def get_wallets(self, user_id: int) -> list[WalletDTO]:
        return await self._repo.get_all(user_id)

    async def create_wallet(self, wallet: Wallet) -> WalletDTO:
        result = await self._repo.add(wallet)
        await self._uow.commit()
        return result
