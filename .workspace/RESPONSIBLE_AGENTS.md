# 👥 AGENTES RESPONSABLES GARANTIZADOS

## 🎯 MATRIZ DE RESPONSABILIDAD CRÍTICA

### 🚨 ARCHIVOS NIVEL CRÍTICO (CON AGENTE RESPONSABLE SIEMPRE DISPONIBLE)

| Archivo | Agente Responsable | Backup Agent | Escalación |
|---------|-------------------|--------------|------------|
| `app/main.py` | **system-architect-ai** | solution-architect-ai | master-orchestrator |
| `frontend/vite.config.ts` | **frontend-performance-ai** | react-specialist-ai | master-orchestrator |
| `docker-compose.yml` | **cloud-infrastructure-ai** | devops-integration-ai | master-orchestrator |
| `app/api/v1/deps/auth.py` | **security-backend-ai** | backend-framework-ai | master-orchestrator |
| `app/services/auth_service.py` | **security-backend-ai** | api-security | master-orchestrator |
| `app/models/user.py` | **database-architect-ai** | backend-framework-ai | master-orchestrator |
| `tests/conftest.py` | **tdd-specialist** | unit-testing-ai | master-orchestrator |
| `app/core/config.py` | **configuration-management** | system-architect-ai | master-orchestrator |
| `app/database.py` | **database-architect-ai** | database-performance | master-orchestrator |

### 🔄 PROTOCOLO DE AUTORIZACIÓN EN CASCADA

#### Nivel 1: Agente Responsable Principal
```
✅ Autorización inmediata si está disponible
⏰ Tiempo máximo respuesta: 5 minutos
📝 Debe proporcionar razón de aprobación/rechazo
```

#### Nivel 2: Agente Backup
```
⚠️ Si principal no responde en 5 minutos
✅ Mismos permisos que el principal
⏰ Tiempo máximo respuesta: 10 minutos
📝 Debe notificar al principal después
```

#### Nivel 3: Master Orchestrator
```
🚨 Si ni principal ni backup responden en 15 minutos
✅ Autorización de emergencia
⏰ Respuesta inmediata
📝 Debe documentar motivo de escalación
```

#### Nivel 4: CEO Director (Solo emergencias)
```
🔥 Solo para emergencias críticas de negocio
✅ Override de todas las restricciones
⏰ Tiempo de respuesta: variable
📝 Requiere justificación ejecutiva
```

## 🤖 DIRECTORIO DE AGENTES RESPONSABLES

### 🏗️ ARQUITECTURA Y DISEÑO

#### system-architect-ai
- **Responsabilidad**: `app/main.py`, arquitectura global
- **Ubicación**: `.workspace/departments/architecture/system-architect-ai/`
- **Backup**: solution-architect-ai
- **Especialidad**: Decisiones arquitectónicas críticas

#### solution-architect-ai
- **Responsabilidad**: Backup para system-architect-ai
- **Ubicación**: `.workspace/departments/architecture/solution-architect-ai/`
- **Especialidad**: Soluciones técnicas complejas

### 🛡️ SEGURIDAD

#### security-backend-ai
- **Responsabilidad**: TODO lo relacionado con autenticación
- **Archivos**: `auth.py`, `auth_service.py`, JWT, roles
- **Ubicación**: `.workspace/departments/backend/security-backend-ai/`
- **Backup**: api-security
- **AUTORIDAD EXCLUSIVA**: Sistema de autenticación

#### api-security
- **Responsabilidad**: Backup para security-backend-ai
- **Ubicación**: `.workspace/departments/backend/api-security/`
- **Especialidad**: Seguridad de APIs y endpoints

### 🗄️ BASE DE DATOS

#### database-architect-ai
- **Responsabilidad**: `user.py`, modelos, esquemas DB
- **Ubicación**: `.workspace/departments/architecture/database-architect-ai/`
- **Backup**: backend-framework-ai
- **AUTORIDAD EXCLUSIVA**: Modelos y migraciones

### 🎨 FRONTEND

#### frontend-performance-ai
- **Responsabilidad**: `vite.config.ts`, configuraciones frontend
- **Ubicación**: `.workspace/departments/frontend/frontend-performance-ai/`
- **Backup**: react-specialist-ai
- **Especialidad**: Optimización y configuración

### ☁️ INFRAESTRUCTURA

#### cloud-infrastructure-ai
- **Responsabilidad**: `docker-compose.yml`, infraestructura
- **Ubicación**: `.workspace/departments/infrastructure/cloud-infrastructure-ai/`
- **Backup**: devops-integration-ai
- **AUTORIDAD EXCLUSIVA**: Orquestación de servicios

### 🧪 TESTING

#### tdd-specialist
- **Responsabilidad**: `conftest.py`, fixtures, NO usuarios duplicados
- **Ubicación**: `.workspace/departments/testing/tdd-specialist/`
- **Backup**: unit-testing-ai
- **AUTORIDAD EXCLUSIVA**: Fixtures y datos de prueba

## 📞 CÓMO CONTACTAR AGENTES RESPONSABLES

### 🚨 PROTOCOLO DE CONTACTO URGENTE

#### Para Modificación de Archivo Protegido:
```bash
# 1. Ejecutar validador automático
python .workspace/scripts/agent_workspace_validator.py [tu-agente] [archivo]

# 2. Si es denegado, contactar agente responsable:
python .workspace/scripts/contact_responsible_agent.py [archivo] [motivo]

# 3. Esperar aprobación (máximo 15 minutos con escalación)
```

#### Ejemplo Práctico:
```bash
# Quiero modificar auth.py
python .workspace/scripts/agent_workspace_validator.py backend-framework-ai app/api/v1/deps/auth.py

# Sistema responde: "❌ Contactar security-backend-ai"
python .workspace/scripts/contact_responsible_agent.py app/api/v1/deps/auth.py "Necesito agregar validación de email"

# Sistema notifica a security-backend-ai y espera respuesta
```

## ⚡ GARANTÍAS DEL SISTEMA

### ✅ SIEMPRE HAY RESPONSABLE DISPONIBLE
- **Agente Principal**: Disponible 24/7 para su área
- **Agente Backup**: Disponible si principal no responde
- **Master Orchestrator**: Disponible SIEMPRE para emergencias
- **CEO Director**: Override ejecutivo para crisis

### ✅ TIEMPOS DE RESPUESTA GARANTIZADOS
- **Principal**: 5 minutos máximo
- **Backup**: 10 minutos máximo
- **Master**: Inmediato
- **Total**: Nunca más de 15 minutos sin respuesta

### ✅ ESCALACIÓN AUTOMÁTICA
- Sistema escala automáticamente si no hay respuesta
- Logs completos de todas las interacciones
- Notificaciones automáticas de escalaciones

## 🔧 HERRAMIENTAS DE CONTACTO

### Script de Contacto Automático
```bash
# Contactar agente responsable
python .workspace/scripts/contact_responsible_agent.py [archivo] [motivo]

# Ver estado de solicitudes pendientes
python .workspace/scripts/check_pending_requests.py

# Forzar escalación (solo emergencias)
python .workspace/scripts/escalate_request.py [request_id] [motivo]
```

### Sistema de Notificaciones
- **Slack/Teams**: Notificaciones inmediatas
- **Email**: Backup de notificaciones
- **Logs**: Registro completo en `.workspace/logs/`
- **Dashboard**: Vista en tiempo real de solicitudes

---

**🎯 GARANTÍA**: Ningún archivo protegido quedará sin agente responsable disponible
**⏰ SLA**: Máximo 15 minutos para cualquier autorización
**🚨 Escalación**: Automática y documentada
**📊 Monitoreo**: Completo y en tiempo real