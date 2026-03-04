"""
Structured Logging Configuration
Provides JSON-formatted logs for production and human-readable logs for development.
"""
import json
import logging
import sys
import time
from datetime import datetime, timezone
from typing import Optional

from core.config import settings


class JSONFormatter(logging.Formatter):
    """JSON log formatter for production environments."""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage(),
        }
        if record.exc_info and record.exc_info[1]:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data)


class HumanFormatter(logging.Formatter):
    """Human-readable formatter for development environments."""

    FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s"

    def __init__(self):
        super().__init__(fmt=self.FORMAT, datefmt="%Y-%m-%d %H:%M:%S")


def setup_logging(log_level: Optional[str] = None, log_format: Optional[str] = None) -> None:
    """
    Configure application-wide logging.

    Args:
        log_level: Override log level (default from settings)
        log_format: 'json' for production, anything else for human-readable
    """
    level = getattr(logging, (log_level or settings.LOG_LEVEL).upper(), logging.INFO)
    fmt = log_format or settings.LOG_FORMAT

    root = logging.getLogger()
    root.setLevel(level)
    # Remove existing handlers to avoid duplicate logs
    root.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    if fmt == "json":
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(HumanFormatter())

    root.addHandler(handler)

    # Silence noisy third-party loggers
    for noisy in ("urllib3", "yfinance", "peewee", "httpcore"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


class RequestTimer:
    """Context manager to time request processing."""

    def __init__(self, label: str = "request"):
        self.label = label
        self.start: float = 0.0
        self.elapsed: float = 0.0

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, *exc):
        self.elapsed = time.perf_counter() - self.start
        return False

    @property
    def elapsed_ms(self) -> float:
        return self.elapsed * 1000
