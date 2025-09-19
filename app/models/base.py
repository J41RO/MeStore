# ~/app/models/base.py
# ---------------------------------------------------------------------------------------------
# MESTOCKER - Base Model Definition
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: base.py
# Ruta: ~/app/models/base.py
# Autor: Jairo
# Fecha de Creación: 2025-07-17
# Última Actualización: 2025-07-19
# Versión: 1.0.1
# Propósito: Definir clase base para todos los modelos del sistema
#            Proporciona funcionalidad común y patrones consistentes
#
# Modificaciones:
# 2025-07-17 - Creación inicial de BaseModel
# 2025-07-19 - Corrección de timestamps para tests robustos
#
# ---------------------------------------------------------------------------------------------

"""
BaseModel - Clase base para todos los modelos del sistema

Proporciona:
- Estructura base común para todos los modelos
- Métodos de utilidad compartidos
- Patrones consistentes de serialización
- Validaciones base
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, String, text

from app.database import Base


class BaseModel(Base):
    """Clase base abstracta para todos los modelos del sistema"""
    
    __abstract__ = True

    # Primary key UUID para mejor performance - SQLite compatible
    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
        comment="ID único del registro",
    )

    # Timestamps automáticos con server defaults
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        comment="Fecha de creación",
    )
    
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        comment="Fecha de última actualización",
    )

    # Soft delete support
    deleted_at = Column(
        DateTime,
        nullable=True,
        default=None,
        comment="Fecha de eliminación lógica (soft delete)",
    )

    def __repr__(self) -> str:
        """Representación string del modelo"""
        return f"<{self.__class__.__name__}(id={self.id})>"

    def to_dict(self) -> dict:
        """Convertir modelo a diccionario base"""
        return {
            "id": str(self.id) if self.id is not None else None,
            "created_at": self.created_at.isoformat() if self.created_at is not None else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at is not None else None,
            "deleted_at": self.deleted_at.isoformat() if self.deleted_at is not None else None,
        }

    def is_deleted(self) -> bool:
        """Verificar si el registro está soft deleted"""
        return self.deleted_at is not None

    def is_active(self) -> bool:
        """Verificar si el registro está activo (no eliminado)"""
        return self.deleted_at is None