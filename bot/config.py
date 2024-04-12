import os
from dotenv import find_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr, PostgresDsn, RedisDsn, conint


class Settings(BaseSettings):

    BOT_TOKEN: SecretStr

    POSTGRES_DSN: PostgresDsn
    REDIS_DSN: RedisDsn

    LOG_DIRECTORY: str  # validation?
    LOG_FILENAME: str  # validation?
    LOG_MAXBYTES: conint(ge=1, le=1_000_000_000)
    LOG_BACKUPS: conint(ge=0, le=1000)

    RESET_POSTGRES_ON_STARTUP: bool
    RESET_REDIS_ON_STARTUP: bool

    model_config = SettingsConfigDict(
        env_file=find_dotenv('.env'),
        env_file_encoding='utf-8',
        case_sensitive=True
    )


config = Settings()
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
CURRENCY_DATA_PATH = os.path.join(ROOT_DIR, "data", "currency.json")
