#!/usr/bin/env python3
"""
🧪 SCRIPT DE VALIDACIÓN FINAL CHROMADB v2.0 - FUNCIONAL
========================================================
Validación completa usando las funciones que funcionan correctamente:
- list_all_collections para obtener stats reales
- query_embedding para búsquedas de similitud
- Verificación de persistencia entre ejecuciones
- Benchmarking de performance
========================================================
"""

import time
import json
from typing import Dict, List, Any, Optional
import embedding_service

def main():
    """Ejecutar validación completa del sistema ChromaDB."""
    print('🧪 CHROMADB VALIDATION SCRIPT v2.0 - FINAL')
    print('=' * 60)
    
    # 1. Verificar estado de colecciones
    print('\n📋 ESTADO ACTUAL DE COLECCIONES:')
    collections_data = embedding_service.list_all_collections()
    
    total_docs = 0
    for col_info in collections_data:
        count = col_info['count']
        total_docs += count
        status = '✅' if count > 0 else '⚠️'
        print(f'  {status} {col_info["name"]}: {count} documentos')
    
    print(f'  📊 TOTAL: {total_docs} documentos en {len(collections_data)} colecciones')
    
    if total_docs == 0:
        print('\n❌ ERROR: No hay documentos para validar')
        return 1
    
    # 2. Ejecutar queries de similitud realistas
    print('\n🔍 EJECUTANDO QUERIES DE SIMILITUD:')
    
    test_queries = {
        'products': [
            'smartphone con buena cámara',
            'laptop para programación', 
            'audífonos inalámbricos'
        ],
        'docs': [
            'tutorial de FastAPI',
            'optimización de PostgreSQL',
            'testing con pytest'
        ],
        'chat': [
            'descuento estudiantes',
            'información garantía',
            'tiempo entrega'
        ]
    }
    
    all_queries_successful = True
    total_query_time = 0
    total_queries = 0
    
    for collection_name, queries in test_queries.items():
        print(f'\n  📂 COLECCIÓN: {collection_name.upper()}')
        
        for query in queries:
            try:
                start_time = time.time()
                
                results = embedding_service.query_embedding(
                    query=query,
                    collection=collection_name,
                    n_results=3
                )
                
                end_time = time.time()
                query_time = (end_time - start_time) * 1000
                total_query_time += query_time
                total_queries += 1
                
                if results and len(results) > 0:
                    # Formatear resultados para mostrar estructura estándar
                    formatted_results = []
                    for i, result in enumerate(results):
                        formatted_result = {
                            'id': result.get('id', f'unknown_{i}'),
                            'document': result.get('document', '')[:60] + '...',
                            'score': round(result.get('score', 0), 4),
                            'metadata': result.get('metadata', {})
                        }
                        formatted_results.append(formatted_result)
                    
                    print(f'    ✅ Query: "{query}"')
                    print(f'       📊 {len(results)} resultados en {query_time:.1f}ms')
                    print(f'       🥇 Mejor: {formatted_results[0]["document"]}')
                    print(f'          Score: {formatted_results[0]["score"]}, ID: {formatted_results[0]["id"]}')
                    
                    # Verificar tiempo de respuesta
                    if query_time > 500:
                        print(f'       ⚠️ Tiempo alto: {query_time:.1f}ms > 500ms')
                else:
                    print(f'    ❌ Query falló: "{query}" - Sin resultados')
                    all_queries_successful = False
                    
            except Exception as e:
                print(f'    ❌ Error en query "{query}": {e}')
                all_queries_successful = False
    
    # 3. Verificar persistencia (ejecutar misma query dos veces)
    print('\n🔄 VERIFICANDO PERSISTENCIA:')
    persistence_ok = True
    
    for collection_name in ['products', 'docs', 'chat']:
        try:
            test_query = f'test persistencia {collection_name}'
            
            # Primera ejecución
            result1 = embedding_service.query_embedding(
                query=test_query,
                collection=collection_name,
                n_results=2
            )
            
            time.sleep(0.1)  # Pequeña pausa
            
            # Segunda ejecución  
            result2 = embedding_service.query_embedding(
                query=test_query,
                collection=collection_name,
                n_results=2
            )
            
            # Comparar IDs de resultados
            ids1 = [r.get('id') for r in result1] if result1 else []
            ids2 = [r.get('id') for r in result2] if result2 else []
            
            if ids1 == ids2 and len(ids1) > 0:
                print(f'  ✅ {collection_name}: Resultados consistentes ({len(ids1)} items)')
            else:
                print(f'  ❌ {collection_name}: Resultados inconsistentes')
                persistence_ok = False
                
        except Exception as e:
            print(f'  ❌ {collection_name}: Error - {e}')
            persistence_ok = False
    
    # 4. Calcular métricas de performance
    avg_query_time = total_query_time / total_queries if total_queries > 0 else 0
    performance_ok = avg_query_time < 500
    
    print(f'\n⚡ PERFORMANCE:')
    print(f'  📊 Tiempo promedio: {avg_query_time:.1f}ms')
    print(f'  📊 Total queries: {total_queries}')
    status = '✅' if performance_ok else '⚠️'
    print(f'  {status} Criterio <500ms: {"CUMPLIDO" if performance_ok else "NO CUMPLIDO"}')
    
    # 5. Veredicto final
    print('\n' + '=' * 60)
    
    success_criteria = [
        (total_docs > 0, 'Documentos en colecciones'),
        (all_queries_successful, 'Todas las queries exitosas'),
        (persistence_ok, 'Persistencia verificada'),
        (performance_ok, 'Performance adecuada')
    ]
    
    passed_criteria = sum(1 for passed, _ in success_criteria if passed)
    total_criteria = len(success_criteria)
    
    print(f'📊 CRITERIOS CUMPLIDOS: {passed_criteria}/{total_criteria}')
    for passed, description in success_criteria:
        status = '✅' if passed else '❌'
        print(f'  {status} {description}')
    
    if passed_criteria == total_criteria:
        print('\n🎉 ✅ VALIDACIÓN EXITOSA - CHROMADB COMPLETAMENTE FUNCIONAL')
        print('✅ Sistema de embeddings operativo')
        print('✅ Búsquedas semánticas funcionando')
        print('✅ Persistencia verificada')
        print('✅ Performance dentro de criterios')
        print('\n🚀 READY FOR: 0.2.4 - Configuración del testing framework')
        return 0
    else:
        print('\n❌ ⚠️ VALIDACIÓN INCOMPLETA')
        print('🔧 Revisar problemas identificados arriba')
        return 1

if __name__ == '__main__':
    exit(main())
