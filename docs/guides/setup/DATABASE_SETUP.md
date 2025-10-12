# 🗄️ DATABASE SETUP - MeStocker

## 📋 CONFIGURACIÓN COMPLETA Y FUNCIONAL

**Fecha**: 2025-09-29
**Estado**: ✅ **OPERATIVO**

---

## 🎯 BASE DE DATOS ÚNICA

### Archivo Principal
```
mestore.db (1.1 MB)
Ubicación: /home/admin-jairo/MeStore/mestore.db
```

### Backup Disponible
```
mestore_production.db.backup
Ubicación: /home/admin-jairo/MeStore/mestore_production.db.backup
```

---

## 🔐 CREDENCIALES SUPERUSUARIO

```
Email:    admin@mestocker.com
Password: Admin123456
Tipo:     SUPERUSER
ID:       bcdf48ce-9e40-493e-a455-304de7fa010c
```

**Estado**: ✅ Activo y Verificado

---

## ⚙️ CONFIGURACIÓN DE ARCHIVOS

### 1. `.env` (Principal)
```bash
DATABASE_URL=sqlite+aiosqlite:///./mestore.db
```

### 2. `.env.development` (Development Override)
```bash
DATABASE_URL=sqlite+aiosqlite:///./mestore.db
```

### 3. `app/core/config.py` (Default Fallback)
```python
DATABASE_URL: str = Field(
    default="sqlite+aiosqlite:///./mestore.db",
    description="SQLite database URL - ÚNICA BASE DE DATOS PARA TODO EL SISTEMA",
)
```

### 4. `app/database/__init__.py` (Engine Configuration)
```python
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mestore.db")
ASYNC_DATABASE_URL = DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://")
```

### 5. `app/core/integrated_auth.py` (Authentication)
```python
from app.core.config import settings
db_path = settings.DATABASE_URL.replace("sqlite+aiosqlite://", "").replace("sqlite://", "").lstrip("/")
conn = sqlite3.connect(db_path)
```

### 6. `app/services/auth_service.py` (Auth Service)
```python
from app.core.config import settings
db_path = settings.DATABASE_URL.replace("sqlite+aiosqlite://", "").replace("sqlite://", "").lstrip("/")
conn = sqlite3.connect(db_path)
```

---

## 📊 ESQUEMA DE BASE DE DATOS

### Tablas Creadas (34 totales)

```
✅ admin_activity_logs       ✅ movement_tracker
✅ admin_permissions          ✅ movimientos_stock
✅ admin_user_permissions     ✅ order_items
✅ categories                 ✅ order_transactions
✅ commission_disputes        ✅ orders
✅ commissions                ✅ payment_intents
✅ discrepancy_reports        ✅ payment_methods
✅ incidentes_inventario      ✅ payment_refunds
✅ incoming_product_queue     ✅ payments
✅ inventory                  ✅ payout_history
✅ inventory_audit_items      ✅ payout_requests
✅ inventory_audits           ✅ product_categories
✅ product_images             ✅ webhook_events
✅ products                   ✅ storages
✅ system_settings            ✅ transactions
✅ users                      ✅ vendor_audit_logs
✅ vendor_documents           ✅ vendor_notes
```

---

## 🚀 BACKEND OPERATIVO

### Servidor FastAPI
```
URL:  http://192.168.1.137:8000
Docs: http://192.168.1.137:8000/docs
```

### Estado del Servicio
```bash
✅ Uvicorn running on http://192.168.1.137:8000
✅ ChromaDB initialized successfully
✅ Application startup completed successfully
```

---

## 🧪 PRUEBA DE LOGIN EXITOSA

### Endpoint de Autenticación
```bash
curl -X POST "http://192.168.1.137:8000/api/v1/auth/admin-login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@mestocker.com", "password": "Admin123456"}'
```

### Respuesta Esperada
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "bcdf48ce-9e40-493e-a455-304de7fa010c",
    "email": "admin@mestocker.com",
    "nombre": "Admin",
    "apellido": "MeStocker",
    "user_type": "SUPERUSER",
    "is_active": true,
    "is_verified": true
  }
}
```

**Estado**: ✅ **LOGIN EXITOSO** con JWT tokens generados correctamente

---

## 🔄 PROCEDIMIENTOS DE MANTENIMIENTO

### Crear Backup Manual
```bash
cp mestore.db mestore.db.backup_$(date +%Y%m%d_%H%M%S)
```

### Recrear Esquema desde Cero
```bash
# 1. Backup
cp mestore.db mestore.db.backup

# 2. Eliminar base de datos
rm mestore.db

# 3. Recrear esquema
python create_schema.py

# 4. Crear superusuario
python create_superuser.py

# 5. Reiniciar backend
pkill -f uvicorn
uvicorn app.main:app --host 192.168.1.137 --port 8000 --reload
```

### Verificar Integridad
```bash
# Ver tablas
sqlite3 mestore.db ".tables"

# Contar usuarios
sqlite3 mestore.db "SELECT COUNT(*) FROM users;"

# Ver superusuario
sqlite3 mestore.db "SELECT id, email, user_type, is_active FROM users WHERE user_type='SUPERUSER';"
```

---

## ⚠️ PROBLEMAS CONOCIDOS Y SOLUCIONES

### Problema: "no such table: users"
**Causa**: Pydantic-settings carga `.env.development` antes de `.env`
**Solución**: Asegurar que TODOS los archivos .env tengan `DATABASE_URL=sqlite+aiosqlite:///./mestore.db`

### Problema: Backend no encuentra la base de datos
**Causa**: Rutas hardcodeadas en el código
**Solución**: Todos los archivos usan `settings.DATABASE_URL` dinámicamente

### Problema: Login devuelve 401 o 500
**Causa**: Base de datos incorrecta o sin tablas
**Solución**:
1. Verificar que `mestore.db` existe y tiene tablas
2. Verificar que `.env.development` apunta a `mestore.db`
3. Reiniciar backend completamente

---

## 📂 ARCHIVOS MODIFICADOS EN LA CORRECCIÓN

1. ✅ `.env` - DATABASE_URL actualizada
2. ✅ `.env.development` - DATABASE_URL corregida
3. ✅ `app/core/config.py` - Default actualizado
4. ✅ `app/database/__init__.py` - Default corregido
5. ✅ `app/core/integrated_auth.py` - Usa settings.DATABASE_URL
6. ✅ `app/services/auth_service.py` - Usa settings.DATABASE_URL

---

## 🎉 ESTADO FINAL

```
✅ Base de datos única: mestore.db
✅ Esquema completo: 34 tablas creadas
✅ Superusuario activo: admin@mestocker.com
✅ Backend operativo: http://192.168.1.137:8000
✅ Login funcional: JWT tokens generados
✅ Configuración unificada: Todos los archivos apuntan a mestore.db
✅ Backup disponible: mestore_production.db.backup
```

**🚀 SISTEMA 100% OPERATIVO Y LISTO PARA USO**

---

## 📞 SOPORTE

Para cualquier problema con la base de datos:

1. Verificar que `mestore.db` existe en el directorio raíz
2. Verificar que `.env.development` tiene `DATABASE_URL=sqlite+aiosqlite:///./mestore.db`
3. Reiniciar backend: `pkill -f uvicorn && uvicorn app.main:app --host 192.168.1.137 --port 8000 --reload`
4. Verificar login: `curl -X POST http://192.168.1.137:8000/api/v1/auth/admin-login ...`

---

**Última actualización**: 2025-09-29 17:30:00
**Responsable**: Claude Code - Database Consolidation Task