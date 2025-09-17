# API de Categorías Jerárquicas - MeStore

## Descripción General

La API de categorías jerárquicas de MeStore proporciona un sistema completo para gestionar categorías de productos en estructura de árbol, optimizado para marketplaces con múltiples niveles de organización.

## Características Principales

### 🏗️ Arquitectura
- **Estructura jerárquica**: Soporte para hasta 10 niveles de profundidad
- **Paths materializados**: Optimización para consultas de ancestros/descendientes
- **Slugs SEO-friendly**: URLs optimizadas para motores de búsqueda
- **Soft delete**: Eliminación segura con preservación de datos

### 🔐 Seguridad y Permisos
- **Autenticación JWT**: Tokens seguros para operaciones protegidas
- **Control de acceso basado en roles**:
  - **Administradores**: CRUD completo, operaciones bulk, estadísticas
  - **Vendedores**: Asignación de categorías a sus productos
  - **Público**: Consultas de navegación y búsqueda

### ⚡ Performance
- **Eager loading**: Optimización de consultas para relaciones
- **Paginación**: Manejo eficiente de listas grandes
- **Cache-ready**: Preparado para implementación de cache Redis
- **Operaciones bulk**: Creación masiva optimizada

## Endpoints Disponibles

### 📋 CRUD de Categorías (Administradores)

#### POST /api/v1/categories
**Crear nueva categoría**
- **Permisos**: Solo administradores
- **Features**:
  - Auto-generación de slug único
  - Validación de jerarquía (máximo 10 niveles)
  - Cálculo automático de level y path

```json
{
  "name": "Electrónicos",
  "description": "Productos electrónicos y tecnología",
  "parent_id": null,
  "is_active": true,
  "sort_order": 0,
  "meta_title": "Electrónicos - MeStore",
  "meta_description": "Encuentra los mejores productos electrónicos"
}
```

#### GET /api/v1/categories/{id}
**Obtener categoría específica**
- **Permisos**: Público
- **Features**: Incluye información del padre y contadores

#### PUT /api/v1/categories/{id}
**Actualizar categoría completa**
- **Permisos**: Solo administradores
- **Features**: Validación de slug único, actualización de timestamps

#### DELETE /api/v1/categories/{id}
**Eliminar categoría (soft delete)**
- **Permisos**: Solo administradores
- **Features**: Validación de subcategorías/productos activos

### 🌐 Consultas Públicas

#### GET /api/v1/categories
**Lista paginada con filtros**
- **Permisos**: Público
- **Parámetros**:
  - `page`, `size`: Paginación
  - `search`: Búsqueda en nombre/descripción
  - `parent_id`: Filtrar por padre
  - `level`: Filtrar por nivel jerárquico
  - `is_active`: Filtrar por estado
  - `sort_by`, `sort_desc`: Ordenamiento

#### GET /api/v1/categories/tree
**Árbol jerárquico completo**
- **Permisos**: Público
- **Features**:
  - Estructura anidada optimizada
  - Control de profundidad máxima
  - Opción de incluir categorías inactivas

```json
{
  "categories": [
    {
      "id": "uuid",
      "name": "Electrónicos",
      "slug": "electronicos",
      "level": 0,
      "children": [
        {
          "id": "uuid",
          "name": "Smartphones",
          "slug": "smartphones",
          "level": 1,
          "children": []
        }
      ]
    }
  ],
  "total_categories": 25,
  "max_depth": 3
}
```

#### GET /api/v1/categories/{id}/children
**Subcategorías directas**
- **Permisos**: Público
- **Features**: Solo subcategorías de nivel inmediato

#### GET /api/v1/categories/{id}/products
**Productos de categoría**
- **Permisos**: Público
- **Features**:
  - Paginación de productos
  - Opción de incluir productos de subcategorías

### 🎯 Operaciones Especiales

#### POST /api/v1/categories/{id}/move
**Mover categoría en jerarquía**
- **Permisos**: Solo administradores
- **Features**:
  - Validación anti-ciclos
  - Recálculo automático de paths
  - Actualización de niveles descendientes

```json
{
  "new_parent_id": "uuid-del-nuevo-padre",
  "new_sort_order": 5
}
```

#### GET /api/v1/categories/slug/{slug}
**Buscar por slug SEO**
- **Permisos**: Público
- **Features**: Búsqueda optimizada por índice de slug

#### GET /api/v1/categories/breadcrumb/{id}
**Ruta de navegación breadcrumb**
- **Permisos**: Público
- **Features**: Ruta completa desde raíz hasta categoría actual

```json
{
  "breadcrumb": [
    {
      "id": "uuid",
      "name": "Electrónicos",
      "slug": "electronicos",
      "level": 0
    },
    {
      "id": "uuid",
      "name": "Smartphones",
      "slug": "smartphones",
      "level": 1
    }
  ],
  "current_category": {
    "id": "uuid",
    "name": "iPhone",
    "slug": "iphone",
    "level": 2
  }
}
```

### 📦 Operaciones Bulk

#### POST /api/v1/categories/bulk
**Creación masiva de categorías**
- **Permisos**: Solo administradores
- **Features**:
  - Transacción atómica (todo o nada)
  - Validación de lote completo
  - Máximo 100 categorías por operación

```json
{
  "categories": [
    {
      "name": "Categoría 1",
      "parent_id": null
    },
    {
      "name": "Categoría 2",
      "parent_id": "uuid-padre"
    }
  ]
}
```

#### PUT /api/v1/categories/products/{product_id}/categories
**Asignar categorías a producto**
- **Permisos**: Administradores y vendedores (solo sus productos)
- **Features**:
  - Máximo 10 categorías por producto
  - Designación de categoría principal

```json
{
  "category_ids": ["uuid1", "uuid2", "uuid3"],
  "primary_category_id": "uuid1"
}
```

### 📊 Estadísticas y Monitoreo

#### GET /api/v1/categories/stats
**Estadísticas del sistema**
- **Permisos**: Solo administradores
- **Features**: Métricas completas del sistema de categorías

```json
{
  "total_categories": 150,
  "active_categories": 142,
  "root_categories": 8,
  "max_depth": 4,
  "categories_with_products": 95,
  "empty_categories": 47,
  "most_popular_categories": [
    {
      "id": "uuid",
      "name": "Electrónicos",
      "products_count": 1250
    }
  ]
}
```

#### GET /api/v1/categories/health
**Health check del sistema**
- **Permisos**: Público
- **Features**: Verificación de integridad de jerarquía

## Arquitectura Técnica

### 📐 Schemas Pydantic

#### CategoryBase
Campos comunes para operaciones de categorías:
- `name`: Nombre (1-100 caracteres)
- `slug`: Slug SEO (auto-generado si no se proporciona)
- `description`: Descripción opcional
- `is_active`: Estado activo (default: true)
- `sort_order`: Orden de clasificación (0-9999)
- `meta_title`, `meta_description`: SEO metadata
- `image_url`: URL de imagen representativa

#### CategoryCreate
Hereda de CategoryBase + `parent_id` para creación

#### CategoryUpdate
Campos opcionales para actualización parcial

#### CategoryRead
Representación completa con metadatos:
- Todos los campos base
- `id`, `parent_id`, `level`, `path`
- `children_count`, `products_count`
- `created_at`, `updated_at`, `parent_name`

#### CategoryTree
Estructura jerárquica anidada con contadores globales

### 🏗️ Servicio de Lógica de Negocio

#### CategoryService
Clase principal que maneja:

**Validaciones**:
- Integridad jerárquica (prevención de ciclos)
- Profundidad máxima (10 niveles)
- Slugs únicos con numeración automática
- Validación de categorías padre

**Operaciones Complejas**:
- Construcción de árboles jerárquicos
- Cálculo de paths materializados
- Movimiento con recálculo de descendientes
- Operaciones bulk optimizadas

**Optimizaciones**:
- Eager loading para relaciones
- Consultas optimizadas por índices
- Cache-ready para Redis

### 🔧 Configuración y Límites

#### Límites del Sistema
- **Profundidad máxima**: 10 niveles
- **Slug máximo**: 120 caracteres
- **Categorías por producto**: 10 máximo
- **Bulk creation**: 100 categorías máximo
- **Paginación**: 1-100 items por página

#### Validaciones de Integridad
- Prevención de ciclos en jerarquía
- Validación de existencia de categorías padre
- Unicidad de slugs con auto-numeración
- Soft delete con preservación de relaciones

## Integración con Frontend

### 🎨 Preparado para React
La API está diseñada para integración directa con:
- **react-specialist-ai**: Componentes de navegación
- **Canvas**: Sistema de productos visuales
- **Filtros dinámicos**: Búsqueda y filtrado en tiempo real

### 📱 Casos de Uso Típicos

1. **Navegación de Marketplace**:
   ```javascript
   // Obtener árbol completo para menú principal
   GET /api/v1/categories/tree

   // Obtener productos de categoría específica
   GET /api/v1/categories/{id}/products?include_subcategories=true
   ```

2. **Breadcrumb Navigation**:
   ```javascript
   // Construir breadcrumb para producto
   GET /api/v1/categories/breadcrumb/{category_id}
   ```

3. **Admin Dashboard**:
   ```javascript
   // Estadísticas para dashboard
   GET /api/v1/categories/stats

   // Crear categorías en lote
   POST /api/v1/categories/bulk
   ```

## Próximos Pasos

### 🔄 Integración Pendiente
1. **Database Architect AI**: Implementación de modelos Category
2. **React Specialist AI**: Componentes de navegación frontend
3. **Cache Layer**: Implementación de Redis para performance
4. **Search Integration**: Conectar con motor de búsqueda

### 🚀 Features Futuras
- **Categorías dinámicas**: Basadas en atributos de productos
- **Recomendaciones**: ML para sugerir categorías
- **Anályticas**: Métricas avanzadas de navegación
- **Multi-idioma**: Soporte para categorías localizadas

---

**Estado**: ✅ Arquitectura API completa - Listo para implementación de modelos
**Autor**: API Architect AI
**Fecha**: 2025-09-17
**Versión**: 1.0.0