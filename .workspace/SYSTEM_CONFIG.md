# 🔧 CONFIGURACIÓN DEL SISTEMA MESTORE

## 🌐 Endpoints del Sistema
**NO CAMBIAR ESTOS VALORES - CONFIGURACIÓN ESTABLE**

### Backend API
- **URL**: `http://192.168.1.137:8000`
- **Puerto**: 8000
- **Estado**: ✅ Activo y funcionando
- **Documentación**: `http://192.168.1.137:8000/docs`

### Frontend Application
- **URL**: `http://192.168.1.137:5173`
- **Puerto**: 5173
- **Estado**: ✅ Activo y funcionando
- **Framework**: React + Vite + TypeScript

---

## 👥 USUARIOS DE PRUEBA DEL SISTEMA
**USUARIOS PREEXISTENTES - NO CREAR DUPLICADOS**

### 🔑 Usuario Administrador
- **Email**: `admin@test.com`
- **Password**: `admin123`
- **Tipo**: `ADMIN`
- **Estado**: ✅ **ACTIVO Y VERIFICADO**

### 🔑 Usuario Vendedor
- **Email**: `vendor@test.com`
- **Password**: `vendor123`
- **Tipo**: `VENDOR`
- **Estado**: ✅ **ACTIVO Y VERIFICADO**

### 🔑 Usuario Comprador
- **Email**: `buyer@test.com`
- **Password**: `buyer123`
- **Tipo**: `BUYER`
- **Estado**: ✅ **ACTIVO Y VERIFICADO**

---

## 📋 INSTRUCCIONES PARA AGENTES

### ⚠️ REGLAS CRÍTICAS
1. **NO CAMBIAR** las URLs de backend y frontend
2. **NO CREAR** usuarios con estos emails si ya existen
3. **USAR ESTOS USUARIOS** para pruebas de autenticación
4. **VERIFICAR EXISTENCIA** antes de crear usuarios de prueba

### 🧪 Creación de Nuevos Usuarios de Prueba
- Solo crear usuarios de prueba cuando se esté probando el flujo de registro
- Usar emails únicos con formato: `test_[tipo]_[timestamp]@example.com`
- Ejemplo: `test_vendor_20250919@example.com`

### 🔍 Verificación de Usuario
Para verificar si un usuario existe:
```bash
curl -X POST "http://192.168.1.137:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "[EMAIL]", "password": "[PASSWORD]"}'
```

---

**Fecha de Creación**: 2025-09-19
**Última Actualización**: 2025-09-19 05:20 UTC
**Estado**: ✅ Sistema completamente verificado y funcional

---

## 🔧 CONFIGURACIONES TÉCNICAS CRÍTICAS

### Proxy de Vite (CORREGIDO)
```typescript
// frontend/vite.config.ts
proxy: {
  "/api": {
    target: "http://192.168.1.137:8000",  // CORREGIDO de localhost
    changeOrigin: true,
    secure: false
  }
}
```

### Variables de Entorno Verificadas
```bash
# frontend/.env
VITE_API_BASE_URL=http://192.168.1.137:8000/api/v1

# frontend/.env.development
VITE_API_BASE_URL=http://192.168.1.137:8000
VITE_LOG_ENDPOINT=http://192.168.1.137:8000/api/logs
```

### AuthStore Verificado
- **Ubicación**: `frontend/src/stores/authStore.ts` ✅ EXISTE
- **Estado**: Funcional con Zustand + persist
- **Funciones**: login, logout, checkAuth, validateSession, refreshUserInfo
- **Conversión de tipos**: Backend UPPERCASE → Frontend enum

---

## 🛡️ DATOS DE SEGURIDAD VERIFICADOS

### Endpoints de Autenticación Funcionando
- **Login**: `POST /api/v1/auth/login` ✅ HTTP 200
- **User Info**: `GET /api/v1/auth/me` ✅ HTTP 200
- **JWT Validation**: ✅ Tokens válidos/inválidos correctamente procesados
- **User Types**: ✅ ADMIN/VENDOR/BUYER identificación correcta

### Servicios de Auth Integrados
- **Primary**: IntegratedAuthService ✅ Funcional
- **Fallback**: AuthService (legacy) ✅ Disponible
- **Conflictos**: ✅ Resueltos completamente

**Última Actualización**: 2025-09-19 05:20 UTC
**Estado**: ✅ Sistema completamente verificado y funcional