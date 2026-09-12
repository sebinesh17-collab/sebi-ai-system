from __future__ import annotations

from pathlib import Path

from sebi.core.models import FileProcessingStatus, IngestionResult
from sebi.knowledge.store import KnowledgeStore
from sebi.multimodal.processors import InputManager


class IngestionPipeline:
    """Validates and ingests files into the knowledge store."""

    def __init__(self, input_manager: InputManager, knowledge_store: KnowledgeStore) -> None:
        self.input_manager = input_manager
        self.knowledge_store = knowledge_store

    def ingest_file(self, path: str) -> IngestionResult:
        file_path = Path(path)
        if not file_path.exists():
            return IngestionResult(
                path=path,
                status=FileProcessingStatus.FAILED,
                message="File does not exist",
            )

        try:
            normalized = self.input_manager.normalize_path(path)
            content = normalized.raw_text.strip()
            if not content:
                return IngestionResult(
                    path=path,
                    status=FileProcessingStatus.SKIPPED,
                    message="No extractable text content found",
                )

            item = self.knowledge_store.add_item(
                title=file_path.name,
                content=content,
                source_path=str(file_path),
                source_type=normalized.input_type.value,
                metadata=normalized.metadata,
            )
            return IngestionResult(
                path=path,
                status=FileProcessingStatus.COMPLETED,
                item_id=item.item_id,
                message="File ingested successfully",
            )
        except Exception as exc:
            return IngestionResult(
                path=path,
                status=FileProcessingStatus.FAILED,
                message=str(exc),
            )
