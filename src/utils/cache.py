"""
Redis-backed cache with file fallback.

Redis: fast in-memory caching for hot data (TTL-based)
File:  persistent fallback when Redis is unavailable
"""
import os
import json
import hashlib
import time
from typing import Any, Optional


class SceneCache:
    """
    Hybrid cache: Redis (fast, TTL) → File (persistent fallback).
    Automatically degrades to file-only if Redis is unavailable.
    """

    def __init__(self, cache_dir: str = "data/cache", redis_url: str = "redis://localhost:6379", ttl: int = 3600):
        self.cache_dir = cache_dir
        self.ttl = ttl  # Redis TTL in seconds (default 1 hour)
        os.makedirs(cache_dir, exist_ok=True)

        # File-based manifest
        self.manifest_path = os.path.join(cache_dir, "manifest.json")
        self._manifest = self._load_manifest()

        # Redis connection (lazy, graceful fallback)
        self._redis = None
        self._redis_url = redis_url
        self._redis_available = None  # None = untested

        # Monitoring
        self.stats = {"hits": 0, "misses": 0, "redis_hits": 0, "file_hits": 0, "stores": 0}

    # ── Redis connection ──
    def _get_redis(self):
        if self._redis_available is False:
            return None
        if self._redis is None:
            try:
                import redis
                self._redis = redis.from_url(self._redis_url, decode_responses=True, socket_timeout=2)
                self._redis.ping()
                self._redis_available = True
                print("[Cache] Redis connected")
            except Exception:
                self._redis = None
                self._redis_available = False
                print("[Cache] Redis unavailable — file-only mode")
        return self._redis

    # ── File manifest ──
    def _load_manifest(self) -> dict:
        if os.path.exists(self.manifest_path):
            try:
                with open(self.manifest_path) as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {}

    def _save_manifest(self):
        with open(self.manifest_path, "w") as f:
            json.dump(self._manifest, f, indent=2)

    @staticmethod
    def _hash(data: Any) -> str:
        raw = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def _cache_key(self, stage: str, input_data: Any) -> str:
        return f"creator:{stage}:{self._hash(input_data)}"

    # ── GET ──
    def get(self, stage: str, input_data: Any) -> Optional[dict]:
        """Check Redis first, then file. Returns cached output or None."""
        key = self._cache_key(stage, input_data)

        # Try Redis
        r = self._get_redis()
        if r:
            try:
                cached = r.get(key)
                if cached:
                    self.stats["hits"] += 1
                    self.stats["redis_hits"] += 1
                    print(f"[Cache] REDIS HIT: {stage}")
                    return json.loads(cached)
            except Exception:
                pass

        # Try file
        file_key = f"{stage}:{self._hash(input_data)}"
        entry = self._manifest.get(file_key)
        if entry:
            path = entry.get("path")
            if path and os.path.exists(path):
                try:
                    with open(path) as f:
                        data = json.load(f)
                    # Backfill Redis
                    if r:
                        try:
                            r.setex(key, self.ttl, json.dumps(data, default=str))
                        except Exception:
                            pass
                    self.stats["hits"] += 1
                    self.stats["file_hits"] += 1
                    print(f"[Cache] FILE HIT: {stage}")
                    return data
                except (json.JSONDecodeError, IOError):
                    pass

        self.stats["misses"] += 1
        return None

    # ── SET ──
    def set(self, stage: str, input_data: Any, output_data: dict):
        """Store in both Redis (TTL) and file (persistent)."""
        key = self._cache_key(stage, input_data)

        # Serialize
        try:
            serialized = json.dumps(output_data, default=str)
        except (TypeError, ValueError):
            return  # Non-serializable — skip

        # Redis
        r = self._get_redis()
        if r:
            try:
                r.setex(key, self.ttl, serialized)
            except Exception:
                pass

        # File
        file_key = f"{stage}:{self._hash(input_data)}"
        path = os.path.join(self.cache_dir, f"{stage}_{self._hash(input_data)}.json")
        try:
            with open(path, "w") as f:
                f.write(serialized)
            self._manifest[file_key] = {"path": path, "stage": stage, "ts": time.time()}
            self._save_manifest()
        except IOError:
            pass

        self.stats["stores"] += 1
        print(f"[Cache] STORED: {stage}")

    # ── INVALIDATE ──
    def invalidate(self, stage: str = None):
        """Clear cache for a stage or all."""
        r = self._get_redis()

        if stage:
            to_remove = [k for k in self._manifest if k.startswith(f"{stage}:")]
            for k in to_remove:
                entry = self._manifest.pop(k, {})
                path = entry.get("path")
                if path and os.path.exists(path):
                    os.remove(path)
                if r:
                    try:
                        r.delete(f"creator:{k}")
                    except Exception:
                        pass
        else:
            # Clear all
            for k, entry in self._manifest.items():
                path = entry.get("path")
                if path and os.path.exists(path):
                    os.remove(path)
                if r:
                    try:
                        r.delete(f"creator:{k}")
                    except Exception:
                        pass
            self._manifest = {}
        self._save_manifest()

    def get_stats(self) -> dict:
        """Return cache performance stats."""
        total = self.stats["hits"] + self.stats["misses"]
        return {
            **self.stats,
            "total_lookups": total,
            "hit_rate": f"{(self.stats['hits'] / max(1, total)) * 100:.1f}%",
        }
