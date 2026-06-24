from decimal import Decimal

from app.custom_enum import CurrencyEnum, ExchangeRateProviderEnum

TEST_EXCHANGE_RATE_DICT:dict[tuple[CurrencyEnum, CurrencyEnum], tuple[Decimal, ExchangeRateProviderEnum]] = {
    (CurrencyEnum.USD, CurrencyEnum.RUB): (Decimal("75.00"), ExchangeRateProviderEnum.APP),
    (CurrencyEnum.USD, CurrencyEnum.EUR): (Decimal("0.85"), ExchangeRateProviderEnum.APP),
    (CurrencyEnum.EUR, CurrencyEnum.RUB): (Decimal("85.00"), ExchangeRateProviderEnum.APP),
    (CurrencyEnum.EUR, CurrencyEnum.USD): (Decimal("1.15"), ExchangeRateProviderEnum.APP),
    (CurrencyEnum.RUB, CurrencyEnum.USD): (Decimal("0.0134"), ExchangeRateProviderEnum.APP),
    (CurrencyEnum.RUB, CurrencyEnum.EUR): (Decimal("0.0118"), ExchangeRateProviderEnum.APP),
    (CurrencyEnum.RUB, CurrencyEnum.RUB): (Decimal("1.00"), ExchangeRateProviderEnum.APP),
    (CurrencyEnum.EUR, CurrencyEnum.EUR): (Decimal("1.00"), ExchangeRateProviderEnum.APP),
    (CurrencyEnum.USD, CurrencyEnum.USD): (Decimal("1.00"), ExchangeRateProviderEnum.APP)
}


async def get_exchange_rate_replacement(from_currency: CurrencyEnum, to_currency: CurrencyEnum) -> Decimal:
    return TEST_EXCHANGE_RATE_DICT.get((from_currency, to_currency))


async def convert_using_exchange_rate(
        balance: Decimal,
        from_currency: CurrencyEnum,
        to_currency: CurrencyEnum
) -> tuple[Decimal, ExchangeRateProviderEnum]:
    rate, provider = await get_exchange_rate_replacement(from_currency, to_currency)
    converted_balance_and_provider = round(rate * balance, 2), provider
    return converted_balance_and_provider
