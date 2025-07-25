# MeStore

## 🛒 Sistema de Marketplace y E-commerce

MeStore es un sistema completo de marketplace que permite a usuarios vender y comprar productos de manera eficiente y segura.

## 📁 Estructura del Proyecto

### Backend (Python/FastAPI)
```
app/
├── models/          # Modelos de datos y entidades
│   ├── __init__.py
│   ├── base.py      # BaseModel para herencia común
│   └── user.py      # Modelo de usuario
├── services/        # Lógica de negocio y servicios
│   └── __init__.py
├── api/            # Endpoints y controladores API
│   ├── __init__.py
│   └── v1/         # Versión 1 de la API
│       └── __init__.py
├── schemas/        # Schemas Pydantic para validación
│   ├── __init__.py
│   └── user.py     # Schemas de usuario
└── main.py         # Aplicación FastAPI principal

tests/              # Tests automatizados
└── __init__.py
```

### Frontend (React/TypeScript)
```
frontend/src/
├── components/     # Componentes reutilizables UI
│   ├── index.ts    # Exportación centralizada
│   └── .gitkeep
├── pages/          # Páginas principales de la app
│   └── .gitkeep
├── hooks/          # Custom hooks de React
│   ├── index.ts    # Exportación centralizada
│   └── .gitkeep
├── utils/          # Utilidades y helpers
│   ├── index.ts    # Exportación centralizada
│   └── .gitkeep
├── App.tsx         # Componente principal
└── main.tsx        # Punto de entrada
```

## 🎯 Convenciones de Naming

### Backend
- **Archivos**: snake_case (user_model.py, product_service.py)
- **Clases**: PascalCase (UserModel, ProductService)
- **Funciones/Variables**: snake_case (get_user, total_price)

### Frontend
- **Componentes**: PascalCase (UserCard.tsx, ProductList.tsx)
- **Hooks**: camelCase con 'use' prefix (useAuth.ts, useProducts.ts)
- **Utils**: camelCase (formatPrice.ts, validateEmail.ts)
- **Páginas**: PascalCase (HomePage.tsx, ProductPage.tsx)

## 🚀 Imports Centralizados

### Frontend
```typescript
// ✅ BIEN: Import centralizado
import { Header, ProductCard } from '@/components'
import { useAuth, useCart } from '@/hooks'
import { formatPrice, apiClient } from '@/utils'

// ❌ MAL: Imports individuales
import { Header } from '@/components/Header'
import { ProductCard } from '@/components/ProductCard'
```

### Backend
```python
# ✅ BIEN: Import desde módulos organizados
from app.models.user import User
from app.services.auth import AuthService
from app.api.v1.users import users_router
```

## 🛠️ Tecnologías

### Backend
- **Python 3.11+** - Lenguaje principal
- **FastAPI** - Framework web moderno
- **Pydantic** - Validación de datos
- **SQLAlchemy** - ORM para base de datos
- **PostgreSQL** - Base de datos principal

### Frontend
- **React 18** - Framework UI
- **TypeScript** - Tipado estático
- **Vite** - Build tool y dev server
- **Tailwind CSS** - Framework CSS
- **ESLint + Prettier** - Calidad de código

## 🚀 Desarrollo

## 🐳 Desarrollo con Docker

### Prerequisitos
- Docker 20.10+
- Docker Compose 2.0+

### Comandos Rápidos

#### Iniciar entorno completo
```bash
# Iniciar todos los servicios
./scripts/dev.sh start

# O manualmente
docker-compose up -d
```

#### Acceso a servicios
- **Backend API**: http://localhost:8000
- **Documentación API**: http://localhost:8000/docs
- **Frontend**: http://localhost:5173
- **Base de datos**: localhost:5432
- **Redis**: localhost:6379

#### Comandos útiles
```bash
# Ver logs
./scripts/dev.sh logs

# Rebuild containers
./scripts/dev.sh build

# Shell en backend
./scripts/dev.sh shell-be

# Shell en base de datos
./scripts/dev.sh shell-db

# Ejecutar tests
./scripts/dev.sh test

# Limpiar todo
./scripts/dev.sh clean
```

### Estructura de Containers

```
Services:
├── backend (FastAPI)    → :8000
├── frontend (React)     → :5173  
├── db (PostgreSQL)      → :5432
├── redis (Cache)        → :6379
└── nginx (Proxy)        → :80 [opcional]
```

### Variables de Entorno

Copiar `.env.template` a `.env` y personalizar:

```bash
cp .env.template .env
# Editar .env con tus configuraciones
```

## 🐳 Desarrollo con Docker

### Prerequisitos
- Docker 20.10+
- Docker Compose 2.0+

### Comandos Rápidos

#### Iniciar entorno completo
```bash
# Iniciar todos los servicios
./scripts/dev.sh start

# O manualmente
docker-compose up -d
```

#### Acceso a servicios
- **Backend API**: http://localhost:8000
- **Documentación API**: http://localhost:8000/docs
- **Frontend**: http://localhost:5173
- **Base de datos**: localhost:5432
- **Redis**: localhost:6379

#### Comandos útiles
```bash
# Ver logs
./scripts/dev.sh logs

# Rebuild containers
./scripts/dev.sh build

# Shell en backend
./scripts/dev.sh shell-be

# Shell en base de datos
./scripts/dev.sh shell-db

# Ejecutar tests
./scripts/dev.sh test

# Limpiar todo
./scripts/dev.sh clean
```

### Estructura de Containers

```
Services:
├── backend (FastAPI)    → :8000
├── frontend (React)     → :5173  
├── db (PostgreSQL)      → :5432
├── redis (Cache)        → :6379
└── nginx (Proxy)        → :80 [opcional]
```

### Variables de Entorno

Copiar `.env.template` a `.env` y personalizar:

```bash
cp .env.template .env
# Editar .env con tus configuraciones
```


### Backend
```bash
# Activar entorno virtual
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor de desarrollo
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend

# Instalar dependencias
npm install

# Ejecutar servidor de desarrollo
npm run dev
```

## 📋 Estado del Proyecto

- ✅ Setup Python con FastAPI
- ✅ Setup Frontend con React + TypeScript
- ✅ Estructura modular backend/frontend
- 🔄 En desarrollo: Sistema de autenticación JWT
## 🗄️ Sistema de Migraciones


## 🔧 Comandos Make para Migraciones

MeStore incluye un **Makefile completo** que simplifica todos los comandos de migraciones. Los comandos make actúan como wrapper inteligente de los scripts existentes.

### 🚀 Comandos Rápidos

```bash
# Ver ayuda completa de comandos
make help

# Aplicar migraciones pendientes
make migrate-upgrade

# Ver estado actual de la base de datos
make migrate-current

# Generar nueva migración automática
make migrate-auto MSG="Agregar tabla productos"

# Ejecutar migraciones en producción (con confirmaciones)
make migrate-prod

# Migraciones usando Docker
make migrate-docker
```

### 📋 Categorías de Comandos

- **🔄 Básicos**: `migrate-upgrade`, `migrate-downgrade`, `migrate-current`, `migrate-history`, `migrate-check`
- **🏗️ Generación**: `migrate-auto`, `migrate-manual` (requieren `MSG="descripción"`)
- **🌍 Entornos**: `migrate-dev`, `migrate-test`, `migrate-prod`
- **🐳 Docker**: `migrate-docker`, `migrate-docker-dev`, `migrate-docker-rebuild`
- **🛠️ Utilidades**: `migrate-reset`, `migrate-validate`, `db-status`, `db-init`
- **⚡ Aliases**: `up`, `down`, `status`, `check`, `auto`

### 📚 Documentación Completa

**Ver guía detallada**: [scripts/MAKEFILE_USAGE.md](scripts/MAKEFILE_USAGE.md)

**Ayuda específica de migraciones**:
```bash
make migrate-help
```

### 🔗 Integración con Scripts Existentes

Los comandos make **no reemplazan** los scripts originales - los utilizan internamente:
- `scripts/run_migrations.py` - Script principal (sigue funcionando independientemente)
- `scripts/deploy_migrations_python.sh` - Usado por `make migrate-prod`
- Comandos `alembic` directos - Totalmente compatibles

### Scripts Disponibles

#### 1. Script Python Principal (`scripts/run_migrations.py`)
Script robusto con validación completa y logging estructurado.

```bash
# Validar sistema sin ejecutar migraciones
python3 scripts/run_migrations.py --validate --env production

# Ejecutar migraciones en development
python3 scripts/run_migrations.py --env development

# Modo dry-run (simulación)
python3 scripts/run_migrations.py --dry-run --env production

# Rollback a revisión específica
python3 scripts/run_migrations.py --rollback abc123def456 --env production

# Forzar ejecución sin validaciones (uso con precaución)
python3 scripts/run_migrations.py --force --env production
2. Wrapper Bash (scripts/deploy_migrations_python.sh)
Interfaz simplificada para integración con scripts de deployment.
bash# Validar sistema
./scripts/deploy_migrations_python.sh --validate production

# Ejecutar migraciones
./scripts/deploy_migrations_python.sh production

# Dry-run
./scripts/deploy_migrations_python.sh --dry-run production

# Rollback
./scripts/deploy_migrations_python.sh --rollback abc123def456 production
3. Docker Compose Integration
Ejecutar migraciones usando Docker Compose con profile específico.
bash# Validar migraciones
docker-compose --profile migrations up migrations

# Ejecutar migraciones en producción
docker-compose --profile migrations run --rm migrations \
  python3 scripts/run_migrations.py --env production

# Rollback usando Docker
docker-compose --profile migrations run --rm migrations \
  python3 scripts/run_migrations.py --rollback abc123def456 --env production
Variables de Entorno Requeridas
bash# Base de datos
DATABASE_URL=postgresql://user:password@host:port/database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=mestore
POSTGRES_USER=mestore_user
POSTGRES_PASSWORD=secure_password

# Entorno (opcional, default: development)
ENVIRONMENT=production
Archivos de Configuración

.env - Configuración de development (default)
.env.production - Configuración de producción
.env.test - Configuración de testing

Logging
Los logs se guardan automáticamente en:

logs/migration_python_YYYYMMDD_HHMMSS.log - Logs del script Python
logs/migration_deploy_YYYYMMDD_HHMMSS.log - Logs del script bash

Ejemplos de Uso en Deployment
Deployment Básico
bash# 1. Validar sistema
./scripts/deploy_migrations_python.sh --validate production

# 2. Ejecutar migraciones
./scripts/deploy_migrations_python.sh production

# 3. Verificar estado
alembic current
Deployment con Docker
bash# 1. Build y preparación
docker-compose build

# 2. Ejecutar migraciones
docker-compose --profile migrations up migrations

# 3. Iniciar servicios principales
docker-compose up -d backend frontend
Rollback de Emergencia
bash# Obtener lista de revisiones
alembic history

# Rollback a revisión específica
./scripts/deploy_migrations_python.sh --rollback abc123def456 production

# Verificar rollback
alembic current
Testing del Sistema de Migraciones
bash# Ejecutar tests del script
python3 -m pytest tests/test_migrations_script.py -v

# Verificar cobertura
python3 -m pytest --cov=scripts tests/test_migrations_script.py --cov-report=term-missing

# Test de integración con Docker
docker-compose --profile migrations run --rm migrations \
  python3 scripts/run_migrations.py --validate --env test