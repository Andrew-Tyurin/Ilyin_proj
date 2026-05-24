from fastapi import HTTPException
from sqlalchemy import update, and_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.contracts.repository_operations import AbstractRepositoryOperation, AbstractRepositoryOperationHistory
from app.custom_enum import OperationEnum, OperationOrderEnum
from app.infrastructure.sqlalchemy_models import WalletORM, OperationWalletORM


class SqlAlchemyRepositoryOperation(AbstractRepositoryOperation):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def addition(self, user_id: int, operation: dict):
        wallet_name = operation.get("wallet_name")
        amount = operation.get("amount")
        description = operation.get("description")

        stmt = await self._session.execute(
            update(WalletORM)
            .where(and_(WalletORM.name == wallet_name, WalletORM.user_id == user_id))
            .values(balance=WalletORM.balance + amount)
            .returning(WalletORM.id, WalletORM.currency)  # что вернуть после обновления
        )
        result = stmt.one_or_none()

        if result is None:
            raise HTTPException(status_code=404, detail=f"Wallet '{wallet_name}' not found")
        await self._session.flush()

        return {
            "wallet_id": result.id,
            "wallet_name": wallet_name,
            "currency": result.currency,
            "amount": amount,
            "description": description
        }

    async def subtraction(self, user_id: int, operation: dict):
        wallet_name = operation.get("wallet_name")
        amount = operation.get("amount")
        description = operation.get("description")

        try:
            stmt = await self._session.execute(
                update(WalletORM)
                .where(and_(WalletORM.name == wallet_name, WalletORM.user_id == user_id))
                .values(balance=WalletORM.balance - amount)
                .returning(WalletORM.id, WalletORM.currency)
            )
            result = stmt.one_or_none()
            if result is None:
                raise HTTPException(status_code=404, detail=f"Wallet '{wallet_name}' not found")
        except IntegrityError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Problem updating object {wallet_name=}\n{e.args[0]}"
            )
        else:
            await self._session.flush()

        return {
            "wallet_id": result.id,
            "wallet_name": wallet_name,
            "currency": result.currency,
            "amount": amount,
            "description": description,
        }


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
        fild_type = OperationEnum.INCOME if income else OperationEnum.EXPENSE

        operation_orm = OperationWalletORM(
            wallet_id=wallet_id,
            type=fild_type,
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

    async def get_history(self, user_id: int, wallet_id: int | None, order_by_data: OperationOrderEnum,
                          limit: int | None):
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
            stm = select(WalletORM.id).where(and_(WalletORM.id == wallet_id, WalletORM.user_id == user_id)).exists()
            result_bool = await self._session.scalar(select(stm))
            if not result_bool:
                raise HTTPException(status_code=404, detail=f"Wallet '{wallet_id}' not found")
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
