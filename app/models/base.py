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

from datetime import datetime
from typing import Any, Dict


class BaseModel:
    """Clase base para todos los modelos del sistema"""

    def __init__(self):
        now = datetime.utcnow()
        self.created_at = now
        self.updated_at = now

    def to_dict(self) -> Dict[str, Any]:
        """Convertir modelo a diccionario"""
        return {
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def update_timestamp(self):
        """Actualizar timestamp de modificación"""
        self.updated_at = datetime.utcnow()

    def __repr__(self):
        return f"{self.__class__.__name__}(created_at={self.created_at})"
