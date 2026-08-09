import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from .base import Base

class RequestStatus(str, enum.Enum):
    PENDING = "PENDING"
    PARTIALLY_COMPLETED = "PARTIALLY_COMPLETED"
    COMPLETED = "COMPLETED"
    EXPIRED = "EXPIRED"

class DocumentStatus(str, enum.Enum):
    PENDING = "PENDING"
    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    VALIDATED = "VALIDATED"
    FAILED = "FAILED"

class UploadRequest(Base):
    __tablename__ = "upload_requests"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_name = Column(String, nullable=False)
    customer_email = Column(String, nullable=True)
    customer_id = Column(String, nullable=True)
    status = Column(String, default=RequestStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    
    expected_documents = relationship("ExpectedDocument", back_populates="upload_request", cascade="all, delete-orphan")

class ExpectedDocument(Base):
    __tablename__ = "expected_documents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    request_id = Column(String, ForeignKey("upload_requests.id"), nullable=False)
    document_type = Column(String, nullable=False)
    validation_rules = Column(JSON, nullable=True) # Defines what needs validation
    status = Column(String, default=DocumentStatus.PENDING)
    blob_url = Column(String, nullable=True)
    validation_results = Column(JSON, nullable=True)

    upload_request = relationship("UploadRequest", back_populates="expected_documents")
