from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


ToolCallStatus = Literal["success", "failed", "skipped"]
MessageRole = Literal["user", "assistant", "system"]


class ChatMessage(BaseModel):
    role: MessageRole
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ToolActivity(BaseModel):
    name: str
    summary: str
    status: ToolCallStatus
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=20000)
    project_name: Optional[str] = None


class FileNode(BaseModel):
    path: str
    name: str
    node_type: Literal["file", "directory"]


class FileContent(BaseModel):
    path: str
    content: str


class UpdateFileRequest(BaseModel):
    path: str
    content: str


class CreateProjectRequest(BaseModel):
    project_name: str = Field(min_length=1, max_length=120)
    description: str = ""
    template: str = "blank"


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=200)


class GitHubInspectRequest(BaseModel):
    repository: str = Field(
        ...,
        description="GitHub repository in owner/name or full URL format.",
    )
    branch: Optional[str] = None


class ProjectTask(BaseModel):
    title: str
    status: Literal["completed", "in_progress", "pending"]


class ProjectMemory(BaseModel):
    project_name: str
    requirements: List[str] = Field(default_factory=list)
    architecture: List[str] = Field(default_factory=list)
    file_tree: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    current_implementation_status: str = "Project initialized"
    known_errors: List[str] = Field(default_factory=list)
    completed_tasks: List[str] = Field(default_factory=list)
    pending_tasks: List[str] = Field(default_factory=list)


class ProjectState(BaseModel):
    project_name: str
    workspace_root: str
    files: List[FileNode]
    memory: ProjectMemory
    recent_messages: List[ChatMessage]
    recent_activity: List[ToolActivity]


class ChatResponse(BaseModel):
    reply: str
    project_state: ProjectState
    artifacts: List[str] = Field(default_factory=list)


class GitHubRepositorySummary(BaseModel):
    repository: str
    default_branch: Optional[str] = None
    description: Optional[str] = None
    top_level_files: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list)


class ExportResponse(BaseModel):
    filename: str
    path: str


class CommandResult(BaseModel):
    command: str
    return_code: int
    stdout: str
    stderr: str
    timed_out: bool = False


class ToolExecutionResult(BaseModel):
    tool_name: str
    status: ToolCallStatus
    summary: str
    payload: Dict[str, Any] = Field(default_factory=dict)
