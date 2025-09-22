# 🤖 PROTOCOLO OBLIGATORIO PARA AGENTES

## 📋 CHECKLIST ANTES DE CUALQUIER MODIFICACIÓN

### ✅ PASO 1: VERIFICACIÓN INICIAL (OBLIGATORIO)
```
□ Leer .workspace/SYSTEM_RULES.md
□ Consultar .workspace/PROTECTED_FILES.md
□ Verificar si archivo está en lista protegida
□ Revisar .workspace/project/[archivo].md para metadatos
□ Identificar agente responsable del archivo
```

### ✅ PASO 2: EVALUACIÓN DE RIESGO
```
□ Archivo NIVEL CRÍTICO (❌) → PROHIBIDO modificar
□ Archivo ALTO RIESGO (⚠️) → Requiere consulta
□ Archivo NORMAL (✅) → Modificación permitida
□ Verificar historial de problemas en metadatos
```

### ✅ PASO 3: PROTOCOLO DE CONSULTA
```
□ Si es archivo protegido → Contactar agente responsable
□ Si es crítico para autenticación → security-backend-ai
□ Si es configuración servidor → system-architect-ai
□ Si es modelo DB → database-architect-ai
□ Si es Docker → cloud-infrastructure-ai
```

### ✅ PASO 4: ANTES DE IMPLEMENTAR
```
□ Obtener aprobación si es requerida
□ Crear backup mental del estado actual
□ Planificar qué tests ejecutar después
□ Verificar dependencies que podrían afectarse
```

### ✅ PASO 5: IMPLEMENTACIÓN SEGURA
```
□ Hacer cambios mínimos incrementales
□ Ejecutar tests relevantes inmediatamente
□ Verificar que servicios siguen funcionando
□ Documentar cambio en commit detallado
```

### ✅ PASO 6: VALIDACIÓN POST-CAMBIO
```
□ Ejecutar suite completa de tests
□ Verificar que autenticación sigue funcionando
□ Confirmar que servicios levantan correctamente
□ Actualizar metadatos del archivo si es necesario
```

## 🎯 PROTOCOLOS ESPECÍFICOS POR TIPO DE AGENTE

### 👑 AGENTES EJECUTIVOS
**master-orchestrator, director-enterprise-ceo, personal-assistant, communication-hub-ai**

```
✅ PERMISOS: Todos los archivos (con responsabilidad)
⚠️ RESPONSABILIDAD: Coordinar otros agentes antes de modificar
🔄 PROTOCOLO: Delegar a especialistas cuando sea posible
```

### 🏗️ AGENTES DE ARQUITECTURA
**system-architect-ai, api-architect-ai, database-architect-ai, etc.**

```
✅ PERMISOS: Archivos de su especialidad
⚠️ RESTRICCIÓN: Consultar con otros arquitectos para cambios globales
🔄 PROTOCOLO: Diseñar antes de implementar
```

### ⚙️ AGENTES BACKEND
**backend-framework-ai, security-backend-ai, api-security, etc.**

```
✅ PERMISOS: Archivos backend específicos de su área
❌ PROHIBIDO: Modificar configuración de puertos/Docker
🔄 PROTOCOLO: Validar con tests de integración
```

### 🎨 AGENTES FRONTEND
**react-specialist-ai, frontend-performance-ai, pwa-specialist, etc.**

```
✅ PERMISOS: Archivos frontend específicos
❌ PROHIBIDO: Modificar configuración Vite ports
🔄 PROTOCOLO: Verificar compatibilidad con backend
```

### 🧪 AGENTES TESTING
**tdd-specialist, unit-testing-ai, integration-testing, etc.**

```
✅ PERMISOS: Archivos de tests y fixtures
❌ PROHIBIDO CRÍTICO: Crear usuarios duplicados en tests
🔄 PROTOCOLO: Usar fixtures existentes SIEMPRE
```

### 🛡️ AGENTES SEGURIDAD
**security-backend-ai, cybersecurity-ai, api-security, etc.**

```
✅ PERMISOS: Archivos de seguridad y autenticación
⚠️ RESPONSABILIDAD CRÍTICA: Mantener auth funcionando
🔄 PROTOCOLO: Probar login/roles después de cambios
```

### ☁️ AGENTES INFRAESTRUCTURA
**cloud-infrastructure-ai, devops-integration-ai, monitoring-ai, etc.**

```
✅ PERMISOS: Docker, configs infraestructura
❌ PROHIBIDO: Cambiar puertos sin coordinación global
🔄 PROTOCOLO: Verificar todos los servicios después
```

## 🚨 CASOS DE USO CRÍTICOS

### 🔥 CASO 1: "Quiero crear usuarios para testing"
```
❌ NO HACER: Crear nuevos usuarios en test individual
✅ HACER: Usar fixtures de tests/conftest.py
🔍 VERIFICAR: No hay usuarios duplicados
👤 RESPONSABLE: tdd-specialist debe validar
```

### 🔥 CASO 2: "Necesito cambiar configuración de servidor"
```
❌ NO HACER: Modificar puertos en main.py o docker-compose
✅ HACER: Consultar con system-architect-ai primero
🔍 VERIFICAR: Frontend mantiene conexión
👤 RESPONSABLE: system-architect-ai decide
```

### 🔥 CASO 3: "Voy a arreglar la autenticación"
```
❌ NO HACER: Modificar auth.py sin consultar
✅ HACER: Contactar security-backend-ai obligatoriamente
🔍 VERIFICAR: Login sigue funcionando después
👤 RESPONSABLE: security-backend-ai ÚNICAMENTE
```

### 🔥 CASO 4: "Necesito agregar un campo a User model"
```
❌ NO HACER: Modificar directamente app/models/user.py
✅ HACER: Consultar database-architect-ai + crear migración
🔍 VERIFICAR: No romper constraints existentes
👤 RESPONSABLE: database-architect-ai supervisa
```

## 📞 MATRIZ DE CONTACTOS POR PROBLEMA

### Problemas de Autenticación/Login
```
👤 CONTACTAR: security-backend-ai
📁 ARCHIVOS: app/api/v1/deps/auth.py, app/services/auth_service.py
🔄 TIEMPO RESPUESTA: Inmediato (crítico)
```

### Problemas de Base de Datos/Modelos
```
👤 CONTACTAR: database-architect-ai
📁 ARCHIVOS: app/models/*.py, alembic/
🔄 TIEMPO RESPUESTA: Inmediato (datos críticos)
```

### Problemas de Servidor/Docker
```
👤 CONTACTAR: system-architect-ai + cloud-infrastructure-ai
📁 ARCHIVOS: docker-compose.yml, app/main.py
🔄 TIEMPO RESPUESTA: Inmediato (infraestructura)
```

### Problemas de Tests/Fixtures
```
👤 CONTACTAR: tdd-specialist
📁 ARCHIVOS: tests/conftest.py, tests/fixtures/
🔄 TIEMPO RESPUESTA: Rápido (calidad)
```

### Problemas de Frontend/React
```
👤 CONTACTAR: react-specialist-ai
📁 ARCHIVOS: frontend/src/
🔄 TIEMPO RESPUESTA: Normal (UI)
```

## 🔧 HERRAMIENTAS DE VERIFICACIÓN

### Comando Pre-Modificación
```bash
# Verificar estado actual
git status
python -m pytest tests/ -v --tb=short
npm run test
```

### Comando Post-Modificación
```bash
# Validar cambios
python -m pytest tests/ -v
npm run test
docker-compose up --build -d
curl http://localhost:8000/health  # Verificar backend
curl http://localhost:5173        # Verificar frontend
```

### Template de Commit Obligatorio
```
tipo(área): descripción breve

Archivo: ruta/del/archivo.py
Agente: nombre-del-agente
Protocolo: [SEGUIDO/CONSULTA_PREVIA/APROBACIÓN_OBTENIDA]
Tests: [PASSED/FAILED/NO_EJECUTADOS]
Impacto: [NINGUNO/MÍNIMO/CRÍTICO]
Aprobación: agente-responsable (si aplica)

Detalle de cambios:
- Qué se modificó exactamente
- Por qué era necesario
- Qué se probó después
```

## ⚡ ESCALACIÓN DE CONFLICTOS

### Nivel 1: Consulta Directa
```
🎯 Contactar agente responsable específico
⏰ Tiempo máximo espera: 5 minutos
📝 Documentar consulta en commit
```

### Nivel 2: Coordinación Departamental
```
🎯 Elevar a development-coordinator
⏰ Tiempo máximo espera: 15 minutos
📝 Crear issue en .workspace/issues/
```

### Nivel 3: Decisión Arquitectónica
```
🎯 Elevar a master-orchestrator
⏰ Tiempo máximo espera: 30 minutos
📝 Documentar decisión arquitectónica
```

### Nivel 4: Decisión Ejecutiva
```
🎯 Elevar a director-enterprise-ceo
⏰ Tiempo máximo espera: 60 minutos
📝 Crear documento de decisión ejecutiva
```

## 📊 MÉTRICAS DE CUMPLIMIENTO

### Indicadores de Éxito
- ✅ 0 modificaciones no autorizadas en archivos críticos
- ✅ 0 usuarios duplicados en testing
- ✅ 0 cambios de puertos sin aprobación
- ✅ 100% de tests pasando después de cambios

### Indicadores de Alerta
- ⚠️ Modificación de archivos sin consulta previa
- ⚠️ Tests fallando después de cambios
- ⚠️ Servicios que no arrancan post-modificación
- ⚠️ Pérdida de funcionalidad existente

---
**📅 Vigencia**: Desde 2025-09-20
**🔄 Actualización**: Requiere aprobación master-orchestrator
**👥 Aplica a**: Todos los agentes sin excepción
**⚖️ Enforcement**: Automático mediante git hooks y validaciones