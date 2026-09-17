from __future__ import annotations

import dataclasses
import hashlib
import json
from enum import Enum
from typing import Any


def _plain(value: Any) -> Any:
    if dataclasses.is_dataclass(value):
        return {k: _plain(v) for k, v in dataclasses.asdict(value).items()}
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {str(k): _plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(v) for v in value]
    return value


def canonical_json_bytes(value: Any) -> bytes:
    """Canonical JSON used by the prototype: sorted keys, UTF-8, no insignificant whitespace."""
    return json.dumps(
        _plain(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def content_id(value: Any) -> str:
    """SHA-256 content identifier as lowercase hexadecimal without a 0x prefix."""
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def content_commitment(value: Any) -> str:
    """Same digest formatted as bytes32-style hexadecimal for DLT interfaces."""
    return "0x" + content_id(value)
