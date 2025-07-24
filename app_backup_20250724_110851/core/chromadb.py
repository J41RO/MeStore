# ~/app/core/chromadb.py
# ---------------------------------------------------------------------------------------------
# MeStore - Cliente ChromaDB para Vector Search
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: chromadb.py
# Ruta: ~/app/core/chromadb.py
# Autor: Jairo
# Fecha de Creación: 2025-07-17
# Última Actualización: 2025-07-17
# Versión: 1.0.0
# Propósito: Cliente ChromaDB configurado para vector search y embeddings
#            Proporciona acceso centralizado a la base de datos vectorial
#
# Modificaciones:
# 2025-07-17 - Implementación inicial del cliente ChromaDB
#
# ---------------------------------------------------------------------------------------------

"""
Cliente ChromaDB para vector search y embeddings.

Proporciona acceso centralizado a ChromaDB con configuración optimizada:
- Persistencia en disco local
- Cliente singleton para reutilización
- Configuración desde variables de entorno
"""

import chromadb
from chromadb.config import Settings
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Cliente global ChromaDB (singleton pattern)
_chroma_client = None

def get_chroma_client() -> chromadb.Client:
    """
    Obtener cliente ChromaDB configurado.

    Implementa patrón singleton para reutilizar conexión.
    Configura persistencia y settings optimizados.

    Returns:
        chromadb.Client: Cliente ChromaDB listo para usar
    """
    global _chroma_client

    if _chroma_client is None:
        logger.info(f"Inicializando cliente ChromaDB en: {settings.CHROMA_PERSIST_DIR}")

        try:
            _chroma_client = chromadb.PersistentClient(
                path=settings.CHROMA_PERSIST_DIR
            )

            # Verificar conexión
            collections = _chroma_client.list_collections()
            logger.info(f"Cliente ChromaDB inicializado. Colecciones existentes: {len(collections)}")

        except Exception as e:
            logger.error(f"Error inicializando ChromaDB: {e}")
            raise

    return _chroma_client

def initialize_base_collections():
    """
    Crear colecciones base del sistema si no existen.

    Colecciones estándar:
    - products: Embeddings de productos del marketplace
    - documents: Documentos y contenido textual
    - chat: Mensajes y conversaciones para IA
    """
    client = get_chroma_client()

    base_collections = [
        "products",    # Productos del marketplace
        "documents",  # Documentación y contenido
        "chat"        # Conversaciones y mensajes
    ]

    existing_collections = {col.name for col in client.list_collections()}

    for collection_name in base_collections:
        if collection_name not in existing_collections:
            logger.info(f"Creando colección: {collection_name}")
            client.create_collection(
                name=collection_name,
                metadata={"created_by": "system", "purpose": "base_collection"}
            )
        else:
            logger.debug(f"Colección {collection_name} ya existe")

    logger.info(f"Colecciones base verificadas: {base_collections}")