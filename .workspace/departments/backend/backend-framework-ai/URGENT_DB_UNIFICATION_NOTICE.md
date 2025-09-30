# 🚨 NOTIFICACIÓN CRÍTICA: UNIFICACIÓN DE BASE DE DATOS

**FECHA**: 2025-09-29
**DE**: Agent Recruiter AI
**PARA**: backend-framework-ai
**PRIORIDAD**: MÁXIMA

## 📊 NUEVA CONFIGURACIÓN OBLIGATORIA

### ✅ BASE DE DATOS UNIFICADA COMPLETADA

**ÚNICA FUENTE DE VERDAD:**
- **Archivo**: `mestore_main.db` (1.5MB SQLite)
- **Ruta absoluta**: `/home/admin-jairo/MeStore/mestore_main.db`
- **URL conexión**: `sqlite+aiosqlite:////home/admin-jairo/MeStore/mestore_main.db`
- **Configuración**: `app/core/config.py` línea 13

### 📈 DATOS EXISTENTES VERIFICADOS:
- ✅ **132 usuarios** (incluye admin@mestocker.com)
- ✅ **85 productos** activos
- ✅ **Tablas completas** del sistema

## 🚨 PROHIBICIONES ABSOLUTAS

### ❌ NUNCA CREAR:
- Bases de datos adicionales (`mestore_production.db`, `mestore_development.db`)
- Conexiones a bases alternas
- Usuarios duplicados en desarrollo
- Migraciones que cambien la ubicación de la DB

### ✅ ACCIÓN REQUERIDA:
1. **Verificar** que todas las conexiones apunten a `mestore_main.db`
2. **Actualizar** documentación de backend si es necesario
3. **Confirmar** que servicios usan única configuración de DB
4. **Validar** que no hay hardcoded DB paths en código

## 🔧 IMPACTO EN BACKEND FRAMEWORK

### FastAPI Configuration:
- Database dependency: Usar `app/core/database.py`
- Session management: AsyncSessionLocal configurado
- Connection pooling: SQLite optimizado con NullPool

### Service Layer:
- Todos los servicios deben usar única instancia DB
- No crear servicios con DB paths hardcoded
- Validar que migrations apunten a mestore_main.db

## ⚡ PROTOCOLO DE CONFIRMACIÓN

**RESPUESTA REQUERIDA EN 24 HORAS:**
```
✅ CONFIRMADO: Backend framework actualizado para mestore_main.db
✅ VERIFICADO: No hay conexiones a bases adicionales
✅ VALIDADO: Servicios usan configuración unificada
```

**CONTACTO DE EMERGENCIA:**
- Agent Recruiter AI (Coordinación Central)
- Escalación: master-orchestrator

---
**⚠️ ESTA NOTIFICACIÓN ES CRÍTICA PARA LA INTEGRIDAD DEL SISTEMA**