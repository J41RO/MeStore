# 🚨 PROTOCOLO OBLIGATORIO DE COORDINACIÓN DEL EQUIPO

## DECLARADO POR: ADMINISTRADOR DEL PROYECTO
## FECHA: 14 Septiembre 2025
## ESTADO: OBLIGATORIO PARA TODOS LOS AGENTES

---

## ⚡ PROBLEMA CRÍTICO IDENTIFICADO

**SITUACIÓN:** Los agentes de seguridad cambiaron la configuración de base de datos de PostgreSQL a SQLite sin coordinación, rompiendo la autenticación que funcionaba correctamente.

**RESULTADO:** Sistema no funcional, pérdida de tiempo, configuración rota.

**CAUSA RAÍZ:** Falta de comunicación y coordinación entre equipos.

---

## 🔒 REGLAS OBLIGATORIAS - SIN EXCEPCIONES

### 1. **REGLA DE NO-CAMBIOS SIN AUTORIZACIÓN**
- ❌ **PROHIBIDO** cambiar configuraciones de base de datos sin autorización explícita
- ❌ **PROHIBIDO** modificar archivos .env sin coordinación
- ❌ **PROHIBIDO** cambiar esquemas de base de datos sin comunicación
- ❌ **PROHIBIDO** asumir que "mejoras" son necesarias sin verificar el estado actual

### 2. **REGLA DE COMUNICACIÓN OBLIGATORIA**
- ✅ **OBLIGATORIO** documentar todos los cambios en este archivo: `TEAM_CHANGES_LOG.md`
- ✅ **OBLIGATORIO** verificar el estado actual antes de hacer cambios
- ✅ **OBLIGATORIO** coordinar con otros equipos antes de modificaciones mayores
- ✅ **OBLIGATORIO** probar que el sistema funciona después de cambios

### 3. **REGLA DE VERIFICACIÓN DE ESTADO**
- ✅ **ANTES** de hacer cambios: Verificar que el sistema funciona
- ✅ **DURANTE** los cambios: Documentar cada modificación
- ✅ **DESPUÉS** de los cambios: Probar que todo sigue funcionando

---

## 📋 ESTADO ACTUAL DEL SISTEMA (BASELINE)

### **CONFIGURACIÓN FUNCIONANDO:**
- **Base de datos:** PostgreSQL (postgresql+asyncpg://postgres:password@localhost:5432/mestocker)
- **Credenciales admin:** super@mestore.com / 123456
- **Backend URL:** http://192.168.1.137:8000
- **Frontend URL:** http://192.168.1.137:5173
- **Estado:** FUNCIONAL (antes de cambios de seguridad)

### **PROBLEMAS CREADOS POR CAMBIOS NO COORDINADOS:**
1. Cambio de PostgreSQL a SQLite sin autorización
2. Modificación de autenticación que rompió el login
3. Cambios en modelos de base de datos sin migraciones
4. "Mejoras de seguridad" que crearon vulnerabilidades

---

## 🔧 PROCESO OBLIGATORIO PARA CAMBIOS

### **PASO 1: VERIFICACIÓN PRE-CAMBIO**
```bash
# Verificar estado actual del sistema
curl -X POST http://192.168.1.137:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "super@mestore.com", "password": "123456"}'

# Documentar resultado en TEAM_CHANGES_LOG.md
```

### **PASO 2: DOCUMENTACIÓN OBLIGATORIA**
```markdown
## [FECHA] - [AGENTE] - [TIPO DE CAMBIO]
**ANTES:** [Estado del sistema]
**CAMBIO:** [Descripción detallada]
**DESPUÉS:** [Resultado esperado]
**PRUEBA:** [Comando para verificar]
**ESTADO:** [EXITOSO/FALLIDO]
```

### **PASO 3: VERIFICACIÓN POST-CAMBIO**
```bash
# Probar que el sistema sigue funcionando
# Si falla, ROLLBACK inmediato
```

---

## 🚫 CAMBIOS PROHIBIDOS SIN AUTORIZACIÓN

### **CONFIGURACIONES CRÍTICAS:**
- ❌ `DATABASE_URL` en .env
- ❌ Credenciales de usuario (super@mestore.com)
- ❌ Esquemas de base de datos
- ❌ Configuraciones de autenticación
- ❌ URLs de servicios principales

### **ARCHIVOS PROTEGIDOS:**
- ❌ `.env` - Solo con autorización explícita
- ❌ `app/models/user.py` - Solo con migraciones coordinadas
- ❌ `app/core/config.py` - Solo cambios documentados
- ❌ `app/services/auth_service.py` - Solo con pruebas

---

## 📞 ESCALACIÓN OBLIGATORIA

### **ANTES DE CAMBIOS CRÍTICOS:**
1. Consultar con enterprise-project-manager
2. Documentar en TEAM_CHANGES_LOG.md
3. Obtener aprobación explícita
4. Ejecutar con monitoreo

### **SI ALGO SE ROMPE:**
1. ROLLBACK inmediato
2. Documentar el problema
3. Notificar a todos los equipos
4. NO intentar "arreglar" sin coordinación

---

## 🎯 RESPONSABILIDADES POR EQUIPO

### **SECURITY-AUDIT-SPECIALIST:**
- ✅ Analizar vulnerabilidades SIN cambiar configuración
- ❌ NO cambiar base de datos sin autorización
- ✅ Documentar recomendaciones en lugar de implementar

### **BACKEND-SENIOR-DEVELOPER:**
- ✅ Cambios de código con pruebas
- ❌ NO cambiar esquemas sin migraciones
- ✅ Coordinar cambios de base de datos

### **QA-ENGINEER-PYTEST:**
- ✅ Probar funcionalidad existente antes de cambios
- ✅ Validar que cambios no rompen funcionalidad
- ❌ NO asumir que "mejoras" son necesarias

### **DEVOPS-DEPLOYMENT-SPECIALIST:**
- ✅ Despliegue con configuración aprobada
- ❌ NO cambiar configuraciones sin documentar
- ✅ Mantener respaldos de configuración

---

## 📝 ARCHIVO DE CAMBIOS OBLIGATORIO

**UBICACIÓN:** `/home/admin-jairo/MeStore/.workspace/departments/team/TEAM_CHANGES_LOG.md`

**FORMATO OBLIGATORIO:**
```markdown
## 2025-09-14 - [AGENTE] - [CAMBIO]
**ANTES:** Sistema funcionando con PostgreSQL
**CAMBIO:** [Descripción detallada]
**PRUEBA:** [Comando de verificación]
**RESULTADO:** [EXITOSO/FALLIDO/ROLLBACK]
**APROBADO POR:** [Administrador/Manager]
---
```

---

## ⚖️ CONSECUENCIAS POR INCUMPLIMIENTO

### **PRIMERA VIOLACIÓN:**
- Advertencia documentada
- Rollback obligatorio del cambio
- Revisión del protocolo

### **SEGUNDA VIOLACIÓN:**
- Restricción de permisos de cambio
- Supervisión obligatoria

### **TERCERA VIOLACIÓN:**
- Remoción de acceso a modificaciones críticas

---

## 🔥 REGLA DE ORO

> **"SI NO ESTÁ ROTO, NO LO ARREGLES"**
> **"SI FUNCIONA, NO LO CAMBIES SIN COORDINACIÓN"**
> **"DOCUMENTA TODO, ASUME NADA"**

---

## 📋 CHECKLIST OBLIGATORIO PARA CUALQUIER CAMBIO

- [ ] ¿El sistema funciona actualmente?
- [ ] ¿He documentado el estado PRE-cambio?
- [ ] ¿He consultado con otros equipos?
- [ ] ¿Tengo autorización para este cambio?
- [ ] ¿He preparado un plan de rollback?
- [ ] ¿He documentado el cambio en TEAM_CHANGES_LOG.md?
- [ ] ¿He probado que el sistema funciona POST-cambio?

**SI CUALQUIER RESPUESTA ES "NO" → NO PROCEDER**

---

## 🚨 ESTADO DE EMERGENCIA ACTUAL

**PROBLEMA:** Login de superusuario roto por cambios no coordinados
**ACCIÓN INMEDIATA:** Restaurar configuración funcional
**RESPONSABLES:** Todos los agentes que modificaron configuración
**PRIORIDAD:** CRÍTICA - Bloquea despliegue a producción

---

**ESTE PROTOCOLO ES OBLIGATORIO Y NO NEGOCIABLE**
**CUMPLIMIENTO: 100% REQUERIDO**
**REVISIÓN: DIARIA HASTA RESTABLECER CONFIANZA**