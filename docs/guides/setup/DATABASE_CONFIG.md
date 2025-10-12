# 🗄️ Configuración de Base de Datos - MeStore

## ⚠️ BASE DE DATOS ÚNICA - CONSOLIDADA

**Fecha de consolidación:** 2025-09-29
**Estado:** ✅ CONSOLIDADO - Una sola base de datos en todo el proyecto

---

## 📍 Base de Datos Principal

**Archivo:** `mestore_production.db`
**Ruta completa:** `/home/admin-jairo/MeStore/mestore_production.db`
**Tamaño:** ~1.1 MB
**Motor:** SQLite con driver `aiosqlite` (async)

### 🔧 Configuración en Archivos

#### 1. `.env` (Configuración de entorno)
```bash
DATABASE_URL=sqlite+aiosqlite:///./mestore_production.db
```

#### 2. `app/core/config.py` (Configuración por defecto)
```python
DATABASE_URL: str = Field(
    default="sqlite+aiosqlite:///./mestore_production.db",
    description="SQLite database URL - ÚNICA BASE DE DATOS PARA TODO EL SISTEMA",
)
```

#### 3. `alembic.ini` (Configuración de migraciones)
```ini
[alembic]
sqlalchemy.url = sqlite:///./mestore_production.db
```

---

## 📊 Schema de Base de Datos

### Tablas Principales (34 totales)

**Usuarios y Autenticación:**
- `users` - Usuarios del sistema (incluye OAuth Google)
- `admin_permissions` - Permisos administrativos
- `admin_user_permissions` - Asignación de permisos
- `admin_activity_logs` - Logs de actividad admin

**Productos y Catálogo:**
- `products` - Catálogo de productos
- `categories` - Categorías de productos
- `product_categories` - Relación productos-categorías
- `product_images` - Imágenes de productos

**Órdenes y Transacciones:**
- `orders` - Órdenes de compra
- `order_items` - Items de órdenes
- `order_transactions` - Transacciones de órdenes

**Pagos:**
- `payments` - Registro de pagos
- `payment_methods` - Métodos de pago
- `payment_intents` - Intenciones de pago
- `payment_refunds` - Reembolsos
- `webhook_events` - Eventos de webhooks

**Inventario:**
- `inventory` - Control de inventario
- `storages` - Almacenes
- `inventory_audits` - Auditorías de inventario
- `inventory_audit_items` - Items auditados
- `movement_tracker` - Rastreo de movimientos
- `movimientos_stock` - Movimientos de stock
- `incidentes_inventario` - Incidentes
- `incoming_product_queue` - Cola de productos entrantes

**Vendors:**
- `vendor_documents` - Documentos de vendors
- `vendor_notes` - Notas de vendors
- `vendor_audit_logs` - Logs de auditoría

**Comisiones y Pagos a Vendors:**
- `commissions` - Comisiones
- `commission_disputes` - Disputas de comisiones
- `payout_requests` - Solicitudes de pago
- `payout_history` - Historial de pagos

**Sistema:**
- `system_settings` - Configuraciones del sistema
- `transactions` - Transacciones generales
- `discrepancy_reports` - Reportes de discrepancias

---

## 🔐 Columnas Google OAuth en `users`

La tabla `users` incluye las siguientes columnas para autenticación con Google:

```sql
google_id VARCHAR(100)              -- ID único de Google
google_email VARCHAR(255)           -- Email de Google
google_name VARCHAR(200)            -- Nombre completo de Google
google_picture VARCHAR(500)         -- URL de foto de perfil
google_verified_email BOOLEAN       -- Email verificado por Google
oauth_provider VARCHAR(50)          -- Proveedor OAuth (google)
oauth_linked_at DATETIME            -- Fecha de vinculación OAuth
```

---

## 🚫 Bases de Datos ELIMINADAS

Las siguientes bases de datos fueron eliminadas durante la consolidación:

- ❌ `mestore_development.db` (vacía)
- ❌ `mestore_main.db` (vacía)

**Razón:** Evitar confusión y garantizar una única fuente de verdad para los datos.

---

## 🔄 Migraciones con Alembic

### Aplicar migraciones
```bash
source .venv/bin/activate
alembic upgrade head
```

### Crear nueva migración
```bash
alembic revision --autogenerate -m "descripción del cambio"
```

### Ver historial de migraciones
```bash
alembic history
```

### Ver versión actual
```bash
alembic current
```

---

## 📝 Servicios Configurados

### Twilio SMS
- ✅ `TWILIO_ACCOUNT_SID`: AC6a938935d463d476368eac88ccf565ff
- ✅ `TWILIO_AUTH_TOKEN`: Configurado
- ✅ `TWILIO_FROM_NUMBER`: +17622631579
- ✅ `SMS_ENABLED`: true

### Email SMTP (Gmail)
- ✅ `EMAIL_HOST`: smtp.gmail.com
- ✅ `EMAIL_PORT`: 587
- ✅ `EMAIL_USE_TLS`: true

### Google OAuth
- ✅ `GOOGLE_CLIENT_ID`: Configurado
- ✅ `GOOGLE_CLIENT_SECRET`: Configurado

---

## ⚠️ IMPORTANTE - Política de Base de Datos Única

### ✅ HACER:
- Usar siempre `mestore_production.db`
- Verificar que `.env` apunte a esta base de datos
- Aplicar migraciones sobre esta base de datos
- Hacer backups regulares de esta base de datos

### ❌ NO HACER:
- Crear nuevas bases de datos `.db` en el proyecto
- Modificar `DATABASE_URL` sin consultar este documento
- Usar bases de datos diferentes en desarrollo vs producción
- Eliminar `mestore_production.db` sin backup

---

## 🔄 Backup y Restauración

### Crear backup
```bash
cp /home/admin-jairo/MeStore/mestore_production.db \
   /home/admin-jairo/MeStore/backups/mestore_production_$(date +%Y%m%d_%H%M%S).db
```

### Restaurar backup
```bash
cp /home/admin-jairo/MeStore/backups/mestore_production_YYYYMMDD_HHMMSS.db \
   /home/admin-jairo/MeStore/mestore_production.db
```

---

## 📞 Soporte

Si necesitas modificar la configuración de base de datos:

1. Consulta este documento primero
2. Verifica que el cambio sea necesario
3. Haz backup antes de cualquier cambio
4. Actualiza este documento con los cambios realizados

---

**Última actualización:** 2025-09-29
**Responsable:** Sistema de consolidación automática