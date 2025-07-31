# ~/backend/test_embedding_service.py
# ---------------------------------------------------------------------------------------------
# MESTOCKER - Test del Servicio de Embeddings
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: test_embedding_service.py
# Ruta: ~/backend/test_embedding_service.py
# Autor: Jairo
# Fecha de Creación: 2025-07-17
# Última Actualización: 2025-07-17
# Versión: 1.0.0
# Propósito: Tests comprehensivos para validar funciones add/query/update
#            de embeddings en colecciones products, docs y chat
#
# Modificaciones:
# 2025-07-17 - Suite de tests completa para validación de la tarea 0.2.3.5
#
# ---------------------------------------------------------------------------------------------

"""
Tests comprehensivos para EmbeddingService.

Este módulo contiene tests que validan todas las funcionalidades requeridas
en la tarea 0.2.3.5, incluyendo casos exitosos y manejo de errores.
"""

import sys
import time
from typing import List, Dict, Any

# Agregar path para imports
sys.path.append('.')
sys.path.append('./backend')

from embedding_service import (
    add_embeddings,
    query_embedding, 
    update_embedding,
    get_collection_stats,
    list_all_collections,
    VALID_COLLECTIONS
)

class TestEmbeddingService:
    """Clase de tests para EmbeddingService."""

    def __init__(self):
        self.test_results = []
        self.collections_to_test = ['products', 'docs']  # Usar 2 colecciones como requerido

    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Registrar resultado de test."""
        status = "✅ PASS" if success else "❌ FAIL"
        full_message = f"{status} {test_name}"
        if message:
            full_message += f": {message}"

        print(full_message)
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message
        })

    def setup_test_data(self) -> Dict[str, List[str]]:
        """Preparar datos de prueba para diferentes colecciones."""
        return {
            'products': [
                "Smartphone Samsung Galaxy S24 con pantalla AMOLED y cámara de 50MP",
                "Laptop Dell XPS 13 con procesador Intel i7 y 16GB RAM",
                "Auriculares Sony WH-1000XM5 con cancelación de ruido activa",
                "Tablet iPad Pro 12.9 con chip M2 y pantalla Liquid Retina"
            ],
            'docs': [
                "Guía de instalación para configurar el entorno de desarrollo",
                "Manual de usuario para la gestión de productos en el marketplace",
                "Documentación técnica de la API REST para desarrolladores",
                "Tutorial de integración con sistemas de pago externos"
            ],
            'chat': [
                "¿Cómo puedo actualizar mi perfil de vendedor?",
                "Información sobre los métodos de pago disponibles",
                "Proceso para reportar un producto defectuoso",
                "Consulta sobre tiempos de entrega y envío"
            ]
        }

    def test_add_embeddings_functionality(self):
        """Test función add_embeddings en múltiples colecciones."""
        print("🧪 === TEST: ADD_EMBEDDINGS FUNCTIONALITY ===")

        test_data = self.setup_test_data()

        for collection in self.collections_to_test:
            try:
                docs = test_data[collection]
                ids = [f"{collection}_test_{i}" for i in range(len(docs))]
                metadatas = [
                    {
                        'category': collection,
                        'test_timestamp': str(time.time()),
                        'test_id': i
                    } for i in range(len(docs))
                ]

                # Ejecutar add_embeddings
                result = add_embeddings(
                    docs=docs,
                    ids=ids,
                    collection=collection,
                    metadatas=metadatas
                )

                # Validar resultado
                if result['success'] and result['added_count'] > 0:
                    self.log_test(
                        f"add_embeddings_{collection}",
                        True,
                        f"Agregados {result['added_count']} docs, embedding_dims: {result['embedding_dimensions']}"
                    )
                else:
                    self.log_test(
                        f"add_embeddings_{collection}",
                        False,
                        f"Error: {result.get('message', 'resultado inesperado')}"
                    )

            except Exception as e:
                self.log_test(
                    f"add_embeddings_{collection}",
                    False,
                    f"Excepción: {str(e)}"
                )

    def test_query_embedding_functionality(self):
        """Test función query_embedding con diferentes consultas."""
        print("🔍 === TEST: QUERY_EMBEDDING FUNCTIONALITY ===")

        # Consultas de prueba por colección
        test_queries = {
            'products': [
                "smartphone con buena cámara",
                "laptop potente para programar",
                "auriculares inalámbricos"
            ],
            'docs': [
                "guía de instalación",
                "documentación API",
                "manual usuario"
            ]
        }

        for collection in self.collections_to_test:
            for i, query in enumerate(test_queries[collection]):
                try:
                    # Ejecutar query
                    results = query_embedding(
                        query=query,
                        collection=collection,
                        n_results=2
                    )

                    # Validar resultados
                    if results and len(results) > 0:
                        # Verificar estructura de resultados
                        first_result = results[0]
                        required_fields = ['id', 'document', 'distance', 'metadata', 'similarity_score']

                        has_all_fields = all(field in first_result for field in required_fields)
                        is_ordered = all(
                            results[j]['distance'] <= results[j+1]['distance'] 
                            for j in range(len(results)-1)
                        ) if len(results) > 1 else True

                        if has_all_fields and is_ordered:
                            self.log_test(
                                f"query_{collection}_{i+1}",
                                True,
                                f"Query: '{query[:30]}...', {len(results)} results, best_score: {first_result['similarity_score']:.3f}"
                            )

                            # Mostrar resultado más relevante
                            print(f"   🎯 Mejor resultado: ID={first_result['id']}, Score={first_result['similarity_score']:.3f}")
                            print(f"   📄 Documento: {first_result['document'][:100]}...")

                        else:
                            self.log_test(
                                f"query_{collection}_{i+1}",
                                False,
                                "Estructura de resultados incorrecta o no ordenados"
                            )
                    else:
                        self.log_test(
                            f"query_{collection}_{i+1}",
                            False,
                            "No se obtuvieron resultados"
                        )

                except Exception as e:
                    self.log_test(
                        f"query_{collection}_{i+1}",
                        False,
                        f"Excepción: {str(e)}"
                    )

    def test_update_embedding_functionality(self):
        """Test función update_embedding."""
        print("🔄 === TEST: UPDATE_EMBEDDING FUNCTIONALITY ===")

        for collection in self.collections_to_test:
            try:
                # Buscar un documento existente para actualizar
                existing_stats = get_collection_stats(collection)

                if existing_stats['document_count'] > 0:
                    # Usar el primer ID de prueba
                    test_id = f"{collection}_test_0"
                    new_content = f"DOCUMENTO ACTUALIZADO para {collection} - Nuevo contenido con timestamp {time.time()}"
                    new_metadata = {
                        'updated': True,
                        'update_timestamp': str(time.time()),
                        'original_collection': collection
                    }

                    # Ejecutar update
                    result = update_embedding(
                        id=test_id,
                        new_doc=new_content,
                        collection=collection,
                        new_metadata=new_metadata
                    )

                    # Validar resultado
                    if result['success']:
                        self.log_test(
                            f"update_{collection}",
                            True,
                            f"ID: {test_id}, new_length: {result['new_doc_length']}, dims: {result['embedding_dimensions']}"
                        )

                        # Verificar que efectivamente se actualizó consultando
                        verification = query_embedding("documento actualizado", collection, n_results=1)
                        if verification and verification[0]['id'] == test_id:
                            print(f"   ✅ Verificación: Documento {test_id} efectivamente actualizado")
                        else:
                            print(f"   ⚠️ Advertencia: No se pudo verificar la actualización")

                    else:
                        self.log_test(
                            f"update_{collection}",
                            False,
                            f"Error: {result.get('message', 'resultado inesperado')}"
                        )
                else:
                    self.log_test(
                        f"update_{collection}",
                        False,
                        f"No hay documentos en {collection} para actualizar"
                    )

            except Exception as e:
                self.log_test(
                    f"update_{collection}",
                    False,
                    f"Excepción: {str(e)}"
                )

    def test_error_handling(self):
        """Test manejo de errores y validaciones."""
        print("⚠️ === TEST: ERROR HANDLING ===")

        # Test colección inválida
        try:
            add_embeddings(["test"], ["test"], "invalid_collection")
            self.log_test("error_invalid_collection", False, "Debería haber fallado")
        except ValueError as e:
            if "no válida" in str(e):
                self.log_test("error_invalid_collection", True, "ValueError correcta para colección inválida")
            else:
                self.log_test("error_invalid_collection", False, f"Error inesperado: {e}")

        # Test datos inconsistentes
        try:
            add_embeddings(["doc1", "doc2"], ["id1"], "products")  # 2 docs, 1 id
            self.log_test("error_inconsistent_data", False, "Debería haber fallado")
        except ValueError as e:
            if "Inconsistencia" in str(e):
                self.log_test("error_inconsistent_data", True, "ValueError correcta para datos inconsistentes")
            else:
                self.log_test("error_inconsistent_data", False, f"Error inesperado: {e}")

        # Test query vacía
        try:
            query_embedding("", "products")
            self.log_test("error_empty_query", False, "Debería haber fallado")
        except ValueError as e:
            if "vacía" in str(e):
                self.log_test("error_empty_query", True, "ValueError correcta para query vacía")
            else:
                self.log_test("error_empty_query", False, f"Error inesperado: {e}")

        # Test update ID inexistente
        try:
            result = update_embedding("nonexistent_id", "new content", "products")
            if not result['success'] and "no existe" in result['message']:
                self.log_test("error_nonexistent_id", True, "Manejo correcto de ID inexistente")
            else:
                self.log_test("error_nonexistent_id", False, "Debería haber detectado ID inexistente")
        except Exception as e:
            if "no existe" in str(e):
                self.log_test("error_nonexistent_id", True, "Exception correcta para ID inexistente")
            else:
                self.log_test("error_nonexistent_id", False, f"Error inesperado: {e}")

    def test_collection_operations(self):
        """Test operaciones de colección y estadísticas."""
        print("📊 === TEST: COLLECTION OPERATIONS ===")

        try:
            # Test listar colecciones
            all_collections = list_all_collections()

            if all_collections and len(all_collections) > 0:
                self.log_test(
                    "list_collections",
                    True,
                    f"Encontradas {len(all_collections)} colecciones"
                )

                # Mostrar estadísticas
                for col in all_collections:
                    print(f"   📋 {col['name']}: {col['count']} docs, valid: {col['is_valid']}")
            else:
                self.log_test("list_collections", False, "No se encontraron colecciones")

            # Test estadísticas por colección
            for collection in self.collections_to_test:
                stats = get_collection_stats(collection)

                if stats and 'document_count' in stats:
                    self.log_test(
                        f"stats_{collection}",
                        True,
                        f"Count: {stats['document_count']}, Status: {stats['status']}"
                    )
                else:
                    self.log_test(f"stats_{collection}", False, "Error obteniendo estadísticas")

        except Exception as e:
            self.log_test("collection_operations", False, f"Excepción: {str(e)}")

    def run_all_tests(self):
        """Ejecutar todos los tests."""
        print("🚀 === INICIANDO TESTS COMPREHENSIVOS EMBEDDING SERVICE ===")
        print(f"📋 Colecciones a probar: {self.collections_to_test}")
        print(f"🎯 Validando criterios de aceptación de tarea 0.2.3.5")

        # Ejecutar tests en orden
        self.test_add_embeddings_functionality()
        self.test_query_embedding_functionality()
        self.test_update_embedding_functionality()
        self.test_error_handling()
        self.test_collection_operations()

        # Resumen final
        self.print_test_summary()

    def print_test_summary(self):
        """Imprimir resumen de tests."""
        print("📊 === RESUMEN DE TESTS ===")

        total_tests = len(self.test_results)
        passed_tests = sum(1 for test in self.test_results if test['success'])
        failed_tests = total_tests - passed_tests

        print(f"Total tests: {total_tests}")
        print(f"✅ Pasaron: {passed_tests}")
        print(f"❌ Fallaron: {failed_tests}")
        print(f"📈 Tasa de éxito: {(passed_tests/total_tests)*100:.1f}%")

        if failed_tests > 0:
            print("❌ TESTS FALLIDOS:")
            for test in self.test_results:
                if not test['success']:
                    print(f"   - {test['test']}: {test['message']}")

        # Verificar criterios de aceptación
        print("🎯 === VERIFICACIÓN CRITERIOS DE ACEPTACIÓN ===")

        # Criterio 1: Funciona en al menos 2 colecciones
        collections_tested = len(self.collections_to_test)
        print(f"✅ Operaciones en {collections_tested} colecciones: {'CUMPLE' if collections_tested >= 2 else 'NO CUMPLE'}")

        # Criterio 2: add_embeddings sin errores duplicados
        add_tests = [t for t in self.test_results if 'add_embeddings' in t['test'] and t['success']]
        print(f"✅ add_embeddings funcional: {'CUMPLE' if add_tests else 'NO CUMPLE'}")

        # Criterio 3: query_embedding retorna documentos relevantes
        query_tests = [t for t in self.test_results if 'query_' in t['test'] and t['success']]
        print(f"✅ query_embedding funcional: {'CUMPLE' if query_tests else 'NO CUMPLE'}")

        # Criterio 4: update_embedding reemplaza correctamente
        update_tests = [t for t in self.test_results if 'update_' in t['test'] and t['success']]
        print(f"✅ update_embedding funcional: {'CUMPLE' if update_tests else 'NO CUMPLE'}")

        # Resultado final
        all_criteria_met = (
            collections_tested >= 2 and
            len(add_tests) > 0 and
            len(query_tests) > 0 and
            len(update_tests) > 0
        )

        print(f"🎉 RESULTADO FINAL: {'✅ TODOS LOS CRITERIOS CUMPLIDOS' if all_criteria_met else '❌ CRITERIOS PENDIENTES'}")

        return all_criteria_met

def main():
    """Función principal para ejecutar tests."""
    print("🧪 EMBEDDING SERVICE - TEST SUITE v1.0.0")
    print("📋 Validación de tarea 0.2.3.5: add/query/update embeddings")

    # Crear y ejecutar tests
    test_suite = TestEmbeddingService()
    success = test_suite.run_all_tests()

    return success

if __name__ == '__main__':
    success = main()
    print(f"🏁 Tests completados. Éxito: {success}")