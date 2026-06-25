from dataclasses import dataclass
from decimal import Decimal

from app.config_env import secret_key_env, psql_env, APP_ENV


@dataclass(frozen=True)
class StartAppSettings:
    app: str = "main:app"
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True
    workers: int = 1


@dataclass(frozen=True)
class JWTokenSettings:
    secret_key: str = secret_key_env.SECRET_KEY
    time_minutes: int = 15
    algorithm: str = "HS256"


@dataclass(frozen=True)
class SaDbSettings:
    app_env: str | None = APP_ENV
    database_url: str = psql_env.async_db_url_str
    pool_size: int = 3
    max_overflow: int = 2
    echo: bool = False


@dataclass(frozen=True)
class ExchangeRateSettings:
    cache_lifetime: int = 120
    timeout_response: int = 5
    usd_to_rub: Decimal = Decimal("75.00")
    usd_to_eur: Decimal = Decimal("0.85")
    eur_to_rub: Decimal = Decimal("85.00")
    eur_to_usd: Decimal = Decimal("1.15")
    rub_to_usd: Decimal = Decimal("0.0134")
    rub_to_eur: Decimal = Decimal("0.0118")
    rub_to_rub: Decimal = Decimal("1.00")
    eur_to_eur: Decimal = Decimal("1.00")
    usd_to_usd: Decimal = Decimal("1.00")
