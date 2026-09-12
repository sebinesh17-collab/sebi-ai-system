from __future__ import annotations

from typing import List

from sebi.core.models import TaskRecord


class TaskPlanner:
    """Builds a lightweight execution plan from intent and context."""

    def create_plan(self, intent: str, message: str) -> List[TaskRecord]:
        tasks: List[TaskRecord] = [
            TaskRecord(
                description="Normalize and understand the input",
                required_tools=["input_manager"],
            ),
            TaskRecord(
                description="Load relevant memory and knowledge",
                dependencies=[],
                required_tools=["memory_manager", "knowledge_store"],
            ),
        ]

        intent_task_map = {
            "build": "Create architecture and implementation plan",
            "generate": "Generate requested content or code",
            "debug": "Inspect errors and propose corrections",
            "search": "Search indexed knowledge and related sources",
            "summarize": "Summarize the provided material",
            "analyze": "Analyze the provided artifact",
            "general": "Reason over the request and produce an answer",
        }

        tasks.append(
            TaskRecord(
                description=intent_task_map.get(intent, "Reason over the request and produce an answer"),
                required_tools=["reasoning_engine", "tool_registry"],
            )
        )
        tasks.append(
            TaskRecord(
                description="Verify the result before responding",
                required_tools=["verifier"],
            )
        )
        return tasks
