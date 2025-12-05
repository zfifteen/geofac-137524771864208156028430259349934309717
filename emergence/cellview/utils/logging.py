"""
Structured logging helpers for reproducible runs.
"""

import json
import os
import time
from typing import Any, Dict


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def timestamp_id(prefix: str = "run") -> str:
    return f"{prefix}_{int(time.time() * 1000)}"


def write_json(path: str, payload: Dict[str, Any]) -> None:
    ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


__all__ = ["ensure_dir", "timestamp_id", "write_json"]
