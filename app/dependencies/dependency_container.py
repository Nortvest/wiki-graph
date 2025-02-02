from logging import Logger

from app.dependencies.services.logger import get_logger, LogLevel


class DependencyContainer:
    _logger: Logger | None = None

    log_level: str = "INFO"

    def __init__(self):
        pass

    def configure_logger(self, log_level: LogLevel) -> None:
        self.log_level = log_level

    @property
    def logger(self) -> Logger:
        if not self._logger:
            self._logger = get_logger(self.log_level)
        return self._logger
