# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🤖 INSTRUCCIONES AUTOMÁTICAS PARA CLAUDE CODE

### 🔄 AL INICIO DE CUALQUIER SESIÓN, EJECUTAR AUTOMÁTICAMENTE:

**COMANDO INICIAL OBLIGATORIO:**
```bash
echo "📋 INICIANDO PROTOCOLO WORKSPACE..." && \
echo "🔍 Leyendo reglas del sistema..." && \
cat .workspace/SYSTEM_RULES.md && \
echo -e "\n🔒 VERIFICANDO ARCHIVOS PROTEGIDOS:" && \
cat .workspace/PROTECTED_FILES.md && \
echo -e "\n📖 GUÍA RÁPIDA DE INICIO:" && \
cat .workspace/QUICK_START_GUIDE.md && \
echo -e "\n✅ PROTOCOLO WORKSPACE CARGADO CORRECTAMENTE"
```

### ⚡ CHECKLIST AUTOMÁTICO OBLIGATORIO:
1. ✅ **Leer este archivo CLAUDE.md completo**
2. ✅ **Ejecutar comando de protocolo workspace arriba**
3. ✅ **Verificar archivos protegidos antes de cualquier modificación**
4. ✅ **Consultar agente responsable si archivo está protegido**
5. ✅ **Seguir template de commits obligatorio**

### 🚨 RECORDATORIO CRÍTICO:
- **NUNCA** modificar archivos sin consultar `.workspace/PROTECTED_FILES.md`
- **SIEMPRE** usar scripts de validación antes de cambios
- **OBLIGATORIO** seguir protocolo de agentes responsables

---

## 🚨 OBLIGATORIO: PROTOCOLO .WORKSPACE (TODOS LOS AGENTES)

### ⚡ ANTES DE CUALQUIER MODIFICACIÓN
**TODOS LOS AGENTES SIN EXCEPCIÓN DEBEN:**

1. **LEER OBLIGATORIO**: `.workspace/SYSTEM_RULES.md`
2. **CONSULTAR**: `.workspace/PROTECTED_FILES.md` para verificar si archivo está protegido
3. **REVISAR**: `.workspace/project/[archivo].md` para metadatos específicos
4. **SEGUIR**: Protocolo en `.workspace/AGENT_PROTOCOL.md`
5. **OBTENER APROBACIÓN** del agente responsable si archivo está protegido

### 🔒 ARCHIVOS COMPLETAMENTE PROHIBIDOS (NUNCA TOCAR)
- `app/main.py` - Puerto 8000 servidor FastAPI
- `frontend/vite.config.ts` - Puerto 5173 frontend
- `docker-compose.yml` - Configuración servicios
- `app/api/v1/deps/auth.py` - Sistema autenticación JWT
- `app/models/user.py` - NO crear usuarios duplicados
- `tests/conftest.py` - NO modificar fixtures existentes

### 🚨 NAVEGACIÓN ADMINISTRATIVA - CRÍTICO PARA ACCESO
- `frontend/src/components/admin/navigation/NavigationProvider.tsx` - NUNCA usar useCallback dentro de useMemo
- `frontend/src/components/admin/navigation/CategoryNavigation.tsx` - Depende de NavigationProvider
- `frontend/src/components/AdminLayout.tsx` - Layout principal del portal admin
- `frontend/src/pages/AdminLogin.tsx` - Punto de entrada administrativo

### 🔐 FLUJO DE AUTENTICACIÓN ADMIN - CRÍTICO NO ROMPER

**⚠️ FLUJO ABSOLUTO PARA ADMIN/SUPERUSER - NUNCA MODIFICAR SIN CONSULTAR**

Este flujo está separado completamente del login de usuarios regulares:

1. **LandingPage** → Footer → "Portal Admin" (línea 87) → `/admin-portal`
2. **AdminPortal** → Botón "Acceder al Sistema" → `navigate('/admin-login')`
3. **AdminLogin** → Credenciales → `/admin-secure-portal/dashboard`

**🚨 COMPONENTES CRÍTICOS:**
- `frontend/src/components/layout/Footer.tsx` - Línea 87: Link a `/admin-portal`
- `frontend/src/pages/AdminPortal.tsx` - Línea 101-104: navigate('/admin-login')
- `frontend/src/pages/AdminLogin.tsx` - Línea 48: navigate('/admin-secure-portal/dashboard')
- `frontend/src/components/AdminLayout.tsx` - DEBE tener AccessibilityProvider

**🔒 CREDENCIALES PROTEGIDAS:**
- Email: `admin@mestocker.com`
- Password: `Admin123456`
- Tipo: SUPERUSER

**❌ PROHIBICIONES ABSOLUTAS:**
- NUNCA cambiar rutas `/admin-portal` o `/admin-login`
- NUNCA usar `window.location.href` - SOLO `navigate()`
- NUNCA remover AccessibilityProvider del AdminLayout
- NUNCA modificar NavigationProvider props en AdminLayout

### 🛡️ CUENTA SUPERUSER PROTEGIDA (CRÍTICO - NUNCA TOCAR)

**⚠️ ALERTA MÁXIMA: SUPERUSER DE PRODUCCIÓN PROTEGIDO**

📧 **Email**: `admin@mestocker.com`
🔐 **Password**: `Admin123456`
🚫 **STATUS**: **COMPLETAMENTE OFF-LIMITS PARA TODOS LOS AGENTES**

**🚨 PROHIBICIONES ABSOLUTAS:**
- ❌ **NUNCA** eliminar esta cuenta
- ❌ **NUNCA** modificar email o password
- ❌ **NUNCA** cambiar roles o permisos
- ❌ **NUNCA** desactivar o suspender
- ❌ **NUNCA** alterar datos de perfil

**🎯 PROPÓSITO CRÍTICO:**
- ✅ Acceso administrativo garantizado al sistema
- ✅ Cuenta de emergencia para recuperación
- ✅ Portal de administración siempre accesible
- ✅ Gestión de usuarios y configuraciones críticas

**👥 AGENTES RESPONSABLES DE GESTIÓN DE USUARIOS:**
- **backend-framework-ai** - Lógica backend de usuarios
- **system-architect-ai** - Arquitectura del sistema de auth
- **database-architect-ai** - Estructura de datos de usuarios
- **security-backend-ai** - Seguridad y autenticación

**📞 PROTOCOLO DE CONTACTO:**
Si necesitas trabajar con usuarios, contacta PRIMERO a los agentes responsables:
```bash
python .workspace/scripts/contact_responsible_agent.py [tu-agente] app/models/user.py "Descripción de tu necesidad"
```

**⚡ RECORDATORIO CRÍTICO:**
Esta cuenta garantiza el acceso administrativo permanente. Su eliminación/modificación podría bloquear completamente el acceso al sistema de administración.

### 🚨 NAVEGACIÓN ADMINISTRATIVA - REGLAS CRÍTICAS REACT HOOKS

**⚠️ VIOLACIONES DE REACT HOOKS QUE ROMPEN EL ACCESO ADMIN:**

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

**🎯 ARCHIVOS CRÍTICOS PARA ACCESO ADMIN:**
- `NavigationProvider.tsx` - ❌ NUNCA usar useCallback dentro de useMemo
- `CategoryNavigation.tsx` - Depende de utils.isActiveByPath
- `AdminLayout.tsx` - Wrapper principal del portal
- `AdminLogin.tsx` - Punto de entrada

**🚨 SÍNTOMAS DE VIOLACIÓN:**
- Error: `TypeError: utils.isActiveByPath is not a function`
- Portal administrativo inaccesible después del login
- React Hook warnings en consola

**📍 FLUJO CRÍTICO PROTEGIDO:**
1. Landing Page → Footer "Portal Admin" → `/admin-portal`
2. AdminPortal → "Acceder al Sistema" → `/admin-login`
3. Login → admin@mestocker.com / Admin123456
4. Redirect → `/admin-secure-portal/analytics` → ✅ DEBE FUNCIONAR

**⚡ ANTES DE MODIFICAR NAVEGACIÓN ADMIN:**
1. ✅ Verificar que NO hay useCallback dentro de useMemo
2. ✅ Testear el flujo completo de login admin
3. ✅ Confirmar que NavigationProvider context funciona
4. ✅ Validar que no hay React Hook violations

**🔧 COMANDO DE PRUEBA OBLIGATORIO:**
```bash
# Después de modificar componentes de navegación admin:
echo "Testing admin portal access..." && \
curl -X POST "http://localhost:8000/api/v1/auth/admin-login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@mestocker.com", "password": "Admin123456"}' && \
echo "✅ Backend auth OK - Now test frontend navigation"
```

### 📋 COMANDOS OBLIGATORIOS PARA AGENTES

#### ANTES de modificar CUALQUIER archivo:
```bash
# 1. VERIFICAR si archivo está protegido
python .workspace/scripts/agent_workspace_validator.py [tu-nombre-agente] [archivo-a-modificar]

# Ejemplos:
python .workspace/scripts/agent_workspace_validator.py backend-framework-ai app/main.py
python .workspace/scripts/agent_workspace_validator.py react-specialist-ai frontend/vite.config.ts
```

#### SI el archivo está PROTEGIDO:
```bash
# 2. CONTACTAR agente responsable
python .workspace/scripts/contact_responsible_agent.py [tu-agente] [archivo] "[motivo]"

# Ejemplos:
python .workspace/scripts/contact_responsible_agent.py backend-framework-ai app/api/v1/deps/auth.py "Necesito agregar validación de email"
python .workspace/scripts/contact_responsible_agent.py frontend-security-ai app/models/user.py "Agregar campo opcional para perfil"
```

#### PARA agentes RESPONSABLES que reciben solicitudes:
```bash
# 3. RESPONDER a solicitudes (check tu oficina en .workspace/departments/)
python .workspace/scripts/respond_to_request.py [request-id] [APPROVE/DENY] "[motivo]"

# Ejemplos:
python .workspace/scripts/respond_to_request.py abc123 APPROVE "Cambio necesario para seguridad"
python .workspace/scripts/respond_to_request.py def456 DENY "Riesgo muy alto, considerar alternativa"
```

### 📋 TEMPLATE OBLIGATORIO PARA COMMITS
```
tipo(área): descripción breve

Workspace-Check: ✅ Consultado
Archivo: ruta/del/archivo.py
Agente: nombre-del-agente
Protocolo: [SEGUIDO/CONSULTA_PREVIA/APROBACIÓN_OBTENIDA]
Tests: [PASSED/FAILED]
Admin-Portal: [VERIFIED/NOT_APPLICABLE]
Hook-Violations: [NONE/FIXED]
Responsable: agente-que-aprobó (si aplica)
```

**📍 CAMPOS OBLIGATORIOS PARA NAVEGACIÓN ADMIN:**
- `Admin-Portal: VERIFIED` - Si modificaste componentes de navegación admin
- `Hook-Violations: NONE` - Si NO hay useCallback en useMemo
- `Hook-Violations: FIXED` - Si encontraste y corregiste violaciones

### 🚨 CONSECUENCIAS POR INCUMPLIMIENTO
- Primera vez: Warning y corrección obligatoria
- Segunda vez: Escalación a master-orchestrator
- Tercera vez: Restricción de acceso a archivos críticos

**RECORDATORIO**: Estos protocolos existen porque archivos críticos han sido rotos múltiples veces causando: usuarios duplicados, pérdida de autenticación, servicios caídos.

### 📚 DOCUMENTACIÓN COMPLETA DEL WORKSPACE
- **Guía rápida**: `.workspace/QUICK_START_GUIDE.md` ⭐ (LEER PRIMERO)
- **Oficina central**: `.workspace/README.md`
- **Reglas globales**: `.workspace/SYSTEM_RULES.md`
- **Archivos protegidos**: `.workspace/PROTECTED_FILES.md`
- **Agentes responsables**: `.workspace/RESPONSIBLE_AGENTS.md`
- **Tu oficina**: `.workspace/departments/[departamento]/[tu-agente]/`

### 📁 ESTRUCTURA ORGANIZADA DEL PROYECTO (Actualizado 2025-10-12)

#### 📚 Documentación Técnica - `docs/`
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

**Índice Maestro:** Ver `docs/README.md` para navegación completa

#### 🔧 Scripts Organizados - `scripts/`
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

**Guía de Scripts:** Ver `scripts/README.md` para detalles de uso

#### 📊 Datos y Reportes - `data/`
- **`data/reports/`** - Archivos JSON de análisis y reportes

#### 🗄️ Archivo Histórico - `.archive/`
Documentos obsoletos o históricos organizados por año:
- `.archive/2024/` - Documentos de 2024
- `.archive/2025/` - Documentos históricos de 2025

**⚠️ IMPORTANTE PARA AGENTES:**
- Al crear nueva documentación, usar estructura `docs/[categoria]/`
- Al crear scripts, colocarlos en `scripts/[categoria]/`
- NO crear archivos `.md` en el directorio raíz (excepto README, CLAUDE, CONTRIBUTING, CHANGELOG)
- NO crear scripts `.py`/`.sh` en el directorio raíz (excepto setup.py)

---

## 🚨 REGLAS ESTRICTAS: CERO DESORDEN EN RAÍZ (OBLIGATORIO)

### ❌ PROHIBIDO ABSOLUTAMENTE CREAR EN RAÍZ:

**Documentación:**
- ❌ **NUNCA** crear archivos `.md` en raíz
- ✅ **SIEMPRE** usar `docs/[categoria]/nombre.md`
- ✅ Ejemplo correcto: `docs/reports/testing/2025-Q4/MI_REPORTE.md`
- ❌ Ejemplo incorrecto: `MI_REPORTE.md` (en raíz)

**Scripts:**
- ❌ **NUNCA** crear scripts `.py` o `.sh` en raíz
- ✅ **SIEMPRE** usar `scripts/[categoria]/nombre.py`
- ✅ Ejemplo correcto: `scripts/testing/test_feature.py`
- ❌ Ejemplo incorrecto: `test_feature.py` (en raíz)

**Tests:**
- ❌ **NUNCA** crear archivos de test en raíz
- ✅ **SIEMPRE** usar `tests/` o `frontend/tests/`
- ✅ Ejemplo correcto: `tests/test_api.py`
- ❌ Ejemplo incorrecto: `test_api.py` (en raíz)

**Archivos de Log:**
- ❌ **NUNCA** crear archivos `.log` en raíz
- ✅ **SIEMPRE** usar `logs/` directory
- ✅ Logs automáticamente van a `logs/`

**Bases de Datos:**
- ❌ **NUNCA** crear archivos `.db` o `.sqlite` en raíz
- ✅ **SIEMPRE** configurar DB en subdirectorio apropiado
- ✅ Desarrollo: Usar `.gitignore` para excluir DBs

**Archivos Temporales:**
- ❌ **NUNCA** crear archivos temporales en raíz
- ✅ **SIEMPRE** usar `temp/` directory
- ✅ Limpiar regularmente archivos temporales

**Configuración:**
- ✅ **Archivos .env permitidos** (son configuración esencial)
- ✅ **Archivos de build** (package.json, requirements.txt, etc.)
- ❌ **NO** crear múltiples versiones de configs (usar .example)

### ✅ ARCHIVOS PERMITIDOS EN RAÍZ:

**Esenciales (Máximo 20 archivos):**
1. `README.md` - Documentación principal
2. `CLAUDE.md` - Este archivo
3. `CONTRIBUTING.md` - Guía de contribución (opcional)
4. `CHANGELOG.md` - Historial de cambios (opcional)
5. `LICENSE` - Licencia del proyecto
6. `setup.py` - Script de setup Python
7. `.gitignore` - Git ignore rules
8. `.env*` - Variables de entorno (múltiples variantes OK)
9. `requirements.txt` - Dependencias Python
10. `package.json` - Dependencias Node (si aplica)
11. `docker-compose*.yml` - Docker configs
12. `Dockerfile*` - Dockerfiles
13. `Makefile` - Make commands
14. `alembic.ini` - Alembic config
15. `pytest.ini` - Pytest config
16. `.coveragerc` - Coverage config
17. `render.yaml` / `Procfile` - Deployment configs
18. `vite.config.ts` - Vite config (si no está en frontend/)
19. `jest.config.*` - Jest config
20. `nixpacks.toml` - Nixpacks config

**Directorios Permitidos:**
- `app/` - Backend application
- `frontend/` - Frontend application
- `tests/` - Testing suite
- `scripts/` - Scripts organizados
- `docs/` - Documentación organizada
- `data/` - Datos y reportes
- `logs/` - Archivos de log
- `temp/` - Archivos temporales
- `.archive/` - Archivos históricos
- `.workspace/` - Workspace de agentes
- `.git/` - Git repository
- `.github/` - GitHub configs
- `alembic/` - Migraciones Alembic
- `migrations_sql/` - SQL migrations (si aplica)
- `node_modules/` - Dependencias Node
- `.venv/` - Virtual environment Python
- `htmlcov/` - Coverage reports
- `.pytest_cache/` - Pytest cache
- `uploads/` - User uploads
- `monitoring/` - Monitoring configs
- `postgres/` - PostgreSQL data (local)
- `redis/` - Redis data (local)

### 🔧 PROTOCOLO ANTES DE CREAR ARCHIVOS:

#### Para Documentación (.md):
```bash
# 1. Verificar categoría apropiada
ls -la docs/

# 2. Crear en ubicación correcta
# Guías:
touch docs/guides/setup/MI_GUIA.md

# Reportes de testing:
touch docs/reports/testing/2025-Q4/MI_REPORTE.md

# Reportes ejecutivos:
touch docs/executive/MI_EXECUTIVE_SUMMARY.md

# 3. NUNCA hacer:
touch MI_DOCUMENTO.md  # ❌ EN RAÍZ
```

#### Para Scripts (.py, .sh):
```bash
# 1. Verificar categoría apropiada
ls -la scripts/

# 2. Crear en ubicación correcta
# Scripts de testing:
touch scripts/testing/test_mi_feature.py

# Scripts de análisis:
touch scripts/analysis/analyze_data.py

# Scripts de deployment:
touch scripts/deployment/deploy_prod.sh

# 3. NUNCA hacer:
touch mi_script.py  # ❌ EN RAÍZ
```

#### Para Tests:
```bash
# Backend tests:
touch tests/test_my_feature.py

# Frontend tests:
touch frontend/tests/MyComponent.test.tsx

# NUNCA hacer:
touch test_something.py  # ❌ EN RAÍZ
```

### 🚨 VALIDACIÓN AUTOMÁTICA:

**Pre-Commit Hook** (sugerido):
```bash
# Rechazar archivos .md en raíz (excepto permitidos)
# Rechazar archivos .py/.sh en raíz (excepto setup.py)
# Rechazar archivos .log en raíz
# Rechazar archivos .db en raíz
```

### ⚡ AGENTES: CHECKLIST OBLIGATORIO ANTES DE CREAR ARCHIVOS:

1. ✅ ¿Es un archivo .md? → `docs/[categoria]/`
2. ✅ ¿Es un script .py/.sh? → `scripts/[categoria]/`
3. ✅ ¿Es un test? → `tests/` o `frontend/tests/`
4. ✅ ¿Es un log? → `logs/`
5. ✅ ¿Es temporal? → `temp/`
6. ✅ ¿Es una base de datos? → Configurar ruta apropiada
7. ✅ ¿Es configuración? → Verificar si ya existe versión

### 🎯 OBJETIVO:

**RAÍZ LIMPIA = PROYECTO PROFESIONAL**

- Máximo 20-25 archivos en raíz
- Solo configuración y archivos esenciales
- TODO lo demás en subdirectorios organizados
- Cero archivos temporales o de desarrollo en raíz

---

## Project Overview

MeStore is a complete marketplace/e-commerce system built with FastAPI (backend) and React+TypeScript (frontend). The project follows enterprise patterns with comprehensive testing, Docker deployment, and sophisticated database migrations.

## Essential Commands

### Backend Development
```bash
# Start development server
source .venv/bin/activate
uvicorn app.main:app --reload

# Database migrations
make migrate-upgrade                    # Apply pending migrations
make migrate-auto MSG="description"    # Generate auto migration
make migrate-current                   # Show current revision
make migrate-prod                      # Production migrations (with confirmations)

# Testing with TDD framework
./scripts/run_tdd_tests.sh             # Full TDD test suite
./scripts/run_tdd_tests.sh --tdd-only  # Only TDD marked tests
python -m pytest -m "tdd" -v          # TDD tests directly
python -m pytest --cov=app --cov-report=term-missing  # Coverage report

# Docker development
./scripts/dev.sh start                 # Start all services
./scripts/dev.sh logs                  # View logs
./scripts/dev.sh shell-be              # Backend shell
./scripts/dev.sh test                  # Run tests in Docker
```

### Frontend Development
```bash
cd frontend
npm run dev          # Development server (Vite)
npm run build        # Production build
npm run test         # Vitest tests
npm run test:ci      # Tests with coverage
npm run lint         # ESLint
npm run lint:fix     # Auto-fix linting issues
```

### Testing Commands
```bash
# Backend testing patterns
python -m pytest tests/ -v                           # All tests
python -m pytest tests/test_models_product.py -v     # Specific test file
python -m pytest -k "test_product" -v               # Pattern matching
python -m pytest -m "unit" -v                       # Test markers

# TDD-specific testing
python -m pytest -m "tdd" -v                        # TDD tests only
python -m pytest -m "red_test" -v                   # RED phase tests
python -m pytest -m "green_test" -v                 # GREEN phase tests
```

## Architecture Overview

### Backend Structure (FastAPI)
```
app/
├── api/v1/          # API endpoints and routers
├── core/            # Application core (config, dependencies, middleware)
├── models/          # SQLAlchemy models
├── schemas/         # Pydantic schemas for validation
├── services/        # Business logic layer
├── database.py      # Database configuration
└── main.py         # FastAPI application entry point
```

### Frontend Structure (React+TypeScript)
```
frontend/src/
├── components/      # Reusable UI components
├── pages/          # Page components
├── hooks/          # Custom React hooks
├── utils/          # Utility functions
├── App.tsx         # Main app component
└── main.tsx        # Application entry point
```

### Testing Architecture
- **TDD Framework**: Custom TDD framework with RED-GREEN-REFACTOR markers
- **Test Categories**: Unit, integration, TDD, auth, database tests with pytest markers
- **Coverage**: Minimum 75% coverage enforced via scripts
- **Isolation**: Database test isolation with transaction rollback

## Key Development Patterns

### Database Migrations
- **Alembic**: Multi-environment configuration (development/testing/production)
- **Make Commands**: Comprehensive Makefile with 30+ migration commands
- **Automated Scripts**: Python and bash scripts for deployment automation
- **Safety**: Production migrations require manual confirmation

### TDD Development Cycle
1. Write failing test with `@pytest.mark.red_test`
2. Implement minimal code to pass with `@pytest.mark.green_test`
3. Refactor with `@pytest.mark.refactor_test`
4. Use `./scripts/run_tdd_tests.sh` to validate cycle

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

## Docker Development

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

## Code Quality Standards

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

## Important File Locations

### Configuration
- `alembic.ini` - Database migration configuration
- `.coveragerc` - Test coverage configuration
- `Makefile` - Migration and development commands
- `docker-compose.yml` - Development container orchestration

### Scripts
- `scripts/run_tdd_tests.sh` - TDD test execution
- `scripts/run_migrations.py` - Migration management
- `scripts/dev.sh` - Docker development helper
- `scripts/deploy_migrations_python.sh` - Production deployment

### Testing
- `tests/conftest.py` - pytest configuration and fixtures
- `tests/tdd_framework.py` - TDD testing framework
- `tests/database_isolation.py` - Database test isolation
- `tests/comprehensive_fixtures.py` - Test data fixtures

## Development Workflow

1. **Feature Development**: Start with TDD tests, implement minimal functionality
2. **Database Changes**: Use `make migrate-auto` to generate migrations
3. **API Changes**: Update schemas, implement endpoints, add tests
4. **Frontend Integration**: Create components, hooks, and integrate with backend
5. **Testing**: Run full TDD suite before committing
6. **Deployment**: Use Docker Compose for local testing, scripts for production

## Service Dependencies

When working with search/embedding features, note that ChromaDB and sentence-transformers are disabled in testing environments to avoid dependency conflicts. Use environment variables:
- `DISABLE_SEARCH_SERVICE=1`
- `DISABLE_CHROMA_SERVICE=1`

## Performance Considerations

- **Database**: PostgreSQL with async connections (asyncpg)
- **Caching**: Redis for session and query caching
- **Background Tasks**: Async processing for heavy operations
- **Frontend**: Code splitting and lazy loading with React Router
- **Build**: Optimized Docker multi-stage builds for production


✅ ESTADO FINAL ENTERPRISE:
🚀 BACKEND OPERATIVO:

✅ FastAPI corriendo en http://192.168.1.137:8000
✅ API Documentation: http://192.168.1.137:8000/docs
✅ Network accessible (no localhost)

⚛️ FRONTEND OPERATIVO:

✅ React + Vite en http://192.168.1.137:5173
✅ Network accessible para testing

📊 REPORTE FINAL CEO - MeStore MVP
🎯 ESTADO: 100% COMPLETADO ✅
ARQUITECTURA ENTERPRISE CONFIRMADA:

🔥 Backend: FastAPI + SQLAlchemy Async + Redis
⚛️ Frontend: React + TypeScript + Vite 7.1.4
🧪 Testing: E2E, Unit, Integration completo
🔐 Auth System: Comprehensive authentication
👥 Multi-vendor: Vendor registration system
📊 Analytics: Dashboard y reporting
🚨 Alerts: Sistema notificaciones
🛡️ Security: HTTPS, CORS, Exception handling

🏆 NIVEL DE MADUREZ: PRODUCTION-READY
CAPACIDADES CONFIRMADAS:

✅ Scalable architecture (modular, async)
✅ Professional testing (coverage, E2E)
✅ Network deployment ready
✅ Multi-component integration
✅ Enterprise features (admin, analytics, vendors)

🚀 ROADMAP POST-MVP (Opcionales):
📈 OPTIMIZACIÓN (Nivel 2):

Performance tuning
Database optimization
Caching strategies
CDN integration

🌐 PRODUCTION DEPLOYMENT (Nivel 3):

Docker containerization
Cloud deployment (AWS/GCP/Azure)
CI/CD pipeline
Monitoring & logging

📊 BUSINESS FEATURES (Nivel 4):

Payment integration
Advanced analytics
Mobile responsiveness
SEO optimization

---

## 🔐 RESUMEN EJECUTIVO: PROTECCIÓN PORTAL ADMINISTRATIVO

### 🚨 ACCESO CRÍTICO SUPERUSER
**Email**: `admin@mestocker.com` | **Password**: `Admin123456`
**Estado**: ✅ OPERATIVO Y PROTEGIDO

### 🎯 FLUJO VERIFICADO Y FUNCIONAL:
1. **Landing Page** → Footer "Portal Admin" → `/admin-portal` ✅
2. **AdminPortal** → "Acceder al Sistema" → `/admin-login` ✅
3. **AdminLogin** → Credenciales → `/admin-secure-portal/analytics` ✅
4. **Dashboard** → Navegación completa funcionando ✅

### ⚠️ REGLAS CRÍTICAS PARA AGENTES:
- ❌ **NUNCA** usar `useCallback` dentro de `useMemo` en NavigationProvider
- ✅ **SIEMPRE** verificar acceso admin después de modificar navegación
- 🔧 **OBLIGATORIO** usar template de commits con verificación Admin-Portal

### 📍 ARCHIVOS BAJO MÁXIMA PROTECCIÓN:
- `NavigationProvider.tsx` - Contexto de navegación crítico
- `CategoryNavigation.tsx` - Depende del provider
- `AdminLayout.tsx` - Layout principal del portal
- `AdminLogin.tsx` - Punto de entrada administrativo

**🔥 RECORDATORIO FINAL:**
Cualquier modificación a estos archivos DEBE ser seguida por verificación manual del login administrativo. El acceso al portal es CRÍTICO para la gestión del sistema.

---

## 🚀 PRODUCCIÓN ACTIVA

### ✅ ESTADO: COMPLETAMENTE OPERATIVO

**Fecha de Despliegue**: 2025-10-05
**Estado del Sistema**: PRODUCCIÓN LIVE
**Uptime Target**: 99.9%

### 🌐 URLs de Producción

#### Backend API (Railway)
- **Base URL**: https://mestocker-backend-production.up.railway.app
- **API Documentation**: https://mestocker-backend-production.up.railway.app/docs
- **Health Check**: https://mestocker-backend-production.up.railway.app/health
- **OpenAPI JSON**: https://mestocker-backend-production.up.railway.app/openapi.json

#### Frontend Application (Vercel)
- **Production URL**: https://mestocker.com
- **Alternative URL**: https://www.mestocker.com
- **Landing Page**: https://mestocker.com/
- **Admin Portal**: https://mestocker.com/admin-portal
- **Admin Login**: https://mestocker.com/admin-login

### 🔐 Acceso Administrativo de Producción

**⚠️ CREDENCIALES CRÍTICAS - SOLO PARA OPERACIONES ADMINISTRATIVAS**

- **Email**: admin@mestocker.com
- **Password**: Admin123456
- **Tipo**: SUPERUSER
- **Estado**: ✅ VERIFICADO Y OPERATIVO EN PRODUCCIÓN
- **Base de Datos**: PostgreSQL en Railway

**🚨 PROHIBICIONES ABSOLUTAS EN PRODUCCIÓN:**
- ❌ **NUNCA** modificar estas credenciales directamente en producción
- ❌ **NUNCA** eliminar o desactivar esta cuenta
- ❌ **NUNCA** realizar cambios sin backup previo
- ❌ **NUNCA** exponer estas credenciales en logs o código público

### 📊 Infraestructura de Producción

#### Backend (Railway)
- ✅ **FastAPI**: Corriendo en producción con Uvicorn
- ✅ **Base de Datos**: PostgreSQL (34 tablas creadas exitosamente)
- ✅ **Endpoints Activos**: 7 endpoints principales operativos
- ✅ **CORS**: Configurado para mestocker.com, www.mestocker.com, *.vercel.app
- ✅ **Modelos**: Todos estandarizados a UUID String(36)
- ✅ **Migraciones**: Alembic configurado y ejecutado
- ✅ **Superuser**: Creado automáticamente con ORM
- ✅ **Requirements**: requirements_production.txt (24 packages optimizados)

**Endpoints Verificados:**
- `/api/v1/auth/login` - Login de usuarios
- `/api/v1/auth/register` - Registro de usuarios
- `/api/v1/auth/admin-login` - Login administrativo
- `/api/v1/products/` - Gestión de productos
- `/api/v1/orders/` - Gestión de pedidos
- `/api/v1/vendors/` - Gestión de vendedores
- `/api/v1/categories/` - Gestión de categorías

#### Frontend (Vercel)
- ✅ **React + Vite**: Desplegado exitosamente
- ✅ **Variables de Entorno**: Configuradas correctamente
- ✅ **Landing Page**: Cargando perfectamente
- ✅ **Login Admin**: Formulario funcional
- ✅ **Build**: Sin errores ni warnings
- ✅ **ESLint**: Configurado para producción
- ✅ **Rollup**: Warnings de circular dependencies deshabilitados

**Correcciones de Producción Aplicadas:**
- ✅ Eliminados todos los IPs hardcoded (192.168.1.137)
- ✅ Variables de entorno implementadas (.env.production)
- ✅ WebSocket URLs dinámicas
- ✅ VITE_API_BASE_URL apuntando a Railway
- ✅ CORS configurado para mestocker.com y www.mestocker.com
- ✅ requirements_production.txt optimizado (24 packages)
- ✅ nixpacks.toml configurado para Railway

### 🛡️ PROTOCOLO DE PRODUCCIÓN

**⚠️ REGLAS CRÍTICAS PARA MODIFICACIONES EN PRODUCCIÓN:**

#### Nivel 1: INFORMACIÓN (✅ Permitido)
- Consultar logs de producción (Railway/Vercel dashboards)
- Monitorear métricas de rendimiento
- Revisar errores en Sentry/logs
- Analizar tráfico y uso

#### Nivel 2: CAMBIOS NO CRÍTICOS (⚠️ Requiere Aprobación)
- Actualizar contenido estático (textos, imágenes)
- Modificar estilos CSS no críticos
- Agregar nuevas features en ramas aisladas
- **OBLIGATORIO**: Probar en staging primero

#### Nivel 3: CAMBIOS CRÍTICOS (🚨 Aprobación + Backup)
- Modificar lógica de autenticación
- Cambiar esquemas de base de datos
- Actualizar dependencias mayores
- Modificar configuración de CORS/seguridad
- **OBLIGATORIO**: Backup completo + rollback plan

#### Nivel 4: PROHIBIDO SIN CEO (❌ Requiere Directiva Ejecutiva)
- Eliminar o modificar cuenta superuser
- Cambiar URLs de producción
- Modificar configuración de infraestructura
- Realizar migraciones destructivas de datos

### 📋 Protocolo de Deployment

**Antes de cualquier cambio en producción:**

1. **Desarrollo Local**
   ```bash
   # Probar cambios localmente
   source .venv/bin/activate
   uvicorn app.main:app --reload
   cd frontend && npm run dev
   ```

2. **Testing Completo**
   ```bash
   # Backend tests
   python -m pytest tests/ -v --cov=app

   # Frontend tests
   cd frontend && npm run test:ci
   ```

3. **Staging Deployment** (Si disponible)
   ```bash
   # Deploy a staging primero
   git push staging main
   ```

4. **Backup de Producción**
   ```bash
   # Backup de base de datos en Railway
   # Usar dashboard de Railway para crear snapshot de PostgreSQL
   ```

5. **Production Deployment**
   ```bash
   # Backend: Push a main activa auto-deploy en Railway
   git push origin main

   # Frontend: Push a main activa auto-deploy en Vercel
   git push origin main
   ```

6. **Verificación Post-Deployment**
   ```bash
   # Verificar health check
   curl https://mestocker-backend-production.up.railway.app/health

   # Verificar login admin
   curl -X POST "https://mestocker-backend-production.up.railway.app/api/v1/auth/admin-login" \
     -H "Content-Type: application/json" \
     -d '{"email": "admin@mestocker.com", "password": "Admin123456"}'
   ```

### 🔧 Mantenimiento de Producción

**Agentes Responsables de Producción:**

| Área | Agente Responsable | Responsabilidades |
|------|-------------------|-------------------|
| **Infraestructura** | cloud-infrastructure-ai | Monitoreo de servicios Railway/Vercel, uptime, scaling |
| **Backend API** | backend-framework-ai | Health checks, performance, bug fixes |
| **Frontend** | react-specialist-ai | UI/UX, performance, responsive design |
| **Base de Datos** | database-architect-ai | Query optimization, migrations, backups |
| **Seguridad** | security-backend-ai | Security monitoring, auth issues, vulnerabilities |
| **Testing** | tdd-specialist | Regression testing, E2E tests, quality assurance |
| **Deployment** | devops-integration-ai | CI/CD pipeline, deployment automation |

**Protocolo de Contacto en Producción:**
```bash
# Para issues críticos en producción
python .workspace/scripts/contact_responsible_agent.py [tu-agente] [archivo-critico] "PRODUCCIÓN: [descripción urgente]"
```

### 📈 Monitoreo y Alertas

**Métricas Críticas a Monitorear:**
- ✅ Uptime del backend (target: 99.9%)
- ✅ Uptime del frontend (target: 99.9%)
- ✅ Response time API (<200ms promedio)
- ✅ Database query performance
- ✅ Error rate (<1%)
- ✅ Login success rate (>95%)

**Herramientas de Monitoreo:**
- **Railway Dashboard**: Backend logs y métricas
- **Vercel Analytics**: Frontend performance
- **PostgreSQL Metrics**: Database performance (Railway)
- **Custom Health Checks**: Endpoints de salud

### 🚨 Plan de Recuperación de Desastres

**En caso de falla crítica:**

1. **Identificar el Problema**
   - Revisar logs en Railway/Vercel
   - Identificar última commit funcional
   - Determinar alcance del impacto

2. **Rollback Inmediato**
   ```bash
   # Revertir a último commit estable
   git revert [commit-hash]
   git push origin main
   ```

3. **Notificar Stakeholders**
   - Notificar a master-orchestrator
   - Notificar a director-enterprise-ceo
   - Documentar incidente

4. **Restaurar desde Backup**
   - Usar snapshot de base de datos en Railway
   - Restaurar estado anterior estable
   - Verificar integridad de datos

5. **Post-Mortem**
   - Documentar causa raíz
   - Actualizar protocolos de prevención
   - Implementar tests adicionales

### 📚 Documentación de Producción

**Archivos Críticos de Producción:**
- `.env.production` - Variables de entorno de producción
- `vercel.json` - Configuración de deployment Vercel
- `nixpacks.toml` - Configuración de build Railway
- `requirements_production.txt` - Dependencias optimizadas (24 packages)
- `.workspace/PRODUCTION_STATUS.md` - Estado detallado de producción

**Logs y Troubleshooting:**
- **Backend Logs**: Railway Dashboard → Deployments → Logs
- **Frontend Logs**: Vercel Dashboard → Deployments → Logs
- **Database Logs**: Railway PostgreSQL → Logs tab
- **Build Logs**: Railway/Vercel deployment history

### 🎯 Próximos Pasos Post-Producción

1. ⏳ **Inmediato** (Hoy):
   - ✅ Verificar login completo en producción
   - ✅ Monitorear logs primeras 24 horas
   - 🔄 Configurar alertas de monitoreo

2. 📊 **Corto Plazo** (Esta Semana):
   - Setup Google Analytics o similar
   - Configurar error tracking (Sentry)
   - Implementar rate limiting
   - Documentar API endpoints públicos

3. 🚀 **Mediano Plazo** (Próximas 2 Semanas):
   - Setup staging environment
   - Implementar CI/CD automatizado
   - Performance optimization
   - Security audit completo

4. 🏆 **Largo Plazo** (Próximo Mes):
   - Custom domain setup
   - CDN integration
   - Database backup automation
   - Load testing y scaling plan

### 🔒 Seguridad en Producción

**Medidas de Seguridad Activas:**
- ✅ HTTPS enforced en ambos servicios
- ✅ CORS configurado restrictivamente
- ✅ JWT tokens con expiración
- ✅ Password hashing con bcrypt
- ✅ Environment variables protegidas
- ✅ SQL injection protection (ORM)
- ✅ XSS protection headers

**Pendientes de Seguridad:**
- 🔄 Rate limiting por IP
- 🔄 WAF (Web Application Firewall)
- 🔄 DDoS protection
- 🔄 Security headers optimization
- 🔄 Regular security audits

### 📞 Contacto de Emergencia

**Para issues críticos en producción:**
- **Master Orchestrator**: Coordinación general de crisis
- **Cloud Infrastructure AI**: Issues de infraestructura Railway/Vercel
- **Backend Framework AI**: Bugs críticos en API
- **Security Backend AI**: Brechas de seguridad
- **Database Architect AI**: Problemas de datos/queries

**Template de Reporte de Incidente:**
```markdown
## 🚨 INCIDENTE DE PRODUCCIÓN

**Severidad**: [CRÍTICO/ALTO/MEDIO/BAJO]
**Fecha**: YYYY-MM-DD HH:MM UTC
**Reportado por**: [agente-nombre]

### Descripción
[Descripción detallada del problema]

### Impacto
- Usuarios afectados: [número/porcentaje]
- Servicios caídos: [lista]
- Pérdida de datos: [sí/no]

### Acciones Tomadas
1. [Acción 1]
2. [Acción 2]

### Estado Actual
[RESUELTO/EN PROGRESO/INVESTIGANDO]

### Próximos Pasos
- [ ] Paso 1
- [ ] Paso 2
```

---

## 🚄 RAILWAY DEPLOYMENT - PLATAFORMA DE PRODUCCIÓN

### ✅ ESTADO: OPERATIVO EN RAILWAY

**Fecha de Migración**: 2025-10-13
**Plataforma**: Railway (https://railway.app)
**Región**: us-west
**Status**: ✅ PRODUCCIÓN ACTIVA

### 📦 CONFIGURACIÓN RAILWAY

#### Build Configuration (`nixpacks.toml`)

```toml
[phases.setup]
nixPkgs = ["python311", "python311Packages.virtualenv"]

[phases.install]
cmds = [
  "python -m venv /opt/venv",
  ". /opt/venv/bin/activate && pip install --upgrade pip",
  ". /opt/venv/bin/activate && pip install -r requirements_production.txt"
]

[start]
cmd = ". /opt/venv/bin/activate && python scripts/create_admin_on_startup.py && uvicorn app.main_production:app --host 0.0.0.0 --port $PORT"
```

#### Requirements Production (`requirements_production.txt`)

**Optimizaciones para Railway**:
- ✅ Solo 24 packages esenciales
- ✅ Sin dependencias ML/AI (torch, chromadb, transformers)
- ✅ Tamaño: ~80MB (vs ~500MB con requirements.txt completo)
- ✅ Tiempo de instalación: ~50 segundos

**Packages Incluidos**:
- FastAPI + Uvicorn
- PostgreSQL drivers (asyncpg + psycopg2-binary)
- SQLAlchemy + Alembic
- JWT Auth (python-jose, passlib, bcrypt, cryptography)
- Redis async
- Logging (structlog, loguru)
- Communications (Twilio, Resend)
- Image processing (Pillow)
- Utils (aiofiles, jinja2, qrcode, phonenumbers)

### 🔧 VARIABLES DE ENTORNO RAILWAY

**Variables Críticas Configuradas**:

```bash
# Database
DATABASE_URL=postgresql://[connection-string]

# Environment
ENVIRONMENT=production

# CORS (Actualizado 2025-10-13)
CORS_ORIGINS=https://mestocker.com,https://www.mestocker.com,https://*.vercel.app

# JWT Secret
SECRET_KEY=[secure-token]

# Services (Opcional - si están configurados)
RESEND_API_KEY=[key]
TWILIO_ACCOUNT_SID=[sid]
TWILIO_AUTH_TOKEN=[token]
TWILIO_FROM_NUMBER=[number]
```

### 🚀 DEPLOYMENT WORKFLOW

**Auto-Deploy desde GitHub**:
1. Push a `main` branch
2. Railway detecta cambio automáticamente
3. Build con nixpacks (~2-3 minutos)
4. Deploy automático
5. Health check (`/health`)

**Timeline Típico**:
- Detección: Inmediato
- Build: 2-3 minutos
- Deploy: 30 segundos
- Total: ~3-4 minutos

### 📊 MONITOREO RAILWAY

**Dashboard Railway**:
- **Deployments**: Historial de deploys con logs
- **Metrics**: CPU, Memory, Network usage
- **Logs**: Real-time streaming logs
- **Database**: PostgreSQL metrics y backups

**Health Checks**:
```bash
# Verificar estado
curl https://mestocker-backend-production.up.railway.app/health

# Verificar API docs
curl https://mestocker-backend-production.up.railway.app/docs
```

### 🔄 ÚLTIMOS CAMBIOS (2025-10-13)

**Commit 8ffbebf5**: CORS origins actualizados
- Agregados: mestocker.com, www.mestocker.com
- Mantenidos: *.vercel.app wildcard

**Commit 1b67f9d3**: requirements_production.txt
- Agregado al repositorio
- 24 packages optimizados
- Build más rápido y ligero

### 🛠️ TROUBLESHOOTING RAILWAY

#### Error: "requirements_production.txt not found"
**Solución**: Verificar que el archivo está en el repositorio root
```bash
git add requirements_production.txt
git commit -m "feat: Add requirements_production.txt"
git push origin main
```

#### Error: Build timeout
**Causa**: Requirements muy pesados o timeouts de red
**Solución**: Usar requirements_production.txt en lugar de requirements.txt

#### Error: Database connection failed
**Causa**: DATABASE_URL no configurado o incorrecto
**Solución**: Verificar variable en Railway Dashboard → Settings → Variables

### 📝 COMANDOS RAILWAY CLI (Opcional)

```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Login
railway login

# Ver logs en tiempo real
railway logs

# Ver variables de entorno
railway variables

# Redeploy manual
railway up
```

### 🔐 SEGURIDAD RAILWAY

**Medidas Implementadas**:
- ✅ HTTPS automático con certificados SSL
- ✅ Variables de entorno encriptadas
- ✅ Network isolation
- ✅ Automatic security updates
- ✅ DDoS protection by Railway

**Variables Sensibles** (NUNCA en código):
- DATABASE_URL
- SECRET_KEY
- RESEND_API_KEY
- TWILIO credentials

### 📚 DOCUMENTACIÓN RAILWAY

**Links Útiles**:
- Dashboard: https://railway.app/dashboard
- Docs: https://docs.railway.app
- Nixpacks: https://nixpacks.com/docs

**Guía Completa**: Ver `docs/deployment/RAILWAY_DEPLOYMENT_GUIDE.md` (pendiente creación)

---

**🎉 HITO HISTÓRICO ALCANZADO**

El proyecto MeStore ha alcanzado su primer despliegue en producción exitoso en Railway. Este es un logro significativo que representa el trabajo coordinado de todo el ecosistema de agentes especializados.

**Fecha de Milestone Original**: 2025-10-05 (Render)
**Fecha de Migración Railway**: 2025-10-13
**Status**: PRODUCTION LIVE EN RAILWAY ✅
**Responsable**: cloud-infrastructure-ai
**Aprobado por**: Director Enterprise CEO