# VENDOR MANAGEMENT DASHBOARD - VISUAL SUMMARY

## Component Structure

```
┌─────────────────────────────────────────────────────────────────────┐
│                         VendorManagement                              │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                         HEADER                                │   │
│  │  [Building Icon] Gestión de Vendedores Pendientes            │   │
│  │  Aprobar o rechazar solicitudes de registro de vendedores    │   │
│  │  [Gradient: Orange → Purple]                                  │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    VENDOR TABLE                               │   │
│  │  ┌──────────┬──────────┬─────────┬──────────┬──────────┐   │   │
│  │  │ Vendedor │   Tipo   │ Estado  │ Registro │ Acciones │   │   │
│  │  ├──────────┼──────────┼─────────┼──────────┼──────────┤   │   │
│  │  │ [Avatar] │ [Badge]  │ [Badge] │ [Date]   │ [Btns]   │   │   │
│  │  │ Name     │ Natural  │ DRAFT   │ Oct 12   │ ✓  ✗     │   │   │
│  │  │ email    │ CC: xxx  │         │ Location │          │   │   │
│  │  │ phone    │          │         │          │          │   │   │
│  │  ├──────────┼──────────┼─────────┼──────────┼──────────┤   │   │
│  │  │ [Avatar] │ [Badge]  │ [Badge] │ [Date]   │ [Btns]   │   │   │
│  │  │ Name     │ Jurídica │ PENDING │ Oct 11   │ ✓  ✗     │   │   │
│  │  │ email    │ NIT: xxx │         │ Location │          │   │   │
│  │  │ phone    │          │         │          │          │   │   │
│  │  └──────────┴──────────┴─────────┴──────────┴──────────┘   │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

## Modal Structures

### Approve Modal

```
┌─────────────────────────────────────────────────────────┐
│                  APPROVE MODAL                          │
│                                                         │
│  [✓ Green Circle Icon]                                 │
│  Aprobar Vendedor                                      │
│                                                         │
│  ¿Confirmas que quieres aprobar a Juan Pérez?         │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │ Email: juan@example.com                         │  │
│  │ Tipo: Persona Natural                           │  │
│  │ Cédula: 1234567890                              │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  [Cancelar]              [Aprobar]                     │
│  (gray btn)              (green btn)                   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Reject Modal

```
┌─────────────────────────────────────────────────────────┐
│                  REJECT MODAL                           │
│                                                         │
│  [✗ Red Circle Icon]                                   │
│  Rechazar Vendedor                                     │
│                                                         │
│  Proporciona una razón para rechazar a Juan Pérez     │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │ Razón del rechazo (mínimo 20 caracteres) *     │  │
│  │ ┌─────────────────────────────────────────────┐ │  │
│  │ │ La documentación proporcionada no cumple... │ │  │
│  │ │                                             │ │  │
│  │ │                                             │ │  │
│  │ └─────────────────────────────────────────────┘ │  │
│  │ 45 / 500 caracteres            [✓ Válido]      │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
│  [Cancelar]              [Rechazar]                    │
│  (gray btn)              (red btn)                     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Toast Notification

```
                                              ┌──────────────────────────┐
                                              │ [✓] Vendedor aprobado   │
                                              │     exitosamente         │
                                              └──────────────────────────┘
                                              (slides in from right)
                                              (auto-dismiss after 5s)
```

## State Diagram

```
┌─────────────┐
│   LOADING   │ ──────────► fetch vendors
└─────────────┘
       │
       ▼
┌─────────────┐
│   LOADED    │ ──────────► display table
└─────────────┘
       │
       ├──► Click "Aprobar" ──────► Show Approve Modal
       │                                    │
       │                                    ▼
       │                              [Confirm] ──────► API Call
       │                                    │
       │                                    ▼
       │                              Success Toast
       │                                    │
       │                                    ▼
       │                              Refresh List
       │
       └──► Click "Rechazar" ──────► Show Reject Modal
                                            │
                                            ▼
                                      Enter Reason (20+ chars)
                                            │
                                            ▼
                                      [Confirm] ──────► API Call
                                            │
                                            ▼
                                      Success Toast
                                            │
                                            ▼
                                      Refresh List
```

## Color Palette

### Primary Colors
```
Orange (Start):  #f97316  ████
Purple (End):    #9333ea  ████
```

### Status Colors
```
Success (Green): #10b981  ████
Error (Red):     #ef4444  ████
Warning (Yellow):#f59e0b  ████
Info (Blue):     #3b82f6  ████
```

### Neutral Colors
```
Gray 50:         #f9fafb  ████
Gray 100:        #f3f4f6  ████
Gray 500:        #6b7280  ████
Gray 900:        #111827  ████
```

## Icon Legend

```
✓ CheckCircle    - Success, Approve action
✗ XCircle        - Error, Reject action
⏰ Clock          - Pending status
👤 User           - Natural person
🏢 Building       - Juridical entity
📧 Mail           - Email contact
📱 Phone          - Phone contact
📍 MapPin         - Location/Address
📅 Calendar       - Date/Time
⚠️ AlertCircle   - Error message
⏳ Loader2        - Loading spinner
```

## Responsive Breakpoints

```
Mobile (<768px)
├── Stack table vertically
├── Full-width modals
├── Touch-optimized buttons (min 44x44px)
└── Horizontal scroll on table

Tablet (768px - 1024px)
├── Condensed table layout
├── Medium-width modals
└── Side-by-side buttons

Desktop (>1024px)
├── Full table layout
├── Spacious padding
└── All features visible
```

## Animation Timeline

```
Toast Notification:
0ms ─────► slide-in-right starts
300ms ────► fully visible
5000ms ───► auto-dismiss starts
5300ms ───► fully hidden

Modal:
0ms ─────► backdrop fade-in starts
0ms ─────► scale-in starts
200ms ────► fully visible
(on close)
0ms ─────► scale-out starts
200ms ────► fully hidden
```

## Data Flow

```
Component Mount
     │
     ▼
useEffect ──────► fetchVendors()
     │                  │
     │                  ▼
     │            GET /api/v1/auth/admin/pending-sellers
     │                  │
     │                  ├──► Success ──────► setVendors(data)
     │                  │                          │
     │                  │                          ▼
     │                  │                    Render Table
     │                  │
     │                  └──► Error ────────► setError(message)
     │                                            │
     │                                            ▼
     │                                      Show Error State
     │
     ▼
User Action (Approve)
     │
     ▼
handleApprove() ──► POST /api/v1/auth/admin/approve-seller/{id}
     │                  │
     │                  ├──► Success ──────► showToast("success")
     │                  │                          │
     │                  │                          ▼
     │                  │                    fetchVendors() (refresh)
     │                  │
     │                  └──► Error ────────► showToast("error")
     │
     ▼
User Action (Reject)
     │
     ▼
handleReject() ─────► Validate reason (>=20 chars)
     │                  │
     │                  ├──► Valid ────────► POST /api/v1/auth/admin/reject-seller/{id}
     │                  │                          │
     │                  │                          ├──► Success ──► showToast("success")
     │                  │                          │                      │
     │                  │                          │                      ▼
     │                  │                          │                fetchVendors()
     │                  │                          │
     │                  │                          └──► Error ────► showToast("error")
     │                  │
     │                  └──► Invalid ──────► setRejectError(message)
     │
     ▼
```

## Component Hierarchy

```
VendorManagement
├── Header (Gradient background)
│   ├── Icon (Building)
│   ├── Title
│   └── Description
│
├── Toast Notification (conditional)
│   ├── Icon (CheckCircle or XCircle)
│   └── Message
│
├── Main Content
│   ├── Loading State (conditional)
│   │   ├── Spinner (Loader2)
│   │   └── Text
│   │
│   ├── Error State (conditional)
│   │   ├── Icon (AlertCircle)
│   │   └── Error Message
│   │
│   ├── Empty State (conditional)
│   │   ├── Icon (Clock)
│   │   ├── Title
│   │   └── Description
│   │
│   └── Vendor Table (conditional)
│       ├── Header
│       │   └── Column Headers (5)
│       │
│       └── Body
│           └── Vendor Rows (map)
│               ├── Avatar + Info
│               ├── Type Badge
│               ├── Status Badge
│               ├── Date + Location
│               └── Action Buttons
│                   ├── Approve
│                   └── Reject
│
├── Approve Modal (conditional)
│   ├── Backdrop (overlay)
│   └── Modal Content
│       ├── Icon Header
│       ├── Title
│       ├── Description
│       ├── Vendor Summary
│       └── Action Buttons
│           ├── Cancel
│           └── Approve
│
└── Reject Modal (conditional)
    ├── Backdrop (overlay)
    └── Modal Content
        ├── Icon Header
        ├── Title
        ├── Description
        ├── Reason Textarea
        │   └── Character Counter
        └── Action Buttons
            ├── Cancel
            └── Reject
```

## Performance Metrics

```
Initial Load Time: <2s
API Response Time: <500ms
Modal Open Time: 200ms
Toast Display Time: 5s
Re-render Optimization: Minimal (only affected components)
```

## Accessibility Features

```
✓ Semantic HTML
✓ ARIA labels on buttons
✓ Keyboard navigation (Tab, Enter, Escape)
✓ Focus management in modals
✓ Screen reader friendly
✓ Color contrast (WCAG AA)
✓ Touch targets (min 44x44px)
✓ Error announcements
```

---

**Visual Summary Created**: 2025-10-13
**Component**: VendorManagement.tsx
**Status**: COMPLETE ✅
