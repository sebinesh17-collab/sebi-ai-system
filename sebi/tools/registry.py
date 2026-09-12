from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Dict, List


class ToolRegistry:
    """Small tool registry for controlled execution."""

    def __init__(self) -> None:
        self._tools: Dict[str, Callable[..., Any]] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        self.register("echo", lambda text: text)
        self.register("list_directory", self._list_directory)
        self.register("read_text_file", self._read_text_file)

    def register(self, name: str, handler: Callable[..., Any]) -> None:
        self._tools[name] = handler

    def available_tools(self) -> List[str]:
        return sorted(self._tools)

    def execute(self, name: str, **kwargs: Any) -> Any:
        if name not in self._tools:
            raise KeyError(f"Unknown tool: {name}")
        return self._tools[name](**kwargs)

    @staticmethod
    def _list_directory(path: str) -> List[str]:
        directory = Path(path)
        return sorted(entry.name for entry in directory.iterdir())

    @staticmethod
    def _read_text_file(path: str) -> str:
        return Path(path).read_text(encoding="utf-8", errors="ignore")
