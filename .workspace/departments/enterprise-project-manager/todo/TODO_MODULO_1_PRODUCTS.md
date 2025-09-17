# 📦 TODO MÓDULO 1: PRODUCT MANAGEMENT SYSTEM

**Base Compatible**: TODO_CONFIGURACION_BASE_ENTERPRISE.md ✅
**Dependencias**: Database Architecture ✅, Auth System ✅, API Structure ✅
**Tiempo Estimado**: 14 horas (8h backend + 6h frontend)
**Prioridad**: 🔴 CRÍTICA - Core Business Module

---

## 🎯 OBJETIVO DEL MÓDULO
Crear el sistema completo de gestión de productos que permita al SUPERUSUARIO controlar todos los productos de todos los vendedores, con funcionalidades avanzadas de categorización, inventario, reviews y analytics.

---

## 🗄️ BACKEND - DATABASE & MODELS (4 horas)

### 1.1 Extender Modelo Product Enterprise (1.5h)
**Compatible con**: Database Architecture Base ✅

```python
# app/models/product.py - EXTENDER MODELO EXISTENTE
class Product(BaseModel):
    # CAMPOS EXISTENTES (mantener compatibilidad)
    id: int
    name: str
    description: text
    price: decimal
    vendor_id: FK
    category_id: FK
    created_at: datetime
    updated_at: datetime

    # NUEVOS CAMPOS ENTERPRISE
    sku: str = Field(unique=True, generated=True)
    barcode: str = Field(nullable=True)
    weight: decimal = Field(nullable=True)
    dimensions: JSON = Field(nullable=True)  # {length, width, height}
    brand: str = Field(nullable=True)
    model: str = Field(nullable=True)
    condition: ProductCondition = Field(default="new")  # new, used, refurbished
    warranty_months: int = Field(default=0)
    tags: JSON = Field(default=list)  # ["electronic", "mobile", "smartphone"]
    seo_title: str = Field(nullable=True)
    seo_description: text = Field(nullable=True)
    is_featured: bool = Field(default=False)  # SUPERUSER puede destacar productos
    is_promoted: bool = Field(default=False)  # Sistema de promociones
    promotion_ends_at: datetime = Field(nullable=True)
    min_order_quantity: int = Field(default=1)
    max_order_quantity: int = Field(nullable=True)
    digital_product: bool = Field(default=False)
    download_link: str = Field(nullable=True)
    requires_shipping: bool = Field(default=True)
    product_score: decimal = Field(default=0.0)  # Calculated from reviews/sales
    last_price_change: datetime = Field(nullable=True)
    price_history: JSON = Field(default=list)  # Track price changes
    created_by: FK = Field(nullable=True)  # SUPERUSER puede crear productos
    last_modified_by: FK = Field(nullable=True)
```

**Dependencias**: User model ✅, Database connection ✅
**Specialist**: @backend-senior-developer

### 1.2 Crear ProductVariant Model (1h)
**Propósito**: Manejar variaciones de productos (talla, color, etc.)

```python
# app/models/product_variant.py - NUEVO MODELO
class ProductVariant(BaseModel):
    id: int = Field(primary_key=True)
    product_id: FK to Product
    variant_type: str  # "size", "color", "material"
    variant_value: str  # "XL", "Red", "Cotton"
    price_modifier: decimal = Field(default=0.0)  # +/- price difference
    sku_suffix: str  # Combined with product SKU
    stock_quantity: int = Field(default=0)
    is_available: bool = Field(default=True)
    variant_image: str = Field(nullable=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Dependencias**: Product model ✅
**Specialist**: @backend-senior-developer

### 1.3 Crear ProductCategory Jerarquías (1h)
**Propósito**: Sistema de categorías con jerarquía multinivel

```python
# app/models/product_category.py - EXTENDER MODELO EXISTENTE
class ProductCategory(BaseModel):
    # CAMPOS EXISTENTES (mantener)
    id: int
    name: str
    description: text

    # NUEVOS CAMPOS ENTERPRISE
    parent_category_id: FK to ProductCategory = Field(nullable=True)  # Self-reference
    category_path: str  # "/Electronics/Mobile/Smartphones"
    level: int = Field(default=0)  # Hierarchy level (0=root, 1=child, etc.)
    sort_order: int = Field(default=0)
    is_active: bool = Field(default=True)
    category_image: str = Field(nullable=True)
    seo_url: str = Field(unique=True)  # "smartphones" for SEO-friendly URLs
    meta_title: str = Field(nullable=True)
    meta_description: text = Field(nullable=True)
    commission_rate: decimal = Field(nullable=True)  # Override default commission
    requires_approval: bool = Field(default=False)  # Some categories need approval
    created_by: FK = Field(nullable=True)  # SUPERUSER can create categories
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Dependencias**: Existing ProductCategory ✅
**Specialist**: @backend-senior-developer

### 1.4 Crear ProductReviews System (0.5h)
**Propósito**: Sistema de reviews integrado con User Management

```python
# app/models/product_review.py - NUEVO MODELO
class ProductReview(BaseModel):
    id: int = Field(primary_key=True)
    product_id: FK to Product
    buyer_id: FK to User  # Only buyers can review
    order_id: FK to Order  # Must have purchased to review
    rating: int = Field(ge=1, le=5)  # 1-5 star rating
    review_title: str = Field(max_length=200)
    review_text: text
    is_verified_purchase: bool = Field(default=False)
    helpful_votes: int = Field(default=0)
    reported_count: int = Field(default=0)
    is_approved: bool = Field(default=True)  # SUPERUSER can moderate
    approved_by: FK to User = Field(nullable=True)  # Admin who approved
    review_images: JSON = Field(default=list)  # Array of image URLs
    response_from_vendor: text = Field(nullable=True)  # Vendor can respond
    responded_at: datetime = Field(nullable=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Dependencias**: Product ✅, User ✅, Order models
**Specialist**: @backend-senior-developer

---

## 🔌 BACKEND - APIS & SERVICES (4 horas)

### 1.5 ProductInventory Service (1h)
**Propósito**: Control de inventario con alertas automáticas

```python
# app/services/product_inventory_service.py - NUEVO SERVICIO
class ProductInventoryService:

    def update_stock(self, product_id: int, quantity: int, operation: str):
        """Update stock with automatic alerts"""
        # Compatible con existing inventory logic
        pass

    def check_low_stock_alerts(self, vendor_id: int = None):
        """Check and send low stock alerts"""
        # SUPERUSER gets alerts for ALL vendors
        # Individual vendors get only their alerts
        pass

    def reserve_inventory(self, product_id: int, quantity: int, order_id: int):
        """Reserve inventory for pending orders"""
        # Compatible con existing order system
        pass

    def bulk_update_inventory(self, inventory_updates: List[dict]):
        """SUPERUSER can bulk update ANY vendor's inventory"""
        # Enterprise function for SUPERUSER only
        pass
```

**Dependencias**: Existing inventory logic ✅, Notification service ✅
**Specialist**: @backend-senior-developer

### 1.6 Product APIs Enterprise (3h)
**Propósito**: APIs completas compatibles con sistema de permisos existente

```python
# app/api/v1/endpoints/products.py - EXTENDER ENDPOINTS EXISTENTES

# BUYER ENDPOINTS (existentes - mantener compatibilidad)
@router.get("/products/", response_model=List[ProductResponse])
async def get_products():
    """Public product listing"""
    pass

@router.get("/products/{product_id}", response_model=ProductDetailResponse)
async def get_product_detail(product_id: int):
    """Product detail view"""
    pass

# VENDOR ENDPOINTS (existentes - mantener compatibilidad)
@router.post("/vendor/products/", response_model=ProductResponse)
@require_role([UserType.VENDOR])
async def create_product():
    """Vendor creates their own product"""
    pass

@router.put("/vendor/products/{product_id}", response_model=ProductResponse)
@require_role([UserType.VENDOR])
async def update_vendor_product():
    """Vendor updates their own product"""
    pass

# NUEVOS ENDPOINTS ENTERPRISE - SUPERUSER
@router.get("/superuser/products/all", response_model=List[ProductResponse])
@require_role([UserType.SUPERUSER])
async def get_all_products_superuser():
    """SUPERUSER gets ALL products from ALL vendors"""
    pass

@router.put("/superuser/products/{product_id}", response_model=ProductResponse)
@require_role([UserType.SUPERUSER])
async def update_any_product_superuser():
    """SUPERUSER can edit ANY product from ANY vendor"""
    pass

@router.post("/superuser/products/bulk-update", response_model=BulkUpdateResponse)
@require_role([UserType.SUPERUSER])
async def bulk_update_products():
    """SUPERUSER bulk operations on products"""
    pass

@router.get("/superuser/products/analytics", response_model=ProductAnalyticsResponse)
@require_role([UserType.SUPERUSER])
async def get_product_analytics():
    """SUPERUSER analytics for all products"""
    pass
```

**Dependencias**: Existing API structure ✅, Auth middleware ✅, Permission system ✅
**Specialist**: @backend-senior-developer

---

## ⚛️ FRONTEND - COMPONENTS & INTERFACES (6 horas)

### 1.7 ProductManagementDashboard SUPERUSER (2h)
**Propósito**: Dashboard central para control total de productos

```jsx
// frontend/src/components/superuser/ProductManagementDashboard.tsx
import { useEffect, useState } from 'react';
import { useAuthStore } from '../stores/authStore'; // Compatible con base ✅
import { productService } from '../services/productService'; // Nuevo servicio

const ProductManagementDashboard = () => {
  const { user, hasPermission } = useAuthStore();
  const [products, setProducts] = useState([]);
  const [analytics, setAnalytics] = useState({});
  const [filters, setFilters] = useState({});

  // Verificar permisos SUPERUSER
  if (!hasPermission('product.manage_all')) {
    return <Unauthorized />;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header con métricas globales */}
      <ProductMetricsHeader analytics={analytics} />

      {/* Filtros avanzados */}
      <ProductAdvancedFilters
        filters={filters}
        onFiltersChange={setFilters}
        showVendorFilter={true} // Solo SUPERUSER ve todos los vendors
      />

      {/* Tabla de productos con acciones bulk */}
      <ProductDataTable
        products={products}
        onBulkEdit={handleBulkEdit}
        onBulkDelete={handleBulkDelete}
        onExport={handleExport}
        actions={[
          'edit', 'delete', 'feature', 'promote',
          'change_vendor', 'bulk_price_update'
        ]}
      />

      {/* Modales para acciones */}
      <ProductBulkEditModal />
      <ProductAnalyticsModal />
    </div>
  );
};
```

**Dependencias**: Auth store ✅, Component architecture ✅
**Specialist**: @frontend-react-specialist

### 1.8 ProductCatalogView Vendors (1.5h)
**Propósito**: Vista de catálogo mejorada para vendors

```jsx
// frontend/src/components/vendor/ProductCatalogView.tsx
import { ProductCard, ProductFilters, ProductStats } from '../ui/products';

const ProductCatalogView = () => {
  const { user } = useAuthStore();
  const [vendorProducts, setVendorProducts] = useState([]);

  // Solo productos del vendor actual
  useEffect(() => {
    productService.getVendorProducts(user.id)
      .then(setVendorProducts);
  }, [user.id]);

  return (
    <div className="space-y-6">
      {/* Stats del vendor */}
      <ProductStats
        totalProducts={vendorProducts.length}
        activeProducts={vendorProducts.filter(p => p.is_active).length}
        lowStockCount={vendorProducts.filter(p => p.stock < 5).length}
        avgRating={calculateAvgRating(vendorProducts)}
      />

      {/* Grid de productos */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6">
        {vendorProducts.map(product => (
          <ProductCard
            key={product.id}
            product={product}
            actions={['edit', 'duplicate', 'analytics']}
            onEdit={() => router.push(`/vendor/products/${product.id}/edit`)}
          />
        ))}
      </div>
    </div>
  );
};
```

**Dependencias**: Existing vendor architecture ✅, UI components ✅
**Specialist**: @frontend-react-specialist

### 1.9 ProductSearchEngine Avanzado (1.5h)
**Propósito**: Búsqueda avanzada con filtros inteligentes

```jsx
// frontend/src/components/ui/ProductSearchEngine.tsx
import { useDebounce } from '../hooks/useDebounce';
import { productService } from '../services/productService';

const ProductSearchEngine = ({ onResults, userRole }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({});
  const debouncedSearchTerm = useDebounce(searchTerm, 300);

  const performSearch = async () => {
    const results = await productService.searchProducts({
      query: debouncedSearchTerm,
      filters,
      includeInactive: userRole === 'SUPERUSER' // Solo SUPERUSER ve inactivos
    });
    onResults(results);
  };

  return (
    <div className="bg-white p-4 rounded-lg shadow">
      {/* Barra de búsqueda principal */}
      <div className="relative">
        <SearchIcon className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="Buscar productos, marcas, categorías..."
          className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Filtros avanzados */}
      <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4">
        <CategoryFilter filters={filters} onChange={setFilters} />
        <PriceRangeFilter filters={filters} onChange={setFilters} />
        <BrandFilter filters={filters} onChange={setFilters} />
        {userRole === 'SUPERUSER' && (
          <VendorFilter filters={filters} onChange={setFilters} />
        )}
      </div>
    </div>
  );
};
```

**Dependencias**: UI components ✅, Search service (nuevo)
**Specialist**: @frontend-react-specialist

### 1.10 ProductReviewSystem Integrado (1h)
**Propósito**: Sistema de reviews integrado con el módulo de usuarios

```jsx
// frontend/src/components/ui/ProductReviewSystem.tsx
const ProductReviewSystem = ({ productId, userRole }) => {
  const [reviews, setReviews] = useState([]);
  const [canReview, setCanReview] = useState(false);

  return (
    <div className="space-y-6">
      {/* Summary de reviews */}
      <ReviewSummary
        averageRating={calculateAverage(reviews)}
        totalReviews={reviews.length}
        ratingBreakdown={calculateRatingBreakdown(reviews)}
      />

      {/* Lista de reviews */}
      <div className="space-y-4">
        {reviews.map(review => (
          <ReviewCard
            key={review.id}
            review={review}
            canModerate={userRole === 'SUPERUSER'}
            onApprove={() => reviewService.approveReview(review.id)}
            onReject={() => reviewService.rejectReview(review.id)}
          />
        ))}
      </div>

      {/* Form para escribir review */}
      {canReview && <ReviewForm productId={productId} />}
    </div>
  );
};
```

**Dependencies**: Review service (nuevo), User system ✅
**Specialist**: @frontend-react-specialist

---

## 📊 INTEGRACIÓN CON SISTEMA BASE

### Compatible con TODO_CONFIGURACION_BASE_ENTERPRISE.md:
✅ **Database Architecture**: Usa existing connection y migrations
✅ **Auth System**: Integra con JWT y role system existente
✅ **API Structure**: Sigue convención `/api/v1/` establecida
✅ **Frontend Architecture**: Usa Zustand stores y component structure
✅ **Error Handling**: Compatible con error hierarchy existente
✅ **State Management**: Integra con authStore y uiStore existentes

### APIs que conectan con otros módulos:
- `GET /api/v1/users/{user_id}/products` → Módulo Users
- `POST /api/v1/orders` con product_id → Módulo Orders
- `GET /api/v1/analytics/products` → Módulo Analytics
- `POST /api/v1/notifications/low-stock` → Módulo Notifications

---

## ✅ TESTING & VALIDATION

### Tests Backend:
```python
# tests/unit/services/test_product_inventory_service.py
def test_superuser_can_update_any_vendor_inventory():
    pass

def test_vendor_can_only_update_own_inventory():
    pass

def test_low_stock_alerts_sent_correctly():
    pass
```

### Tests Frontend:
```typescript
// frontend/src/components/__tests__/ProductManagementDashboard.test.tsx
describe('ProductManagementDashboard', () => {
  test('SUPERUSER sees all products', () => {});
  test('Vendor sees only own products', () => {});
  test('Bulk operations work correctly', () => {});
});
```

---

## 🎯 CRITERIOS DE ÉXITO

### Funcionalidades Críticas:
- [ ] SUPERUSER puede gestionar productos de TODOS los vendors
- [ ] Vendors pueden gestionar solo sus propios productos
- [ ] Sistema de inventario con alertas automáticas funcional
- [ ] Reviews integrados con sistema de usuarios
- [ ] Categorías jerárquicas funcionando correctamente
- [ ] Búsqueda avanzada operativa

### Integración Exitosa:
- [ ] APIs respetan sistema de permisos existente
- [ ] Frontend usa stores y components architecture base
- [ ] Database migrations son compatibles con esquema existente
- [ ] No hay conflictos con otros módulos

### Performance:
- [ ] Búsqueda de productos <500ms
- [ ] Dashboard SUPERUSER carga en <2s
- [ ] Bulk operations <10s para 1000+ productos

---

**🔗 MÓDULO COMPATIBLE CON ENTERPRISE BASE**
**📦 SISTEMA DE PRODUCTOS COMPLETO**
**⏱️ 14 HORAS IMPLEMENTACIÓN COORDINADA**