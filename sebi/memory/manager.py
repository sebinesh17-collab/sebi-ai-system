from __future__ import annotations

from typing import Dict, List, Optional

from sebi.core.models import MemoryRecord, MemoryScope


class MemoryManager:
    """In-memory memory layers suitable for local development and tests."""

    def __init__(self) -> None:
        self._records: Dict[MemoryScope, List[MemoryRecord]] = {
            MemoryScope.CONVERSATION: [],
            MemoryScope.LONG_TERM: [],
            MemoryScope.PROJECT: [],
        }

    def remember(
        self,
        scope: MemoryScope,
        key: str,
        value: str,
        metadata: Optional[dict] = None,
    ) -> MemoryRecord:
        record = MemoryRecord(scope=scope, key=key, value=value, metadata=metadata or {})
        self._records[scope].append(record)
        return record

    def recall(self, query: str, limit: int = 5) -> List[MemoryRecord]:
        lowered = query.lower()
        matches: List[MemoryRecord] = []
        for records in self._records.values():
            for record in records:
                haystack = f"{record.key} {record.value}".lower()
                if lowered in haystack or any(word in haystack for word in lowered.split()):
                    matches.append(record)
        return matches[:limit]

    def list_scope(self, scope: MemoryScope) -> List[MemoryRecord]:
        return list(self._records[scope])
