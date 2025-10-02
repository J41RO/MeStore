"""Helper de URLs para archivos estáticos."""

from app.core.config import settings


def build_public_url(file_path: str) -> str:
    """
    Construir URL pública para archivo.

    Args:
        file_path: Ruta relativa del archivo

    Returns:
        URL pública completa
    """
    # Remover '/' inicial si existe
    clean_path = file_path.lstrip('/')

    # Si es URL absoluta, retornarla directamente
    if clean_path.startswith('http'):
        return clean_path

    # Construir URL completa con dominio
    # TODO: Configurar esto con variables de entorno
    base_url = "http://192.168.1.137:8000"
    return f"{base_url}/{clean_path}"
