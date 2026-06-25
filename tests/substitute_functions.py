from decimal import Decimal

from app.config_app import ExchangeRateSettings
from app.custom_enum import CurrencyEnum, ExchangeRateProviderEnum
from app.domain.rules import WalletRules

TEST_EXCHANGE_RATE_DICT: dict[tuple[CurrencyEnum, CurrencyEnum], tuple[Decimal, ExchangeRateProviderEnum]] = {
    (CurrencyEnum.USD, CurrencyEnum.RUB): (ExchangeRateSettings.usd_to_rub, ExchangeRateProviderEnum.APP),
    (CurrencyEnum.USD, CurrencyEnum.EUR): (ExchangeRateSettings.usd_to_eur, ExchangeRateProviderEnum.APP),
    (CurrencyEnum.EUR, CurrencyEnum.RUB): (ExchangeRateSettings.eur_to_rub, ExchangeRateProviderEnum.APP),
    (CurrencyEnum.EUR, CurrencyEnum.USD): (ExchangeRateSettings.eur_to_usd, ExchangeRateProviderEnum.APP),
    (CurrencyEnum.RUB, CurrencyEnum.USD): (ExchangeRateSettings.rub_to_usd, ExchangeRateProviderEnum.APP),
    (CurrencyEnum.RUB, CurrencyEnum.EUR): (ExchangeRateSettings.rub_to_eur, ExchangeRateProviderEnum.APP),
    (CurrencyEnum.RUB, CurrencyEnum.RUB): (ExchangeRateSettings.rub_to_rub, ExchangeRateProviderEnum.APP),
    (CurrencyEnum.EUR, CurrencyEnum.EUR): (ExchangeRateSettings.eur_to_eur, ExchangeRateProviderEnum.APP),
    (CurrencyEnum.USD, CurrencyEnum.USD): (ExchangeRateSettings.usd_to_usd, ExchangeRateProviderEnum.APP),
}


async def get_exchange_rate_replacement(from_currency: CurrencyEnum, to_currency: CurrencyEnum) -> Decimal:
    return TEST_EXCHANGE_RATE_DICT.get((from_currency, to_currency))


async def convert_using_exchange_rate(
        balance: Decimal,
        from_currency: CurrencyEnum,
        to_currency: CurrencyEnum
) -> tuple[Decimal, ExchangeRateProviderEnum]:
    rate, provider = await get_exchange_rate_replacement(from_currency, to_currency)
    converted_balance_and_provider = (round(rate * balance, WalletRules.balance_length_after_point), provider)
    return converted_balance_and_provider
