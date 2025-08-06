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
- Dashboard con estadísticas y rankings
"""

import logging
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, Optional


from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import AuthService, get_auth_service, get_current_user
from app.core.database import get_db
from app.models.user import User, UserType
from app.schemas.auth import TokenResponse
from app.schemas.user import UserRead
from app.schemas.vendedor import (
    DashboardComisionesResponse, ComisionDetalle, EstadoComision,
    DashboardProductosTopResponse,
    DashboardVentasResponse,
    PeriodoVentas,
    ProductoTop,
    TipoRankingProducto,
    VendedorCreate,
    VendedorDashboardResumen,
    VendedorErrorResponse,
    VendedorLogin,
    VendedorResponse,
    VentasPorPeriodo,
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
        logger.error(f"Error de validación: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Error de validación: {str(e)}",
        )

    except Exception as e:
        # Errores inesperados
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
        total_productos=25,
        productos_activos=23,
        ventas_mes=42,
        ingresos_mes=Decimal("15750.50"),
        comision_total=Decimal("1890.06"),
        estadisticas_mes="Incremento del 15% vs mes anterior"
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
        total_transacciones=sum(d.ventas_cantidad for d in datos_ejemplo[:limite]),
        ventas_totales=sum(d.ventas_monto for d in datos_ejemplo[:limite]),
        pedidos_pendientes=7,
        productos_activos=23,
        comision_total=Decimal("1890.06")
    )


@router.get("/dashboard/productos-top", response_model=DashboardProductosTopResponse, status_code=status.HTTP_200_OK)
async def get_dashboard_productos_top(
    ranking: TipoRankingProducto = Query(TipoRankingProducto.VENTAS, description="Tipo de ranking a generar"),
    limite: int = Query(10, ge=1, le=50, description="Número de productos top a retornar"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> DashboardProductosTopResponse:
    """Obtener ranking de productos top del vendedor."""
    # Verificar permisos de vendedor (reutilizar patrón exacto)
    if current_user.user_type != UserType.VENDEDOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo vendedores pueden acceder al dashboard de productos"
        )
    
    # TODO: Implementar queries reales cuando tengamos modelo Venta/Producto
    # Por ahora simulamos ranking con productos ejemplo
    # Datos simulados según el tipo de ranking
    if ranking == TipoRankingProducto.VENTAS:
        productos_ejemplo = [
            ProductoTop(sku="PROD-001", nombre="Camiseta Premium", ventas_cantidad=45, ingresos_total=Decimal("2250.00"), precio_venta=Decimal("50.00"), posicion_ranking=1),
            ProductoTop(sku="PROD-015", nombre="Pantalón Clásico", ventas_cantidad=32, ingresos_total=Decimal("2880.00"), precio_venta=Decimal("90.00"), posicion_ranking=2),
            ProductoTop(sku="PROD-008", nombre="Zapatos Deportivos", ventas_cantidad=28, ingresos_total=Decimal("4200.00"), precio_venta=Decimal("150.00"), posicion_ranking=3)
        ]
    elif ranking == TipoRankingProducto.INGRESOS:
        productos_ejemplo = [
            ProductoTop(sku="PROD-008", nombre="Zapatos Deportivos", ventas_cantidad=28, ingresos_total=Decimal("4200.00"), precio_venta=Decimal("150.00"), posicion_ranking=1),
            ProductoTop(sku="PROD-015", nombre="Pantalón Clásico", ventas_cantidad=32, ingresos_total=Decimal("2880.00"), precio_venta=Decimal("90.00"), posicion_ranking=2),
            ProductoTop(sku="PROD-001", nombre="Camiseta Premium", ventas_cantidad=45, ingresos_total=Decimal("2250.00"), precio_venta=Decimal("50.00"), posicion_ranking=3)
        ]
    else:  # POPULARIDAD
        productos_ejemplo = [
            ProductoTop(sku="PROD-020", nombre="Accesorio Tendencia", ventas_cantidad=52, ingresos_total=Decimal("1560.00"), precio_venta=Decimal("30.00"), posicion_ranking=1),
            ProductoTop(sku="PROD-001", nombre="Camiseta Premium", ventas_cantidad=45, ingresos_total=Decimal("2250.00"), precio_venta=Decimal("50.00"), posicion_ranking=2)
        ]

    # Datos simulados según el tipo de ranking
    if ranking == TipoRankingProducto.VENTAS:
        productos_ejemplo = [
            ProductoTop(sku="PROD-001", nombre="Camiseta Premium", ventas_cantidad=45, ingresos_total=Decimal("2250.00"), precio_venta=Decimal("50.00"), posicion_ranking=1),
            ProductoTop(sku="PROD-015", nombre="Pantalón Clásico", ventas_cantidad=32, ingresos_total=Decimal("2880.00"), precio_venta=Decimal("90.00"), posicion_ranking=2),
            ProductoTop(sku="PROD-008", nombre="Zapatos Deportivos", ventas_cantidad=28, ingresos_total=Decimal("4200.00"), precio_venta=Decimal("150.00"), posicion_ranking=3)
        ]
    elif ranking == TipoRankingProducto.INGRESOS:
        productos_ejemplo = [
            ProductoTop(sku="PROD-008", nombre="Zapatos Deportivos", ventas_cantidad=28, ingresos_total=Decimal("4200.00"), precio_venta=Decimal("150.00"), posicion_ranking=1),
            ProductoTop(sku="PROD-015", nombre="Pantalón Clásico", ventas_cantidad=32, ingresos_total=Decimal("2880.00"), precio_venta=Decimal("90.00"), posicion_ranking=2),
            ProductoTop(sku="PROD-001", nombre="Camiseta Premium", ventas_cantidad=45, ingresos_total=Decimal("2250.00"), precio_venta=Decimal("50.00"), posicion_ranking=3)
        ]
    else:  # POPULARIDAD
        productos_ejemplo = [
            ProductoTop(sku="PROD-020", nombre="Accesorio Tendencia", ventas_cantidad=52, ingresos_total=Decimal("1560.00"), precio_venta=Decimal("30.00"), posicion_ranking=1),
            ProductoTop(sku="PROD-001", nombre="Camiseta Premium", ventas_cantidad=45, ingresos_total=Decimal("2250.00"), precio_venta=Decimal("50.00"), posicion_ranking=2)
        ]

    return DashboardProductosTopResponse(
        productos_ranking=productos_simulados[:limite],
        tipo_ranking=tipo_ranking,
        total_productos_analizados=len(productos_simulados),
        periodo_analisis="últimos_30_días"
    )


@router.get("/dashboard/comisiones", response_model=DashboardComisionesResponse, status_code=status.HTTP_200_OK)
async def get_dashboard_comisiones(
    estado: Optional[EstadoComision] = Query(None, description="Filtrar por estado de comisión"),
    limite: int = Query(20, ge=1, le=100, description="Número de comisiones a retornar"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> DashboardComisionesResponse:
    """Obtener detalle de comisiones y earnings del vendedor."""
    # Verificar permisos de vendedor (reutilizar patrón exacto)
    if current_user.user_type != UserType.VENDEDOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo vendedores pueden acceder al dashboard de comisiones"
        )

# Generar datos simulados de comisiones
    from datetime import date
    comisiones_ejemplo = [
        ComisionDetalle(
            transaccion_id="TXN-001", fecha_transaccion=date(2025, 8, 5), producto_sku="PROD-001",
            monto_venta=Decimal("150.00"), comision_porcentaje=Decimal("15.0"), 
            comision_monto=Decimal("22.50"), monto_vendedor=Decimal("127.50"), estado=EstadoComision.PAGADA
        ),
        ComisionDetalle(
            transaccion_id="TXN-002", fecha_transaccion=date(2025, 8, 6), producto_sku="PROD-015", 
            monto_venta=Decimal("280.00"), comision_porcentaje=Decimal("12.0"),
            comision_monto=Decimal("33.60"), monto_vendedor=Decimal("246.40"), estado=EstadoComision.PENDIENTE
        ),
        ComisionDetalle(
            transaccion_id="TXN-003", fecha_transaccion=date(2025, 8, 4), producto_sku="PROD-008",
            monto_venta=Decimal("450.00"), comision_porcentaje=Decimal("18.0"),
            comision_monto=Decimal("81.00"), monto_vendedor=Decimal("369.00"), estado=EstadoComision.PAGADA
        )
    ]

    # Filtrar por estado si se especifica
    if estado:
        comisiones_filtradas = [c for c in comisiones_ejemplo if c.estado == estado]
    else:
        comisiones_filtradas = comisiones_ejemplo

    # Aplicar límite
    comisiones_resultado = comisiones_filtradas[:limite]

    # Calcular totales
    total_comisiones = sum(c.comision_monto for c in comisiones_resultado)
    total_earnings = sum(c.monto_vendedor for c in comisiones_resultado)  
    pendientes = sum(c.comision_monto for c in comisiones_resultado if c.estado == EstadoComision.PENDIENTE)

    return DashboardComisionesResponse(
        comisiones_detalle=comisiones_resultado,
        total_comisiones_generadas=total_comisiones,
        total_earnings_vendedor=total_earnings,
        comisiones_pendientes=pendientes,
        periodo_analisis="último_mes"
    )


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint para monitorear el estado del módulo vendedores.
    
    Returns:
        Dict con información de estado del módulo
    """
    return {
        "status": "healthy",
        "module": "vendedores",
        "version": "1.0.0",
        "endpoints": [
            "POST /vendedores/registro",
            "POST /vendedores/login",
            "GET /vendedores/dashboard/resumen",
            "GET /vendedores/dashboard/ventas",
            "GET /vendedores/dashboard/productos-top",
            "GET /vendedores/dashboard/comisiones",
            "GET /vendedores/health"
        ],
    }


# Exports para facilitar imports
__all__ = ["router"]