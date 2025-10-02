# 🚨 ALERTA URGENTE - DEPARTAMENTO FRONTEND

**Fecha**: 2025-10-01
**De**: Director Enterprise CEO
**Para**: TODOS los agentes del departamento Frontend
**Prioridad**: CRÍTICA

---

## 📢 DIRECTIVA CEO: ESTANDARIZACIÓN DE CÓDIGO

Se ha emitido una **directiva ejecutiva obligatoria** sobre estandarización de código.

### ⚡ CAMBIOS INMEDIATOS PARA FRONTEND:

#### ❌ PROHIBIDO en código TypeScript/JavaScript:
```typescript
// ❌ Variables/funciones en español
const crearProducto = (datosProducto) => {
  const precioTotal = calcularTotal();
};

// ❌ Archivos en español
src/services/servicioProductos.ts
```

#### ✅ OBLIGATORIO en código:
```typescript
// ✅ Variables/funciones en inglés
const createProduct = (productData) => {
  const totalPrice = calculateTotal();
};

// ✅ Archivos en inglés
src/services/productService.ts
```

#### ✅ MANTENER UI en español (sin cambios):
```typescript
// ✅ CORRECTO - UI en español
<Button>Agregar al Carrito</Button>
<Alert>Producto agregado exitosamente</Alert>
<Title>Mis Productos</Title>
<ErrorMessage>El producto ya existe</ErrorMessage>
```

---

## 🎯 AGENTES FRONTEND CON RESPONSABILIDAD DIRECTA:

### LÍDER DE MIGRACIÓN:
**react-specialist-ai** - Responsable principal migración a nuevas APIs

### OTROS RESPONSABLES:
- **frontend-security-ai** - Validación cambios
- **api-integration-specialist** - Integración APIs
- **ux-specialist-ai** - UX (mantener textos español)
- **state-management-specialist** - Gestión estado

---

## 🔄 MIGRACIÓN DE SERVICIOS API (Semanas 3-5):

### Actualizar llamadas API:
```typescript
// ❌ ANTES (deprecado)
await api.get('/api/v1/productos/');
await api.post('/api/v1/vendedores/registro');

// ✅ DESPUÉS (obligatorio)
await api.get('/api/v1/products/');
await api.post('/api/v1/vendors/register');
```

### Archivos a actualizar:
- `src/services/productService.ts` - Endpoints productos
- `src/services/vendorService.ts` - Endpoints vendedores
- `src/services/commissionService.ts` - Endpoints comisiones
- `src/services/paymentService.ts` - Endpoints pagos

---

## 📝 NUEVO TEMPLATE DE COMMITS:

```
tipo(área): descripción en inglés

Workspace-Check: ✅ Consultado
File: ruta/del/archivo
Agent: [tu-nombre]
Protocol: FOLLOWED
Tests: PASSED
Code-Standard: ✅ ENGLISH_CODE / ✅ SPANISH_UI
API-Duplication: NONE

Description:
[Descripción del cambio]
```

**Campos OBLIGATORIOS**:
- `Code-Standard: ✅ ENGLISH_CODE` (para código)
- `Code-Standard: ✅ SPANISH_UI` (para textos UI)

---

## ✅ ACCIÓN REQUERIDA:

1. **Leer directiva completa**: `.workspace/URGENT_BROADCAST_CEO_CODE_STANDARDIZATION.md`
2. **Confirmar lectura**:
   ```bash
   python .workspace/scripts/confirm_directive_read.py [tu-agente] CEO-CODE-STANDARDS-2025-10-01
   ```
3. **Aplicar desde próximo commit**

---

## 🔗 RECURSOS:

- **Directiva Completa**: `.workspace/URGENT_BROADCAST_CEO_CODE_STANDARDIZATION.md`
- **Resumen Ejecutivo**: `.workspace/EXECUTIVE_SUMMARY_CODE_STANDARDIZATION.md`

---

**Esta directiva es de cumplimiento OBLIGATORIO para todo el departamento Frontend**
