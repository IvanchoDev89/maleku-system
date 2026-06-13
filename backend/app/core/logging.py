"""
Structured logging configuration
Replaces print statements with proper logging
"""

import logging
import json
import sys
from datetime import datetime, timezone
from typing import Any, Dict


class JSONFormatter(logging.Formatter):
    """
    JSON formatter for structured logging.
    Outputs logs as JSON for easier parsing by log aggregators.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_obj: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add extra fields if present
        if hasattr(record, "extra"):
            log_obj.update(record.extra)

        # Add exception info if present
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        # Add file location for debugging
        if record.levelno >= logging.WARNING:
            log_obj["source"] = {
                "file": record.filename,
                "line": record.lineno,
                "function": record.funcName,
            }

        return json.dumps(log_obj, default=str)


class SimpleFormatter(logging.Formatter):
    """
    Simple colored formatter for development.
    """

    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
        "RESET": "\033[0m",
    }

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
        reset = self.COLORS["RESET"]

        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        log_message = f"{color}[{timestamp}] {record.levelname:8} | {record.name:20} | {record.getMessage()}{reset}"

        if record.exc_info:
            log_message += f"\n{self.formatException(record.exc_info)}"

        return log_message


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.
    """
    return logging.getLogger(name)


def setup_logging(
    level: str = "INFO", json_format: bool = False, log_file: str = None
) -> None:
    """
    Setup application logging.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_format: Use JSON formatting for production
        log_file: Optional file to write logs to
    """
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    root_logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))

    if json_format:
        console_handler.setFormatter(JSONFormatter())
    else:
        console_handler.setFormatter(SimpleFormatter())

    root_logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(file_handler)

    # Suppress noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    # Log startup message
    logger = get_logger(__name__)
    logger.info(
        "Logging configured",
        extra={
            "level": level,
            "json_format": json_format,
            "file_logging": bool(log_file),
        },
    )


def log_request(
    logger: logging.Logger,
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    user_id: str = None,
    extra: Dict = None,
) -> None:
    """
    Log an HTTP request.
    """
    log_data = {
        "method": method,
        "path": path,
        "status_code": status_code,
        "duration_ms": round(duration_ms, 2),
    }

    if user_id:
        log_data["user_id"] = str(user_id)

    if extra:
        log_data.update(extra)

    level = logging.INFO if status_code < 400 else logging.WARNING

    logger.log(level, f"{method} {path} - {status_code}", extra={"request": log_data})


def log_error(
    logger: logging.Logger, message: str, error: Exception = None, context: Dict = None
) -> None:
    """
    Log an error with context.
    """
    log_data = {"message": message}

    if error:
        log_data["error_type"] = type(error).__name__
        log_data["error_message"] = str(error)

    if context:
        log_data["context"] = context

    logger.error(message, extra={"error": log_data})


def log_security_event(
    logger: logging.Logger,
    event_type: str,
    user_id: str = None,
    ip_address: str = None,
    details: Dict = None,
) -> None:
    """
    Log a security-related event.
    """
    log_data = {
        "event_type": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    if user_id:
        log_data["user_id"] = str(user_id)
    if ip_address:
        log_data["ip_address"] = ip_address
    if details:
        log_data["details"] = details

    logger.warning(f"Security event: {event_type}", extra={"security": log_data})
