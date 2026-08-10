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
    
    # Mock validation results
    validation_results = {
        "is_valid": True, 
        "confidence": 0.98,
        "justification": "All required fields were present and match the customer's profile."
    }
    
    # Publish Kafka Event for THIS specific document
    from app.services.messaging_service import messaging_service
    messaging_service.publish_upload_event(request_id, document_id, blob_url, validation_results)
    
    # Now check if this was the last document and the request is finished
    asyncio.run(_finalize_document(request_id, document_id, validation_results['is_valid']))
    
    logger.info(f"Completed processing for document {document_id}")
    return {"status": "success", "document_id": document_id}

async def _finalize_document(request_id: str, document_id: str, is_valid: bool):
    from app.db.session import SessionLocal
    from app.models.request import UploadRequest, ExpectedDocument, DocumentStatus, RequestStatus
    from sqlalchemy.future import select
    from sqlalchemy.orm import selectinload
    from app.services.messaging_service import messaging_service
    
    async with SessionLocal() as db:
        # Update this document's status
        stmt = select(ExpectedDocument).where(ExpectedDocument.id == document_id)
        result = await db.execute(stmt)
        doc = result.scalar_one_or_none()
        
        if doc:
            doc.status = DocumentStatus.VALIDATED if is_valid else DocumentStatus.FAILED
            await db.commit()
            
        # Check if parent request is COMPLETED and if ALL documents are done validating
        stmt = select(UploadRequest).options(selectinload(UploadRequest.expected_documents)).where(UploadRequest.id == request_id)
        result = await db.execute(stmt)
        req = result.scalar_one_or_none()
        
        if req and req.status == RequestStatus.COMPLETED:
            # Check if any documents are still PENDING, UPLOADED (waiting to be picked up), or PROCESSING
            in_progress = [d for d in req.expected_documents if d.status in [DocumentStatus.PENDING, DocumentStatus.UPLOADED, DocumentStatus.PROCESSING]]
            
            if len(in_progress) == 0:
                # Everyone is finished processing!
                all_valid = all(d.status == DocumentStatus.VALIDATED for d in req.expected_documents if not d.is_extra)
                messaging_service.publish_request_completed_event(request_id, all_valid=all_valid)
