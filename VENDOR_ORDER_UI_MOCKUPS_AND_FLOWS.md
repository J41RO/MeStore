# Vendor Order Management - UI Mockups & User Flows

**Project**: Vendor Order Management System
**Date**: 2025-10-03
**Type**: UX/UI Specifications
**Status**: Design Complete

---

## User Flows

### Flow 1: Vendor Views New Order

```
┌─────────────────────────────────────────────────────────────────┐
│                     VENDOR DASHBOARD                             │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  📊 Órdenes Pendientes: 5                                │  │
│  │  ⚡ Requieren Atención Inmediata                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  [Ver Órdenes] button clicked                                   │
└─────────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│              VENDOR ORDER MANAGEMENT PAGE                        │
│                                                                  │
│  Gestión de Órdenes                                             │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                                  │
│  Filtros: [Estado ▼] [Estado Preparación ▼] [Buscar...] 🔍     │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ 🛍️ Orden #ORD-20251003-ABC123    🟡 PENDIENTE          │    │
│  │                                                         │    │
│  │ Cliente: Juan Pérez                                    │    │
│  │ Email: juan@example.com                                │    │
│  │ Fecha: 03 Oct 2025, 10:30 AM                           │    │
│  │                                                         │    │
│  │ ┌───────────────────────────────────────────────────┐  │    │
│  │ │ 📦 Producto A - SKU: ABC123                       │  │    │
│  │ │ Cantidad: 2 × $50,000 = $100,000                  │  │    │
│  │ │ Estado: ⏳ Pendiente                              │  │    │
│  │ │ [Marcar como Preparando] [Detalles]              │  │    │
│  │ └───────────────────────────────────────────────────┘  │    │
│  │                                                         │    │
│  │ Total tus productos: $100,000 (2 items)                │    │
│  │                                                         │    │
│  │ [Ver Detalles Completos]                               │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ 🛍️ Orden #ORD-20251003-DEF456    🔵 PROCESANDO        │    │
│  │ ... (more orders)                                       │    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### Flow 2: Update Item Status

```
                    USER ACTION
                        ↓
  [Marcar como Preparando] button clicked
                        ↓
        ┌───────────────────────────────┐
        │  Loading spinner + API call   │
        │  POST /vendor/orders/.../status │
        └───────────────────────────────┘
                        ↓
              ┌─────────────────┐
              │  API Response   │
              │  Status: 200 OK │
              └─────────────────┘
                        ↓
        ┌───────────────────────────────┐
        │  ✅ Toast Notification        │
        │  "Estado actualizado a        │
        │   Preparando"                 │
        └───────────────────────────────┘
                        ↓
        ┌───────────────────────────────┐
        │  UI Update                    │
        │  Badge changes:               │
        │  ⏳ Pendiente → ⏱️ Preparando  │
        │                               │
        │  Button changes:              │
        │  [Marcar como Listo]          │
        └───────────────────────────────┘
```

### Flow 3: View Order Details

```
┌─────────────────────────────────────────────────────────────────┐
│                  ORDER DETAIL PAGE                               │
│                                                                  │
│  ← Volver a Órdenes                                             │
│                                                                  │
│  Orden #ORD-20251003-ABC123                   🟡 PENDIENTE      │
│  Creada el 03 Octubre 2025, 10:30 AM                            │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                                  │
│  ┌──────────────────────┐  ┌──────────────────────────────────┐│
│  │ 👤 INFORMACIÓN       │  │ 📦 DIRECCIÓN DE ENVÍO             ││
│  │    DEL CLIENTE       │  │                                   ││
│  │                      │  │ Calle 123 #45-67                  ││
│  │ Juan Pérez           │  │ Bogotá, Cundinamarca              ││
│  │ juan@example.com     │  │ CP: 110111                        ││
│  │ +57 300 1234567      │  │ Colombia                          ││
│  └──────────────────────┘  └──────────────────────────────────┘│
│                                                                  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                                  │
│  TUS PRODUCTOS EN ESTA ORDEN                                    │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ ┌──────┐                                               │    │
│  │ │ IMG  │  Producto A                                   │    │
│  │ │      │  SKU: ABC123                                  │    │
│  │ └──────┘                                               │    │
│  │                                                         │    │
│  │ Cantidad: 2                                            │    │
│  │ Precio Unitario: $50,000                               │    │
│  │ Total: $100,000                                        │    │
│  │                                                         │    │
│  │ Estado de Preparación:                                 │    │
│  │ ┌─────────────────────────────────────────────────┐   │    │
│  │ │ ● Pendiente (Actual)                            │   │    │
│  │ │ ○ Preparando                                    │   │    │
│  │ │ ○ Listo para Envío                              │   │    │
│  │ │ ○ Enviado                                       │   │    │
│  │ └─────────────────────────────────────────────────┘   │    │
│  │                                                         │    │
│  │ [Marcar como Preparando] [Marcar como Listo]          │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ 📊 RESUMEN DE TUS PRODUCTOS                            │    │
│  │                                                         │    │
│  │ Subtotal: $100,000                                     │    │
│  │ Cantidad de Items: 2                                   │    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Mockups

### 1. OrderCard Component

```
┌────────────────────────────────────────────────────────────┐
│ 🛍️ Orden #ORD-20251003-ABC123         🟡 PENDIENTE        │
│                                                             │
│ 👤 Cliente: Juan Pérez                                     │
│ 📧 juan@example.com                                        │
│ 📅 03 Oct 2025, 10:30 AM                                   │
│                                                             │
│ ┌─────────────────────────────────────────────────────┐   │
│ │ 📦 Producto A - SKU: ABC123                         │   │
│ │ 2 × $50,000 = $100,000                              │   │
│ │ ⏳ Pendiente  [Marcar como Preparando ▶]           │   │
│ └─────────────────────────────────────────────────────┘   │
│                                                             │
│ ┌─────────────────────────────────────────────────────┐   │
│ │ 📦 Producto B - SKU: DEF456                         │   │
│ │ 1 × $75,000 = $75,000                               │   │
│ │ ⏱️ Preparando  [Marcar como Listo ▶]               │   │
│ └─────────────────────────────────────────────────────┘   │
│                                                             │
│ ──────────────────────────────────────────────────────────│
│ 📊 Total tus productos: $175,000 (3 items)                 │
│                                                             │
│ [Ver Detalles Completos]                                   │
└────────────────────────────────────────────────────────────┘
```

**Color Coding:**
- 🟡 PENDING (Yellow) - `bg-yellow-100 text-yellow-800`
- 🔵 PROCESSING (Blue) - `bg-blue-100 text-blue-800`
- 🟢 SHIPPED (Green) - `bg-green-100 text-green-800`
- ⚫ DELIVERED (Gray) - `bg-gray-100 text-gray-800`
- 🔴 CANCELLED (Red) - `bg-red-100 text-red-800`

---

### 2. OrderItemCard Component

```
┌─────────────────────────────────────────────────────┐
│ ┌──────┐                                            │
│ │ IMG  │  Producto A - Premium Quality              │
│ │      │  SKU: ABC123                               │
│ └──────┘                                            │
│                                                      │
│ Cantidad: 2 unidades                                │
│ Precio: $50,000 c/u                                 │
│ Total: $100,000                                     │
│                                                      │
│ Estado: ⏳ Pendiente                                │
│                                                      │
│ [Marcar como Preparando]                            │
└─────────────────────────────────────────────────────┘
```

**State Transitions:**
```
⏳ Pendiente
  ↓ [Marcar como Preparando]
⏱️ Preparando
  ↓ [Marcar como Listo]
✅ Listo para Envío
  ↓ [Sistema marca como enviado]
🚚 Enviado
```

---

### 3. PreparationTimeline Component

```
┌─────────────────────────────────────────────────────────────┐
│ LÍNEA DE TIEMPO DE PREPARACIÓN                              │
│                                                               │
│  ●────────●────────○────────○                               │
│  │        │        │        │                                │
│  │        │        │        └─ Enviado                       │
│  │        │        └────────── Listo para Envío             │
│  │        └─────────────────── Preparando                   │
│  └──────────────────────────── Pendiente (actual)           │
│                                                               │
│  03 Oct   [esperando]  [esperando]  [esperando]             │
│  10:30 AM                                                    │
└─────────────────────────────────────────────────────────────┘
```

**Interactive Version (with timestamps):**
```
┌─────────────────────────────────────────────────────────────┐
│  ●────────●────────●────────○                               │
│  │        │        │        │                                │
│  │        │        │        └─ Enviado                       │
│  │        │        └────────── ✅ Listo (03 Oct, 14:30)     │
│  │        └─────────────────── ✅ Preparando (03 Oct, 11:00)│
│  └──────────────────────────── ✅ Pendiente (03 Oct, 10:30) │
└─────────────────────────────────────────────────────────────┘
```

---

### 4. OrderFilters Component

```
┌──────────────────────────────────────────────────────────────┐
│ FILTROS                                                       │
│                                                               │
│ ┌──────────────┐ ┌──────────────────┐ ┌─────────────────┐  │
│ │ Estado Orden │ │ Estado Preparación│ │ Buscar Orden    │  │
│ │ [Todos    ▼] │ │ [Todos         ▼] │ │ [ORD-...]    🔍│  │
│ └──────────────┘ └──────────────────┘ └─────────────────┘  │
│                                                               │
│ ┌────────────┐ ┌────────────┐                               │
│ │ Fecha Desde│ │ Fecha Hasta│                               │
│ │ [📅 Picker]│ │ [📅 Picker]│  [Limpiar Filtros]            │
│ └────────────┘ └────────────┘                               │
└──────────────────────────────────────────────────────────────┘
```

**Filter Options:**

**Estado Orden:**
- Todos
- Pendiente
- Confirmado
- Procesando
- Enviado
- Entregado
- Cancelado

**Estado Preparación:**
- Todos
- Pendiente
- Preparando
- Listo para Envío
- Enviado

---

### 5. StatusUpdateButton Component

```
State: PENDING
┌─────────────────────────────┐
│ ▶ Marcar como Preparando    │ ← Primary button
└─────────────────────────────┘

State: PREPARING
┌─────────────────────────────┐
│ ✓ Marcar como Listo         │ ← Success button
└─────────────────────────────┘

State: READY_TO_SHIP
┌─────────────────────────────┐
│ ⏳ Esperando Envío           │ ← Disabled button (admin action)
└─────────────────────────────┘

State: SHIPPED
┌─────────────────────────────┐
│ ✅ Enviado                  │ ← Success badge (not button)
└─────────────────────────────┘
```

**Button States:**
- **PENDING** → Blue button "Marcar como Preparando"
- **PREPARING** → Green button "Marcar como Listo"
- **READY_TO_SHIP** → Gray disabled "Esperando Envío"
- **SHIPPED** → Green badge "Enviado"

---

### 6. VendorOrderStats Dashboard

```
┌──────────────────────────────────────────────────────────────┐
│ ESTADÍSTICAS DE VENTAS                                        │
│                                                               │
│ Período: [Hoy] [Semana] [Mes ✓] [Personalizado]             │
│                                                               │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐         │
│ │ 💰 VENTAS    │ │ 📦 ÓRDENES   │ │ ⏳ PENDIENTES │         │
│ │              │ │              │ │              │         │
│ │ $2,450,000   │ │     23       │ │      5       │         │
│ │ ↑ 15%        │ │ ↑ 8%         │ │ ↓ 2          │         │
│ └──────────────┘ └──────────────┘ └──────────────┘         │
│                                                               │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐         │
│ │ 📊 ITEMS     │ │ ✅ LISTOS    │ │ 💵 PROMEDIO  │         │
│ │              │ │              │ │              │         │
│ │     67       │ │     45       │ │  $106,521    │         │
│ │ ↑ 12%        │ │ ↑ 20%        │ │ ↑ 7%         │         │
│ └──────────────┘ └──────────────┘ └──────────────┘         │
│                                                               │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                               │
│ TOP PRODUCTOS DEL MES                                        │
│                                                               │
│ ┌────────────────────────────────────────────────────────┐  │
│ │ 1️⃣ Producto A - SKU: ABC123                            │  │
│ │    23 unidades vendidas | $1,150,000                    │  │
│ │    ████████████████░░░░░░░░░░ 47%                      │  │
│ └────────────────────────────────────────────────────────┘  │
│                                                               │
│ ┌────────────────────────────────────────────────────────┐  │
│ │ 2️⃣ Producto B - SKU: DEF456                            │  │
│ │    15 unidades vendidas | $750,000                      │  │
│ │    ███████████░░░░░░░░░░░░░░░ 31%                      │  │
│ └────────────────────────────────────────────────────────┘  │
│                                                               │
│ ┌────────────────────────────────────────────────────────┐  │
│ │ 3️⃣ Producto C - SKU: GHI789                            │  │
│ │    10 unidades vendidas | $550,000                      │  │
│ │    ███████░░░░░░░░░░░░░░░░░░░ 22%                      │  │
│ └────────────────────────────────────────────────────────┘  │
│                                                               │
│ [Ver Reporte Completo] [Exportar PDF]                       │
└──────────────────────────────────────────────────────────────┘
```

---

## Mobile Responsive Views

### Mobile: Order List (< 640px)

```
┌───────────────────────┐
│ ☰  Gestión de Órdenes │
│                        │
│ Filtros: [Expandir ▼] │
│                        │
│ ┌────────────────────┐│
│ │ 🛍️ #ORD-...ABC123 ││
│ │ 🟡 PENDIENTE       ││
│ │                    ││
│ │ Juan Pérez         ││
│ │ 03 Oct, 10:30      ││
│ │                    ││
│ │ 📦 2 productos     ││
│ │ 💰 $175,000        ││
│ │                    ││
│ │ ⏳ 1 Pendiente     ││
│ │ ⏱️ 1 Preparando    ││
│ │                    ││
│ │ [Ver Detalles]     ││
│ └────────────────────┘│
│                        │
│ ┌────────────────────┐│
│ │ 🛍️ #ORD-...DEF456 ││
│ │ ... (next order)   ││
│ └────────────────────┘│
│                        │
│ [Cargar Más]           │
└───────────────────────┘
```

### Mobile: Order Detail

```
┌───────────────────────┐
│ ← Orden #ORD-...ABC123│
│ 🟡 PENDIENTE          │
│                        │
│ ━━━━━━━━━━━━━━━━━━━━ │
│                        │
│ 👤 CLIENTE            │
│ Juan Pérez            │
│ juan@example.com      │
│ +57 300 1234567       │
│                        │
│ ━━━━━━━━━━━━━━━━━━━━ │
│                        │
│ 📦 ENVÍO              │
│ Calle 123 #45-67      │
│ Bogotá, Cundinamarca  │
│ CP: 110111            │
│                        │
│ ━━━━━━━━━━━━━━━━━━━━ │
│                        │
│ TUS PRODUCTOS         │
│                        │
│ ┌──────────────────┐  │
│ │ [IMG]            │  │
│ │ Producto A       │  │
│ │ SKU: ABC123      │  │
│ │                  │  │
│ │ 2 × $50,000      │  │
│ │ = $100,000       │  │
│ │                  │  │
│ │ ⏳ Pendiente     │  │
│ │                  │  │
│ │ [Preparando ▶]   │  │
│ └──────────────────┘  │
│                        │
│ ━━━━━━━━━━━━━━━━━━━━ │
│                        │
│ Total: $175,000       │
│ 3 items               │
└───────────────────────┘
```

### Touch Actions (Swipe Gestures)

```
Order Card:
← Swipe Left: Quick "Mark Preparing"
→ Swipe Right: View Details

Item Card:
← Swipe Left: Next Status
→ Swipe Right: Previous Page

Pull Down: Refresh List
```

---

## Color Palette

### Order Status Colors

```css
/* Pending */
.status-pending {
  background: #FEF3C7; /* yellow-100 */
  color: #92400E;      /* yellow-800 */
  border: #FDE047;     /* yellow-300 */
}

/* Confirmed */
.status-confirmed {
  background: #DBEAFE; /* blue-100 */
  color: #1E3A8A;      /* blue-800 */
  border: #60A5FA;     /* blue-300 */
}

/* Processing */
.status-processing {
  background: #E0E7FF; /* indigo-100 */
  color: #3730A3;      /* indigo-800 */
  border: #818CF8;     /* indigo-300 */
}

/* Shipped */
.status-shipped {
  background: #D1FAE5; /* green-100 */
  color: #065F46;      /* green-800 */
  border: #34D399;     /* green-300 */
}

/* Delivered */
.status-delivered {
  background: #F3F4F6; /* gray-100 */
  color: #1F2937;      /* gray-800 */
  border: #9CA3AF;     /* gray-300 */
}

/* Cancelled */
.status-cancelled {
  background: #FEE2E2; /* red-100 */
  color: #991B1B;      /* red-800 */
  border: #F87171;     /* red-300 */
}
```

### Preparation Status Colors

```css
/* Pending */
.prep-pending {
  background: #FEF3C7;
  color: #92400E;
}

/* Preparing */
.prep-preparing {
  background: #DBEAFE;
  color: #1E3A8A;
}

/* Ready to Ship */
.prep-ready {
  background: #D1FAE5;
  color: #065F46;
}

/* Shipped */
.prep-shipped {
  background: #F3F4F6;
  color: #1F2937;
}
```

---

## Accessibility Features

### Keyboard Navigation

```
Tab Navigation Order:
1. Filter controls
2. Search input
3. Order cards
4. Action buttons
5. Pagination

Keyboard Shortcuts:
- Enter: Open selected order
- Space: Toggle status update
- Esc: Close modal/detail
- ← →: Navigate between orders
- ↑ ↓: Navigate items within order
```

### Screen Reader Support

```html
<!-- Order Card -->
<article
  role="article"
  aria-label="Order ORD-20251003-ABC123 from Juan Pérez, status pending"
>
  <h3>Order #ORD-20251003-ABC123</h3>
  <span aria-label="Order status: pending" class="status-badge">
    Pendiente
  </span>

  <!-- Status Button -->
  <button
    aria-label="Mark item as preparing"
    aria-describedby="item-description"
  >
    Marcar como Preparando
  </button>
</article>
```

### Focus Management

```
Focus Indicators:
- Ring: 2px solid blue
- Offset: 2px
- Radius: matches element

Focus Trap:
- Modal dialogs trap focus
- Escape closes and returns focus
- Tab cycles within modal
```

---

## Animation & Transitions

### Status Change Animation

```css
/* Button Click */
.status-button:active {
  transform: scale(0.95);
  transition: transform 0.1s ease;
}

/* Status Badge Update */
@keyframes statusChange {
  0% { opacity: 0; transform: scale(0.9); }
  50% { transform: scale(1.05); }
  100% { opacity: 1; transform: scale(1); }
}

.status-badge.updated {
  animation: statusChange 0.3s ease;
}

/* Loading State */
.status-button.loading {
  position: relative;
  color: transparent;
}

.status-button.loading::after {
  content: "";
  position: absolute;
  width: 16px;
  height: 16px;
  border: 2px solid #fff;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
```

### List Updates

```css
/* New Order Appears */
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.order-card.new {
  animation: slideIn 0.4s ease;
}

/* Order Removed */
@keyframes slideOut {
  to {
    opacity: 0;
    transform: translateX(-100%);
  }
}

.order-card.removed {
  animation: slideOut 0.3s ease forwards;
}
```

---

## Error States

### Network Error

```
┌────────────────────────────────────────────┐
│ ⚠️ Error de Conexión                       │
│                                             │
│ No se pudo cargar las órdenes.             │
│ Por favor verifica tu conexión a internet. │
│                                             │
│ [Reintentar] [Ver Caché]                   │
└────────────────────────────────────────────┘
```

### Update Failed

```
┌────────────────────────────────────────────┐
│ ❌ Error al Actualizar Estado              │
│                                             │
│ No se pudo actualizar el estado del item.  │
│ Error: Network timeout                     │
│                                             │
│ [Reintentar] [Cancelar]                    │
└────────────────────────────────────────────┘
```

### Empty State

```
┌────────────────────────────────────────────┐
│          📭                                 │
│                                             │
│    No hay órdenes para mostrar             │
│                                             │
│ Cuando recibas órdenes con tus productos,  │
│ aparecerán aquí.                           │
│                                             │
│ [Actualizar] [Ver Productos]               │
└────────────────────────────────────────────┘
```

---

## Notification Toasts

### Success

```
┌────────────────────────────────┐
│ ✅ Estado actualizado           │
│ El item está ahora "Preparando" │
│                                 │
│ [×] Auto-close in 3s            │
└────────────────────────────────┘
```

### Warning

```
┌────────────────────────────────┐
│ ⚠️ Conexión lenta               │
│ La actualización puede tardar   │
│                                 │
│ [×] Auto-close in 5s            │
└────────────────────────────────┘
```

### Error

```
┌────────────────────────────────┐
│ ❌ Error al actualizar          │
│ Inténtalo de nuevo              │
│                                 │
│ [Reintentar] [×]                │
└────────────────────────────────┘
```

---

## Loading States

### Skeleton Loader

```
┌────────────────────────────────────┐
│ ▓▓▓▓▓▓▓▓▓▓▓▓   ▓▓▓▓▓▓▓            │
│                                     │
│ ▓▓▓▓▓▓▓▓▓                          │
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓                    │
│                                     │
│ ┌─────────────────────────────┐   │
│ │ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓           │   │
│ │ ▓▓▓▓▓▓▓▓ ▓▓▓▓▓▓▓            │   │
│ └─────────────────────────────┘   │
│                                     │
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓  ▓▓▓▓▓▓▓           │
│                                     │
│ [▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓]                  │
└────────────────────────────────────┘
```

### Spinner

```
┌────────────────────┐
│                     │
│        ⟳           │
│   Cargando...      │
│                     │
└────────────────────┘
```

---

## Responsive Breakpoints

```css
/* Mobile First Approach */

/* Mobile (default) */
.order-grid {
  grid-template-columns: 1fr;
  gap: 1rem;
}

/* Tablet */
@media (min-width: 640px) {
  .order-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 1.5rem;
  }
}

/* Desktop */
@media (min-width: 1024px) {
  .order-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 2rem;
  }
}

/* Large Desktop */
@media (min-width: 1280px) {
  .order-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}
```

---

**Document Version**: 1.0
**Created**: 2025-10-03
**Status**: Design Complete

