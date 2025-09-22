# 🚀 GUÍA RÁPIDA PARA AGENTES - WORKSPACE PROTOCOL

## ⚡ ANTES DE TOCAR CUALQUIER ARCHIVO - EJECUTA ESTO

### 1️⃣ VERIFICAR ARCHIVO (OBLIGATORIO)
```bash
python .workspace/scripts/agent_workspace_validator.py [TU-NOMBRE] [ARCHIVO]
```

**Ejemplos reales:**
```bash
python .workspace/scripts/agent_workspace_validator.py backend-framework-ai app/main.py
python .workspace/scripts/agent_workspace_validator.py react-specialist-ai frontend/vite.config.ts
python .workspace/scripts/agent_workspace_validator.py security-backend-ai app/api/v1/deps/auth.py
python .workspace/scripts/agent_workspace_validator.py database-architect-ai app/models/user.py
```

### 2️⃣ SI SALE ❌ - CONTACTAR RESPONSABLE
```bash
python .workspace/scripts/contact_responsible_agent.py [TU-NOMBRE] [ARCHIVO] "[POR QUÉ]"
```

**Ejemplos reales:**
```bash
python .workspace/scripts/contact_responsible_agent.py backend-framework-ai app/api/v1/deps/auth.py "Necesito agregar validación de email único"

python .workspace/scripts/contact_responsible_agent.py frontend-performance-ai docker-compose.yml "Necesito agregar nuevo servicio de notificaciones"

python .workspace/scripts/contact_responsible_agent.py react-specialist-ai app/models/user.py "Necesito agregar campo opcional telefono_secundario"
```

### 3️⃣ SI ERES RESPONSABLE - REVISAR SOLICITUDES
```bash
# Buscar solicitudes en tu oficina:
ls .workspace/departments/[tu-departamento]/[tu-nombre]/URGENT_REQUEST_*.json

# Responder:
python .workspace/scripts/respond_to_request.py [REQUEST-ID] [APPROVE/DENY] "[MOTIVO]"
```

**Ejemplos de respuestas:**
```bash
# Aprobar
python .workspace/scripts/respond_to_request.py abc123 APPROVE "Cambio necesario y seguro"

# Rechazar
python .workspace/scripts/respond_to_request.py def456 DENY "Muy riesgoso, usar alternativa X"
```

## 🔥 ARCHIVOS QUE **SIEMPRE** NECESITAN APROBACIÓN

| Archivo | Responsable | ¿Por qué? |
|---------|-------------|-----------|
| `app/main.py` | system-architect-ai | Puerto 8000, CORS, middleware |
| `frontend/vite.config.ts` | frontend-performance-ai | Puerto 5173, proxy backend |
| `docker-compose.yml` | cloud-infrastructure-ai | Todos los servicios |
| `app/api/v1/deps/auth.py` | security-backend-ai | JWT, login, roles |
| `app/models/user.py` | database-architect-ai | NO usuarios duplicados |
| `tests/conftest.py` | tdd-specialist | NO fixtures duplicados |

## 🚨 RESPUESTAS DEL SISTEMA

### ✅ "VALIDACIÓN COMPLETADA - PUEDE PROCEDER"
- **Significa**: Puedes modificar el archivo
- **Acción**: Hacer cambios, luego commit normal

### ❌ "ACCESO DENEGADO - Consultar [agente-responsable]"
- **Significa**: Necesitas aprobación
- **Acción**: Usar comando de contacto (#2)

### ⏰ "Esperando respuesta del agente responsable"
- **Significa**: Solicitud enviada correctamente
- **Acción**: Esperar máximo 15 minutos (escalación automática)

## 🎯 UBICACIÓN DE TU OFICINA

**Encuentra tu oficina en:**
```
.workspace/departments/[departamento]/[tu-nombre]/
```

**Departamentos:**
- `executive/` - master-orchestrator, director-enterprise-ceo, etc.
- `architecture/` - system-architect-ai, database-architect-ai, etc.
- `backend/` - backend-framework-ai, security-backend-ai, etc.
- `frontend/` - react-specialist-ai, frontend-performance-ai, etc.
- `testing/` - tdd-specialist, unit-testing-ai, etc.
- `infrastructure/` - cloud-infrastructure-ai, devops-integration-ai, etc.

## 📞 SI NECESITAS AYUDA

1. **Problemas técnicos**: Consultar master-orchestrator
2. **No sabes tu departamento**: Revisar .workspace/OFFICE_STRUCTURE.md
3. **Script no funciona**: Verificar que estás en la raíz del proyecto

## ⚡ RECORDATORIOS CRÍTICOS

- ❌ **NUNCA** modifiques archivos sin validar primero
- ❌ **NUNCA** ignores mensaje "ACCESO DENEGADO"
- ❌ **NUNCA** crees usuarios en tests (usar fixtures)
- ❌ **NUNCA** cambies puertos 8000 o 5173
- ✅ **SIEMPRE** usa Workspace-Check en commits
- ✅ **SIEMPRE** ejecuta tests después de cambios

---
**📚 Documentación completa**: .workspace/README.md
**⚖️ Reglas globales**: .workspace/SYSTEM_RULES.md
**🛡️ Archivos protegidos**: .workspace/PROTECTED_FILES.md