from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class InputType(str, Enum):
    TEXT = "text"
    DOCUMENT = "document"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    CODE = "code"
    JSON = "json"
    CSV = "csv"
    UNKNOWN = "unknown"


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class FileProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    SKIPPED = "skipped"


class MemoryScope(str, Enum):
    CONVERSATION = "conversation"
    LONG_TERM = "long_term"
    PROJECT = "project"


class NormalizedInput(BaseModel):
    input_type: InputType
    raw_text: str = ""
    source_name: Optional[str] = None
    source_path: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = 1.0


class TaskRecord(BaseModel):
    task_id: str = Field(default_factory=lambda: str(uuid4()))
    description: str
    dependencies: List[str] = Field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    required_tools: List[str] = Field(default_factory=list)
    inputs: Dict[str, Any] = Field(default_factory=dict)
    outputs: Dict[str, Any] = Field(default_factory=dict)
    validation_result: Dict[str, Any] = Field(default_factory=dict)
    error_state: Optional[str] = None


class KnowledgeItem(BaseModel):
    item_id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    content: str
    source_path: str
    source_type: str
    content_hash: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    relationships: List[str] = Field(default_factory=list)
    version: str = "v1"
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class MemoryRecord(BaseModel):
    record_id: str = Field(default_factory=lambda: str(uuid4()))
    scope: MemoryScope
    key: str
    value: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class ToolCall(BaseModel):
    name: str
    permission_level: str = "read"
    arguments: Dict[str, Any] = Field(default_factory=dict)


class ExecutionArtifact(BaseModel):
    artifact_type: str
    location: Optional[str] = None
    content: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class VerificationReport(BaseModel):
    passed: bool = False
    checks: Dict[str, Any] = Field(default_factory=dict)
    issues: List[str] = Field(default_factory=list)


class RequestContext(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: Optional[str] = None
    original_input: str
    normalized_input: Optional[NormalizedInput] = None
    intent: str = "general"
    goal: str = ""
    context_data: Dict[str, Any] = Field(default_factory=dict)
    memory_records: List[MemoryRecord] = Field(default_factory=list)
    knowledge_items: List[KnowledgeItem] = Field(default_factory=list)
    tasks: List[TaskRecord] = Field(default_factory=list)
    selected_tools: List[ToolCall] = Field(default_factory=list)
    execution_artifacts: List[ExecutionArtifact] = Field(default_factory=list)
    verification: VerificationReport = Field(default_factory=VerificationReport)
    response_text: str = ""
    created_at: datetime = Field(default_factory=utc_now)
    finished_at: Optional[datetime] = None


class ProcessRequest(BaseModel):
    message: str
    user_id: Optional[str] = None
    remember: bool = False
    output_format: str = "markdown"


class ProcessResponse(BaseModel):
    request_id: str
    intent: str
    goal: str
    response: str
    tasks: List[TaskRecord]
    verification: VerificationReport
    knowledge_count: int
    memory_count: int


class IngestionRequest(BaseModel):
    path: str
    tags: List[str] = Field(default_factory=list)


class IngestionResult(BaseModel):
    path: str
    status: FileProcessingStatus
    item_id: Optional[str] = None
    message: str
