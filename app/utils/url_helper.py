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
    # Remover 'uploads/' del inicio si existe
    clean_path = file_path.replace("uploads/", "") if file_path.startswith("uploads/") else file_path
    return f"{settings.MEDIA_URL}/{clean_path}"
