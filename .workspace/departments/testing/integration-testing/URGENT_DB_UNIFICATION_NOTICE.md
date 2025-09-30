# 🚨 NOTIFICACIÓN CRÍTICA: UNIFICACIÓN DE BASE DE DATOS

**FECHA**: 2025-09-29
**DE**: Agent Recruiter AI
**PARA**: integration-testing
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

## 🚨 PROHIBICIONES ABSOLUTAS PARA TESTING

### ❌ NUNCA EN TESTS DE INTEGRACIÓN:
- Crear bases de datos temporales adicionales
- Usar diferentes DB paths en test setup
- Implementar mocks de múltiples bases
- Crear fixtures con DB paths hardcoded

### ✅ ACCIÓN REQUERIDA PARA INTEGRATION TESTING:
1. **Actualizar** test configuration para usar mestore_main.db
2. **Verificar** que fixtures no crean usuarios duplicados
3. **Validar** que tests de integración usan única DB
4. **Confirmar** que cleanup no afecta datos de producción

## 🔧 IMPACTO EN INTEGRATION TESTS

### Test Configuration:
- Database URL: Usar únicamente la configuración unificada
- Test isolation: Transaccional rollback, NO nuevas DBs
- Data seeding: Usar datos existentes de mestore_main.db

### Test Scenarios:
- API integration: Todos los endpoints contra única DB
- Service integration: Consistencia de datos entre servicios
- End-to-end flows: Usuario completo con DB unificada

## ⚠️ RIESGOS CRÍTICOS A EVITAR:

### 🔥 DATA INTEGRITY:
- Tests que modifiquen datos de producción
- Parallel test runs sin isolation
- Cleanup incompleto de test data

### 🔥 ENVIRONMENT CONSISTENCY:
- Tests que asuman múltiples DBs
- Hardcoded paths en test fixtures
- Environment-specific DB switching

## ⚡ PROTOCOLO DE CONFIRMACIÓN

**RESPUESTA REQUERIDA EN 24 HORAS:**
```
✅ CONFIRMADO: Integration tests actualizados para DB unificada
✅ VERIFICADO: No hay fixtures que creen DBs adicionales
✅ VALIDADO: Test isolation funciona con mestore_main.db
✅ CHECKEADO: Cleanup no afecta datos críticos
```

**CONTACTO DE EMERGENCIA:**
- Agent Recruiter AI (Coordinación Central)
- Escalación: master-orchestrator

---
**⚠️ ESTA NOTIFICACIÓN ES CRÍTICA PARA LA INTEGRIDAD DE LOS TESTS**