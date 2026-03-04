"""
Rate Limiting Module
Simple in-memory rate limiter for API endpoints.
Uses sliding window counters per client IP.
"""
import time
import logging
from collections import defaultdict
from typing import Dict, List

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from core.config import settings

logger = logging.getLogger(__name__)


class _SlidingWindowCounter:
    """Tracks request counts within a sliding time window."""

    def __init__(self):
        self._requests: Dict[str, List[float]] = defaultdict(list)

    def _cleanup(self, key: str, window_seconds: float) -> None:
        cutoff = time.time() - window_seconds
        self._requests[key] = [t for t in self._requests[key] if t > cutoff]

    def is_allowed(self, key: str, max_requests: int, window_seconds: float) -> bool:
        self._cleanup(key, window_seconds)
        if len(self._requests[key]) >= max_requests:
            return False
        self._requests[key].append(time.time())
        return True

    def remaining(self, key: str, max_requests: int, window_seconds: float) -> int:
        self._cleanup(key, window_seconds)
        return max(0, max_requests - len(self._requests[key]))


# Module-level singleton
_counter = _SlidingWindowCounter()


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Applies per-minute and per-hour rate limits from settings.
    Injects standard rate-limit headers into every response.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip rate limiting for health/docs endpoints
        skip_paths = {"/", "/health", "/docs", "/openapi.json", "/redoc"}
        if request.url.path in skip_paths:
            return await call_next(request)

        ip = _client_ip(request)

        per_min = settings.RATE_LIMIT_PER_MINUTE
        per_hour = settings.RATE_LIMIT_PER_HOUR

        if not _counter.is_allowed(f"{ip}:min", per_min, 60):
            logger.warning(f"Rate limit exceeded (per-minute) for {ip}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Try again in a minute.",
            )

        if not _counter.is_allowed(f"{ip}:hr", per_hour, 3600):
            logger.warning(f"Rate limit exceeded (per-hour) for {ip}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Hourly rate limit exceeded. Try again later.",
            )

        response: Response = await call_next(request)

        remaining_min = _counter.remaining(f"{ip}:min", per_min, 60)
        response.headers["X-RateLimit-Limit"] = str(per_min)
        response.headers["X-RateLimit-Remaining"] = str(remaining_min)
        return response
