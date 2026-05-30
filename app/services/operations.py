from decimal import Decimal
from typing import Callable

from app.contracts.repository_operations import AbstractRepositoryOperation, AbstractRepositoryOperationHistory
from app.custom_enum import OperationOrderEnum


class ServiceOperation:
    def __init__(
            self,
            repo_operation: AbstractRepositoryOperation,
            repo_operation_history: AbstractRepositoryOperationHistory,
            exchange_func: Callable[[str, str], Decimal]
    ):
        self._repo_operation = repo_operation
        self._repo_operation_history = repo_operation_history
        self._exchange_func = exchange_func

    async def add_income(self, user_id: int, operation: dict):
        updated_wallet = await self._repo_operation.addition(user_id, operation)
        result = await self._repo_operation_history.add_history(updated_wallet, income=True)
        return result

    async def add_expense(self, user_id: int, operation: dict):
        updated_wallet = await self._repo_operation.subtraction(user_id, operation)
        result = await self._repo_operation_history.add_history(updated_wallet, expense=True)
        return result

    async def transfer_between_wallets(self, user_id: int, transfer_wallets: dict):
        from_wallet, to_wallet = await self._repo_operation.transfer(
            user_id,
            transfer_wallets,
            exchange_func=self._exchange_func
        )
        result = await self._repo_operation_history.add_transfer_history_between(from_wallet, to_wallet)
        return result

    async def get_operations_history(
            self,
            user_id: int,
            wallet_id: int | None,
            order_by_data: OperationOrderEnum,
            limit: int | None
    ):
        return await self._repo_operation_history.get_history(user_id, wallet_id, order_by_data, limit)
