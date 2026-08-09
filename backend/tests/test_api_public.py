import pytest
from app.models.request import UploadRequest, ExpectedDocument, DocumentStatus, RequestType
import uuid
import io

import pytest_asyncio
from datetime import datetime, timedelta

@pytest_asyncio.fixture(scope="function")
async def sample_request(db_session):
    req_id = "REQ-PUBLIC-1"
    req = UploadRequest(
        id=req_id,
        customer_name="John Public",
        request_type=RequestType.STRUCTURED,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    doc1 = ExpectedDocument(
        id="DOC-1",
        request_id=req_id,
        document_type="W2",
        status=DocumentStatus.PENDING
    )
    db_session.add(req)
    db_session.add(doc1)
    await db_session.commit()
    return req_id

@pytest.mark.asyncio
async def test_get_request(client, sample_request):
    response = await client.get(f"/api/v1/public/requests/{sample_request}")
    assert response.status_code == 200
    data = response.json()
    assert data["customer_name"] == "John Public"
    assert len(data["expected_documents"]) == 1
    assert data["expected_documents"][0]["id"] == "DOC-1"

@pytest.mark.asyncio
async def test_upload_extra_document(client, sample_request):
    # Upload an extra document
    file_content = b"fake pdf content"
    files = [("files", ("extra.pdf", file_content, "application/pdf"))]
    data = {"document_ids": "extra"}
    
    response = await client.post(
        f"/api/v1/public/requests/{sample_request}/upload",
        data=data,
        files=files
    )
    
    assert response.status_code == 200
    
    # Fetch to see if it was added
    resp2 = await client.get(f"/api/v1/public/requests/{sample_request}")
    docs = resp2.json()["expected_documents"]
    
    assert len(docs) == 2
    extra_docs = [d for d in docs if d["is_extra"]]
    assert len(extra_docs) == 1
    assert extra_docs[0]["document_type"] == "extra.pdf"
    
@pytest.mark.asyncio
async def test_finish_request_fails_if_pending(client, sample_request):
    response = await client.post(f"/api/v1/public/requests/{sample_request}/finish")
    assert response.status_code == 400
    assert "Not all required documents are uploaded" in response.json()["detail"]
