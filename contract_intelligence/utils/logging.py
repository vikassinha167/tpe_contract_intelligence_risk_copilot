"""
Logging configuration for the Contract Intelligence application.

Uses structlog for structured logging with JSON output.
"""

import logging
import sys
from typing import Any, Dict

import structlog
from contract_intelligence.config.settings import settings


def configure_logging() -> None:
    """
    Configure structured logging for the application.

    Sets up structlog with JSON formatting and appropriate log levels.
    """
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.logging.level.upper()),
    )

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, settings.logging.level.upper())
        ),
        context_class=dict,
        logger_factory=structlog.WriteLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> Any:
    """
    Get a structured logger instance.

    Args:
        name: The name of the logger (usually __name__).

    Returns:
        A structlog logger instance.
    """
    return structlog.get_logger(name)