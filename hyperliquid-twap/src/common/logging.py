"""Structured logging configuration."""

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any, Dict


class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add any extra fields
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)
        
        return json.dumps(log_data)


def setup_structured_logging(level: str = "INFO", use_json: bool = True):
    """
    Configure structured logging for the application.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        use_json: If True, use JSON formatter; if False, use human-readable format
    """
    # Remove existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    
    if use_json:
        # Use JSON formatter
        formatter = StructuredFormatter()
    else:
        # Use human-readable format with structured fields
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, level.upper()))
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the given name.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


class StructuredLogger:
    """Wrapper for structured logging with extra fields."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def _log(self, level: int, message: str, **extra_fields):
        """Log with extra structured fields."""
        record = self.logger.makeRecord(
            self.logger.name,
            level,
            "(unknown file)",
            0,
            message,
            (),
            None
        )
        record.extra_fields = extra_fields
        self.logger.handle(record)
    
    def debug(self, message: str, **extra_fields):
        """Log debug message with extra fields."""
        self._log(logging.DEBUG, message, **extra_fields)
    
    def info(self, message: str, **extra_fields):
        """Log info message with extra fields."""
        self._log(logging.INFO, message, **extra_fields)
    
    def warning(self, message: str, **extra_fields):
        """Log warning message with extra fields."""
        self._log(logging.WARNING, message, **extra_fields)
    
    def error(self, message: str, **extra_fields):
        """Log error message with extra fields."""
        self._log(logging.ERROR, message, **extra_fields)
    
    def critical(self, message: str, **extra_fields):
        """Log critical message with extra fields."""
        self._log(logging.CRITICAL, message, **extra_fields)
