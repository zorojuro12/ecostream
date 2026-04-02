"""Tests for structured JSON logging configuration."""
import json
import logging

from app.utils.logging_config import JsonFormatter


def test_json_formatter_outputs_valid_json_with_required_fields():
    formatter = JsonFormatter()
    record = logging.LogRecord(
        name="app.services.forecasting_service",
        level=logging.INFO,
        pathname="forecasting_service.py",
        lineno=42,
        msg="ETA calculated: %.1f min",
        args=(25.5,),
        exc_info=None,
    )
    output = formatter.format(record)
    parsed = json.loads(output)

    assert parsed["level"] == "INFO"
    assert parsed["logger"] == "app.services.forecasting_service"
    assert "25.5" in parsed["message"]
    assert "timestamp" in parsed


def test_json_formatter_includes_exception_when_present():
    formatter = JsonFormatter()
    try:
        raise ValueError("bad input")
    except ValueError:
        import sys

        exc_info = sys.exc_info()

    record = logging.LogRecord(
        name="test",
        level=logging.ERROR,
        pathname="test.py",
        lineno=1,
        msg="Something failed",
        args=(),
        exc_info=exc_info,
    )
    output = formatter.format(record)
    parsed = json.loads(output)

    assert parsed["level"] == "ERROR"
    assert "exception" in parsed
    assert "ValueError" in parsed["exception"]
