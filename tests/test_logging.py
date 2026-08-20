import io
import json
import logging

from app.core.logging import JSONFormatter, get_logger, setup_logging


def test_json_formatter_structure():
    """Tests that JSONFormatter emits valid, parseable JSON with all standard keys."""
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JSONFormatter())

    logger = logging.getLogger("test_json_logger")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    logger.info("Structured event occurred")
    handler.flush()

    output = stream.getvalue().strip()
    assert output, "Log output must not be empty"

    log_entry = json.loads(output)
    assert log_entry["level"] == "INFO"
    assert log_entry["logger"] == "test_json_logger"
    assert log_entry["module"] == "test_logging"
    assert log_entry["message"] == "Structured event occurred"
    assert "timestamp" in log_entry


def test_json_formatter_with_exception():
    """Tests exception stack trace formatting in JSON logs."""
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JSONFormatter())

    logger = logging.getLogger("test_exc_logger")
    logger.setLevel(logging.ERROR)
    logger.addHandler(handler)

    try:
        raise ValueError("Simulated DSP calculation error")
    except ValueError:
        logger.exception("Audio processing failed")

    output = stream.getvalue().strip()
    log_entry = json.loads(output)
    assert log_entry["level"] == "ERROR"
    assert "Simulated DSP calculation error" in log_entry["exception"]


def test_get_logger_factory():
    """Tests get_logger factory function returns a configured Logger instance."""
    setup_logging()
    log = get_logger("my_service")
    assert isinstance(log, logging.Logger)
    assert log.name == "my_service"
