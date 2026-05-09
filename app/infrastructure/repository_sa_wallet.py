from fastapi import HTTPException
from sqlalchemy import select, func, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.contracts.repository_wallets import AbstractRepositoryWallet
from app.infrastructure.sqlalchemy_models import WalletORM, UserORM


class SqlAlchemyRepositoryWallet(AbstractRepositoryWallet):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get(self, user_id: int, wallet_name: str | None = None):
        if wallet_name is None:
            result: int = await self._session.scalar(
                select(func.sum(WalletORM.balance))
                .where(WalletORM.user_id == user_id)
            )
            return {"total_balance": 0 if result is None else result}

        stm = await self._session.scalars(
            select(WalletORM)
            .where(and_(WalletORM.name == wallet_name, WalletORM.user_id == user_id))
        )
        result = stm.one_or_none()

        if result is None:
            raise HTTPException(status_code=404, detail=f"Wallet '{wallet_name}' does not exist")

        return result.model_dump()

    async def get_all(self, user_id: int):
        wallets_stm = (
            select(WalletORM.name, WalletORM.balance)
            .where(WalletORM.user_id == user_id)
            .order_by(WalletORM.id)
        )
        wallets_result = await self._session.execute(wallets_stm)
        wallets_serialized = [dict(wallet._mapping) for wallet in wallets_result]
        return wallets_serialized

    async def add(self, user_id: int, wallet: dict):
        name = wallet.get("name")
        wallet["balance"] = wallet.pop("initial_balance")

        stm = select(WalletORM.id).where(and_(WalletORM.name == name, WalletORM.user_id == user_id)).exists()
        result_bool = await self._session.scalar(select(stm))
        if result_bool:
            raise HTTPException(status_code=400, detail=f"Wallet '{name}' already exists")
        try:
            orm_wallet = WalletORM(**wallet, user_id=user_id)
            self._session.add(orm_wallet)
            await self._session.commit()
        except IntegrityError as e:
            raise HTTPException(status_code=400, detail=f"Problem with creation Wallet: {e.args[0]}")

        return {
            "message": f"wallet '{name}' created",
            "wallet": orm_wallet.model_dump(),
        }
