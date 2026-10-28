"""High-performance Redis and In-Memory caching layer for MedOracle (Step 9.1).

Provides:
1. Universal CacheManager supporting Redis backend with automatic in-memory
   LRU/TTL fallback for local Windows environments without Docker.
2. Serialization helpers for SQLAlchemy ORM models avoiding DetachedInstanceError.
3. Database query caching for patient profiles, medical histories, and lab results
   with automated cache invalidation on write/update operations.
4. Foundation for multi-agent LangGraph debate state checkpointer (Step 14).
"""

from abc import ABC, abstractmethod
import copy
from datetime import date, datetime, timezone
import fnmatch
import json
import logging
import threading
import time
from typing import Any, Dict, List, Optional, Tuple, Type

try:
    import redis
except ImportError:
    redis = None  # type: ignore

from app.core.config import get_settings

logger = logging.getLogger("cache_service")


# =============================================================================
# JSON Serialization Helpers for Models & Dates
# =============================================================================
class CacheJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder handling datetimes, dates, UUIDs, and Sets."""

    def default(self, o: Any) -> Any:
        if isinstance(o, (datetime, date)):
            return o.isoformat()
        if hasattr(o, "hex"):  # UUID
            return str(o)
        if isinstance(o, set):
            return list(o)
        return super().default(o)


def serialize_data(value: Any) -> str:
    """Serialize Python object to JSON string."""
    return json.dumps(value, cls=CacheJSONEncoder)


def deserialize_data(payload: str) -> Any:
    """Deserialize JSON string to Python object."""
    return json.loads(payload)


def model_to_dict(model: Any) -> Optional[Dict[str, Any]]:
    """Extract column-level data dictionary from a SQLAlchemy ORM model instance."""
    if model is None:
        return None
    if not hasattr(model, "__table__"):
        if isinstance(model, dict):
            return model
        return None

    data: Dict[str, Any] = {}
    for col in model.__table__.columns:
        val = getattr(model, col.name, None)
        if isinstance(val, (datetime, date)):
            data[col.name] = val.isoformat()
        else:
            data[col.name] = val
    return data


def dict_to_model(model_cls: Type[Any], data: Optional[Dict[str, Any]]) -> Optional[Any]:
    """Reconstruct an unmanaged ORM model instance from a cached data dictionary."""
    if data is None or not isinstance(data, dict):
        return None
    if not hasattr(model_cls, "__table__"):
        return None

    from sqlalchemy import Date, DateTime

    parsed: Dict[str, Any] = {}
    for k, val in data.items():
        if val is not None and k in model_cls.__table__.columns:
            col_type = model_cls.__table__.columns[k].type
            if isinstance(col_type, (DateTime, Date)) and isinstance(val, str):
                try:
                    if isinstance(col_type, DateTime):
                        parsed[k] = datetime.fromisoformat(val)
                    else:
                        parsed[k] = date.fromisoformat(val)
                except Exception:
                    parsed[k] = val
            else:
                parsed[k] = val
        elif k in model_cls.__table__.columns:
            parsed[k] = val

    return model_cls(**parsed)


# =============================================================================
# Cache Backend Protocol / Base Class
# =============================================================================
class BaseCacheBackend(ABC):
    """Abstract caching backend protocol."""

    @abstractmethod
    def get(self, key: str) -> Optional[str]:
        """Retrieve raw cached string value or None."""
        pass

    @abstractmethod
    def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        """Store string value with optional TTL in seconds."""
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete specific key."""
        pass

    @abstractmethod
    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern (e.g. 'medoracle:db:patient:*')."""
        pass

    @abstractmethod
    def clear(self) -> bool:
        """Clear all keys in backend."""
        pass

    @abstractmethod
    def is_healthy(self) -> bool:
        """Check if backend connection is active and operational."""
        pass

    @property
    @abstractmethod
    def backend_name(self) -> str:
        """Return backend identifier ('redis' or 'in_memory')."""
        pass


# =============================================================================
# In-Memory Cache Backend (Resilient Windows Fallback)
# =============================================================================
class InMemoryCacheBackend(BaseCacheBackend):
    """Thread-safe in-memory cache with TTL expiration and pattern deletion."""

    def __init__(self):
        self._store: Dict[str, Tuple[str, Optional[float]]] = {}
        self._lock = threading.RLock()

    @property
    def backend_name(self) -> str:
        return "in_memory"

    def is_healthy(self) -> bool:
        return True

    def _is_expired(self, expiry: Optional[float]) -> bool:
        if expiry is None:
            return False
        return time.time() > expiry

    def get(self, key: str) -> Optional[str]:
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            val, expiry = entry
            if self._is_expired(expiry):
                del self._store[key]
                return None
            return val

    def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        with self._lock:
            expiry = time.time() + ttl if ttl and ttl > 0 else None
            self._store[key] = (value, expiry)
            return True

    def delete(self, key: str) -> bool:
        with self._lock:
            if key in self._store:
                del self._store[key]
                return True
            return False

    def delete_pattern(self, pattern: str) -> int:
        with self._lock:
            deleted_count = 0
            matching_keys = [k for k in self._store.keys() if fnmatch.fnmatch(k, pattern)]
            for k in matching_keys:
                del self._store[k]
                deleted_count += 1
            return deleted_count

    def clear(self) -> bool:
        with self._lock:
            self._store.clear()
            return True


# =============================================================================
# Redis Cache Backend
# =============================================================================
class RedisCacheBackend(BaseCacheBackend):
    """Redis cache backend client using redis-py with connection pooling."""

    def __init__(self, redis_url: str):
        if redis is None:
            raise ImportError("The 'redis' package is required for RedisCacheBackend.")
        self.redis_url = redis_url
        self._client: Optional[redis.Redis] = None
        self._init_client()

    def _init_client(self) -> None:
        try:
            self._client = redis.Redis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_connect_timeout=2.0,
                socket_timeout=3.0,
            )
            # Test ping
            self._client.ping()
            logger.info("Successfully connected to Redis cache at %s", self.redis_url)
        except Exception as e:
            logger.warning("Could not connect to Redis at %s (%s). Will degrade gracefully.", self.redis_url, e)
            self._client = None

    @property
    def backend_name(self) -> str:
        return "redis"

    def is_healthy(self) -> bool:
        if self._client is None:
            return False
        try:
            return bool(self._client.ping())
        except Exception:
            return False

    def get(self, key: str) -> Optional[str]:
        if not self.is_healthy():
            return None
        try:
            return self._client.get(key)  # type: ignore
        except Exception as e:
            logger.warning("Redis GET failed for key %s: %s", key, e)
            return None

    def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        if not self.is_healthy():
            return False
        try:
            if ttl and ttl > 0:
                return bool(self._client.setex(key, ttl, value))  # type: ignore
            return bool(self._client.set(key, value))  # type: ignore
        except Exception as e:
            logger.warning("Redis SET failed for key %s: %s", key, e)
            return False

    def delete(self, key: str) -> bool:
        if not self.is_healthy():
            return False
        try:
            return bool(self._client.delete(key))  # type: ignore
        except Exception as e:
            logger.warning("Redis DELETE failed for key %s: %s", key, e)
            return False

    def delete_pattern(self, pattern: str) -> int:
        if not self.is_healthy():
            return 0
        try:
            keys = list(self._client.scan_iter(match=pattern))  # type: ignore
            if keys:
                return int(self._client.delete(*keys))  # type: ignore
            return 0
        except Exception as e:
            logger.warning("Redis DELETE_PATTERN failed for %s: %s", pattern, e)
            return 0

    def clear(self) -> bool:
        if not self.is_healthy():
            return False
        try:
            return bool(self._client.flushdb())  # type: ignore
        except Exception as e:
            logger.warning("Redis CLEAR failed: %s", e)
            return False


# =============================================================================
# Unified Cache Manager Singleton
# =============================================================================
class CacheManager:
    """Unified application cache manager supporting Redis with In-Memory fallback."""

    _instance: Optional["CacheManager"] = None
    _lock = threading.Lock()

    def __init__(self, backend: Optional[BaseCacheBackend] = None):
        settings = get_settings()
        self.enabled = settings.redis_cache_enabled
        self.prefix = settings.redis_key_prefix or "medoracle"
        self.default_ttl = settings.redis_default_ttl or 600

        self.hits = 0
        self.misses = 0

        if backend is not None:
            self._backend = backend
        else:
            self._backend = self._resolve_backend(settings.redis_url)

    def _resolve_backend(self, redis_url: Optional[str]) -> BaseCacheBackend:
        """Resolve backend based on configuration and availability."""
        if redis_url and redis is not None:
            try:
                candidate = RedisCacheBackend(redis_url=redis_url)
                if candidate.is_healthy():
                    return candidate
            except Exception as e:
                logger.warning("Failed initializing RedisCacheBackend (%s). Falling back to memory.", e)

        logger.info("Using InMemoryCacheBackend (zero-downtime local Windows fallback).")
        return InMemoryCacheBackend()

    @classmethod
    def get_instance(cls) -> "CacheManager":
        """Return thread-safe singleton CacheManager instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Reset singleton instance (useful for unit test isolation)."""
        with cls._lock:
            cls._instance = None

    @property
    def backend_type(self) -> str:
        """Return the active backend name ('redis' or 'in_memory')."""
        return self._backend.backend_name

    def is_healthy(self) -> bool:
        """Return health status of current backend."""
        return self._backend.is_healthy()

    def build_key(self, namespace: str, *parts: Any) -> str:
        """Generate standardized namespaced cache key.

        Format: `{prefix}:{namespace}:{part1}:{part2}:...`
        Example: `medoracle:db:patient:usr_123`
        """
        clean_parts = [str(p).strip() for p in parts if p is not None]
        return f"{self.prefix}:{namespace}:{':'.join(clean_parts)}"

    # -------------------------------------------------------------------------
    # Generic Cache Operations
    # -------------------------------------------------------------------------
    def get(self, key: str) -> Optional[Any]:
        """Retrieve and deserialize value by key."""
        if not self.enabled:
            return None

        raw = self._backend.get(key)
        if raw is None:
            self.misses += 1
            return None

        try:
            val = deserialize_data(raw)
            self.hits += 1
            return val
        except Exception as e:
            logger.warning("Failed deserializing cache key %s: %s", key, e)
            self.misses += 1
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Serialize and store value with specified or default TTL."""
        if not self.enabled or value is None:
            return False

        effective_ttl = ttl if ttl is not None else self.default_ttl
        try:
            raw = serialize_data(value)
            return self._backend.set(key, raw, ttl=effective_ttl)
        except Exception as e:
            logger.warning("Failed serializing cache key %s: %s", key, e)
            return False

    def delete(self, key: str) -> bool:
        """Remove a single key from cache."""
        return self._backend.delete(key)

    def delete_pattern(self, pattern: str) -> int:
        """Remove all keys matching pattern."""
        return self._backend.delete_pattern(pattern)

    def invalidate_namespace(self, namespace: str) -> int:
        """Invalidate all keys under a specific namespace (e.g. 'db:patient:*')."""
        pattern = f"{self.prefix}:{namespace}:*"
        return self.delete_pattern(pattern)

    def clear(self) -> bool:
        """Flush the entire cache store."""
        return self._backend.clear()

    # -------------------------------------------------------------------------
    # Database ORM Model Cache Helpers
    # -------------------------------------------------------------------------
    def get_model(self, key: str, model_cls: Type[Any]) -> Optional[Any]:
        """Retrieve and reconstruct an ORM model instance from cache."""
        cached_dict = self.get(key)
        if cached_dict is None or not isinstance(cached_dict, dict):
            return None
        return dict_to_model(model_cls, cached_dict)

    def set_model(self, key: str, model: Any, ttl: Optional[int] = None) -> bool:
        """Serialize and cache a SQLAlchemy ORM model instance as a dictionary."""
        model_dict = model_to_dict(model)
        if model_dict is None:
            return False
        return self.set(key, model_dict, ttl=ttl)

    def get_model_list(self, key: str, model_cls: Type[Any]) -> Optional[List[Any]]:
        """Retrieve and reconstruct a list of ORM model instances from cache."""
        cached_list = self.get(key)
        if cached_list is None or not isinstance(cached_list, list):
            return None
        return [dict_to_model(model_cls, item) for item in cached_list if isinstance(item, dict)]

    def set_model_list(self, key: str, models: List[Any], ttl: Optional[int] = None) -> bool:
        """Serialize and cache a list of SQLAlchemy ORM models."""
        dict_list = [model_to_dict(m) for m in models if m is not None]
        return self.set(key, dict_list, ttl=ttl)

    def get_stats(self) -> Dict[str, Any]:
        """Return operational cache statistics."""
        total = self.hits + self.misses
        hit_ratio = round((self.hits / total) * 100, 2) if total > 0 else 0.0
        return {
            "backend": self.backend_type,
            "is_healthy": self.is_healthy(),
            "enabled": self.enabled,
            "prefix": self.prefix,
            "default_ttl": self.default_ttl,
            "hits": self.hits,
            "misses": self.misses,
            "hit_ratio_pct": hit_ratio,
        }


def get_cache_manager() -> CacheManager:
    """Return the singleton CacheManager instance."""
    return CacheManager.get_instance()

