from fastapi import HTTPException
from sqlalchemy import update, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.infrastructure.sqlalchemy_models import WalletORM
from app.contracts.repository_operations import AbstractRepositoryOperation


class SqlAlchemyRepositoryOperation(AbstractRepositoryOperation):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def addition(self, user_id: int, operation: dict):
        wallet_name = operation.get("wallet_name")
        amount = operation.get("amount")
        description = operation.get("description")

        stmt = (
            update(WalletORM)
            .where(and_(WalletORM.name == wallet_name, WalletORM.user_id == user_id))
            .values(balance=WalletORM.balance + amount)
            .returning(WalletORM.balance)  # что вернуть после обновления
        )
        new_balance = await self._session.scalar(stmt)
        if new_balance is None:
            raise HTTPException(status_code=404, detail=f"Wallet '{wallet_name}' not found")
        await self._session.commit()

        return {
            "message": "Income added",
            "wallet_name": wallet_name,
            "amount": amount,
            "description": description,
            "new_balance": new_balance,
        }

    async def subtraction(self, user_id: int, operation: dict):
        wallet_name = operation.get("wallet_name")
        amount = operation.get("amount")
        description = operation.get("description")

        try:
            stmt = (
                update(WalletORM)
                .where(and_(WalletORM.name == wallet_name, WalletORM.user_id == user_id))
                .values(balance=WalletORM.balance - amount)
                .returning(WalletORM.balance)
            )
            new_balance = await self._session.scalar(stmt)
            if new_balance is None:
                raise HTTPException(status_code=404, detail=f"Wallet '{wallet_name}' not found")
        except IntegrityError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Problem updating object {wallet_name=}\n{e.args[0]}"
            )
        else:
            await self._session.commit()

        return {
            "message": "Expense added",
            "wallet_name": wallet_name,
            "amount": amount,
            "description": description,
            "new_balance": new_balance,
        }
