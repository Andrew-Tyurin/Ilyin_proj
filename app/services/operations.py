from datetime import date, datetime, time
from decimal import Decimal
from typing import Callable, Awaitable
from zoneinfo import ZoneInfo

from app.contracts.repository_operations import AbstractRepositoryOperation, AbstractRepositoryOperationHistory
from app.contracts.unit_of_work_interface import InterfaceUnitOfWork
from app.custom_enum import OperationOrderEnum, OperationTypeEnum
from app.domain.dto import OperationHistoryDTO, WalletUpdateDTO
from app.domain.entities import Operation


class ServiceOperation:
    def __init__(
            self,
            repo_operation: AbstractRepositoryOperation,
            repo_operation_history: AbstractRepositoryOperationHistory,
            exchange_func: Callable[[str, str], Awaitable[Decimal]],
            uow: InterfaceUnitOfWork,
    ):
        self._repo_operation = repo_operation
        self._repo_operation_history = repo_operation_history
        self._exchange_func = exchange_func
        self._uow = uow

    async def add_income(self, operation: Operation, wallet: WalletUpdateDTO) -> OperationHistoryDTO:
        wallet_updated = await self._repo_operation.addition(wallet, operation.amount)
        result = await self._repo_operation_history.add_history(operation, wallet_updated)
        await self._uow.commit()
        return result

    async def add_expense(self, operation: Operation, wallet: WalletUpdateDTO) -> OperationHistoryDTO:
        wallet_updated = await self._repo_operation.subtraction(wallet, operation.amount)
        result = await self._repo_operation_history.add_history(operation, wallet_updated)
        await self._uow.commit()
        return result

    async def transfer_between_wallets(
            self,
            from_wallet: WalletUpdateDTO,
            to_wallet: WalletUpdateDTO,
            amount: Decimal
    ) -> tuple[OperationHistoryDTO, OperationHistoryDTO]:
        wallets = await self._repo_operation.transfer(from_wallet, to_wallet, amount, exchange_func=self._exchange_func)
        from_wallet_updated, to_wallet_updated = wallets
        operation_from_wallet = Operation(
            wallet_id=from_wallet_updated.id,
            amount=from_wallet_updated.balance,
            description=f"transfer into wallet_id={to_wallet.id}",
            type=OperationTypeEnum.TRANSFER_EXPENSE
        )
        operation_to_wallet = Operation(
            wallet_id=to_wallet_updated.id,
            amount=to_wallet_updated.balance,
            description=f"transfer from wallet_id={from_wallet.id}",
            type=OperationTypeEnum.TRANSFER_INCOME
        )
        from_operation_and_wallet = (operation_from_wallet, from_wallet_updated)
        to_operation_and_wallet = (operation_to_wallet, to_wallet_updated)
        result = await self._repo_operation_history.add_transfer_history_between(
            from_operation_and_wallet,
            to_operation_and_wallet
        )
        await self._uow.commit()
        return result

    async def get_operations_history(
            self,
            user_id: int,
            wallet_id: int | None,
            order_by_data: OperationOrderEnum,
            limit: int,
            offset: int
    ) -> list[OperationHistoryDTO]:
        return await self._repo_operation_history.get_history(
            user_id,
            wallet_id,
            order_by_data,
            limit=limit,
            offset=offset
        )

    async def crete_file_containing_operations(
            self,
            user_id: int,
            date_from: date,
            date_to: date,
            timezone: str
    ) -> list[OperationHistoryDTO]:
        tz = ZoneInfo(timezone)
        start = datetime.combine(date_from, time.min, tzinfo=tz)
        end = datetime.combine(date_to, time.max, tzinfo=tz)
        result = await self._repo_operation_history.look_history_by_date(user_id, start, end)
        return result
