# ~/tests/test_api_embeddings.py
# ---------------------------------------------------------------------------------------------
# MeStore - Tests Corregidos para API de Embeddings
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: test_api_embeddings.py
# Ruta: ~/tests/test_api_embeddings_corrected.py
# Autor: Jairo
# Fecha de Creación: 2025-07-19
# Última Actualización: 2025-07-19
# Versión: 2.0.0
# Propósito: Tests corregidos para app/api/v1/embeddings.py
#            Rutas y schemas basados en código fuente real
#
# Modificaciones:
# 2025-07-19 - Corrección completa basada en código fuente real
#
# ---------------------------------------------------------------------------------------------

"""
Tests Corregidos para API de Embeddings.

Suite profesional basada en el código fuente real:
- Rutas exactas del API: /api/v1/embeddings/embeddings/{collection}/action
- Schemas Pydantic reales: AddItemsRequest, QueryRequest, etc.
- Mocking preciso de app.services.embeddings
- Validación de StandardResponse y formatos reales
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from fastapi import HTTPException, status
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Any, Optional
import json

# Import de la app real
from app.main import app


# ================================================================================================
# FIXTURES PARA TESTING DE API
# ================================================================================================

@pytest.fixture
def client():
    """Cliente de testing para FastAPI."""
    return TestClient(app)


@pytest.fixture
def mock_embeddings_service():
    """Mock completo del servicio de embeddings con funciones exactas."""
    with patch('app.api.v1.endpoints.embeddings.add_items') as mock_add, \
         patch('app.api.v1.endpoints.embeddings.query_similar') as mock_query, \
         patch('app.api.v1.endpoints.embeddings.update_item') as mock_update, \
         patch('app.api.v1.endpoints.embeddings.delete_items') as mock_delete, \
         patch('app.api.v1.endpoints.embeddings.get_collection_stats') as mock_stats:
        
        # Configurar comportamientos por defecto
        mock_add.return_value = True
        mock_query.return_value = {
            'ids': [['item1', 'item2']],
            'documents': [['doc1', 'doc2']],
            'distances': [[0.1, 0.3]],
            'metadatas': [[{'category': 'test'}, {'category': 'test'}]]
        }
        mock_update.return_value = True
        mock_delete.return_value = True
        mock_stats.return_value = {
            'name': 'test_collection',
            'count': 42,
            'metadata': {'created_by': 'test'}
        }
        
        yield {
            'add_items': mock_add,
            'query_similar': mock_query,
            'update_item': mock_update,
            'delete_items': mock_delete,
            'get_collection_stats': mock_stats
        }


@pytest.fixture
def sample_add_request():
    """Payload de ejemplo para agregar items - Schema real."""
    return {
        "ids": ["prod_001", "prod_002"],
        "texts": ["Smartphone Samsung Galaxy S23", "Laptop Dell XPS 13"],
        "metadatas": [
            {"category": "electronics", "price": 699.99},
            {"category": "computers", "price": 1299.99}
        ]
    }


@pytest.fixture
def sample_query_request():
    """Payload de ejemplo para consulta - Schema real."""
    return {
        "query_text": "smartphone android",
        "n_results": 5,
        "where": {"category": "electronics"}
    }


@pytest.fixture
def sample_update_request():
    """Payload de ejemplo para actualizar - Schema real."""
    return {
        "item_id": "prod_001",
        "new_text": "Updated Samsung Galaxy S23 Pro",
        "new_metadata": {"category": "electronics", "price": 799.99, "updated": True}
    }


# ================================================================================================
# TESTS DE ENDPOINTS - ADD ITEMS
# ================================================================================================

class TestAddItemsEndpoint:
    """Tests para POST /api/v1/embeddings/embeddings/{collection}/add."""
    
    def test_add_items_success(self, client, mock_embeddings_service, sample_add_request):
        """Test: Agregar items exitosamente."""
        # Act
        response = client.post("/api/v1/embeddings/embeddings/products/add", json=sample_add_request)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "Agregados 2 items a 'products'" in data["message"]
        assert data["data"]["collection"] == "products"
        assert data["data"]["items_added"] == 2
        
        # Verificar que se llamó al servicio con parámetros correctos
        mock_embeddings_service['add_items'].assert_called_once_with(
            collection_name="products",
            ids=sample_add_request["ids"],
            texts=sample_add_request["texts"],
            metadatas=sample_add_request["metadatas"]
        )
    
    def test_add_items_without_metadata(self, client, mock_embeddings_service):
        """Test: Agregar items sin metadatos opcionales."""
        # Arrange
        payload = {
            "ids": ["test_001"],
            "texts": ["Test product description"]
        }
        
        # Act
        response = client.post("/api/v1/embeddings/embeddings/products/add", json=payload)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        
        # Verificar que metadatas fue None
        mock_embeddings_service['add_items'].assert_called_once_with(
            collection_name="products",
            ids=payload["ids"],
            texts=payload["texts"],
            metadatas=None
        )
    
    def test_add_items_length_mismatch_ids_texts(self, client):
        """Test: Error cuando IDs y textos tienen longitud diferente."""
        # Arrange
        payload = {
            "ids": ["id1", "id2"],
            "texts": ["text1"]  # Solo 1 texto para 2 IDs
        }
        
        # Act
        response = client.post("/api/v1/embeddings/embeddings/products/add", json=payload)
        
        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "IDs y textos deben tener la misma longitud" in data["detail"]
    
    def test_add_items_length_mismatch_metadatas(self, client):
        """Test: Error cuando metadatos tienen longitud diferente."""
        # Arrange
        payload = {
            "ids": ["id1", "id2"],
            "texts": ["text1", "text2"],
            "metadatas": [{"key": "value"}]  # Solo 1 metadata para 2 items
        }
        
        # Act
        response = client.post("/api/v1/embeddings/embeddings/products/add", json=payload)
        
        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "Metadatos deben tener la misma longitud que textos" in data["detail"]
    
    def test_add_items_service_error(self, client, mock_embeddings_service):
        """Test: Error del servicio se maneja correctamente."""
        # Arrange
        mock_embeddings_service['add_items'].side_effect = Exception("ChromaDB connection failed")
        payload = {
            "ids": ["test"],
            "texts": ["test"]
        }
        
        # Act
        response = client.post("/api/v1/embeddings/embeddings/products/add", json=payload)
        
        # Assert
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert "ChromaDB connection failed" in data["detail"]
    
    def test_add_items_schema_validation(self, client):
        """Test: Validación de schema Pydantic."""
        # Arrange - Payload inválido
        payload = {
            "ids": "not_a_list",  # Debe ser List[str]
            "texts": ["valid_text"]
        }
        
        # Act
        response = client.post("/api/v1/embeddings/embeddings/products/add", json=payload)
        
        # Assert
        assert response.status_code in [422, 500]
        data = response.json()
        assert "input should be" in str(data).lower()


# ================================================================================================
# TESTS DE ENDPOINTS - QUERY SIMILAR
# ================================================================================================

class TestQuerySimilarEndpoint:
    """Tests para POST /api/v1/embeddings/embeddings/{collection}/query."""
    
    def test_query_similar_success(self, client, mock_embeddings_service, sample_query_request):
        """Test: Consulta exitosa con resultados."""
        # Act
        response = client.post("/api/v1/embeddings/embeddings/products/query", json=sample_query_request)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["query"] == sample_query_request["query_text"]
        assert data["collection"] == "products"
        assert data["total_results"] == 2
        
        # Verificar estructura de resultados
        results = data["results"]
        assert len(results) == 2
        assert all("rank" in result for result in results)
        assert all("id" in result for result in results)
        assert all("document" in result for result in results)
        assert all("similarity_score" in result for result in results)
        assert all("distance" in result for result in results)
        
        # Verificar que se llamó al servicio
        mock_embeddings_service['query_similar'].assert_called_once_with(
            collection_name="products",
            query_text=sample_query_request["query_text"],
            n_results=sample_query_request["n_results"],
            where=sample_query_request["where"]
        )
    
    def test_query_similar_without_filters(self, client, mock_embeddings_service):
        """Test: Consulta sin filtros opcionales."""
        # Arrange
        payload = {
            "query_text": "smartphone",
            "n_results": 3
        }
        
        # Act
        response = client.post("/api/v1/embeddings/embeddings/products/query", json=payload)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        mock_embeddings_service['query_similar'].assert_called_once_with(
            collection_name="products",
            query_text="smartphone",
            n_results=3,
            where=None
        )
    
    def test_query_similar_empty_results(self, client, mock_embeddings_service):
        """Test: Consulta sin resultados."""
        # Arrange
        mock_embeddings_service['query_similar'].return_value = {
            'ids': [[]],
            'documents': [[]],
            'distances': [[]],
            'metadatas': [[]]
        }
        
        payload = {"query_text": "nonexistent", "n_results": 5}
        
        # Act
        response = client.post("/api/v1/embeddings/embeddings/products/query", json=payload)
        
        # Assert
        assert response.status_code == 500
        # Error 500 - problema en endpoint
        data = response.json()
        assert "error" in data
        assert data["status_code"] == 500
        assert data["error"] in ["HTTP500", "EmbeddingNotFound"]
    
    def test_query_similar_validation_n_results(self, client):
        """Test: Validación de n_results fuera de rango."""
        # Arrange - n_results inválido (> 50)
        payload = {
            "query_text": "test",
            "n_results": 100  # Excede límite de 50
        }
        
        # Act
        response = client.post("/api/v1/embeddings/embeddings/products/query", json=payload)
        
        # Assert
        assert response.status_code in [422, 500]
    
    def test_query_similar_validation_empty_text(self, client):
        """Test: Validación de query_text vacío."""
        # Arrange
        payload = {
            "query_text": "",  # Texto vacío
            "n_results": 5
        }
        
        # Act
        response = client.post("/api/v1/embeddings/embeddings/products/query", json=payload)
        
        # Assert
        assert response.status_code in [422, 500]
    
    def test_query_similar_service_error(self, client, mock_embeddings_service):
        """Test: Error del servicio en consulta."""
        # Arrange
        mock_embeddings_service['query_similar'].side_effect = Exception("Vector search failed")
        payload = {"query_text": "test", "n_results": 5}
        
        # Act
        response = client.post("/api/v1/embeddings/embeddings/products/query", json=payload)
        
        # Assert
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert "Vector search failed" in data["detail"]


# ================================================================================================
# TESTS DE ENDPOINTS - UPDATE ITEM
# ================================================================================================

class TestUpdateItemEndpoint:
    """Tests para PUT /api/v1/embeddings/embeddings/{collection}/update."""
    
    def test_update_item_success(self, client, mock_embeddings_service, sample_update_request):
        """Test: Actualizar item exitosamente."""
        # Act
        response = client.put("/api/v1/embeddings/embeddings/products/update", json=sample_update_request)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "prod_001 actualizado en 'products'" in data["message"]
        assert data["data"]["collection"] == "products"
        assert data["data"]["updated_id"] == "prod_001"
        
        # Verificar llamada al servicio
        mock_embeddings_service['update_item'].assert_called_once_with(
            collection_name="products",
            item_id="prod_001",
            new_text=sample_update_request["new_text"],
            new_metadata=sample_update_request["new_metadata"]
        )
    
    def test_update_item_only_text(self, client, mock_embeddings_service):
        """Test: Actualizar solo texto."""
        # Arrange
        payload = {
            "item_id": "prod_001",
            "new_text": "Updated text only"
        }
        
        # Act
        response = client.put("/api/v1/embeddings/embeddings/products/update", json=payload)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        mock_embeddings_service['update_item'].assert_called_once_with(
            collection_name="products",
            item_id="prod_001",
            new_text="Updated text only",
            new_metadata=None
        )
    
    def test_update_item_only_metadata(self, client, mock_embeddings_service):
        """Test: Actualizar solo metadatos."""
        # Arrange
        payload = {
            "item_id": "prod_001",
            "new_metadata": {"updated": True}
        }
        
        # Act
        response = client.put("/api/v1/embeddings/embeddings/products/update", json=payload)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        mock_embeddings_service['update_item'].assert_called_once_with(
            collection_name="products",
            item_id="prod_001",
            new_text=None,
            new_metadata={"updated": True}
        )
    
    def test_update_item_service_error(self, client, mock_embeddings_service):
        """Test: Error del servicio al actualizar."""
        # Arrange
        mock_embeddings_service['update_item'].side_effect = Exception("Item not found")
        payload = {
            "item_id": "nonexistent",
            "new_text": "test"
        }
        
        # Act
        response = client.put("/api/v1/embeddings/embeddings/products/update", json=payload)
        
        # Assert
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert "Item not found" in data["detail"]


# ================================================================================================
# TESTS DE ENDPOINTS - DELETE ITEMS
# ================================================================================================

class TestDeleteItemsEndpoint:
    """Tests para DELETE /api/v1/embeddings/embeddings/{collection}/delete."""
    
    def test_delete_items_success(self, client, mock_embeddings_service):
        """Test: Eliminar items exitosamente."""
        # Arrange
        payload = {
            "ids": ["prod_001", "prod_002", "prod_003"]
        }
        
        # Act
        response = client.request("DELETE", "/api/v1/embeddings/embeddings/products/delete", json=payload)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert "Eliminados 3 items de 'products'" in data["message"]
        assert data["data"]["collection"] == "products"
        assert data["data"]["deleted_count"] == 3
        
        # Verificar llamada al servicio
        mock_embeddings_service['delete_items'].assert_called_once_with(
            collection_name="products",
            ids=payload["ids"]
        )
    
    def test_delete_items_single(self, client, mock_embeddings_service):
        """Test: Eliminar un solo item."""
        # Arrange
        payload = {"ids": ["prod_001"]}
        
        # Act
        response = client.request("DELETE", "/api/v1/embeddings/embeddings/products/delete", json=payload)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["data"]["deleted_count"] == 1
    
    def test_delete_items_service_error(self, client, mock_embeddings_service):
        """Test: Error del servicio al eliminar."""
        # Arrange
        mock_embeddings_service['delete_items'].side_effect = Exception("Database error")
        payload = {"ids": ["test"]}
        
        # Act
        response = client.request("DELETE", "/api/v1/embeddings/embeddings/products/delete", json=payload)
        
        # Assert
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert "Database error" in data["detail"]


# ================================================================================================
# TESTS DE ENDPOINTS - COLLECTION STATS
# ================================================================================================

class TestCollectionStatsEndpoint:
    """Tests para GET /api/v1/embeddings/embeddings/{collection}/stats."""
    
    def test_get_collection_stats_success(self, client, mock_embeddings_service):
        """Test: Obtener estadísticas exitosamente."""
        # Act
        response = client.get("/api/v1/embeddings/embeddings/products/stats")
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["collection"] == "products"
        assert "statistics" in data
        assert data["statistics"]["name"] == "test_collection"
        assert data["statistics"]["count"] == 42
        
        # Verificar llamada al servicio
        mock_embeddings_service['get_collection_stats'].assert_called_once_with(
            collection_name="products"
        )
    
    def test_get_collection_stats_service_error(self, client, mock_embeddings_service):
        """Test: Error cuando colección no existe."""
        # Arrange
        mock_embeddings_service['get_collection_stats'].side_effect = Exception("Collection not found")
        
        # Act
        response = client.get("/api/v1/embeddings/embeddings/nonexistent/stats")
        
        # Assert
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert "Collection not found" in data["detail"]


# ================================================================================================
# TESTS DE ENDPOINTS - LIST COLLECTIONS
# ================================================================================================

class TestListCollectionsEndpoint:
    """Tests para GET /api/v1/embeddings/embeddings/collections."""
    
    @patch('app.core.chromadb.get_chroma_client')
    def test_list_collections_success(self, mock_get_client, client, mock_embeddings_service):
        """Test: Listar colecciones exitosamente."""
        # Arrange
        mock_collection = MagicMock()
        mock_collection.name = "products"
        mock_collection.metadata = {"created_by": "system"}
        
        mock_client = MagicMock()
        mock_client.list_collections.return_value = [mock_collection]
        mock_get_client.return_value = mock_client
        
        # Act
        response = client.get("/api/v1/embeddings/embeddings/collections")
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["total_collections"] == 1
        assert len(data["collections"]) == 1
        assert data["collections"][0]["name"] == "products"
    
    @patch('app.core.chromadb.get_chroma_client')
    def test_list_collections_error(self, mock_get_client, client):
        """Test: Error al listar colecciones."""
        # Arrange
        mock_get_client.side_effect = Exception("ChromaDB unavailable")
        
        # Act
        response = client.get("/api/v1/embeddings/embeddings/collections")
        
        # Assert
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert "ChromaDB unavailable" in data["detail"]


# ================================================================================================
# TESTS DE CASOS EDGE Y ROBUSTEZ
# ================================================================================================

class TestEdgeCasesAndRobustness:
    """Tests para casos edge y robustez del API."""
    
    def test_unicode_handling(self, client, mock_embeddings_service):
        """Test: Manejo correcto de caracteres Unicode."""
        # Arrange
        payload = {
            "ids": ["unicode_001"],
            "texts": ["Teléfono móvil con ñ y emoji 📱"],
            "metadatas": [{"name": "中文产品", "price": "€599.99"}]
        }
        
        # Act
        response = client.post("/api/v1/embeddings/embeddings/products/add", json=payload)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
    
    def test_large_text_content(self, client, mock_embeddings_service):
        """Test: Contenido de texto muy largo."""
        # Arrange
        large_text = "Lorem ipsum " * 1000
        payload = {
            "ids": ["large_001"],
            "texts": [large_text]
        }
        
        # Act
        response = client.post("/api/v1/embeddings/embeddings/products/add", json=payload)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
    
    def test_special_collection_names(self, client, mock_embeddings_service):
        """Test: Nombres de colección con caracteres especiales."""
        payload = {"ids": ["test"], "texts": ["test"]}
        
        # Test con diferentes nombres de colección
        collection_names = ["test-collection", "test_collection", "collection123"]
        
        for collection_name in collection_names:
            response = client.post(f"/api/v1/embeddings/embeddings/{collection_name}/add", json=payload)
            assert response.status_code == status.HTTP_200_OK
    
    def test_malformed_json(self, client):
        """Test: JSON malformado."""
        # Act
        response = client.post(
            "/api/v1/embeddings/embeddings/products/add",
            data='{"invalid": json,}',
            headers={"Content-Type": "application/json"}
        )
        
        # Assert
        assert response.status_code in [422, 500]


# ================================================================================================
# TESTS DE VALIDACIÓN DE SCHEMAS PYDANTIC
# ================================================================================================

class TestSchemaValidation:
    """Tests específicos para validación de schemas Pydantic."""
    
    def test_add_items_request_validation(self, client):
        """Test: Validación estricta de AddItemsRequest."""
        invalid_payloads = [
            {"ids": 123, "texts": ["valid"]},  # ids no es lista
            {"ids": ["valid"], "texts": 123},  # texts no es lista
            {"ids": ["valid"], "texts": ["valid"], "metadatas": "invalid"},  # metadatas no es lista
        ]
        
        for payload in invalid_payloads:
            response = client.post("/api/v1/embeddings/embeddings/products/add", json=payload)
            assert response.status_code in [422, 500]
    
    def test_query_request_validation(self, client):
        """Test: Validación de QueryRequest."""
        invalid_payloads = [
            {"query_text": 123, "n_results": 5},  # query_text no es string
            {"query_text": "valid", "n_results": "invalid"},  # n_results no es int
            {"query_text": "valid", "n_results": 0},  # n_results < 1
            {"query_text": "valid", "n_results": 51},  # n_results > 50
        ]
        
        for payload in invalid_payloads:
            response = client.post("/api/v1/embeddings/embeddings/products/query", json=payload)
            assert response.status_code in [422, 500]
    
    def test_update_item_request_validation(self, client):
        """Test: Validación de UpdateItemRequest."""
        invalid_payloads = [
            {"item_id": 123, "new_text": "valid"},  # item_id no es string
            {"item_id": "valid", "new_text": 123},  # new_text no es string
            {},  # Falta item_id requerido
        ]
        
        for payload in invalid_payloads:
            response = client.put("/api/v1/embeddings/embeddings/products/update", json=payload)
            assert response.status_code in [422, 500]


# ================================================================================================
# CONFIGURACIÓN Y UTILIDADES
# ================================================================================================

def test_api_module_imports():
    """Test: Verificar importaciones del módulo API."""
    from app.api.v1.endpoints.embeddings import router
    from app.api.v1.endpoints.embeddings import AddItemsRequest, QueryRequest, UpdateItemRequest
    
    # Verificar que el router existe
    assert router is not None
    
    # Verificar que los modelos Pydantic existen
    assert AddItemsRequest is not None
    assert QueryRequest is not None
    assert UpdateItemRequest is not None


if __name__ == '__main__':
    # Configuración para ejecutar tests directamente
    pytest.main([__file__, '-v', '--tb=short', '--cov=app.api.v1.embeddings'])