from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import BaseModel


class PayoutHistory(BaseModel):
    """
    Modelo para tracking completo de cambios de estado en PayoutRequest.
    Registra automáticamente todos los cambios de estado para auditoría completa.
    """
    __tablename__ = "payout_history"
    
    id = Column(Integer, primary_key=True, index=True)
    payout_request_id = Column(Integer, ForeignKey("payout_requests.id"), nullable=False, index=True)
    estado_anterior = Column(String(50), nullable=True)  # None para el primer estado
    estado_nuevo = Column(String(50), nullable=False)
    fecha_cambio = Column(DateTime, default=datetime.utcnow, nullable=False)
    observaciones = Column(Text, nullable=True)
    usuario_responsable = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    payout_request = relationship("PayoutRequest", back_populates="history")
    usuario = relationship("User")
    
    @classmethod
    def registrar_cambio(cls, db_session, payout_request_id: int, estado_anterior: str, 
                        estado_nuevo: str, observaciones: str = None, usuario_id: int = None):
        """
        Método para registrar automáticamente cambios de estado.
        
        Args:
            db_session: Sesión de base de datos
            payout_request_id: ID del PayoutRequest
            estado_anterior: Estado previo (None para primer registro)
            estado_nuevo: Nuevo estado
            observaciones: Notas adicionales del cambio
            usuario_id: ID del usuario responsable del cambio
        """
        nuevo_registro = cls(
            payout_request_id=payout_request_id,
            estado_anterior=estado_anterior,
            estado_nuevo=estado_nuevo,
            observaciones=observaciones,
            usuario_responsable=usuario_id
        )
        db_session.add(nuevo_registro)
        return nuevo_registro
    
    def __repr__(self):
        return f"<PayoutHistory(id={self.id}, payout_id={self.payout_request_id}, {self.estado_anterior} -> {self.estado_nuevo})>"
