import asyncio
from decimal import Decimal
from time import perf_counter

import httpx

from app.config_app import ExchangeRateDefaultSettings, InstanceExchangeRateApiSettings
from app.custom_enum import CurrencyEnum, ExchangeRateProviderEnum
from app.domain.rules import WalletRules

RESERVE_EXCHANGE_RATE: dict[tuple[CurrencyEnum, CurrencyEnum], tuple[Decimal, ExchangeRateProviderEnum]] = {
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
CACHE_EXCHANGE_RATE: dict[
    tuple[CurrencyEnum, CurrencyEnum], tuple[Decimal, ExchangeRateProviderEnum, float | int]
] = {}


def append_to_cache(data: dict, currency: CurrencyEnum, cache_time: float) -> None:
    for specific_currency in (CurrencyEnum.RUB, CurrencyEnum.USD, CurrencyEnum.EUR):
        value_and_exchange = (Decimal(str(data[specific_currency])), ExchangeRateProviderEnum.API, cache_time)
        CACHE_EXCHANGE_RATE[(currency, specific_currency)] = value_and_exchange


async def collect_cache_from_api(client: httpx.AsyncClient, currency: CurrencyEnum, cache_time: float) -> None:
    url_1 = f"https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/{currency}.json"
    url_2 = f"https://latest.currency-api.pages.dev/v1/currencies/{currency}.json"
    for url in (url_1, url_2):
        try:
            response = await client.get(url, timeout=InstanceExchangeRateApiSettings.timeout_response)
            response.raise_for_status()  # raise except если статус код != 200
            data = response.json()
            append_to_cache(data[currency], currency, cache_time)
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
            cache_time = perf_counter()
            tasks_list = [collect_cache_from_api(client, currency, cache_time) for currency in currencies]
            try:
                await asyncio.gather(*tasks_list)
            except ConnectionError:
                CACHE_EXCHANGE_RATE.clear()
                InstanceExchangeRateApiSettings.api_start_recovery_time()
            else:
                value = CACHE_EXCHANGE_RATE.get((from_currency, to_currency))
                return value[:2] if value else None

    return None


def get_exchange_rate_cache(key: tuple[CurrencyEnum, CurrencyEnum]) -> tuple[Decimal, ExchangeRateProviderEnum] | None:
    cache_exchange_rate = CACHE_EXCHANGE_RATE.get(key)
    if cache_exchange_rate:
        current_lifetime = int(perf_counter() - cache_exchange_rate[2])
        if current_lifetime <= InstanceExchangeRateApiSettings.cache_lifetime:
            return cache_exchange_rate[:2]

    return None


async def get_exchange_rate(
        from_currency: CurrencyEnum,
        to_currency: CurrencyEnum
) -> tuple[Decimal, ExchangeRateProviderEnum]:
    key = (from_currency, to_currency)

    rate_and_provider = get_exchange_rate_cache(key)
    if rate_and_provider:
        return rate_and_provider

    async with InstanceExchangeRateApiSettings.lock_response:
        # Double-Checked Locking - проверка до блокировки
        # и повторная проверка после её получения.
        rate_and_provider = get_exchange_rate_cache(key)
        if rate_and_provider:
            return rate_and_provider

        rate_and_provider = await get_exchange_rate_api(from_currency, to_currency)
        if rate_and_provider:
            return rate_and_provider

    return RESERVE_EXCHANGE_RATE.get(key)


async def convert_using_exchange_rate(
        balance: Decimal,
        from_currency: CurrencyEnum,
        to_currency: CurrencyEnum
) -> tuple[Decimal, ExchangeRateProviderEnum]:
    """
    Конвертирует сумму между валютами и возвращает результат вместе
    с источником курса обмена.

    Последовательность получения курса:
    1. Выполняется попытка получить актуальный курс из кэша.
    2. Если кэш отсутствует или устарел, только одна корутина
       обновляет его через asyncio.Lock, остальные ожидают завершения
       обновления и повторно проверяют кэш.
    3. При успешном обращении к внешнему API кэш полностью
       обновляется для всех поддерживаемых валют.
    4. Если API временно недоступно, используется время восстановления,
       в течение которого повторные обращения к API не выполняются.
    5. При невозможности получить актуальные данные используется
       резервный курс, встроенный в приложение.

    Возвращаемый provider указывает источник использованного курса
    (API или APP - резервное значение приложения).
    """
    rate, provider = await get_exchange_rate(from_currency, to_currency)
    converted_balance_and_provider = (round(rate * balance, WalletRules.balance_length_after_point), provider)
    return converted_balance_and_provider
