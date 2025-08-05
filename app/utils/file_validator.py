# ~/app/utils/file_validator.py
# ---------------------------------------------------------------------------------------------
# MESTORE - Utilidades de Validación de Archivos
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: file_validator.py
# Ruta: ~/app/utils/file_validator.py
# Autor: Jairo
# Fecha de Creación: 2025-08-05
# Última Actualización: 2025-08-05
# Versión: 1.0.0
# Propósito: Utilidades para validación robusta de archivos e imágenes
#            Incluye validaciones de formato, tamaño, contenido y seguridad
#
# Modificaciones:
# 2025-08-05 - Creación inicial con validaciones comprehensivas
#
# ---------------------------------------------------------------------------------------------

"""
Utilidades para validación de archivos e imágenes.

Descripción detallada de qué contiene este módulo:
- FileValidationError: Excepción personalizada para errores de validación
- validate_image_file: Validación individual de archivos de imagen
- validate_multiple_files: Validación en lote con manejo de errores
- get_image_dimensions: Utilidad para obtener dimensiones de imagen
"""

import os
from typing import List, Tuple, Optional
from PIL import Image
from fastapi import UploadFile, HTTPException
from app.core.config import settings
import mimetypes


class FileValidationError(Exception):
    """Excepción para errores de validación de archivos"""
    pass


async def validate_image_file(file: UploadFile) -> Tuple[bool, str]:
    """
    Validar un archivo de imagen individual.

    Args:
        file: Archivo a validar
    Returns:
        Tuple[bool, str]: (es_válido, mensaje_error)
    """
    try:
        # Validar tamaño del archivo
        if file.size and file.size > settings.MAX_FILE_SIZE:
            return False, f"Archivo {file.filename} excede el tamaño máximo de {settings.MAX_FILE_SIZE // (1024*1024)}MB"

        # Validar extensión
        if file.filename:
            ext = os.path.splitext(file.filename.lower())[1]
            if ext not in settings.ALLOWED_EXTENSIONS:
                return False, f"Extensión {ext} no permitida. Permitidas: {', '.join(settings.ALLOWED_EXTENSIONS)}"

        # Leer contenido para validación
        contents = await file.read()
        if not contents:
            return False, f"Archivo {file.filename} está vacío"

        # Resetear puntero para uso posterior
        await file.seek(0)

        # Validar que es imagen real usando Pillow
        try:
            image = Image.open(file.file)
            image.verify()  # Verificar integridad
            await file.seek(0)  # Resetear nuevamente

            # Validar MIME type
            if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
                return False, f"Tipo MIME {file.content_type} no permitido"

            return True, "Válido"

        except Exception as img_error:
            return False, f"Archivo {file.filename} no es una imagen válida: {str(img_error)}"

    except Exception as e:
        return False, f"Error validando archivo {file.filename}: {str(e)}"


async def validate_multiple_files(files: List[UploadFile]) -> Tuple[List[UploadFile], List[str]]:
    """
    Validar múltiples archivos de imagen.

    Args:
        files: Lista de archivos a validar
    Returns:
        Tuple[List[UploadFile], List[str]]: (archivos_válidos, errores)
    """
    # Validar cantidad
    if len(files) > settings.MAX_FILES_PER_UPLOAD:
        raise HTTPException(
            status_code=400,
            detail=f"Máximo {settings.MAX_FILES_PER_UPLOAD} archivos por upload. Recibidos: {len(files)}"
        )

    valid_files = []
    errors = []

    for file in files:
        is_valid, error_msg = await validate_image_file(file)
        if is_valid:
            valid_files.append(file)
        else:
            errors.append(error_msg)

    return valid_files, errors


def get_image_dimensions(image_path: str) -> Tuple[int, int]:
    """
    Obtener dimensiones de imagen.

    Args:
        image_path: Ruta de la imagen
    Returns:
        Tuple[int, int]: (ancho, alto)
    """
    try:
        with Image.open(image_path) as img:
            return img.size
    except Exception:
        return (0, 0)