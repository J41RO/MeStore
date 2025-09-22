# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

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
Responsable: agente-que-aprobó (si aplica)
```

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