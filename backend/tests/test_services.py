import pytest
from app.services.request_service import request_service
from app.schemas.request import StructuredRequestCreate, ExpectedDocumentBase
from app.models.request import UploadRequest, RequestType
from sqlalchemy.future import select

@pytest.mark.asyncio
async def test_create_structured_request(db_session):
    data = StructuredRequestCreate(
        reference_id="TEST-1234",
        customer_name="Test Customer",
        customer_email="test@example.com",
        expected_documents=[
            ExpectedDocumentBase(document_type="ID Card")
        ]
    )
    
    url = await request_service.create_structured_request(db_session, data)
    assert url == "/upload/TEST-1234"
    
    # Verify DB
    stmt = select(UploadRequest).where(UploadRequest.id == "TEST-1234")
    result = await db_session.execute(stmt)
    req = result.scalar_one_or_none()
    
    assert req is not None
    assert req.customer_name == "Test Customer"
    assert req.request_type == RequestType.STRUCTURED
