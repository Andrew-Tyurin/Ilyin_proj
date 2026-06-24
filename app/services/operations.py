from datetime import date, datetime, time
from decimal import Decimal
from io import BytesIO
from typing import Callable, Awaitable
from zoneinfo import ZoneInfo

from app.contracts.render_files_interface import InterfaceFilesPDF
from app.contracts.repository_operations import AbstractRepositoryOperation, AbstractRepositoryOperationHistory
from app.contracts.unit_of_work_interface import InterfaceUnitOfWork
from app.custom_enum import OperationOrderEnum, OperationTypeEnum, ExchangeRateProviderEnum
from app.domain.dto import OperationHistoryDTO, WalletUpdateDTO
from app.domain.entities import Operation


class ServiceOperation:
    def __init__(
            self,
            repo_operation: AbstractRepositoryOperation,
            repo_operation_history: AbstractRepositoryOperationHistory,
            exchange_func: Callable[[str, str], Awaitable[Decimal]],
            uow: InterfaceUnitOfWork,
            render_files: InterfaceFilesPDF
    ):
        self._repo_operation = repo_operation
        self._repo_operation_history = repo_operation_history
        self._exchange_func = exchange_func
        self._uow = uow
        self._render_files = render_files

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
    ) -> tuple[OperationHistoryDTO, OperationHistoryDTO, ExchangeRateProviderEnum]:
        wallets = await self._repo_operation.transfer(from_wallet, to_wallet, amount, exchange_func=self._exchange_func)
        from_wallet_updated, to_wallet_updated, provider = wallets
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
        wallets_provider = list(result)
        wallets_provider.append(provider)
        return tuple(wallets_provider)

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
            user_name: str,
            date_from: date,
            date_to: date,
            timezone: str
    ) -> BytesIO:
        tz = ZoneInfo(timezone)
        start = datetime.combine(date_from, time.min, tzinfo=tz)
        end = datetime.combine(date_to, time.max, tzinfo=tz)
        result = await self._repo_operation_history.look_history_by_date(user_id, start, end)

        for obj in result:
            timezone_datetime = obj.operation.created_at.astimezone(tz)
            obj.operation.created_at = timezone_datetime

        return self._render_files.create(result, user_name, date_from, date_to, timezone)
