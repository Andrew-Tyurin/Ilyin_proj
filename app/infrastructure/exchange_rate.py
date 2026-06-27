import asyncio
from decimal import Decimal
from time import perf_counter

import httpx

from app.config_app import ExchangeRateDefaultSettings, InstanceExchangeRateApiSettings
from app.custom_enum import CurrencyEnum, ExchangeRateProviderEnum
from app.domain.rules import WalletRules

EXCHANGE_RATE_DICT: dict[tuple[CurrencyEnum, CurrencyEnum], tuple[Decimal, ExchangeRateProviderEnum]] = {
    (CurrencyEnum.USD, CurrencyEnum.RUB): (ExchangeRateDefaultSettings.usd_to_rub, ExchangeRateProviderEnum.APP),
    (CurrencyEnum.USD, CurrencyEnum.EUR): (ExchangeRateDefaultSettings.usd_to_eur, ExchangeRateProviderEnum.APP),
    (CurrencyEnum.EUR, CurrencyEnum.RUB): (ExchangeRateDefaultSettings.eur_to_rub, ExchangeRateProviderEnum.APP),
    (CurrencyEnum.EUR, CurrencyEnum.USD): (ExchangeRateDefaultSettings.eur_to_usd, ExchangeRateProviderEnum.APP),
    (CurrencyEnum.RUB, CurrencyEnum.USD): (ExchangeRateDefaultSettings.rub_to_usd, ExchangeRateProviderEnum.APP),
    (CurrencyEnum.RUB, CurrencyEnum.EUR): (ExchangeRateDefaultSettings.rub_to_eur, ExchangeRateProviderEnum.APP),
    (CurrencyEnum.RUB, CurrencyEnum.RUB): (ExchangeRateDefaultSettings.rub_to_rub, ExchangeRateProviderEnum.APP),
    (CurrencyEnum.EUR, CurrencyEnum.EUR): (ExchangeRateDefaultSettings.eur_to_eur, ExchangeRateProviderEnum.APP),
    (CurrencyEnum.USD, CurrencyEnum.USD): (ExchangeRateDefaultSettings.usd_to_usd, ExchangeRateProviderEnum.APP),
}
CACHE_EXCHANGE_RATE_DICT: dict[
    tuple[CurrencyEnum, CurrencyEnum], tuple[Decimal, ExchangeRateProviderEnum, float | int]
] = {}


async def collect_cache_from_api(client: httpx.AsyncClient, currency: CurrencyEnum) -> None:
    url_1 = f"https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/{currency}.json"
    url_2 = f"https://latest.currency-api.pages.dev/v1/currencies/{currency}.json"
    for url in (url_1, url_2):
        try:
            response = await client.get(url, timeout=InstanceExchangeRateApiSettings.timeout_response)
            response.raise_for_status()  # raise except если статус код != 200
            data = response.json()
            data = data[currency]
            cache_time = perf_counter()
            value_rub = (Decimal(str(data[CurrencyEnum.RUB])), ExchangeRateProviderEnum.API, cache_time)
            value_usd = (Decimal(str(data[CurrencyEnum.USD])), ExchangeRateProviderEnum.API, cache_time)
            value_eur = (Decimal(str(data[CurrencyEnum.EUR])), ExchangeRateProviderEnum.API, cache_time)
            CACHE_EXCHANGE_RATE_DICT[(currency, CurrencyEnum.RUB)] = value_rub
            CACHE_EXCHANGE_RATE_DICT[(currency, CurrencyEnum.USD)] = value_usd
            CACHE_EXCHANGE_RATE_DICT[(currency, CurrencyEnum.EUR)] = value_eur
        except Exception:
            continue
        else:
            return None

    raise ConnectionError


async def get_exchange_rate_api(
        from_currency: CurrencyEnum,
        to_currency: CurrencyEnum
) -> tuple[Decimal, ExchangeRateProviderEnum] | None:
    if InstanceExchangeRateApiSettings.verification_of_recovery_time:
        async with httpx.AsyncClient() as client:
            currencies = (CurrencyEnum.RUB, CurrencyEnum.USD, CurrencyEnum.EUR)
            tasks_list = [collect_cache_from_api(client, currency) for currency in currencies]
            try:
                await asyncio.gather(*tasks_list)
            except ConnectionError:
                CACHE_EXCHANGE_RATE_DICT.clear()
                InstanceExchangeRateApiSettings.api_start_recovery_time()
            else:
                value = CACHE_EXCHANGE_RATE_DICT.get((from_currency, to_currency))
                return value[:2] if value else None
    return None


async def get_exchange_rate(
        from_currency: CurrencyEnum,
        to_currency: CurrencyEnum
) -> tuple[Decimal, ExchangeRateProviderEnum]:
    key = (from_currency, to_currency)
    async with InstanceExchangeRateApiSettings.lock_response:
        cache_exchange_rate = CACHE_EXCHANGE_RATE_DICT.get(key)
        if cache_exchange_rate:
            current_lifetime = int(perf_counter() - cache_exchange_rate[2])
            if current_lifetime > InstanceExchangeRateApiSettings.cache_lifetime:
                rate_and_provider = await get_exchange_rate_api(from_currency, to_currency)
                if rate_and_provider:
                    return rate_and_provider
            else:
                return cache_exchange_rate[:2]
        else:
            rate_and_provider = await get_exchange_rate_api(from_currency, to_currency)
            if rate_and_provider:
                return rate_and_provider

        return EXCHANGE_RATE_DICT.get(key)


async def convert_using_exchange_rate(
        balance: Decimal,
        from_currency: CurrencyEnum,
        to_currency: CurrencyEnum
) -> tuple[Decimal, ExchangeRateProviderEnum]:
    rate, provider = await get_exchange_rate(from_currency, to_currency)
    converted_balance_and_provider = (round(rate * balance, WalletRules.balance_length_after_point), provider)
    return converted_balance_and_provider
