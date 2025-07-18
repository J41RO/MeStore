#!/usr/bin/env python3
"""
Script para inicializar colecciones base de ChromaDB para agentes IA.

Colecciones creadas:
- products: Embeddings de productos del marketplace
- docs: Embeddings de documentación y conocimiento
- chat: Embeddings de conversaciones y contexto de chat

Características:
- Verificación previa: no duplica colecciones existentes
- Metadata descriptiva para identificación
- Logging detallado de operaciones
- Persistencia verificada
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Agregar el directorio backend al path para imports
backend_dir = Path(__file__).parent.parent
sys.path.append(str(backend_dir))

try:
    import chromadb
    from chromadb.config import Settings
except ImportError as e:
    print(f"❌ ERROR: ChromaDB no disponible: {e}")
    print("💡 Instalar con: pip install chromadb")
    sys.exit(1)


class CollectionInitializer:
    """Inicializador de colecciones base para agentes IA."""
    
    # Definición de colecciones con metadata
    COLLECTIONS_CONFIG = {
        "products": {
            "metadata": {
                "type": "agent_store",
                "purpose": "product_embeddings",
                "agent_type": "marketplace",
                "description": "Embeddings de productos del marketplace para búsqueda semántica",
                "created_by": "initialize_collections_script",
                "version": "1.0.0"
            }
        },
        "docs": {
            "metadata": {
                "type": "agent_store",
                "purpose": "documentation_embeddings",
                "agent_type": "knowledge",
                "description": "Embeddings de documentación y base de conocimiento",
                "created_by": "initialize_collections_script",
                "version": "1.0.0"
            }
        },
        "chat": {
            "metadata": {
                "type": "agent_store",
                "purpose": "conversation_embeddings",
                "agent_type": "conversational",
                "description": "Embeddings de conversaciones y contexto de chat",
                "created_by": "initialize_collections_script",
                "version": "1.0.0"
            }
        }
    }
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """Inicializar el cliente ChromaDB con persistencia."""
        self.persist_directory = persist_directory
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Inicializar cliente ChromaDB con configuración de persistencia."""
        try:
            # Configurar cliente con persistencia
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    is_persistent=True
                )
            )
            print(f"✅ Cliente ChromaDB inicializado con persistencia en: {self.persist_directory}")
            
        except Exception as e:
            print(f"❌ ERROR inicializando cliente ChromaDB: {e}")
            raise
    
    def get_existing_collections(self) -> List[str]:
        """Obtener lista de colecciones existentes."""
        try:
            collections = self.client.list_collections()
            collection_names = [col.name for col in collections]
            
            if collection_names:
                print(f"📋 Colecciones existentes encontradas: {collection_names}")
            else:
                print("📋 No hay colecciones existentes")
            
            return collection_names
            
        except Exception as e:
            print(f"❌ ERROR listando colecciones: {e}")
            return []
    
    def create_collection_if_not_exists(self, name: str, config: Dict[str, Any]) -> bool:
        """Crear colección si no existe."""
        try:
            existing_collections = self.get_existing_collections()
            
            if name in existing_collections:
                print(f"ℹ️ Colección '{name}' ya existe - saltando creación")
                
                # Obtener información de la colección existente
                collection = self.client.get_collection(name)
                count = collection.count()
                print(f"   📊 Documentos actuales en '{name}': {count}")
                return False
            
            # Crear nueva colección
            print(f"🔧 Creando colección '{name}'...")
            
            # Agregar timestamp a metadata
            metadata = config["metadata"].copy()
            metadata["created_at"] = datetime.now().isoformat()
            
            collection = self.client.create_collection(
                name=name,
                metadata=metadata
            )
            
            print(f"✅ Colección '{name}' creada exitosamente")
            print(f"   📋 Metadata: {metadata['purpose']}")
            print(f"   🎯 Agente: {metadata['agent_type']}")
            
            return True
            
        except Exception as e:
            print(f"❌ ERROR creando colección '{name}': {e}")
            return False
    
    def initialize_all_collections(self) -> Dict[str, bool]:
        """Inicializar todas las colecciones definidas."""
        print("=== 🚀 INICIALIZANDO COLECCIONES BASE PARA AGENTES IA ===")
        print(f"📍 Directorio de persistencia: {self.persist_directory}")
        print(f"⏰ Timestamp: {datetime.now().isoformat()}")
        print()
        
        results = {}
        
        for collection_name, config in self.COLLECTIONS_CONFIG.items():
            print(f"🔍 Procesando colección: '{collection_name}'")
            created = self.create_collection_if_not_exists(collection_name, config)
            results[collection_name] = created
            print()
        
        return results
    
    def verify_collections(self) -> bool:
        """Verificar que todas las colecciones estén creadas correctamente."""
        print("=== 🔍 VERIFICACIÓN DE COLECCIONES ===")
        
        try:
            existing_collections = self.get_existing_collections()
            expected_collections = list(self.COLLECTIONS_CONFIG.keys())
            
            # Verificar que todas las colecciones esperadas existan
            missing_collections = []
            for expected in expected_collections:
                if expected not in existing_collections:
                    missing_collections.append(expected)
            
            if missing_collections:
                print(f"❌ FALTA(N) COLECCIÓN(ES): {missing_collections}")
                return False
            
            # Verificar cada colección individualmente
            print("📊 Estado detallado de colecciones:")
            for collection_name in expected_collections:
                try:
                    collection = self.client.get_collection(collection_name)
                    count = collection.count()
                    metadata = collection.metadata
                    
                    print(f"   ✅ {collection_name}:")
                    print(f"      📋 Documentos: {count}")
                    print(f"      🎯 Propósito: {metadata.get('purpose', 'N/A')}")
                    print(f"      🤖 Agente: {metadata.get('agent_type', 'N/A')}")
                    print(f"      📅 Creado: {metadata.get('created_at', 'N/A')}")
                    
                except Exception as e:
                    print(f"   ❌ Error accediendo a {collection_name}: {e}")
                    return False
            
            print()
            print("✅ TODAS LAS COLECCIONES VERIFICADAS CORRECTAMENTE")
            return True
            
        except Exception as e:
            print(f"❌ ERROR en verificación: {e}")
            return False
    
    def test_persistence(self) -> bool:
        """Probar que la persistencia funciona correctamente."""
        print("=== 🧪 PRUEBA DE PERSISTENCIA ===")
        
        try:
            # Crear un nuevo cliente para simular reinicio
            print("🔄 Simulando reinicio del sistema...")
            test_client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    is_persistent=True
                )
            )
            
            # Verificar que las colecciones persisten
            collections = test_client.list_collections()
            collection_names = [col.name for col in collections]
            expected_collections = list(self.COLLECTIONS_CONFIG.keys())
            
            missing_after_restart = []
            for expected in expected_collections:
                if expected not in collection_names:
                    missing_after_restart.append(expected)
            
            if missing_after_restart:
                print(f"❌ PERSISTENCIA FALLÓ: Colecciones perdidas: {missing_after_restart}")
                return False
            
            print(f"✅ PERSISTENCIA VERIFICADA: {len(collection_names)} colecciones recuperadas")
            print(f"📋 Colecciones persistentes: {collection_names}")
            
            # Verificar archivos en disco
            chroma_path = Path(self.persist_directory)
            if chroma_path.exists():
                files = list(chroma_path.rglob("*"))
                print(f"📁 Archivos persistidos: {len(files)} archivos en disco")
            else:
                print("⚠️ Directorio de persistencia no encontrado")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ ERROR en prueba de persistencia: {e}")
            return False


def main():
    """Función principal del script."""
    print("🚀 INICIALIZADOR DE COLECCIONES CHROMADB v1.0.0")
    print("📊 Colecciones objetivo: products, docs, chat")
    print()
    
    try:
        # Inicializar el sistema
        initializer = CollectionInitializer()
        
        # Crear todas las colecciones
        results = initializer.initialize_all_collections()
        
        # Mostrar resumen de creación
        print("=== 📊 RESUMEN DE CREACIÓN ===")
        created_count = sum(1 for created in results.values() if created)
        existing_count = len(results) - created_count
        
        print(f"🆕 Colecciones creadas: {created_count}")
        print(f"📋 Colecciones existentes: {existing_count}")
        print(f"📊 Total de colecciones: {len(results)}")
        print()
        
        # Verificar todas las colecciones
        verification_success = initializer.verify_collections()
        
        if not verification_success:
            print("❌ VERIFICACIÓN FALLÓ")
            sys.exit(1)
        
        # Probar persistencia
        persistence_success = initializer.test_persistence()
        
        if not persistence_success:
            print("❌ PRUEBA DE PERSISTENCIA FALLÓ")
            sys.exit(1)
        
        print("=== 🎉 INICIALIZACIÓN COMPLETADA EXITOSAMENTE ===")
        print("✅ Las 3 colecciones base están listas para los agentes IA")
        print("🔧 Las colecciones persistirán entre reinicios del sistema")
        print("📊 Sistema ChromaDB completamente configurado")
        
    except Exception as e:
        print(f"❌ ERROR CRÍTICO: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
