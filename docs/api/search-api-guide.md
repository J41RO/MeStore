# MeStore Search API Guide

## Guía Completa de la API de Búsqueda Avanzada

### Descripción General

La API de Búsqueda de MeStore proporciona un sistema de búsqueda híbrido potente que combina búsqueda de texto tradicional con búsqueda semántica avanzada usando ChromaDB. Diseñada para ofrecer resultados relevantes y rápidos con múltiples opciones de filtrado y personalización.

### Características Principales

- **Búsqueda Híbrida**: Combina PostgreSQL full-text search con ChromaDB semantic search
- **Autocomplete Inteligente**: Sugerencias en tiempo real con cache optimizado
- **Facetas Dinámicas**: Filtros contextuales que se ajustan a los resultados
- **Analytics Integrados**: Tracking automático para mejora continua
- **Cache Multi-Nivel**: Sistema de cache inteligente para performance óptima
- **Rate Limiting**: Protección contra abuso con límites ajustables

## Endpoints Principales

### 1. Búsqueda General
**GET** `/api/v1/search`

Búsqueda principal con filtros múltiples.

**Parámetros:**
```
q: string (opcional) - Término de búsqueda
category_id: UUID (opcional) - Filtrar por categoría
vendor_id: UUID (opcional) - Filtrar por vendor
min_price: float (opcional) - Precio mínimo
max_price: float (opcional) - Precio máximo
in_stock: boolean (opcional) - Solo productos con stock
sort_by: enum - Criterio de ordenamiento
page: int - Número de página (default: 1)
limit: int - Resultados por página (default: 20, max: 100)
search_type: enum - Tipo de búsqueda (text|semantic|hybrid)
```

**Ejemplo de Request:**
```bash
GET /api/v1/search?q=laptop gaming&category_id=123&min_price=500&max_price=1500&sort_by=relevancia&page=1&limit=20
```

**Ejemplo de Response:**
```json
{
  "results": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "sku": "LAP001",
      "name": "Laptop Gaming ASUS ROG",
      "description": "Laptop gaming de alta performance",
      "precio_venta": 1500.00,
      "categoria": "Electrónicos",
      "tags": ["gaming", "laptop", "asus"],
      "status": "DISPONIBLE",
      "stock_disponible": 5,
      "vendor_name": "TechStore",
      "score": 0.95,
      "match_type": "exact",
      "created_at": "2025-09-17T10:30:00Z"
    }
  ],
  "metadata": {
    "total_results": 150,
    "page": 1,
    "limit": 20,
    "total_pages": 8,
    "search_time_ms": 45,
    "search_type": "text",
    "has_next_page": true,
    "has_prev_page": false
  },
  "facets": [
    {
      "name": "category",
      "display_name": "Categoría",
      "type": "category",
      "values": [
        {"value": "Electrónicos", "count": 85, "selected": false},
        {"value": "Computadoras", "count": 42, "selected": false}
      ],
      "multiple": true
    }
  ],
  "suggestions": ["laptop gaming", "laptop asus", "gaming computer"]
}
```

### 2. Búsqueda Avanzada
**POST** `/api/v1/search/advanced`

Búsqueda con configuración granular y filtros complejos.

**Request Body:**
```json
{
  "query": "laptop gaming",
  "filters": {
    "category_path": "/electronics/computers/",
    "price_range": {"min": 500, "max": 2000},
    "vendor_rating": {"min": 4.0},
    "in_stock": true
  },
  "facets": ["category", "vendor", "price_ranges", "brands"],
  "boost": {"name": 2.0, "description": 1.5},
  "fuzzy": {"enabled": true, "distance": 2},
  "page": 1,
  "limit": 20,
  "sort_by": "relevancia",
  "search_type": "hybrid"
}
```

### 3. Búsqueda Semántica
**POST** `/api/v1/search/semantic`

Búsqueda por similitud semántica usando ChromaDB.

**Request Body:**
```json
{
  "query": "computadora para juegos",
  "limit": 10,
  "threshold": 0.7,
  "include_metadata": true,
  "category_filter": null,
  "vendor_filter": null
}
```

**Response:**
```json
{
  "results": [...],
  "query": "computadora para juegos",
  "similarity_threshold": 0.7,
  "total_embeddings_searched": 1500,
  "response_time_ms": 85
}
```

### 4. Autocomplete
**GET** `/api/v1/search/autocomplete`

Sugerencias en tiempo real para autocompletado.

**Parámetros:**
```
q: string (requerido) - Término parcial
limit: int - Número de sugerencias (default: 5, max: 20)
category_id: UUID (opcional) - Filtrar por categoría
include_categories: boolean - Incluir categorías (default: true)
include_vendors: boolean - Incluir vendors (default: false)
```

**Response:**
```json
{
  "suggestions": [
    {
      "text": "laptop gaming",
      "type": "product",
      "score": 0.95,
      "metadata": {"category": "Electrónicos", "count": 25}
    },
    {
      "text": "Laptops",
      "type": "category",
      "score": 0.88,
      "id": "cat-123",
      "metadata": {"product_count": 150}
    }
  ],
  "query": "lap",
  "response_time_ms": 15
}
```

### 5. Productos Similares
**GET** `/api/v1/search/similar/{product_id}`

Encontrar productos similares a uno específico.

**Parámetros:**
```
product_id: UUID (path) - ID del producto base
limit: int - Número de productos similares (default: 10, max: 20)
```

### 6. Opciones de Filtro
**GET** `/api/v1/search/filters`

Obtener opciones de filtro disponibles.

**Response:**
```json
{
  "categories": [
    {"id": "cat-123", "name": "Electrónicos", "product_count": 500}
  ],
  "vendors": [
    {"id": "ven-123", "name": "TechStore", "product_count": 150}
  ],
  "price_ranges": [
    {"min": 0, "max": 100, "count": 250}
  ],
  "tags": ["gaming", "premium", "sale", "new"],
  "status_options": ["DISPONIBLE", "VERIFICADO", "TRANSITO"]
}
```

### 7. Analytics de Búsqueda
**POST** `/api/v1/search/analytics`

Trackear analytics de búsquedas.

**Request Body:**
```json
{
  "query": "laptop gaming",
  "search_type": "text",
  "results_count": 150,
  "response_time_ms": 45,
  "user_id": "user-123",
  "session_id": "session-456",
  "clicked_results": ["product-789"],
  "filters_used": {"category_id": "cat-123"},
  "page_viewed": 1
}
```

### 8. Términos Trending
**GET** `/api/v1/search/trending`

Obtener términos de búsqueda trending.

**Parámetros:**
```
period: enum - Período (last_24_hours|last_7_days|last_30_days)
limit: int - Número de términos (default: 10, max: 50)
category_id: UUID (opcional) - Filtrar por categoría
```

### 9. Búsquedas Populares
**GET** `/api/v1/search/popular`

Obtener búsquedas más populares.

**Parámetros:**
```
period: enum - Período (last_7_days|last_30_days|last_90_days)
limit: int - Número de búsquedas (default: 10, max: 50)
category_id: UUID (opcional) - Filtrar por categoría
```

## Tipos de Búsqueda

### Text Search
Búsqueda tradicional basada en coincidencias de texto:
- Búsqueda en nombre, descripción y SKU
- Soporte para palabras parciales
- Búsqueda por frases exactas
- Filtros por campos específicos

### Semantic Search
Búsqueda por similitud semántica:
- Entiende el significado, no solo palabras
- "teléfono inteligente" encuentra "smartphone"
- Ideal para búsquedas conceptuales
- Usa embeddings de ChromaDB

### Hybrid Search
Combina ambos enfoques:
- Fusiona scores de text y semantic search
- Mejor precisión y recall
- Adaptativo según el tipo de query
- Configuración de boost por método

## Opciones de Ordenamiento

- **relevancia**: Score calculado por algoritmo (default)
- **precio_asc**: Precio ascendente
- **precio_desc**: Precio descendente
- **fecha_asc**: Fecha de creación ascendente
- **fecha_desc**: Fecha de creación descendente (más recientes primero)
- **nombre_asc**: Nombre alfabético A-Z
- **nombre_desc**: Nombre alfabético Z-A
- **popularidad**: Basado en métricas de popularidad

## Performance y Caching

### Cache Multi-Nivel
- **L1**: Queries exactas (TTL: 5 min)
- **L2**: Resultados procesados (TTL: 30 min)
- **L3**: Facetas y agregaciones (TTL: 1 hora)
- **L4**: Autocomplete (TTL: 2 horas)

### Optimizaciones
- Compresión automática para respuestas > 1KB
- Cache hit ratio típico: >85%
- Respuesta promedio: <100ms para queries cacheadas
- Warm-up automático de queries populares

## Rate Limiting

### Límites por Endpoint
- **Búsqueda general**: 60 requests/minuto
- **Búsqueda avanzada**: 20 requests/minuto
- **Búsqueda semántica**: 10 requests/minuto
- **Autocomplete**: 120 requests/minuto
- **Productos similares**: 30 requests/minuto

### Headers de Rate Limit
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1632150000
```

## Códigos de Error

### 400 Bad Request
```json
{
  "error": "validation_error",
  "message": "Invalid search parameters",
  "suggestions": ["Check your search parameters", "Verify data types"]
}
```

### 429 Too Many Requests
```json
{
  "error": "rate_limit_exceeded",
  "message": "Rate limit exceeded for search requests",
  "suggestions": ["Reduce request frequency", "Upgrade to higher tier"]
}
```

### 500 Internal Server Error
```json
{
  "error": "internal_error",
  "message": "Search service temporarily unavailable",
  "suggestions": ["Try again in a few moments", "Use simpler search terms"]
}
```

## Ejemplos de Uso

### Búsqueda Básica por Texto
```bash
curl -X GET "https://api.mestore.com/v1/search?q=laptop&limit=10" \
  -H "Authorization: Bearer your-token"
```

### Búsqueda con Filtros
```bash
curl -X GET "https://api.mestore.com/v1/search?q=smartphone&category_id=electronics&min_price=200&max_price=800&in_stock=true" \
  -H "Authorization: Bearer your-token"
```

### Búsqueda Semántica
```bash
curl -X POST "https://api.mestore.com/v1/search/semantic" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token" \
  -d '{
    "query": "dispositivo para hacer ejercicio en casa",
    "limit": 5,
    "threshold": 0.8
  }'
```

### Autocomplete
```bash
curl -X GET "https://api.mestore.com/v1/search/autocomplete?q=lap&limit=5" \
  -H "Authorization: Bearer your-token"
```

## SDKs y Bibliotecas

### JavaScript/TypeScript
```typescript
import { MeStoreSearchClient } from '@mestore/search-sdk';

const client = new MeStoreSearchClient({
  apiKey: 'your-api-key',
  baseUrl: 'https://api.mestore.com'
});

// Búsqueda básica
const results = await client.search({
  query: 'laptop gaming',
  filters: {
    category: 'electronics',
    priceRange: [500, 1500]
  }
});

// Autocomplete
const suggestions = await client.autocomplete('lap');
```

### Python
```python
from mestore_search import SearchClient

client = SearchClient(
    api_key='your-api-key',
    base_url='https://api.mestore.com'
)

# Búsqueda básica
results = client.search(
    query='laptop gaming',
    category_id='electronics',
    min_price=500,
    max_price=1500
)

# Búsqueda semántica
semantic_results = client.semantic_search(
    query='computadora para juegos',
    threshold=0.8
)
```

## Mejores Prácticas

### Para Desarrolladores Frontend
1. **Implementar debouncing** para autocomplete (300-500ms)
2. **Usar paginación** para listas largas
3. **Mostrar facetas** para refinamiento de búsqueda
4. **Implementar búsqueda incremental** para mejor UX
5. **Cachear resultados** en el cliente temporalmente

### Para Integración Backend
1. **Usar filtros específicos** antes de búsqueda de texto
2. **Implementar retry logic** para fallos temporales
3. **Monitorear métricas** de performance y hit ratio
4. **Usar semantic search** para queries conceptuales
5. **Trackear analytics** para optimización continua

### Optimización de Performance
1. **Filtrar por categoría** cuando sea posible
2. **Usar límites apropiados** (20-50 resultados típico)
3. **Implementar lazy loading** para metadatos pesados
4. **Usar cache del cliente** para queries repetitivas
5. **Monitorear response times** y optimizar queries lentas

## Soporte y Contacto

- **Documentación**: https://docs.mestore.com/search-api
- **Status Page**: https://status.mestore.com
- **GitHub Issues**: https://github.com/mestore/search-api/issues
- **Email**: api-support@mestore.com
- **Discord**: https://discord.gg/mestore-dev

---

*Última actualización: 2025-09-17*
*Versión API: v1.0*
