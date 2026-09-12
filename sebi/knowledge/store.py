from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Dict, List, Optional

from sebi.core.models import KnowledgeItem
from sebi.storage.files import JsonStore


class KnowledgeStore:
    """Simple file-backed knowledge store with lexical search."""

    INDEX_FILE = "knowledge/items.json"

    def __init__(self, base_path: Path) -> None:
        self.store = JsonStore(base_path)
        self._items: Dict[str, KnowledgeItem] = {}
        self._load()

    def _load(self) -> None:
        items = self.store.read_json(self.INDEX_FILE, default=[])
        for item in items:
            knowledge_item = KnowledgeItem.model_validate(item)
            self._items[knowledge_item.item_id] = knowledge_item

    def _persist(self) -> None:
        payload = [item.model_dump(mode="json") for item in self._items.values()]
        self.store.write_json(self.INDEX_FILE, payload)

    def compute_hash(self, content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def add_item(
        self,
        title: str,
        content: str,
        source_path: str,
        source_type: str,
        metadata: Optional[dict] = None,
    ) -> KnowledgeItem:
        content_hash = self.compute_hash(content)
        for item in self._items.values():
            if item.content_hash == content_hash:
                return item

        knowledge_item = KnowledgeItem(
            title=title,
            content=content,
            source_path=source_path,
            source_type=source_type,
            content_hash=content_hash,
            metadata=metadata or {},
        )
        self._items[knowledge_item.item_id] = knowledge_item
        self._persist()
        return knowledge_item

    def search(self, query: str, limit: int = 5) -> List[KnowledgeItem]:
        tokens = [token for token in query.lower().split() if token]
        scored: List[tuple[int, KnowledgeItem]] = []

        for item in self._items.values():
            haystack = f"{item.title} {item.content}".lower()
            score = sum(1 for token in tokens if token in haystack)
            if score:
                scored.append((score, item))

        scored.sort(key=lambda entry: entry[0], reverse=True)
        return [item for _, item in scored[:limit]]

    def list_items(self) -> List[KnowledgeItem]:
        return list(self._items.values())
