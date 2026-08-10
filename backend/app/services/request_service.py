from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from app.models.request import UploadRequest, ExpectedDocument, RequestStatus, DocumentStatus
from app.schemas.request import StructuredRequestCreate, UnstructuredRequestCreate
from app.services.validation_service import validation_service
from app.core.config import settings
import uuid

class RequestService:
    
    def _create_upload_request_model(self, data, request_type: str, request_id: str, raw_request_explanation: str = None) -> UploadRequest:
        return UploadRequest(
            id=request_id,
            request_type=request_type,
            customer_name=data.customer_name,
            customer_email=data.customer_email,
            customer_id=data.customer_id,
            raw_request_explanation=raw_request_explanation,
            status=RequestStatus.PENDING,
            expires_at=datetime.utcnow() + timedelta(days=settings.DEFAULT_LINK_EXPIRATION_DAYS)
        )

    async def create_structured_request(self, db: AsyncSession, data: StructuredRequestCreate) -> str:
        request_id = str(uuid.uuid4())
        
        upload_request = self._create_upload_request_model(data, request_type="STRUCTURED", request_id=request_id)
        db.add(upload_request)
        
        for doc_schema in data.expected_documents:
            doc = ExpectedDocument(
                id=str(uuid.uuid4()),
                request_id=request_id,
                document_type=doc_schema.document_type,
                validation_rules=doc_schema.validation_rules,
                status=DocumentStatus.PENDING
            )
            db.add(doc)
            
        await db.commit()
        return f"/upload/{upload_request.id}"

    async def create_unstructured_request(self, db: AsyncSession, data: UnstructuredRequestCreate) -> str:
        # Step 1: Parse unstructured text via Azure Foundry (Validation Service)
        expected_docs = await validation_service.analyze_unstructured_request(data.request_explanation)
        
        request_id = str(uuid.uuid4())
        
        # Step 2: Create DB records
        upload_request = self._create_upload_request_model(
            data, 
            request_type="UNSTRUCTURED", 
            request_id=request_id,
            raw_request_explanation=data.request_explanation
        )
        db.add(upload_request)
        
        for doc_schema in expected_docs:
            doc = ExpectedDocument(
                id=str(uuid.uuid4()),
                request_id=request_id,
                document_type=doc_schema.document_type,
                validation_rules=doc_schema.validation_rules,
                status=DocumentStatus.PENDING
            )
            db.add(doc)
        await db.commit()
        return f"/upload/{upload_request.id}"

request_service = RequestService()
