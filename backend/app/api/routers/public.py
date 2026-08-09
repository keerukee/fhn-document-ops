from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.db.session import get_db
from app.models.request import UploadRequest, ExpectedDocument, DocumentStatus
from app.schemas.request import UploadRequestResponse
from typing import List

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
    # In a real implementation:
    # 1. Upload file to Azure Blob Storage
    # 2. Update ExpectedDocument status to UPLOADED and set blob_url
    # 3. Trigger Celery background task for Document Intelligence, Foundry Validation, Kafka
    
    # Simple mock response
    return {"status": "accepted", "message": f"Received {len(files)} files for processing."}
