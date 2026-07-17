import asyncio
import logging
from typing import Dict, Optional
from backend.workers.abstractions import QueueBackend, Job

logger = logging.getLogger("apollo.workers.queue")

class InMemoryQueue(QueueBackend):
    """
    A non-persistent, asyncio-based in-memory queue.
    Useful for development or single-node deployments.
    Designed to be easily swapped with Redis/Celery via DI.
    """
    def __init__(self):
        self._queue: asyncio.Queue[Job] = asyncio.Queue()
        self._jobs_store: Dict[str, Job] = {}

    async def enqueue(self, job: Job) -> None:
        """Puts a job in the execution queue and tracks its state."""
        self._jobs_store[job.id] = job
        await self._queue.put(job)
        logger.debug(f"Job {job.id} enqueued. Queue size: {self._queue.qsize()}")

    async def dequeue(self) -> Optional[Job]:
        """Pulls the next available job, waiting if necessary."""
        job = await self._queue.get()
        return job

    async def acknowledge(self, job_id: str) -> None:
        """Marks the job as processed in the asyncio queue."""
        self._queue.task_done()
        logger.debug(f"Job {job_id} acknowledged.")

    async def get_job_state(self, job_id: str) -> Optional[Job]:
        """Retrieves the current state/metadata of a job."""
        return self._jobs_store.get(job_id)

    async def update_job(self, job: Job) -> None:
        """Updates the job in the tracking store."""
        self._jobs_store[job.id] = job

# Global instance for DI
in_memory_queue = InMemoryQueue()
