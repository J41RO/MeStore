# ~/app/schemas/payout_request.py
from pydantic import BaseModel, Field, ConfigDict, field_validator
from pydantic import validator, ConfigDict, field_validator
from decimal import Decimal
from datetime import datetime
from typing import Optional
from app.models.payout_request import EstadoPayout

class PayoutRequestCreate(BaseModel):
    monto_solicitado: Decimal = Field(..., gt=0, description="Monto a solicitar")
    tipo_cuenta: str = Field(..., pattern="^(AHORROS|CORRIENTE)$")
    numero_cuenta: str = Field(..., min_length=8, max_length=50)
    banco: str = Field(..., min_length=3, max_length=100)






    class Config:
        from_attributes = True  # Para SQLAlchemy 2.0
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            Decimal: lambda v: float(v)
        }
    observaciones: Optional[str] = Field(None, max_length=500)

    class Config:
        from_attributes = True

    @field_validator('numero_cuenta')


    @classmethod
    def validar_numero_cuenta(cls, v):
        """Validar que el número de cuenta sea numérico."""
        if not v.isdigit():
            raise ValueError('El número de cuenta debe contener solo dígitos')
        return v

    @field_validator('banco')


    @classmethod
    def validar_banco(cls, v):
        """Validar nombre del banco."""
        if not v.strip():
            raise ValueError('El nombre del banco es obligatorio')
        return v.strip().title()

    @field_validator('monto_solicitado')


    @classmethod
    def validar_monto_colombia(cls, v):
        """Validar límites de monto para Colombia."""
        if v > 50000000:  # 50 millones COP
            raise ValueError('El monto máximo es 50,000,000 COP')
        if v < 10000:  # Mínimo 10 mil COP
            raise ValueError('El monto mínimo es 10,000 COP')
        return v

class PayoutRequestRead(BaseModel):
    id: str
    monto_solicitado: Decimal
    estado: EstadoPayout
    tipo_cuenta: str
    banco: str