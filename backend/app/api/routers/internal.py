from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.request import StructuredRequestCreate, UnstructuredRequestCreate
from app.services.request_service import request_service
from app.core.security import verify_token
from app.db.session import get_db

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
