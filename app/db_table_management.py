import asyncio

from app.infrastructure.sqlalchemy_db import async_create_table, async_drop_table
from app.infrastructure.sqlalchemy_models import UserORM, WalletORM, OperationWalletORM  # noqa: F401


def operations_on_db(
        drop_table: bool = False,
        create_table: bool = True,
) -> None:
    async def table_management() -> None:
        if drop_table:
            await async_drop_table()

        if create_table:
            await async_create_table()

    asyncio.run(table_management())


if __name__ == "__main__":
    # из корня проекта: python -m app.db_table_management
    user_value = input("Отформатировать таблицы: 'f' дропнуть таблицы 'd' \n")
    if user_value == "f":
        operations_on_db(drop_table=True)
    elif user_value == "d":
        operations_on_db(drop_table=True, create_table=False)
    else:
        operations_on_db()
