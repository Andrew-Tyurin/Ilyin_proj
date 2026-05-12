from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.contracts.repository_users import AbstractRepositoryUser
from app.infrastructure.hashing import HashArgon2
from app.infrastructure.sqlalchemy_models import UserORM


class SqlAlchemyRepositoryUser(AbstractRepositoryUser):
    _hash_password = HashArgon2()

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_all(self, offset: int):
        stm = await self._session.execute(
            select(UserORM.id, UserORM.user_name)
            .offset(offset)
            .limit(10)
            .order_by(UserORM.id)
        )
        users = [dict(user._mapping) for user in stm.all()]
        return users

    async def get_one(self, user_id: int):
        stm = await self._session.execute(
            select(UserORM.id, UserORM.user_name)
            .where(UserORM.id == user_id)
        )
        user = stm.one_or_none()
        if user is None:
            raise HTTPException(status_code=404, detail=f"User id - {user_id} does not exist")

        user = dict(user._mapping)
        return user

    async def create(self, user: dict):
        user_name = user.get("user_name")
        password = user.get("password")
        hash_password = self._hash_password.hash(password)

        stm = select(UserORM).where(UserORM.user_name == user_name).exists()
        result_bool = await self._session.scalar(select(stm))
        if result_bool:
            raise HTTPException(status_code=400, detail=f"User '{user_name}' already exists")

        try:
            user_orm = UserORM(user_name=user_name, password=hash_password)
            self._session.add(user_orm)
            await self._session.commit()
        except IntegrityError as e:
            raise HTTPException(status_code=400, detail=f"Problem with creation User: {e.args[0]}")

        return {"id": user_orm.id, "user_name": user_orm.user_name}

    async def authorization(self, user: dict):
        detail_error = "Incorrect login or password"
        user_name = user.get("user_name")
        password = user.get("password")

        stm = await self._session.execute(
            select(UserORM.id, UserORM.user_name, UserORM.password)
            .where(UserORM.user_name == user_name)
        )
        user = stm.one_or_none()

        if user is None:
            raise HTTPException(status_code=400, detail=detail_error)

        hash_password = user.password
        valid_password = self._hash_password.verify(password, hash_password)

        if not valid_password:
            raise HTTPException(status_code=400, detail=detail_error)

        user = dict(user._mapping)
        del user["password"]
        return user
