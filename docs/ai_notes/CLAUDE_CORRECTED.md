# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🤖 INSTRUCCIONES AUTOMÁTICAS PARA CLAUDE CODE

### 🔄 AL INICIO DE CUALQUIER SESIÓN

**COMANDO INICIAL RECOMENDADO:**
```bash
# Verificar workspace y estado del proyecto
python .workspace/scripts/init_workspace.py --summary
```

**Output Esperado:**
```
✅ Workspace OK
📁 47 archivos protegidos verificados
👥 12 agentes activos
🔐 Credenciales admin: OK
📊 Última actualización: 2025-10-13
```

### ⚡ CHECKLIST AUTOMÁTICO OBLIGATORIO

1. ✅ **Leer este archivo CLAUDE.md completo**
2. ✅ **Verificar archivos protegidos antes de cualquier modificación**
3. ✅ **Consultar agente responsable si archivo está protegido**
4. ✅ **Seguir template de commits simplificado**
5. ✅ **Ejecutar tests antes de commits importantes**

### 🚨 RECORDATORIO CRÍTICO

- **NUNCA** modificar archivos sin consultar `.workspace/PROTECTED_FILES.md`
- **SIEMPRE** usar scripts de validación antes de cambios
- **OBLIGATORIO** seguir protocolo de agentes responsables

---

## 🔐 CREDENCIALES ADMINISTRATIVAS

### Cuenta Superuser de Producción

**⚠️ INFORMACIÓN CRÍTICA - MÁXIMA PROTECCIÓN**

- **Email**: `admin@mestocker.com`
- **Password**: `Admin123456`
- **Tipo**: SUPERUSER
- **Estado**: ✅ OPERATIVO EN PRODUCCIÓN
- **Base de Datos**: PostgreSQL en Render

### Propósito Crítico

- ✅ Acceso administrativo garantizado al sistema
- ✅ Cuenta de emergencia para recuperación
- ✅ Portal de administración siempre accesible
- ✅ Gestión de usuarios y configuraciones críticas

### Prohibiciones Absolutas

- ❌ **NUNCA** eliminar esta cuenta
- ❌ **NUNCA** modificar email o password sin aprobación CEO
- ❌ **NUNCA** cambiar roles o permisos
- ❌ **NUNCA** desactivar o suspender
- ❌ **NUNCA** exponer en logs o código público

### Agentes Responsables

- **backend-framework-ai** - Lógica backend de usuarios
- **system-architect-ai** - Arquitectura del sistema de auth
- **database-architect-ai** - Estructura de datos de usuarios
- **security-backend-ai** - Seguridad y autenticación

**Protocolo de Contacto:**
```bash
python .workspace/scripts/contact_responsible_agent.py [tu-agente] app/models/user.py "Descripción de tu necesidad"
```

---

## 🚨 PROTOCOLO WORKSPACE (TODOS LOS AGENTES)

### Antes de Cualquier Modificación

**TODOS LOS AGENTES SIN EXCEPCIÓN DEBEN:**

1. **LEER**: `.workspace/SYSTEM_RULES.md` - Reglas globales del sistema
2. **CONSULTAR**: `.workspace/PROTECTED_FILES.md` - Archivos bajo protección
3. **REVISAR**: `.workspace/project/[archivo].md` - Metadatos específicos
4. **SEGUIR**: `.workspace/AGENT_PROTOCOL.md` - Protocolo de agentes
5. **OBTENER APROBACIÓN**: Del agente responsable si archivo está protegido

### Documentación Completa

- **Guía rápida**: `.workspace/QUICK_START_GUIDE.md` ⭐ (LEER PRIMERO)
- **Oficina central**: `.workspace/README.md`
- **Reglas globales**: `.workspace/SYSTEM_RULES.md`
- **Archivos protegidos**: `.workspace/PROTECTED_FILES.md`
- **Agentes responsables**: `.workspace/RESPONSIBLE_AGENTS.md`
- **Tu oficina**: `.workspace/departments/[departamento]/[tu-agente]/`

---

## 🔒 ARCHIVOS CRÍTICOS PROTEGIDOS

### Backend Critical Files

- `app/main.py` - Puerto 8000 servidor FastAPI
- `app/api/v1/deps/auth.py` - Sistema autenticación JWT
- `app/models/user.py` - NO crear usuarios duplicados
- `tests/conftest.py` - NO modificar fixtures existentes

### Frontend Critical Files

- `frontend/vite.config.ts` - Puerto 5173 frontend
- `frontend/src/components/AdminLayout.tsx` - Layout principal del portal admin
- `frontend/src/pages/AdminLogin.tsx` - Punto de entrada administrativo
- `frontend/src/components/admin/navigation/NavigationProvider.tsx` - Contexto de navegación

### Infrastructure Critical Files

- `docker-compose.yml` - Configuración servicios
- `alembic.ini` - Configuración migraciones
- `Makefile` - Comandos de desarrollo

---

## 🛡️ NAVEGACIÓN ADMINISTRATIVA Y REACT HOOKS

### Flujo de Autenticación Admin

**⚠️ FLUJO ABSOLUTO - NUNCA MODIFICAR SIN CONSULTAR**

Este flujo está separado completamente del login de usuarios regulares:

1. **LandingPage** → Footer → "Portal Admin" → `/admin-portal`
2. **AdminPortal** → Botón "Acceder al Sistema" → `/admin-login`
3. **AdminLogin** → Credenciales → `/admin-secure-portal/dashboard`

### Componentes Críticos

- `frontend/src/components/layout/Footer.tsx` - Link a `/admin-portal`
- `frontend/src/pages/AdminPortal.tsx` - Navegación a `/admin-login`
- `frontend/src/pages/AdminLogin.tsx` - Autenticación y redirect
- `frontend/src/components/AdminLayout.tsx` - DEBE tener AccessibilityProvider

### Prohibiciones Absolutas

- ❌ NUNCA cambiar rutas `/admin-portal` o `/admin-login`
- ❌ NUNCA usar `window.location.href` - SOLO `navigate()`
- ❌ NUNCA remover AccessibilityProvider del AdminLayout
- ❌ NUNCA modificar NavigationProvider props en AdminLayout

### Reglas Críticas de React Hooks

**🔥 REGLA #1: NUNCA useCallback DENTRO DE useMemo**

```typescript
// ❌ INCORRECTO - ROMPE EL PORTAL ADMIN
const utils = useMemo(() => ({
  isActiveByPath: useCallback((path, currentPath) => { ... }, [])
}), []);

// ✅ CORRECTO - PORTAL ADMIN FUNCIONA
const utils = useMemo(() => ({
  isActiveByPath: (path, currentPath) => { ... }
}), []);
```

### Síntomas de Violación

- Error: `TypeError: utils.isActiveByPath is not a function`
- Portal administrativo inaccesible después del login
- React Hook warnings en consola

### Comando de Prueba Obligatorio

```bash
# Después de modificar componentes de navegación admin:
echo "Testing admin portal access..." && \
curl -X POST "http://localhost:8000/api/v1/auth/admin-login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@mestocker.com", "password": "Admin123456"}' && \
echo "✅ Backend auth OK - Now test frontend navigation"
```

### Verificación Post-Modificación

1. ✅ Verificar que NO hay useCallback dentro de useMemo
2. ✅ Testear el flujo completo de login admin
3. ✅ Confirmar que NavigationProvider context funciona
4. ✅ Validar que no hay React Hook violations

---

## 📋 COMANDOS PARA AGENTES

### Verificar Protección de Archivos

```bash
# 1. VERIFICAR si archivo está protegido
python .workspace/scripts/agent_workspace_validator.py [tu-nombre-agente] [archivo-a-modificar]

# Ejemplos:
python .workspace/scripts/agent_workspace_validator.py backend-framework-ai app/main.py
python .workspace/scripts/agent_workspace_validator.py react-specialist-ai frontend/vite.config.ts
```

### Contactar Agente Responsable

```bash
# 2. CONTACTAR agente responsable si archivo está protegido
python .workspace/scripts/contact_responsible_agent.py [tu-agente] [archivo] "[motivo]"

# Ejemplos:
python .workspace/scripts/contact_responsible_agent.py backend-framework-ai app/api/v1/deps/auth.py "Necesito agregar validación de email"
python .workspace/scripts/contact_responsible_agent.py frontend-security-ai app/models/user.py "Agregar campo opcional para perfil"
```

### Responder a Solicitudes

```bash
# 3. RESPONDER a solicitudes (para agentes responsables)
python .workspace/scripts/respond_to_request.py [request-id] [APPROVE/DENY] "[motivo]"

# Ejemplos:
python .workspace/scripts/respond_to_request.py abc123 APPROVE "Cambio necesario para seguridad"
python .workspace/scripts/respond_to_request.py def456 DENY "Riesgo muy alto, considerar alternativa"
```

---

## 📋 TEMPLATE DE COMMITS (SIMPLIFICADO)

```
tipo(área): descripción breve

Workspace-Check: [✅ Consultado / ⚠️ N/A]
Archivo: ruta/del/archivo.py
Tests: [PASSED / FAILED / N/A]
Responsable: agente-que-aprobó (si aplica)
```

**Campos Opcionales** (solo si aplican):
- `Admin-Portal: VERIFIED` - Si modificaste componentes de navegación admin
- `Hook-Violations: NONE` - Si trabajaste con React Hooks

### Ejemplo de Commit

```
feat(auth): Agregar validación de email en registro

Workspace-Check: ✅ Consultado
Archivo: app/api/v1/endpoints/auth.py
Tests: PASSED
Responsable: backend-framework-ai
```

---

## 📁 ESTRUCTURA ORGANIZADA DEL PROYECTO

### Documentación Técnica - `docs/`

Toda la documentación del proyecto está organizada en `/docs/` con estructura profesional:

**Ubicaciones Estándar:**
- **`docs/architecture/`** - Diseño de sistemas, diagramas, decisiones arquitectónicas
- **`docs/guides/`** - Guías de configuración, features e integración
  - `docs/guides/setup/` - Setup de servicios (DB, SMS, Twilio)
  - `docs/guides/features/` - Implementación de features
  - `docs/guides/integration/` - Integraciones externas (Wompi, PayU)
- **`docs/reports/`** - Reportes organizados por trimestre
  - `docs/reports/testing/2025-Q4/` - Reportes de testing
  - `docs/reports/implementation/2025-Q4/` - Reportes de implementación
  - `docs/reports/bugs/2025-Q4/` - Fixes de bugs
  - `docs/reports/audits/2025-Q4/` - Auditorías y análisis
  - `docs/reports/performance/2025-Q4/` - Performance testing
- **`docs/executive/`** - Resúmenes ejecutivos, MVP, roadmaps
- **`docs/api/`** - Documentación de API
- **`docs/deployment/`** - Guías de deployment y operaciones de producción

**Índice Maestro**: Ver `docs/README.md` para navegación completa

### Scripts Organizados - `scripts/`

Todos los scripts están categorizados en `/scripts/`:

- **`scripts/analysis/`** - Análisis de código y cobertura
- **`scripts/testing/`** - Ejecución de tests y validación
- **`scripts/validation/`** - Validación de componentes y datos
- **`scripts/debug/`** - Herramientas de debugging
- **`scripts/database/`** - Operaciones de DB
- **`scripts/deployment/`** - Scripts de despliegue
- **`scripts/maintenance/`** - Mantenimiento y limpieza
- **`scripts/services/`** - Gestión de servicios
- **`scripts/user_management/`** - Gestión de usuarios
- **`scripts/backup/`** - Backups

**Guía de Scripts**: Ver `scripts/README.md` para detalles de uso

### Datos y Reportes - `data/`

- **`data/reports/`** - Archivos JSON de análisis y reportes

### Archivo Histórico - `.archive/`

Documentos obsoletos o históricos organizados por año:
- `.archive/2024/` - Documentos de 2024
- `.archive/2025/` - Documentos históricos de 2025

---

## 🚨 REGLAS ESTRICTAS: CERO DESORDEN EN RAÍZ

### Prohibido Crear en Raíz

**Documentación:**
- ❌ **NUNCA** crear archivos `.md` en raíz
- ✅ **SIEMPRE** usar `docs/[categoria]/nombre.md`

**Scripts:**
- ❌ **NUNCA** crear scripts `.py` o `.sh` en raíz (excepto setup.py)
- ✅ **SIEMPRE** usar `scripts/[categoria]/nombre.py`

**Tests:**
- ❌ **NUNCA** crear archivos de test en raíz
- ✅ **SIEMPRE** usar `tests/` o `frontend/tests/`

**Archivos Temporales:**
- ❌ **NUNCA** crear archivos `.log`, `.db`, `.sqlite` en raíz
- ✅ **SIEMPRE** usar `logs/` o configurar rutas apropiadas

### Archivos Permitidos en Raíz (Máximo 20-25)

**Esenciales:**
1. `README.md` - Documentación principal
2. `CLAUDE.md` - Este archivo
3. `CONTRIBUTING.md` - Guía de contribución (opcional)
4. `CHANGELOG.md` - Historial de cambios (opcional)
5. `LICENSE` - Licencia del proyecto
6. `setup.py` - Script de setup Python
7. `.gitignore` - Git ignore rules
8. `.env*` - Variables de entorno (múltiples variantes OK)
9. `requirements.txt` - Dependencias Python
10. `package.json` - Dependencias Node
11. `docker-compose*.yml` - Docker configs
12. `Dockerfile*` - Dockerfiles
13. `Makefile` - Make commands
14. `alembic.ini` - Alembic config
15. `pytest.ini` - Pytest config
16. `.coveragerc` - Coverage config
17. `render.yaml` / `Procfile` - Deployment configs
18. `nixpacks.toml` - Nixpacks config

### Checklist Antes de Crear Archivos

1. ✅ ¿Es un archivo .md? → `docs/[categoria]/`
2. ✅ ¿Es un script .py/.sh? → `scripts/[categoria]/`
3. ✅ ¿Es un test? → `tests/` o `frontend/tests/`
4. ✅ ¿Es un log? → `logs/`
5. ✅ ¿Es temporal? → `temp/`
6. ✅ ¿Es configuración? → Verificar si ya existe versión

### Objetivo

**RAÍZ LIMPIA = PROYECTO PROFESIONAL**

- Máximo 20-25 archivos en raíz
- Solo configuración y archivos esenciales
- TODO lo demás en subdirectorios organizados
- Cero archivos temporales o de desarrollo en raíz

---

## 🚀 PROJECT OVERVIEW

MeStore is a complete marketplace/e-commerce system built with FastAPI (backend) and React+TypeScript (frontend). The project follows enterprise patterns with comprehensive testing, Docker deployment, and sophisticated database migrations.

### Tech Stack

**Backend:**
- FastAPI + SQLAlchemy Async
- PostgreSQL database
- Redis for caching
- JWT authentication
- Alembic migrations

**Frontend:**
- React + TypeScript
- Vite 7.1.4
- React Router v6
- Zustand (state management)
- Axios + React Query

**Testing:**
- pytest (backend)
- Vitest (frontend)
- E2E testing
- TDD framework

**Infrastructure:**
- Docker Compose
- Render (production backend)
- Vercel (production frontend)

---

## 📋 ESSENTIAL COMMANDS

### Backend Development

```bash
# Start development server
source .venv/bin/activate
uvicorn app.main:app --reload

# Database migrations
make migrate-upgrade                    # Apply pending migrations
make migrate-auto MSG="description"     # Generate auto migration
make migrate-current                    # Show current revision
make migrate-prod                       # Production migrations (with confirmations)

# Testing with TDD framework
./scripts/testing/run_tdd_tests.sh             # Full TDD test suite
./scripts/testing/run_tdd_tests.sh --tdd-only  # Only TDD marked tests
python -m pytest -m "tdd" -v                   # TDD tests directly
python -m pytest --cov=app --cov-report=term-missing  # Coverage report

# Docker development
docker-compose up -d                    # Start all services
docker-compose logs -f                  # View logs
docker-compose exec backend bash        # Backend shell
docker-compose exec backend pytest      # Run tests in Docker
```

### Frontend Development

```bash
cd frontend

# Development
npm run dev          # Development server (Vite)
npm run build        # Production build

# Testing
npm run test         # Vitest tests
npm run test:ci      # Tests with coverage

# Linting
npm run lint         # ESLint
npm run lint:fix     # Auto-fix linting issues
```

### Testing Commands

```bash
# Backend testing patterns
python -m pytest tests/ -v                           # All tests
python -m pytest tests/test_models_product.py -v     # Specific test file
python -m pytest -k "test_product" -v                # Pattern matching
python -m pytest -m "unit" -v                        # Test markers

# TDD-specific testing
python -m pytest -m "tdd" -v                         # TDD tests only
python -m pytest -m "red_test" -v                    # RED phase tests
python -m pytest -m "green_test" -v                  # GREEN phase tests
```

---

## 🏗️ ARCHITECTURE OVERVIEW

### Backend Structure (FastAPI)

```
app/
├── api/v1/          # API endpoints and routers
├── core/            # Application core (config, dependencies, middleware)
├── models/          # SQLAlchemy models
├── schemas/         # Pydantic schemas for validation
├── services/        # Business logic layer
├── database.py      # Database configuration
└── main.py          # FastAPI application entry point
```

### Frontend Structure (React+TypeScript)

```
frontend/src/
├── components/      # Reusable UI components
├── pages/           # Page components
├── hooks/           # Custom React hooks
├── utils/           # Utility functions
├── App.tsx          # Main app component
└── main.tsx         # Application entry point
```

### Testing Architecture

- **TDD Framework**: Custom TDD framework with RED-GREEN-REFACTOR markers
- **Test Categories**: Unit, integration, TDD, auth, database tests with pytest markers
- **Coverage**: Minimum 75% coverage enforced via scripts
- **Isolation**: Database test isolation with transaction rollback

---

## 🔑 KEY DEVELOPMENT PATTERNS

### Database Migrations

- **Alembic**: Multi-environment configuration (development/testing/production)
- **Make Commands**: Comprehensive Makefile with 30+ migration commands
- **Automated Scripts**: Python and bash scripts for deployment automation
- **Safety**: Production migrations require manual confirmation

### TDD Development Cycle

1. Write failing test with `@pytest.mark.red_test`
2. Implement minimal code to pass with `@pytest.mark.green_test`
3. Refactor with `@pytest.mark.refactor_test`
4. Use `./scripts/testing/run_tdd_tests.sh` to validate cycle

### API Development

- **Version Namespacing**: All endpoints under `/api/v1/`
- **Schema Validation**: Pydantic schemas for request/response validation
- **Exception Handling**: Centralized exception handlers
- **Documentation**: Auto-generated OpenAPI docs at `/docs`

### Service Integration

- **Search/Embeddings**: ChromaDB integration with vector search capabilities
- **Authentication**: JWT-based auth with role-based access control
- **Caching**: Redis integration for performance optimization
- **Background Tasks**: Async task processing with proper error handling

---

## 🐳 DOCKER DEVELOPMENT

### Container Services

- **backend**: FastAPI application on port 8000
- **frontend**: React application on port 5173
- **postgres**: PostgreSQL database on port 5432
- **redis**: Redis cache on port 6379
- **migrations**: Dedicated migration service

### Environment Management

- **Development**: `docker-compose.yml` with hot reload
- **Production**: `docker-compose.production.yml` with optimizations
- **Staging**: `docker-compose.staging.yml` for testing
- **Secrets**: `docker-compose.secrets.yml` for sensitive data

---

## ✅ CODE QUALITY STANDARDS

### Python (Backend)

- **Formatting**: Black, isort for code formatting
- **Linting**: Flake8 for code quality
- **Testing**: pytest with async support, fixtures, and markers
- **Type Hints**: Full type annotation required
- **Documentation**: Docstrings for all public methods

### TypeScript (Frontend)

- **Build Tool**: Vite for fast development and building
- **Testing**: Vitest + Testing Library for component testing
- **State Management**: Zustand for lightweight state management
- **HTTP Client**: Axios with React Query for data fetching
- **Routing**: React Router v6 for navigation

---

## 📍 IMPORTANT FILE LOCATIONS

### Configuration Files

- `alembic.ini` - Database migration configuration
- `.coveragerc` - Test coverage configuration
- `Makefile` - Migration and development commands
- `docker-compose.yml` - Development container orchestration

### Scripts

- `scripts/testing/run_tdd_tests.sh` - TDD test execution
- `scripts/database/run_migrations.py` - Migration management
- `scripts/deployment/deploy_migrations_python.sh` - Production deployment

### Testing

- `tests/conftest.py` - pytest configuration and fixtures
- `tests/tdd_framework.py` - TDD testing framework (si existe)
- `tests/database_isolation.py` - Database test isolation (si existe)

---

## 🔄 DEVELOPMENT WORKFLOW

1. **Feature Development**: Start with TDD tests, implement minimal functionality
2. **Database Changes**: Use `make migrate-auto` to generate migrations
3. **API Changes**: Update schemas, implement endpoints, add tests
4. **Frontend Integration**: Create components, hooks, and integrate with backend
5. **Testing**: Run full TDD suite before committing
6. **Deployment**: Use Docker Compose for local testing, scripts for production

---

## ⚙️ SERVICE DEPENDENCIES

When working with search/embedding features, note that ChromaDB and sentence-transformers are disabled in testing environments to avoid dependency conflicts. Use environment variables:

- `DISABLE_SEARCH_SERVICE=1`
- `DISABLE_CHROMA_SERVICE=1`

---

## ⚡ PERFORMANCE CONSIDERATIONS

- **Database**: PostgreSQL with async connections (asyncpg)
- **Caching**: Redis for session and query caching
- **Background Tasks**: Async processing for heavy operations
- **Frontend**: Code splitting and lazy loading with React Router
- **Build**: Optimized Docker multi-stage builds for production

---

## 🚀 PRODUCCIÓN ACTIVA

**Ver documentación completa**: `docs/deployment/PRODUCTION_OPERATIONS_GUIDE.md`

### Estado Actual

**Fecha de Despliegue**: 2025-10-05
**Estado del Sistema**: PRODUCCIÓN LIVE ✅
**Uptime Target**: 99.9%

### URLs de Producción

**Backend API (Render):**
- Base URL: https://mestore.onrender.com
- API Documentation: https://mestore.onrender.com/docs
- Health Check: https://mestore.onrender.com/health

**Frontend Application (Vercel):**
- Production URL: https://me-store-zbc5wx48r-jairos-projects-6e49f915.vercel.app
- Admin Portal: https://me-store-zbc5wx48r-jairos-projects-6e49f915.vercel.app/admin-portal
- Admin Login: https://me-store-zbc5wx48r-jairos-projects-6e49f915.vercel.app/admin-login

### Infraestructura de Producción

**Backend (Render):**
- ✅ FastAPI con Uvicorn
- ✅ PostgreSQL (34 tablas)
- ✅ 7 endpoints principales
- ✅ CORS configurado
- ✅ Migraciones Alembic

**Frontend (Vercel):**
- ✅ React + Vite desplegado
- ✅ Variables de entorno configuradas
- ✅ Build sin errores

### Agentes Responsables de Producción

| Área | Agente Responsable | Responsabilidades |
|------|-------------------|-------------------|
| **Infraestructura** | cloud-infrastructure-ai | Monitoreo Render/Vercel, uptime, scaling |
| **Backend API** | backend-framework-ai | Health checks, performance, bug fixes |
| **Frontend** | react-specialist-ai | UI/UX, performance, responsive design |
| **Base de Datos** | database-architect-ai | Query optimization, migrations, backups |
| **Seguridad** | security-backend-ai | Security monitoring, auth issues |
| **Testing** | tdd-specialist | Regression testing, E2E tests, QA |
| **Deployment** | devops-integration-ai | CI/CD pipeline, automation |

### Verificación Post-Deployment

```bash
# Verificar health check
curl https://mestore.onrender.com/health

# Verificar login admin
curl -X POST "https://mestore.onrender.com/api/v1/auth/admin-login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@mestocker.com", "password": "Admin123456"}'
```

### Documentación Adicional

- **Guía Completa de Operaciones**: `docs/deployment/PRODUCTION_OPERATIONS_GUIDE.md`
- **Plan de Recuperación**: Ver documento de operaciones
- **Monitoreo y Alertas**: Ver documento de operaciones
- **Protocolo de Deployment**: Ver documento de operaciones

---

## 📞 CONTACTO DE EMERGENCIA

**Para issues críticos en producción:**

- **Master Orchestrator**: Coordinación general de crisis
- **Cloud Infrastructure AI**: Issues de infraestructura Render/Vercel
- **Backend Framework AI**: Bugs críticos en API
- **Security Backend AI**: Brechas de seguridad
- **Database Architect AI**: Problemas de datos/queries

**Template de Reporte de Incidente**: Ver `docs/deployment/PRODUCTION_OPERATIONS_GUIDE.md`

---

## 🎯 RECURSOS ADICIONALES

### Documentación Principal

- **Project README**: `/README.md`
- **Documentation Index**: `/docs/README.md`
- **Scripts Guide**: `/scripts/README.md`
- **Workspace Guide**: `.workspace/QUICK_START_GUIDE.md`

### Guías Específicas

- **Production Operations**: `docs/deployment/PRODUCTION_OPERATIONS_GUIDE.md`
- **Workspace Protocol**: `docs/workspace/WORKSPACE_PROTOCOL.md` (si existe)
- **System Architecture**: `docs/architecture/SYSTEM_ARCHITECTURE.md` (si existe)
- **Development Guide**: `docs/guides/DEVELOPMENT_GUIDE.md` (si existe)

### Reportes y Auditorías

- **Latest Reports**: `docs/reports/testing/2025-Q4/`
- **Architecture Decisions**: `docs/architecture/`
- **Executive Summaries**: `docs/executive/`

---

**Última Actualización**: Octubre 2025
**Versión**: 2.0 (Simplificada y Reorganizada)
**Responsable**: Quality Operations Team
