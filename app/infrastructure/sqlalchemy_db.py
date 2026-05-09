from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from config_env import settings_psql

async_engine = create_async_engine(
    url=settings_psql.DB_URL_ASYNCPG_STR,
    pool_size=4,
    max_overflow=4,
    echo=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    autocommit=False,  # False - сами управляем, когда комитить в бд
    autoflush=False,  # False - сами управляем, когда отправить запрос в бд
    expire_on_commit=False,
)


async def async_create_table() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


class Base(DeclarativeBase):
    def __repr__(self):
        try:
            columns = self.__table__.columns.keys()
        except AttributeError:
            return f'<{self.__class__.__name__}: __table__ - absent>'

        values = (f"{col}={getattr(self, col, 'Errors')}" for col in columns)
        return f'<{self.__class__.__name__}: {"; ".join(values)}>'

    def model_dump(self):
        columns = self.__table__.columns.keys()
        return {col: getattr(self, col, 'Errors') for col in columns}
