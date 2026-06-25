from decimal import Decimal
from time import perf_counter

import httpx

from app.config_app import ExchangeRateSettings
from app.custom_enum import CurrencyEnum, ExchangeRateProviderEnum
from app.domain.rules import WalletRules

EXCHANGE_RATE_DICT: dict[tuple[CurrencyEnum, CurrencyEnum], tuple[Decimal, ExchangeRateProviderEnum]] = {
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
CACHE_EXCHANGE_RATE_DICT: dict[
    tuple[CurrencyEnum, CurrencyEnum], tuple[Decimal, ExchangeRateProviderEnum, float | int]
] = {}


async def get_exchange_rates_via_an_api(from_currency: CurrencyEnum, to_currency: CurrencyEnum, url: str) -> Decimal:
    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=ExchangeRateSettings.timeout_response)
        response.raise_for_status()  # raise except если статус код != 200
        data = response.json()
        currency_all = data[from_currency]
        exchange_rate: Decimal = Decimal(str(currency_all[to_currency]))
        return exchange_rate


async def preparation_before_get_rate(
        from_currency: CurrencyEnum,
        to_currency: CurrencyEnum
) -> tuple[Decimal, ExchangeRateProviderEnum] | None:
    url_1 = f"https://latest.currency-api.pages.dev/v1/currencies/{from_currency}.json"
    url_2 = f"https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/{from_currency}.json"

    for url in [url_2, url_1]:
        try:
            rate = await get_exchange_rates_via_an_api(from_currency, to_currency, url)
            print("Запрос из api")
        except Exception:
            continue
        else:
            value = (rate, ExchangeRateProviderEnum.API, perf_counter())
            CACHE_EXCHANGE_RATE_DICT[(from_currency, to_currency)] = value
            return value[:2]

    return None


async def get_exchange_rate(
        from_currency: CurrencyEnum,
        to_currency: CurrencyEnum
) -> tuple[Decimal, ExchangeRateProviderEnum]:
    key = (from_currency, to_currency)
    cache_exchange_rate = CACHE_EXCHANGE_RATE_DICT.get(key)
    if cache_exchange_rate:
        current_lifetime = int(perf_counter() - cache_exchange_rate[2])
        if current_lifetime > ExchangeRateSettings.cache_lifetime:
            rate_and_provider = await preparation_before_get_rate(from_currency, to_currency)
            if rate_and_provider:
                return rate_and_provider
        else:
            print(f"Запрос из кэша {current_lifetime}/{ExchangeRateSettings.cache_lifetime}")
            return cache_exchange_rate[:2]
    else:
        rate_and_provider = await preparation_before_get_rate(from_currency, to_currency)
        if rate_and_provider:
            return rate_and_provider

    print("Запрос из приложения")
    return EXCHANGE_RATE_DICT.get(key)


async def convert_using_exchange_rate(
        balance: Decimal,
        from_currency: CurrencyEnum,
        to_currency: CurrencyEnum
) -> tuple[Decimal, ExchangeRateProviderEnum]:
    rate, provider = await get_exchange_rate(from_currency, to_currency)
    converted_balance_and_provider = (round(rate * balance, WalletRules.balance_length_after_point), provider)
    return converted_balance_and_provider
