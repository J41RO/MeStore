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