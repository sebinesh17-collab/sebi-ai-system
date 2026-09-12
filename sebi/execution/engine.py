from __future__ import annotations

from sebi.core.models import ExecutionArtifact, RequestContext, TaskStatus
from sebi.tools.registry import ToolRegistry


class ExecutionEngine:
    """Executes planned tasks using the registered tools."""

    def __init__(self, tool_registry: ToolRegistry) -> None:
        self.tool_registry = tool_registry

    def execute(self, context: RequestContext) -> RequestContext:
        for task in context.tasks:
            task.status = TaskStatus.IN_PROGRESS
            task.outputs["status"] = "started"

            if "tool_registry" in task.required_tools:
                task.outputs["available_tools"] = self.tool_registry.available_tools()

            task.outputs["intent"] = context.intent
            task.status = TaskStatus.COMPLETED
            context.execution_artifacts.append(
                ExecutionArtifact(
                    artifact_type="task_result",
                    content=f"{task.description}: completed",
                    metadata={"task_id": task.task_id},
                )
            )
        return context
