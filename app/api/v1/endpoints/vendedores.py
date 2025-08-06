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

import logging
from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select
from sqlalchemy import func
from decimal import Decimal
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import AuthService, get_auth_service, get_current_user
from app.core.database import get_db
from app.models.user import User, UserType
from app.schemas.auth import TokenResponse
from app.schemas.user import UserRead
from app.schemas.vendedor import (
    VendedorCreate,
    VendedorErrorResponse,
    VendedorLogin,
    VendedorResponse,
    VendedorDashboardResumen,
    VendedorDashboardResumen,
    DashboardVentasResponse, 
    PeriodoVentas,
)

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
    """,
)
async def registrar_vendedor(
    vendedor_data: VendedorCreate, db: AsyncSession = Depends(get_db)
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
            logger.warning(
                f"Intento de registro con email duplicado: {vendedor_data.email}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email ya está registrado en el sistema",
            )

        # PASO 2: Verificar que cédula no esté registrada (si se proporciona)
        if vendedor_data.cedula:
            stmt = select(User).where(User.cedula == vendedor_data.cedula)
            result = await db.execute(stmt)
            existing_cedula = result.scalar_one_or_none()

            if existing_cedula:
                logger.warning(
                    f"Intento de registro con cédula duplicada: {vendedor_data.cedula}"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cédula ya está registrada en el sistema",
                )

        # PASO 3: Hash de la contraseña usando AuthService
        password_hash = await auth_service.get_password_hash(vendedor_data.password)

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
            is_verified=False,  # Requerirá verificación posterior
        )

        # PASO 5: Guardar en base de datos
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        logger.info(
            f"Vendedor registrado exitosamente: {new_user.id} - {new_user.email}"
        )

        # PASO 6: Preparar respuesta
        user_read = UserRead.model_validate(new_user)

        return VendedorResponse(
            success=True, message="Vendedor registrado exitosamente", vendedor=user_read
        )

    except HTTPException:
        # Re-lanzar HTTPExceptions para mantener status codes específicos
        raise

    except IntegrityError as e:
        # Errores de integridad de BD
        # await db.rollback()  # CORREGIDO: get_db() maneja rollback automáticamente
        logger.error(f"Error de integridad en registro: {str(e)}")

        if "email" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email ya está registrado en el sistema",
            )
        elif "cedula" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cédula ya está registrada en el sistema",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error de integridad en los datos proporcionados",
            )

    except ValueError as e:
        # Errores de validación de Pydantic
        # await db.rollback()  # CORREGIDO: get_db() maneja rollback automáticamente
        logger.error(f"Error de validación: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Error de validación: {str(e)}",
        )

    except Exception as e:
        # Errores inesperados
        # await db.rollback()  # CORREGIDO: get_db() maneja rollback automáticamente
        logger.error(f"Error inesperado en registro de vendedor: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor durante el registro",
        )


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login_vendedor(
    login_data: VendedorLogin, auth_service: AuthService = Depends(get_auth_service)
) -> TokenResponse:
    """
    Endpoint de login específico para vendedores.

    Valida credenciales y verifica que el usuario sea tipo VENDEDOR.
    Retorna tokens JWT si la autenticación es exitosa.

    Args:
        login_data: Datos de login (email, password)
        auth_service: Servicio de autenticación

    Returns:
        TokenResponse: Tokens de acceso y refresh

    Raises:
        HTTPException: 401 si credenciales inválidas o usuario no es vendedor
    """
    logger.info(f"Intento de login vendedor: {login_data.email}")

    try:
        # Autenticar usuario usando el core auth
        user = await auth_service.authenticate_user(
            email=login_data.email, password=login_data.password
        )

        if not user:
            logger.warning(f"Login vendedor fallido - credenciales inválidas: {login_data.email}")

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas",
            )

        # Verificar que el usuario sea tipo VENDEDOR
        if user.user_type != UserType.VENDEDOR:
            logger.warning(f"Login vendedor fallido - tipo incorrecto: {login_data.email}, tipo: {user.user_type.value}")


            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Este endpoint es solo para vendedores",
            )

        # Actualizar last_login
        from app.core.database import get_db

        async for db in get_db():
            try:
                user.last_login = datetime.utcnow()
                await db.commit()
                break
            except Exception as e:
                logger.error(f"Error actualizando last_login: {str(e)}")

        # Crear tokens JWT
        access_token = auth_service.create_access_token(str(user.id))
        refresh_token = auth_service.create_refresh_token(str(user.id))

        logger.info(
            f"Login vendedor exitoso - user_id: {str(user.id)}, email: {user.email}"
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=3600,  # 1 hora
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en login vendedor: {str(e)}, email: {login_data.email}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor",
        )


@router.get(
    "/health",
    summary="Health check vendedores",
    description="Endpoint de verificación de salud del módulo vendedores",
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
        "endpoints": ["POST /vendedores/registro", "GET /vendedores/health"],
    }


# Exports para facilitar imports
__all__ = ["router"]


@router.get("/dashboard/resumen", response_model=VendedorDashboardResumen, status_code=status.HTTP_200_OK)
async def get_dashboard_resumen(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> VendedorDashboardResumen:
    """Obtener KPIs principales del vendedor para dashboard."""
    # Verificar que el usuario es vendedor
    if current_user.user_type != UserType.VENDEDOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo vendedores pueden acceder al dashboard"
        )

    # TODO: Implementar queries reales cuando tengamos modelos de Producto/Venta
    # Por ahora devolvemos datos simulados pero con estructura correcta

    # Simular datos realistas para el vendedor
    kpis = VendedorDashboardResumen(
        ventas_totales=Decimal("15750.50"),
        pedidos_pendientes=7,
        productos_activos=23,
        comision_total=Decimal("1890.06")
    )

    return kpis

@router.get("/dashboard/ventas", response_model=DashboardVentasResponse, status_code=status.HTTP_200_OK)
async def get_dashboard_ventas(
    periodo: PeriodoVentas = Query(PeriodoVentas.MENSUAL, description="Tipo de período para agrupar ventas"),
    limite: int = Query(12, ge=1, le=24, description="Número máximo de períodos a retornar"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> DashboardVentasResponse:
    """Obtener datos de ventas agrupados por período para gráficos del dashboard."""
    # Verificar permisos de vendedor (reutilizar patrón)
    if current_user.user_type != UserType.VENDEDOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo vendedores pueden acceder al dashboard de ventas"
        )
    
    # TODO: Implementar queries reales por período cuando tengamos modelo Venta
    # Por ahora simulamos datos por período
# Datos simulados según el período solicitado
    if periodo == PeriodoVentas.MENSUAL:
        datos_ejemplo = [
            VentasPorPeriodo(periodo="2025-06", ventas_cantidad=15, ventas_monto=Decimal("4500.00")),
            VentasPorPeriodo(periodo="2025-07", ventas_cantidad=23, ventas_monto=Decimal("6750.50")),
            VentasPorPeriodo(periodo="2025-08", ventas_cantidad=18, ventas_monto=Decimal("5200.00"))
        ]
    elif periodo == PeriodoVentas.SEMANAL:
        datos_ejemplo = [
            VentasPorPeriodo(periodo="Semana 30", ventas_cantidad=8, ventas_monto=Decimal("2400.00")),
            VentasPorPeriodo(periodo="Semana 31", ventas_cantidad=12, ventas_monto=Decimal("3600.50"))
        ]
    else:  # DIARIO
        datos_ejemplo = [
            VentasPorPeriodo(periodo="2025-08-05", ventas_cantidad=3, ventas_monto=Decimal("890.00")),
            VentasPorPeriodo(periodo="2025-08-06", ventas_cantidad=5, ventas_monto=Decimal("1450.50"))
        ]

    return DashboardVentasResponse(
        periodo_solicitado=periodo,
        datos_grafico=datos_ejemplo[:limite],
        total_ventas=sum(d.ventas_monto for d in datos_ejemplo[:limite]),
        total_transacciones=sum(d.ventas_cantidad for d in datos_ejemplo[:limite])
    )