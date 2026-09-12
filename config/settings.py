from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """SEBI runtime configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    env: str = "development"
    debug: bool = True
    log_level: str = "INFO"

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 1
    api_reload: bool = True

    model_name: str = "local-lite"
    model_path: str = "./models"
    model_device: str = "cpu"
    model_precision: str = "int8"
    model_max_tokens: int = 2048
    model_temperature: float = 0.4
    model_top_p: float = 0.95
    model_top_k: int = 50

    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimension: int = 384
    embedding_batch_size: int = 32

    database_url: str = "sqlite:///./storage/sebi.db"
    redis_url: str = "redis://localhost:6379/0"

    storage_path: str = "./storage"
    knowledge_index_path: str = "./storage/knowledge_index"
    dataset_path: str = "./storage/datasets"
    model_registry_path: str = "./storage/models"
    temporary_media_retention_minutes: int = 5

    top_k_retrieval: int = 5
    similarity_threshold: float = 0.5
    chunk_size: int = 512
    chunk_overlap: int = 50

    web_search_enabled: bool = False
    web_search_max_results: int = 5
    web_search_timeout: int = 10

    deepseek_api_key: Optional[str] = None
    deepseek_api_url: str = "https://api.deepseek.com/v1"
    openai_api_key: Optional[str] = None
    openai_api_url: str = "https://api.openai.com/v1"

    training_enabled: bool = False
    training_batch_size: int = 8
    training_learning_rate: float = 2e-5
    training_epochs: int = 3
    training_max_grad_norm: float = 1.0
    training_warmup_steps: int = 500
    training_eval_steps: int = 500
    training_save_steps: int = 1000

    quality_min_length: int = 10
    quality_max_length: int = 4096
    quality_duplicate_threshold: float = 0.95
    quality_toxicity_threshold: float = 0.7
    quality_hallucination_threshold: float = 0.6

    secret_key: str = "change-this-secret-key"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    api_key_header: str = "X-SEBI-API-Key"

    audit_enabled: bool = True
    audit_log_path: str = "./logs/sebi.log"
    metrics_enabled: bool = True
    observability_enabled: bool = True

    file_ingestion_enabled: bool = True
    file_watch_directory: str = "./input_files"
    supported_file_types: List[str] = Field(
        default_factory=lambda: ["txt", "md", "json", "pdf", "docx", "py", "js", "ts", "yaml", "yml"]
    )
    max_file_size_mb: int = 100

    reasoning_effort: str = "medium"

    short_term_memory_size: int = 100
    long_term_memory_enabled: bool = True
    project_memory_enabled: bool = True

    tool_timeout_seconds: int = 30
    tool_execution_limit: int = 50
    tool_sandbox_enabled: bool = True

    @property
    def storage_root(self) -> Path:
        return Path(self.storage_path)

    @property
    def logs_root(self) -> Path:
        return Path(self.audit_log_path).resolve().parent

    @property
    def watch_root(self) -> Path:
        return Path(self.file_watch_directory)

@lru_cache()
def get_settings() -> Settings:
    return Settings()
