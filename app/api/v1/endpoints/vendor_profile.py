# ~/app/api/v1/endpoints/vendor_profile.py
# ---------------------------------------------------------------------------------------------
# MeStore - Endpoints API para Perfil de Vendor
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: vendor_profile.py
# Ruta: ~/app/api/v1/endpoints/vendor_profile.py
# Autor: Jairo
# Fecha de Creación: 2025-09-11
# Última Actualización: 2025-09-11
# Versión: 1.0.0
# Propósito: Endpoints FastAPI para gestión de perfil de vendor
#            Incluye CRUD de perfil, upload de avatar, configuraciones
#
# Modificaciones:
# 2025-09-11 - Creación inicial con endpoints completos de perfil vendor
#
# ---------------------------------------------------------------------------------------------

"""
Endpoints API para Perfil de Vendor en MeStore.

Este módulo contiene los endpoints para:
- GET /profile - Obtener perfil de vendor actual
- PUT /profile - Actualizar información del negocio
- POST /avatar - Upload de avatar/logo
- PUT /banking - Configurar información bancaria  
- PUT /notifications - Configurar preferencias de notificaciones
- GET /profile/complete - Obtener perfil completo con todas las configuraciones
"""

import os
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from PIL import Image
import aiofiles

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User, UserType
from app.schemas.vendor_profile import (
    VendorProfileResponse,
    VendorProfileUpdateRequest,
    VendorBankingInfo,
    VendorBankingUpdateRequest,
    VendorNotificationPreferences,
    VendorNotificationUpdateRequest,
    VendorAvatarUploadResponse,
    VendorProfileCompleteResponse,
    StandardResponse
)


router = APIRouter(prefix="/vendor", tags=["vendor-profile"])


# Directorio para almacenar avatares
AVATAR_UPLOAD_DIR = "uploads/avatars"
ALLOWED_AVATAR_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif"}
MAX_AVATAR_SIZE = 5 * 1024 * 1024  # 5MB


def get_current_vendor(current_user: User = Depends(get_current_user)) -> User:
    """Verificar que el usuario actual es un vendor."""
    if current_user.user_type not in [UserType.VENDOR, UserType.ADMIN, UserType.SUPERUSER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: Se requieren permisos de vendor"
        )
    return current_user


def ensure_avatar_directory():
    """Crear directorio de avatares si no existe."""
    os.makedirs(AVATAR_UPLOAD_DIR, exist_ok=True)


@router.get("/profile", response_model=VendorProfileResponse)
async def get_vendor_profile(
    current_user: User = Depends(get_current_vendor)
):
    """
    Obtener perfil actual del vendor.
    
    Retorna toda la información del perfil incluyendo:
    - Información básica del usuario
    - Datos del negocio 
    - Avatar/logo
    """
    return VendorProfileResponse.from_orm(current_user)


@router.put("/profile", response_model=VendorProfileResponse)
async def update_vendor_profile(
    profile_data: VendorProfileUpdateRequest,
    current_user: User = Depends(get_current_vendor),
    db: AsyncSession = Depends(get_db)
):
    """
    Actualizar información del perfil de vendor.
    
    Permite actualizar:
    - Nombre comercial del negocio
    - Descripción del negocio
    - Website y redes sociales
    - Horarios de atención
    - Políticas de envío y devoluciones
    """
    try:
        # Actualizar solo los campos enviados
        update_data = profile_data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            if hasattr(current_user, field):
                setattr(current_user, field, value)
        
        await db.commit()
        await db.refresh(current_user)
        
        return VendorProfileResponse.from_orm(current_user)
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar perfil: {str(e)}"
        )


@router.post("/avatar", response_model=VendorAvatarUploadResponse)
async def upload_vendor_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_vendor),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload de avatar/logo del vendor.
    
    Validaciones:
    - Tipos de archivo permitidos: JPG, PNG, GIF
    - Tamaño máximo: 5MB
    - Redimensionamiento automático a 500x500px máximo
    """
    try:
        # Validar tipo de archivo
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in ALLOWED_AVATAR_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo de archivo no permitido. Use: {', '.join(ALLOWED_AVATAR_EXTENSIONS)}"
            )
        
        # Validar tamaño
        if file.size > MAX_AVATAR_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El archivo es muy grande. Tamaño máximo: 5MB"
            )
        
        # Asegurar directorio existe
        ensure_avatar_directory()
        
        # Generar nombre único
        file_id = str(uuid.uuid4())
        filename = f"{file_id}{file_extension}"
        file_path = os.path.join(AVATAR_UPLOAD_DIR, filename)
        
        # Guardar archivo
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Redimensionar imagen
        try:
            with Image.open(file_path) as img:
                # Convertir a RGB si es necesario
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Redimensionar manteniendo aspecto
                img.thumbnail((500, 500), Image.Resampling.LANCZOS)
                img.save(file_path, quality=90, optimize=True)
        except Exception as img_error:
            # Si falla el procesamiento de imagen, eliminar archivo
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error procesando imagen: {str(img_error)}"
            )
        
        # Generar URL del avatar
        avatar_url = f"/uploads/avatars/{filename}"
        
        # Actualizar usuario
        current_user.avatar_url = avatar_url
        await db.commit()
        
        return VendorAvatarUploadResponse(
            avatar_url=avatar_url,
            message="Avatar actualizado exitosamente"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error subiendo avatar: {str(e)}"
        )


@router.put("/banking", response_model=StandardResponse)
async def update_banking_info(
    banking_data: VendorBankingUpdateRequest,
    current_user: User = Depends(get_current_vendor),
    db: AsyncSession = Depends(get_db)
):
    """
    Actualizar información bancaria del vendor.
    
    Permite configurar:
    - Nombre del banco
    - Titular de la cuenta
    - Número de cuenta
    - Tipo de cuenta (Ahorros/Corriente)
    
    Nota: Esta información se usa para procesamiento de pagos y retiros.
    """
    try:
        # Actualizar campos bancarios
        update_data = banking_data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            if hasattr(current_user, field):
                setattr(current_user, field, value)
        
        await db.commit()
        
        return StandardResponse(
            success=True,
            message="Información bancaria actualizada exitosamente"
        )
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error actualizando información bancaria: {str(e)}"
        )


@router.put("/notifications", response_model=StandardResponse)
async def update_notification_preferences(
    preferences: VendorNotificationUpdateRequest,
    current_user: User = Depends(get_current_vendor),
    db: AsyncSession = Depends(get_db)
):
    """
    Actualizar preferencias de notificaciones del vendor.
    
    Configuraciones disponibles:
    - Email para nuevas órdenes
    - Email para stock bajo
    - SMS para órdenes urgentes  
    - Push notifications para resumen diario
    """
    try:
        # Obtener preferencias actuales o crear default
        current_prefs = current_user.notification_preferences or {
            "email_new_orders": True,
            "email_low_stock": True,
            "sms_urgent_orders": False,
            "push_daily_summary": True
        }
        
        # Actualizar solo las preferencias enviadas
        update_data = preferences.dict(exclude_unset=True)
        current_prefs.update(update_data)
        
        # Guardar preferencias actualizadas
        current_user.notification_preferences = current_prefs
        await db.commit()
        
        return StandardResponse(
            success=True,
            message="Preferencias de notificaciones actualizadas exitosamente"
        )
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error actualizando preferencias: {str(e)}"
        )


@router.get("/profile/complete", response_model=VendorProfileCompleteResponse)
async def get_complete_vendor_profile(
    current_user: User = Depends(get_current_vendor)
):
    """
    Obtener perfil completo del vendor.
    
    Retorna toda la información del vendor incluyendo:
    - Perfil básico y del negocio
    - Información bancaria
    - Preferencias de notificaciones
    """
    try:
        # Construir respuesta completa
        profile = VendorProfileResponse.from_orm(current_user)
        
        banking_info = VendorBankingInfo(
            bank_name=current_user.bank_name,
            account_holder_name=current_user.account_holder_name,
            account_number=current_user.account_number,
            tipo_cuenta=current_user.tipo_cuenta
        )
        
        notification_preferences = VendorNotificationPreferences(
            **(current_user.notification_preferences or {
                "email_new_orders": True,
                "email_low_stock": True,
                "sms_urgent_orders": False,
                "push_daily_summary": True
            })
        )
        
        return VendorProfileCompleteResponse(
            profile=profile,
            banking_info=banking_info,
            notification_preferences=notification_preferences
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo perfil completo: {str(e)}"
        )


@router.delete("/avatar", response_model=StandardResponse)
async def delete_vendor_avatar(
    current_user: User = Depends(get_current_vendor),
    db: AsyncSession = Depends(get_db)
):
    """
    Eliminar avatar actual del vendor.
    """
    try:
        if current_user.avatar_url:
            # Construir ruta del archivo
            filename = os.path.basename(current_user.avatar_url)
            file_path = os.path.join(AVATAR_UPLOAD_DIR, filename)
            
            # Eliminar archivo físico si existe
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # Limpiar URL en base de datos
            current_user.avatar_url = None
            await db.commit()
            
            return StandardResponse(
                success=True,
                message="Avatar eliminado exitosamente"
            )
        else:
            return StandardResponse(
                success=True,
                message="No hay avatar para eliminar"
            )
            
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error eliminando avatar: {str(e)}"
        )