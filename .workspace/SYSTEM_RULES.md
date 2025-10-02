# 🚨 REGLAS GLOBALES DEL SISTEMA MESTORE

## 🔒 PROTOCOLO OBLIGATORIO PARA TODOS LOS AGENTES

### ⚡ REGLA #1: CONSULTA OBLIGATORIA
**ANTES DE MODIFICAR CUALQUIER ARCHIVO, TODO AGENTE DEBE:**
1. Consultar `.workspace/project/[ruta-archivo].md` para ver metadatos
2. Verificar si el archivo está en `PROTECTED_FILES.md`
3. Seguir el protocolo específico del archivo
4. Obtener aprobación del agente responsable si es necesario

### 🚫 ARCHIVOS COMPLETAMENTE PROHIBIDOS (NUNCA TOCAR)

#### Configuración de Servidores
- `app/main.py` - Punto de entrada FastAPI
- `frontend/vite.config.ts` - Configuración Vite
- `docker-compose.yml` - Orquestación servicios
- `app/core/config.py` - Configuraciones aplicación

#### Sistema de Autenticación
- `app/api/v1/deps/auth.py` - Dependencias auth JWT
- `app/services/auth_service.py` - Lógica autenticación
- `frontend/src/contexts/AuthContext.tsx` - Contexto auth frontend
- `frontend/src/services/authService.ts` - Servicio auth

#### Modelos Críticos de Base de Datos
- `app/models/user.py` - Modelo usuarios
- `app/models/order.py` - Modelo pedidos
- `alembic/` - Migraciones de base de datos

### ⚠️ ARCHIVOS DE ALTO RIESGO (CONSULTA OBLIGATORIA)

#### Pagos y Transacciones
- `app/services/integrated_payment_service.py`
- `app/api/v1/endpoints/payments.py`
- `frontend/src/components/payments/`

#### Base de Datos
- `app/database.py`
- `tests/conftest.py` (fixtures de testing)
- `app/models/` (todos los modelos)

### 🔄 PROTOCOLO DE MODIFICACIÓN ESCALONADA

#### Nivel 1: INFORMACIÓN (✅ Permitido)
- Leer archivos para entender código
- Buscar patrones y estructuras
- Analizar sin modificar

#### Nivel 2: CONSULTA REQUERIDA (⚠️ Verificar primero)
- Modificaciones menores (comentarios, formato)
- Agregar funciones nuevas sin afectar existentes
- Tests unitarios nuevos

#### Nivel 3: APROBACIÓN OBLIGATORIA (🚨 Crítico)
- Modificar lógica existente
- Cambiar configuraciones
- Alterar esquemas de base de datos
- Modificar autenticación

#### Nivel 4: PROHIBIDO (❌ Nunca)
- Cambiar puertos de servidores
- Modificar configuración Docker
- Alterar dependencias de autenticación
- Crear usuarios duplicados en testing
- **🚨 NUEVO: Crear endpoints en español** (Directiva CEO 2025-10-01)
- **🚨 NUEVO: Usar nombres de variables/funciones en español en código** (Directiva CEO 2025-10-01)
- **🚨 NUEVO: Crear archivos con nombres en español** (Directiva CEO 2025-10-01)

### 🏢 JURISDICCIÓN POR DEPARTAMENTOS

#### EJECUTIVO (.workspace/departments/executive/)
- **master-orchestrator**: Coordinación suprema, decisiones finales
- **director-enterprise-ceo**: Representación empresarial
- **personal-assistant**: Asistencia ejecutiva, coordinación
- **communication-hub-ai**: Comunicación entre agentes

#### ARQUITECTURA (.workspace/departments/architecture/)
- **system-architect-ai**: Decisiones arquitectónicas globales
- **api-architect-ai**: Diseño APIs y endpoints
- **database-architect-ai**: Modelos y esquemas de datos
- **solution-architect-ai**: Soluciones técnicas complejas

#### BACKEND (.workspace/departments/backend/)
- **security-backend-ai**: Todo lo relacionado con autenticación
- **backend-framework-ai**: FastAPI y lógica backend
- **configuration-management**: Variables y configuraciones

### 🎯 CASOS DE USO ESPECÍFICOS

#### ❌ PROHIBIDO: "Crear usuarios para testing"
**PROBLEMA**: Tests crean usuarios duplicados constantemente
**SOLUCIÓN**: Usar fixtures existentes en `tests/conftest.py`
**RESPONSABLE**: `tdd-specialist` debe validar

#### ❌ PROHIBIDO: "Cambiar puerto del servidor"
**PROBLEMA**: Modifica `8000` o `5173` rompe Docker
**SOLUCIÓN**: Mantener puertos estándar
**RESPONSABLE**: `cloud-infrastructure-ai` decide puertos

#### ❌ PROHIBIDO: "Arreglar autenticación"
**PROBLEMA**: Rompe sistema de login existente
**SOLUCIÓN**: Consultar con `security-backend-ai` SIEMPRE
**RESPONSABLE**: Solo `security-backend-ai` modifica auth

#### 🚨 NUEVO PROHIBIDO: "Código en español" (DIRECTIVA CEO 2025-10-01)
**PROBLEMA**: APIs duplicadas en español/inglés, código inconsistente
**SOLUCIÓN OBLIGATORIA**:
  - ✅ **TODO código técnico EN INGLÉS**: APIs, variables, funciones, archivos, comentarios
  - ✅ **TODO contenido de usuario EN ESPAÑOL**: UI, mensajes, errores, notificaciones
**RESPONSABLES**: backend-framework-ai + api-architect-ai
**REFERENCIA**: `.workspace/URGENT_BROADCAST_CEO_CODE_STANDARDIZATION.md`

### 🔧 HERRAMIENTAS DE VALIDACIÓN

#### Antes de Commit (Obligatorio)
```bash
# Ejecutar tests completos
python -m pytest tests/ -v
npm run test

# Verificar linting
npm run lint
python -m black app/

# Confirmar que servicios arrancan
docker-compose up --build
```

#### Verificación de Archivos Protegidos
```bash
# Verificar metadatos antes de modificar
cat .workspace/project/[archivo].md
```

### 📋 REGISTRO DE MODIFICACIONES

#### Template Obligatorio para Commits
```
tipo(área): descripción en inglés

Workspace-Check: ✅ Consultado
File: ruta/del/archivo
Agent: nombre-del-agente
Protocol: [FOLLOWED/PRIOR_CONSULTATION/APPROVAL_OBTAINED]
Tests: [PASSED/FAILED]
Code-Standard: ✅ ENGLISH_CODE / ✅ SPANISH_UI
API-Duplication: [NONE/CONSOLIDATED/DEPRECATED]
Responsible: agente-que-aprobó (si aplica)

Description:
[Descripción detallada del cambio]
```

**🚨 NUEVO (2025-10-01)**: Campo `Code-Standard` es OBLIGATORIO para validar directiva CEO

### 🚨 ESCALACIÓN DE PROBLEMAS

#### Si un agente no puede proceder:
1. **Nivel 1**: Consultar agente especialista del área
2. **Nivel 2**: Elevar a `development-coordinator`
3. **Nivel 3**: Escalación a `master-orchestrator`
4. **Nivel 4**: Decisión ejecutiva de `director-enterprise-ceo`

#### En caso de conflicto entre agentes:
1. `master-orchestrator` toma decisión final
2. Se documenta en `.workspace/conflicts/YYYY-MM-DD-conflict.md`
3. Se actualiza protocolo si es necesario

### ✅ CUMPLIMIENTO OBLIGATORIO

**TODOS LOS AGENTES DEBEN:**
- ✅ Leer estas reglas antes de primera modificación
- ✅ Consultar metadatos de archivos antes de tocar
- ✅ Seguir protocolo de escalación
- ✅ Documentar cambios en commits
- ✅ Ejecutar tests antes de commits
- ✅ Respetar jurisdicciones de otros agentes

**CONSECUENCIAS POR INCUMPLIMIENTO:**
- 🔸 Primera vez: Warning y corrección
- 🔸 Segunda vez: Escalación a supervisor
- 🔸 Tercera vez: Restricción de acceso a archivos críticos

---
**📅 Vigencia**: Desde 2025-09-20
**🔄 Actualización**: Requiere aprobación `master-orchestrator`
**👥 Aplica a**: Todos los 72 agentes actuales + 39 expansión futura