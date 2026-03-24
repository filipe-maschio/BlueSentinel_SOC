import os
import logging
from logging import Formatter
from logging.handlers import RotatingFileHandler

from shared.paths import LOGS_DIR


class MaxLevelFilter(logging.Filter):
    def __init__(self, max_level):
        super().__init__()
        self.max_level = max_level

    def filter(self, record):
        return record.levelno <= self.max_level


class ExactLoggerNameFilter(logging.Filter):
    def __init__(self, logger_names):
        super().__init__()
        self.logger_names = set(logger_names)

    def filter(self, record):
        return record.name in self.logger_names


class ExcludeLoggerNameFilter(logging.Filter):
    def __init__(self, logger_names):
        super().__init__()
        self.logger_names = set(logger_names)

    def filter(self, record):
        return record.name not in self.logger_names


def _build_formatter():
    return Formatter(
        "%(asctime)s | %(levelname)-5s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def _build_rotating_handler(file_path, level, formatter, max_bytes=2_000_000, backup_count=5):
    handler = RotatingFileHandler(
        file_path,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    handler.setLevel(level)
    handler.setFormatter(formatter)
    return handler


def setup_logging():
    os.makedirs(LOGS_DIR, exist_ok=True)

    formatter = _build_formatter()

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    if root_logger.handlers:
        root_logger.handlers.clear()

    soc_log_file = os.path.join(LOGS_DIR, "soc.log")
    execution_log_file = os.path.join(LOGS_DIR, "execution.log")
    error_log_file = os.path.join(LOGS_DIR, "error.log")

    scheduler_logger_names = {"__main__", "scheduler"}

    # Console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # soc.log -> visão executiva
    soc_handler = _build_rotating_handler(
        soc_log_file,
        level=logging.INFO,
        formatter=formatter,
    )
    soc_handler.addFilter(MaxLevelFilter(logging.INFO))
    soc_handler.addFilter(ExactLoggerNameFilter(scheduler_logger_names))
    root_logger.addHandler(soc_handler)

    # execution.log -> detalhe técnico
    execution_handler = _build_rotating_handler(
        execution_log_file,
        level=logging.INFO,
        formatter=formatter,
    )
    execution_handler.addFilter(MaxLevelFilter(logging.INFO))
    execution_handler.addFilter(ExcludeLoggerNameFilter(scheduler_logger_names))
    root_logger.addHandler(execution_handler)

    # error.log -> somente erros e tracebacks
    error_handler = _build_rotating_handler(
        error_log_file,
        level=logging.ERROR,
        formatter=formatter,
    )
    root_logger.addHandler(error_handler)