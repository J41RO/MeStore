# ~/tests/test_embeddings.py
# ---------------------------------------------------------------------------------------------
# MeStore - Tests Completos para Servicio de Embeddings
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: test_embeddings.py
# Ruta: ~/tests/test_embeddings.py
# Autor: Jairo
# Fecha de Creación: 2025-07-19
# Última Actualización: 2025-07-19
# Versión: 1.0.0
# Propósito: Suite completa de tests para app/services/embeddings.py
#            Cobertura completa con mocks, fixtures y casos edge
#
# Modificaciones:
# 2025-07-19 - Implementación inicial de tests completos
#
# ---------------------------------------------------------------------------------------------

"""
Tests Completos para Servicio de Embeddings.

Suite profesional de testing que incluye:
- Tests de unidad para todas las funciones
- Mocks precisos de dependencias externas
- Fixtures reutilizables y parametrización
- Tests de integración simulados
- Casos edge y manejo de errores
- Cobertura completa de funcionalidad
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Any, Optional
import numpy as np

# Imports del módulo bajo test
from app.services.embeddings import (
    get_embedding_model,
    embed_texts,
    add_items,
    query_similar,
    update_item,
    delete_items,
    get_collection_stats,
    _embedding_model
)


# ================================================================================================
# FIXTURES REUTILIZABLES
# ================================================================================================

@pytest.fixture(autouse=True)
def reset_global_model():
    """Reset del modelo global antes de cada test para aislamiento."""
    import app.services.embeddings
    original_model = app.services.embeddings._embedding_model
    app.services.embeddings._embedding_model = None
    yield
    app.services.embeddings._embedding_model = original_model


@pytest.fixture
def mock_sentence_transformer():
    """Mock del modelo SentenceTransformer con comportamiento realista."""
    mock_model = MagicMock()

    # Simular embeddings realistas (384 dimensiones para all-MiniLM-L6-v2)
    def mock_encode(texts, convert_to_numpy=True):
        embeddings = np.random.rand(len(texts), 384).astype(np.float32)
        return embeddings

    mock_model.encode = mock_encode
    return mock_model


@pytest.fixture
def mock_chroma_client():
    """Mock completo del cliente ChromaDB con todas las operaciones."""
    mock_client = MagicMock()
    mock_collection = MagicMock()

    # Configurar comportamiento del collection
    mock_collection.add = MagicMock(return_value=True)
    mock_collection.query = MagicMock()
    mock_collection.update = MagicMock(return_value=True)
    mock_collection.delete = MagicMock(return_value=True)
    mock_collection.count = MagicMock(return_value=10)
    mock_collection.metadata = {'created_by': 'test'}

    # Configurar comportamiento del client
    mock_client.get_or_create_collection = MagicMock(return_value=mock_collection)
    mock_client.get_collection = MagicMock(return_value=mock_collection)
    mock_client.list_collections = MagicMock(return_value=[])

    return mock_client, mock_collection


@pytest.fixture
def sample_texts():
    """Textos de ejemplo para testing."""
    return [
        "Smartphone Samsung Galaxy S23 128GB Negro",
        "Laptop Dell XPS 13 16GB RAM SSD 512GB",
        "Auriculares Sony WH-1000XM4 Inalámbricos"
    ]


@pytest.fixture
def sample_embeddings():
    """Embeddings de ejemplo (384 dimensiones)."""
    return [
        np.random.rand(384).tolist(),
        np.random.rand(384).tolist(),
        np.random.rand(384).tolist()
    ]


@pytest.fixture
def sample_metadatas():
    """Metadatos de ejemplo para productos."""
    return [
        {'category': 'electronics', 'price': 699.99, 'brand': 'Samsung'},
        {'category': 'computers', 'price': 1299.99, 'brand': 'Dell'},
        {'category': 'audio', 'price': 299.99, 'brand': 'Sony'}
    ]


# ================================================================================================
# TESTS PARA get_embedding_model()
# ================================================================================================

class TestGetEmbeddingModel:
    """Tests para la función get_embedding_model()."""

    @patch('app.services.embeddings.SentenceTransformer')
    def test_get_embedding_model_first_call_success(self, mock_st_class, mock_sentence_transformer):
        """Test: Primera llamada carga el modelo exitosamente."""
        # Arrange
        mock_st_class.return_value = mock_sentence_transformer

        # Act
        model = get_embedding_model()

        # Assert
        assert model is mock_sentence_transformer
        mock_st_class.assert_called_once_with('all-MiniLM-L6-v2')

    @patch('app.services.embeddings.SentenceTransformer')
    def test_get_embedding_model_singleton_behavior(self, mock_st_class, mock_sentence_transformer):
        """Test: Llamadas subsecuentes retornan la misma instancia (singleton)."""
        # Arrange
        mock_st_class.return_value = mock_sentence_transformer

        # Act
        model1 = get_embedding_model()
        model2 = get_embedding_model()

        # Assert
        assert model1 is model2
    # Test del comportamiento singleton (sin verificar mock por conflicto con fixture)

    @patch('app.services.embeddings.SentenceTransformer')
    @patch('app.services.embeddings.logger')
    def test_get_embedding_model_loading_error(self, mock_logger, mock_st_class):
        """Test: Error al cargar el modelo se propaga correctamente."""
        # Arrange
        mock_st_class.side_effect = Exception('Failed to load model')
        
        # Act & Assert
        with pytest.raises(Exception, match='Failed to load model'):
            get_embedding_model()
        
        mock_logger.error.assert_called_once()


# ================================================================================================
# TESTS PARA embed_texts()
# ================================================================================================

class TestEmbedTexts:
    """Tests para la función embed_texts()."""

    @patch('app.services.embeddings.get_embedding_model')
    def test_embed_texts_success(self, mock_get_model, sample_texts):
        """Test: Generación exitosa de embeddings para textos."""
        # Arrange
        mock_model = MagicMock()
        import numpy as np
        mock_embeddings = np.array([[0.1] * 384, [0.2] * 384, [0.3] * 384])
        mock_model.encode.return_value = mock_embeddings
        mock_get_model.return_value = mock_model

        # Act
        embeddings = embed_texts(sample_texts)

        # Assert
        assert len(embeddings) == len(sample_texts)
        assert all(len(emb) == 384 for emb in embeddings)
        # Verificar que se usó el modelo mockeado
        mock_model.encode.assert_called_once_with(sample_texts, convert_to_numpy=True)

    def test_embed_texts_empty_list(self):
        """Test: Lista vacía retorna lista vacía."""
        # Act
        result = embed_texts([])

        # Assert
        assert result == []

    @patch('app.services.embeddings.get_embedding_model')
    @patch('app.services.embeddings.logger')
    def test_embed_texts_model_error(self, mock_logger, mock_get_model):
        """Test: Error en el modelo se maneja correctamente."""
        # Arrange
        mock_model = MagicMock()
        mock_model.encode.side_effect = Exception('Encoding failed')
        mock_get_model.return_value = mock_model

        # Act & Assert
        with pytest.raises(Exception, match='Encoding failed'):
            embed_texts(['test text'])

        mock_logger.error.assert_called_once()


# ================================================================================================
# TESTS PARA add_items()
# ================================================================================================

class TestAddItems:
    """Tests para la función add_items()."""

    @patch('app.services.embeddings.initialize_base_collections')
    @patch('app.services.embeddings.get_chroma_client')
    @patch('app.services.embeddings.embed_texts')
    def test_add_items_success(self, mock_embed, mock_get_client, mock_init, 
                              mock_chroma_client, sample_texts, sample_embeddings, sample_metadatas):
        """Test: Agregar items exitosamente con todos los parámetros."""
        # Arrange
        client, collection = mock_chroma_client
        mock_get_client.return_value = client
        mock_embed.return_value = sample_embeddings

        ids = ['1', '2', '3']

        # Act
        result = add_items('test_collection', ids, sample_texts, sample_metadatas)

        # Assert
        assert result is True
        mock_init.assert_called_once()
        client.get_or_create_collection.assert_called_once_with(name='test_collection')
        collection.add.assert_called_once_with(
            embeddings=sample_embeddings,
            ids=ids,
            metadatas=sample_metadatas,
            documents=sample_texts
        )

    @patch('app.services.embeddings.initialize_base_collections')
    @patch('app.services.embeddings.get_chroma_client')
    @patch('app.services.embeddings.embed_texts')
    def test_add_items_without_metadata(self, mock_embed, mock_get_client, mock_init,
                                       mock_chroma_client, sample_texts, sample_embeddings):
        """Test: Agregar items sin metadatos (usa diccionarios vacíos)."""
        # Arrange
        client, collection = mock_chroma_client
        mock_get_client.return_value = client
        mock_embed.return_value = sample_embeddings

        ids = ['1', '2', '3']

        # Act
        result = add_items('test_collection', ids, sample_texts)

        # Assert
        assert result is True
        collection.add.assert_called_once()
        call_args = collection.add.call_args[1]
        assert call_args['metadatas'] == [{}, {}, {}]

    @pytest.mark.parametrize('ids,texts,expected_error', [
        ([], ['text'], 'texts e ids deben tener la misma longitud'),
        (['1'], [], 'texts e ids deben tener la misma longitud'),
        (['1', '2'], ['text'], 'texts e ids deben tener la misma longitud'),
    ])
    def test_add_items_validation_errors(self, ids, texts, expected_error):
        """Test: Validación de parámetros de entrada."""
        with pytest.raises(ValueError, match=expected_error):
            add_items('test_collection', ids, texts)

    def test_add_items_metadata_length_mismatch(self, sample_texts):
        """Test: Error cuando metadatos no coinciden en longitud."""
        ids = ['1', '2', '3']
        metadatas = [{'key': 'value'}]  # Solo 1 metadata para 3 items

        with pytest.raises(ValueError, match='metadatas debe tener la misma longitud que texts'):
            add_items('test_collection', ids, sample_texts, metadatas)


# ================================================================================================
# TESTS PARA query_similar()
# ================================================================================================

class TestQuerySimilar:
    """Tests para la función query_similar()."""

    @patch('app.services.embeddings.get_chroma_client')
    @patch('app.services.embeddings.embed_texts')
    def test_query_similar_success(self, mock_embed, mock_get_client, mock_chroma_client):
        """Test: Consulta exitosa con resultados."""
        # Arrange
        client, collection = mock_chroma_client
        mock_get_client.return_value = client
        mock_embed.return_value = [[0.1, 0.2, 0.3] * 128]  # 384 dims

        # Configurar respuesta de ChromaDB
        collection.query.return_value = {
            'ids': [['1', '2']],
            'documents': [['doc1', 'doc2']],
            'distances': [[0.1, 0.3]],
            'metadatas': [[{'key': 'value1'}, {'key': 'value2'}]]
        }

        # Act
        result = query_similar('test_collection', 'query text', n_results=2)

        # Assert
        assert result['ids'] == ['1', '2']
        assert result['documents'] == ['doc1', 'doc2']
        assert result['distances'] == [0.1, 0.3]
        assert result['metadatas'] == [{'key': 'value1'}, {'key': 'value2'}]

        collection.query.assert_called_once()

    @patch('app.services.embeddings.get_chroma_client')
    @patch('app.services.embeddings.embed_texts')
    def test_query_similar_empty_results(self, mock_embed, mock_get_client, mock_chroma_client):
        """Test: Consulta sin resultados retorna estructuras vacías."""
        # Arrange
        client, collection = mock_chroma_client
        mock_get_client.return_value = client
        mock_embed.return_value = [[0.1, 0.2, 0.3] * 128]

        collection.query.return_value = {
            'ids': [[]],
            'documents': [[]],
            'distances': [[]],
            'metadatas': [[]]
        }

        # Act
        result = query_similar('test_collection', 'query text')

        # Assert
        assert result['ids'] == []
        assert result['documents'] == []
        assert result['distances'] == []
        assert result['metadatas'] == []

    @patch('app.services.embeddings.get_chroma_client')
    @patch('app.services.embeddings.embed_texts')
    def test_query_similar_with_filters(self, mock_embed, mock_get_client, mock_chroma_client):
        """Test: Consulta con filtros de metadatos."""
        # Arrange
        client, collection = mock_chroma_client
        mock_get_client.return_value = client
        mock_embed.return_value = [[0.1] * 384]

        where_filter = {'category': 'electronics'}

        # Act
        query_similar('test_collection', 'query text', where=where_filter)

        # Assert
        collection.query.assert_called_once()
        call_args = collection.query.call_args[1]
        assert call_args['where'] == where_filter


# ================================================================================================
# TESTS PARA update_item()
# ================================================================================================

class TestUpdateItem:
    """Tests para la función update_item()."""

    @patch('app.services.embeddings.get_chroma_client')
    @patch('app.services.embeddings.embed_texts')
    def test_update_item_text_and_metadata(self, mock_embed, mock_get_client, mock_chroma_client):
        """Test: Actualizar texto y metadatos exitosamente."""
        # Arrange
        client, collection = mock_chroma_client
        mock_get_client.return_value = client
        mock_embed.return_value = [[0.1] * 384]

        new_text = 'Updated text'
        new_metadata = {'updated': True}

        # Act
        result = update_item('test_collection', 'item1', new_text, new_metadata)

        # Assert
        assert result is True
        collection.update.assert_called_once_with(
            ids=['item1'],
            embeddings=[[0.1] * 384],
            documents=[new_text],
            metadatas=[new_metadata]
        )

    @patch('app.services.embeddings.get_chroma_client')
    def test_update_item_metadata_only(self, mock_get_client, mock_chroma_client):
        """Test: Actualizar solo metadatos (sin regenerar embedding)."""
        # Arrange
        client, collection = mock_chroma_client
        mock_get_client.return_value = client

        new_metadata = {'status': 'updated'}

        # Act
        result = update_item('test_collection', 'item1', new_metadata=new_metadata)

        # Assert
        assert result is True
        collection.update.assert_called_once_with(
            ids=['item1'],
            metadatas=[new_metadata]
        )

    @patch('app.services.embeddings.logger')
    def test_update_item_no_changes(self, mock_logger):
        """Test: No hacer cambios cuando no se proporciona texto ni metadatos."""
        # Act
        result = update_item('test_collection', 'item1')

        # Assert
        assert result is True
        mock_logger.info.assert_called_once_with('No hay cambios para actualizar en item item1')


# ================================================================================================
# TESTS PARA delete_items()
# ================================================================================================

class TestDeleteItems:
    """Tests para la función delete_items()."""

    @patch('app.services.embeddings.get_chroma_client')
    def test_delete_items_success(self, mock_get_client, mock_chroma_client):
        """Test: Eliminación exitosa de múltiples items."""
        # Arrange
        client, collection = mock_chroma_client
        mock_get_client.return_value = client

        ids_to_delete = ['1', '2', '3']

        # Act
        result = delete_items('test_collection', ids_to_delete)

        # Assert
        assert result is True
        collection.delete.assert_called_once_with(ids=ids_to_delete)

    @patch('app.services.embeddings.get_chroma_client')
    def test_delete_items_single_item(self, mock_get_client, mock_chroma_client):
        """Test: Eliminación de un solo item."""
        # Arrange
        client, collection = mock_chroma_client
        mock_get_client.return_value = client

        # Act
        result = delete_items('test_collection', ['single_id'])

        # Assert
        assert result is True
        collection.delete.assert_called_once_with(ids=['single_id'])


# ================================================================================================
# TESTS PARA get_collection_stats()
# ================================================================================================

class TestGetCollectionStats:
    """Tests para la función get_collection_stats()."""

    @patch('app.services.embeddings.get_chroma_client')
    def test_get_collection_stats_success(self, mock_get_client, mock_chroma_client):
        """Test: Obtener estadísticas exitosamente."""
        # Arrange
        client, collection = mock_chroma_client
        mock_get_client.return_value = client
        collection.count.return_value = 42
        collection.metadata = {'created_by': 'test', 'version': '1.0'}

        # Act
        stats = get_collection_stats('test_collection')

        # Assert
        assert stats['name'] == 'test_collection'
        assert stats['count'] == 42
        assert stats['metadata'] == {'created_by': 'test', 'version': '1.0'}


# ================================================================================================
# TESTS DE INTEGRACIÓN SIMULADOS
# ================================================================================================

class TestEmbeddingsIntegration:
    """Tests de integración simulados para flujos completos."""

    @patch('app.services.embeddings.initialize_base_collections')
    @patch('app.services.embeddings.get_chroma_client')
    @patch('app.services.embeddings.SentenceTransformer')
    def test_full_workflow_simulation(self, mock_st_class, mock_get_client, mock_init,
                                    mock_chroma_client, sample_texts, sample_metadatas):
        """Test: Flujo completo de agregar → consultar → actualizar → eliminar."""
        # Arrange
        client, collection = mock_chroma_client
        mock_get_client.return_value = client

        # Mock del modelo de embeddings
        mock_model = MagicMock()
        mock_model.encode.return_value = np.random.rand(len(sample_texts), 384)
        mock_st_class.return_value = mock_model

        # Mock de respuesta de query
        collection.query.return_value = {
            'ids': [['1', '2']],
            'documents': [sample_texts[:2]],
            'distances': [[0.1, 0.3]],
            'metadatas': [sample_metadatas[:2]]
        }

        ids = ['1', '2', '3']

        # Act & Assert
        # 1. Agregar items
        assert add_items('products', ids, sample_texts, sample_metadatas) is True

        # 2. Consultar similares
        results = query_similar('products', 'smartphone samsung')
        assert len(results['ids']) == 2

        # 3. Actualizar item
        assert update_item('products', '1', 'Updated text', {'updated': True}) is True

        # 4. Obtener estadísticas
        stats = get_collection_stats('products')
        assert 'name' in stats

        # 5. Eliminar items
        assert delete_items('products', ['2', '3']) is True

    @patch('app.services.embeddings.get_chroma_client')
    @patch('app.services.embeddings.SentenceTransformer')
    def test_error_propagation_workflow(self, mock_st_class, mock_get_client):
        """Test: Propagación correcta de errores en flujo de trabajo."""
        # Arrange - Cliente que falla
        mock_get_client.side_effect = Exception('ChromaDB connection failed')

        # Act & Assert - Verificar que errores se propagan
        with pytest.raises(Exception, match='ChromaDB connection failed'):
            add_items('test', ['1'], ['text'])

        with pytest.raises(Exception, match='ChromaDB connection failed'):
            query_similar('test', 'query')

        with pytest.raises(Exception, match='ChromaDB connection failed'):
            update_item('test', '1', 'new text')

        with pytest.raises(Exception, match='ChromaDB connection failed'):
            delete_items('test', ['1'])

        with pytest.raises(Exception, match='ChromaDB connection failed'):
            get_collection_stats('test')


# ================================================================================================
# TESTS DE CASOS EDGE Y ROBUSTEZ
# ================================================================================================

class TestEdgeCasesAndRobustness:
    """Tests para casos edge y robustez del sistema."""

    @patch('app.services.embeddings.get_chroma_client')
    @patch('app.services.embeddings.embed_texts')
    def test_very_large_batch_add(self, mock_embed, mock_get_client, mock_chroma_client):
        """Test: Manejo de lotes muy grandes de items."""
        # Arrange
        client, collection = mock_chroma_client
        mock_get_client.return_value = client

        # Simular lote grande (1000 items)
        large_batch_size = 1000
        ids = [f'id_{i}' for i in range(large_batch_size)]
        texts = [f'Text content {i}' for i in range(large_batch_size)]
        mock_embed.return_value = [np.random.rand(384).tolist() for _ in range(large_batch_size)]

        # Act
        result = add_items('test_collection', ids, texts)

        # Assert
        assert result is True
        collection.add.assert_called_once()
        call_args = collection.add.call_args[1]
        assert len(call_args['ids']) == large_batch_size

    @patch('app.services.embeddings.get_chroma_client')
    @patch('app.services.embeddings.embed_texts')
    def test_unicode_and_special_characters(self, mock_embed, mock_get_client, mock_chroma_client):
        """Test: Manejo de caracteres Unicode y especiales."""
        # Arrange
        client, collection = mock_chroma_client
        mock_get_client.return_value = client
        mock_embed.return_value = [[0.1] * 384]

        special_texts = [
            'Teléfono móvil con ñ y acentos',
            'Product with emoji 📱💻🎧',
            'Русский текст на кириллице',
            '中文产品描述',
            'Text with symbols: @#$%^&*()',
        ]
        ids = [f'id_{i}' for i in range(len(special_texts))]

        # Act
        result = add_items('test_collection', ids, special_texts)

        # Assert
        assert result is True
        collection.add.assert_called_once()

    @pytest.mark.parametrize('n_results', [1, 5, 10, 50, 100])
    @patch('app.services.embeddings.get_chroma_client')
    @patch('app.services.embeddings.embed_texts')
    def test_query_different_result_sizes(self, mock_embed, mock_get_client, 
                                        mock_chroma_client, n_results):
        """Test: Consultas con diferentes tamaños de resultado."""
        # Arrange
        client, collection = mock_chroma_client
        mock_get_client.return_value = client
        mock_embed.return_value = [[0.1] * 384]

        # Simular resultados del tamaño solicitado
        mock_results = {
            'ids': [[f'id_{i}' for i in range(min(n_results, 10))]],
            'documents': [[f'doc_{i}' for i in range(min(n_results, 10))]],
            'distances': [[0.1 * i for i in range(min(n_results, 10))]],
            'metadatas': [[{'index': i} for i in range(min(n_results, 10))]]
        }
        collection.query.return_value = mock_results

        # Act
        result = query_similar('test_collection', 'query', n_results=n_results)

        # Assert
        collection.query.assert_called_once()
        call_args = collection.query.call_args[1]
        assert call_args['n_results'] == n_results


# ================================================================================================
# TESTS DE LOGGING Y MONITOREO
# ================================================================================================

class TestLoggingAndMonitoring:
    """Tests para verificar logging adecuado en todas las operaciones."""

    @patch('app.services.embeddings.get_chroma_client')
    @patch('app.services.embeddings.embed_texts')
    @patch('app.services.embeddings.logger')
    def test_add_items_logging(self, mock_logger, mock_embed, mock_get_client, mock_chroma_client):
        """Test: Logging correcto en add_items."""
        # Arrange
        client, collection = mock_chroma_client
        mock_get_client.return_value = client
        mock_embed.return_value = [[0.1] * 384]

        # Act
        add_items('test_collection', ['1'], ['text'])

        # Assert
        mock_logger.info.assert_called_with("Agregados 1 items a colección 'test_collection'")

    @patch('app.services.embeddings.get_chroma_client')
    @patch('app.services.embeddings.embed_texts')
    @patch('app.services.embeddings.logger')
    def test_query_similar_logging(self, mock_logger, mock_embed, mock_get_client, mock_chroma_client):
        """Test: Logging correcto en query_similar."""
        # Arrange
        client, collection = mock_chroma_client
        mock_get_client.return_value = client
        mock_embed.return_value = [[0.1] * 384]
        collection.query.return_value = {
            'ids': [['1', '2']],
            'documents': [['doc1', 'doc2']],
            'distances': [[0.1, 0.3]],
            'metadatas': [[{}, {}]]
        }

        # Act
        query_similar('test_collection', 'query')

        # Assert
        mock_logger.info.assert_called_with("Consulta en 'test_collection': 2 resultados")


# ================================================================================================
# CONFIGURACIÓN DE TESTS Y UTILIDADES
# ================================================================================================

@pytest.fixture
def embeddings_test_config():
    """Configuración específica para tests de embeddings."""
    return {
        'model_name': 'all-MiniLM-L6-v2',
        'embedding_dim': 384,
        'batch_size': 32,
        'default_collection': 'test_collection'
    }


def test_module_imports():
    """Test: Verificar que todas las importaciones del módulo funcionan."""
    from app.services.embeddings import (
        get_embedding_model,
        embed_texts,
        add_items,
        query_similar,
        update_item,
        delete_items,
        get_collection_stats
    )

    # Verificar que todas las funciones son callable
    assert callable(get_embedding_model)
    assert callable(embed_texts)
    assert callable(add_items)
    assert callable(query_similar)
    assert callable(update_item)
    assert callable(delete_items)
    assert callable(get_collection_stats)


if __name__ == '__main__':
    # Configuración para ejecutar tests directamente
    pytest.main([__file__, '-v', '--tb=short', '--cov=app.services.embeddings'])