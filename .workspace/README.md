# 🏢 .WORKSPACE - OFICINA CENTRAL MESTORE

## 🎯 PROPÓSITO
Sistema de control y coordinación para evitar que agentes modifiquen archivos críticos, rompan autenticación, dupliquen usuarios o cambien configuraciones establecidas.

## 📁 ESTRUCTURA COMPLETA

```
.workspace/
├── README.md                 # Este archivo - Guía principal
├── OFFICE_STRUCTURE.md       # Organización de 72+39 agentes
├── SYSTEM_RULES.md          # Reglas globales obligatorias
├── PROTECTED_FILES.md       # Lista archivos intocables
├── AGENT_PROTOCOL.md        # Protocolo paso a paso
│
├── departments/             # Oficinas por departamento
│   ├── executive/          # 4 agentes dirección
│   ├── architecture/       # 7 agentes + 1 expansión
│   ├── backend/           # 15 agentes + 10 expansión
│   ├── frontend/          # 16 agentes + 3 expansión
│   ├── mobile/            # 0 agentes + 5 expansión
│   ├── integration/       # 6 agentes
│   ├── data-ai/          # 8 agentes + 4 expansión
│   ├── security/         # 1 agente + 7 expansión
│   ├── infrastructure/   # 5 agentes + 7 expansión
│   ├── testing/          # 8 agentes + 4 expansión
│   └── management/       # 12 agentes
│
└── project/               # Espejo del proyecto con metadatos
    ├── app/
    │   ├── main.py.md     # Metadatos servidor FastAPI
    │   ├── api/v1/deps/
    │   │   └── auth.py.md # Metadatos autenticación
    │   └── models/
    │       └── user.py.md # Metadatos modelo usuario
    ├── frontend/
    │   └── vite.config.ts.md # Metadatos config Vite
    └── docker-compose.yml.md # Metadatos Docker
```

## 🚨 PROBLEMAS RESUELTOS

### ✅ Usuarios Duplicados en Testing
- **Antes**: Tests creaban usuarios constantemente
- **Ahora**: Metadatos en `user.py.md` advierten usar fixtures
- **Responsable**: `tdd-specialist` supervisa

### ✅ Cambios de Puertos de Servidor
- **Antes**: Agentes cambiaban 8000→otro, 5173→otro
- **Ahora**: Archivos marcados como PROTEGIDO CRÍTICO
- **Responsables**: `system-architect-ai`, `cloud-infrastructure-ai`

### ✅ Autenticación Rota
- **Antes**: Agentes "arreglaban" auth y lo rompían
- **Ahora**: Solo `security-backend-ai` puede modificar
- **Protocolo**: Consulta obligatoria antes de tocar

### ✅ Configuraciones Docker Modificadas
- **Antes**: Cambios rompían orquestación completa
- **Ahora**: `docker-compose.yml` en lista protegida
- **Validación**: Servicios deben seguir funcionando

## 🎯 CÓMO USAR ESTE SISTEMA

### Para Agentes (Al inicio de cualquier tarea):
1. **LEE** `.workspace/SYSTEM_RULES.md`
2. **CONSULTA** `.workspace/PROTECTED_FILES.md`
3. **VERIFICA** si tu archivo está protegido
4. **REVISA** `.workspace/project/archivo.md` para metadatos
5. **SIGUE** protocolo en `.workspace/AGENT_PROTOCOL.md`

### Para Desarrollador (Supervisión):
1. **MONITOREA** que agentes consulten antes de modificar
2. **VERIFICA** que tests pasen después de cambios
3. **VALIDA** que servicios sigan funcionando
4. **ACTUALIZA** metadatos si es necesario

## 🔧 COMANDOS DE VERIFICACIÓN

### Verificar Archivos Protegidos
```bash
# Ver qué archivos están siendo modificados
git status app/main.py app/api/v1/deps/auth.py docker-compose.yml

# Verificar estado de servicios
docker-compose ps
curl http://localhost:8000/health
curl http://localhost:5173
```

### Validar Sistema Completo
```bash
# Tests backend
python -m pytest tests/ -v

# Tests frontend
cd frontend && npm run test

# Levantar servicios
docker-compose up --build
```

## 📊 ESTADÍSTICAS ACTUALES

### Agentes Configurados
- **Total Actual**: 72 agentes
- **Expansión Planificada**: +39 agentes
- **Total Óptimo**: 111 agentes

### Archivos Protegidos
- **Nivel Crítico**: 12 archivos
- **Alto Riesgo**: 15 archivos
- **Total Vigilados**: 27 archivos

### Departamentos Activos
- **Ejecutivo**: 4 agentes
- **Backend**: 15 agentes (más críticos)
- **Frontend**: 16 agentes
- **Testing**: 8 agentes
- **Otros**: 29 agentes

## 🎯 PRÓXIMOS PASOS

1. **Implementar** validaciones automáticas en git hooks
2. **Crear** alertas para modificaciones no autorizadas
3. **Desarrollar** sistema de reporting de cumplimiento
4. **Expandir** a los 39 agentes adicionales cuando sea necesario

## 🆘 SOPORTE Y ESCALACIÓN

### Problemas con Archivos Protegidos
1. **Consultar** agente responsable listado en metadatos
2. **Escalar** a `development-coordinator` si no responde
3. **Elevar** a `master-orchestrator` para decisión final

### Emergencias del Sistema
1. **Revertir** cambios problemáticos inmediatamente
2. **Documentar** incidente en `.workspace/incidents/`
3. **Notificar** a `director-enterprise-ceo`

---
**🏢 Sistema Creado**: 2025-09-20
**🔄 Mantenimiento**: Continuo
**👤 Responsable**: master-orchestrator
**🎯 Objetivo**: Cero roturas de configuraciones críticas