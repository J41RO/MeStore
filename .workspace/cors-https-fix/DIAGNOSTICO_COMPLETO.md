# 🔍 DIAGNÓSTICO COMPLETO - CORS + HTTPS FIX

**Fecha**: 2025-10-09 20:45 UTC
**Squad**: @backend-framework-ai @api-security @cloud-architect-ai @security-backend-ai
**Problema**: Mixed Content + CORS Policy Blocking en producción

---

## 🚨 PROBLEMA IDENTIFICADO

### Error Principal en Consola:
```
Access to fetch at 'https://mestocker-backend-production.up.railway.app/api/v1/auth/register'
from origin 'https://www.mestocker.com' has been blocked by CORS policy:
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

### Errores Secundarios:
1. **Mixed Content Error**: HTTP request desde HTTPS page
2. **ERR_FAILED**: Todas las peticiones al backend fallando

---

## 📂 ARQUITECTURA DEL BACKEND

### 1. Archivo Principal FastAPI

**Ubicación**: `/home/admin-jairo/MeStore/app/main.py`

**Configuración Actual**:
```python
# Líneas 155-157
logger_early.info("DEBUG: Setting up application middleware...")
setup_application_middleware(app)
logger_early.info("DEBUG: Application middleware setup completed")
```

**Observación**:
- ✅ Utiliza `setup_application_middleware()` para configurar CORS
- ⚠️ No hay configuración CORS inline en main.py (delega a middleware_integration_simple.py)

---

### 2. Archivo de Producción Alternativo

**Ubicación**: `/home/admin-jairo/MeStore/app/main_production.py`

**Configuración CORS**:
```python
# Líneas 47-57
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ❌ PROBLEMA: Wildcard en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=3600,
)
```

**Observación**:
- ❌ **CRÍTICO**: `allow_origins=["*"]` con `allow_credentials=True` es INVÁLIDO
- ⚠️ Comentario dice "En producción, específica los dominios reales" pero no lo hace
- 🔴 Este archivo podría estar siendo usado en Railway

---

### 3. Middleware Integration (Archivo Principal de CORS)

**Ubicación**: `/home/admin-jairo/MeStore/app/core/middleware_integration_simple.py`

**Configuración CORS Actual** (líneas 23-81):

```python
# Base origins from settings.CORS_ORIGINS
base_origins = [
    origin.strip()
    for origin in settings.CORS_ORIGINS.split(",")
    if origin.strip() and not origin.strip().startswith("https://*")
]

# Hardcoded Vercel origins
vercel_origins = [
    "https://me-store-alpha.vercel.app",
    "https://me-store-4rch67v8-jairos-projects-6e49f915.vercel.app",
]

# Development localhost
if settings.ENVIRONMENT == "development":
    localhost_origins = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]
    allowed_origins = list(set(base_origins + localhost_origins + vercel_origins))
else:
    # Production: combine base_origins with Vercel origins
    allowed_origins = list(set(base_origins + vercel_origins))

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=3600,
)
```

**Análisis**:
- ✅ NO usa wildcard `["*"]`
- ✅ Maneja environment-specific origins
- ❌ **PROBLEMA CRÍTICO**: `https://www.mestocker.com` **NO ESTÁ EN LA LISTA**
- ⚠️ Vercel URLs hardcoded (debería venir de env vars)

---

## 🔧 CONFIGURACIÓN DE VARIABLES DE ENTORNO

### 1. Config Settings (app/core/config.py)

**Línea 139-142**:
```python
CORS_ORIGINS: str = Field(
    default="http://localhost:5173,http://localhost:3000,http://192.168.1.137:5173,http://192.168.1.137:5175,http://192.168.1.137:5176,https://me-store-alpha.vercel.app,https://me-store-4rch67v8-jairos-projects-6e49f915.vercel.app,https://*.vercel.app",
    description="Comma-separated list of allowed CORS origins (Vercel wildcard permitted)"
)
```

**Observación**:
- ❌ **PROBLEMA CRÍTICO**: `https://www.mestocker.com` **NO ESTÁ EN DEFAULT**
- ⚠️ Tiene IPs locales (desarrollo) pero no producción
- ⚠️ Wildcard `https://*.vercel.app` (no soportado por FastAPI CORS)

---

### 2. Environment File (.env)

**Ubicación**: `/home/admin-jairo/MeStore/.env`

**Línea 4**:
```bash
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://192.168.1.137:5173
```

**Observación**:
- ❌ **PROBLEMA**: Solo tiene localhost/IPs locales
- ❌ **FALTA**: `https://www.mestocker.com`
- ❌ **FALTA**: URLs de producción

---

## 🌐 PRODUCCIÓN - RAILWAY ENVIRONMENT

### Railway debe tener estas variables:

**ENVIRONMENT VARIABLES NECESARIAS**:
```bash
ENVIRONMENT=production
CORS_ORIGINS=https://www.mestocker.com,https://me-store-alpha.vercel.app
DATABASE_URL=postgresql+asyncpg://...  # Railway PostgreSQL
SECRET_KEY=<secure-32-chars-minimum>
```

**Estado Actual (ESPECULACIÓN)**:
- ⚠️ Railway probablemente NO tiene `CORS_ORIGINS` configurado
- ⚠️ O usa defaults de config.py que no incluyen www.mestocker.com
- ⚠️ Posible que esté usando `main_production.py` con `allow_origins=["*"]`

---

## 🔍 URLS HARDCODED

### Backend (app/):
```bash
grep -r "http://mestocker-backend" app/ --include="*.py"
# Resultado: No hardcoded HTTP backend URLs found ✅
```

### Frontend URL en CORS:
```bash
grep -r "https://www.mestocker.com" app/core/ --include="*.py"
# Resultado: NO ENCONTRADO ❌
```

**Conclusión**: `https://www.mestocker.com` **NO ESTÁ CONFIGURADO** en ningún lado del backend.

---

## 📊 MATRIZ DE DIAGNÓSTICO

| Componente | Estado | Problema Identificado |
|-----------|--------|----------------------|
| **main.py** | ✅ Correcto | Delega CORS a middleware_integration_simple |
| **main_production.py** | ❌ CRÍTICO | `allow_origins=["*"]` inválido con credentials |
| **middleware_integration_simple.py** | ⚠️ INCOMPLETO | Falta `https://www.mestocker.com` |
| **config.py CORS_ORIGINS default** | ❌ INCOMPLETO | Solo localhost y Vercel, falta producción |
| **.env CORS_ORIGINS** | ❌ SOLO DEV | Solo localhost, sin producción |
| **Railway CORS_ORIGINS** | ❓ DESCONOCIDO | Probablemente no configurado |

---

## 🎯 CAUSA RAÍZ IDENTIFICADA

### PROBLEMA 1: CORS Origin Missing
**Frontend**: `https://www.mestocker.com`
**Backend CORS Allowed**: NO INCLUYE `www.mestocker.com`

**Efecto**:
```
Access-Control-Allow-Origin header is not present
```

### PROBLEMA 2: Railway Environment Variables
**Probable**: Railway NO tiene `CORS_ORIGINS` configurado
**Fallback**: Usa defaults de config.py que no incluyen producción

### PROBLEMA 3: main_production.py Potencial
**Si Railway usa**: `main_production.py`
**Problema**: `allow_origins=["*"]` + `allow_credentials=True` = **INVÁLIDO**

---

## 🚨 IMPACTO

### Usuarios Afectados:
- ❌ **100% de usuarios** en https://www.mestocker.com/
- ✅ 0% en localhost (funciona en dev)
- ❓ Vercel URLs (probablemente funcionan)

### Funcionalidades Bloqueadas:
- ❌ Registro de usuarios
- ❌ Login
- ❌ Todas las API calls
- ❌ Backend completamente inaccesible

---

## 📋 ARCHIVOS CLAVE PARA FIX

### Backend Files:
```
/home/admin-jairo/MeStore/app/main.py
/home/admin-jairo/MeStore/app/main_production.py
/home/admin-jairo/MeStore/app/core/middleware_integration_simple.py
/home/admin-jairo/MeStore/app/core/config.py
```

### Environment Files:
```
/home/admin-jairo/MeStore/.env (development)
Railway Dashboard → Environment Variables (production)
```

---

## 🔧 FIX STRATEGY (Preliminar)

### FASE 2: Backend Fix
1. ✅ Agregar `https://www.mestocker.com` a `middleware_integration_simple.py`
2. ✅ Agregar a `config.py` CORS_ORIGINS default
3. ⚠️ Decidir: ¿Usar main.py o main_production.py en Railway?
4. ✅ Fix `main_production.py` si se usa (remover wildcard)

### FASE 3: Railway Environment
1. 🔧 Configurar `CORS_ORIGINS` en Railway Dashboard
2. 🔧 Agregar `https://www.mestocker.com` explícitamente
3. 🔧 Verificar `ENVIRONMENT=production`

### FASE 4: Validación
1. 🧪 Test endpoint directo con curl
2. 🧪 Verificar headers CORS en response
3. 🧪 Test desde frontend producción

---

## ✅ CHECKLIST DE VALIDACIÓN

- [x] Localizado archivo principal FastAPI (main.py)
- [x] Identificado archivo de producción (main_production.py)
- [x] Revisado middleware CORS (middleware_integration_simple.py)
- [x] Analizado config settings (config.py)
- [x] Revisado .env local
- [x] Identificado causa raíz (missing www.mestocker.com)
- [x] Verificado no hay URLs HTTP hardcoded
- [ ] Verificar configuración Railway (requiere acceso a dashboard)

---

## 📞 PRÓXIMOS PASOS

**APROBACIÓN REQUERIDA DEL DIRECTOR**:

1. ¿Confirmar que Railway usa `main.py` o `main_production.py`?
2. ¿Acceso a Railway Dashboard para verificar env vars?
3. ¿Proceder con FASE 2 - Backend Fix?

**EQUIPO ASIGNADO**:
- @backend-framework-ai - Fix CORS middleware
- @api-security - Validar security headers
- @cloud-architect-ai - Railway configuration
- @security-backend-ai - HTTPS enforcement

---

**Generado por**: react-specialist-ai (líder temporal del squad)
**Timestamp**: 2025-10-09T20:45:00Z
**Status**: ✅ **DIAGNÓSTICO COMPLETADO**
**Próxima Fase**: APROBACIÓN DIRECTOR → FASE 2 FIX
