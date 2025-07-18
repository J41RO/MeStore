# ~/backend/embedding_model.py
# ---------------------------------------------------------------------------------------------
# MESTOCKER - Módulo de Embedding Model
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: embedding_model.py
# Ruta: ~/backend/embedding_model.py
# Autor: Jairo
# Fecha de Creación: 2025-07-17
# Última Actualización: 2025-07-17
# Versión: 1.0.0
# Propósito: Configurar y gestionar el modelo de embeddings sentence-transformers
#            para vectorización de texto en colecciones ChromaDB
#
# Modificaciones:
# 2025-07-17 - Implementación inicial con caching LRU y singleton pattern
#
# ---------------------------------------------------------------------------------------------

"""
Módulo de Embedding Model para ChromaDB.

Este módulo proporciona una interfaz unificada para generar embeddings de texto
utilizando el modelo sentence-transformers 'all-MiniLM-L6-v2'. Incluye:
- Caching inteligente con LRU para mejorar performance
- Singleton pattern para una sola instancia del modelo
- Validación de dimensiones y manejo robusto de errores
- Documentación completa de uso y troubleshooting
"""

import logging
import time
from functools import lru_cache
from typing import List, Optional

from sentence_transformers import SentenceTransformer

# Configurar logging específico para embedding model
logger = logging.getLogger(__name__)


class EmbeddingModelSingleton:
    """
    Singleton para gestionar una única instancia del modelo de embeddings.

    Este patrón asegura que el modelo se cargue solo una vez en memoria,
    optimizando recursos y tiempo de respuesta en aplicaciones con múltiples
    requests que requieren embeddings.
    """

    _instance: Optional["EmbeddingModelSingleton"] = None
    _model: Optional[SentenceTransformer] = None
    _model_name: str = "all-MiniLM-L6-v2"
    _expected_dimensions: int = 384

    def __new__(cls) -> "EmbeddingModelSingleton":
        """Implementación del patrón Singleton."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            logger.info("🔧 Inicializando EmbeddingModelSingleton por primera vez")
        return cls._instance

    def __init__(self) -> None:
        """Inicializar el modelo solo si no está ya cargado."""
        if self._model is None:
            self._load_model()

    def _load_model(self) -> None:
        """
        Cargar el modelo sentence-transformers con logging detallado.

        El modelo se descarga automáticamente la primera vez y se mantiene
        en cache local para usos posteriores.
        """
        logger.info(f"📦 Cargando modelo: {self._model_name}")
        logger.info("⏳ Primera carga puede tardar ~30s descargando modelo (80MB)")

        start_time = time.time()

        try:
            self._model = SentenceTransformer(self._model_name)
            load_time = time.time() - start_time

            logger.info(f"✅ Modelo cargado exitosamente en {load_time:.2f}s")
            logger.info(f"📊 Dimensiones esperadas: {self._expected_dimensions}")

            # Verificar dimensiones con texto de prueba
            test_vector = self._model.encode("test")
            actual_dimensions = len(test_vector)

            if actual_dimensions == self._expected_dimensions:
                logger.info(f"✅ Dimensiones verificadas: {actual_dimensions}D")
            else:
                logger.warning(
                    f"⚠️ Dimensiones inesperadas: {actual_dimensions}D "
                    f"(esperadas: {self._expected_dimensions}D)"
                )
                self._expected_dimensions = actual_dimensions

        except Exception as e:
            logger.error(f"❌ Error cargando modelo: {e}")
            raise RuntimeError(f"No se pudo cargar el modelo {self._model_name}: {e}")

    def get_model(self) -> SentenceTransformer:
        """
        Obtener la instancia del modelo sentence-transformers.

        Returns:
            SentenceTransformer: Instancia del modelo cargado

        Raises:
            RuntimeError: Si el modelo no se pudo cargar
        """
        if self._model is None:
            raise RuntimeError("Modelo no inicializado correctamente")
        return self._model

    def get_expected_dimensions(self) -> int:
        """Obtener las dimensiones esperadas del vector de embedding."""
        return self._expected_dimensions


# Instancia global del singleton
_embedding_singleton = EmbeddingModelSingleton()


@lru_cache(maxsize=1000)
def get_embedding(text: str) -> List[float]:
    """
    Generar embedding vectorial para un texto dado.

    Esta función utiliza caching LRU para evitar recálculos innecesarios
    del mismo texto, mejorando significativamente el performance en
    aplicaciones con queries repetitivas.

    Args:
        text (str): Texto a vectorizar. Se recomienda texto limpio sin
                   caracteres especiales excesivos.

    Returns:
        List[float]: Vector de embeddings de 384 dimensiones.
                    Cada elemento es un float entre -1.0 y 1.0.

    Raises:
        ValueError: Si el texto está vacío o es None
        RuntimeError: Si hay problemas con el modelo de embeddings

    Example:
        >>> vector = get_embedding("Producto excelente para cocina")
        >>> len(vector)
        384
        >>> type(vector[0])
        <class 'float'>

    Note:
        - Tiempo típico: <100ms para textos cortos (<100 palabras)
        - Cache LRU mantiene 1000 embeddings más recientes
        - Textos idénticos retornan vectores idénticos (determinístico)
    """

    # Validación de entrada
    if not text or not isinstance(text, str):
        raise ValueError("El texto debe ser una cadena no vacía")

    if len(text.strip()) == 0:
        raise ValueError("El texto no puede estar vacío o solo espacios")

    try:
        # Obtener modelo desde singleton
        model = _embedding_singleton.get_model()

        # Generar embedding
        logger.debug(f"🔄 Generando embedding para texto: {text[:50]}...")
        start_time = time.time()

        # encode() retorna numpy array, convertir a lista de floats
        embedding_array = model.encode(text)
        embedding_list = embedding_array.tolist()

        generation_time = time.time() - start_time
        logger.debug(f"✅ Embedding generado en {generation_time:.3f}s")

        # Validación de salida
        expected_dims = _embedding_singleton.get_expected_dimensions()
        if len(embedding_list) != expected_dims:
            raise RuntimeError(
                f"Dimensiones incorrectas: {len(embedding_list)} "
                f"(esperadas: {expected_dims})"
            )

        return embedding_list

    except Exception as e:
        logger.error(f"❌ Error generando embedding: {e}")
        raise RuntimeError(f"No se pudo generar embedding: {e}")


def get_embedding_info() -> dict:
    """
    Obtener información técnica del modelo de embeddings.

    Returns:
        dict: Información del modelo incluyendo nombre, dimensiones,
              cache stats y estado de inicialización.

    Example:
        >>> info = get_embedding_info()
        >>> print(info['model_name'])
        'all-MiniLM-L6-v2'
    """

    cache_info = get_embedding.cache_info()

    return {
        "model_name": _embedding_singleton._model_name,
        "dimensions": _embedding_singleton.get_expected_dimensions(),
        "model_loaded": _embedding_singleton._model is not None,
        "cache_size": cache_info.currsize,
        "cache_maxsize": cache_info.maxsize,
        "cache_hits": cache_info.hits,
        "cache_misses": cache_info.misses,
        "cache_hit_rate": (
            cache_info.hits / (cache_info.hits + cache_info.misses)
            if (cache_info.hits + cache_info.misses) > 0
            else 0.0
        ),
    }


def clear_embedding_cache() -> None:
    """
    Limpiar el cache LRU de embeddings.

    Útil para liberar memoria o forzar regeneración de embeddings
    en caso de actualizaciones del modelo.
    """
    get_embedding.cache_clear()
    logger.info("🧹 Cache de embeddings limpiado")


def warm_up_model(sample_texts: Optional[List[str]] = None) -> None:
    """
    Pre-cargar el modelo con textos de ejemplo para optimizar performance.

    Args:
        sample_texts: Lista de textos para warm-up. Si None, usa textos por defecto.
    """

    if sample_texts is None:
        sample_texts = [
            "producto de alta calidad",
            "excelente servicio al cliente",
            "entrega rápida y segura",
            "precio competitivo en el mercado",
        ]

    logger.info(f"🔥 Calentando modelo con {len(sample_texts)} textos de ejemplo")

    start_time = time.time()
    for text in sample_texts:
        get_embedding(text)

    warm_up_time = time.time() - start_time
    logger.info(f"✅ Warm-up completado en {warm_up_time:.2f}s")


if __name__ == "__main__":
    # Código de prueba y demostración
    logging.basicConfig(level=logging.INFO)

    print("🧪 DEMO: Embedding Model v1.0")
    print("=" * 50)

    # Warm-up del modelo
    warm_up_model()

    # Ejemplo de uso básico
    test_text = "Smartphone de última generación con excelente calidad"
    vector = get_embedding(test_text)

    print(f"📝 Texto: {test_text}")
    print(f"📊 Dimensiones: {len(vector)}")
    print(f"📈 Rango: [{min(vector):.3f}, {max(vector):.3f}]")
    print(f"🎯 Primeros 5 valores: {vector[:5]}")

    # Información del modelo
    info = get_embedding_info()
    print(f"📋 Info del modelo:")
    for key, value in info.items():
        print(f"  {key}: {value}")