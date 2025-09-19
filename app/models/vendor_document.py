from sqlalchemy import Column, String, DateTime, Boolean, Integer, ForeignKey, Text, Enum as SQLEnum
# UUID import removed for SQLite compatibility
from sqlalchemy.orm import relationship
from app.database import Base
import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

class DocumentType(str, Enum):
    CEDULA = "cedula"
    RUT = "rut"
    CERTIFICADO_BANCARIO = "certificado_bancario"
    CAMARA_COMERCIO = "camara_comercio"

class DocumentStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"

class VendorDocument(Base):
    __tablename__ = "vendor_documents"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    vendor_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    document_type = Column(SQLEnum(DocumentType), nullable=False)
    
    # Información del archivo
    file_path = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String, nullable=False)
    
    # Estado de verificación
    status = Column(SQLEnum(DocumentStatus), default=DocumentStatus.PENDING, nullable=False)
    verified_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    verification_notes = Column(Text, nullable=True)
    
    # Timestamps
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    verified_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    vendor = relationship("User", foreign_keys=[vendor_id], back_populates="vendor_documents")
    verified_by_user = relationship("User", foreign_keys=[verified_by])
    
    def __repr__(self):
        return f"<VendorDocument(id={self.id}, vendor_id={self.vendor_id}, type={self.document_type}, status={self.status})>"