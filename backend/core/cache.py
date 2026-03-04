"""
In-Memory Cache for Market Data and Recommendations
Thread-safe, TTL-based cache to reduce external API calls.
"""
import time
import logging
from datetime import datetime
from typing import Any, Optional, Dict

from core.config import settings

logger = logging.getLogger(__name__)


class TTLCache:
    """Simple time-to-live cache backed by a dict."""

    def __init__(self, default_ttl_seconds: int = 3600):
        self._store: Dict[str, Dict[str, Any]] = {}
        self._default_ttl = default_ttl_seconds

    def get(self, key: str) -> Optional[Any]:
        entry = self._store.get(key)
        if entry is None:
            return None
        if time.time() > entry["expires"]:
            del self._store[key]
            return None
        return entry["value"]

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        self._store[key] = {
            "value": value,
            "expires": time.time() + (ttl or self._default_ttl),
            "created": datetime.utcnow().isoformat(),
        }

    def invalidate(self, key: str) -> None:
        self._store.pop(key, None)

    def clear(self) -> None:
        self._store.clear()

    @property
    def size(self) -> int:
        # Prune expired entries first
        now = time.time()
        expired = [k for k, v in self._store.items() if now > v["expires"]]
        for k in expired:
            del self._store[k]
        return len(self._store)


# Module-level singleton caches
market_data_cache = TTLCache(default_ttl_seconds=settings.MARKET_DATA_CACHE_MINUTES * 60)
recommendation_cache = TTLCache(default_ttl_seconds=settings.MODEL_CACHE_HOURS * 3600)


def get_or_fetch_market_data(key: str, fetcher_fn, *args, **kwargs) -> Any:
    """Return cached market data or call *fetcher_fn* and cache the result."""
    cached = market_data_cache.get(key)
    if cached is not None:
        logger.debug(f"Cache HIT for market data key={key}")
        return cached

    logger.debug(f"Cache MISS for market data key={key}, fetching…")
    data = fetcher_fn(*args, **kwargs)
    if data is not None:
        market_data_cache.set(key, data)
    return data


def get_or_compute_recommendation(key: str, generator_fn, *args, **kwargs) -> Any:
    """Return cached recommendation or generate a new one."""
    if not settings.ENABLE_RECOMMENDATION_CACHING:
        return generator_fn(*args, **kwargs)

    cached = recommendation_cache.get(key)
    if cached is not None:
        logger.debug(f"Cache HIT for recommendation key={key}")
        return cached

    logger.debug(f"Cache MISS for recommendation key={key}, computing…")
    result = generator_fn(*args, **kwargs)
    if result is not None:
        recommendation_cache.set(key, result)
    return result
