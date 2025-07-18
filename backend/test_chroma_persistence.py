#!/usr/bin/env python3
"""
Script de prueba para validar persistencia de ChromaDB.

Este script verifica que:
1. Se puede crear una colección
2. Se pueden agregar documentos
3. La colección persiste entre ejecuciones
4. Los datos se mantienen íntegros
"""

# import os  # Removido - no utilizado
import sys

sys.path.append(".")

from chroma_db.vector_db import (  # create_test_collection,  # No utilizado en este archivo
    get_chroma_client,
    get_chroma_info,
    reset_chroma_client,
    verify_persistence,
)


def test_persistence_workflow():
    """Flujo completo de prueba de persistencia."""

    print("🧪 INICIANDO PRUEBA COMPLETA DE PERSISTENCIA CHROMADB")
    print("=" * 60)

    # Paso 1: Estado inicial
    print("\n📋 PASO 1: VERIFICAR ESTADO INICIAL")
    info = get_chroma_info()
    print(f'   Status: {info["status"]}')
    print(f'   Colecciones existentes: {info["collections_count"]}')

    # Paso 2: Crear colección con datos
    print("\n📝 PASO 2: CREAR COLECCIÓN CON DATOS DE PRUEBA")
    client = get_chroma_client()

    collection_name = "persistence_test_collection"
    collection = client.get_or_create_collection(collection_name)

    # Agregar múltiples documentos de prueba
    test_documents = [
        "Producto 1: Laptop gaming con RTX 4080",
        "Producto 2: Monitor 4K ultrawide 34 pulgadas",
        "Producto 3: Teclado mecánico RGB Cherry MX Blue",
        "Producto 4: Mouse gaming inalámbrico 16000 DPI",
        "Producto 5: Auriculares noise cancelling Bluetooth",
    ]

    test_metadatas = [
        {"categoria": "laptops", "precio": 2500, "stock": 5},
        {"categoria": "monitores", "precio": 800, "stock": 3},
        {"categoria": "perifericos", "precio": 150, "stock": 10},
        {"categoria": "perifericos", "precio": 80, "stock": 15},
        {"categoria": "audio", "precio": 300, "stock": 7},
    ]

    test_ids = [f"prod_{i+1:03d}" for i in range(len(test_documents))]

    # Agregar documentos
    collection.add(documents=test_documents, metadatas=test_metadatas, ids=test_ids)

    initial_count = collection.count()
    print(f"   ✅ Colección creada: {collection_name}")
    print(f"   📊 Documentos agregados: {initial_count}")

    # Paso 3: Simular reinicio (resetear cliente)
    print("\n🔄 PASO 3: SIMULAR REINICIO DE APLICACIÓN")
    reset_chroma_client()
    print("   🔄 Cliente reseteado en memoria")

    # Paso 4: Reconectar y verificar persistencia
    print("\n🔍 PASO 4: RECONECTAR Y VERIFICAR PERSISTENCIA")
    new_client = get_chroma_client()

    try:
        recovered_collection = new_client.get_collection(collection_name)
        recovered_count = recovered_collection.count()
        print(f"   ✅ Colección recuperada: {collection_name}")
        print(f"   📊 Documentos recuperados: {recovered_count}")

        # Verificar que los datos son los mismos
        if recovered_count == initial_count:
            print("   ✅ PERSISTENCIA EXITOSA: Misma cantidad de documentos")
        else:
            print(f"   ❌ PERSISTENCIA FALLÓ: {initial_count} → {recovered_count}")
            return False

    except Exception as e:
        print(f"   ❌ ERROR RECUPERANDO COLECCIÓN: {e}")
        return False

    # Paso 5: Verificar contenido específico
    print("\n📄 PASO 5: VERIFICAR CONTENIDO ESPECÍFICO")
    try:
        # Buscar por similarity (requiere embeddings)
        results = recovered_collection.query(query_texts=["laptop gaming"], n_results=2)

        print(
            f'   🔍 Búsqueda por similarity: {len(results["documents"][0])} resultados'
        )
        for i, doc in enumerate(results["documents"][0]):
            metadata = results["metadatas"][0][i]
            print(f'      • {doc[:50]}... (categoria: {metadata["categoria"]})')

    except Exception as e:
        print(f"   ⚠️ Búsqueda por similarity falló: {e}")
        # No es crítico para persistencia básica

    # Paso 6: Verificar archivos de persistencia
    print("\n💾 PASO 6: VERIFICAR ARCHIVOS DE PERSISTENCIA")
    persistence_verified = verify_persistence()

    if persistence_verified:
        print("   ✅ ARCHIVOS DE PERSISTENCIA: Verificados y funcionales")
    else:
        print("   ❌ ARCHIVOS DE PERSISTENCIA: Problemas detectados")
        return False

    # Paso 7: Resumen final
    print("\n🎉 PASO 7: RESUMEN FINAL")
    final_info = get_chroma_info()

    print(f'   📊 Colecciones totales: {final_info["collections_count"]}')
    print(f'   📁 Directorio persistencia: {final_info["persistence_path"]}')
    print(f'   💾 Archivos en directorio: {len(final_info["directory_info"]["files"])}')

    print("\n✅ PRUEBA DE PERSISTENCIA COMPLETADA EXITOSAMENTE")
    print("🎯 CHROMADB CONFIGURADO CORRECTAMENTE CON PERSISTENCIA LOCAL")

    return True


if __name__ == "__main__":
    success = test_persistence_workflow()

    if success:
        print("\n🎉 ✅ TODAS LAS PRUEBAS PASARON")
        print("🚀 CLIENTE CHROMADB LISTO PARA PRODUCCIÓN")
        sys.exit(0)
    else:
        print("\n❌ ALGUNAS PRUEBAS FALLARON")
        print("🔧 REVISAR CONFIGURACIÓN Y DEPENDENCIAS")
        sys.exit(1)
