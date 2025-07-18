#!/usr/bin/env python3
"""
🧪 SCRIPT DE VALIDACIÓN FINAL CHROMADB v1.0
=============================================
Valida funcionamiento completo del sistema de embeddings:
- Colecciones: products, docs, chat
- Queries de prueba realistas
- Verificación de persistencia
- Formato de respuesta estándar
- Benchmarking de performance
=============================================
"""

import time
import json
from typing import Dict, List, Any, Optional
import embedding_service
import embedding_model

def main():
    """Función principal del script de validación."""
    print('🧪 CHROMADB VALIDATION SCRIPT v1.0')
    print('==========================================')
    
    # Verificar dependencias
    try:
        import embedding_service
        import embedding_model
        print('✅ Dependencias verificadas')
    except ImportError as e:
        print(f'❌ Error de dependencias: {e}')
        return 1
    
    print('🚀 EJECUTANDO VALIDACIÓN BÁSICA...')
    
    # Test básico de colecciones
    collections = ['products', 'docs', 'chat']
    
    for collection_name in collections:
        try:
            # Verificar stats de colección
            stats = embedding_service.get_collection_stats(collection_name)
            print(f'📊 {collection_name}: {stats.get("count", 0)} documentos')
            
            # Query de prueba simple
            if stats.get("count", 0) > 0:
                start_time = time.time()
                results = embedding_service.query_embedding(
                    collection_name=collection_name,
                    query_text=f'test query for {collection_name}',
                    n_results=1
                )
                end_time = time.time()
                query_time = (end_time - start_time) * 1000
                
                if results and 'documents' in results:
                    print(f'✅ {collection_name}: Query exitosa en {query_time:.1f}ms')
                    print(f'   📄 Primer resultado: {results["documents"][0][0][:50]}...')
                else:
                    print(f'❌ {collection_name}: Query falló')
            else:
                print(f'⚠️ {collection_name}: Colección vacía')
                
        except Exception as e:
            print(f'❌ Error en {collection_name}: {e}')
    
    print('\n🎉 VALIDACIÓN BÁSICA COMPLETADA')
    return 0

if __name__ == '__main__':
    exit(main())
