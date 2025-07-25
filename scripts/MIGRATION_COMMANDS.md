🚀 Comandos Rápidos de Migraciones
Comandos Más Usados
Development
bash# Validar y ejecutar en development
python3 scripts/run_migrations.py --env development

# Solo validar
python3 scripts/run_migrations.py --validate --env development
Production
bash# Validar antes de deployment
./scripts/deploy_migrations_python.sh --validate production

# Ejecutar migraciones
./scripts/deploy_migrations_python.sh production

# Con Docker
docker-compose --profile migrations up migrations
Emergency Rollback
bash# Ver historial
alembic history

# Rollback
./scripts/deploy_migrations_python.sh --rollback REVISION production
Troubleshooting
Error: Variables de entorno faltantes
bash# Verificar archivo .env
cat .env.production

# Verificar variables
env | grep POSTGRES_
Error: Conexión DB falló
bash# Test conexión manual
psql $DATABASE_URL

# Validar con force
python3 scripts/run_migrations.py --validate --force --env production
Error: Alembic config
bash# Verificar configuración
alembic check

# Ver estado actual
alembic current
