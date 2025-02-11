import sys

from loguru import logger
from typing_extensions import Literal, Protocol

type LogLevel = Literal["TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class Logger(Protocol):
    def trace(self, msg: str) -> None:
        raise NotImplementedError

    def debug(self, msg: str) -> None:
        raise NotImplementedError

    def info(self, msg: str, *args: str | int) -> None:
        raise NotImplementedError

    def warning(self, msg: str) -> None:
        raise NotImplementedError

    def error(self, msg: str) -> None:
        raise NotImplementedError

    def critical(self, msg: str) -> None:
        raise NotImplementedError

    def exception(self, msg: str) -> None:
        raise NotImplementedError


def get_logger(level: LogLevel) -> Logger:
    logger.remove()
    logger.add(sys.stdout, level=level)
    return logger
