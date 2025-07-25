# 📚 GUÍA COMPLETA DEL MAKEFILE MESTORE

## 🎯 Introducción

Este Makefile proporciona comandos simplificados para gestión de migraciones Alembic en el proyecto MeStore. Actúa como wrapper inteligente de los scripts existentes `run_migrations.py` y `deploy_migrations_python.sh`.

## 🚀 Inicio Rápido

### Comandos Más Utilizados

```bash
# Ver ayuda completa
make help

# Aplicar migraciones pendientes
make migrate-upgrade

# Ver estado actual
make migrate-current

# Generar nueva migración
make migrate-auto MSG="Agregar tabla usuarios"

# Migraciones en producción
make migrate-prod
```

## 📋 Referencia Completa de Comandos

### 🔄 Migraciones Básicas

#### `make migrate-upgrade`
Aplica todas las migraciones pendientes en el entorno actual.

```bash
# Development (por defecto)
make migrate-upgrade

# Testing específico
ENV=testing make migrate-upgrade
```

**Equivalente manual:**
```bash
python3 scripts/run_migrations.py --env development --operation upgrade
```

#### `make migrate-downgrade`
Revierte la última migración aplicada.

```bash
make migrate-downgrade
```

**⚠️ Precaución:** Esta operación puede causar pérdida de datos.

#### `make migrate-current`
Muestra la revisión actual de la base de datos.

```bash
make migrate-current
```

#### `make migrate-history`
Muestra el historial completo de migraciones.

```bash
make migrate-history
```

#### `make migrate-check`
Verifica si hay migraciones pendientes por aplicar.

```bash
make migrate-check
```

### 🏗️ Generación de Migraciones

#### `make migrate-auto MSG="descripción"`
Genera una migración automática basada en cambios en los modelos.

```bash
# Generar migración para nuevos modelos
make migrate-auto MSG="Agregar modelo Product"

# Con cambios específicos
make migrate-auto MSG="Agregar índices a tabla users"
```

**Equivalente manual:**
```bash
alembic revision --autogenerate -m "Descripción del cambio"
```

#### `make migrate-manual MSG="descripción"`
Crea una migración manual vacía para cambios personalizados.

```bash
make migrate-manual MSG="Migración de datos específica"
```

### 🌍 Entornos Específicos

#### `make migrate-dev`
Ejecuta migraciones en entorno de desarrollo.

```bash
make migrate-dev
```

#### `make migrate-test`
Ejecuta migraciones en entorno de testing.

```bash
make migrate-test
```

#### `make migrate-prod`
Ejecuta migraciones en producción con confirmaciones de seguridad.

```bash
make migrate-prod
```

**Características especiales:**
- Solicita confirmación del usuario
- Ejecuta script de deployment especializado
- Incluye validaciones adicionales

### 🐳 Comandos Docker

#### `make migrate-docker`
Ejecuta migraciones usando Docker Compose.

```bash
make migrate-docker
```

**Equivalente manual:**
```bash
docker-compose --profile migration up migrations
```

#### `make migrate-docker-dev`
Migraciones Docker específicas para development.

```bash
make migrate-docker-dev
```

#### `make migrate-docker-rebuild`
Rebuild del contenedor y ejecución de migraciones.

```bash
make migrate-docker-rebuild
```

### 🛠️ Utilidades Avanzadas

#### `make migrate-reset`
**⚠️ PELIGROSO:** Reset completo de la base de datos.

```bash
make migrate-reset
```

- Solicita confirmación doble
- Elimina TODOS los datos
- Operación irreversible

#### `make migrate-validate`
Valida el estado actual de las migraciones.

```bash
make migrate-validate
```

#### `make db-status`
Muestra estado completo de la base de datos.

```bash
make db-status
```

**Información incluida:**
- Revisión actual
- Migraciones pendientes
- Últimas 5 migraciones aplicadas

#### `make db-init`
Inicializa la base de datos desde cero.

```bash
make db-init
```

### ⚡ Comandos Rápidos (Aliases)

```bash
make up        # = migrate-upgrade
make down      # = migrate-downgrade  
make status    # = migrate-current
make check     # = migrate-check
make auto      # = migrate-auto (requiere MSG)
```

### 🧪 Testing y Desarrollo

#### `make migrate-test-all`
Ejecuta todos los tests de migraciones.

```bash
make migrate-test-all
```

#### `make migrate-dry-run`
Simula migraciones sin ejecutarlas.

```bash
make migrate-dry-run
```

#### `make dev-setup`
Setup completo para nuevo entorno de desarrollo.

```bash
make dev-setup
```

#### `make dev-reset`
Reset y recarga completa para desarrollo.

```bash
make dev-reset
```

### 📚 Documentación y Configuración

#### `make migrate-docs`
Genera documentación automática de migraciones.

```bash
make migrate-docs
```

#### `make show-config`
Muestra configuración actual del entorno.

```bash
make show-config
```

#### `make clean-migrations`
Limpia archivos temporales de migraciones.

```bash
make clean-migrations
```

## 🔧 Variables de Entorno

### Variable ENV
Controla el entorno objetivo para las migraciones.

```bash
# Valores válidos
ENV=development  # Por defecto
ENV=testing
ENV=production

# Uso
ENV=testing make migrate-upgrade
```

### Variable DOCKER_COMPOSE_FILE
Especifica archivo docker-compose personalizado.

```bash
DOCKER_COMPOSE_FILE=docker-compose.prod.yml make migrate-docker
```

## 📊 Workflows Recomendados

### 🏗️ Desarrollo de Nueva Funcionalidad

```bash
# 1. Modificar modelos en código
# 2. Generar migración
make migrate-auto MSG="Agregar modelo Usuario"

# 3. Revisar migración generada
cat alembic/versions/XXX_agregar_modelo_usuario.py

# 4. Aplicar migración
make migrate-upgrade

# 5. Verificar estado
make migrate-current
```

### 🧪 Testing

```bash
# 1. Setup entorno de testing
ENV=testing make dev-setup

# 2. Ejecutar migraciones de testing
make migrate-test

# 3. Ejecutar tests
make migrate-test-all

# 4. Limpiar después
ENV=testing make migrate-reset
```

### 🚀 Deployment a Producción

```bash
# 1. Verificar estado en development
make migrate-check

# 2. Crear backup (manual)
# pg_dump mestocker_prod > backup_pre_migration.sql

# 3. Ejecutar migraciones en producción
make migrate-prod

# 4. Verificar resultado
ENV=production make migrate-current
```

### 🐳 Workflow Docker

```bash
# 1. Desarrollo local con Docker
make migrate-docker-dev

# 2. Testing en Docker
ENVIRONMENT=testing make migrate-docker

# 3. Production deployment
make migrate-docker-rebuild
```

## ⚠️ Consideraciones de Seguridad

### Comandos Destructivos
Estos comandos pueden causar pérdida de datos:

- `make migrate-reset` - Elimina toda la base de datos
- `make migrate-downgrade` - Puede revertir cambios importantes
- `make dev-reset` - Reset completo de desarrollo

### Producción
- Siempre crear backup antes de `make migrate-prod`
- Verificar migraciones en staging primero
- Usar `make migrate-dry-run` para previsualiazar

### Docker
- Verificar variables de entorno antes de ejecutar
- Asegurar que volúmenes están correctamente configurados

## 🔍 Troubleshooting

### Error: "Makefile not found"
```bash
# Verificar ubicación actual
pwd
ls -la Makefile

# Ejecutar desde directorio raíz del proyecto
cd /path/to/MeStore
make help
```

### Error: "Target not found"
```bash
# Ver todos los targets disponibles
make help

# Verificar sintaxis del comando
make migrate-upgrade  # Correcto
make migrate_upgrade  # Incorrecto (underscore)
```

### Error: "Script not found"
```bash
# Verificar scripts existen
ls -la scripts/run_migrations.py
ls -la scripts/deploy_migrations_python.sh

# Verificar permisos de ejecución
chmod +x scripts/*.py scripts/*.sh
```

### Error: "Database connection failed"
```bash
# Verificar variables de entorno
make show-config

# Verificar archivos .env
ls -la .env*

# Test conexión directa
python3 scripts/run_migrations.py --env development --validate
```

### Error: "Alembic command failed"
```bash
# Verificar configuración Alembic
cat alembic.ini

# Test comando alembic directo
alembic current

# Verificar historial
alembic history
```

## 📈 Mejores Prácticas

### 1. **Siempre usar mensajes descriptivos**
```bash
# ✅ Bueno
make migrate-auto MSG="Agregar índice email único a tabla users"

# ❌ Malo
make migrate-auto MSG="cambios"
```

### 2. **Verificar antes de aplicar**
```bash
# Verificar estado actual
make migrate-current

# Verificar migraciones pendientes
make migrate-check

# Aplicar migraciones
make migrate-upgrade
```

### 3. **Usar entornos específicos**
```bash
# Desarrollo
make migrate-dev

# Testing explícito
ENV=testing make migrate-upgrade

# Producción con cuidado
make migrate-prod
```

### 4. **Documentar cambios importantes**
```bash
# Generar documentación después de cambios
make migrate-docs

# Verificar historial
make migrate-history
```

## 🤝 Integración con Workflow Existente

### Scripts Preservados
El Makefile **NO reemplaza** los scripts existentes:

- `scripts/run_migrations.py` - Sigue funcionando independientemente
- `scripts/deploy_migrations_python.sh` - Usado por `make migrate-prod`
- Comandos `alembic` directos - Siguen disponibles

### Compatibilidad
```bash
# Estas formas siguen funcionando:
python3 scripts/run_migrations.py --help
alembic current
docker-compose up migrations

# Y ahora también:
make migrate-current
make migrate-docker
make help
```

## 📞 Soporte

Para problemas específicos:

1. **Ver ayuda completa:** `make help` y `make migrate-help`
2. **Verificar configuración:** `make show-config`
3. **Ejecutar tests:** `make migrate-test-all`
4. **Estado de la DB:** `make db-status`

---

**Versión:** 1.0.0  
**Última actualización:** 2025-07-25  
**Proyecto:** MeStore - Sistema de Gestión de Inventario
