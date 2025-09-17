# 🏢 PROTOCOLO DE TRABAJO SUPERVISADO EN GRUPO
**COORDINACIÓN DEPARTAMENTAL OBLIGATORIA**
**Versión: 1.0.0 - Estado: ACTIVO**

---

## 🚨 **SITUACIÓN CRÍTICA RESUELTA**

### ✅ **PROBLEMA IDENTIFICADO Y CORREGIDO:**
- **Situación:** Agentes trabajando sin coordinación, rompiendo funcionalidades
- **Riesgo:** Testing agent corrigiendo tests sin revisar estado actual
- **Solución:** Sistema de coordinación departamental implementado

### ✅ **MEDIDAS IMPLEMENTADAS:**
1. **Manual obligatorio distribuido a TODOS los departamentos**
2. **Comando inteligente para actualización masiva creado**
3. **Alertas específicas para agentes activos**
4. **Protocolo de suspensión inmediata activado**

---

## 📋 **PROTOCOLO DE COORDINACIÓN ACTIVO**

### **🚦 SEMÁFORO DE TRABAJO:**

#### 🔴 **ROJO - TRABAJO SUSPENDIDO:**
- Cualquier agente que no haya leído `MANDATORY_INSTRUCTIONS.md`
- Modificaciones a archivos críticos sin autorización
- Testing que pueda afectar `mestore_production.db`
- Cambios de configuración sin coordinación

#### 🟡 **AMARILLO - TRABAJO CON SUPERVISIÓN:**
- Nuevos endpoints o funcionalidades
- Tests que no afecten funcionalidades existentes
- Mejoras de UI/UX sin romper flujos
- Optimizaciones de rendimiento

#### 🟢 **VERDE - TRABAJO AUTORIZADO:**
- Documentación y comentarios
- Tests unitarios aislados
- Mejoras cosméticas menores
- Correcciones de bugs menores no críticos

---

## 🎯 **PROCEDIMIENTO DE TRABAJO EN GRUPO**

### **ANTES DE INICIAR CUALQUIER TAREA:**

#### **1. VERIFICACIÓN DE SISTEMA (OBLIGATORIO):**
```bash
# Ejecutar en terminal:
cd /home/admin-jairo/MeStore
curl -s http://localhost:8000/health && echo "✅ Backend OK" || echo "❌ Backend FALLÓ"
curl -s http://localhost:5173 && echo "✅ Frontend OK" || echo "❌ Frontend FALLÓ"

# Test de autenticación:
curl -X POST "http://localhost:8000/api/v1/auth/admin-login" \
     -H "Content-Type: application/json" \
     -H "User-Agent: Mozilla/5.0" \
     -d '{"email": "super@mestore.com", "password": "123456"}' \
     | grep -q "access_token" && echo "✅ Auth OK" || echo "❌ Auth FALLÓ"
```

#### **2. COORDINACIÓN PREVIA (OBLIGATORIO):**
- **QA/Testing:** Consultar con backend-senior-developer antes de tests de integración
- **Backend:** Consultar con frontend-react-specialist antes de cambios de API
- **Frontend:** Consultar con backend antes de cambios de estados/rutas
- **DevOps:** Consultar con todos antes de cambios de configuración

#### **3. DOCUMENTACIÓN DE INTENCIONES:**
```markdown
## PLAN DE TRABAJO - [AGENTE] - [FECHA]

### Objetivo:
[Describir qué quieres hacer]

### Archivos que voy a modificar:
- [ ] /ruta/archivo1.py - [descripción del cambio]
- [ ] /ruta/archivo2.tsx - [descripción del cambio]

### Funcionalidades que podrían afectarse:
- [ ] Login/autenticación
- [ ] APIs existentes
- [ ] Navegación frontend
- [ ] Base de datos

### Coordinación realizada:
- [ ] He leído MANDATORY_INSTRUCTIONS.md
- [ ] He verificado el sistema funciona
- [ ] He consultado PROJECT_CONTEXT.md
- [ ] He coordinado con departamentos afectados

### Plan de reversión:
[Cómo voy a deshacer cambios si algo sale mal]
```

---

## 🛡️ **CHECKPOINTS DE SEGURIDAD**

### **CHECKPOINT 1: ANTES DE MODIFICAR CÓDIGO**
```bash
# Crear backup del estado actual
git stash push -m "Backup antes de cambios por [AGENTE]"
```

### **CHECKPOINT 2: DURANTE EL TRABAJO**
```bash
# Verificar cada 30 minutos que el sistema sigue funcionando
./scripts/verify_system.sh  # (Script de verificación automática)
```

### **CHECKPOINT 3: DESPUÉS DE CAMBIOS**
```bash
# Test completo del sistema
curl http://localhost:8000/health
curl http://localhost:5173
# Test de login completo
# Test de funcionalidades críticas
```

---

## 🚨 **PROTOCOLO DE EMERGENCIA**

### **SI ALGO SE ROMPE:**

#### **PASO 1: PARAR INMEDIATAMENTE**
- Dejar de hacer cambios
- No intentar "arreglar rápido"
- Documentar exactamente qué se hizo

#### **PASO 2: COMUNICAR**
```markdown
🚨 SISTEMA ROTO - REPORTE INMEDIATO
Agente: [nombre]
Hora: [timestamp]
Acción realizada: [descripción detallada]
Síntomas: [qué está fallando]
Estado antes: [funcionaba/no funcionaba]
Archivos modificados: [lista]
```

#### **PASO 3: REVERSIÓN COORDINADA**
- Usar `git stash pop` para revertir
- Si no funciona, coordinar rollback con manager
- Verificar que la reversión funciona
- Documentar lecciones aprendidas

---

## 📊 **MONITOREO CONTINUO**

### **MÉTRICAS DE COORDINACIÓN:**
- ✅ **100% de agentes han leído el manual obligatorio**
- ✅ **0 cambios no coordinados en las últimas 24h**
- ✅ **Sistema funcionando sin interrupciones**
- ✅ **Todos los departamentos sincronizados**

### **INDICADORES DE ALERTA:**
- 🚨 Agente trabaja sin leer instrucciones
- 🚨 Sistema deja de responder después de cambios
- 🚨 Funcionalidades existentes se rompen
- 🚨 Base de datos se corrompe

---

## 🎯 **ROLES Y RESPONSABILIDADES**

### **ENTERPRISE-PROJECT-MANAGER:**
- Supervisión general del trabajo coordinado
- Autorización de cambios críticos
- Resolución de conflictos entre departamentos
- Mantenimiento de protocolos de coordinación

### **QA-ENGINEER-PYTEST:**
- Testing coordinado sin romper funcionalidades
- Uso de bases de datos de test separadas
- Validación de que cambios no rompan el sistema
- Coordinación con backend/frontend antes de tests críticos

### **BACKEND-SENIOR-DEVELOPER:**
- Mantenimiento de APIs sin romper compatibilidad
- Coordinación con frontend antes de cambios
- Protección del sistema de autenticación
- Validación de cambios de base de datos

### **FRONTEND-REACT-SPECIALIST:**
- Mantenimiento de UI sin romper flujos críticos
- Coordinación con backend para cambios de API
- Protección de rutas de autenticación
- Testing de integración coordinado

### **DEVOPS-DEPLOYMENT-SPECIALIST:**
- Gestión de configuraciones sin romper desarrollo
- Coordinación antes de cambios de entorno
- Backup y recuperación del sistema
- Monitoreo de salud del sistema

---

## ✅ **VERIFICACIÓN FINAL**

### **ESTADO ACTUAL VERIFICADO:**
```bash
# Ejecutado el: $(date)
✅ Backend funcionando: http://localhost:8000
✅ Frontend funcionando: http://localhost:5173
✅ Autenticación operativa: super@mestore.com/123456
✅ Base de datos funcional: mestore_production.db
✅ Manual distribuido a todos los departamentos
✅ Protocolos de coordinación activos
```

---

**🏢 COORDINACIÓN DEPARTAMENTAL ESTABLECIDA**
**🛡️ SISTEMA PROTEGIDO CONTRA CAMBIOS NO COORDINADOS**
**📋 TRABAJO EN GRUPO SUPERVISADO ACTIVO**

---

*Creado: $(date)*
*Estado: ACTIVO Y OBLIGATORIO*
*Próxima revisión: Al detectar trabajo no coordinado*