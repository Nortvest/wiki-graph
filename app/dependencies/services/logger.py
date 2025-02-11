import sys
from logging import Logger
from typing import Literal

from loguru import logger

type LogLevel = Literal["TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


def get_logger(level: LogLevel) -> Logger:
    logger.remove()
    logger.add(sys.stdout, level=level)
    return logger
