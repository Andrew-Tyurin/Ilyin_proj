from app.contracts.repository_wallets import AbstractRepositoryWallet


class ServiceWallet:
    def __init__(self, repo: AbstractRepositoryWallet):
        self._repo = repo

    async def get_balance(self, user_id: int, wallet_name: str | None = None) -> dict:
        return await self._repo.get(user_id, wallet_name)

    async def get_wallets(self, user_id: int):
        return await self._repo.get_all(user_id)

    async def create_wallet(self, user_id: int, wallet: dict) -> dict:
        return await self._repo.add(user_id, wallet)
