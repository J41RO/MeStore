# 🔧 REQUISITOS TÉCNICOS OBLIGATORIOS

## ⚠️ CONFIGURACIONES QUE NO SE DEBEN CAMBIAR

### 🌐 URLs y Puertos del Sistema
```bash
# NUNCA CAMBIAR ESTOS VALORES
BACKEND_URL="http://192.168.1.137:8000"
FRONTEND_URL="http://192.168.1.137:5173"
BACKEND_PORT=8000
FRONTEND_PORT=5173
```

### 🔧 Configuración de Proxy (Vite)
```typescript
// frontend/vite.config.ts - CONFIGURACIÓN VERIFICADA
proxy: {
  "/api": {
    target: "http://192.168.1.137:8000",  // NO CAMBIAR A localhost
    changeOrigin: true,
    secure: false
  }
}
```

### 🌍 Variables de Entorno Obligatorias
```bash
# frontend/.env - VERIFICADO FUNCIONANDO
VITE_API_BASE_URL=http://192.168.1.137:8000/api/v1

# frontend/.env.development - VERIFICADO FUNCIONANDO
VITE_API_BASE_URL=http://192.168.1.137:8000
VITE_LOG_ENDPOINT=http://192.168.1.137:8000/api/logs
```

### 👥 Usuarios del Sistema (EXISTENTES - NO DUPLICAR)
```bash
# USUARIOS VERIFICADOS Y ACTIVOS
admin@test.com / admin123   # ADMIN - ID: admin-test-001
vendor@test.com / vendor123 # VENDOR - ID: vendor-test-001
buyer@test.com / buyer123   # BUYER - ID: buyer-test-001
```

---

## 🏗️ ARQUITECTURA VERIFICADA

### 🔐 Sistema de Autenticación
- **Servicio Principal**: `IntegratedAuthService` ✅ Funcional
- **Servicio Legacy**: `AuthService` ✅ Fallback disponible
- **AuthStore**: `frontend/src/stores/authStore.ts` ✅ Zustand + persist
- **Endpoints**: `/api/v1/auth/login`, `/api/v1/auth/me` ✅ HTTP 200

### 🎯 Tipos de Usuario Verificados
```typescript
// Backend (UPPERCASE) → Frontend (enum)
"ADMIN" → UserType.ADMIN
"VENDOR" → UserType.VENDOR
"BUYER" → UserType.BUYER
"SUPERUSER" → UserType.SUPERUSER
```

### 🔄 Flujo de Integración Verificado
1. Frontend:5173 → Proxy Vite → Backend:8000 ✅
2. Login → JWT Token → AuthStore → Persist ✅
3. Auth/me → User Data → Type Conversion ✅

---

## 🚨 REGLAS OBLIGATORIAS PARA AGENTES

### ❌ PROHIBIDO:
- Cambiar puertos 8000/5173
- Modificar URLs de 192.168.1.137
- Crear usuarios admin@test.com, vendor@test.com, buyer@test.com
- Cambiar configuración proxy de localhost a 192.168.1.137
- Modificar IntegratedAuthService sin justificación

### ✅ PERMITIDO:
- Crear usuarios de prueba con formato: `test_[tipo]_[timestamp]@example.com`
- Agregar nuevos endpoints manteniendo arquitectura
- Extender AuthStore con nuevas funciones
- Mejorar servicios manteniendo compatibilidad

### 🔍 ANTES DE CUALQUIER CAMBIO:
1. Verificar que no afecte configuraciones críticas
2. Probar integración frontend-backend
3. Validar usuarios existentes siguen funcionando
4. Confirmar proxy Vite sigue operativo

---

**Creado**: 2025-09-19 05:20 UTC
**Estado**: Configuración técnica verificada y funcional
**Próxima Revisión**: Solo si hay problemas de integración