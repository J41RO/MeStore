# Sistema de Búsqueda Avanzada - MeStore

## Descripción General

Sistema completo de búsqueda para el marketplace MeStore, desarrollado con React 18, TypeScript, Zustand, y Tailwind CSS. Incluye funcionalidades avanzadas como autocomplete, filtros dinámicos, búsqueda semántica, y optimizaciones de performance.

## Arquitectura del Sistema

### 📁 Estructura de Archivos

```
src/
├── components/search/
│   ├── SearchBar.tsx              # Barra principal de búsqueda
│   ├── SearchResults.tsx          # Resultados con infinite scroll
│   ├── SearchFilters.tsx          # Filtros avanzados
│   ├── SearchFacets.tsx           # Facetas dinámicas
│   ├── SearchSuggestions.tsx      # Sugerencias y autocomplete
│   ├── AdvancedSearchModal.tsx    # Modal de búsqueda avanzada
│   └── index.ts                   # Exportaciones
├── hooks/search/
│   ├── useSearch.ts               # Hook principal
│   ├── useSearchFilters.ts        # Gestión de filtros
│   ├── useSearchHistory.ts        # Historial de búsquedas
│   ├── useSearchSuggestions.ts    # Autocomplete
│   ├── useSearchAnalytics.ts      # Analytics opcional
│   └── index.ts                   # Exportaciones
├── stores/
│   └── searchStore.ts             # Estado global con Zustand
├── services/
│   └── searchService.ts           # Integración con APIs
├── types/
│   └── search.types.ts            # Tipos TypeScript
└── pages/
    └── SearchPage.tsx             # Página principal de búsqueda
```

### 🔧 Tecnologías Utilizadas

- **React 18**: Concurrent features, Suspense, hooks modernos
- **TypeScript**: Tipado estricto y interfaces completas
- **Zustand**: Estado global con middleware de persistencia
- **Tailwind CSS**: Styling responsive y componentes
- **Axios**: Cliente HTTP para APIs
- **React Router**: Navegación y sincronización de URL

## Componentes Principales

### 🔍 SearchBar

Barra de búsqueda principal con funcionalidades avanzadas.

**Características:**
- Autocomplete en tiempo real
- Debounce configurable (300ms por defecto)
- Búsqueda por voz (Web Speech API)
- Navegación con teclado
- Validación de queries
- Responsive design

**Props principales:**
```typescript
interface SearchBarProps {
  placeholder?: string;
  showVoiceSearch?: boolean;
  showAdvancedLink?: boolean;
  enableAutocomplete?: boolean;
  size?: 'sm' | 'md' | 'lg';
  onSearchChange?: (query: string) => void;
}
```

**Ejemplo de uso:**
```tsx
<SearchBar
  placeholder="Buscar productos..."
  showVoiceSearch={true}
  enableAutocomplete={true}
  size="md"
/>
```

### 📊 SearchResults

Componente para mostrar resultados con optimizaciones de performance.

**Características:**
- Infinite scroll optimizado
- Vista grid/list intercambiable
- Sorting por múltiples criterios
- Loading skeletons
- Estados de error y vacío
- Virtual scrolling para grandes datasets

**Props principales:**
```typescript
interface SearchResultsProps {
  onResultClick?: (product: Product) => void;
  showSorting?: boolean;
  showViewToggle?: boolean;
  infiniteScroll?: boolean;
  emptyStateMessage?: string;
}
```

### 🎛️ SearchFilters

Filtros avanzados con múltiples criterios de búsqueda.

**Características:**
- Filtros colapsibles por sección
- Multi-selección con contadores
- Rango de precios con sliders
- Chips de filtros activos
- Orientación horizontal/vertical
- Persistencia de estado

**Tipos de filtros:**
- Categorías (tree structure)
- Rango de precios
- Vendedores
- Calificación mínima
- Disponibilidad
- Fechas
- Ubicación (opcional)

### 🔮 SearchSuggestions

Sistema de sugerencias inteligentes y autocomplete.

**Características:**
- Sugerencias por tipo (query, categoría, producto, vendor)
- Highlighting de términos coincidentes
- Búsquedas recientes y populares
- Navegación con teclado (Arrow keys, Enter, Escape)
- Agrupación inteligente de resultados

### ⚙️ AdvancedSearchModal

Modal completo para búsquedas avanzadas.

**Características:**
- Búsqueda semántica
- Gestión de búsquedas guardadas
- Exportar/importar configuraciones
- Formulario completo de filtros
- Tags y categorización

## Hooks Personalizados

### 🎣 useSearch

Hook principal que combina toda la funcionalidad de búsqueda.

```typescript
const {
  // Estado
  query,
  results,
  isSearching,
  hasResults,
  error,

  // Métodos
  search,
  quickSearch,
  clearSearch,

  // Selectores
  products,
  totalProducts,
  canLoadMore,

  // Paginación
  loadMore,
  goToPage,
} = useSearch();
```

### 🎣 useSearchFilters

Hook especializado para gestión de filtros.

```typescript
const {
  filters,
  activeFiltersCount,
  categories,
  vendors,
  setFilter,
  toggleFilter,
  clearAllFilters,
  isFilterActive,
} = useSearchFilters();
```

### 🎣 useSearchHistory

Hook para gestión del historial de búsquedas.

```typescript
const {
  recentSearches,
  savedSearches,
  saveCurrentSearch,
  loadSavedSearch,
  clearHistory,
} = useSearchHistory();
```

## Estado Global (Zustand)

### 📦 SearchStore

El store principal maneja todo el estado de búsqueda con persistencia.

**Estado incluido:**
- Query actual y filtros
- Resultados y metadatos
- Historial y búsquedas guardadas
- Configuración de búsqueda
- Cache de resultados
- Estados de carga y error

**Middleware utilizado:**
- `persist`: Persistencia en localStorage
- `devtools`: Integración con Redux DevTools
- `subscribeWithSelector`: Suscripciones selectivas
- `immer`: Mutaciones inmutables

## Integración con APIs

### 🌐 SearchService

Servicio para comunicación con el backend.

**Endpoints principales:**
```typescript
// Búsqueda principal
GET /api/v1/search/products?q=query&filters=...

// Sugerencias
GET /api/v1/search/suggestions?q=query

// Categorías para filtros
GET /api/v1/search/categories

// Vendors para filtros
GET /api/v1/search/vendors

// Analytics (opcional)
POST /api/v1/search/analytics
```

**Transformaciones de datos:**
- Parámetros de búsqueda a formato API
- Respuestas API a tipos TypeScript
- Manejo de errores y fallbacks
- Cache y optimizaciones

## Performance y Optimizaciones

### ⚡ Optimizaciones React

- **React.memo**: Componentes memoizados para evitar re-renders
- **useMemo/useCallback**: Cálculos y funciones memoizadas
- **Lazy loading**: Imágenes y componentes bajo demanda
- **Code splitting**: División de código por rutas
- **Virtual scrolling**: Para listas grandes de productos

### 🚀 Optimizaciones de Estado

- **Debounce**: 300ms para búsquedas automáticas
- **Cache inteligente**: Resultados en memoria con TTL
- **Optimistic updates**: Updates inmediatos en UI
- **Batch updates**: Agrupación de actualizaciones de estado

### 📱 Responsive Design

- **Mobile-first**: Diseño optimizado para móviles
- **Breakpoints**: sm, md, lg, xl responsive
- **Touch-friendly**: Controles optimizados para touch
- **Adaptive layout**: Layout que se adapta al contenido

## Casos de Uso por Rol

### 👤 Buyer (Comprador)

**Búsqueda principal:**
```tsx
// Búsqueda simple
<SearchBar placeholder="¿Qué estás buscando?" />

// Resultados con filtros
<SearchResults onResultClick={navigateToProduct} />
<SearchFilters orientation="vertical" />
```

**Funcionalidades específicas:**
- Búsqueda de productos disponibles
- Filtros por precio, categoría, ubicación
- Comparación de productos
- Guardar búsquedas favoritas

### 🏪 Vendor (Vendedor)

**Búsqueda de inventario:**
```tsx
// Búsqueda de sus productos
const { searchVendorProducts } = useSearch();

searchVendorProducts(vendorId, {
  query: 'laptop',
  filters: { inStock: true }
});
```

**Funcionalidades específicas:**
- Gestión de inventario propio
- Análisis de competencia
- Optimización de listings
- Reportes de búsquedas

### 👑 Admin (Administrador)

**Analytics y gestión:**
```tsx
// Búsqueda con analytics completos
const { trackSearch, trackClick } = useSearchAnalytics();

// Dashboard de métricas
<SearchAnalyticsDashboard />
```

**Funcionalidades específicas:**
- Analytics globales de búsqueda
- Gestión de categorías y filtros
- Moderación de contenido
- Optimización del sistema

## URL State Management

### 🔗 Sincronización de URL

El sistema sincroniza automáticamente el estado con la URL para búsquedas compartibles.

**Formato de URL:**
```
/search?q=laptop&category=electronicos&min=500&max=1500&sort=price&page=2
```

**Parámetros soportados:**
- `q`: Query de búsqueda
- `category`: Categorías seleccionadas
- `vendor`: Vendedores seleccionados
- `min`/`max`: Rango de precios
- `rating`: Calificación mínima
- `sort`: Criterio de ordenamiento
- `page`: Página actual
- `view`: Modo de vista (grid/list)

## Testing

### 🧪 Estrategia de Testing

**Unit Tests:**
- Hooks personalizados
- Utilidades y helpers
- Componentes aislados

**Integration Tests:**
- Flujo completo de búsqueda
- Interacción entre componentes
- Estado global

**E2E Tests:**
- User journeys completos
- Performance testing
- Cross-browser testing

## Configuración y Personalización

### ⚙️ Configuración del Store

```typescript
const searchConfig: SearchConfig = {
  debounceMs: 300,
  minQueryLength: 2,
  maxSuggestions: 10,
  maxRecentSearches: 20,
  enableVoiceSearch: false,
  enableSemanticSearch: true,
  defaultSort: 'relevance',
  infiniteScroll: true,
};
```

### 🎨 Personalización de Estilos

Los componentes usan Tailwind CSS y son completamente personalizables:

```tsx
<SearchBar
  className="custom-search-bar"
  size="lg"
/>

<SearchResults
  className="custom-results"
  // Personalizar colores, spacing, etc.
/>
```

## Roadmap y Futuras Mejoras

### 🚀 Próximas Características

1. **AI-Powered Search**
   - Búsqueda por imágenes
   - Recomendaciones inteligentes
   - NLP avanzado

2. **Performance Avanzada**
   - Service Worker para cache
   - Background sync
   - Offline support

3. **UX Enhancements**
   - Filtros por AR/VR
   - Búsqueda geolocalizada
   - Social search

4. **Analytics Avanzados**
   - Heat maps de búsqueda
   - A/B testing integrado
   - Predictive analytics

## Troubleshooting

### 🐛 Problemas Comunes

**Búsquedas lentas:**
- Verificar debounce configuration
- Revisar cache de resultados
- Optimizar queries del backend

**Autocomplete no funciona:**
- Verificar `minQueryLength`
- Revisar conexión con API
- Comprobar CORS settings

**Filtros no se aplican:**
- Verificar sincronización de estado
- Revisar URL parameters
- Comprobar API integration

**Memory leaks:**
- Verificar cleanup de efectos
- Revisar cache size limits
- Comprobar event listeners

## Soporte y Contribución

### 📞 Contacto

- **Developer**: React Specialist AI
- **Team**: Frontend Department
- **Email**: frontend@mestore.com

### 🤝 Contribución

1. Fork del repositorio
2. Crear feature branch
3. Implementar cambios con tests
4. Crear pull request
5. Code review y merge

### 📚 Documentación Adicional

- [API Documentation](../../../docs/api.md)
- [Component Storybook](../../../storybook)
- [Performance Guide](../../../docs/performance.md)
- [Testing Guide](../../../docs/testing.md)

---

**Última actualización**: 2025-09-17
**Versión**: 1.0.0
**Compatibilidad**: React 18+, TypeScript 5+