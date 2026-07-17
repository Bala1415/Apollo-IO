import logging
import asyncio
from backend.workers.abstractions import Job
from backend.services.notifications.service import notification_service
# Assume LangGraph Supervisor exposes an entry point, e.g., run_pipeline
# from backend.graph.supervisor import run_pipeline

logger = logging.getLogger("apollo.workers.tasks")

async def analyze_lead_task(job: Job) -> None:
    """
    Executes the heavy LangGraph Supervisor AI pipeline for lead qualification.
    Designed to run asynchronously within a BackgroundWorker.
    """
    lead_email = job.payload.get("email")
    company_domain = job.payload.get("company_domain")
    user_id = job.payload.get("user_id")

    logger.info(f"Task {job.task_name} (Job {job.id}) started for lead: {lead_email}")
    
    # Progress hook: started
    job.progress = 10.0
    job.current_stage = "Initialization"
    
    try:
        # Simulate processing delay or actual graph invocation
        # In actual deployment, this imports and runs the LangGraph supervisor:
        # result = await run_pipeline(email=lead_email, domain=company_domain)
        
        job.progress = 50.0
        job.current_stage = "AI Graph Execution"
        await asyncio.sleep(2) # Simulated workload
        
        job.progress = 90.0
        job.current_stage = "Finalizing Data"
        
        # Trigger success notification using the existing Notification Service
        if user_id:
            await notification_service.send_alert(
                user_id=user_id,
                title="Lead Analysis Complete",
                message=f"The AI pipeline successfully processed {lead_email}.",
                level="info"
            )
            
        logger.info(f"Task {job.task_name} (Job {job.id}) successfully completed.")
        
    except Exception as e:
        logger.error(f"Task {job.task_name} (Job {job.id}) failed: {e}")
        
        # Trigger failure notification
        if user_id:
            await notification_service.send_alert(
                user_id=user_id,
                title="Lead Analysis Failed",
                message=f"The AI pipeline encountered an error processing {lead_email}.",
                level="error"
            )
        # Re-raise to trigger Worker Retry Policy
        raise
