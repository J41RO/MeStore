# 📋 GUÍA: ALEMBIC MULTI-ENVIRONMENT

## 🎯 Descripción
Sistema de configuración multi-environment para Alembic que permite ejecutar migraciones en diferentes entornos (development, testing, production) con configuraciones específicas.

## 📂 Archivos Configurados

### 1. `alembic.ini`
- Sections específicas: `[alembic:development]`, `[alembic:testing]`, `[alembic:production]`
- Configuración de logging por environment
- URL de database con expansion de variables

### 2. `alembic/env.py`
- Función `get_environment_config()` para detectar environment actual
- Fallback automático a settings Pydantic para compatibilidad
- Soporte para expansion de variables de entorno

### 3. `scripts/alembic_helpers.sh`
- Helpers para facilitar uso: `alembic-dev`, `alembic-test`, `alembic-prod`
- Verificación de configuración: `alembic-check`
- Status de todos los environments: `alembic-status`

### 4. Archivos `.env.*`
- `.env`: ENVIRONMENT=development, DATABASE_URL para dev
- `.env.test`: ENVIRONMENT=development (para testing), DATABASE_URL para test
- `.env.production`: ENVIRONMENT=production, DATABASE_URL para prod

## 🚀 Uso

### Comandos Básicos
```bash
# Cargar helpers
source scripts/alembic_helpers.sh

# Ver revision actual por environment
alembic-dev current
alembic-test current
alembic-prod current

# Crear migration
alembic-dev revision --autogenerate -m "Add new field"

# Ejecutar migrations
alembic-dev upgrade head
alembic-test upgrade head
alembic-prod upgrade head  # Con confirmación de seguridad
Comandos Manuales
bash# Usar environment específico
ENVIRONMENT=development alembic current
ENVIRONMENT=testing alembic upgrade head
ENVIRONMENT=production alembic history
Comandos de Utilidad
bash# Verificar configuración
alembic-check

# Ver status de todos los environments
alembic-status

# Ver ayuda
alembic-help
⚙️ Configuración
Variables de Entorno
bash# Development (.env)
ENVIRONMENT=development
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/db_dev

# Testing (.env.test)
ENVIRONMENT=development  # Uses testing DB URL
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/db_test

# Production (.env.production)
ENVIRONMENT=production
DATABASE_URL=postgresql+asyncpg://user:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}
DB_HOST=localhost
DB_PORT=5432
DB_NAME=mestocker_prod
DB_PASSWORD=production_secure_password_change_me
Sections en alembic.ini
ini[alembic:development]
sqlalchemy.url = ${DATABASE_URL}
sqlalchemy.echo = true

[alembic:testing]
sqlalchemy.url = ${DATABASE_URL}
sqlalchemy.echo = false
sqlalchemy.poolclass = NullPool

[alembic:production]
sqlalchemy.url = ${DATABASE_URL}
sqlalchemy.echo = false
sqlalchemy.poolclass = QueuePool
🔧 Troubleshooting
Error: Section not found

Verificar que alembic.ini tiene las sections correctas
Ejecutar alembic-check para diagnóstico

Error: DATABASE_URL expansion

Verificar que variables de entorno están definidas
Variables en formato ${VAR_NAME} se expanden automáticamente

Error: Pool configuration

Testing usa NullPool para evitar problemas de concurrencia
Production usa QueuePool con configuración optimizada

✅ Testing
Tests Unitarios
bashpytest tests/migrations/test_environments.py -v
Verificación Manual
bash# Verificar detección de environment
python3 -c "
import os
os.environ['ENVIRONMENT'] = 'development'
# Test import
import sys; sys.path.append('alembic')
from env import get_environment_config
print(get_environment_config())
"
📊 Beneficios

Separación de Environments: Cada entorno usa su propia configuración
Seguridad: Confirmación requerida para operaciones en production
Flexibilidad: Fallback automático a settings Pydantic
Conveniencia: Helpers para uso rápido
Monitoreo: Status de migrations en todos los environments
Expansión de Variables: Soporte para variables de entorno en URLs

🎯 Próximos Pasos

Configurar CI/CD para ejecutar migrations automáticamente
Implementar backup automático antes de migrations en production
Agregar logging de migrations a sistema de observabilidad
