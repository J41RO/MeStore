# 🛡️ ESTRATEGIA SEGURA DE MIGRACIÓN DE APIs

**Fecha:** 2025-10-01
**Status:** ⚠️ MIGRACIÓN REQUERIDA ANTES DE ELIMINAR ENDPOINTS

---

## 🚨 PROBLEMA IDENTIFICADO

**El frontend está usando activamente las APIs en español:**

```typescript
// ❌ ACTUAL - EN USO ACTIVO
services/api.ts:
  - create: '/api/v1/productos'
  - update: '/api/v1/productos/${id}'
  - getWithFilters: '/api/v1/productos'

services/productImageService.ts:
  - baseURL: '/api/v1/productos'

services/productValidationService.ts:
  - baseURL: '/api/v1/productos'
```

**Si eliminas los endpoints en español AHORA:**
- ❌ El frontend se romperá completamente
- ❌ No podrás crear/editar productos
- ❌ Upload de imágenes fallará
- ❌ Validaciones fallarán
- ❌ 67+ llamadas API fallarán

---

## ✅ ESTRATEGIA DE MIGRACIÓN SEGURA (SIN DOWNTIME)

### **FASE 1: Backend - Mantener Compatibilidad (1 día)**

#### Opción A: Alias Transparente (RECOMENDADA)

Mantener ambos endpoints funcionando durante la migración:

```python
# app/api/v1/endpoints/productos.py
from app.api.v1.endpoints.products import router as products_router

@router.get("/")
async def list_productos_deprecated(
    *args, **kwargs
) -> Any:
    """
    ⚠️ DEPRECATED: Use /api/v1/products/ instead

    This endpoint will be removed in version 2.0.0
    Migrate to: GET /api/v1/products/
    """
    logger.warning(
        "DEPRECATED endpoint /api/v1/productos/ called. "
        "Migrate to /api/v1/products/"
    )
    # Redirigir internamente a la versión en inglés
    return await products_router.list_products(*args, **kwargs)
```

**Ventajas:**
- ✅ Cero downtime
- ✅ Frontend sigue funcionando
- ✅ Puedes migrar gradualmente
- ✅ Logs para tracking de uso

---

### **FASE 2: Frontend - Migración Archivo por Archivo (1 semana)**

#### Archivos Críticos a Migrar:

**1. services/api.ts** (Principal)
```typescript
// ANTES
products: {
  create: (data: any) => baseApi.post('/api/v1/productos', data),
  update: (id: string, data: any) => baseApi.put(`/api/v1/productos/${id}`, data),
  getWithFilters: (filters: any) => baseApi.get('/api/v1/productos', { params: filters }),
}

// DESPUÉS ✅
products: {
  create: (data: any) => baseApi.post('/api/v1/products', data),
  update: (id: string, data: any) => baseApi.put(`/api/v1/products/${id}`, data),
  getWithFilters: (filters: any) => baseApi.get('/api/v1/products', { params: filters }),
}
```

**2. services/productImageService.ts**
```typescript
// ANTES
private baseURL = 'http://192.168.1.137:8000/api/v1/productos';

// DESPUÉS ✅
private baseURL = 'http://192.168.1.137:8000/api/v1/products';
```

**3. services/productValidationService.ts**
```typescript
// ANTES
private baseURL = '/api/v1/productos';

// DESPUÉS ✅
private baseURL = '/api/v1/products';
```

**Lista Completa de Archivos a Migrar:**
```bash
✅ services/api.ts                           (CRÍTICO)
✅ services/productImageService.ts           (CRÍTICO)
✅ services/productValidationService.ts      (CRÍTICO)
□ components/forms/ProductForm.tsx
□ components/vendor/ProductForm.tsx
□ pages/admin/ProductApprovalPage.tsx
□ hooks/useDashboardMetrics.ts
□ hooks/useVendorRegistration.ts
□ components/admin/VendorDetail.tsx
□ pages/CategoryPage.tsx
□ pages/ProductDetail.tsx
□ pages/MarketplaceSearch.tsx
□ services/api_vendor.ts
□ services/exportService.ts
□ components/payout/PayoutHistoryTable.tsx
□ components/dashboard/ComparativeDashboard.tsx
```

---

### **FASE 3: Testing Exhaustivo (3 días)**

#### Checklist de Testing:

**Funcionalidades Productos:**
- [ ] Listar productos
- [ ] Crear producto nuevo
- [ ] Editar producto existente
- [ ] Eliminar producto
- [ ] Upload de imágenes
- [ ] Eliminar imágenes
- [ ] Aprobar producto (admin)
- [ ] Rechazar producto (admin)
- [ ] Validación de producto

**Funcionalidades Vendedores:**
- [ ] Registro vendedor
- [ ] Login vendedor
- [ ] Ver perfil
- [ ] Editar perfil
- [ ] Dashboard vendedor
- [ ] Listar productos del vendedor

**Funcionalidades Comisiones:**
- [ ] Ver comisiones
- [ ] Solicitar pago
- [ ] Historial de pagos

**Funcionalidades Pagos:**
- [ ] Historial de pagos
- [ ] Ver detalle de pago

---

### **FASE 4: Monitoring y Validación (1 semana)**

**Verificar que NADIE usa los endpoints deprecated:**

```bash
# Buscar en logs del backend
grep "DEPRECATED endpoint" logs/mestocker.log

# Si durante 1 semana no hay llamadas, es seguro eliminar
```

**Dashboard de Monitoring:**
```python
# Agregar métricas
deprecated_endpoint_calls = Counter(
    'deprecated_api_calls_total',
    'Total calls to deprecated Spanish endpoints',
    ['endpoint']
)

# En cada endpoint deprecated
deprecated_endpoint_calls.labels(endpoint='/productos').inc()
```

---

### **FASE 5: Eliminación Segura (1 día)**

**Solo después de confirmar CERO uso durante 1 semana:**

```bash
# 1. Backup de archivos
cp app/api/v1/endpoints/productos.py app/api/v1/endpoints/.backup/productos.py.backup

# 2. Eliminar archivos
rm app/api/v1/endpoints/productos.py
rm app/api/v1/endpoints/vendedores.py
rm app/api/v1/endpoints/comisiones.py
rm app/api/v1/endpoints/pagos.py

# 3. Actualizar routers
# Remover imports en app/api/v1/__init__.py

# 4. Commit
git add -A
git commit -m "refactor(api): remove deprecated Spanish endpoints

- Removed /api/v1/productos (use /products)
- Removed /api/v1/vendedores (use /vendors)
- Removed /api/v1/comisiones (use /commissions)
- Removed /api/v1/pagos (use /payments)

All frontend migrated to English endpoints.
Zero deprecated endpoint calls for 1 week confirmed.

BREAKING CHANGE: Spanish API endpoints removed"
```

---

## 📊 CRONOGRAMA DETALLADO

| Fase | Duración | Días | Actividades | Riesgo |
|------|----------|------|-------------|--------|
| **1. Backend Alias** | 1 día | 1 | Agregar deprecation warnings | 🟢 Bajo |
| **2. Frontend Migration** | 1 semana | 5-7 | Migrar 17 archivos | 🟡 Medio |
| **3. Testing** | 3 días | 3 | Testing exhaustivo | 🟡 Medio |
| **4. Monitoring** | 1 semana | 7 | Verificar cero uso deprecated | 🟢 Bajo |
| **5. Cleanup** | 1 día | 1 | Eliminar endpoints español | 🟢 Bajo |

**Total:** ~3 semanas (17-19 días)

---

## 🎯 PLAN DE EJECUCIÓN PASO A PASO

### **DÍA 1: Backend Preparation**

```bash
# 1. Crear branch
git checkout -b feature/api-migration-to-english

# 2. Modificar productos.py para agregar deprecation
# 3. Modificar vendedores.py para agregar deprecation
# 4. Modificar comisiones.py para agregar deprecation
# 5. Modificar pagos.py para agregar deprecation

# 6. Testing local
pytest tests/api/

# 7. Deploy a desarrollo
# 8. Verificar que todo funciona igual
```

### **DÍA 2-8: Frontend Migration**

```bash
# Día 2: Servicios Core
- services/api.ts
- services/productImageService.ts
- services/productValidationService.ts

# Día 3-4: Components
- components/forms/ProductForm.tsx
- components/vendor/ProductForm.tsx
- pages/admin/ProductApprovalPage.tsx

# Día 5-6: Hooks y Pages
- hooks/useDashboardMetrics.ts
- hooks/useVendorRegistration.ts
- pages/CategoryPage.tsx
- pages/ProductDetail.tsx
- pages/MarketplaceSearch.tsx

# Día 7-8: Resto de archivos
- components/admin/VendorDetail.tsx
- services/api_vendor.ts
- services/exportService.ts
- components/payout/PayoutHistoryTable.tsx
- components/dashboard/ComparativeDashboard.tsx

# Testing después de cada migración
npm run test
npm run build
```

### **DÍA 9-11: Testing Exhaustivo**

```bash
# Testing manual de todas las funcionalidades
# Testing E2E con Playwright/Cypress
# Testing de regresión
# Performance testing
```

### **DÍA 12-18: Monitoring**

```bash
# Monitorear logs diariamente
# Verificar métricas de uso
# Confirmar cero llamadas a deprecated endpoints
```

### **DÍA 19: Cleanup**

```bash
# Eliminar archivos deprecated
# Actualizar documentación
# Merge a main
# Deploy a producción
```

---

## ⚠️ RIESGOS Y MITIGACIONES

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| **Breaking frontend** | Media | Alto | Mantener alias, testing exhaustivo |
| **API externa usando endpoints** | Baja | Alto | Monitoring 1 semana antes de eliminar |
| **Tests fallidos** | Media | Medio | Actualizar tests junto con código |
| **Rollback necesario** | Baja | Alto | Feature flags, deploy gradual |

---

## 🚀 QUICK START - COMENZAR HOY

### **Script Automático para Migración Frontend:**

```bash
#!/bin/bash
# migrate_apis_to_english.sh

echo "🔄 Migrando APIs de español a inglés..."

# Backup
mkdir -p .backups/api-migration-$(date +%Y%m%d)
cp -r frontend/src .backups/api-migration-$(date +%Y%m%d)/

# Migración automática
cd frontend/src

# Productos → Products
find . -type f \( -name "*.ts" -o -name "*.tsx" \) -exec sed -i 's|/api/v1/productos|/api/v1/products|g' {} +

# Vendedores → Vendors
find . -type f \( -name "*.ts" -o -name "*.tsx" \) -exec sed -i 's|/api/v1/vendedores|/api/v1/vendors|g' {} +

# Comisiones → Commissions
find . -type f \( -name "*.ts" -o -name "*.tsx" \) -exec sed -i 's|/api/v1/comisiones|/api/v1/commissions|g' {} +

# Pagos → Payments
find . -type f \( -name "*.ts" -o -name "*.tsx" \) -exec sed -i 's|/api/v1/pagos|/api/v1/payments|g' {} +

echo "✅ Migración completada"
echo "⚠️  IMPORTANTE: Revisar cambios y hacer testing exhaustivo"

# Mostrar archivos modificados
git diff --name-only
```

**Ejecutar:**
```bash
chmod +x migrate_apis_to_english.sh
./migrate_apis_to_english.sh
```

---

## 📝 CHECKLIST FINAL

Antes de eliminar endpoints español, verificar:

- [ ] Todos los archivos frontend migrados
- [ ] Tests pasando al 100%
- [ ] Build de producción exitoso
- [ ] No hay referencias a endpoints español en código
- [ ] Logs muestran cero llamadas deprecated por 7 días
- [ ] Documentación actualizada
- [ ] Team notificado
- [ ] Rollback plan preparado
- [ ] Backup de archivos deprecated creado

---

## 🆘 PLAN DE ROLLBACK

Si algo sale mal:

```bash
# 1. Restaurar archivos desde backup
cp .backups/api-migration-YYYYMMDD/frontend/src/* frontend/src/

# 2. Revertir commits
git revert HEAD~3..HEAD

# 3. Redeploy versión anterior
git checkout <commit-anterior>
./deploy.sh

# 4. Notificar al equipo
```

---

## 💡 RECOMENDACIÓN FINAL

**NO ELIMINES LAS APIs EN ESPAÑOL TODAVÍA.**

Sigue este plan de 3 semanas para una migración segura y sin riesgo:

1. **Semana 1:** Backend alias + Frontend migration
2. **Semana 2:** Testing + Monitoring
3. **Semana 3:** Cleanup seguro

De esta forma:
- ✅ Cero downtime
- ✅ Cero breaking changes
- ✅ Migración gradual y controlada
- ✅ Puedes revertir en cualquier momento

**Next step:** Ejecutar el script de migración frontend y empezar el testing.
