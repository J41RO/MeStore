# ~/app/api/v1/endpoints/vendors.py
# ---------------------------------------------------------------------------------------------
# MeStore - Vendor Registration Endpoint
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: vendors.py
# Ruta: ~/app/api/v1/endpoints/vendors.py
# Autor: Backend Framework AI
# Fecha de Creación: 2025-10-01
# Última Actualización: 2025-10-01
# Versión: 1.0.0
# Propósito: Endpoint para registro de vendors (MVP - auto-aprobación)
#
# Modificaciones:
# 2025-10-01 - Creación inicial con endpoint de registro
#
# ---------------------------------------------------------------------------------------------

"""
Vendor Registration Endpoint para MeStore MVP.

Este módulo contiene el endpoint para:
- POST /vendors/register: Registrar nuevo vendor con auto-aprobación
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.core.database import get_db
from app.schemas.vendor import VendorCreate, VendorResponse
from app.services.vendor_service import VendorService

router = APIRouter(tags=["vendor-registration"])


@router.post("/register", response_model=VendorResponse, status_code=status.HTTP_201_CREATED)
async def register_vendor(
    vendor_data: VendorCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Registrar nuevo vendor (MVP - auto-aprobación).

    **Flujo de Registro:**
    1. Validación de datos (email, password, teléfono, etc.)
    2. Verificación de email único
    3. Creación de cuenta con auto-aprobación
    4. Retorno de información de bienvenida

    **Request Body:**
    - email: Email único del vendor
    - password: Contraseña segura (mín. 8 caracteres, mayúscula, minúscula, número)
    - full_name: Nombre completo del vendor
    - phone: Teléfono colombiano (+57...)
    - business_name: Nombre del negocio
    - city: Ciudad de operación
    - business_type: Tipo de negocio (persona_natural o empresa)
    - primary_category: Categoría principal de productos
    - terms_accepted: Aceptación de términos (debe ser true)

    **Response:**
    - vendor_id: UUID del vendor creado
    - email: Email del vendor
    - full_name: Nombre completo
    - business_name: Nombre del negocio
    - status: "active" (auto-aprobado en MVP)
    - message: Mensaje de bienvenida
    - next_steps: Enlaces a próximas acciones recomendadas
    - created_at: Timestamp de registro

    **Errores:**
    - 400 Bad Request: Email ya registrado
    - 422 Unprocessable Entity: Validación de datos fallida
    - 500 Internal Server Error: Error interno del servidor
    """
    try:
        # Crear instancia de VendorService
        vendor_service = VendorService(db)

        # Intentar crear vendor
        new_vendor = await vendor_service.create_vendor(vendor_data)

        # Construir respuesta exitosa
        response = VendorResponse(
            vendor_id=str(new_vendor.id),
            email=new_vendor.email,
            full_name=f"{new_vendor.nombre} {new_vendor.apellido}".strip() or new_vendor.email,
            business_name=new_vendor.business_name or vendor_data.business_name,
            status="active",
            message="¡Registro exitoso! Bienvenida a MeStocker.",
            next_steps={
                "add_products": f"/vendor/products/new?vendor_id={new_vendor.id}",
                "view_dashboard": f"/vendor/dashboard?vendor_id={new_vendor.id}"
            },
            created_at=new_vendor.created_at or datetime.utcnow()
        )

        return response

    except ValueError as e:
        # Error de validación (email duplicado, etc.)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Error interno del servidor
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno al registrar vendor: {str(e)}"
        )
