from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.db.session import get_db
from app.models.request import UploadRequest, ExpectedDocument, DocumentStatus, RequestStatus
from app.schemas.request import UploadRequestResponse
from typing import List
from app.services.storage_service import storage_service
from app.workers.tasks import process_uploaded_document

router = APIRouter()

@router.get("/requests/{reference_id}", response_model=UploadRequestResponse)
async def get_request(reference_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(UploadRequest).options(selectinload(UploadRequest.expected_documents)).where(UploadRequest.id == reference_id)
    result = await db.execute(stmt)
    upload_request = result.scalar_one_or_none()
    
    if not upload_request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")
        
    return upload_request

@router.post("/requests/{reference_id}/upload")
async def upload_documents(
    reference_id: str,
    document_ids: str = Form(...), # comma separated list mapping to files
    files: List[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db)
):
    # document_ids should match the number of files
    doc_ids = [did.strip() for did in document_ids.split(",")]
    if len(doc_ids) != len(files):
        raise HTTPException(status_code=400, detail="Mismatched document IDs and files")
        
    stmt = select(UploadRequest).options(selectinload(UploadRequest.expected_documents)).where(UploadRequest.id == reference_id)
    result = await db.execute(stmt)
    upload_request = result.scalar_one_or_none()
    
    if not upload_request:
        raise HTTPException(status_code=404, detail="Request not found")

    # Upload files and update ExpectedDocuments
    current_extras = sum(1 for d in upload_request.expected_documents if d.is_extra)
    
    for i, file in enumerate(files):
        doc_id = doc_ids[i]
        
        if doc_id == "extra":
            if current_extras >= 3:
                raise HTTPException(status_code=400, detail="Maximum of 3 extra documents allowed")
                
            # Upload to Azure (or mock)
            file_content = await file.read()
            blob_url = await storage_service.upload_document(file.filename, file_content, reference_id)
            
            # Create new extra ExpectedDocument
            new_doc = ExpectedDocument(
                request_id=reference_id,
                document_type=file.filename or "Supplemental Document",
                status=DocumentStatus.UPLOADED,
                blob_url=blob_url,
                is_extra=True
            )
            db.add(new_doc)
            # Need to flush to get ID for celery
            await db.flush()
            
            # Trigger Background Celery Task
            process_uploaded_document.delay(reference_id, new_doc.id, blob_url)
            current_extras += 1
            
        else:
            expected_doc = next((doc for doc in upload_request.expected_documents if doc.id == doc_id), None)
            
            if expected_doc:
                # Upload to Azure (or mock)
                file_content = await file.read()
                blob_url = await storage_service.upload_document(file.filename, file_content, reference_id)
                
                # Update DB
                expected_doc.status = DocumentStatus.UPLOADED
                expected_doc.blob_url = blob_url
                
                # Trigger Background Celery Task
                process_uploaded_document.delay(reference_id, expected_doc.id, blob_url)

    # Check overall request status (only for required docs)
    required_docs = [d for d in upload_request.expected_documents if not d.is_extra]
    total_required = len(required_docs)
    uploaded_required = sum(1 for d in required_docs if d.status in [DocumentStatus.UPLOADED, DocumentStatus.VALIDATED, DocumentStatus.PROCESSING, DocumentStatus.FAILED])
    
    # We no longer auto-complete here unless they specifically hit the finish endpoint,
    # but we can set PARTIALLY_COMPLETED.
    if uploaded_required > 0 and upload_request.status != RequestStatus.COMPLETED:
        upload_request.status = RequestStatus.PARTIALLY_COMPLETED
        
    await db.commit()
    
    return {"status": "accepted", "message": f"Processed {len(files)} files."}

@router.post("/requests/{reference_id}/finish")
async def finish_upload(reference_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(UploadRequest).options(selectinload(UploadRequest.expected_documents)).where(UploadRequest.id == reference_id)
    result = await db.execute(stmt)
    upload_request = result.scalar_one_or_none()
    
    if not upload_request:
        raise HTTPException(status_code=404, detail="Request not found")
        
    # Check if all required docs are uploaded
    required_docs = [d for d in upload_request.expected_documents if not d.is_extra]
    pending = [d for d in required_docs if d.status == DocumentStatus.PENDING]
    
    if pending:
        raise HTTPException(status_code=400, detail="Cannot finish: Not all required documents are uploaded.")
        
    upload_request.status = RequestStatus.COMPLETED
    await db.commit()
    
    return {"status": "completed"}
