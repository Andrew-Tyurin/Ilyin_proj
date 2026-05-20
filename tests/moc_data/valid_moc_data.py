from tests.moc_data.user_moc import (
    CreateUserDataclassMoc,
    ResultCreateUserDataclassMoc,
    ReadUserAuthorizationMoc,
    ReadUserDataclassMoc,
    ReadPayloadUserJwtDataclassMoc
)
from tests.moc_data.wallet_moc import (
    CreateWalletDataclassMoc,
    ReadWalletDataclassMoc,
    FullReadWalletMoc,
    ResultCreateWalletDataclassMoc,
    ReadSumBalanceWalletsDataclassMoc,
    ReadWalletsDataclassMoc,
    UpdateWalletDataclassMoc,
    ResultUpdateWalletDataclassMoc
)


status_code_200 = 200
status_code_201 = 201

status_code_400 = 400
status_code_401 = 401


class User1:
    id: int = 1
    user_name: str = "test_user_1"
    password: str = "1234"
    access_token: str = "access_token_user_1"


class User2:
    id: int = 2
    user_name: str = "test_user_2"
    password: str = "12345"
    access_token: str = "access_token_user_2"


class BaseWallet:
    message_income: str = "Income added"
    message_expense: str = "Expense added"


class Wallet1User1(BaseWallet):
    id: int = 1
    name: str = "SBER"
    user: User1 = User1()
    current_balance: int = 400
    balance_add_income: int = 200
    balance_add_expense: int = 350
    result_add_income: int = 600
    result_add_expense: int = 50
    description_add_income: str = "salary"
    description_add_expense: str = "food"


class Wallet2User1(BaseWallet):
    id: int = 2
    name: str = "VTB"
    user: User1 = User1()
    current_balance: int = 1000
    balance_add_income: int = 600
    balance_add_expense: int = 200
    result_add_income: int = 1600
    result_add_expense: int = 800
    description_add_income = "donate"
    description_add_expense = "woman"


create_user1 = CreateUserDataclassMoc(user_name=User1.user_name, password=User1.password)
create_user2 = CreateUserDataclassMoc(user_name=User2.user_name, password=User2.password)

read_user1 = ReadUserDataclassMoc(id=User1.id, user_name=User1.user_name)
read_user2 = ReadUserDataclassMoc(id=User2.id, user_name=User2.user_name)

result_create_user1 = ResultCreateUserDataclassMoc(
    id=User1.id,
    user_name=User1.user_name,
    access_token=User1.access_token
)

user1_read_authorization = ReadUserAuthorizationMoc(**result_create_user1.model_dump())

user1_read_payload_jwt = ReadPayloadUserJwtDataclassMoc(id=1, user_name=read_user1.user_name, expires_time_life=1)

user1_create_wallet1 = CreateWalletDataclassMoc(name=Wallet1User1.name, initial_balance=Wallet1User1.current_balance)
user1_create_wallet2 = CreateWalletDataclassMoc(name=Wallet2User1.name, initial_balance=Wallet2User1.current_balance)

user1_result_wallet1 = ReadWalletDataclassMoc(
    id=Wallet1User1.id,
    name=Wallet1User1.name,
    balance=Wallet1User1.current_balance,
)
user1_result_wallet2 = ReadWalletDataclassMoc(
    id=Wallet2User1.id,
    name=Wallet2User1.name,
    balance=Wallet2User1.current_balance,
)

user1_result_full_wallet1 = FullReadWalletMoc(
    **user1_result_wallet1.model_dump(),
    user_id=User1.id,
)
user1_result_full_wallet2 = FullReadWalletMoc(
    **user1_result_wallet2.model_dump(),
    user_id=User1.id,
)

user1_result_create_wallet1 = ResultCreateWalletDataclassMoc(
    message=f"wallet '{Wallet1User1.name}' created",
    wallet=user1_result_full_wallet1,
)
user1_result_create_wallet2 = ResultCreateWalletDataclassMoc(
    message=f"wallet '{Wallet2User1.name}' created",
    wallet=user1_result_full_wallet2,
)

user1_read_sum_balance_wallets = ReadSumBalanceWalletsDataclassMoc(
    total_balance=Wallet1User1.current_balance + Wallet2User1.current_balance,
)

user1_read_wallets_moc = ReadWalletsDataclassMoc(
    user_id=User1.id,
    user_name=User1.user_name,
    wallets=[user1_result_wallet1, user1_result_wallet2]
)

user1_update_wallet1_add_income = UpdateWalletDataclassMoc(
    wallet_name=Wallet1User1.name,
    amount=Wallet1User1.balance_add_income,
    description=Wallet1User1.description_add_income,
)
user1_update_wallet1_add_expense = UpdateWalletDataclassMoc(
    wallet_name=Wallet1User1.name,
    amount=Wallet1User1.balance_add_expense,
    description=Wallet1User1.description_add_expense,
)

user1_result_update_wallet1_add_income = ResultUpdateWalletDataclassMoc(
    message=Wallet1User1.message_income,
    wallet_name=Wallet1User1.name,
    amount=Wallet1User1.balance_add_income,
    description=Wallet1User1.description_add_income,
    new_balance=Wallet1User1.result_add_income,
)
user1_result_update_wallet1_add_expense = ResultUpdateWalletDataclassMoc(
    message=Wallet1User1.message_expense,
    wallet_name=Wallet1User1.name,
    amount=Wallet1User1.balance_add_expense,
    description=Wallet1User1.description_add_expense,
    new_balance=Wallet1User1.result_add_expense,
)
