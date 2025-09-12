"""
Router para gestión de perfil de usuario.
Este módulo maneja todas las operaciones relacionadas con:
- Actualización de datos bancarios
- Configuración de perfil
- Información personal del usuario
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_db as get_db
from app.api.v1.deps.auth import get_current_user
from app.schemas.user import UserRead, UserUpdate

router = APIRouter()


@router.put("/datos-bancarios", response_model=UserRead, status_code=status.HTTP_200_OK)
async def update_datos_bancarios(
    datos: UserUpdate,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> UserRead:
    """
    Actualizar datos bancarios del perfil del usuario actual.

    Solo actualiza los campos bancarios: banco, tipo_cuenta, numero_cuenta.
    El usuario debe estar autenticado.
    """
    # TODO: Implementar lógica de actualización en base de datos
    return current_user