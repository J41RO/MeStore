# ~/app/api/v1/endpoints/vendedores.py
# ---------------------------------------------------------------------------------------------
# MESTOCKER - API Endpoints Vendedores
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: vendedores.py
# Ruta: ~/app/api/v1/endpoints/vendedores.py
# Autor: Jairo
# Fecha de Creación: 2025-07-31
# Última Actualización: 2025-07-31
# Versión: 1.0.0
# Propósito: Endpoints API específicos para gestión de vendedores
#            con registro especializado y validaciones colombianas
#
# Modificaciones:
# 2025-07-31 - Creación inicial con registro de vendedores
#
# ---------------------------------------------------------------------------------------------

"""
Endpoints API para gestión de vendedores en MeStore.

Este módulo contiene endpoints especializados para:
- Registro de vendedores con validaciones obligatorias
- Integración con sistema de autenticación existente
- Manejo de errores específicos para vendedores
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from typing import Dict, Any
import logging

from app.core.database import get_db
from app.core.auth import AuthService
from app.models.user import User, UserType
from app.schemas.vendedor import VendedorCreate, VendedorResponse, VendedorErrorResponse
from app.schemas.user import UserRead

# Configurar logging
logger = logging.getLogger(__name__)

# Router para vendedores
router = APIRouter(prefix="/vendedores", tags=["vendedores"])

# Instancia del servicio de autenticación
auth_service = AuthService()


@router.post(
    "/registro",
    response_model=None,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo vendedor",
    description="""
    Registra un nuevo vendedor en el sistema con validaciones específicas colombianas.

    **Campos obligatorios para vendedores:**
    - email: Email único en el sistema
    - password: Contraseña fuerte (mín 8 chars, mayúscula, minúscula, número)
    - nombre: Nombre completo del vendedor
    - apellido: Apellido completo del vendedor
    - cedula: Cédula de ciudadanía colombiana (6-10 dígitos)
    - telefono: Número de teléfono colombiano (formato +57)

    **Campos opcionales:**
    - ciudad: Ciudad de residencia
    - empresa: Empresa del vendedor
    - direccion: Dirección completa

    El user_type se asigna automáticamente como VENDEDOR.
    """
)
async def registrar_vendedor(
    vendedor_data: VendedorCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Registrar nuevo vendedor con validaciones específicas.

    Args:
        vendedor_data: Datos del vendedor a registrar
        db: Sesión de base de datos

    Returns:
        VendedorResponse: Datos del vendedor registrado

    Raises:
        HTTPException: Si hay errores de validación o registro
    """

    try:
        logger.info(f"Iniciando registro de vendedor: {vendedor_data.email}")

        # PASO 1: Verificar que email no esté registrado
        stmt = select(User).where(User.email == vendedor_data.email)
        result = await db.execute(stmt)
        existing_user = result.scalar_one_or_none()

        if existing_user:
            logger.warning(f"Intento de registro con email duplicado: {vendedor_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email ya está registrado en el sistema"
            )

        # PASO 2: Verificar que cédula no esté registrada (si se proporciona)
        if vendedor_data.cedula:
            stmt = select(User).where(User.cedula == vendedor_data.cedula)
            result = await db.execute(stmt)
            existing_cedula = result.scalar_one_or_none()

            if existing_cedula:
                logger.warning(f"Intento de registro con cédula duplicada: {vendedor_data.cedula}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cédula ya está registrada en el sistema"
                )

        # PASO 3: Hash de la contraseña usando AuthService
        password_hash = auth_service.get_password_hash(vendedor_data.password)

        # PASO 4: Crear nuevo usuario vendedor
        new_user = User(
            email=vendedor_data.email,
            password_hash=password_hash,
            nombre=vendedor_data.nombre,
            apellido=vendedor_data.apellido,
            user_type=UserType.VENDEDOR,  # Forzar tipo VENDEDOR
            cedula=vendedor_data.cedula,
            telefono=vendedor_data.telefono,
            ciudad=vendedor_data.ciudad,
            empresa=vendedor_data.empresa,
            direccion=vendedor_data.direccion,
            is_active=True,
            is_verified=False  # Requerirá verificación posterior
        )

        # PASO 5: Guardar en base de datos
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        logger.info(f"Vendedor registrado exitosamente: {new_user.id} - {new_user.email}")

        # PASO 6: Preparar respuesta
        user_read = UserRead.model_validate(new_user)

        return VendedorResponse(
            success=True,
            message="Vendedor registrado exitosamente",
            vendedor=user_read
        )

    except HTTPException:
        # Re-lanzar HTTPExceptions para mantener status codes específicos
        raise

    except IntegrityError as e:
        # Errores de integridad de BD
        db.rollback()
        logger.error(f"Error de integridad en registro: {str(e)}")

        if "email" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email ya está registrado en el sistema"
            )
        elif "cedula" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cédula ya está registrada en el sistema"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error de integridad en los datos proporcionados"
            )

    except ValueError as e:
        # Errores de validación de Pydantic
        db.rollback()
        logger.error(f"Error de validación: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Error de validación: {str(e)}"
        )

    except Exception as e:
        # Errores inesperados
        db.rollback()
        logger.error(f"Error inesperado en registro de vendedor: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor durante el registro"
        )


@router.get(
    "/health",
    summary="Health check vendedores",
    description="Endpoint de verificación de salud del módulo vendedores"
)
async def health_check() -> Dict[str, Any]:
    """
    Verificar estado del módulo vendedores.

    Returns:
        Dict con información de estado del módulo
    """
    return {
        "status": "healthy",
        "module": "vendedores",
        "version": "1.0.0",
        "endpoints": [
            "POST /vendedores/registro",
            "GET /vendedores/health"
        ]
    }


# Exports para facilitar imports
__all__ = ["router"]