# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Architecture

MeStore is a comprehensive marketplace e-commerce system built with FastAPI backend and React frontend, designed for multi-vendor operations with integrated fulfillment and commission systems.

### High-Level Architecture

- **Backend**: FastAPI + SQLAlchemy + PostgreSQL/SQLite (async)
- **Frontend**: React 18 + TypeScript + Vite + Tailwind CSS
- **State Management**: Zustand for React state
- **Database**: PostgreSQL (production) / SQLite (development)
- **Migrations**: Alembic with multi-environment support
- **Authentication**: JWT with role-based access control (Admin, Vendor, Buyer)
- **Payment**: Wompi integration for Colombian market
- **Caching**: Redis for sessions and rate limiting
- **Testing**: Pytest (backend) + Jest/Vitest (frontend)

### Core Business Domains

1. **User Management**: Multi-role system (Admin, Vendor, Buyer) with JWT authentication
2. **Product Management**: Vendor product catalog with inventory tracking
3. **Order System**: Complete order lifecycle with status tracking
4. **Commission System**: Automated vendor commission calculation and tracking
5. **Payment Processing**: Wompi payment gateway integration
6. **Audit & Security**: Comprehensive logging, rate limiting, and fraud detection

## Development Commands

### Backend (Python/FastAPI)

```bash
# Environment setup
source .venv/bin/activate  # or: python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Testing
python -m pytest                    # All tests
python -m pytest tests/unit/        # Unit tests only
python -m pytest tests/integration/ # Integration tests only
python -m pytest -v --tb=short      # Verbose with short traceback
python -m pytest --cov=app          # With coverage

# Code quality
black .                             # Format code
flake8                             # Lint code
isort .                            # Sort imports
```

### Frontend (React/TypeScript)

```bash
cd frontend

# Development server
npm run dev                         # Start dev server (localhost:5173)
npm run dev:network                # Start dev server accessible on network

# Building
npm run build                      # Production build
npm run preview                    # Preview production build

# Testing
npm test                           # Run Jest tests
npm run test:watch                 # Watch mode
npm run test:coverage              # With coverage
npm run test:ci                    # CI mode

# Code quality
npm run lint                       # ESLint
npm run lint --fix                 # ESLint with auto-fix
npm run format                     # Prettier format
npm run format:check               # Check formatting
```

### Database Migrations

The project uses Alembic with a comprehensive Makefile system for database migrations:

```bash
# Basic migration commands
make migrate-upgrade               # Apply pending migrations
make migrate-current              # Show current revision
make migrate-history              # Show migration history
make migrate-check                # Check for pending migrations

# Create new migrations
make migrate-auto MSG="Add user table"     # Auto-generate migration
make migrate-manual MSG="Custom change"    # Create empty migration

# Environment-specific
make migrate-dev                  # Development environment
make migrate-prod                 # Production environment (with confirmations)
make migrate-test                 # Testing environment

# Utilities
make migrate-validate             # Validate migration state
make db-status                   # Complete database status
make migrate-help                 # Detailed migration help

# Alternative: Direct Python script
python3 scripts/run_migrations.py --env development
python3 scripts/run_migrations.py --env production --validate
```

## Key File Locations and Patterns

### Backend Structure
```
app/
├── main.py                    # FastAPI application entry point
├── core/                      # Core configuration and security
│   ├── config.py             # Environment configuration
│   ├── security.py           # JWT and password handling
│   └── redis/                # Redis configuration and sessions
├── models/                    # SQLAlchemy models
│   ├── user.py               # User model with roles
│   ├── product.py            # Product and inventory models
│   ├── order.py              # Order and transaction models
│   └── commission.py         # Commission tracking
├── api/v1/                   # API endpoints
│   ├── deps/                 # Dependencies (auth, database)
│   └── endpoints/            # Route handlers
├── services/                 # Business logic layer
├── schemas/                  # Pydantic schemas for validation
└── middleware/               # Custom middleware (security, logging)
```

### Frontend Structure
```
frontend/src/
├── components/               # Reusable UI components
│   ├── buyer/               # Buyer-specific components
│   ├── vendor/              # Vendor-specific components
│   └── orders/              # Order management components
├── pages/                   # Route pages
├── hooks/                   # Custom React hooks
├── services/                # API service functions
├── config/                  # Configuration and constants
└── utils/                   # Utility functions
```

### Configuration Files
- `.env` - Environment variables (development defaults)
- `alembic.ini` - Database migration configuration with multi-environment support
- `requirements.txt` - Python dependencies
- `frontend/package.json` - Node.js dependencies and scripts

## Testing Strategies

### Backend Testing
- **Unit Tests**: Located in `tests/unit/` - Test individual functions and classes
- **Integration Tests**: Located in `tests/integration/` - Test API endpoints and database operations
- **Fixtures**: Located in `tests/fixtures/` - Shared test data and setup
- **Test Configuration**: Uses separate test database with automatic cleanup

### Frontend Testing
- **Component Tests**: Jest + React Testing Library for component testing
- **E2E Tests**: Vitest for responsive design testing
- **Coverage**: Configured to exclude build artifacts and focus on source code

## Development Workflow

### Authentication Testing
Use these test credentials for development:
```
Admin: admin@test.com / admin123
Vendor: vendor@test.com / vendor123
Buyer: buyer@test.com / buyer123
```

### Database Management
- Development uses SQLite (`mestore_production.db`)
- Migrations are tracked in `alembic/versions/`
- Use the Makefile commands for consistent migration management
- Always validate migrations in development before production deployment

### Code Style
- **Backend**: Black for formatting, isort for imports, flake8 for linting
- **Frontend**: Prettier for formatting, ESLint for linting
- **Naming Conventions**:
  - Backend: snake_case for files/functions, PascalCase for classes
  - Frontend: PascalCase for components, camelCase for functions/variables

### Environment Management
- Use `.env` for local development configuration
- Never commit secrets or production credentials
- Database URLs and API keys are environment-specific
- Redis is used for caching and sessions in production

## Important Notes

- The project includes comprehensive audit logging for admin actions
- Rate limiting is implemented to prevent abuse
- All API endpoints require authentication except public routes
- Commission calculations are automated based on configurable rates
- The system supports multi-vendor operations with separate vendor dashboards
- Frontend uses centralized imports from index.ts files for better organization
- Alembic migrations support multiple environments (development, testing, production)