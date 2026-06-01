from abc import ABC, abstractmethod

from app.domain.dto import WalletsTotalBalanceDTO, WalletDTO
from app.domain.entities import Wallet


class AbstractRepositoryWallet(ABC):
    @abstractmethod
    async def get_balance(self, user_id: int, **kwargs) -> WalletsTotalBalanceDTO:
        pass

    @abstractmethod
    async def get(self, user_id: int, wallet_name: str) -> WalletDTO:
        pass

    @abstractmethod
    async def get_all(self, user_id: int) -> list[WalletDTO]:
        pass

    @abstractmethod
    async def add(self, wallet: Wallet) -> WalletDTO:
        pass
