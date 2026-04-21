"""Reusable retry decorator built on `tenacity`.

Centralising retry policy means every adapter behaves consistently when Azure
services throttle / transient-fail.
"""
from __future__ import annotations

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)


def with_retry(exceptions: type[BaseException] | tuple[type[BaseException], ...] = Exception):
    """Exponential back-off retry: 3 attempts, 1s -> 2s -> 4s."""
    return retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        retry=retry_if_exception_type(exceptions),
    )
