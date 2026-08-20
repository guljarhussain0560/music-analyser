import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any

from app.core.config import settings


class JSONFormatter(logging.Formatter):
    """
    Structured JSON log formatter for production observability and log aggregators.
    Outputs log records with timestamp, level, logger name, module, message, and exception stack trace.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_obj: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "module": record.module,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        if hasattr(record, "extra_data") and isinstance(record.extra_data, dict):
            log_obj.update(record.extra_data)
        return json.dumps(log_obj)


def setup_logging() -> None:
    """Configures application root logger with JSON stdout handler."""
    root_logger = logging.getLogger()
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO
    root_logger.setLevel(log_level)

    # Avoid duplicate handlers on re-configuration
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(console_handler)

    # Suppress verbose third-party loggers
    for noisy_pkg in [
        "urllib3",
        "botocore",
        "s3transfer",
        "boto3",
        "multipart",
        "passlib",
        "asyncio",
    ]:
        logging.getLogger(noisy_pkg).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Returns a named logger configured with JSON formatting."""
    return logging.getLogger(name)
