#!/usr/bin/env python3
"""
Script de verificación para ChromaDB y sentence-transformers
Usar para verificar que el entorno está correctamente configurado
"""
import chromadb
from sentence_transformers import SentenceTransformer


def verify_chromadb_setup():
    """Verificar que ChromaDB está funcionando correctamente"""
    try:
        # Crear cliente persistente
        client = chromadb.PersistentClient(path="./chroma_db")

        # Verificar funcionalidad básica
        collections = client.list_collections()
        print(f"✅ ChromaDB funcionando - {len(collections)} colecciones existentes")

        # Verificar sentence-transformers
        model = SentenceTransformer("all-MiniLM-L6-v2")
        test_embedding = model.encode(["Test sentence"])
        print(
            f"✅ Sentence-transformers funcionando - embedding shape: {test_embedding.shape}"
        )

        return True
    except Exception as e:
        print(f"❌ Error en verificación: {e}")
        return False


if __name__ == "__main__":
    verify_chromadb_setup()
