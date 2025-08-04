import logging
import sys


class StructuredFormatter(logging.Formatter):
    """Clean structured formatter for console and file log outputs."""

    COLOR_CODES = {
        logging.DEBUG: "\033[36m",  # Cyan
        logging.INFO: "\033[32m",  # Green
        logging.WARNING: "\033[33m",  # Yellow
        logging.ERROR: "\033[31m",  # Red
        logging.CRITICAL: "\033[41m",  # Red background
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        level_name = record.levelname
        message = record.getMessage()
        time_str = self.formatTime(record, "%Y-%m-%d %H:%M:%S")
        name = record.name

        color = self.COLOR_CODES.get(record.levelno, self.RESET)
        formatted = f"{time_str} | {color}{level_name:<8}{self.RESET} | {name} - {message}"

        if record.exc_info:
            formatted += "\n" + self.formatException(record.exc_info)
        return formatted


def setup_logging(level: int = logging.INFO) -> None:
    """Initializes root logger with structured formatting."""
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(StructuredFormatter())
    root_logger.addHandler(console_handler)

    # Quieten chatty third-party loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("botocore").setLevel(logging.WARNING)
    logging.getLogger("s3transfer").setLevel(logging.WARNING)
    logging.getLogger("passlib").setLevel(logging.WARNING)


def get_logger(name: str | None = None) -> logging.Logger:
    """Returns a named logger instance."""
    return logging.getLogger(name or "app")
