import asyncio
import logging
import traceback
from typing import Callable, Dict, Awaitable
from backend.workers.abstractions import QueueBackend, Job, JobState

logger = logging.getLogger("apollo.workers.worker")

class BackgroundWorker:
    """
    Consumes jobs from the QueueBackend and executes them asynchronously.
    Includes robust error handling, exponential backoff retries, and timeout enforcement.
    """
    def __init__(self, queue_backend: QueueBackend, worker_id: str = "worker-1"):
        self.queue = queue_backend
        self.worker_id = worker_id
        self._registry: Dict[str, Callable[[Job], Awaitable[None]]] = {}
        self._running = False

    def register_task(self, task_name: str, handler: Callable[[Job], Awaitable[None]]):
        """Registers an asynchronous handler for a specific task name."""
        self._registry[task_name] = handler
        logger.info(f"Worker {self.worker_id} registered handler for '{task_name}'")

    async def _execute_with_retry(self, job: Job, handler: Callable[[Job], Awaitable[None]]):
        """Executes a job, applying exponential backoff on failures."""
        try:
            # Enforce execution timeout
            await asyncio.wait_for(handler(job), timeout=job.timeout_seconds)
            job.mark_completed()
            logger.info(f"Job {job.id} completed successfully in {job.completed_at - job.started_at}")
        
        except asyncio.TimeoutError:
            logger.error(f"Job {job.id} timed out after {job.timeout_seconds}s")
            job.state = JobState.TIMED_OUT
            job.failure_reason = "Execution timed out"
            
        except Exception as e:
            logger.error(f"Job {job.id} failed: {str(e)}\n{traceback.format_exc()}")
            job.retry_count += 1
            
            if job.can_retry():
                job.state = JobState.RETRYING
                backoff_time = 2 ** job.retry_count
                logger.info(f"Job {job.id} scheduling retry {job.retry_count}/{job.max_retries} in {backoff_time}s")
                
                # Re-enqueue the job after a delay
                asyncio.create_task(self._delayed_requeue(job, backoff_time))
            else:
                job.mark_failed(str(e))
                logger.error(f"Job {job.id} permanently failed after {job.retry_count} retries.")
        finally:
            if hasattr(self.queue, 'update_job'):
                await self.queue.update_job(job)

    async def _delayed_requeue(self, job: Job, delay_seconds: int):
        """Helper to requeue a job after backoff."""
        await asyncio.sleep(delay_seconds)
        job.state = JobState.QUEUED
        await self.queue.enqueue(job)

    async def start(self):
        """Starts the worker polling loop."""
        logger.info(f"Worker {self.worker_id} starting...")
        self._running = True
        
        while self._running:
            try:
                job = await self.queue.dequeue()
                if not job:
                    await asyncio.sleep(1)
                    continue

                if job.state == JobState.CANCELLED:
                    logger.info(f"Skipping cancelled Job {job.id}")
                    await self.queue.acknowledge(job.id)
                    continue

                handler = self._registry.get(job.task_name)
                if not handler:
                    logger.error(f"No handler registered for task '{job.task_name}'. Failing job.")
                    job.mark_failed("No handler registered")
                    if hasattr(self.queue, 'update_job'):
                        await self.queue.update_job(job)
                    await self.queue.acknowledge(job.id)
                    continue

                job.mark_running(self.worker_id)
                if hasattr(self.queue, 'update_job'):
                    await self.queue.update_job(job)

                # Execute concurrently without blocking the polling loop
                asyncio.create_task(self._process_job(job, handler))

            except Exception as e:
                logger.error(f"Worker loop error: {e}")
                await asyncio.sleep(5) # Prevent tight spin on severe errors

    async def _process_job(self, job: Job, handler: Callable[[Job], Awaitable[None]]):
        """Wrapper to execute and acknowledge."""
        await self._execute_with_retry(job, handler)
        await self.queue.acknowledge(job.id)

    async def stop(self):
        """Stops the worker polling loop gracefully."""
        logger.info(f"Worker {self.worker_id} stopping...")
        self._running = False
