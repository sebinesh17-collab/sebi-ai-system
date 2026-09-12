from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from PyPDF2 import PdfReader
from docx import Document

from sebi.core.models import InputType, NormalizedInput


class InputManager:
    """Detects input type and normalizes it into a shared structure."""

    CODE_EXTENSIONS = {".py", ".js", ".ts", ".tsx", ".java", ".go", ".rs", ".cpp", ".c", ".cs"}
    DOCUMENT_EXTENSIONS = {".txt", ".md", ".pdf", ".docx"}
    JSON_EXTENSIONS = {".json"}
    CSV_EXTENSIONS = {".csv"}
    IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
    AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".flac"}
    VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".avi"}

    def normalize_text(self, text: str, source_name: Optional[str] = None) -> NormalizedInput:
        return NormalizedInput(
            input_type=InputType.TEXT,
            raw_text=text.strip(),
            source_name=source_name,
            metadata={"length": len(text)},
        )

    def normalize_path(self, path: str) -> NormalizedInput:
        file_path = Path(path)
        suffix = file_path.suffix.lower()
        content = self._extract_file_content(file_path, suffix)
        return NormalizedInput(
            input_type=self._detect_type(suffix),
            raw_text=content,
            source_name=file_path.name,
            source_path=str(file_path),
            metadata={"suffix": suffix, "size_bytes": file_path.stat().st_size},
        )

    def _detect_type(self, suffix: str) -> InputType:
        if suffix in self.CODE_EXTENSIONS:
            return InputType.CODE
        if suffix in self.DOCUMENT_EXTENSIONS:
            return InputType.DOCUMENT
        if suffix in self.JSON_EXTENSIONS:
            return InputType.JSON
        if suffix in self.CSV_EXTENSIONS:
            return InputType.CSV
        if suffix in self.IMAGE_EXTENSIONS:
            return InputType.IMAGE
        if suffix in self.AUDIO_EXTENSIONS:
            return InputType.AUDIO
        if suffix in self.VIDEO_EXTENSIONS:
            return InputType.VIDEO
        return InputType.UNKNOWN

    def _extract_file_content(self, file_path: Path, suffix: str) -> str:
        if suffix in {".txt", ".md", ".py", ".js", ".ts", ".tsx", ".yaml", ".yml", ".csv"}:
            return file_path.read_text(encoding="utf-8", errors="ignore")
        if suffix == ".json":
            payload = json.loads(file_path.read_text(encoding="utf-8"))
            return json.dumps(payload, indent=2, ensure_ascii=True)
        if suffix == ".pdf":
            reader = PdfReader(str(file_path))
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        if suffix == ".docx":
            doc = Document(str(file_path))
            return "\n".join(paragraph.text for paragraph in doc.paragraphs)
        return f"Binary content for {file_path.name} is registered but not text-extracted yet."
