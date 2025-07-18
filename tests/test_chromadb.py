#!/usr/bin/env python3
# ~/tests/test_chromadb.py
# ---------------------------------------------------------------------------------------------
# MeStore - Tests ChromaDB y Sistema de Embeddings
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# ---------------------------------------------------------------------------------------------

"""
Tests para ChromaDB y sistema de embeddings.

Verifica funcionamiento completo del pipeline de vector search:
- Conexión a ChromaDB
- Generación de embeddings  
- Operaciones CRUD
- Búsqueda semántica
"""

import pytest
from app.services.embeddings import (
    add_items, 
    query_similar, 
    get_collection_stats,
    delete_items,
    update_item
)
from app.core.chromadb import initialize_base_collections

class TestChromaDBSetup:
    """Tests de configuración básica de ChromaDB."""
    
    def test_initialize_base_collections(self):
        """Test inicialización de colecciones base."""
        # Inicializar colecciones
        initialize_base_collections()
        
        # Verificar que se pueden obtener stats (colecciones existen)
        stats = get_collection_stats("products")
        assert "count" in stats
        assert stats["name"] == "products"

class TestEmbeddingsOperations:
    """Tests de operaciones de embeddings."""
    
    @pytest.fixture(autouse=True)
    def setup_test_data(self):
        """Setup datos de prueba para cada test."""
        self.test_products = [
            "Manzana roja fresca de Boyacá",
            "Banana amarilla premium", 
            "Aguacate hass cremoso"
        ]
        
        self.test_ids = ["test_001", "test_002", "test_003"]
        
        self.test_metadatas = [
            {"tipo": "fruta", "origen": "nacional"},
            {"tipo": "fruta", "origen": "importado"},
            {"tipo": "fruta", "origen": "nacional"}
        ]
    
    def test_add_items_success(self):
        """Test agregar items exitosamente."""
        result = add_items(
            "products", 
            self.test_ids, 
            self.test_products, 
            self.test_metadatas
        )
        assert result is True
    
    def test_query_similar_basic(self):
        """Test búsqueda semántica básica."""
        # Primero agregar datos
        add_items("products", self.test_ids, self.test_products, self.test_metadatas)
        
        # Buscar similares
        results = query_similar("products", "fruta roja", n_results=2)
        
        assert "ids" in results
        assert "documents" in results
        assert "distances" in results
        assert len(results["ids"][0]) <= 2

class TestSemanticSearch:
    """Tests específicos de búsqueda semántica."""
    
    def test_semantic_similarity_food(self):
        """Test que búsqueda de comida encuentra productos alimentarios."""
        # Agregar productos de prueba
        semantic_products = ["Manzana roja dulce", "Computador portátil", "Camisa azul"]
        semantic_ids = ["sem_001", "sem_002", "sem_003"]
        
        # Agregar metadatos requeridos por ChromaDB v1.0+
        semantic_metadata = [
            {"categoria": "alimentacion"},
            {"categoria": "tecnologia"}, 
            {"categoria": "ropa"}
        ]

        add_items("products", semantic_ids, semantic_products, semantic_metadata)
        
        results = query_similar("products", "fruta dulce", n_results=3)
        
        # El resultado debería incluir la manzana
        top_result = results["documents"][0][0]
        assert "manzana" in top_result.lower()