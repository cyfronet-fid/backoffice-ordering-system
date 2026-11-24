import json
import logging
import sys
from datetime import datetime, timezone
from functools import wraps
from typing import Any, Callable


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger_name": record.name,
            "message": record.getMessage(),
        }

        if record.exc_info and record.exc_info[0] is not None:
            exc_type, exc_value, _ = record.exc_info

            log_entry["exception_type"] = exc_type.__name__
            log_entry["exception_message"] = str(exc_value)
            log_entry["stack_trace"] = self.formatException(record.exc_info)

        # Add basic uvicorn/fastapi request context if present
        if hasattr(record, "request_meta"):
            log_entry["request"] = record.request_meta

        fields = (
            "method",
            "path",
            "status_code",
            "duration_ms",
            "task",
            "message_id",
            "order_id",
            "operation",
            "smtp_host",
            "smtp_port",
            "recipient_count",
            "failure_count",
            "success_count",
            "exception_type",
            "missing_settings",
        )
        for field in fields:
            value = getattr(record, field, None)
            if value is not None:
                log_entry[field] = value

        return json.dumps(log_entry, default=str, ensure_ascii=False)


def setup_logging() -> None:
    """Configures root logger to output JSON logs."""
    root_logger = logging.getLogger()
    # Remove existing handlers to avoid duplicates
    if root_logger.handlers:
        for handler in root_logger.handlers:
            root_logger.removeHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)

    # Force uvicorn loggers to use root handlers instead of their own colored handlers
    for logger_name in ("uvicorn", "uvicorn.access", "uvicorn.error", "fastapi"):
        l = logging.getLogger(logger_name)
        l.handlers = []
        l.propagate = True


def log_background_task_exceptions(func: Callable) -> Callable:
    """Decorator for BackgroundTasks to log any exceptions they throw."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger = logging.getLogger(__name__)
            context = {
                key: value
                for key, value in kwargs.items()
                if key in {"message_id", "order_id"} and isinstance(value, (str, int))
            }
            logger.exception(
                "Background task failed",
                extra={"task": func.__name__, "exception_type": type(e).__name__, **context},
            )
            raise e

    return wrapper
