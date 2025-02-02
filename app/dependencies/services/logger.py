import sys
from logging import Logger
from typing import Literal

from loguru import logger

type LogLevel = Literal["TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


def get_logger(level: LogLevel) -> Logger:
    logger.add(sys.stderr, level=level)
    return logger
