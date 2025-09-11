from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from app.models.vendor_document import DocumentType, DocumentStatus

# Base schema
class VendorDocumentBase(BaseModel):
    document_type: DocumentType
    original_filename: str
    file_size: int
    mime_type: str

# Schema para crear documento
class VendorDocumentCreate(VendorDocumentBase):
    vendor_id: UUID
    file_path: str
    
    @validator('file_size')
    def validate_file_size(cls, v):
        max_size = 5 * 1024 * 1024  # 5MB
        if v > max_size:
            raise ValueError(f'File size must be less than {max_size} bytes')
        return v
    
    @validator('mime_type')
    def validate_mime_type(cls, v):
        allowed_types = [
            'image/jpeg', 'image/png', 'image/webp',
            'application/pdf'
        ]
        if v not in allowed_types:
            raise ValueError(f'Mime type must be one of: {", ".join(allowed_types)}')
        return v

# Schema para actualizar documento
class VendorDocumentUpdate(BaseModel):
    status: Optional[DocumentStatus] = None
    verification_notes: Optional[str] = None
    verified_by: Optional[UUID] = None
    verified_at: Optional[datetime] = None

# Schema para respuesta
class VendorDocumentResponse(VendorDocumentBase):
    id: UUID
    vendor_id: UUID
    status: DocumentStatus
    verified_by: Optional[UUID] = None
    verification_notes: Optional[str] = None
    uploaded_at: datetime
    verified_at: Optional[datetime] = None
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Schema para listar documentos
class VendorDocumentListResponse(BaseModel):
    documents: List[VendorDocumentResponse]
    total: int
    
class VendorDocumentSummary(BaseModel):
    document_type: DocumentType
    status: DocumentStatus
    uploaded_at: datetime
    verified_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Schema para upload de archivo
class DocumentUploadResponse(BaseModel):
    id: UUID
    document_type: DocumentType
    original_filename: str
    status: DocumentStatus
    uploaded_at: datetime
    
    class Config:
        from_attributes = True

# Schema para verificación de documentos (admin)
class DocumentVerificationRequest(BaseModel):
    status: DocumentStatus
    verification_notes: Optional[str] = None
    
    @validator('status')
    def validate_status(cls, v):
        if v not in [DocumentStatus.VERIFIED, DocumentStatus.REJECTED]:
            raise ValueError('Status must be either VERIFIED or REJECTED')
        return v
    
    @validator('verification_notes')
    def validate_notes_on_rejection(cls, v, values):
        if values.get('status') == DocumentStatus.REJECTED and not v:
            raise ValueError('Verification notes are required when rejecting a document')
        return v