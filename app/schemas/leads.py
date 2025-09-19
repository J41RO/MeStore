from pydantic import BaseModel, EmailStr, Field, validator, ConfigDict, field_validator
from typing import Optional, Literal
from datetime import datetime

class LeadCreateSchema(BaseModel):
    email: EmailStr = Field(..., description="Email corporativo del lead")
    nombre: str = Field(..., min_length=2, max_length=100, description="Nombre completo del contacto")
    tipo_negocio: Literal['vendedor', 'comprador', 'ambos'] = Field(..., description="Tipo de negocio del lead")
    telefono: Optional[str] = Field(None, max_length=20, description="Número de teléfono WhatsApp")
    empresa: Optional[str] = Field(None, max_length=200, description="Nombre de la empresa")
    source: Optional[str] = Field("landing", max_length=50, description="Fuente de captación del lead")

    @field_validator('telefono')
    @classmethod
    def validate_telefono(cls, v):
        if v and v.strip():
            # Basic phone validation - allow numbers, spaces, +, -, ()
            import re
            if not re.match(r'^[+]?[0-9\s\-()]{7,15}$', v.strip()):
                raise ValueError('Formato de teléfono inválido')
            return v.strip()
        return None

    @field_validator('nombre')
    @classmethod
    def validate_nombre(cls, v):
        if not v or not v.strip():
            raise ValueError('Nombre es requerido')
        return v.strip().title()

    @field_validator('empresa')
    @classmethod
    def validate_empresa(cls, v):
        if v and v.strip():
            return v.strip()
        return None

    model_config = ConfigDict(
        json_schema_extra = {
            "example": {
                "email": "juan.perez@miempresa.com",
                "nombre": "Juan Pérez",
                "tipo_negocio": "vendedor",
                "telefono": "+57 300 123 4567",
                "empresa": "Mi Empresa S.A.S",
                "source": "landing"
            }
        }
    )

class LeadResponseSchema(BaseModel):
    id: int
    email: str
    nombre: str
    tipo_negocio: str
    telefono: Optional[str]
    empresa: Optional[str]
    source: str
    created_at: datetime
    status: str

    model_config = ConfigDict(from_attributes=True)

class LeadStatsSchema(BaseModel):
    total_leads: int
    leads_today: int
    leads_this_week: int
    leads_this_month: int
    conversion_rate: float
    top_sources: list[dict]
    business_type_breakdown: dict

class EmailCampaignSchema(BaseModel):
    subject: str = Field(..., min_length=5, max_length=200)
    template: str = Field(..., description="Nombre del template de email")
    target_audience: Literal['all', 'vendedor', 'comprador', 'ambos'] = Field('all')
    send_immediately: bool = Field(True)
    scheduled_at: Optional[datetime] = Field(None)

class LeadUpdateSchema(BaseModel):
    status: Optional[Literal['active', 'contacted', 'converted', 'inactive']] = None
    notes: Optional[str] = Field(None, max_length=1000)
    last_contact_at: Optional[datetime] = None

class LeadBulkActionSchema(BaseModel):
    lead_ids: list[int] = Field(..., min_items=1)
    action: Literal['update_status', 'send_email', 'export', 'delete']
    parameters: Optional[dict] = None