from tests.moc_data.base_moc import BaseDataclassMoc


class CreateWalletDataclassMoc(BaseDataclassMoc):
    name: str
    initial_balance: int


class ReadWalletDataclassMoc(BaseDataclassMoc):
    id: int
    name: str
    balance: int


class FullReadWalletMoc(ReadWalletDataclassMoc):
    user_id: int


class ResultCreateWalletDataclassMoc(BaseDataclassMoc):
    message: str
    wallet: FullReadWalletMoc


class ReadSumBalanceWalletsDataclassMoc(BaseDataclassMoc):
    total_balance: int


class ReadWalletsDataclassMoc(BaseDataclassMoc):
    user_id: int
    user_name: str
    wallets: list[ReadWalletDataclassMoc]


class UpdateWalletDataclassMoc(BaseDataclassMoc):
    wallet_name: str
    amount: int
    description: str


class ResultUpdateWalletDataclassMoc(BaseDataclassMoc):
    message: str
    wallet_name: str
    amount: int
    description: str
    new_balance: int
