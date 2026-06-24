from datetime import datetime, timezone
from decimal import Decimal

from app.custom_enum import CurrencyEnum, OperationTypeEnum, ExchangeRateProviderEnum
from tests.moc_data.user_moc import (
    CreateUserDataclassMoc,
    ResultCreateUserDataclassMoc,
    ReadUserAuthorizationMoc,
    ReadUserDataclassMoc,
    ReadPayloadUserJwtDataclassMoc
)
from tests.moc_data.wallet_moc import (
    CreateWalletDataclassMoc,
    CreateFullWalletDataclassMoc,
    CreateOperationWalletDataclassMoc,
    ReadWalletDataclassMoc,
    ResultCreateWalletDataclassMoc,
    ReadSumBalanceWalletsDataclassMoc,
    UpdateWalletDataclassMoc,
    ReadResultUpdateWalletDataclassMoc,
    ReadOperationWalletDataclassMoc,
    TransferBetweenWalletDataclassMoc,
)

status_code_200 = 200
status_code_201 = 201


class User1:
    id: int = 1
    user_name: str = "test_user_1"
    password: str = "1234"
    access_token: str = "access_token_user_1"
    provider = ExchangeRateProviderEnum.APP


class User2:
    id: int = 2
    user_name: str = "test_user_2"
    password: str = "12345"
    access_token: str = "access_token_user_2"
    provider = ExchangeRateProviderEnum.APP


class Wallet1User1:
    id: int = 1
    name: str = "SBER"
    currency: CurrencyEnum = CurrencyEnum.RUB
    user: User1 = User1()
    start_balance: Decimal = Decimal("0.00")
    balance_add_income: Decimal = Decimal("500.00")
    balance_add_expense: Decimal = Decimal("350.00")
    description_add_income: str = "salary"
    description_add_expense: str = "food"
    to_usd_rate: Decimal = Decimal("0.0134")
    balance_transfer: Decimal = Decimal("400.00")


class Wallet2User1:
    id: int = 2
    name: str = "USA"
    currency: CurrencyEnum = CurrencyEnum.USD
    user: User1 = User1()
    start_balance: Decimal = Decimal("0.00")
    balance_add_income: Decimal = Decimal("100.00")
    balance_add_expense: Decimal = Decimal("25.00")
    description_add_income = "donate"
    description_add_expense = "woman"
    to_rub_rate: Decimal = Decimal("75.00")
    balance_transfer: Decimal = Decimal("50.00")


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

user1_read_payload_jwt = ReadPayloadUserJwtDataclassMoc(id=User1.id, user_name=User1.user_name, expires_time_life=1)

user1_create_wallet_rub = CreateWalletDataclassMoc(name=Wallet1User1.name, currency=CurrencyEnum.RUB)
user1_create_wallet_usd = CreateWalletDataclassMoc(name=Wallet2User1.name, currency=CurrencyEnum.USD)

user1_create_full_wallet_rub = CreateFullWalletDataclassMoc(
    name=Wallet1User1.name,
    currency=CurrencyEnum.RUB,
    balance=Wallet1User1.balance_add_income
)
user1_create_full_wallet_usd = CreateFullWalletDataclassMoc(
    name=Wallet2User1.name,
    currency=CurrencyEnum.USD,
    balance=Wallet2User1.balance_add_income
)

user1_create_wallet_operation_rub = CreateOperationWalletDataclassMoc(
    wallet_id=Wallet1User1.id,
    type=OperationTypeEnum.INCOME,
    amount=Wallet1User1.balance_add_income,
    description=None,
)
user1_create_wallet_operation_usd = CreateOperationWalletDataclassMoc(
    wallet_id=Wallet2User1.id,
    type=OperationTypeEnum.INCOME,
    amount=Wallet2User1.balance_add_income,
    description=None,
)

user1_result_wallet1 = ReadWalletDataclassMoc(
    id=Wallet1User1.id,
    name=Wallet1User1.name,
    balance=str(Wallet1User1.start_balance),
    currency=CurrencyEnum.RUB,
    user_id=User1.id
)
user1_result_wallet2 = ReadWalletDataclassMoc(
    id=Wallet2User1.id,
    name=Wallet2User1.name,
    balance=str(Wallet2User1.start_balance),
    currency=CurrencyEnum.USD,
    user_id=User1.id
)

user1_result_create_wallet1 = ResultCreateWalletDataclassMoc(
    message=f"wallet '{Wallet1User1.name}' created",
    wallet=user1_result_wallet1,
)
user1_result_create_wallet2 = ResultCreateWalletDataclassMoc(
    message=f"wallet '{Wallet2User1.name}' created",
    wallet=user1_result_wallet2,
)

user1_read_balance_zero_wallets = ReadSumBalanceWalletsDataclassMoc(
    user_id=User1.id,
    currency=CurrencyEnum.RUB,
    total_balance=str(Decimal("0.00")),
    provider=User1.provider
)
sum_rub_wallets = Wallet2User1.to_rub_rate * Wallet2User1.balance_add_income + Wallet1User1.balance_add_income
user1_read_balance_not_zero_wallets = ReadSumBalanceWalletsDataclassMoc(
    user_id=User1.id,
    currency=CurrencyEnum.RUB,
    total_balance=str(round(sum_rub_wallets, 2)),
    provider=User1.provider
)

user1_update_wallet1_add_income = UpdateWalletDataclassMoc(
    wallet_id=Wallet1User1.id,
    amount=str(Wallet1User1.balance_add_income),
    description=Wallet1User1.description_add_income,
)
user1_update_wallet1_add_expense = UpdateWalletDataclassMoc(
    wallet_id=Wallet1User1.id,
    amount=str(Wallet1User1.balance_add_expense),
    description=Wallet1User1.description_add_expense,
)

user1_operation_wallet1_add_income = ReadOperationWalletDataclassMoc(
    id=1,
    type=OperationTypeEnum.INCOME,
    amount=str(Wallet1User1.balance_add_income),
    description=Wallet1User1.description_add_income,
    created_at=datetime.now(timezone.utc)
)
user1_result_update_wallet1_add_income = ReadResultUpdateWalletDataclassMoc(
    wallet_id=Wallet1User1.id,
    wallet_name=Wallet1User1.name,
    currency=Wallet1User1.currency,
    operation=user1_operation_wallet1_add_income,
)

user1_operation_wallet1_add_expense = ReadOperationWalletDataclassMoc(
    id=3,
    type=OperationTypeEnum.EXPENSE,
    amount=str(Wallet1User1.balance_add_expense),
    description=Wallet1User1.description_add_expense,
    created_at=datetime.now(timezone.utc)
)
user1_result_update_wallet1_add_expense = ReadResultUpdateWalletDataclassMoc(
    wallet_id=Wallet1User1.id,
    wallet_name=Wallet1User1.name,
    currency=Wallet1User1.currency,
    operation=user1_operation_wallet1_add_expense,
)

user1_transfer_between = TransferBetweenWalletDataclassMoc(
    from_wallet_id=Wallet2User1.id,
    to_wallet_id=Wallet1User1.id,
    amount=str(Wallet2User1.balance_transfer)
)

user1_operation_transfer_between_from_wallet2 = ReadOperationWalletDataclassMoc(
    id=3,
    type=OperationTypeEnum.TRANSFER_EXPENSE,
    amount=str(Wallet2User1.balance_transfer),
    description=f"transfer into wallet_id={Wallet1User1.id}",
    created_at=datetime.now(timezone.utc)
)
user1_result_transfer_between_from_wallet2 = ReadResultUpdateWalletDataclassMoc(
    wallet_id=Wallet2User1.id,
    wallet_name=Wallet2User1.name,
    currency=Wallet2User1.currency,
    operation=user1_operation_transfer_between_from_wallet2,
)

user1_operation_transfer_between_to_wallet1 = ReadOperationWalletDataclassMoc(
    id=4,
    type=OperationTypeEnum.TRANSFER_INCOME,
    amount=str(round(Wallet2User1.balance_transfer * Wallet2User1.to_rub_rate, 2)),
    description=f"transfer from wallet_id={Wallet2User1.id}",
    created_at=datetime.now(timezone.utc)
)
user1_result_transfer_between_to_wallet1 = ReadResultUpdateWalletDataclassMoc(
    wallet_id=Wallet1User1.id,
    wallet_name=Wallet1User1.name,
    currency=Wallet1User1.currency,
    operation=user1_operation_transfer_between_to_wallet1,
)

user1_read_operation_income_wallet1 = ReadOperationWalletDataclassMoc(
    id=1,
    type=OperationTypeEnum.INCOME,
    amount=str(Wallet1User1.balance_add_income),
    description=None,
    created_at=datetime.now(timezone.utc)
)
user1_result_read_operation_income_wallet1 = ReadResultUpdateWalletDataclassMoc(
    wallet_id=Wallet1User1.id,
    wallet_name=Wallet1User1.name,
    currency=Wallet1User1.currency,
    operation=user1_read_operation_income_wallet1,
)
user1_read_operation_income_wallet2 = ReadOperationWalletDataclassMoc(
    id=2,
    type=OperationTypeEnum.INCOME,
    amount=str(Wallet2User1.balance_add_income),
    description=None,
    created_at=datetime.now(timezone.utc)
)
user1_result_read_operation_income_wallet2 = ReadResultUpdateWalletDataclassMoc(
    wallet_id=Wallet2User1.id,
    wallet_name=Wallet2User1.name,
    currency=Wallet2User1.currency,
    operation=user1_read_operation_income_wallet2,
)
