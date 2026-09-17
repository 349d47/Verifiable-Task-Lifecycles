from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .canonical import canonical_json_bytes, content_id


class ArtifactStore:
    """Simple filesystem artifact store keyed by SHA-256 content identifiers."""

    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def put(self, value: Any) -> str:
        identifier = content_id(value)
        (self.root / f"{identifier}.json").write_bytes(canonical_json_bytes(value))
        return identifier

    def get(self, identifier: str) -> Any:
        return json.loads((self.root / f"{identifier}.json").read_text(encoding="utf-8"))
