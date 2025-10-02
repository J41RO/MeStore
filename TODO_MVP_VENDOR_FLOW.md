# TODO MVP - FLUJO DE VENDEDORES (VENDOR FLOW)

## 🎯 OBJETIVO MVP
Permitir que 10-20 vendedores puedan registrarse, listar productos, recibir órdenes, ver sus ganancias, y solicitar pagos en **2-3 semanas**.

**Filosofía**: Construir lo MÍNIMO necesario para validar el modelo de negocio con vendedores reales.

---

# 📋 SCOPE MVP

## ✅ QUÉ SÍ INCLUYE (MUST-HAVE)
- Registro de vendedor (single-page form)
- Dashboard con 4 métricas clave
- Gestión básica de productos (mejorar existente)
- Lista de órdenes recibidas
- Vista de comisiones y solicitud de pago

## ❌ QUÉ NO INCLUYE (POST-MVP)
- Multi-step registration con verificación OCR
- Analytics avanzado con gráficos
- Marketing automation
- AI-powered forecasting
- Customer journey mapping
- Predictive analytics

---

# 🚀 BACKEND - VENDOR CORE APIs

## 5.1 Vendor Registration (SIMPLE)
**Prioridad**: P0 🔥 | **Tiempo**: 1-2 días | **Agente**: `backend-framework-ai`

### 5.1.1 Single-Page Registration Endpoint
- [ ] **Task**: Crear endpoint `POST /api/v1/vendors/register`
  ```python
  Request Body:
  {
    "email": "maria@ejemplo.com",
    "password": "SecurePass123!",
    "full_name": "María González",
    "phone": "+573001234567",
    "business_name": "MaríaStyle",
    "city": "Bucaramanga",
    "business_type": "persona_natural", # o "empresa"
    "primary_category": "ropa_femenina",
    "terms_accepted": true
  }

  Response:
  {
    "vendor_id": "uuid",
    "email": "maria@ejemplo.com",
    "status": "active", # Auto-aprobado para MVP
    "message": "Registro exitoso. Bienvenida a MeStocker!",
    "next_steps": {
      "add_products": "/vendor/products/new",
      "view_dashboard": "/vendor/dashboard"
    }
  }
  ```

  **Validaciones**:
  - Email único (no duplicados)
  - Password min 8 caracteres
  - Phone formato colombiano (+57...)
  - Terms accepted = true

  **Reglas de Negocio**:
  - Auto-aprobación para MVP (no requiere verificación manual)
  - Asignar commission_rate = 5% por defecto
  - Crear usuario con role = "VENDOR"
  - Enviar email de bienvenida (básico)

  **Agente Responsable**: `backend-framework-ai`
  **Archivos**:
  - `app/api/v1/endpoints/vendors.py` (crear o mejorar)
  - `app/models/vendor.py` (validar que existe)
  - `app/schemas/vendor.py` (VendorCreate, VendorResponse)
  - `app/services/vendor_service.py` (create_vendor logic)

- [ ] **Task**: Agregar validación de email único
  **Agente**: `backend-framework-ai`
  **Archivo**: `app/services/vendor_service.py`

- [ ] **Task**: Implementar envío de email de bienvenida
  **Agente**: `communication-ai`
  **Template**: Email simple con link al dashboard
  **Archivo**: `app/services/email_service.py`

### 5.1.2 Vendor Profile Management
- [ ] **Task**: Crear endpoint `GET /api/v1/vendors/me/profile`
  ```python
  Response:
  {
    "vendor_id": "uuid",
    "email": "maria@ejemplo.com",
    "full_name": "María González",
    "business_name": "MaríaStyle",
    "phone": "+573001234567",
    "city": "Bucaramanga",
    "business_type": "persona_natural",
    "primary_category": "ropa_femenina",
    "commission_rate": 5.0,
    "status": "active",
    "created_at": "2024-02-01T10:00:00Z",
    "total_products": 23,
    "total_sales": 1250000 # COP
  }
  ```
  **Agente**: `backend-framework-ai`

- [ ] **Task**: Crear endpoint `PUT /api/v1/vendors/me/profile`
  **Agente**: `backend-framework-ai`
  **Campos editables**: full_name, phone, business_name, city

- [ ] **Task**: Crear endpoint `PUT /api/v1/vendors/me/banking`
  ```python
  Request:
  {
    "bank_name": "Bancolombia",
    "account_type": "ahorros",
    "account_number": "encrypted",
    "account_holder": "María González",
    "cedula": "1234567890"
  }
  ```
  **Agente**: `backend-framework-ai` + `data-security`
  **Seguridad**: Encriptar account_number con Fernet

---

## 5.2 Vendor Dashboard API (4 METRICS)
**Prioridad**: P0 🔥 | **Tiempo**: 1-2 días | **Agente**: `backend-framework-ai`

### 5.2.1 Dashboard Overview Endpoint
- [ ] **Task**: Crear endpoint `GET /api/v1/vendors/dashboard/overview`
  ```python
  Response:
  {
    "vendor_id": "uuid",
    "business_name": "MaríaStyle",
    "period": "current_month", # Mes actual

    "metrics": {
      "total_sales": {
        "value": 1250000, # COP
        "currency": "COP",
        "change_percent": 23.5, # vs mes anterior
        "trend": "up"
      },
      "total_orders": {
        "value": 45,
        "change_percent": 15.2,
        "trend": "up"
      },
      "pending_commission": {
        "value": 75000, # COP
        "currency": "COP",
        "next_payout_date": "2024-02-15",
        "status": "pending"
      },
      "active_products": {
        "value": 23,
        "low_stock_count": 3,
        "out_of_stock_count": 1
      }
    },

    "recent_orders": [
      {
        "order_id": "uuid",
        "customer_name": "Cliente Anónimo", # Privacidad
        "products": [
          {"name": "Vestido Casual", "quantity": 1}
        ],
        "total": 120000,
        "status": "confirmed",
        "created_at": "2024-02-01T14:30:00Z"
      }
    ], # Últimas 5 órdenes

    "alerts": [
      {
        "type": "low_stock",
        "severity": "warning",
        "message": "3 productos con stock bajo",
        "action_url": "/vendor/products?filter=low_stock"
      }
    ]
  }
  ```

  **Lógica de Cálculo**:
  - `total_sales`: SUM(order_items.price * quantity) WHERE vendor_id = X AND created_at >= start_of_month
  - `total_orders`: COUNT(DISTINCT order_id) WHERE vendor_id = X AND created_at >= start_of_month
  - `pending_commission`: SUM(commissions.amount) WHERE vendor_id = X AND status = 'pending'
  - `active_products`: COUNT(products) WHERE vendor_id = X AND status = 'approved'

  **Agente**: `backend-framework-ai`
  **Archivos**:
  - `app/api/v1/endpoints/vendors.py` (dashboard router)
  - `app/services/vendor_dashboard_service.py` (nueva clase)
  - Queries optimizadas con índices

- [ ] **Task**: Implementar cálculo de `change_percent` (vs mes anterior)
  **Agente**: `backend-framework-ai`
  **Lógica**: (mes_actual - mes_anterior) / mes_anterior * 100

- [ ] **Task**: Optimizar queries con índices de base de datos
  ```sql
  CREATE INDEX idx_orders_vendor_date ON orders(vendor_id, created_at);
  CREATE INDEX idx_products_vendor_status ON products(vendor_id, status);
  CREATE INDEX idx_commissions_vendor_status ON commissions(vendor_id, status);
  ```
  **Agente**: `database-architect-ai`

---

## 5.3 Product Management (MEJORAR EXISTENTE)
**Prioridad**: P0 🔥 | **Tiempo**: 1 día | **Agente**: `backend-framework-ai`

### 5.3.1 Verificar Endpoints Existentes
- [ ] **Task**: Auditar endpoints actuales de productos
  **Agente**: `backend-framework-ai`
  **Verificar**:
  - ✅ `POST /api/v1/productos` (crear)
  - ✅ `GET /api/v1/productos` (listar)
  - ✅ `PUT /api/v1/productos/{id}` (editar)
  - ✅ `DELETE /api/v1/productos/{id}` (eliminar)
  - ⚠️ `GET /api/v1/vendors/products` (filtrar por vendor)

- [ ] **Task**: Crear endpoint `GET /api/v1/vendors/me/products`
  ```python
  Query Params:
  - status: approved | pending | rejected
  - search: string
  - category: string
  - sort: recent | popular | price_high | price_low
  - page: int (default 1)
  - limit: int (default 20)

  Response:
  {
    "products": [
      {
        "id": "uuid",
        "name": "Vestido Casual Verano",
        "price": 120000,
        "stock": 15,
        "status": "approved",
        "category": "ropa_femenina",
        "image_url": "https://...",
        "views": 234,
        "sales": 12,
        "created_at": "2024-01-15T10:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total_products": 23,
      "total_pages": 2
    }
  }
  ```
  **Agente**: `backend-framework-ai`
  **Archivo**: `app/api/v1/endpoints/vendors.py`

- [ ] **Task**: Fix bug validación peso/dimensiones (VALIDATION_ERROR_REPORT_422.md)
  **Agente**: `backend-framework-ai`
  **Archivo**: `app/api/v1/endpoints/productos.py`
  **Issue**: Validar que peso y dimensiones sean opcionales en edición

### 5.3.2 Product Stats for Vendors
- [ ] **Task**: Agregar estadísticas a cada producto
  ```python
  GET /api/v1/vendors/me/products/{product_id}/stats
  Response:
  {
    "product_id": "uuid",
    "name": "Vestido Casual Verano",
    "performance": {
      "total_views": 234,
      "total_sales": 12,
      "revenue": 1440000,
      "avg_rating": 4.5,
      "conversion_rate": 5.1 # (sales / views * 100)
    },
    "inventory": {
      "current_stock": 15,
      "stock_alert_threshold": 5,
      "days_of_stock": 12 # Basado en velocidad de venta
    }
  }
  ```
  **Agente**: `backend-framework-ai`

---

## 5.4 Orders Management para Vendors
**Prioridad**: P0 🔥 | **Tiempo**: 1-2 días | **Agente**: `backend-framework-ai`

### 5.4.1 Vendor Orders List
- [ ] **Task**: Crear endpoint `GET /api/v1/vendors/me/orders`
  ```python
  Query Params:
  - status: pending | confirmed | shipped | delivered | cancelled
  - date_from: date
  - date_to: date
  - page: int
  - limit: int

  Response:
  {
    "orders": [
      {
        "order_id": "uuid",
        "order_number": "ORD-20240201-001",
        "customer": {
          "id": "uuid",
          "name": "Cliente Anónimo", # Privacidad en MVP
          "city": "Bucaramanga"
        },
        "items": [
          {
            "product_id": "uuid",
            "product_name": "Vestido Casual Verano",
            "quantity": 1,
            "unit_price": 120000,
            "subtotal": 120000
          }
        ],
        "totals": {
          "subtotal": 120000,
          "shipping": 15000,
          "total": 135000
        },
        "status": "confirmed",
        "created_at": "2024-02-01T14:30:00Z",
        "estimated_delivery": "2024-02-05"
      }
    ],
    "pagination": {...},
    "summary": {
      "total_orders": 45,
      "pending_orders": 8,
      "total_revenue": 1250000
    }
  }
  ```
  **Agente**: `backend-framework-ai`
  **Archivo**: `app/api/v1/endpoints/vendors.py`

- [ ] **Task**: Crear endpoint `GET /api/v1/vendors/me/orders/{order_id}`
  **Agente**: `backend-framework-ai`
  **Detalle completo**: Customer info, shipping address, payment status

- [ ] **Task**: Crear endpoint `PUT /api/v1/vendors/me/orders/{order_id}/status`
  ```python
  Request:
  {
    "status": "shipped",
    "tracking_number": "TRK123456",
    "carrier": "Servientrega",
    "notes": "Enviado en la mañana"
  }

  Response:
  {
    "order_id": "uuid",
    "status": "shipped",
    "updated_at": "2024-02-02T09:00:00Z",
    "notification_sent": true
  }
  ```
  **Agente**: `backend-framework-ai`
  **Side-effects**:
  - Enviar email/SMS a customer
  - Actualizar inventory si status = 'confirmed'

---

## 5.5 Commission & Earnings Management
**Prioridad**: P0 🔥 | **Tiempo**: 2 días | **Agente**: `backend-framework-ai`

### 5.5.1 Commission Calculation & Tracking
- [ ] **Task**: Crear endpoint `GET /api/v1/vendors/me/commissions`
  ```python
  Query Params:
  - period: current_month | last_month | custom
  - date_from: date
  - date_to: date

  Response:
  {
    "period": {
      "start_date": "2024-02-01",
      "end_date": "2024-02-29",
      "label": "Febrero 2024"
    },

    "summary": {
      "total_sales": 1250000, # COP
      "commission_rate": 5.0, # %
      "gross_commission": 62500,
      "deductions": {
        "storage_fees": 15000,
        "transaction_fees": 5000,
        "total": 20000
      },
      "net_earnings": 42500,
      "status": "pending_payout"
    },

    "breakdown": [
      {
        "product_name": "Vestido Casual Verano",
        "quantity_sold": 12,
        "unit_price": 120000,
        "total_sales": 1440000,
        "commission_amount": 72000
      }
    ],

    "payout_info": {
      "next_payout_date": "2024-03-05",
      "payout_method": "bank_transfer",
      "bank_account": "Bancolombia ***1234"
    }
  }
  ```
  **Agente**: `backend-framework-ai`
  **Archivo**: `app/services/commission_service.py` (usar existente o mejorar)

- [ ] **Task**: Implementar cálculo automático de comisiones
  **Agente**: `backend-framework-ai`
  **Trigger**: Cuando order.status = 'delivered'
  **Lógica**:
  ```python
  commission_amount = order_item.price * quantity * (commission_rate / 100)
  net_amount = commission_amount - storage_fees - transaction_fees

  # Crear registro en tabla commissions
  Commission.create(
    vendor_id=vendor.id,
    order_id=order.id,
    product_id=product.id,
    gross_amount=commission_amount,
    deductions=total_deductions,
    net_amount=net_amount,
    status='pending',
    period='2024-02'
  )
  ```

- [ ] **Task**: Crear job para calcular comisiones mensuales
  **Agente**: `backend-framework-ai`
  **Schedule**: Día 1 de cada mes a las 00:00
  **Acción**: Consolidar comisiones del mes anterior

### 5.5.2 Payout Request System
- [ ] **Task**: Crear endpoint `POST /api/v1/vendors/me/payouts/request`
  ```python
  Request:
  {
    "amount": 42500, # COP
    "bank_account_id": "uuid", # Cuenta bancaria guardada
    "notes": "Pago mensual febrero"
  }

  Response:
  {
    "payout_id": "uuid",
    "amount": 42500,
    "processing_fee": 2000,
    "net_amount": 40500,
    "status": "pending_approval",
    "estimated_date": "2024-03-05",
    "created_at": "2024-03-01T10:00:00Z"
  }
  ```
  **Agente**: `backend-framework-ai`
  **Validaciones**:
  - amount <= pending_commission
  - bank_account exists and verified
  - No hay payout pendiente del mismo mes

  **Side-effects**:
  - Enviar notificación a admin para aprobación
  - Crear registro en tabla payouts
  - Actualizar commission.status = 'payout_requested'

- [ ] **Task**: Crear endpoint `GET /api/v1/vendors/me/payouts`
  ```python
  Response:
  {
    "payouts": [
      {
        "payout_id": "uuid",
        "amount": 40500,
        "status": "approved", # pending_approval | approved | paid | rejected
        "requested_at": "2024-03-01T10:00:00Z",
        "paid_at": "2024-03-05T14:00:00Z",
        "bank_account": "Bancolombia ***1234",
        "transaction_id": "TXN123456"
      }
    ],
    "total_paid": 125000, # Histórico
    "pending_amount": 42500
  }
  ```
  **Agente**: `backend-framework-ai`

- [ ] **Task**: Crear endpoint `GET /api/v1/vendors/me/payouts/{payout_id}`
  **Agente**: `backend-framework-ai`
  **Detalle completo**: Incluir commission breakdown, deductions, timeline

---

## 5.6 Notifications para Vendors
**Prioridad**: P1 ⚠️ | **Tiempo**: 1 día | **Agente**: `communication-ai`

### 5.6.1 Email Notifications
- [ ] **Task**: Email de bienvenida al registrarse
  **Template**: "Bienvenido a MeStocker - Primeros pasos"
  **Agente**: `communication-ai`

- [ ] **Task**: Email cuando recibe nueva orden
  **Template**: "¡Nueva orden recibida! #ORD-123"
  **Agente**: `communication-ai`

- [ ] **Task**: Email cuando payout es aprobado
  **Template**: "Tu pago de $X está en camino"
  **Agente**: `communication-ai`

- [ ] **Task**: Email semanal con resumen de ventas
  **Template**: "Resumen semanal - Tu negocio en MeStocker"
  **Agente**: `communication-ai`
  **Schedule**: Lunes 8am

### 5.6.2 In-App Notifications (OPCIONAL MVP)
- [ ] **Task**: Sistema básico de notificaciones in-app
  **Agente**: `backend-framework-ai`
  **Scope**: Tabla notifications + endpoint GET /api/v1/vendors/me/notifications
  **Nice-to-have**: Puede dejarse para v1.1

---

# 🎨 FRONTEND - VENDOR INTERFACE

## 5.7 Vendor Registration Page
**Prioridad**: P0 🔥 | **Tiempo**: 1 día | **Agente**: `react-specialist-ai`

### 5.7.1 Registration Form Component
- [ ] **Task**: Crear componente `VendorRegistration.tsx`
  ```tsx
  // Path: frontend/src/pages/VendorRegistration.tsx

  import React, { useState } from 'react';
  import { useNavigate } from 'react-router-dom';
  import { vendorApiService } from '../services/vendorApiService';

  interface RegistrationForm {
    email: string;
    password: string;
    confirmPassword: string;
    full_name: string;
    phone: string;
    business_name: string;
    city: string;
    business_type: 'persona_natural' | 'empresa';
    primary_category: string;
    terms_accepted: boolean;
  }

  export const VendorRegistration: React.FC = () => {
    const [formData, setFormData] = useState<RegistrationForm>({
      email: '',
      password: '',
      confirmPassword: '',
      full_name: '',
      phone: '',
      business_name: '',
      city: '',
      business_type: 'persona_natural',
      primary_category: '',
      terms_accepted: false
    });

    const [errors, setErrors] = useState<Record<string, string>>({});
    const [isSubmitting, setIsSubmitting] = useState(false);
    const navigate = useNavigate();

    const handleSubmit = async (e: React.FormEvent) => {
      e.preventDefault();

      // Validaciones básicas
      if (formData.password !== formData.confirmPassword) {
        setErrors({ confirmPassword: 'Las contraseñas no coinciden' });
        return;
      }

      if (!formData.terms_accepted) {
        setErrors({ terms: 'Debes aceptar los términos y condiciones' });
        return;
      }

      setIsSubmitting(true);

      try {
        const response = await vendorApiService.register(formData);

        // Mostrar mensaje de éxito
        toast.success('¡Registro exitoso! Bienvenido a MeStocker');

        // Redirigir a login o dashboard
        navigate('/vendor/login');

      } catch (error: any) {
        setErrors({
          general: error.response?.data?.message || 'Error al registrarse'
        });
      } finally {
        setIsSubmitting(false);
      }
    };

    return (
      <div className="vendor-registration-container">
        <div className="registration-header">
          <h1>Únete a MeStocker</h1>
          <p>Comienza a vender tus productos hoy mismo</p>
        </div>

        <form onSubmit={handleSubmit} className="registration-form">
          <div className="form-section">
            <h2>Información Personal</h2>

            <input
              type="text"
              placeholder="Nombre completo"
              value={formData.full_name}
              onChange={e => setFormData({...formData, full_name: e.target.value})}
              required
            />

            <input
              type="email"
              placeholder="Email"
              value={formData.email}
              onChange={e => setFormData({...formData, email: e.target.value})}
              required
            />

            <input
              type="tel"
              placeholder="Teléfono (+57...)"
              value={formData.phone}
              onChange={e => setFormData({...formData, phone: e.target.value})}
              required
            />

            <input
              type="password"
              placeholder="Contraseña"
              value={formData.password}
              onChange={e => setFormData({...formData, password: e.target.value})}
              required
              minLength={8}
            />

            <input
              type="password"
              placeholder="Confirmar contraseña"
              value={formData.confirmPassword}
              onChange={e => setFormData({...formData, confirmPassword: e.target.value})}
              required
            />
            {errors.confirmPassword && <span className="error">{errors.confirmPassword}</span>}
          </div>

          <div className="form-section">
            <h2>Información del Negocio</h2>

            <input
              type="text"
              placeholder="Nombre del negocio"
              value={formData.business_name}
              onChange={e => setFormData({...formData, business_name: e.target.value})}
              required
            />

            <select
              value={formData.business_type}
              onChange={e => setFormData({...formData, business_type: e.target.value as any})}
              required
            >
              <option value="persona_natural">Persona Natural</option>
              <option value="empresa">Empresa</option>
            </select>

            <input
              type="text"
              placeholder="Ciudad"
              value={formData.city}
              onChange={e => setFormData({...formData, city: e.target.value})}
              required
            />

            <select
              value={formData.primary_category}
              onChange={e => setFormData({...formData, primary_category: e.target.value})}
              required
            >
              <option value="">Selecciona categoría principal</option>
              <option value="ropa_femenina">Ropa Femenina</option>
              <option value="ropa_masculina">Ropa Masculina</option>
              <option value="accesorios">Accesorios</option>
              <option value="calzado">Calzado</option>
              <option value="hogar">Hogar y Decoración</option>
              <option value="tecnologia">Tecnología</option>
            </select>
          </div>

          <div className="form-section">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={formData.terms_accepted}
                onChange={e => setFormData({...formData, terms_accepted: e.target.checked})}
                required
              />
              <span>
                Acepto los <a href="/terms" target="_blank">términos y condiciones</a> y la
                <a href="/privacy" target="_blank">política de privacidad</a>
              </span>
            </label>
            {errors.terms && <span className="error">{errors.terms}</span>}
          </div>

          {errors.general && (
            <div className="error-message">{errors.general}</div>
          )}

          <button
            type="submit"
            className="submit-button"
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Registrando...' : 'Crear Cuenta'}
          </button>

          <div className="login-link">
            ¿Ya tienes cuenta? <a href="/vendor/login">Inicia sesión</a>
          </div>
        </form>
      </div>
    );
  };
  ```
  **Agente**: `react-specialist-ai`
  **Archivos**:
  - `frontend/src/pages/VendorRegistration.tsx` (crear)
  - `frontend/src/services/vendorApiService.ts` (crear)
  - `frontend/src/styles/VendorRegistration.css` (crear)

- [ ] **Task**: Crear servicio `vendorApiService.ts`
  ```typescript
  // Path: frontend/src/services/vendorApiService.ts

  import axios from 'axios';

  const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  export const vendorApiService = {
    register: async (data: any) => {
      const response = await axios.post(`${API_BASE}/api/v1/vendors/register`, data);
      return response.data;
    },

    getDashboard: async () => {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_BASE}/api/v1/vendors/dashboard/overview`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      return response.data;
    },

    getProducts: async (params?: any) => {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_BASE}/api/v1/vendors/me/products`, {
        headers: { Authorization: `Bearer ${token}` },
        params
      });
      return response.data;
    },

    getOrders: async (params?: any) => {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_BASE}/api/v1/vendors/me/orders`, {
        headers: { Authorization: `Bearer ${token}` },
        params
      });
      return response.data;
    },

    getCommissions: async (params?: any) => {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_BASE}/api/v1/vendors/me/commissions`, {
        headers: { Authorization: `Bearer ${token}` },
        params
      });
      return response.data;
    },

    requestPayout: async (data: any) => {
      const token = localStorage.getItem('token');
      const response = await axios.post(`${API_BASE}/api/v1/vendors/me/payouts/request`, data, {
        headers: { Authorization: `Bearer ${token}` }
      });
      return response.data;
    }
  };
  ```
  **Agente**: `react-specialist-ai`

- [ ] **Task**: Agregar ruta en React Router
  ```typescript
  // En frontend/src/App.tsx
  <Route path="/vendor/register" element={<VendorRegistration />} />
  ```
  **Agente**: `react-specialist-ai`

---

## 5.8 Vendor Dashboard Page
**Prioridad**: P0 🔥 | **Tiempo**: 2 días | **Agente**: `react-specialist-ai`

### 5.8.1 Dashboard Main Component
- [ ] **Task**: Crear componente `VendorDashboard.tsx`
  ```tsx
  // Path: frontend/src/pages/vendor/VendorDashboard.tsx

  import React, { useEffect, useState } from 'react';
  import { vendorApiService } from '../../services/vendorApiService';

  interface DashboardData {
    business_name: string;
    metrics: {
      total_sales: { value: number; change_percent: number; trend: string };
      total_orders: { value: number; change_percent: number };
      pending_commission: { value: number; next_payout_date: string };
      active_products: { value: number; low_stock_count: number };
    };
    recent_orders: Array<any>;
    alerts: Array<any>;
  }

  export const VendorDashboard: React.FC = () => {
    const [data, setData] = useState<DashboardData | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
      loadDashboard();
    }, []);

    const loadDashboard = async () => {
      try {
        const response = await vendorApiService.getDashboard();
        setData(response);
      } catch (error) {
        console.error('Error loading dashboard:', error);
      } finally {
        setLoading(false);
      }
    };

    if (loading) return <LoadingSpinner />;
    if (!data) return <ErrorMessage />;

    return (
      <div className="vendor-dashboard">
        {/* Header */}
        <div className="dashboard-header">
          <h1>Buenos días 👋</h1>
          <p className="business-name">{data.business_name}</p>
          <div className="quick-actions">
            <button onClick={() => navigate('/vendor/products/new')}>
              + Agregar Producto
            </button>
            <button onClick={() => navigate('/vendor/orders')}>
              Ver Órdenes
            </button>
          </div>
        </div>

        {/* Alerts */}
        {data.alerts.length > 0 && (
          <div className="alerts-section">
            {data.alerts.map((alert, idx) => (
              <Alert key={idx} type={alert.type} message={alert.message} />
            ))}
          </div>
        )}

        {/* Metrics Grid */}
        <div className="metrics-grid">
          <MetricCard
            title="Ventas este mes"
            value={formatCurrency(data.metrics.total_sales.value)}
            change={data.metrics.total_sales.change_percent}
            trend={data.metrics.total_sales.trend}
            icon="💰"
          />

          <MetricCard
            title="Órdenes"
            value={data.metrics.total_orders.value}
            change={data.metrics.total_orders.change_percent}
            icon="📦"
          />

          <MetricCard
            title="Comisión pendiente"
            value={formatCurrency(data.metrics.pending_commission.value)}
            subtitle={`Próximo pago: ${formatDate(data.metrics.pending_commission.next_payout_date)}`}
            icon="💵"
          />

          <MetricCard
            title="Productos activos"
            value={data.metrics.active_products.value}
            subtitle={data.metrics.active_products.low_stock_count > 0
              ? `⚠️ ${data.metrics.active_products.low_stock_count} con stock bajo`
              : 'Todo en orden'}
            icon="📊"
          />
        </div>

        {/* Recent Orders */}
        <div className="recent-orders-section">
          <h2>Órdenes Recientes</h2>
          <OrdersTable orders={data.recent_orders} compact />
          <button onClick={() => navigate('/vendor/orders')}>
            Ver todas las órdenes →
          </button>
        </div>
      </div>
    );
  };

  // Sub-componentes
  const MetricCard: React.FC<any> = ({ title, value, change, trend, subtitle, icon }) => (
    <div className="metric-card">
      <div className="metric-icon">{icon}</div>
      <div className="metric-content">
        <h3>{title}</h3>
        <div className="metric-value">{value}</div>
        {change !== undefined && (
          <div className={`metric-change ${trend}`}>
            {change > 0 ? '↑' : '↓'} {Math.abs(change)}%
          </div>
        )}
        {subtitle && <div className="metric-subtitle">{subtitle}</div>}
      </div>
    </div>
  );
  ```
  **Agente**: `react-specialist-ai`
  **Archivos**:
  - `frontend/src/pages/vendor/VendorDashboard.tsx`
  - `frontend/src/components/vendor/MetricCard.tsx`
  - `frontend/src/components/vendor/OrdersTable.tsx`
  - `frontend/src/styles/vendor/Dashboard.css`

- [ ] **Task**: Implementar auto-refresh cada 30 segundos
  **Agente**: `react-specialist-ai`
  **Técnica**: setInterval + useEffect cleanup

- [ ] **Task**: Agregar loading skeletons para mejor UX
  **Agente**: `react-specialist-ai` + `ux-specialist-ai`

---

## 5.9 Vendor Products Page
**Prioridad**: P0 🔥 | **Tiempo**: 1 día | **Agente**: `react-specialist-ai`

### 5.9.1 Products List Component
- [ ] **Task**: Crear componente `VendorProducts.tsx`
  ```tsx
  // Path: frontend/src/pages/vendor/VendorProducts.tsx

  export const VendorProducts: React.FC = () => {
    const [products, setProducts] = useState([]);
    const [filters, setFilters] = useState({
      status: 'all',
      search: '',
      category: '',
      sort: 'recent'
    });

    return (
      <div className="vendor-products">
        <div className="products-header">
          <h1>Mis Productos</h1>
          <button onClick={() => navigate('/vendor/products/new')}>
            + Nuevo Producto
          </button>
        </div>

        <div className="products-filters">
          <input
            type="search"
            placeholder="Buscar productos..."
            value={filters.search}
            onChange={e => setFilters({...filters, search: e.target.value})}
          />

          <select
            value={filters.status}
            onChange={e => setFilters({...filters, status: e.target.value})}
          >
            <option value="all">Todos</option>
            <option value="approved">Aprobados</option>
            <option value="pending">Pendientes</option>
            <option value="rejected">Rechazados</option>
          </select>

          <select
            value={filters.sort}
            onChange={e => setFilters({...filters, sort: e.target.value})}
          >
            <option value="recent">Más recientes</option>
            <option value="popular">Más vendidos</option>
            <option value="price_high">Precio mayor</option>
            <option value="price_low">Precio menor</option>
          </select>
        </div>

        <div className="products-grid">
          {products.map(product => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>
      </div>
    );
  };

  const ProductCard: React.FC<{product: any}> = ({ product }) => (
    <div className="product-card">
      <img src={product.image_url} alt={product.name} />
      <div className="product-info">
        <h3>{product.name}</h3>
        <p className="price">{formatCurrency(product.price)}</p>
        <div className="product-stats">
          <span>Stock: {product.stock}</span>
          <span>Ventas: {product.sales}</span>
        </div>
        <StatusBadge status={product.status} />
      </div>
      <div className="product-actions">
        <button onClick={() => navigate(`/vendor/products/${product.id}/edit`)}>
          Editar
        </button>
        <button onClick={() => navigate(`/vendor/products/${product.id}/stats`)}>
          Ver stats
        </button>
      </div>
    </div>
  );
  ```
  **Agente**: `react-specialist-ai`

- [ ] **Task**: Reutilizar componente ProductForm existente
  **Agente**: `react-specialist-ai`
  **Archivo**: `frontend/src/components/vendor/ProductForm.tsx` (ya existe)
  **Acción**: Adaptar para vendor use case

---

## 5.10 Vendor Orders Page
**Prioridad**: P0 🔥 | **Tiempo**: 1 día | **Agente**: `react-specialist-ai`

### 5.10.1 Orders List Component
- [ ] **Task**: Crear componente `VendorOrders.tsx`
  ```tsx
  // Path: frontend/src/pages/vendor/VendorOrders.tsx

  export const VendorOrders: React.FC = () => {
    const [orders, setOrders] = useState([]);
    const [selectedOrder, setSelectedOrder] = useState(null);
    const [statusFilter, setStatusFilter] = useState('all');

    return (
      <div className="vendor-orders">
        <h1>Mis Órdenes</h1>

        <div className="orders-stats">
          <StatCard title="Total" value={orders.length} />
          <StatCard title="Pendientes" value={orders.filter(o => o.status === 'pending').length} />
          <StatCard title="En proceso" value={orders.filter(o => o.status === 'confirmed').length} />
        </div>

        <div className="orders-filters">
          <select value={statusFilter} onChange={e => setStatusFilter(e.target.value)}>
            <option value="all">Todas</option>
            <option value="pending">Pendientes</option>
            <option value="confirmed">Confirmadas</option>
            <option value="shipped">Enviadas</option>
            <option value="delivered">Entregadas</option>
          </select>
        </div>

        <table className="orders-table">
          <thead>
            <tr>
              <th>Orden</th>
              <th>Fecha</th>
              <th>Cliente</th>
              <th>Productos</th>
              <th>Total</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {orders.map(order => (
              <tr key={order.order_id}>
                <td>{order.order_number}</td>
                <td>{formatDate(order.created_at)}</td>
                <td>{order.customer.name}</td>
                <td>{order.items.length} items</td>
                <td>{formatCurrency(order.totals.total)}</td>
                <td><StatusBadge status={order.status} /></td>
                <td>
                  <button onClick={() => setSelectedOrder(order)}>
                    Ver detalle
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {selectedOrder && (
          <OrderDetailModal
            order={selectedOrder}
            onClose={() => setSelectedOrder(null)}
            onUpdateStatus={handleUpdateStatus}
          />
        )}
      </div>
    );
  };
  ```
  **Agente**: `react-specialist-ai`

### 5.10.2 Order Detail Modal
- [ ] **Task**: Crear componente `OrderDetailModal.tsx`
  ```tsx
  export const OrderDetailModal: React.FC<any> = ({ order, onClose, onUpdateStatus }) => {
    const [newStatus, setNewStatus] = useState(order.status);
    const [trackingNumber, setTrackingNumber] = useState('');

    const handleSubmit = async () => {
      await onUpdateStatus(order.order_id, {
        status: newStatus,
        tracking_number: trackingNumber
      });
      onClose();
    };

    return (
      <Modal onClose={onClose}>
        <h2>Detalle de Orden #{order.order_number}</h2>

        <section className="order-customer">
          <h3>Cliente</h3>
          <p>{order.customer.name}</p>
          <p>{order.customer.city}</p>
        </section>

        <section className="order-items">
          <h3>Productos</h3>
          {order.items.map(item => (
            <div key={item.product_id}>
              <span>{item.product_name}</span>
              <span>x{item.quantity}</span>
              <span>{formatCurrency(item.subtotal)}</span>
            </div>
          ))}
        </section>

        <section className="order-status-update">
          <h3>Actualizar Estado</h3>
          <select value={newStatus} onChange={e => setNewStatus(e.target.value)}>
            <option value="confirmed">Confirmar</option>
            <option value="shipped">Marcar como enviada</option>
            <option value="delivered">Marcar como entregada</option>
          </select>

          {newStatus === 'shipped' && (
            <input
              type="text"
              placeholder="Número de guía"
              value={trackingNumber}
              onChange={e => setTrackingNumber(e.target.value)}
            />
          )}

          <button onClick={handleSubmit}>Actualizar</button>
        </section>
      </Modal>
    );
  };
  ```
  **Agente**: `react-specialist-ai`

---

## 5.11 Vendor Earnings Page
**Prioridad**: P0 🔥 | **Tiempo**: 1 día | **Agente**: `react-specialist-ai`

### 5.11.1 Earnings Overview Component
- [ ] **Task**: Crear componente `VendorEarnings.tsx`
  ```tsx
  // Path: frontend/src/pages/vendor/VendorEarnings.tsx

  export const VendorEarnings: React.FC = () => {
    const [commissionData, setCommissionData] = useState(null);
    const [payouts, setPayouts] = useState([]);
    const [showPayoutModal, setShowPayoutModal] = useState(false);

    return (
      <div className="vendor-earnings">
        <h1>Mis Ganancias</h1>

        {/* Summary Cards */}
        <div className="earnings-summary">
          <SummaryCard
            title="Ventas del mes"
            value={formatCurrency(commissionData?.summary.total_sales)}
            icon="💰"
          />
          <SummaryCard
            title="Comisión neta"
            value={formatCurrency(commissionData?.summary.net_earnings)}
            icon="💵"
          />
          <SummaryCard
            title="Próximo pago"
            value={formatDate(commissionData?.payout_info.next_payout_date)}
            icon="📅"
          />
        </div>

        {/* Payout Request */}
        <div className="payout-request-section">
          <h2>Solicitar Pago</h2>
          <p>Monto disponible: {formatCurrency(commissionData?.summary.net_earnings)}</p>
          <button
            onClick={() => setShowPayoutModal(true)}
            disabled={commissionData?.summary.net_earnings < 50000} // Mínimo 50k
          >
            Solicitar Pago
          </button>
        </div>

        {/* Commission Breakdown */}
        <div className="commission-breakdown">
          <h2>Detalle de Comisiones</h2>
          <table>
            <thead>
              <tr>
                <th>Producto</th>
                <th>Vendidos</th>
                <th>Ventas</th>
                <th>Comisión</th>
              </tr>
            </thead>
            <tbody>
              {commissionData?.breakdown.map(item => (
                <tr key={item.product_name}>
                  <td>{item.product_name}</td>
                  <td>{item.quantity_sold}</td>
                  <td>{formatCurrency(item.total_sales)}</td>
                  <td>{formatCurrency(item.commission_amount)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Payout History */}
        <div className="payout-history">
          <h2>Historial de Pagos</h2>
          <table>
            <thead>
              <tr>
                <th>Fecha</th>
                <th>Monto</th>
                <th>Estado</th>
                <th>Banco</th>
              </tr>
            </thead>
            <tbody>
              {payouts.map(payout => (
                <tr key={payout.payout_id}>
                  <td>{formatDate(payout.requested_at)}</td>
                  <td>{formatCurrency(payout.amount)}</td>
                  <td><StatusBadge status={payout.status} /></td>
                  <td>{payout.bank_account}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {showPayoutModal && (
          <PayoutRequestModal
            availableAmount={commissionData?.summary.net_earnings}
            onClose={() => setShowPayoutModal(false)}
            onSubmit={handlePayoutRequest}
          />
        )}
      </div>
    );
  };
  ```
  **Agente**: `react-specialist-ai`

### 5.11.2 Payout Request Modal
- [ ] **Task**: Crear componente `PayoutRequestModal.tsx`
  ```tsx
  export const PayoutRequestModal: React.FC<any> = ({ availableAmount, onClose, onSubmit }) => {
    const [amount, setAmount] = useState(availableAmount);
    const [bankAccount, setBankAccount] = useState('');

    return (
      <Modal onClose={onClose}>
        <h2>Solicitar Pago</h2>

        <div className="payout-form">
          <label>
            Monto a solicitar
            <input
              type="number"
              value={amount}
              onChange={e => setAmount(Number(e.target.value))}
              max={availableAmount}
              min={50000}
            />
            <span>Máximo: {formatCurrency(availableAmount)}</span>
          </label>

          <label>
            Cuenta bancaria
            <select value={bankAccount} onChange={e => setBankAccount(e.target.value)}>
              <option value="">Seleccionar cuenta</option>
              <option value="primary">Bancolombia ***1234</option>
            </select>
          </label>

          <div className="payout-summary">
            <p>Monto solicitado: {formatCurrency(amount)}</p>
            <p>Comisión de procesamiento: {formatCurrency(amount * 0.02)}</p>
            <p><strong>Recibirás: {formatCurrency(amount * 0.98)}</strong></p>
          </div>

          <button onClick={() => onSubmit({ amount, bank_account: bankAccount })}>
            Confirmar Solicitud
          </button>
        </div>
      </Modal>
    );
  };
  ```
  **Agente**: `react-specialist-ai`

---

## 5.12 Vendor Navigation & Layout
**Prioridad**: P0 🔥 | **Tiempo**: 0.5 días | **Agente**: `react-specialist-ai`

### 5.12.1 Vendor Layout Component
- [ ] **Task**: Crear componente `VendorLayout.tsx`
  ```tsx
  // Path: frontend/src/components/layout/VendorLayout.tsx

  export const VendorLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const navigate = useNavigate();
    const location = useLocation();

    const navItems = [
      { path: '/vendor/dashboard', label: 'Dashboard', icon: '📊' },
      { path: '/vendor/products', label: 'Productos', icon: '📦' },
      { path: '/vendor/orders', label: 'Órdenes', icon: '🛒' },
      { path: '/vendor/earnings', label: 'Ganancias', icon: '💰' },
      { path: '/vendor/profile', label: 'Perfil', icon: '👤' }
    ];

    return (
      <div className="vendor-layout">
        <aside className="vendor-sidebar">
          <div className="vendor-logo">
            <h2>MeStocker</h2>
            <span>Vendor Portal</span>
          </div>

          <nav className="vendor-nav">
            {navItems.map(item => (
              <a
                key={item.path}
                href={item.path}
                className={location.pathname === item.path ? 'active' : ''}
                onClick={e => {
                  e.preventDefault();
                  navigate(item.path);
                }}
              >
                <span className="nav-icon">{item.icon}</span>
                <span className="nav-label">{item.label}</span>
              </a>
            ))}
          </nav>

          <div className="vendor-sidebar-footer">
            <button onClick={handleLogout}>Cerrar sesión</button>
          </div>
        </aside>

        <main className="vendor-content">
          <header className="vendor-header">
            <div className="search-bar">
              <input type="search" placeholder="Buscar..." />
            </div>
            <div className="vendor-user">
              <NotificationBell />
              <UserAvatar />
            </div>
          </header>

          <div className="vendor-main">
            {children}
          </div>
        </main>
      </div>
    );
  };
  ```
  **Agente**: `react-specialist-ai`

- [ ] **Task**: Agregar rutas protegidas para vendors
  ```tsx
  // En App.tsx
  <Route path="/vendor" element={<ProtectedRoute role="VENDOR"><VendorLayout /></ProtectedRoute>}>
    <Route path="dashboard" element={<VendorDashboard />} />
    <Route path="products" element={<VendorProducts />} />
    <Route path="products/new" element={<ProductForm />} />
    <Route path="products/:id/edit" element={<ProductForm />} />
    <Route path="orders" element={<VendorOrders />} />
    <Route path="earnings" element={<VendorEarnings />} />
    <Route path="profile" element={<VendorProfile />} />
  </Route>
  ```
  **Agente**: `react-specialist-ai`

---

# ✅ TESTING & VALIDATION

## 5.13 Backend Testing
**Prioridad**: P0 🔥 | **Tiempo**: 1 día | **Agente**: `tdd-specialist`

### 5.13.1 API Endpoint Tests
- [ ] **Task**: Crear tests para vendor registration
  ```python
  # tests/test_vendor_registration.py

  def test_vendor_registration_success():
      response = client.post("/api/v1/vendors/register", json={
          "email": "test@example.com",
          "password": "SecurePass123!",
          "full_name": "Test Vendor",
          "phone": "+573001234567",
          "business_name": "Test Business",
          "city": "Bucaramanga",
          "business_type": "persona_natural",
          "primary_category": "ropa_femenina",
          "terms_accepted": True
      })
      assert response.status_code == 200
      assert "vendor_id" in response.json()

  def test_vendor_registration_duplicate_email():
      # Register first time
      client.post("/api/v1/vendors/register", json={...})

      # Try to register again with same email
      response = client.post("/api/v1/vendors/register", json={...})
      assert response.status_code == 400
      assert "email already exists" in response.json()["message"]
  ```
  **Agente**: `tdd-specialist`

- [ ] **Task**: Crear tests para dashboard API
  ```python
  def test_vendor_dashboard_requires_auth():
      response = client.get("/api/v1/vendors/dashboard/overview")
      assert response.status_code == 401

  def test_vendor_dashboard_returns_metrics(authenticated_vendor):
      response = client.get("/api/v1/vendors/dashboard/overview",
          headers={"Authorization": f"Bearer {authenticated_vendor.token}"})
      assert response.status_code == 200
      data = response.json()
      assert "metrics" in data
      assert "total_sales" in data["metrics"]
  ```
  **Agente**: `tdd-specialist`

- [ ] **Task**: Crear tests para commission calculation
  ```python
  def test_commission_calculation_accuracy():
      # Create order with known values
      order = create_test_order(
          vendor_id=vendor.id,
          product_price=100000,
          quantity=1,
          commission_rate=5.0
      )

      # Mark as delivered to trigger commission
      order.status = "delivered"
      db.commit()

      # Check commission was created correctly
      commission = db.query(Commission).filter_by(order_id=order.id).first()
      assert commission.gross_amount == 5000  # 5% of 100000
      assert commission.status == "pending"
  ```
  **Agente**: `tdd-specialist`

- [ ] **Task**: Crear tests para payout request
  ```python
  def test_payout_request_success(vendor_with_commission):
      response = client.post("/api/v1/vendors/me/payouts/request",
          json={"amount": 50000, "bank_account_id": "uuid"},
          headers={"Authorization": f"Bearer {vendor_with_commission.token}"})
      assert response.status_code == 200
      assert "payout_id" in response.json()

  def test_payout_request_exceeds_balance(vendor):
      response = client.post("/api/v1/vendors/me/payouts/request",
          json={"amount": 999999, "bank_account_id": "uuid"},
          headers={"Authorization": f"Bearer {vendor.token}"})
      assert response.status_code == 400
  ```
  **Agente**: `tdd-specialist`

### 5.13.2 Integration Tests
- [ ] **Task**: Test complete vendor journey (E2E backend)
  ```python
  def test_complete_vendor_journey():
      # 1. Register
      reg_response = client.post("/api/v1/vendors/register", json={...})
      vendor_id = reg_response.json()["vendor_id"]

      # 2. Login
      login_response = client.post("/api/v1/auth/login", json={...})
      token = login_response.json()["access_token"]

      # 3. Create product
      product_response = client.post("/api/v1/productos",
          json={...}, headers={"Authorization": f"Bearer {token}"})

      # 4. Simulate order
      order = create_order_for_product(product_response.json()["id"])
      order.status = "delivered"

      # 5. Check commission was created
      commission_response = client.get("/api/v1/vendors/me/commissions",
          headers={"Authorization": f"Bearer {token}"})
      assert commission_response.json()["summary"]["net_earnings"] > 0

      # 6. Request payout
      payout_response = client.post("/api/v1/vendors/me/payouts/request",
          json={"amount": 50000}, headers={"Authorization": f"Bearer {token}"})
      assert payout_response.status_code == 200
  ```
  **Agente**: `integration-testing` + `tdd-specialist`

---

## 5.14 Frontend Testing
**Prioridad**: P1 ⚠️ | **Tiempo**: 1 día | **Agente**: `unit-testing-ai`

### 5.14.1 Component Tests
- [ ] **Task**: Test VendorRegistration component
  ```tsx
  // tests/VendorRegistration.test.tsx

  describe('VendorRegistration', () => {
    it('validates required fields', async () => {
      render(<VendorRegistration />);

      const submitButton = screen.getByText('Crear Cuenta');
      fireEvent.click(submitButton);

      expect(await screen.findByText(/nombre completo es requerido/i)).toBeInTheDocument();
    });

    it('validates password match', async () => {
      render(<VendorRegistration />);

      fireEvent.change(screen.getByPlaceholderText('Contraseña'), {
        target: { value: 'Pass123!' }
      });
      fireEvent.change(screen.getByPlaceholderText('Confirmar contraseña'), {
        target: { value: 'Different!' }
      });

      fireEvent.click(screen.getByText('Crear Cuenta'));

      expect(await screen.findByText(/contraseñas no coinciden/i)).toBeInTheDocument();
    });

    it('submits form successfully', async () => {
      const mockRegister = jest.fn().mockResolvedValue({ vendor_id: 'uuid' });
      vendorApiService.register = mockRegister;

      render(<VendorRegistration />);

      // Fill form
      fireEvent.change(screen.getByPlaceholderText('Nombre completo'), {
        target: { value: 'Test Vendor' }
      });
      // ... fill other fields

      fireEvent.click(screen.getByText('Crear Cuenta'));

      await waitFor(() => {
        expect(mockRegister).toHaveBeenCalled();
      });
    });
  });
  ```
  **Agente**: `unit-testing-ai`

- [ ] **Task**: Test VendorDashboard component
  **Agente**: `unit-testing-ai`

- [ ] **Task**: Test VendorEarnings component
  **Agente**: `unit-testing-ai`

### 5.14.2 E2E Tests (Frontend)
- [ ] **Task**: Test complete vendor registration flow
  ```typescript
  // tests/e2e/vendor-registration.spec.ts

  test('vendor can register successfully', async ({ page }) => {
    await page.goto('/vendor/register');

    await page.fill('input[name="full_name"]', 'María González');
    await page.fill('input[name="email"]', 'maria@test.com');
    await page.fill('input[name="password"]', 'SecurePass123!');
    await page.fill('input[name="confirmPassword"]', 'SecurePass123!');
    await page.fill('input[name="phone"]', '+573001234567');
    await page.fill('input[name="business_name"]', 'MaríaStyle');
    await page.selectOption('select[name="business_type"]', 'persona_natural');
    await page.fill('input[name="city"]', 'Bucaramanga');
    await page.selectOption('select[name="primary_category"]', 'ropa_femenina');
    await page.check('input[name="terms_accepted"]');

    await page.click('button[type="submit"]');

    await expect(page).toHaveURL('/vendor/login');
    await expect(page.locator('.success-message')).toContainText('Registro exitoso');
  });
  ```
  **Agente**: `e2e-testing-ai`

---

## 5.15 Manual Testing Checklist
**Prioridad**: P0 🔥 | **Tiempo**: 1 día | **Agente**: Manual QA + `ux-specialist-ai`

### 5.15.1 Vendor Registration Flow
- [ ] **Test**: Abrir http://192.168.1.137:5173/vendor/register
  **Verificar**:
  - [ ] Formulario se carga correctamente
  - [ ] Validaciones funcionan en tiempo real
  - [ ] Password strength indicator funciona
  - [ ] Términos y condiciones link funciona
  - [ ] Submit registra vendor correctamente
  - [ ] Redirección a login después de registro
  - [ ] Email de bienvenida se envía

  **Agente Responsable**: `ux-specialist-ai` (validación UX)
  **Criterio de Éxito**: Registro completo en <3 minutos

### 5.15.2 Vendor Dashboard
- [ ] **Test**: Login como vendor → Dashboard
  **Verificar**:
  - [ ] URL: http://192.168.1.137:5173/vendor/dashboard
  - [ ] 4 metric cards cargan correctamente
  - [ ] Valores son precisos (comparar con DB)
  - [ ] Change percent calcula correctamente
  - [ ] Recent orders muestra últimas 5 órdenes
  - [ ] Alerts aparecen si hay low stock
  - [ ] Quick actions buttons funcionan
  - [ ] Auto-refresh cada 30 segundos
  - [ ] Mobile responsive

  **Agente Responsable**: `frontend-performance-ai` (performance)
  **Criterio de Éxito**: Dashboard carga en <2 segundos

### 5.15.3 Product Management
- [ ] **Test**: Crear nuevo producto como vendor
  **Verificar**:
  - [ ] URL: http://192.168.1.137:5173/vendor/products/new
  - [ ] Formulario carga correctamente
  - [ ] Upload de imágenes funciona
  - [ ] Validación de peso/dimensiones arreglada (bug fix)
  - [ ] Submit crea producto correctamente
  - [ ] Status = 'approved' automáticamente (MVP)
  - [ ] Redirección a lista de productos
  - [ ] Nuevo producto aparece en lista

  **Agente Responsable**: `react-specialist-ai`
  **Criterio de Éxito**: Crear producto en <5 minutos

- [ ] **Test**: Editar producto existente
  **Verificar**:
  - [ ] URL: http://192.168.1.137:5173/vendor/products/{id}/edit
  - [ ] Formulario pre-rellena datos correctamente
  - [ ] Cambios se guardan correctamente
  - [ ] Imágenes existentes se muestran
  - [ ] Validación no bloquea edición (bug peso/dimensiones)

  **Agente Responsable**: `react-specialist-ai`

### 5.15.4 Orders Management
- [ ] **Test**: Ver órdenes recibidas
  **Verificar**:
  - [ ] URL: http://192.168.1.137:5173/vendor/orders
  - [ ] Lista carga todas las órdenes del vendor
  - [ ] Filtros funcionan correctamente
  - [ ] Paginación funciona
  - [ ] Click en orden abre modal de detalle
  - [ ] Modal muestra información completa

  **Agente Responsable**: `react-specialist-ai`

- [ ] **Test**: Actualizar estado de orden
  **Verificar**:
  - [ ] En modal, cambiar status a "shipped"
  - [ ] Agregar tracking number
  - [ ] Submit actualiza orden correctamente
  - [ ] Customer recibe notificación email/SMS
  - [ ] Estado se refleja inmediatamente en UI

  **Agente Responsable**: `communication-ai` (notificaciones)

### 5.15.5 Earnings & Payouts
- [ ] **Test**: Ver comisiones y solicitar pago
  **Verificar**:
  - [ ] URL: http://192.168.1.137:5173/vendor/earnings
  - [ ] Summary cards muestran datos correctos
  - [ ] Commission breakdown es preciso
  - [ ] Cálculos coinciden con backend
  - [ ] Click "Solicitar Pago" abre modal
  - [ ] Modal valida monto mínimo (50k)
  - [ ] Submit crea payout request
  - [ ] Payout aparece en historial con status "pending_approval"
  - [ ] Admin recibe notificación para aprobar

  **Agente Responsable**: `backend-framework-ai` (cálculos)
  **Criterio de Éxito**: Cálculos 100% precisos

### 5.15.6 Mobile Responsiveness
- [ ] **Test**: Todas las páginas en mobile
  **Verificar**:
  - [ ] Dashboard responsive
  - [ ] Products list responsive
  - [ ] Orders table responsive (scroll horizontal)
  - [ ] Earnings page responsive
  - [ ] Navigation funciona en mobile
  - [ ] Touch interactions funcionan bien

  **Agente Responsable**: `mobile-ux-ai`
  **Criterio de Éxito**: Todas las funciones usables en 375px width

### 5.15.7 Performance Testing
- [ ] **Test**: Dashboard performance bajo carga
  **Verificar**:
  - [ ] Dashboard carga en <2s con 100 productos
  - [ ] Products list carga en <1s con paginación
  - [ ] Orders list carga en <1.5s con 50 órdenes
  - [ ] API responses <500ms
  - [ ] No memory leaks con auto-refresh

  **Agente Responsable**: `performance-optimization-ai`
  **Tool**: Lighthouse, Chrome DevTools

---

## 5.16 Bug Fixes & Improvements
**Prioridad**: P0 🔥 | **Tiempo**: 0.5 días

### 5.16.1 Critical Bug Fix
- [ ] **Task**: Fix validación peso/dimensiones en ProductForm
  **Archivo**: `app/api/v1/endpoints/productos.py`
  **Issue**: VALIDATION_ERROR_REPORT_422.md
  **Agente**: `backend-framework-ai`
  **Solución**: Hacer peso y dimensiones opcionales en PUT request

### 5.16.2 UX Improvements
- [ ] **Task**: Agregar loading states en todos los componentes
  **Agente**: `react-specialist-ai`

- [ ] **Task**: Agregar error boundaries para manejo de errores
  **Agente**: `react-specialist-ai`

- [ ] **Task**: Mejorar mensajes de validación (más claros)
  **Agente**: `ux-specialist-ai`

---

# 📊 SUCCESS METRICS & KPIs

## 5.17 Metrics Tracking
**Prioridad**: P1 ⚠️ | **Agente**: `real-time-analytics-ai`

### 5.17.1 Vendor Acquisition Metrics
- **Registration Completion Rate**: >85%
  - Track: Formulario iniciado vs completado
- **Time to First Product**: <24 horas después de registro
  - Track: vendor.created_at vs first product.created_at
- **Onboarding Completion**: >90%
  - Track: Vendors que completan perfil + agregan producto + configuran banco

### 5.17.2 Vendor Engagement Metrics
- **Daily Active Vendors**: >70% de total
  - Track: Vendors que hacen login en últimas 24h
- **Products per Vendor**: >10 promedio
  - Track: AVG(COUNT(products) per vendor)
- **Orders Fulfillment Time**: <48 horas promedio
  - Track: AVG(order.confirmed_at - order.created_at)

### 5.17.3 Business Metrics
- **Vendor Retention**: >90% a 30 días
  - Track: Vendors activos después de 30 días / total registered
- **Average Revenue per Vendor**: >$500k COP/mes
  - Track: AVG(SUM(sales) per vendor per month)
- **Vendor Satisfaction Score (NPS)**: >7/10
  - Track: Surveys + reviews

---

# 🚀 DEPLOYMENT & LAUNCH

## 5.18 Deployment Checklist
**Prioridad**: P0 🔥 | **Agente**: `cloud-infrastructure-ai`

### 5.18.1 Pre-Deployment
- [ ] **Task**: Validar todas las migraciones de base de datos
  ```bash
  # Verificar migraciones pendientes
  alembic current
  alembic upgrade head

  # Verificar que vendors table existe
  psql -d mestore -c "\d vendors"
  ```
  **Agente**: `database-architect-ai`

- [ ] **Task**: Configurar variables de entorno
  ```bash
  # Backend .env
  DATABASE_URL=postgresql://...
  SECRET_KEY=...
  SENDGRID_API_KEY=...
  TWILIO_ACCOUNT_SID=...
  FRONTEND_URL=http://192.168.1.137:5173

  # Frontend .env
  VITE_API_URL=http://192.168.1.137:8000
  ```
  **Agente**: `cloud-infrastructure-ai`

- [ ] **Task**: Ejecutar tests completos
  ```bash
  # Backend
  pytest tests/ -v --cov=app

  # Frontend
  cd frontend && npm run test
  ```
  **Agente**: `tdd-specialist`

### 5.18.2 Deployment
- [ ] **Task**: Deploy backend
  ```bash
  # Opción 1: Docker
  docker-compose up -d backend

  # Opción 2: Uvicorn directo
  uvicorn app.main:app --host 0.0.0.0 --port 8000
  ```
  **Agente**: `cloud-infrastructure-ai`

- [ ] **Task**: Deploy frontend
  ```bash
  cd frontend
  npm run build
  npm run preview -- --host 0.0.0.0 --port 5173
  ```
  **Agente**: `cloud-infrastructure-ai`

- [ ] **Task**: Verificar servicios están corriendo
  ```bash
  # Backend health check
  curl http://192.168.1.137:8000/health

  # Frontend accessible
  curl http://192.168.1.137:5173
  ```
  **Agente**: `devops-integration-ai`

### 5.18.3 Post-Deployment Validation
- [ ] **Test**: Registrar vendor de prueba en producción
  **URL**: http://192.168.1.137:5173/vendor/register
  **Verificar**: Registro completo → Login → Dashboard carga

- [ ] **Test**: Crear producto de prueba
  **Verificar**: Producto aparece en lista

- [ ] **Test**: Simular orden y verificar comisión
  **Verificar**: Comisión se calcula correctamente

- [ ] **Test**: Solicitar payout de prueba
  **Verificar**: Payout request llega a admin

**Agente Responsable**: `e2e-testing-ai` + Manual QA

---

## 5.19 Pilot Program
**Prioridad**: P0 🔥 | **Tiempo**: 1 semana

### 5.19.1 Pilot Setup
- [ ] **Task**: Reclutar 5-10 vendors piloto
  **Criterio**:
  - Negocio establecido
  - 10-50 productos listos
  - Dispuestos a dar feedback

  **Agente**: `business-analyst-ai` (estrategia)

- [ ] **Task**: Preparar materiales de onboarding
  - Video tutorial (5 min)
  - Guía rápida PDF
  - FAQ document
  - Grupo WhatsApp de soporte

  **Agente**: `communication-ai`

### 5.19.2 Pilot Execution
- [ ] **Week 1**: Onboarding + Setup
  - Registrar vendors
  - Ayudar a subir primeros productos
  - Resolver dudas

- [ ] **Week 2**: Operations
  - Monitorear uso diario
  - Resolver issues rápidamente
  - Recolectar feedback

- [ ] **Week 3**: Optimization
  - Implementar mejoras basadas en feedback
  - Validar que issues principales están resueltos

### 5.19.3 Success Criteria
- [ ] 80%+ vendors completan onboarding
- [ ] 100+ productos listados
- [ ] 10+ órdenes procesadas
- [ ] 5+ payouts solicitados
- [ ] NPS >7/10

**Si se cumplen**: Proceder a lanzamiento público
**Si no**: Iterar y extender pilot 1 semana más

---

# 📋 ROADMAP POST-MVP (v1.1)

## Features para v1.1 (Mes 2)
**Solo si vendors piden activamente**:

- [ ] Analytics avanzado con gráficos (si >50% vendors lo piden)
- [ ] Multi-step registration con verificación (si abandonment >30%)
- [ ] Inventory alerts automation (si >70% vendors tienen stock issues)
- [ ] Bulk product operations (si vendors tienen >50 productos)
- [ ] Email marketing básico (si vendors piden ayuda con marketing)

## Features para v2.0 (Mes 6+)
**Solo con tracción comprobada**:

- [ ] Mobile app (React Native)
- [ ] Advanced analytics con ML
- [ ] Marketing automation platform
- [ ] Vendor financing program
- [ ] API para integraciones externas

---

# ✅ DEFINITION OF DONE

## Cada Feature está "DONE" cuando:
- [ ] ✅ Backend API implementado y testeado
- [ ] ✅ Frontend component implementado
- [ ] ✅ Tests unitarios passing (>80% coverage)
- [ ] ✅ Integration tests passing
- [ ] ✅ Manual testing completado en http://192.168.1.137
- [ ] ✅ Mobile responsive verificado
- [ ] ✅ Performance <2s load time
- [ ] ✅ No console errors
- [ ] ✅ Code review aprobado
- [ ] ✅ Documentation actualizada

## MVP está "DONE" cuando:
- [ ] ✅ 5-10 vendors reales onboarded
- [ ] ✅ 50+ productos reales listados
- [ ] ✅ 10+ órdenes reales procesadas
- [ ] ✅ 3+ payouts reales solicitados
- [ ] ✅ NPS promedio >7/10
- [ ] ✅ No bugs críticos (P0/P1)
- [ ] ✅ Performance metrics cumplidos
- [ ] ✅ Pilot program exitoso

---

# 📊 RESUMEN EJECUTIVO

## Scope MVP Vendor Flow:
- **Backend**: 6 módulos core (20 endpoints)
- **Frontend**: 5 páginas principales + layout
- **Testing**: Unit + Integration + E2E + Manual
- **Deployment**: Network accessible (192.168.1.137)

## Timeline Realista:
- **Week 1**: Backend APIs (registration, dashboard, products, orders)
- **Week 2**: Frontend pages (registration, dashboard, products, orders, earnings)
- **Week 3**: Testing, bug fixes, pilot setup
- **Total**: 3 semanas con 2 desarrolladores

## Inversión:
- Backend: 80 horas × $50 = $4,000
- Frontend: 120 horas × $50 = $6,000
- Testing: 40 horas × $50 = $2,000
- **Total**: $12,000 USD

## ROI Esperado:
- **Mes 1**: 10 vendors × 20 productos × 2 ventas/mes × 5% comisión × $100k avg = $200k COP comisión
- **Mes 3**: 30 vendors = $600k COP comisión/mes
- **Mes 6**: 70 vendors = $1.4M COP comisión/mes = $350 USD/mes
- **Break-even**: Mes 6-8

## Success Metrics:
- Vendor Registration Completion: >85%
- Time to First Sale: <7 días
- Vendor Retention: >90% a 30 días
- Vendor NPS: >7/10
- Platform Uptime: >99.5%

---

**FILOSOFÍA MVP**: Construir lo MÍNIMO para validar que vendedores:
1. ✅ Pueden registrarse fácilmente
2. ✅ Pueden listar productos sin fricción
3. ✅ Reciben órdenes correctamente
4. ✅ Ven sus ganancias claramente
5. ✅ Pueden solicitar pagos sin problemas

**Si estos 5 puntos funcionan**: Tenemos un MVP viable.
**Si no**: Iterar hasta que funcionen antes de agregar más features.

---

**NEXT STEPS INMEDIATOS**:
1. ✅ Aprobar este TODO MVP
2. ✅ Asignar agentes a tareas
3. ✅ Crear branch `feature/vendor-mvp-flow`
4. ✅ Comenzar con backend registration endpoint
5. ✅ Daily standups para tracking

**Let's ship it! 🚀**
