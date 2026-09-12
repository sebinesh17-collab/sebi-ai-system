from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


class JsonStore:
    """Small local JSON store used by the starter SEBI runtime."""

    def __init__(self, base_path: Path) -> None:
        self.base_path = base_path
        self.base_path.mkdir(parents=True, exist_ok=True)

    def read_json(self, name: str, default: Optional[Any] = None) -> Any:
        path = self.base_path / name
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8"))

    def write_json(self, name: str, payload: Any) -> Path:
        path = self.base_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")
        return path

    def append_json_list(self, name: str, item: Dict[str, Any]) -> Path:
        current = self.read_json(name, default=[])
        if not isinstance(current, list):
            current = []
        current.append(item)
        return self.write_json(name, current)

    def list_files(self, pattern: str = "*") -> List[Path]:
        return sorted(self.base_path.glob(pattern))


def ensure_directories(paths: Iterable[Path]) -> None:
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)
