import logging
from typing import Optional, Dict, Any
from backend.workers.abstractions import Job, QueueBackend
from backend.workers.queue import in_memory_queue

logger = logging.getLogger("apollo.workers.manager")

class JobManager:
    """
    Coordinates job submission and state tracking.
    Uses Dependency Injection for the underlying queue implementation.
    """
    def __init__(self, queue_backend: QueueBackend):
        self.queue = queue_backend

    async def enqueue_job(
        self, 
        task_name: str, 
        payload: Dict[str, Any], 
        metadata: Optional[Dict[str, Any]] = None
    ) -> Job:
        """
        Creates and enqueues a new background job.
        """
        job = Job(
            task_name=task_name,
            payload=payload,
            metadata=metadata or {}
        )
        
        logger.info(f"Enqueuing Job {job.id} for task '{task_name}'")
        await self.queue.enqueue(job)
        return job

    async def get_job_status(self, job_id: str) -> Optional[Job]:
        """
        Retrieves the current execution status and progress of a job.
        """
        return await self.queue.get_job_state(job_id)

    async def cancel_job(self, job_id: str) -> bool:
        """
        Attempts to cancel a job if it has not yet started.
        Note: Cancellation of currently running jobs requires a distributed signal or cooperative cancellation.
        """
        job = await self.queue.get_job_state(job_id)
        if not job:
            return False
            
        if job.state in ["QUEUED", "PENDING"]:
            job.state = "CANCELLED"
            # If using in_memory_queue, update the store
            if hasattr(self.queue, 'update_job'):
                await self.queue.update_job(job)
            logger.info(f"Job {job_id} cancelled.")
            return True
            
        logger.warning(f"Cannot cancel Job {job_id} in state {job.state}")
        return False

# Global instance for DI
job_manager = JobManager(in_memory_queue)
