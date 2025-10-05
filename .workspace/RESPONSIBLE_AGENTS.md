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

## 🚀 RESPONSABILIDADES DE PRODUCCIÓN

### 📊 NUEVA SECCIÓN: MANTENIMIENTO EN PRODUCCIÓN (2025-10-05)

**Estado**: ✅ PRODUCCIÓN LIVE EN RENDER Y VERCEL

#### Agentes Responsables por Área de Producción

| Área | Agente Principal | Agente Backup | Responsabilidades |
|------|------------------|---------------|-------------------|
| **Infraestructura Cloud** | cloud-infrastructure-ai | devops-integration-ai | Monitoreo Render/Vercel, uptime, scaling, configuración de servicios |
| **Backend API Health** | backend-framework-ai | api-architect-ai | Health checks, performance API, bug fixes, endpoint monitoring |
| **Frontend Performance** | react-specialist-ai | frontend-performance-ai | UI/UX production, responsive design, build optimization |
| **Base de Datos Producción** | database-architect-ai | database-performance | Query optimization, migrations en producción, backups, monitoring |
| **Seguridad Producción** | security-backend-ai | api-security | Security monitoring, auth issues, vulnerability scanning |
| **Testing Regresión** | tdd-specialist | unit-testing-ai | Regression testing, E2E tests, quality assurance pre-deploy |
| **Deployment Pipeline** | devops-integration-ai | cloud-infrastructure-ai | CI/CD automation, deployment scripts, rollback procedures |
| **Monitoreo y Logs** | master-orchestrator | communication-hub-ai | Log aggregation, error tracking, alertas críticas |

#### Protocolo de Contacto para Issues de Producción

**Para reportar issues críticos en producción:**

```bash
# Formato especial para producción (prioridad ALTA)
python .workspace/scripts/contact_responsible_agent.py [tu-agente] [componente] "PRODUCCIÓN: [descripción urgente]"

# Ejemplos:
python .workspace/scripts/contact_responsible_agent.py agent-recruiter-ai backend-api "PRODUCCIÓN: API returning 500 errors"

python .workspace/scripts/contact_responsible_agent.py react-specialist-ai frontend-vercel "PRODUCCIÓN: Build failing on Vercel"

python .workspace/scripts/contact_responsible_agent.py database-architect-ai postgresql-render "PRODUCCIÓN: Database connection timeout"
```

**Tiempos de Respuesta en Producción:**

| Severidad | Tiempo Máximo Respuesta | Agente Principal | Escalación |
|-----------|------------------------|------------------|------------|
| **CRÍTICO** (Sistema caído) | 5 minutos | Agente responsable | Inmediata a master-orchestrator |
| **ALTA** (Funcionalidad afectada) | 15 minutos | Agente responsable | A backup después de 15 min |
| **MEDIA** (Performance degradada) | 30 minutos | Agente responsable | A backup después de 30 min |
| **BAJA** (Issues menores) | 2 horas | Agente responsable | No requerida |

#### Archivos Críticos de Producción

**Nuevos archivos bajo protección de producción:**

| Archivo | Agente Responsable | Modificación Permitida | Backup Requerido |
|---------|-------------------|----------------------|------------------|
| `.env.production` | configuration-management | Solo con aprobación CEO | ✅ OBLIGATORIO |
| `vercel.json` | cloud-infrastructure-ai | Solo con testing previo | ✅ OBLIGATORIO |
| `render.yaml` | cloud-infrastructure-ai | Solo con testing previo | ✅ OBLIGATORIO |
| `.workspace/PRODUCTION_STATUS.md` | master-orchestrator | Solo agentes autorizados | No requerido |
| `app/main.py` (PRODUCCIÓN) | system-architect-ai | ❌ PROHIBIDO directo | ✅ CRÍTICO |

#### Protocolo de Deployment a Producción

**ANTES de cualquier deployment a producción:**

1. **Validación Obligatoria** (tdd-specialist)
   ```bash
   python -m pytest tests/ -v --cov=app
   # Coverage mínimo: 75%
   # Todos los tests deben pasar
   ```

2. **Aprobación Arquitectura** (system-architect-ai)
   - Revisar cambios arquitectónicos
   - Validar compatibilidad con producción
   - Aprobar deployment

3. **Verificación Seguridad** (security-backend-ai)
   - Scan de vulnerabilidades
   - Validar cambios en auth
   - Aprobar si no hay riesgos

4. **Backup Crítico** (database-architect-ai)
   - Crear snapshot de base de datos
   - Documentar estado pre-deployment
   - Confirmar backup exitoso

5. **Deployment Autorizado** (devops-integration-ai)
   - Ejecutar deployment
   - Monitorear logs
   - Verificar health checks

6. **Verificación Post-Deployment** (master-orchestrator)
   - Confirmar todos los servicios operativos
   - Verificar métricas clave
   - Documentar resultado

#### URLs de Producción (Referencia Rápida)

**Backend (Render):**
```
https://mestore.onrender.com
https://mestore.onrender.com/docs
https://mestore.onrender.com/health
```

**Frontend (Vercel):**
```
https://me-store-zbc5wx48r-jairos-projects-6e49f915.vercel.app
https://me-store-zbc5wx48r-jairos-projects-6e49f915.vercel.app/admin-portal
https://me-store-zbc5wx48r-jairos-projects-6e49f915.vercel.app/admin-login
```

#### Credenciales de Emergencia

**⚠️ INFORMACIÓN CLASIFICADA - SOLO AGENTES AUTORIZADOS**

**Acceso Administrativo:**
- Email: admin@mestocker.com
- Password: Admin123456
- Tipo: SUPERUSER
- **Agentes Autorizados**: master-orchestrator, security-backend-ai, director-enterprise-ceo

**Acceso a Dashboards:**
- Render Dashboard: [Credenciales en vault]
- Vercel Dashboard: [Credenciales en vault]
- PostgreSQL Admin: [Solo database-architect-ai]

#### Plan de Recuperación de Desastres

**Responsable General**: master-orchestrator
**Equipo de Crisis**:
- cloud-infrastructure-ai (Infraestructura)
- backend-framework-ai (Backend)
- database-architect-ai (Datos)
- security-backend-ai (Seguridad)
- director-enterprise-ceo (Decisiones ejecutivas)

**Procedimiento de Emergencia:**

1. **Detección de Crisis** (Cualquier agente)
   ```bash
   # Notificar inmediatamente
   python .workspace/scripts/emergency_alert.py "CRISIS: [descripción]"
   ```

2. **Activación de Equipo** (master-orchestrator)
   - Convoca equipo de crisis
   - Evalúa severidad
   - Asigna responsabilidades

3. **Contención** (Agentes especializados)
   - Identificar causa raíz
   - Contener propagación
   - Implementar workaround temporal

4. **Rollback** (devops-integration-ai)
   ```bash
   git revert [commit-hash]
   git push origin main
   # Auto-redeploy en Render/Vercel
   ```

5. **Verificación** (tdd-specialist)
   - Confirmar sistema estable
   - Validar funcionalidad
   - Monitorear métricas

6. **Post-Mortem** (master-orchestrator)
   - Documentar incidente
   - Identificar mejoras
   - Actualizar protocolos

#### Monitoreo Continuo

**Métricas Críticas** (Responsable: master-orchestrator)

| Métrica | Target | Frecuencia Check | Alerta Si |
|---------|--------|------------------|-----------|
| Backend Uptime | 99.9% | Cada 5 min | <99% |
| Frontend Uptime | 99.9% | Cada 5 min | <99% |
| API Response Time | <200ms | Cada 1 min | >500ms |
| Error Rate | <1% | Cada 1 min | >5% |
| Database Queries | <100ms | Cada 5 min | >300ms |
| Login Success | >95% | Cada 15 min | <90% |

**Herramientas de Monitoreo:**
- Render Dashboard (Logs backend)
- Vercel Analytics (Performance frontend)
- Custom health check scripts
- Error tracking (Pendiente: Sentry)

#### Contacto de Emergencia 24/7

**Para incidentes críticos fuera de horario:**

| Severidad | Contactar | Método | Tiempo Respuesta |
|-----------|-----------|--------|------------------|
| CRÍTICO (P0) | master-orchestrator | Inmediato | <5 minutos |
| ALTO (P1) | Agente responsable área | Urgente | <15 minutos |
| MEDIO (P2) | Agente responsable área | Normal | <1 hora |
| BAJO (P3) | Ticket en GitHub | Issue | <24 horas |

---

**🚀 PRODUCCIÓN ACTIVA DESDE**: 2025-10-05
**📊 ÚLTIMA ACTUALIZACIÓN**: 2025-10-05
**👥 AGENTES EN PRODUCCIÓN**: 8 principales + 8 backup
**🔐 NIVEL DE PROTECCIÓN**: CRÍTICO
**⚡ DISPONIBILIDAD**: 24/7

---

**🎯 GARANTÍA**: Ningún archivo protegido quedará sin agente responsable disponible
**⏰ SLA**: Máximo 15 minutos para cualquier autorización
**🚨 Escalación**: Automática y documentada
**📊 Monitoreo**: Completo y en tiempo real
**🚀 NUEVO**: Protección especial para producción con SLA mejorado