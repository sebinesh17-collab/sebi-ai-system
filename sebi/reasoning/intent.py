from __future__ import annotations

from sebi.core.models import NormalizedInput


class IntentDetector:
    """Simple rule-based intent detector for the starter system."""

    def detect(self, normalized_input: NormalizedInput) -> str:
        text = normalized_input.raw_text.lower()

        if any(token in text for token in ("debug", "traceback", "fix bug", "error")):
            return "debug"
        if any(token in text for token in ("build website", "generate app", "create api", "scaffold")):
            return "build"
        if any(token in text for token in ("summarize", "summary", "extract")):
            return "summarize"
        if any(token in text for token in ("search", "find", "lookup", "retrieve")):
            return "search"
        if any(token in text for token in ("code", "write", "implement", "generate")):
            return "generate"
        if normalized_input.input_type.value in {"document", "code", "json", "csv"}:
            return "analyze"
        return "general"
