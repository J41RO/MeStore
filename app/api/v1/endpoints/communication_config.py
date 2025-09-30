# ~/app/api/v1/endpoints/communication_config.py
# ---------------------------------------------------------------------------------------------
# MeStore - Configuración de Comunicaciones (SMS y Email)
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# ---------------------------------------------------------------------------------------------

"""
Endpoints para configurar y testear servicios de comunicación (SMS y Email).

Este módulo permite:
- Verificar estado de servicios SMS y Email
- Enviar SMS y emails de prueba
- Configurar proveedores de comunicación
- Obtener instrucciones de configuración
"""

from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi import Request
from pydantic import BaseModel, Field

from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.services.alternative_sms_service import alternative_sms_service
from app.services.smtp_email_service import SMTPEmailService
from app.core.logger import get_logger

# Configurar router y logger
router = APIRouter(prefix="/communications", tags=["Communication Configuration"])
logger = get_logger(__name__)


class SMSTestRequest(BaseModel):
    phone_number: str = Field(..., description="Número de teléfono para test")
    test_message: str = Field(default="Test desde MeStore", description="Mensaje de prueba")


class EmailTestRequest(BaseModel):
    email: str = Field(..., description="Email para test")
    test_subject: str = Field(default="Test desde MeStore", description="Asunto de prueba")
    test_message: str = Field(default="Este es un email de prueba", description="Mensaje de prueba")


class ServiceStatusResponse(BaseModel):
    sms_service: Dict[str, Any]
    email_service: Dict[str, Any]
    setup_instructions: Dict[str, Any]


@router.get("/status", response_model=ServiceStatusResponse)
async def get_communication_status():
    """
    Obtiene el estado actual de los servicios de comunicación.

    Returns:
        ServiceStatusResponse: Estado de SMS y Email services
    """
    try:
        # Obtener estado del servicio SMS
        sms_status = alternative_sms_service.get_service_status()
        sms_instructions = alternative_sms_service.get_setup_instructions()

        # Obtener estado del servicio Email
        smtp_service = SMTPEmailService()
        email_status = smtp_service.get_service_status()
        email_instructions = smtp_service.get_setup_instructions()

        return ServiceStatusResponse(
            sms_service=sms_status,
            email_service=email_status,
            setup_instructions={
                "sms_providers": sms_instructions,
                "email_smtp": email_instructions
            }
        )

    except Exception as e:
        logger.error(f"Error obteniendo estado de comunicaciones: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo estado: {str(e)}"
        )


@router.post("/test-sms")
async def test_sms_service(
    request: SMSTestRequest,
    development_mode: bool = Query(False, description="Forzar modo desarrollo")
):
    """
    Envía un SMS de prueba usando el servicio configurado.

    Args:
        request: Datos del SMS de prueba
        development_mode: Si forzar modo desarrollo (solo simular)
    """
    try:
        logger.info(f"Enviando SMS de prueba a: {request.phone_number}")

        if development_mode:
            logger.info(f"SMS TEST (Desarrollo) - Para: {request.phone_number}, Mensaje: {request.test_message}")
            return {
                "success": True,
                "message": f"SMS de prueba simulado enviado a {request.phone_number}",
                "provider": "development_mode",
                "development": True
            }

        # Enviar SMS real usando el servicio alternativo
        success, message = await alternative_sms_service.send_otp_sms(
            phone_number=request.phone_number,
            otp_code="TEST123",  # Código de prueba
            user_name="Usuario de Prueba"
        )

        if success:
            return {
                "success": True,
                "message": message,
                "provider": "alternative_sms_service",
                "development": False
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error enviando SMS: {message}"
            )

    except Exception as e:
        logger.error(f"Error en test SMS: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error enviando SMS de prueba: {str(e)}"
        )


@router.post("/test-email")
async def test_email_service(
    request: EmailTestRequest,
    development_mode: bool = Query(False, description="Forzar modo desarrollo")
):
    """
    Envía un email de prueba usando el servicio SMTP configurado.

    Args:
        request: Datos del email de prueba
        development_mode: Si forzar modo desarrollo (solo simular)
    """
    try:
        logger.info(f"Enviando email de prueba a: {request.email}")

        smtp_service = SMTPEmailService()

        if development_mode:
            logger.info(f"EMAIL TEST (Desarrollo) - Para: {request.email}, Asunto: {request.test_subject}")
            return {
                "success": True,
                "message": f"Email de prueba simulado enviado a {request.email}",
                "provider": "development_mode",
                "development": True
            }

        # Enviar email real usando SMTP
        success, message = await smtp_service.send_otp_email_async(
            email=request.email,
            otp_code="TEST123",
            user_name="Usuario de Prueba"
        )

        if success:
            return {
                "success": True,
                "message": message,
                "provider": "smtp_service",
                "development": False
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error enviando email: {message}"
            )

    except Exception as e:
        logger.error(f"Error en test email: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error enviando email de prueba: {str(e)}"
        )


@router.get("/sms-providers")
async def get_sms_providers():
    """
    Obtiene información de los proveedores SMS disponibles.
    """
    try:
        return {
            "providers": alternative_sms_service.providers,
            "setup_instructions": alternative_sms_service.get_setup_instructions(),
            "current_status": alternative_sms_service.get_service_status()
        }

    except Exception as e:
        logger.error(f"Error obteniendo proveedores SMS: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo proveedores: {str(e)}"
        )


@router.get("/email-config")
async def get_email_config():
    """
    Obtiene información de la configuración de email SMTP.
    """
    try:
        smtp_service = SMTPEmailService()
        return {
            "configuration": smtp_service.get_service_status(),
            "setup_instructions": smtp_service.get_setup_instructions()
        }

    except Exception as e:
        logger.error(f"Error obteniendo configuración email: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo configuración: {str(e)}"
        )