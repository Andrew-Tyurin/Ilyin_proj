import asyncio

from app.infrastructure.sqlalchemy_db import async_create_table, async_drop_table


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
    operations_on_db()
