# Guía de Deployment con Migraciones - MeStore

## Descripción General

Esta guía documenta el sistema de deployment automático con migraciones para MeStore, incluyendo scripts, configuración Docker y procedimientos de rollback.

## Scripts Principales

### 1. `scripts/run_migrations.sh`
Script principal para ejecutar migraciones durante deployment.

**Uso:**
```bash
# Ejecutar migraciones en development
./scripts/run_migrations.sh development

# Dry-run para ver migraciones pendientes
./scripts/run_migrations.sh --dry-run production

# Forzar ejecución sin confirmación
./scripts/run_migrations.sh --force staging

# Con backup automático
./scripts/run_migrations.sh --backup production
Características:

Auto-detección de environment
Validación de conectividad DB
Backup automático en producción
Logging detallado
Confirmación interactiva

2. scripts/deploy_with_migrations.sh
Script completo de deployment con secuencia completa.
Uso:
bash# Deployment completo
./scripts/deploy_with_migrations.sh production

# Solo health check
./scripts/deploy_with_migrations.sh --check-only production

# Rollback de emergencia
./scripts/deploy_with_migrations.sh --rollback abc123 production

# Deployment sin backup
./scripts/deploy_with_migrations.sh --skip-backup development
Secuencia de Deployment:

Health check inicial del sistema
Backup de base de datos (si aplica)
Ejecución de migraciones
Validación post-migración
Restart de aplicación (Docker)
Health check final

Integración con Docker
Servicio de Migración
bash# Ejecutar solo migraciones
docker-compose --profile migration up migrations

# Deployment completo con migraciones
docker-compose --profile migration up -d
Configuración del Servicio

Container: mestocker_migrations
Profile: migration
Dependencias: postgres (healthy), redis (healthy)
Comando: Ejecuta run_migrations.sh --force

Environments Soportados
Development

Validaciones relajadas
Backup opcional
Warnings en lugar de errores críticos
Confirmación interactiva opcional

Staging/Testing

Validaciones moderadas
Backup recomendado
Logging detallado
Confirmación interactiva

Production

Validaciones estrictas
Backup obligatorio
Doble confirmación requerida
Aplicación no inicia si hay migraciones pendientes

Validación de Migraciones en Startup
La aplicación FastAPI incluye validación automática de migraciones:
python# En app/main.py
async def validate_migrations_on_startup():
    # Validar que DB está en la revisión más reciente
    # En producción: error crítico si hay migraciones pendientes
    # En development: warning solamente
Procedimientos de Rollback
Rollback Automático
bash# Rollback de emergencia
./scripts/deploy_with_migrations.sh --rollback <revision> production

# Usando alembic_helpers.sh
source scripts/alembic_helpers.sh
emergency_rollback production <revision>
Rollback Manual
bash# Downgrade a revisión específica
alembic -x env=production downgrade <revision>

# Restaurar desde backup
psql $DATABASE_URL < backups/db_backup_YYYYMMDD_HHMMSS.sql
Logging y Monitoreo
Archivos de Log

Migraciones: logs/migration_deploy_YYYYMMDD_HHMMSS.log
Deployment: logs/full_deploy_YYYYMMDD_HHMMSS.log
Aplicación: logs/mestocker-{environment}.log

Health Checks
bash# Health check de DB
curl http://localhost:8000/health
curl http://localhost:8000/ready

# Health check manual
source scripts/alembic_helpers.sh
health_check_database development
Variables de Entorno Requeridas
bash# .env (development)
ENVIRONMENT=development
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/db

# .env.production
ENVIRONMENT=production
DATABASE_URL=postgresql+asyncpg://user:pass@prod-host:5432/db
Comandos de Verificación
Pre-Deployment
bash# Verificar scripts
bash -n scripts/run_migrations.sh
bash -n scripts/deploy_with_migrations.sh

# Verificar configuración Docker
docker-compose config

# Test de conectividad
./scripts/run_migrations.sh --dry-run development
Post-Deployment
bash# Verificar estado de migraciones
alembic -x env=production current
alembic -x env=production history --indicate-current

# Health check completo
./scripts/deploy_with_migrations.sh --check-only production
Troubleshooting
Problemas Comunes

"No se puede conectar a la base de datos"

Verificar DATABASE_URL
Verificar que PostgreSQL está corriendo
Verificar credenciales


"Migraciones pendientes en producción"

Ejecutar deployment script completo
Verificar que todas las migraciones están aplicadas


"Error durante rollback"

Verificar que la revisión objetivo existe
Usar backup manual si es necesario



Debug Mode
bash# Ejecutar con debug detallado
bash -x scripts/run_migrations.sh development

# Ver logs en tiempo real
tail -f logs/migration_deploy_*.log
Testing
Ejecutar Tests
bash# Tests de scripts de deployment
python -m pytest tests/scripts/test_migration_deploy.py -v

# Test específico
python -m pytest tests/scripts/test_migration_deploy.py::TestMigrationDeployScripts::test_run_migrations_help -v
Tests Automatizados

Existencia y permisos de scripts
Sintaxis bash válida
Comandos --help funcionales
Configuración Docker correcta
Integración con alembic_helpers.sh

Mejores Prácticas

Siempre usar dry-run en producción antes del deployment real
Verificar backups antes de migraciones críticas
Monitorear logs durante deployment
Tener plan de rollback preparado
Validar en staging antes de producción

Próximos Pasos

Integración con CI/CD pipelines
Métricas de deployment automatizadas
Notificaciones de Slack/email
Blue-green deployment support
