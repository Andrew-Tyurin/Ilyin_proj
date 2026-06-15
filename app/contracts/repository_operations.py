from abc import ABC, abstractmethod
from decimal import Decimal

from app.domain.dto import WalletUpdateDTO, OperationHistoryDTO
from app.domain.entities import Operation, Wallet


class AbstractRepositoryOperation(ABC):
    @abstractmethod
    async def addition(self, wallet: WalletUpdateDTO, add_to_balance: Decimal) -> Wallet:
        pass

    @abstractmethod
    async def subtraction(self, wallet: WalletUpdateDTO, subtract_to_balance: Decimal) -> Wallet:
        pass

    @abstractmethod
    async def transfer(
            self,
            from_wallet: WalletUpdateDTO,
            to_wallet: WalletUpdateDTO,
            amount: Decimal, **kwargs
    ) -> tuple[Wallet, Wallet]:
        pass


class AbstractRepositoryOperationHistory(ABC):
    @abstractmethod
    async def add_history(self, operation: Operation, wallet: Wallet) -> OperationHistoryDTO:
        pass

    @abstractmethod
    async def add_transfer_history_between(
            self,
            from_operation_and_wallet: tuple[Operation, Wallet],
            to_operation_and_wallet: tuple[Operation, Wallet],
    ) -> tuple[OperationHistoryDTO, OperationHistoryDTO]:
        pass

    @abstractmethod
    async def get_history(
            self,
            user_id: int,
            wallet_id: int | None,
            order_by_data: str
    ) -> list[OperationHistoryDTO]:
        pass
