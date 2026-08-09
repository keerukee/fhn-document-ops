from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.request import StructuredRequestCreate, UnstructuredRequestCreate
from app.services.request_service import request_service
from app.core.security import verify_token
from app.db.session import get_db
from app.models.request import UploadRequest, ExpectedDocument
from app.schemas.request import UploadRequestResponse
from app.services.storage_service import storage_service
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from fastapi.responses import Response

router = APIRouter()

@router.post("/requests/structured", status_code=status.HTTP_201_CREATED)
async def create_structured_request(
    data: StructuredRequestCreate,
    db: AsyncSession = Depends(get_db),
    username: str = Depends(verify_token)
):
    upload_url = await request_service.create_structured_request(db, data)
    return {"upload_url": upload_url}

@router.post("/requests/unstructured", status_code=status.HTTP_201_CREATED)
async def create_unstructured_request(
    data: UnstructuredRequestCreate,
    db: AsyncSession = Depends(get_db),
    username: str = Depends(verify_token)
):
    upload_url = await request_service.create_unstructured_request(db, data)
    return {"upload_url": upload_url}

@router.get("/requests/{request_id}/status", response_model=UploadRequestResponse)
async def get_request_status(
    request_id: str,
    db: AsyncSession = Depends(get_db),
    username: str = Depends(verify_token)
):
    stmt = select(UploadRequest).options(selectinload(UploadRequest.expected_documents)).where(UploadRequest.id == request_id)
    result = await db.execute(stmt)
    upload_request = result.scalar_one_or_none()
    
    if not upload_request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")
        
    return upload_request

@router.get("/requests/{request_id}/documents/{document_id}")
async def get_document(
    request_id: str,
    document_id: str,
    db: AsyncSession = Depends(get_db),
    username: str = Depends(verify_token)
):
    stmt = select(ExpectedDocument).where(
        ExpectedDocument.id == document_id,
        ExpectedDocument.request_id == request_id
    )
    result = await db.execute(stmt)
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        
    if not document.blob_url:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Document has not been uploaded yet")
        
    # Download the document from Blob Storage
    file_bytes = await storage_service.download_document(document.blob_url)
    
    # Return as octet-stream for download
    return Response(content=file_bytes, media_type="application/octet-stream")
