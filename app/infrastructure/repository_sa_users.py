from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.contracts.repository_users import AbstractRepositoryUser
from app.domain.dto import UserWithoutPasswDTO
from app.domain.entities import User
from app.infrastructure.hashing import HashArgon2
from app.infrastructure.sqlalchemy_models import UserORM


class SqlAlchemyRepositoryUser(AbstractRepositoryUser):
    _hash_password = HashArgon2()

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_all(self, offset: int) -> list[UserWithoutPasswDTO]:
        users_row = (await self._session.execute(
            select(UserORM.id, UserORM.user_name)
            .offset(offset)
            .limit(10)
            .order_by(UserORM.id)
        )).all()

        return [UserWithoutPasswDTO(**dict(user_row._mapping)) for user_row in users_row]

    async def get_one(self, user_id: int) -> UserWithoutPasswDTO:
        user_row = (await self._session.execute(
            select(UserORM.id, UserORM.user_name)
            .where(UserORM.id == user_id)
        )).one_or_none()

        if user_row is None:
            raise HTTPException(status_code=404, detail=f"User id - {user_id} does not exist")

        return UserWithoutPasswDTO(**dict(user_row._mapping))

    async def create(self, user: User) -> UserWithoutPasswDTO:
        user_name = user.user_name
        password = user.password
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

        return UserWithoutPasswDTO(id=user_orm.id, user_name=user_orm.user_name)

    async def authorization(self, user: User) -> UserWithoutPasswDTO:
        user_name = user.user_name
        password = user.password
        error_400 = HTTPException(status_code=400, detail="Incorrect login or password")

        user_row = (await self._session.execute(
            select(UserORM.id, UserORM.user_name, UserORM.password)
            .where(UserORM.user_name == user_name)
        )).one_or_none()

        if user_row is None:
            raise error_400

        hash_password = user_row.password
        valid_password = self._hash_password.verify(password, hash_password)

        if not valid_password:
            raise error_400

        return UserWithoutPasswDTO(id=user_row.id, user_name=user_row.user_name)
