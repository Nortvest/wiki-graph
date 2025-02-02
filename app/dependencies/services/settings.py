from pydantic_settings import BaseSettings as BaseSettingsPydantic
from pydantic_settings import SettingsConfigDict


class BaseSettings(BaseSettingsPydantic):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


class LoggerConfig(BaseSettings):
    log_level: str = "INFO"


class Settings(BaseSettings):
    logger: LoggerConfig = LoggerConfig()
