from __future__ import annotations

from pathlib import Path
from typing import Set

from sebi.core.models import IngestionResult
from sebi.knowledge.ingestion.pipeline import IngestionPipeline


class FileWatcher:
    """Polling watcher used for simple local development."""

    def __init__(self, watch_directory: str, ingestion_pipeline: IngestionPipeline) -> None:
        self.watch_directory = Path(watch_directory)
        self.watch_directory.mkdir(parents=True, exist_ok=True)
        self.ingestion_pipeline = ingestion_pipeline
        self._seen: Set[str] = set()

    def scan_once(self) -> list[IngestionResult]:
        results: list[IngestionResult] = []
        for path in sorted(self.watch_directory.glob("*")):
            if not path.is_file():
                continue
            key = str(path.resolve())
            if key in self._seen:
                continue
            results.append(self.ingestion_pipeline.ingest_file(str(path)))
            self._seen.add(key)
        return results
