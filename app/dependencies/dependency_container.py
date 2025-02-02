from logging import Logger

from app.dependencies.services.logger import LogLevel, get_logger


class DependencyContainer:
    _logger: Logger | None = None

    log_level: str = "INFO"

    @classmethod
    def configure_logger(cls, log_level: LogLevel) -> None:
        cls.log_level = log_level

    @property
    def logger(self) -> Logger:
        if not self._logger:
            self._logger = get_logger(self.log_level)
        return self._logger
