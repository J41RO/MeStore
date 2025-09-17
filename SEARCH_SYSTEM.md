# Sistema de Búsqueda Avanzada - MeStore

## Resumen Ejecutivo

El sistema de búsqueda avanzada de MeStore combina **PostgreSQL full-text search** con **ChromaDB vector search** para proporcionar una experiencia de búsqueda híbrida que maximiza tanto la precisión como la relevancia semántica.

### Características Principales

- 🔍 **Búsqueda Híbrida**: Combina búsqueda textual tradicional con búsqueda semántica
- ⚡ **Performance Optimizada**: Cache inteligente con Redis y índices GIN optimizados
- 🎯 **Filtros Avanzados**: Por categorías, precio, vendor, stock y más
- 📊 **Analytics Completos**: Métricas de uso, trending queries y business intelligence
- 🔄 **Sincronización Automática**: Embeddings actualizados en tiempo real
- 🌐 **API RESTful**: Endpoints completos para integración frontend

## Arquitectura del Sistema

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend UI   │    │   API Gateway   │    │   Search API    │
│                 │◄──►│                 │◄──►│                 │
│ React/TypeScript│    │    FastAPI      │    │   Endpoints     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                       ┌─────────────────────────────────┼─────────────────────────────────┐
                       │                                 ▼                                 │
                       │                    ┌─────────────────┐                           │
                       │                    │ SearchService   │                           │
                       │                    │   (Híbrido)     │                           │
                       │                    └─────────────────┘                           │
                       │                             │                                     │
           ┌───────────▼──────────┐    ┌─────────────▼─────────────┐    ┌─────────────▼──────────┐
           │   PostgreSQL         │    │      ChromaDB             │    │      Redis Cache       │
           │                      │    │                           │    │                        │
           │ • Full-text Search   │    │ • Vector Embeddings       │    │ • Search Results       │
           │ • GIN Indexes        │    │ • Semantic Similarity     │    │ • Autocomplete         │
           │ • Product Data       │    │ • ML Models (Spanish)     │    │ • Analytics           │
           │ • Categories         │    │ • Similarity Search       │    │ • Trending Queries    │
           └──────────────────────┘    └───────────────────────────┘    └────────────────────────┘
```

## Componentes del Sistema

### 1. SearchService (Servicio Principal)
**Archivo**: `app/services/search_service.py`

Orchestrador principal que combina múltiples estrategias de búsqueda:

- **Text Search**: PostgreSQL con índices GIN para español
- **Semantic Search**: ChromaDB con embeddings multilingües
- **Hybrid Ranking**: Algoritmo que combina relevancia textual y semántica
- **Cache Integration**: Optimización automática con Redis

```python
# Ejemplo de uso
filters = SearchFilters(
    query="laptop gaming",
    price_max=2000,
    categories=["electronics"],
    has_stock=True
)

results = await search_service.search_products(
    session=session,
    filters=filters,
    page=1,
    page_size=20
)
```

### 2. ChromaDB Service
**Archivo**: `app/services/chroma_service.py`

Gestión de embeddings y búsqueda vectorial:

- **Modelo**: `paraphrase-multilingual-mpnet-base-v2` optimizado para español
- **Dimensiones**: 768-dimensional embeddings
- **Collections**: Productos y categorías por separado
- **Batch Processing**: Optimizado para alto volumen

```python
# Agregar productos en batch
await chroma_service.add_products_batch(products_data)

# Búsqueda semántica
results = await chroma_service.search_products(
    query="computadora para juegos",
    max_results=10,
    category_filter="electronics"
)
```

### 3. Cache Service
**Archivo**: `app/services/search_cache_service.py`

Cache inteligente con TTL adaptativo:

- **TTL Dinámico**: Basado en popularidad de queries
- **Cache Warming**: Pre-carga de búsquedas populares
- **Invalidación Granular**: Por productos o categorías específicas
- **Métricas**: Hit/miss rates para optimización

### 4. Sync Service
**Archivo**: `app/services/embedding_sync_service.py`

Sincronización entre PostgreSQL y ChromaDB:

- **Full Sync**: Sincronización completa inicial
- **Incremental Sync**: Solo cambios desde última sync
- **Cleanup**: Eliminación de embeddings huérfanos
- **Monitoring**: Estado y progreso de sincronización

### 5. Analytics Service
**Archivo**: `app/services/search_analytics_service.py`

Business Intelligence y métricas:

- **Search Analytics**: Volumen, tendencias, success rates
- **User Behavior**: Segmentación por tipo de usuario
- **Performance Metrics**: Tiempos de respuesta, percentiles
- **Business Insights**: Oportunidades de conversión

## API Endpoints

### Búsqueda Principal
```http
POST /api/v1/search/search
```

**Request Body**:
```json
{
  "query": "laptop gaming",
  "categories": ["electronics"],
  "price_min": 500,
  "price_max": 2000,
  "has_stock": true,
  "sort_by": "relevance"
}
```

**Response**:
```json
{
  "results": [
    {
      "product": {
        "id": "uuid",
        "name": "Laptop Gaming ASUS ROG",
        "price": 1899.99,
        "category": "Electronics"
      },
      "scores": {
        "final_score": 0.95,
        "text_score": 0.88,
        "semantic_score": 0.92
      }
    }
  ],
  "pagination": {
    "page": 1,
    "total_count": 156,
    "has_next": true
  },
  "search_metadata": {
    "search_time_ms": 245,
    "used_cache": false
  }
}
```

### Autocomplete
```http
GET /api/v1/search/autocomplete?q=lap&limit=10
```

### Productos Similares
```http
GET /api/v1/search/products/{product_id}/similar?limit=5
```

### Analytics y Trending
```http
GET /api/v1/search/trending?limit=20
GET /api/v1/search/analytics?days=7
```

## Índices de Base de Datos

### PostgreSQL GIN Indexes
**Archivo**: `alembic/versions/2025_09_17_1200-add_fulltext_search_indexes.py`

```sql
-- Búsqueda full-text en español
CREATE INDEX ix_product_name_fulltext_gin
ON products USING gin(to_tsvector('spanish', name));

-- Búsqueda por similitud trigram
CREATE INDEX ix_product_name_trgm_gin
ON products USING gin(name gin_trgm_ops);

-- Búsqueda combinada
CREATE INDEX ix_product_combined_fulltext_gin
ON products USING gin(
  (to_tsvector('spanish', name) || to_tsvector('spanish', COALESCE(description, '')))
);
```

## Configuración

### Variables de Entorno
```bash
# ChromaDB
CHROMA_PERSIST_DIR=./data/chroma

# Redis Cache
REDIS_CACHE_URL=redis://localhost:6379/0
REDIS_CACHE_TTL=300

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/db
```

### Requirements
```text
chromadb>=0.4.15
sentence-transformers>=2.3.0
redis>=5.0.1
fastapi>=0.116.1
sqlalchemy>=2.0.41
```

## Instalación y Setup

### 1. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 2. Configurar Base de Datos
```bash
# Ejecutar migraciones
alembic upgrade head
```

### 3. Inicializar Sistema de Búsqueda
```bash
# Inicialización completa
python scripts/init_search_system.py --full-sync --reset-chroma --test

# Solo sincronización incremental
python scripts/init_search_system.py

# Solo tests
python scripts/init_search_system.py --test --skip-sync
```

### 4. Verificar Estado
```bash
# Health check
curl http://localhost:8000/api/v1/search/health

# Métricas
curl http://localhost:8000/api/v1/search/analytics
```

## Performance y Optimización

### Métricas Objetivo
- **Tiempo de respuesta**: < 500ms para 95% de búsquedas
- **Cache hit rate**: > 75%
- **Search success rate**: > 90% (con resultados)
- **Throughput**: > 1000 searches/min

### Optimizaciones Implementadas

1. **Índices GIN**: Búsqueda full-text optimizada en PostgreSQL
2. **Cache Inteligente**: TTL adaptativo basado en popularidad
3. **Batch Processing**: Embeddings generados en lotes
4. **Async Operations**: Búsquedas paralelas text + semantic
5. **Connection Pooling**: Conexiones reutilizadas

### Monitoring

```python
# Cache metrics
cache_metrics = await cache_service.get_cache_metrics()
print(f"Hit rate: {cache_metrics['hit_rate']}%")

# Search analytics
analytics = await search_service.get_search_analytics(days=7)
print(f"Total searches: {analytics['total_searches']}")

# ChromaDB stats
stats = await chroma_service.get_collection_stats()
print(f"Products embedded: {stats['products_collection']['count']}")
```

## Casos de Uso

### 1. Búsqueda Simple
```bash
curl -X POST http://localhost:8000/api/v1/search/search \
  -H "Content-Type: application/json" \
  -d '{"query": "laptop"}'
```

### 2. Búsqueda con Filtros
```bash
curl -X POST http://localhost:8000/api/v1/search/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "smartphone",
    "price_max": 800,
    "categories": ["electronics"],
    "has_stock": true
  }'
```

### 3. Búsqueda Semántica
```bash
# "laptop para gaming" encontrará "computadora para juegos"
curl -X POST http://localhost:8000/api/v1/search/search \
  -H "Content-Type: application/json" \
  -d '{"query": "computadora para juegos"}'
```

### 4. Productos Similares
```bash
curl http://localhost:8000/api/v1/search/products/uuid-123/similar
```

## Troubleshooting

### Problemas Comunes

1. **ChromaDB no inicializa**
   ```bash
   # Resetear collections
   python scripts/init_search_system.py --reset-chroma
   ```

2. **Búsquedas lentas**
   ```bash
   # Verificar índices
   SELECT indexname FROM pg_indexes WHERE tablename = 'products';

   # Ejecutar migración de índices
   alembic upgrade head
   ```

3. **Cache hit rate bajo**
   ```bash
   # Verificar configuración Redis
   redis-cli ping

   # Revisar métricas
   curl http://localhost:8000/api/v1/search/analytics
   ```

4. **Embeddings desactualizados**
   ```bash
   # Sincronización incremental
   python scripts/init_search_system.py

   # Sincronización completa
   python scripts/init_search_system.py --full-sync
   ```

### Logs y Debugging

```python
import logging
logging.getLogger('app.services.search_service').setLevel(logging.DEBUG)
logging.getLogger('app.services.chroma_service').setLevel(logging.DEBUG)
```

## Roadmap Futuro

### Próximas Mejoras
- [ ] **A/B Testing**: Framework para testing de algoritmos de ranking
- [ ] **Personalization**: Búsquedas personalizadas por usuario
- [ ] **Multi-language**: Soporte completo para múltiples idiomas
- [ ] **Real-time Sync**: Sincronización en tiempo real con webhooks
- [ ] **ML Ranking**: Modelos de machine learning para ranking
- [ ] **Voice Search**: Integración con búsqueda por voz
- [ ] **Image Search**: Búsqueda por imágenes de productos

### Escalabilidad
- [ ] **Distributed ChromaDB**: Configuración distribuida
- [ ] **Elasticsearch Integration**: Para casos de alto volumen
- [ ] **Microservices**: Separación en microservicios independientes
- [ ] **Edge Caching**: CDN para resultados de búsqueda
- [ ] **Async Processing**: Queue system para sincronización

---

## Contacto y Soporte

Para preguntas técnicas o reportar issues:
- **Documentación**: Este archivo (SEARCH_SYSTEM.md)
- **Health Check**: `/api/v1/search/health`
- **Analytics**: `/api/v1/search/analytics`

---

**🎯 El sistema de búsqueda avanzada de MeStore está diseñado para escalar y evolucionar con las necesidades del marketplace, proporcionando una experiencia de búsqueda superior que combina precisión técnica con relevancia semántica.**