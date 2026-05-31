from decimal import Decimal
from typing import Callable, Awaitable

from fastapi import HTTPException
from sqlalchemy import update, and_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.contracts.repository_operations import AbstractRepositoryOperation, AbstractRepositoryOperationHistory
from app.custom_enum import OperationTypeEnum, OperationOrderEnum
from app.infrastructure.sqlalchemy_models import WalletORM, OperationWalletORM


def raise_404(name_value: str, value: int | str):
    raise HTTPException(status_code=404, detail=f"Wallet '{name_value}={value}' not found")


class SqlAlchemyRepositoryOperation(AbstractRepositoryOperation):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def addition(self, user_id: int, operation: dict):
        wallet_id = operation.get("wallet_id")
        amount = operation.get("amount")
        description = operation.get("description")

        stmt = await self._session.execute(
            update(WalletORM)
            .where(and_(WalletORM.id == wallet_id, WalletORM.user_id == user_id))
            .values(balance=WalletORM.balance + amount)
            .returning(WalletORM.name, WalletORM.currency)
        )
        result = stmt.one_or_none()

        if result is None:
            raise raise_404("wallet_id", wallet_id)

        return {
            "wallet_id": wallet_id,
            "wallet_name": result.name,
            "currency": result.currency,
            "amount": amount,
            "description": description
        }

    async def subtraction(self, user_id: int, operation: dict):
        wallet_id = operation.get("wallet_id")
        amount = operation.get("amount")
        description = operation.get("description")

        try:
            stmt = await self._session.execute(
                update(WalletORM)
                .where(and_(WalletORM.id == wallet_id, WalletORM.user_id == user_id))
                .values(balance=WalletORM.balance - amount)
                .returning(WalletORM.name, WalletORM.currency)
            )
            result = stmt.one_or_none()
        except IntegrityError as e:
            raise HTTPException(status_code=400, detail=f"Problem updating object {wallet_id=}\n{e.args[0]}")

        if result is None:
            raise raise_404("wallet_id", wallet_id)

        return {
            "wallet_id": wallet_id,
            "wallet_name": result.name,
            "currency": result.currency,
            "amount": amount,
            "description": description,
        }

    async def transfer(self, user_id: int, transfer_wallets: dict, **kwargs):
        from_wallet_id = transfer_wallets.get("from_wallet_id")
        to_wallet_id = transfer_wallets.get("to_wallet_id")
        amount = transfer_wallets.get("amount")
        exchange_func: Callable[[str, str], Awaitable[Decimal]] = kwargs.get("exchange_func")

        from_wallet = await self._session.scalar(
            select(WalletORM)
            .where(and_(WalletORM.id == from_wallet_id, WalletORM.user_id == user_id))
        )
        to_wallet = await self._session.scalar(
            select(WalletORM)
            .where(and_(WalletORM.id == to_wallet_id, WalletORM.user_id == user_id))
        )

        if not from_wallet:
            raise raise_404("from_wallet_id", from_wallet_id)

        if not to_wallet:
            raise raise_404("to_wallet_id", to_wallet_id)

        rate = await exchange_func(from_wallet.currency, to_wallet.currency)
        serialized_amount = round(amount * rate, 2)

        try:
            from_wallet.balance -= amount
            to_wallet.balance += serialized_amount
            await self._session.flush()
        except IntegrityError as e:
            raise HTTPException(status_code=400, detail=f"Problem updating object:\n{e.args[0]}")

        return (
            {
                "wallet_id": from_wallet.id,
                "wallet_name": from_wallet.name,
                "currency": from_wallet.currency,
                "amount": amount,
                "description": f"transfer into wallet_id={to_wallet.id}",
            },
            {
                "wallet_id": to_wallet.id,
                "wallet_name": to_wallet.name,
                "currency": to_wallet.currency,
                "amount": serialized_amount,
                "description": f"transfer from wallet_id={from_wallet.id}",
            },
        )


class SqlAlchemyRepositoryOperationHistory(AbstractRepositoryOperationHistory):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add_history(self, updated_wallet: dict, income: bool = False, expense: bool = False):
        if income + expense != 1:
            raise ValueError("There must be only Income or Expense")

        wallet_id = updated_wallet.get("wallet_id")
        wallet_name = updated_wallet.get("wallet_name")
        amount = updated_wallet.get("amount")
        description = updated_wallet.get("description")
        currency = updated_wallet.get("currency")
        operation_type = OperationTypeEnum.INCOME if income else OperationTypeEnum.EXPENSE

        operation_orm = OperationWalletORM(
            wallet_id=wallet_id,
            type=operation_type,
            amount=amount,
            description=description,
        )
        self._session.add(operation_orm)
        await self._session.commit()

        wallet_operation = {
            "wallet_id": wallet_id,
            "wallet_name": wallet_name,
            "currency": currency,
            "operation": {
                "id": operation_orm.id,
                "type": operation_orm.type,
                "amount": operation_orm.amount,
                "description": operation_orm.description,
                "created_at": operation_orm.created_at,
            }
        }
        return wallet_operation

    async def get_history(
            self,
            user_id: int,
            wallet_id: int | None,
            order_by_data: OperationOrderEnum,
            limit: int | None
    ):
        stmt = (
            select(
                OperationWalletORM.wallet_id,
                WalletORM.name,
                WalletORM.currency,
                OperationWalletORM.id,
                OperationWalletORM.type,
                OperationWalletORM.amount,
                OperationWalletORM.description,
                OperationWalletORM.created_at,
            )
            .join(OperationWalletORM.wallet)
            .where(WalletORM.user_id == user_id)
        )

        if wallet_id:
            stm = (
                select(WalletORM.id)
                .where(and_(WalletORM.id == wallet_id, WalletORM.user_id == user_id))
                .exists()
            )
            result_bool = await self._session.scalar(select(stm))
            if not result_bool:
                raise raise_404("wallet_id", wallet_id)

            stmt = stmt.where(OperationWalletORM.wallet_id == wallet_id)

        if limit:
            stmt = stmt.limit(limit)

        if order_by_data == OperationOrderEnum.DECREASE:
            stmt = stmt.order_by(OperationWalletORM.created_at.desc())
        else:
            stmt = stmt.order_by(OperationWalletORM.created_at.asc())

        rows = (await self._session.execute(stmt)).all()

        def dto(obj):
            return {
                "wallet_id": obj.wallet_id,
                "wallet_name": obj.name,
                "currency": obj.currency,
                "operation": {
                    "id": obj.id,
                    "type": obj.type,
                    "amount": obj.amount,
                    "description": obj.description,
                    "created_at": obj.created_at,
                }
            }

        return [dto(row) for row in rows]

    async def add_transfer_history_between(self, from_wallet: dict, to_wallet: dict):
        wallets = (
            (from_wallet, OperationTypeEnum.TRANSFER_EXPENSE),
            (to_wallet, OperationTypeEnum.TRANSFER_INCOME)
        )

        operations_full_data: list[tuple] = []

        for wallet, operation_type in wallets:
            wallet_id = wallet.get("wallet_id")
            wallet_name = wallet.get("wallet_name")
            amount = wallet.get("amount")
            description = wallet.get("description")
            currency = wallet.get("currency")

            operation_orm = OperationWalletORM(
                wallet_id=wallet_id,
                type=operation_type,
                amount=amount,
                description=description,
            )
            self._session.add(operation_orm)
            operation_additional_data = {"wallet_id": wallet_id, "wallet_name": wallet_name, "currency": currency}
            operations_full_data.append((operation_orm, operation_additional_data))

        def dto(obj_orm, additional_data):
            return {
                "wallet_id": additional_data.get("wallet_id"),
                "wallet_name": additional_data.get("wallet_name"),
                "currency": additional_data.get("currency"),
                "operation": {
                    "id": obj_orm.id,
                    "type": obj_orm.type,
                    "amount": obj_orm.amount,
                    "description": obj_orm.description,
                    "created_at": obj_orm.created_at,
                }
            }

        await self._session.commit()
        return [dto(obj, data) for obj, data in operations_full_data]
