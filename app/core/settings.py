from pydantic_settings import BaseSettings as BaseSettingsPydantic
from pydantic_settings import SettingsConfigDict
from typing_extensions import Literal

type LogLevel = Literal["TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class BaseSettings(BaseSettingsPydantic):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


class LoggerConfig(BaseSettings):
    log_level: LogLevel = "INFO"


class GraphDBConfig(BaseSettings):
    graph_db_url: str = "neo4j://localhost:7687"
    graph_db_user: str = ""
    graph_db_password: str = ""
    graph_db_name: str = "neo4j"


class AppConfig(BaseSettings):
    num_page_workers: int = 4


class Settings(BaseSettings):
    app: AppConfig = AppConfig()
    logger: LoggerConfig = LoggerConfig()
    graph_db: GraphDBConfig = GraphDBConfig()
