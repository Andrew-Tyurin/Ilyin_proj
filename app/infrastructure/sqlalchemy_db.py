from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

from app.config_app import SaDbSettings

if SaDbSettings.app_env == 'prod':
    async_engine = create_async_engine(
        url=SaDbSettings.database_url,
        pool_size=SaDbSettings.pool_size,
        max_overflow=SaDbSettings.max_overflow,
        echo=SaDbSettings.echo,
    )

elif SaDbSettings.app_env == 'test':
    async_engine = create_async_engine(
        url=SaDbSettings.database_url,
        poolclass=NullPool,
        echo=False,
    )

else:
    raise ValueError(f"Invalid APP_ENV: {SaDbSettings.app_env}")

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


async def async_create_table() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def async_drop_table() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def async_truncate_tables():
    async with async_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(
                text(f'TRUNCATE TABLE "{table.name}" RESTART IDENTITY CASCADE')
            )


class Base(DeclarativeBase):
    def __repr__(self):
        try:
            columns = self.__table__.columns.keys()
        except AttributeError:
            return f'<{self.__class__.__name__}: __table__ - absent>'

        values = (f"{col}={getattr(self, col, 'Errors')}" for col in columns)
        return f'<{self.__class__.__name__}: {"; ".join(values)}>'

    def model_dump(self) -> dict:
        columns = self.__table__.columns.keys()
        return {col: getattr(self, col, 'Error') for col in columns}
