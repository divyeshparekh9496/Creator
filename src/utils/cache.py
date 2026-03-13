"""
Scene-level cache — skip regeneration for unchanged inputs.
"""
import os
import json
import hashlib
from typing import Any, Optional


class SceneCache:
    """Hash-based cache for pipeline stage outputs."""

    def __init__(self, cache_dir: str = "data/cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        self.manifest_path = os.path.join(cache_dir, "manifest.json")
        self._manifest = self._load_manifest()

    def _load_manifest(self) -> dict:
        if os.path.exists(self.manifest_path):
            with open(self.manifest_path) as f:
                return json.load(f)
        return {}

    def _save_manifest(self):
        with open(self.manifest_path, "w") as f:
            json.dump(self._manifest, f, indent=2)

    @staticmethod
    def _hash(data: Any) -> str:
        raw = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def get(self, stage: str, input_data: Any) -> Optional[dict]:
        """Return cached output if inputs haven't changed."""
        key = f"{stage}:{self._hash(input_data)}"
        entry = self._manifest.get(key)
        if entry:
            path = entry.get("path")
            if path and os.path.exists(path):
                with open(path) as f:
                    print(f"[Cache] HIT: {stage}")
                    return json.load(f)
        return None

    def set(self, stage: str, input_data: Any, output_data: dict):
        """Cache the output for a stage."""
        key = f"{stage}:{self._hash(input_data)}"
        path = os.path.join(self.cache_dir, f"{stage}_{self._hash(input_data)}.json")
        try:
            with open(path, "w") as f:
                json.dump(output_data, f, default=str)
            self._manifest[key] = {"path": path, "stage": stage}
            self._save_manifest()
            print(f"[Cache] STORED: {stage}")
        except (TypeError, ValueError):
            pass  # Non-serializable — skip caching

    def invalidate(self, stage: str = None):
        """Clear cache for a stage or all."""
        if stage:
            to_remove = [k for k in self._manifest if k.startswith(f"{stage}:")]
            for k in to_remove:
                entry = self._manifest.pop(k, {})
                path = entry.get("path")
                if path and os.path.exists(path):
                    os.remove(path)
        else:
            self._manifest = {}
        self._save_manifest()
