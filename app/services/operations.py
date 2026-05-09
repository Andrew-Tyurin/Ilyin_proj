from app.contracts.repository_operations import AbstractRepositoryOperation


class ServiceOperation:
    def __init__(self, repo: AbstractRepositoryOperation):
        self._repo = repo

    async def add_income(self, user_id: int, operation: dict):
        return await self._repo.addition(user_id, operation)

    async def add_expense(self, user_id: int, operation: dict):
        return await self._repo.subtraction(user_id, operation)
