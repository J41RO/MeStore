# ~/backend/chroma_db/vector_db.py
# ---------------------------------------------------------------------------------------------
# MESTOCKER - Vector Database Client Module
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: vector_db.py
# Ruta: ~/backend/chroma_db/vector_db.py
# Autor: Jairo
# Fecha de Creación: 2025-07-17
# Última Actualización: 2025-07-17
# Versión: 1.0.0
# Propósito: Cliente ChromaDB singleton con persistencia local para mantener colecciones
#            entre ejecuciones del sistema
#
# Modificaciones:
# 2025-07-17 - Implementación inicial con persistencia en ./chroma_db
#
# ---------------------------------------------------------------------------------------------

"""
ChromaDB Vector Database Client

Este módulo proporciona un cliente ChromaDB singleton con persistencia local
para mantener colecciones de embeddings entre ejecuciones de la aplicación.

Características principales:
- Cliente singleton para acceso centralizado
- Persistencia en disco (./chroma_db/)
- Configuración robusta con manejo de errores
- Compatible con FastAPI dependency injection
- Logging detallado para debugging

Ejemplo de uso:
   # Obtener cliente
   client = get_chroma_client()

   # Crear/obtener colección
   collection = client.get_or_create_collection('productos')

   # Usar en FastAPI
   async def endpoint(client: ChromaClient = Depends(get_chroma_client)):
       pass
"""

import logging

# import os  # Removido - no utilizado
from pathlib import Path
from typing import Any, Dict, Optional

import chromadb
from chromadb.api.client import Client as ChromaClient
from chromadb.config import Settings

# Configurar logging
logger = logging.getLogger(__name__)

# Variable global para singleton
_chroma_client: Optional[ChromaClient] = None

# Configuración de ChromaDB
CHROMA_DB_PATH = "./chroma_db"
CHROMA_SETTINGS = Settings(
    persist_directory=CHROMA_DB_PATH,
    anonymized_telemetry=False,  # Deshabilitar telemetría para privacidad
    allow_reset=True,  # Permitir reset en desarrollo
)


def get_chroma_client(force_recreate: bool = False) -> ChromaClient:
    """
    Obtener cliente ChromaDB singleton con persistencia local.

    Args:
        force_recreate: Si True, fuerza recreación del cliente (útil para testing)

    Returns:
        ChromaClient: Cliente ChromaDB configurado con persistencia

    Raises:
        Exception: Si hay problemas de configuración o inicialización
    """
    global _chroma_client

    # Si ya existe cliente y no se fuerza recreación, retornar existente
    if _chroma_client is not None and not force_recreate:
        logger.debug("📋 USANDO CLIENTE CHROMADB EXISTENTE")
        return _chroma_client

    try:
        logger.info("🔧 INICIALIZANDO CLIENTE CHROMADB CON PERSISTENCIA")

        # Crear directorio de persistencia si no existe
        chroma_path = Path(CHROMA_DB_PATH)
        chroma_path.mkdir(exist_ok=True)
        logger.info(f"📁 DIRECTORIO PERSISTENCIA: {chroma_path.absolute()}")

        # Verificar si ya existe base de datos
        sqlite_file = chroma_path / "chroma.sqlite3"
        if sqlite_file.exists():
            logger.info(f"✅ BASE DE DATOS EXISTENTE ENCONTRADA: {sqlite_file}")
        else:
            logger.info("📝 CREANDO NUEVA BASE DE DATOS CHROMADB")

        # Crear cliente con configuración
        _chroma_client = chromadb.Client(CHROMA_SETTINGS)

        # Verificar funcionamiento básico
        heartbeat = _chroma_client.heartbeat()
        logger.info(f"💓 CHROMADB HEARTBEAT: {heartbeat}")

        # Listar colecciones existentes
        collections = _chroma_client.list_collections()
        logger.info(f"📋 COLECCIONES EXISTENTES: {len(collections)}")
        for collection in collections:
            logger.info(f"   • {collection.name} (count: {collection.count()})")

        logger.info("✅ CLIENTE CHROMADB INICIALIZADO EXITOSAMENTE")
        return _chroma_client

    except Exception as e:
        logger.error(f"❌ ERROR INICIALIZANDO CHROMADB: {e}")
        _chroma_client = None
        raise


def reset_chroma_client() -> None:
    """
    Resetear cliente ChromaDB (útil para testing).

    Warning: Esto elimina el cliente en memoria, no los datos persistidos.
    """
    global _chroma_client

    if _chroma_client is not None:
        logger.warning("🔄 RESETEANDO CLIENTE CHROMADB")
        _chroma_client = None
    else:
        logger.info("ℹ️ CLIENTE CHROMADB YA ESTABA RESETEADO")


def get_chroma_info() -> Dict[str, Any]:
    """
    Obtener información detallada del cliente ChromaDB.

    Returns:
        Dict con información del cliente, colecciones y configuración
    """
    try:
        client = get_chroma_client()

        # Información básica
        heartbeat = client.heartbeat()
        collections = client.list_collections()

        # Información de cada colección
        collections_info = []
        for collection in collections:
            collections_info.append(
                {
                    "name": collection.name,
                    "count": collection.count(),
                    "metadata": collection.metadata,
                }
            )

        # Información del directorio
        chroma_path = Path(CHROMA_DB_PATH)
        directory_info = {
            "path": str(chroma_path.absolute()),
            "exists": chroma_path.exists(),
            "files": list(chroma_path.glob("*")) if chroma_path.exists() else [],
        }

        return {
            "status": "connected",
            "heartbeat": heartbeat,
            "version": chromadb.__version__,
            "persistence_path": CHROMA_DB_PATH,
            "directory_info": directory_info,
            "collections_count": len(collections),
            "collections": collections_info,
            "settings": {
                "persist_directory": CHROMA_SETTINGS.persist_directory,
                "anonymized_telemetry": CHROMA_SETTINGS.anonymized_telemetry,
                "allow_reset": CHROMA_SETTINGS.allow_reset,
            },
        }

    except Exception as e:
        logger.error(f"❌ ERROR OBTENIENDO INFO CHROMADB: {e}")
        return {
            "status": "error",
            "error": str(e),
            "version": chromadb.__version__,
            "persistence_path": CHROMA_DB_PATH,
        }


# FastAPI Dependency
async def get_chroma_dependency() -> ChromaClient:
    """
    Dependency para FastAPI que proporciona cliente ChromaDB.

    Returns:
        ChromaClient: Cliente ChromaDB configurado
    """
    return get_chroma_client()


# Función para testing
def create_test_collection(collection_name: str = "test_collection") -> bool:
    """
    Crear una colección de prueba para verificar persistencia.

    Args:
        collection_name: Nombre de la colección de prueba

    Returns:
        bool: True si la colección se creó exitosamente
    """
    try:
        client = get_chroma_client()

        # Crear o obtener colección
        collection = client.get_or_create_collection(collection_name)

        # Agregar un documento de prueba
        test_doc = {
            "documents": ["Documento de prueba para verificar persistencia"],
            "metadatas": [{"type": "test", "created_by": "vector_db_module"}],
            "ids": ["test_doc_001"],
        }

        collection.add(**test_doc)

        # Verificar que se agregó
        count = collection.count()
        logger.info(
            f"✅ COLECCIÓN DE PRUEBA CREADA: {collection_name} (count: {count})"
        )

        return True

    except Exception as e:
        logger.error(f"❌ ERROR CREANDO COLECCIÓN DE PRUEBA: {e}")
        return False


def verify_persistence() -> bool:
    """
    Verificar que la persistencia funciona correctamente.

    Returns:
        bool: True si la persistencia está funcionando
    """
    try:
        # Obtener cliente y colecciones
        client = get_chroma_client()
        collections = client.list_collections()

        # Verificar que existe base de datos
        sqlite_file = Path(CHROMA_DB_PATH) / "chroma.sqlite3"

        persistence_ok = sqlite_file.exists() and sqlite_file.stat().st_size > 0

        logger.info(
            f"📁 ARCHIVO PERSISTENCIA: {sqlite_file} (exists: {sqlite_file.exists()})"
        )
        logger.info(f"📊 COLECCIONES PERSISTIDAS: {len(collections)}")
        logger.info(f"✅ PERSISTENCIA VERIFICADA: {persistence_ok}")

        return persistence_ok

    except Exception as e:
        logger.error(f"❌ ERROR VERIFICANDO PERSISTENCIA: {e}")
        return False


if __name__ == "__main__":
    # Demo de uso directo
    print("🔧 DEMO VECTOR_DB MODULE")
    print("=" * 50)

    # Configurar logging para demo
    logging.basicConfig(level=logging.INFO)

    # Obtener cliente
    client = get_chroma_client()

    # Mostrar información
    info = get_chroma_info()
    print(f"📋 ESTADO: {info['status']}")
    print(f"📁 PERSISTENCIA: {info['persistence_path']}")
    print(f"📊 COLECCIONES: {info['collections_count']}")

    # Crear colección de prueba
    success = create_test_collection()
    print(f"🧪 COLECCIÓN DE PRUEBA: {'✅ CREADA' if success else '❌ FALLÓ'}")

    # Verificar persistencia
    persistent = verify_persistence()
    print(f"💾 PERSISTENCIA: {'✅ FUNCIONAL' if persistent else '❌ PROBLEMA'}")
