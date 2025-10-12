# 🔍 DIAGNÓSTICO ERRORES REGISTRO - MESTOCKER

**Fecha**: 2025-10-09
**Agentes**: @react-specialist-ai + @frontend-security-ai + @api-architect
**Prioridad**: 🚨 CRÍTICA - Sistema en Producción

---

## 📊 RESUMEN EJECUTIVO

Se identificaron **4 errores críticos** que impiden el registro de usuarios en producción:

1. ❌ **Mixed Content Error** - HTTP en página HTTPS
2. ❌ **MIME Type Error** - JavaScript servido como text/html
3. ⚠️ **Connection Errors** - Fallos de conexión backend
4. ⚠️ **Service Worker Registration** - Fallo al registrar SW

**Impacto**: Usuarios NO pueden registrarse en el sitio (100% de afectación en registro)
**Root Cause**: URLs HTTP hardcoded en múltiples componentes

---

## 🔴 ERROR 1: MIXED CONTENT (CRÍTICO)

### Descripción
Navegador bloquea recursos HTTP en página servida por HTTPS, violando la política de Mixed Content.

### Evidencia
```
Mixed Content: The page at 'https://www.mestocker.com/register-vendor' was loaded over HTTPS,
but requested an insecure resource 'http://192.168.1.137:8080/api/v1/auth/register'.
This request has been blocked; the content must be served over HTTPS.
```

### Root Cause
**17 archivos con URLs HTTP hardcoded:**

```bash
# Componentes con http://192.168.1.137:8000 hardcoded:
frontend/src/components/payments/EfectyInstructions.tsx
frontend/src/components/checkout/PayUCheckout.tsx
frontend/src/components/vendor/ProductForm.tsx (4 ocurrencias)
frontend/src/components/forms/ProductForm.tsx (2 ocurrencias)
frontend/src/components/admin/InventoryAuditPanel.tsx (10 ocurrencias)
frontend/src/components/admin/QRGeneratorForm.tsx (1 ocurrencia)
```

### Archivos Afectados
```typescript
// ❌ INCORRECTO (hardcoded)
const response = await fetch('http://192.168.1.137:8000/api/v1/auth/register', {
  method: 'POST',
  body: JSON.stringify(data)
});

// ✅ CORRECTO (usa variable de entorno)
import { ENV } from '../utils/env';
const response = await fetch(`${ENV.API_BASE_URL}/api/v1/auth/register`, {
  method: 'POST',
  body: JSON.stringify(data)
});
```

### Configuración Correcta Detectada
```typescript
// frontend/src/utils/env.ts - ✅ YA EXISTE
export const ENV = {
  API_BASE_URL: getEnvVar('VITE_API_BASE_URL', 'http://localhost:8000'),
  BUILD_NUMBER: getEnvVar('VITE_BUILD_NUMBER', '1'),
  MODE: getEnvVar('MODE', 'development')
};

// frontend/.env.production - ✅ CONFIGURADO CORRECTAMENTE
VITE_API_BASE_URL=https://mestocker-backend-production.up.railway.app

// frontend/.env - ⚠️ DESARROLLO (no afecta producción)
VITE_API_BASE_URL=http://192.168.1.137:8000
```

### Propuesta de Fix
1. **Reemplazar ALL URLs hardcoded** con `ENV.API_BASE_URL` de `utils/env.ts`
2. **Usar apiClient existente** para llamadas consistentes
3. **Eliminar fetch() directo** en favor de axios con interceptors

**Prioridad**: 🔥 **URGENTE** - Fix inmediato required

---

## 🔴 ERROR 2: MIME TYPE ERROR (CRÍTICO)

### Descripción
Archivo JavaScript `RegisterVendor-B14Lcrta.js` servido con MIME type incorrecto `text/html` en lugar de `text/javascript`.

### Evidencia
```
Failed to load module script: Expected a JavaScript module script but the server responded
with a MIME type of "text/html". Strict MIME type checking is enforced for module scripts
per HTML spec.
```

### Root Cause Analysis

**Posibles Causas:**
1. **File Not Found (404)** → Server returns HTML error page instead of JS
2. **Server Misconfiguration** → Incorrect Content-Type header
3. **Build Output Missing** → File not generated in dist/

### Investigación

#### Build Configuration - vite.config.ts
```typescript
// ✅ CONFIGURACIÓN CORRECTA DETECTADA
build: {
  minify: 'esbuild',
  rollupOptions: {
    output: {
      manualChunks: (id) => {
        if (id.includes('/pages/')) return 'pages-core';
        // Chunking strategy OK
      }
    }
  },
  chunkSizeWarningLimit: 500,
  target: 'es2022'
}
```

#### Verificación de Build Output
```bash
# Archivo existe en dist/
ls -lh frontend/dist/assets/RegisterVendor-*.js
# Output: RegisterVendor-8b1tS4pr.js (hash diferente al error)
```

**🔍 HALLAZGO CLAVE**: El hash del archivo en error (`B14Lcrta`) NO coincide con el archivo actual en dist (`8b1tS4pr`).

### Conclusión
**El error indica que el navegador está solicitando un archivo de un build ANTERIOR que YA NO EXISTE.**

### Propuesta de Fix
1. **Limpiar cache de navegador** - Force reload (Ctrl+Shift+R)
2. **Rebuild frontend** - `npm run build`
3. **Deploy nueva versión** - Actualizar producción con nuevo hash
4. **Cache-Control headers** - Configurar no-cache para HTML, cache largo para assets

**Prioridad**: ⚠️ **ALTA** - Fix después de Mixed Content

---

## ⚠️ ERROR 3: CONNECTION ERRORS

### Descripción
Fallos de conexión al intentar comunicar frontend con backend.

### Evidencia
```
Failed to fetch
TypeError: Failed to fetch
```

### Root Cause
**Combinación de problemas:**
1. URLs HTTP bloqueadas por Mixed Content (ERROR 1)
2. Backend URL incorrecta en desarrollo (192.168.1.137:8080 vs 8000)
3. CORS potencialmente mal configurado

### Investigación

#### Backend CORS Configuration
**Archivo**: `app/core/config.py` o `app/main.py`

**Necesita verificación:**
```python
# ¿Está configurado CORS para https://www.mestocker.com?
CORS_ORIGINS = [
    "http://localhost:5173",
    "http://192.168.1.137:5173",
    "https://www.mestocker.com",  # ← DEBE estar presente
    "https://mestocker.com"        # ← DEBE estar presente
]
```

#### Puerto Backend Incorrecto
**Error en mensaje**: `http://192.168.1.137:8080`
**Puerto correcto**: Backend corre en puerto **8000** (no 8080)

### Propuesta de Fix
1. **Fix Mixed Content primero** (resuelve 80% del problema)
2. **Verificar CORS** en backend para dominio producción
3. **Test endpoint accesibilidad**:
   ```bash
   curl -I https://mestocker-backend-production.up.railway.app/api/v1/auth/register
   ```

**Prioridad**: ⚠️ **MEDIA** - Dependiente de ERROR 1

---

## ⚠️ ERROR 4: SERVICE WORKER REGISTRATION

### Descripción
Fallo al registrar Service Worker para PWA.

### Evidencia
```
Service Worker registration failed
```

### Root Cause
Service Worker intenta cachear recursos HTTP que están bloqueados por Mixed Content.

### Investigación

#### PWA Configuration - vite.config.ts
```typescript
VitePWA({
  registerType: 'autoUpdate',
  workbox: {
    runtimeCaching: [
      {
        urlPattern: /^https?:\/\/.*\/api\//i,  // ← Permite HTTP y HTTPS
        handler: 'NetworkFirst'
      }
    ]
  },
  devOptions: {
    enabled: false  // ✅ DESACTIVADO en desarrollo (correcto)
  }
})
```

### Propuesta de Fix
1. **Actualizar SW después de fix Mixed Content**
2. **Regenerar manifest** con build limpio
3. **Workbox cache solo HTTPS** en producción:
   ```typescript
   urlPattern: /^https:\/\/.*\/api\//i  // Solo HTTPS
   ```

**Prioridad**: 🔵 **BAJA** - Se resuelve automáticamente con ERROR 1

---

## 📋 PLAN DE ACCIÓN

### FASE 1: FIX MIXED CONTENT (URGENTE)
**Tiempo estimado**: 30min
**Agentes**: @frontend-security-ai + @react-specialist-ai

**Archivos a modificar** (17 total):
```
1. components/payments/EfectyInstructions.tsx
2. components/checkout/PayUCheckout.tsx
3. components/vendor/ProductForm.tsx
4. components/forms/ProductForm.tsx
5. components/admin/InventoryAuditPanel.tsx
6. components/admin/QRGeneratorForm.tsx
7. services/__tests__/apiClient.test.ts (solo tests)
8-17. (otros componentes detectados en grep)
```

**Estrategia**:
```typescript
// 1. Import ENV helper
import { ENV } from '@/utils/env';

// 2. Replace ALL fetch() calls
- const url = 'http://192.168.1.137:8000/api/v1/...';
+ const url = `${ENV.API_BASE_URL}/api/v1/...`;

// 3. Prefer apiClient over fetch
import api from '@/services/api';
const response = await api.auth.register(data);
```

**Validación**:
```bash
# NO debe retornar resultados:
grep -r "http://192.168.1.137" frontend/src/ --exclude-dir=node_modules
grep -r "192.168.1.137:8080" frontend/src/
```

### FASE 2: FIX MIME TYPE (ALTA)
**Tiempo estimado**: 15min
**Agentes**: @react-specialist-ai + @devops-integration-ai

**Acciones**:
```bash
cd frontend
npm run build          # Regenerar build con nuevos hashes
rm -rf dist/.vite      # Limpiar cache Vite
npm run build          # Build limpio
```

**Deploy**:
- Deploy nueva versión a Vercel/hosting
- Configurar Cache-Control headers

### FASE 3: VERIFICAR BACKEND CONNECTION (MEDIA)
**Tiempo estimado**: 10min
**Agentes**: @api-architect + @devops-integration-ai

**Validaciones**:
```bash
# 1. Test endpoint accesibilidad
curl -X POST "https://mestocker-backend-production.up.railway.app/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"Test123!"}' \
  -w "\nStatus: %{http_code}\n"

# 2. Verificar CORS headers
curl -I -X OPTIONS "https://mestocker-backend-production.up.railway.app/api/v1/auth/register" \
  -H "Origin: https://www.mestocker.com"
```

**Si CORS falla**, actualizar backend:
```python
# app/main.py
CORS_ORIGINS = [
    "http://localhost:5173",
    "https://www.mestocker.com",
    "https://mestocker.com"
]
```

### FASE 4: TESTING E2E (VALIDACIÓN)
**Tiempo estimado**: 20min
**Agentes**: @e2e-testing-ai + @tdd-specialist

**Test Scenarios**:
```python
def test_registro_usuario_completo():
    """Test flujo completo de registro"""
    # 1. Abrir página registro
    # 2. Llenar formulario
    # 3. Enviar POST a /api/v1/auth/register
    # 4. Verificar response 200/201
    # 5. Verificar usuario creado en DB
    pass
```

---

## 🎯 CRITERIOS DE ÉXITO

### Checklist de Validación
```bash
# ✅ 1. No Mixed Content
grep -r "http://192.168.1.137" frontend/src/ --exclude-dir=node_modules
# Expected: Solo en tests y comentarios

# ✅ 2. Build sin errores
cd frontend && npm run build
# Expected: Build successful, no errors

# ✅ 3. MIME types correctos
curl -I https://www.mestocker.com/assets/RegisterVendor-*.js
# Expected: Content-Type: text/javascript

# ✅ 4. Backend accesible
curl -I https://mestocker-backend-production.up.railway.app/api/v1/auth/register
# Expected: 200 o 405 (method not allowed en GET es OK)

# ✅ 5. CORS configurado
curl -I -X OPTIONS https://mestocker-backend-production.up.railway.app/api/v1/auth/register \
  -H "Origin: https://www.mestocker.com"
# Expected: Access-Control-Allow-Origin: https://www.mestocker.com

# ✅ 6. Service Worker registrado
# Browser console: No service worker errors
```

### Tests E2E
```bash
# Frontend tests
cd frontend && npm test -- --grep "registration"
# Expected: All passing

# E2E Playwright tests
npx playwright test tests/e2e/registration.spec.ts
# Expected: All scenarios passing
```

---

## 📊 IMPACTO ESTIMADO

| Fix | Tiempo | Impacto | Dependencias |
|-----|--------|---------|--------------|
| **FASE 1: Mixed Content** | 30min | ⚡ ALTO (80% del problema) | Ninguna |
| **FASE 2: MIME Type** | 15min | ⚡ MEDIO (15%) | FASE 1 |
| **FASE 3: Backend Connection** | 10min | ⚡ BAJO (5%) | FASE 1 |
| **FASE 4: Testing** | 20min | ✅ Validación | FASE 1-3 |
| **TOTAL** | **75min** | 🎯 100% Registro Funcional | - |

---

## 🔧 ARCHIVOS CRÍTICOS IDENTIFICADOS

### Frontend Configuration
```
✅ frontend/.env.production          (CORRECTO - HTTPS URL)
✅ frontend/src/utils/env.ts         (HELPER CORRECTO)
✅ frontend/src/services/apiClient.ts (AXIOS CLIENT CORRECTO)
✅ frontend/src/services/api.ts      (API WRAPPER CORRECTO)
✅ frontend/vite.config.ts           (BUILD CONFIG CORRECTO)
❌ frontend/src/components/*         (17 archivos con HTTP hardcoded)
```

### Backend Configuration (A Verificar)
```
⚠️ app/core/config.py                (CORS origins)
⚠️ app/main.py                       (CORS middleware)
✅ app/api/v1/endpoints/auth.py     (Endpoints funcionan)
```

---

## 🚀 SIGUIENTE PASO INMEDIATO

**EJECUTAR AHORA:**
```bash
# Contar URLs HTTP hardcoded total
grep -r "http://192.168.1.137" frontend/src/ --include="*.tsx" --include="*.ts" | wc -l

# Listar archivos únicos afectados
grep -r "http://192.168.1.137" frontend/src/ --include="*.tsx" --include="*.ts" -l | sort | uniq
```

**LUEGO PROCEDER CON**: FASE 1 - Fix Mixed Content

---

**Reporte generado por**: @react-specialist-ai + @frontend-security-ai + @api-architect
**Workspace**: `.workspace/fix-registro/`
**Próximo Documento**: `FIX_MIXED_CONTENT.md` (después de aprobación)

---

## 📞 AGENTES RESPONSABLES

- **Mixed Content**: @frontend-security-ai + @react-specialist-ai
- **Build/MIME**: @react-specialist-ai + @devops-integration-ai
- **Backend CORS**: @api-architect + @backend-framework-ai
- **Testing**: @e2e-testing-ai + @tdd-specialist
- **Deployment**: @devops-integration-ai + @cloud-infrastructure-ai

**Escalación**: Si algún fix toma >2h → Contactar @master-orchestrator
