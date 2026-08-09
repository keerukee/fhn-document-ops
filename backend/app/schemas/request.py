from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class ExpectedDocumentBase(BaseModel):
    document_type: str
    validation_rules: Optional[Dict[str, Any]] = None

class StructuredRequestCreate(BaseModel):
    reference_id: str
    customer_name: str
    customer_email: Optional[str] = None
    customer_id: Optional[str] = None
    expected_documents: List[ExpectedDocumentBase]

class UnstructuredRequestCreate(BaseModel):
    reference_id: str
    customer_name: str
    customer_email: Optional[str] = None
    customer_id: Optional[str] = None
    request_explanation: str

class ExpectedDocumentResponse(BaseModel):
    id: str
    document_type: str
    status: str
    validation_rules: Optional[Dict[str, Any]] = None
    is_extra: bool = False
    
    class Config:
        from_attributes = True

class UploadRequestResponse(BaseModel):
    id: str
    request_type: str
    customer_name: str
    status: str
    expires_at: datetime
    expected_documents: List[ExpectedDocumentResponse]
    upload_url: str
