from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from config.settings import Settings
from sebi.core.models import (
    MemoryScope,
    ProcessRequest,
    ProcessResponse,
    RequestContext,
    ToolCall,
)
from sebi.evaluation.verifier import Verifier
from sebi.execution.engine import ExecutionEngine
from sebi.knowledge.ingestion.pipeline import IngestionPipeline
from sebi.knowledge.store import KnowledgeStore
from sebi.memory.manager import MemoryManager
from sebi.multimodal.processors import InputManager
from sebi.reasoning.intent import IntentDetector
from sebi.reasoning.planner import TaskPlanner
from sebi.tools.registry import ToolRegistry
from sebi.watchers.file_watcher import FileWatcher


class SEBIBrain:
    """Central orchestrator for understanding, planning, execution, and memory."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.logger = logging.getLogger("sebi.brain")

        storage_root = Path(settings.storage_path)
        self.input_manager = InputManager()
        self.memory_manager = MemoryManager()
        self.knowledge_store = KnowledgeStore(storage_root)
        self.intent_detector = IntentDetector()
        self.task_planner = TaskPlanner()
        self.tool_registry = ToolRegistry()
        self.execution_engine = ExecutionEngine(self.tool_registry)
        self.verifier = Verifier()
        self.ingestion_pipeline = IngestionPipeline(self.input_manager, self.knowledge_store)
        self.file_watcher = FileWatcher(settings.file_watch_directory, self.ingestion_pipeline)

    def process(self, request: ProcessRequest) -> ProcessResponse:
        context = RequestContext(
            user_id=request.user_id,
            original_input=request.message,
        )

        self.logger.info("Processing request %s", context.request_id)

        context.normalized_input = self.input_manager.normalize_text(request.message)
        context.intent = self.intent_detector.detect(context.normalized_input)
        context.goal = self._derive_goal(request.message, context.intent)
        context.context_data = self._load_context(request)
        context.memory_records = self.memory_manager.recall(request.message)
        context.knowledge_items = self.knowledge_store.search(
            request.message,
            limit=self.settings.top_k_retrieval,
        )
        context.tasks = self.task_planner.create_plan(context.intent, request.message)
        context.selected_tools = self._select_tools(context.intent)
        context = self.execution_engine.execute(context)
        context.response_text = self._build_response(context)

        if request.remember:
            self.memory_manager.remember(
                scope=MemoryScope.LONG_TERM,
                key=f"user:{request.user_id or 'anonymous'}",
                value=request.message,
                metadata={"request_id": context.request_id},
            )
            context.memory_records = self.memory_manager.recall(request.message)

        context.verification = self.verifier.verify(context)
        context.finished_at = datetime.now(timezone.utc)

        return ProcessResponse(
            request_id=context.request_id,
            intent=context.intent,
            goal=context.goal,
            response=context.response_text,
            tasks=context.tasks,
            verification=context.verification,
            knowledge_count=len(context.knowledge_items),
            memory_count=len(context.memory_records),
        )

    def run_watcher_once(self) -> list[dict]:
        return [result.model_dump(mode="json") for result in self.file_watcher.scan_once()]

    def ingest_path(self, path: str) -> dict:
        result = self.ingestion_pipeline.ingest_file(path)
        return result.model_dump(mode="json")

    def system_status(self) -> dict:
        return {
            "name": "SEBI",
            "brain": "SEBIBrain",
            "environment": self.settings.env,
            "knowledge_items": len(self.knowledge_store.list_items()),
            "tools": self.tool_registry.available_tools(),
            "watch_directory": self.settings.file_watch_directory,
        }

    def _derive_goal(self, message: str, intent: str) -> str:
        if intent == "build":
            return "Design architecture and generate a working implementation."
        if intent == "generate":
            return "Generate the requested content with validation."
        if intent == "debug":
            return "Find the failure cause and propose a fix."
        if intent == "search":
            return "Retrieve relevant knowledge and answer accurately."
        if intent == "summarize":
            return "Condense the material into a useful summary."
        if intent == "analyze":
            return "Analyze the provided artifact and explain findings."
        return f"Respond helpfully to: {message[:80]}"

    def _load_context(self, request: ProcessRequest) -> dict:
        return {
            "user_id": request.user_id,
            "remember": request.remember,
            "output_format": request.output_format,
            "watch_directory": self.settings.file_watch_directory,
        }

    def _select_tools(self, intent: str) -> list[ToolCall]:
        selected = [ToolCall(name="echo")]
        if intent in {"search", "analyze"}:
            selected.append(ToolCall(name="read_text_file"))
        if intent in {"build", "generate", "debug"}:
            selected.append(ToolCall(name="list_directory"))
        return selected

    def _build_response(self, context: RequestContext) -> str:
        knowledge_summary = (
            f"Loaded {len(context.knowledge_items)} knowledge item(s)."
            if context.knowledge_items
            else "No indexed knowledge matched the request yet."
        )
        memory_summary = (
            f"Matched {len(context.memory_records)} memory record(s)."
            if context.memory_records
            else "No relevant memory was found."
        )
        task_lines = "\n".join(
            f"- {task.description} [{task.status.value}]"
            for task in context.tasks
        )

        return (
            f"SEBI intent: {context.intent}\n"
            f"Goal: {context.goal}\n\n"
            f"{knowledge_summary}\n"
            f"{memory_summary}\n\n"
            "Planned pipeline:\n"
            f"{task_lines}\n\n"
            "Selected tools: "
            + ", ".join(tool.name for tool in context.selected_tools)
        )
