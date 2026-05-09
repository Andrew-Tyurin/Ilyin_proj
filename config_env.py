from pathlib import Path

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class SettingsPsql(BaseSettings ):
    DB_URL_ASYNCPG: PostgresDsn | None = None
    DB_URL_PSYCOPG: PostgresDsn | None = None

    @property
    def DB_URL_ASYNCPG_STR(self) -> str:
        return str(self.DB_URL_ASYNCPG)

    @property
    def DB_URL_PSYCOPG_STR(self) -> str:
        return str(self.DB_URL_PSYCOPG)

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent / '.env',
        env_file_encoding='utf-8',
        extra="ignore"
    )


class SettingsSecretKey(BaseSettings):
    SECRET_KEY: str | None = None

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent / '.env',
        env_file_encoding='utf-8',
        extra="ignore"
    )


settings_psql = SettingsPsql()
settings_secret_key = SettingsSecretKey()
