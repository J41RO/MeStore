# 🚨 INSTRUCCIONES OBLIGATORIAS DEPARTAMENTALES
**LECTURA OBLIGATORIA ANTES DE CUALQUIER TRABAJO**
**Version: 1.0.0**
**Fecha: 14 Septiembre 2025**
**ESTADO: ACTIVO Y OBLIGATORIO**

---

## ⚠️ **ALERTA CRÍTICA DE COORDINACIÓN**

### 🚫 **PROHIBIDO TERMINANTEMENTE:**
- Trabajar sin consultar este manual PRIMERO
- Hacer cambios sin revisar el estado actual del sistema
- Ignorar las configuraciones existentes
- Trabajar sin coordinación con otros departamentos
- Romper funcionalidades que ya están operativas

### ✅ **OBLIGATORIO ANTES DE INICIAR CUALQUIER TAREA:**
1. **LEER** este manual completo
2. **CONSULTAR** PROJECT_CONTEXT.md
3. **VERIFICAR** estado actual del sistema
4. **COORDINAR** con el manager antes de cambios críticos
5. **DOCUMENTAR** todos los cambios realizados

---

## 📊 **ESTADO ACTUAL CRÍTICO DEL SISTEMA**

### ✅ **FUNCIONALIDADES QUE ESTÁN OPERATIVAS:**
- **Autenticación:** super@mestore.com/123456 - ❌ NO TOCAR
- **Backend API:** Puerto 8000 - ❌ NO ROMPER
- **Frontend:** Puerto 5173 - ❌ NO ALTERAR
- **Base de datos:** SQLite funcionando - ❌ NO MODIFICAR ESQUEMA
- **Swagger docs:** /docs disponible - ❌ NO AFECTAR

### 🔒 **ARCHIVOS CRÍTICOS - PROHIBIDO MODIFICAR SIN AUTORIZACIÓN:**
```
/home/admin-jairo/MeStore/app/main.py
/home/admin-jairo/MeStore/app/core/database.py
/home/admin-jairo/MeStore/app/core/security.py
/home/admin-jairo/MeStore/app/services/auth_service.py
/home/admin-jairo/MeStore/app/models/user.py
/home/admin-jairo/MeStore/.env
/home/admin-jairo/MeStore/mestore_production.db
```

---

## 🎯 **PROTOCOLO DE TRABAJO COORDINADO**

### **ANTES DE CUALQUIER MODIFICACIÓN:**

#### **PASO 1: VERIFICACIÓN OBLIGATORIA**
```bash
# 1. Verificar que el sistema esté funcionando
curl http://localhost:8000/health
curl http://localhost:5173

# 2. Verificar autenticación
curl -X POST "http://localhost:8000/api/v1/auth/admin-login" \
     -H "Content-Type: application/json" \
     -d '{"email": "super@mestore.com", "password": "123456"}'

# 3. Si alguno falla - PARAR INMEDIATAMENTE
```

#### **PASO 2: CONSULTA OBLIGATORIA**
- **Para testing:** Consultar PROJECT_CONTEXT.md para entender qué está implementado
- **Para cambios backend:** Verificar que no rompas las APIs existentes
- **Para cambios frontend:** Verificar que no rompas el login ni navegación
- **Para base de datos:** ❌ PROHIBIDO - Consultar manager primero

#### **PASO 3: DOCUMENTACIÓN DE CAMBIOS**
```bash
# OBLIGATORIO: Registrar cambios en el log
echo "$(date): [TU_DEPARTAMENTO] - Cambio realizado: DESCRIPCIÓN" >> .workspace/departments/team/TEAM_CHANGES_LOG.md
```

---

## 📂 **CONFIGURACIONES Y UBICACIONES CRÍTICAS**

### **CONFIGURACIÓN DE AUTENTICACIÓN:**
```
Ubicación: /home/admin-jairo/MeStore/app/core/security.py
Credenciales: super@mestore.com / 123456
Estado: FUNCIONANDO - NO MODIFICAR
```

### **CONFIGURACIÓN DE BASE DE DATOS:**
```
Archivo: /home/admin-jairo/MeStore/.env
DATABASE_URL=sqlite+aiosqlite:///./mestore_production.db
Estado: OPERATIVA - NO CAMBIAR
```

### **CONFIGURACIÓN DEL SERVIDOR:**
```
Backend: Puerto 8000 (FastAPI + Uvicorn)
Frontend: Puerto 5173 (Vite + React)
Estado: FUNCIONANDO - NO ALTERAR PUERTOS
```

### **TESTING - CONFIGURACIONES ESPECÍFICAS:**
```
Framework: pytest (backend), Jest (frontend)
Ubicación tests: /home/admin-jairo/MeStore/tests/
Base de datos test: mestore_test.db (independiente)
❌ NO usar mestore_production.db para tests
```

---

## 🔧 **PROTOCOLO ESPECÍFICO POR DEPARTAMENTO**

### **QA/TESTING AGENTS:**
```
✅ PERMITIDO:
- Crear tests nuevos en /tests/
- Usar base de datos de test separada
- Agregar archivos de test que no afecten producción

❌ PROHIBIDO:
- Modificar mestore_production.db
- Cambiar configuraciones de autenticación
- Alterar esquemas de base de datos existentes
- Modificar archivos core sin autorización
```

### **BACKEND DEVELOPERS:**
```
✅ PERMITIDO:
- Agregar nuevos endpoints (sin romper existentes)
- Crear nuevos servicios
- Agregar middlewares compatibles

❌ PROHIBIDO:
- Modificar auth_service.py sin coordinación
- Cambiar esquemas de User existentes
- Alterar configuraciones de seguridad
```

### **FRONTEND DEVELOPERS:**
```
✅ PERMITIDO:
- Agregar nuevas páginas/componentes
- Mejorar UI sin romper funcionalidad
- Agregar nuevas rutas

❌ PROHIBIDO:
- Modificar sistema de autenticación
- Cambiar rutas de login existentes
- Alterar configuraciones de API calls
```

### **DEVOPS SPECIALISTS:**
```
✅ PERMITIDO:
- Dockerización y deployment
- Configuraciones de producción
- Scripts de automatización

❌ PROHIBIDO:
- Cambiar configuraciones de desarrollo activas
- Modificar .env sin backup
- Alterar puertos en uso
```

---

## 📋 **CHECKLIST OBLIGATORIO ANTES DE TRABAJAR**

### **VERIFICACIÓN INICIAL:**
- [ ] ✅ He leído este manual completo
- [ ] ✅ He consultado PROJECT_CONTEXT.md
- [ ] ✅ He verificado que el sistema funciona actualmente
- [ ] ✅ He identificado qué necesito hacer sin romper lo existente
- [ ] ✅ He coordinado con otros departamentos si es necesario

### **DURANTE EL TRABAJO:**
- [ ] ✅ Estoy documentando cada cambio que hago
- [ ] ✅ Estoy probando que no rompo funcionalidades existentes
- [ ] ✅ Estoy usando ambientes de test apropiados
- [ ] ✅ No estoy tocando archivos críticos sin autorización

### **AL FINALIZAR:**
- [ ] ✅ He verificado que el sistema sigue funcionando
- [ ] ✅ He documentado todos los cambios realizados
- [ ] ✅ He actualizado el log de cambios departamental
- [ ] ✅ He coordinado entrega con el manager

---

## 🚨 **PROTOCOLO DE EMERGENCIA**

### **SI ROMPES ALGO:**
1. **PARAR** inmediatamente todo el trabajo
2. **DOCUMENTAR** exactamente qué hiciste
3. **REVERTIR** los cambios si es posible
4. **REPORTAR** al manager inmediatamente
5. **NO** intentar arreglar solo - puede empeorar

### **SI ENCUENTRAS ALGO ROTO:**
1. **NO** tocar nada más
2. **DOCUMENTAR** el estado actual
3. **REPORTAR** al manager
4. **ESPERAR** instrucciones antes de proceder

---

## 📞 **CONTACTOS DE COORDINACIÓN**

### **PARA CONSULTAS:**
- **Manager Principal:** enterprise-project-manager
- **Coordinación:** Usar el sistema de Task para consultas
- **Emergencias:** Reportar inmediatamente al usuario

### **ESCALACIÓN:**
- **Nivel 1:** Consultar PROJECT_CONTEXT.md
- **Nivel 2:** Consultar con manager a través de Task
- **Nivel 3:** Reportar al usuario directamente

---

## ⚡ **COMANDO DE VERIFICACIÓN RÁPIDA**

**ANTES DE INICIAR CUALQUIER TRABAJO, EJECUTAR:**
```bash
# Verificación rápida del sistema
cd /home/admin-jairo/MeStore
echo "🔍 Verificando estado del sistema..."
curl -s http://localhost:8000/health && echo "✅ Backend OK" || echo "❌ Backend FALLÓ"
curl -s http://localhost:5173 && echo "✅ Frontend OK" || echo "❌ Frontend FALLÓ"
ls -la mestore_production.db && echo "✅ DB existe" || echo "❌ DB NO EXISTE"
echo "📋 Verificación completa"
```

---

**🚨 ESTE MANUAL ES DE CUMPLIMIENTO OBLIGATORIO**
**🚨 NO SEGUIR ESTAS INSTRUCCIONES PUEDE RESULTAR EN REMOCIÓN DEL PROYECTO**
**🚨 CUANDO TENGAS DUDAS, PREGUNTA ANTES DE ACTUAR**

---

*Última actualización: 14 Septiembre 2025*
*Próxima revisión: Cuando haya cambios en el sistema*