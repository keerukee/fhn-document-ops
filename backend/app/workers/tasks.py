import os
from celery import Celery
import asyncio
import logging

logger = logging.getLogger(__name__)

# Redis is typically default for Celery
redis_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "docops_worker",
    broker=redis_url,
    backend=redis_url
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

@celery_app.task(name="process_uploaded_document")
def process_uploaded_document(request_id: str, document_id: str, blob_url: str):
    """
    Background task that:
    1. Triggers Azure Document Intelligence
    2. Validates extracted data against Azure Foundry
    3. Updates database status
    4. Publishes a Kafka event
    """
    logger.info(f"Starting processing for document {document_id} (Request: {request_id})")
    
    # In a real scenario, this would invoke the ai_service, validation_service, and messaging_service.
    # Since Celery tasks are synchronous by default in this setup, we'd use async to sync wrappers 
    # or just use synchronous clients for the SDKs.
    
    # Mock processing delay
    import time
    time.sleep(2) 
    
    logger.info(f"Completed processing for document {document_id}")
    return {"status": "success", "document_id": document_id}
