import uuid
from enum import Enum
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Callable, Awaitable
from pydantic import BaseModel, Field

class JobState(str, Enum):
    """Lifecycle states of a background job."""
    QUEUED = "QUEUED"
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    RETRYING = "RETRYING"
    TIMED_OUT = "TIMED_OUT"

class Job(BaseModel):
    """
    Abstractions representing a discrete unit of work in the background execution engine.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_name: str
    payload: Dict[str, Any]
    
    state: JobState = JobState.QUEUED
    progress: float = 0.0
    current_stage: str = "Initialized"
    
    # Retry policy configuration
    max_retries: int = 3
    retry_count: int = 0
    timeout_seconds: int = 300
    
    # Temporal tracking
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Execution metadata
    failure_reason: Optional[str] = None
    worker_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def mark_running(self, worker_id: str):
        self.state = JobState.RUNNING
        self.started_at = datetime.now(timezone.utc)
        self.worker_id = worker_id

    def mark_completed(self):
        self.state = JobState.COMPLETED
        self.completed_at = datetime.now(timezone.utc)
        self.progress = 100.0

    def mark_failed(self, reason: str):
        self.state = JobState.FAILED
        self.completed_at = datetime.now(timezone.utc)
        self.failure_reason = reason

    def can_retry(self) -> bool:
        return self.retry_count < self.max_retries


class QueueBackend:
    """
    Interface for queue implementations (In-Memory, Redis, Celery, ARQ).
    """
    async def enqueue(self, job: Job) -> None:
        raise NotImplementedError

    async def dequeue(self) -> Optional[Job]:
        raise NotImplementedError

    async def acknowledge(self, job_id: str) -> None:
        raise NotImplementedError

    async def get_job_state(self, job_id: str) -> Optional[Job]:
        raise NotImplementedError
