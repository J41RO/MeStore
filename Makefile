# ==============================================================================
# MESTORE - MAKEFILE PARA GESTION DE MIGRACIONES
# ==============================================================================
# Comandos simplificados para gestion de migraciones Alembic
# Integra con scripts existentes: run_migrations.py, deploy_migrations_python.sh
# ==============================================================================

.PHONY: help migrate-help migrate-upgrade migrate-downgrade migrate-current migrate-history migrate-check
.PHONY: migrate-auto migrate-manual migrate-dev migrate-test migrate-prod migrate-docker migrate-docker-dev
.PHONY: migrate-reset migrate-validate db-status db-init clean-migrations up down status check auto

# Configuracion de colores para output
CYAN := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
NC := \033[0m

# Variables de entorno por defecto
ENV ?= development
DOCKER_COMPOSE_FILE ?= docker-compose.yml

# ==============================================================================
# HELP Y DOCUMENTACION
# ==============================================================================

help: ## Mostrar ayuda general
	@echo ""
	@echo "$(CYAN)=== MESTORE MAKEFILE - COMANDOS DISPONIBLES ===$(NC)"
	@echo ""
	@echo "$(GREEN)AYUDA Y DOCUMENTACION:$(NC)"
	@echo "  $(CYAN)help$(NC)                 Mostrar esta ayuda"
	@echo "  $(CYAN)migrate-help$(NC)         Ayuda especifica de migraciones"
	@echo ""
	@echo "$(GREEN)MIGRACIONES BASICAS:$(NC)"
	@echo "  $(CYAN)migrate-upgrade$(NC)      Aplicar migraciones pendientes"
	@echo "  $(CYAN)migrate-downgrade$(NC)    Revertir ultima migracion"
	@echo "  $(CYAN)migrate-current$(NC)      Mostrar revision actual"
	@echo "  $(CYAN)migrate-history$(NC)      Mostrar historial completo"
	@echo "  $(CYAN)migrate-check$(NC)        Verificar migraciones pendientes"
	@echo ""
	@echo "$(GREEN)GENERACION DE MIGRACIONES:$(NC)"
	@echo "  $(CYAN)migrate-auto$(NC)         Generar migracion automatica (usar: MSG='descripcion')"
	@echo "  $(CYAN)migrate-manual$(NC)       Crear migracion manual vacia (usar: MSG='descripcion')"
	@echo ""
	@echo "$(GREEN)ENTORNOS ESPECIFICOS:$(NC)"
	@echo "  $(CYAN)migrate-dev$(NC)          Migraciones en development"
	@echo "  $(CYAN)migrate-test$(NC)         Migraciones en testing"
	@echo "  $(CYAN)migrate-prod$(NC)         Migraciones en production"
	@echo ""
	@echo "$(GREEN)DOCKER:$(NC)"
	@echo "  $(CYAN)migrate-docker$(NC)       Ejecutar migraciones en Docker"
	@echo "  $(CYAN)migrate-docker-dev$(NC)   Migraciones Docker development"
	@echo ""
	@echo "$(GREEN)UTILIDADES:$(NC)"
	@echo "  $(CYAN)migrate-reset$(NC)        Reset completo de DB (PELIGROSO)"
	@echo "  $(CYAN)migrate-validate$(NC)     Validar estado de migraciones"
	@echo "  $(CYAN)db-status$(NC)           Estado completo de la base de datos"
	@echo ""
	@echo "$(GREEN)ALIASES RAPIDOS:$(NC)"
	@echo "  $(CYAN)up$(NC)                   = migrate-upgrade"
	@echo "  $(CYAN)down$(NC)                 = migrate-downgrade"
	@echo "  $(CYAN)status$(NC)               = migrate-current"
	@echo "  $(CYAN)check$(NC)                = migrate-check"
	@echo ""
	@echo "$(YELLOW)Ejemplos de uso:$(NC)"
	@echo "  make migrate-upgrade          # Actualizar a ultima migracion"
	@echo "  make migrate-auto MSG='...'   # Generar migracion automatica"
	@echo "  make migrate-prod             # Migraciones en produccion"
	@echo "  make migrate-docker-dev       # Migraciones en Docker development"
	@echo ""

migrate-help: ## Ayuda especifica de migraciones
	@echo ""
	@echo "$(CYAN)=== GUIA COMPLETA DE MIGRACIONES MESTORE ===$(NC)"
	@echo ""
	@echo "$(GREEN)COMANDOS BASICOS:$(NC)"
	@echo "  make migrate-upgrade     - Aplicar todas las migraciones pendientes"
	@echo "  make migrate-downgrade   - Revertir ultima migracion"
	@echo "  make migrate-current     - Mostrar revision actual de DB"
	@echo "  make migrate-history     - Historial completo de migraciones"
	@echo "  make migrate-check       - Verificar migraciones pendientes"
	@echo ""
	@echo "$(GREEN)CREAR MIGRACIONES:$(NC)"
	@echo "  make migrate-auto MSG='descripcion'    - Generar migracion automatica"
	@echo "  make migrate-manual MSG='descripcion'  - Crear migracion manual vacia"
	@echo ""
	@echo "$(GREEN)ENTORNOS:$(NC)"
	@echo "  make migrate-dev         - Migraciones en development (por defecto)"
	@echo "  make migrate-test        - Migraciones en testing"
	@echo "  make migrate-prod        - Migraciones en production"
	@echo ""
	@echo "$(GREEN)DOCKER:$(NC)"
	@echo "  make migrate-docker      - Ejecutar migraciones en contenedor"
	@echo "  make migrate-docker-dev  - Migraciones Docker development"
	@echo ""
	@echo "$(GREEN)UTILIDADES:$(NC)"
	@echo "  make migrate-reset       - Reset completo de database"
	@echo "  make migrate-validate    - Validar estado de migraciones"
	@echo "  make db-status          - Estado completo de la base de datos"
	@echo ""
	@echo "$(YELLOW)Archivos importantes:$(NC)"
	@echo "  scripts/run_migrations.py        - Script principal de migraciones"
	@echo "  scripts/deploy_migrations_python.sh - Script de deployment"
	@echo "  alembic.ini                      - Configuracion Alembic"
	@echo "  alembic/versions/                - Archivos de migracion"
	@echo ""

# ==============================================================================
# COMANDOS BASICOS DE MIGRACIONES
# ==============================================================================

migrate-upgrade: ## Aplicar todas las migraciones pendientes
	@echo "$(CYAN)Aplicando migraciones pendientes...$(NC)"
	@python3 scripts/run_migrations.py --env $(ENV) --operation upgrade
	@echo "$(GREEN)Migraciones aplicadas exitosamente$(NC)"

migrate-downgrade: ## Revertir ultima migracion
	@echo "$(YELLOW)Revirtiendo ultima migracion...$(NC)"
	@python3 scripts/run_migrations.py --env $(ENV) --operation downgrade --revision -1
	@echo "$(GREEN)Migracion revertida exitosamente$(NC)"

migrate-current: ## Mostrar revision actual de la base de datos
	@echo "$(CYAN)Revision actual de la base de datos:$(NC)"
	@python3 scripts/run_migrations.py --env $(ENV) --operation current

migrate-history: ## Mostrar historial completo de migraciones
	@echo "$(CYAN)Historial de migraciones:$(NC)"
	@python3 scripts/run_migrations.py --env $(ENV) --operation history

migrate-check: ## Verificar migraciones pendientes
	@echo "$(CYAN)Verificando migraciones pendientes...$(NC)"
	@python3 scripts/run_migrations.py --env $(ENV) --validate

# ==============================================================================
# GENERACION DE MIGRACIONES
# ==============================================================================

migrate-auto: ## Generar migracion automatica (usar: MSG='descripcion')
ifndef MSG
	@echo "$(RED)Error: Falta mensaje de migracion$(NC)"
	@echo "$(YELLOW)Uso: make migrate-auto MSG='Descripcion del cambio'$(NC)"
	@exit 1
endif
	@echo "$(CYAN)Generando migracion automatica: $(MSG)...$(NC)"
	@cd . && alembic revision --autogenerate -m "$(MSG)"
	@echo "$(GREEN)Migracion generada exitosamente$(NC)"

migrate-manual: ## Crear migracion manual vacia (usar: MSG='descripcion')
ifndef MSG
	@echo "$(RED)Error: Falta mensaje de migracion$(NC)"
	@echo "$(YELLOW)Uso: make migrate-manual MSG='Descripcion del cambio'$(NC)"
	@exit 1
endif
	@echo "$(CYAN)Creando migracion manual: $(MSG)...$(NC)"
	@cd . && alembic revision -m "$(MSG)"
	@echo "$(GREEN)Migracion manual creada exitosamente$(NC)"

# ==============================================================================
# ENTORNOS ESPECIFICOS
# ==============================================================================

migrate-dev: ## Ejecutar migraciones en development
	@echo "$(CYAN)Ejecutando migraciones en DEVELOPMENT...$(NC)"
	@ENV=development $(MAKE) migrate-upgrade

migrate-test: ## Ejecutar migraciones en testing
	@echo "$(CYAN)Ejecutando migraciones en TESTING...$(NC)"
	@ENV=testing $(MAKE) migrate-upgrade

migrate-prod: ## Ejecutar migraciones en production
	@echo "$(YELLOW)ADVERTENCIA: Ejecutando migraciones en PRODUCTION$(NC)"
	@echo "$(RED)Asegurate de tener backup de la base de datos$(NC)"
	@read -p "Continuar? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	@echo "$(CYAN)Ejecutando deployment de migraciones...$(NC)"
	@bash scripts/deploy_migrations_python.sh
	@echo "$(GREEN)Migraciones de produccion completadas$(NC)"

# ==============================================================================
# COMANDOS DOCKER
# ==============================================================================

migrate-docker: ## Ejecutar migraciones en contenedor Docker
	@echo "$(CYAN)Ejecutando migraciones en Docker...$(NC)"
	@docker-compose -f $(DOCKER_COMPOSE_FILE) --profile migration up migrations
	@echo "$(GREEN)Migraciones Docker completadas$(NC)"

migrate-docker-dev: ## Migraciones Docker en development
	@echo "$(CYAN)Ejecutando migraciones Docker en development...$(NC)"
	@ENVIRONMENT=development docker-compose up migrations
	@echo "$(GREEN)Migraciones Docker development completadas$(NC)"

migrate-docker-rebuild: ## Rebuild y ejecutar migraciones Docker
	@echo "$(CYAN)Rebuild y migraciones Docker...$(NC)"
	@docker-compose build migrations
	@docker-compose --profile migration up migrations
	@echo "$(GREEN)Rebuild y migraciones completadas$(NC)"

# ==============================================================================
# UTILIDADES AVANZADAS
# ==============================================================================

migrate-reset: ## Reset completo de la base de datos (PELIGROSO)
	@echo "$(RED)ADVERTENCIA: Esto eliminara TODOS los datos de la base de datos$(NC)"
	@echo "$(YELLOW)Esta operacion es IRREVERSIBLE$(NC)"
	@read -p "Estas SEGURO que quieres continuar? (escribe 'RESET'): " confirm && [ "$$confirm" = "RESET" ] || exit 1
	@echo "$(CYAN)Ejecutando reset completo...$(NC)"
	@python3 scripts/run_migrations.py --env $(ENV) --operation reset
	@echo "$(GREEN)Reset completado$(NC)"

migrate-validate: ## Validar estado actual de migraciones
	@echo "$(CYAN)Validando estado de migraciones...$(NC)"
	@python3 scripts/run_migrations.py --env $(ENV) --validate
	@echo "$(GREEN)Validacion completada$(NC)"

db-status: ## Estado completo de la base de datos
	@echo "$(CYAN)Estado completo de la base de datos:$(NC)"
	@echo ""
	@echo "$(GREEN)Revision actual:$(NC)"
	@python3 scripts/run_migrations.py --env $(ENV) --operation current
	@echo ""
	@echo "$(GREEN)Migraciones pendientes:$(NC)"
	@python3 scripts/run_migrations.py --env $(ENV) --validate
	@echo ""
	@echo "$(GREEN)Ultimas 5 migraciones:$(NC)"
	@python3 scripts/run_migrations.py --env $(ENV) --operation history | head -10

db-init: ## Inicializar base de datos desde cero
	@echo "$(CYAN)Inicializando base de datos desde cero...$(NC)"
	@python3 scripts/run_migrations.py --env $(ENV) --operation init
	@echo "$(GREEN)Base de datos inicializada$(NC)"

# ==============================================================================
# COMANDOS DE TESTING
# ==============================================================================

migrate-test-all: ## Ejecutar todos los tests de migraciones

test-product: ## Ejecutar todos los tests de Product
	@echo \"🧪 Ejecutando tests de Product...\"
	@python3 -m pytest tests/test_models_product.py tests/test_models_product_status.py -v
	@echo \"✅ Tests Product completados\"

test-product-detailed: ## Tests Product con detalles y coverage
	@echo \"🧪 Tests Product detallados...\"
	@python3 -m pytest tests/test_models_product.py tests/test_models_product_status.py -v --tb=short --cov=app.models.product
	@echo \"📊 Reporte detallado completado\"
	@echo "$(CYAN)Ejecutando tests de migraciones...$(NC)"
	@python3 -m pytest tests/test_makefile_commands.py -v
	@echo "$(GREEN)Tests de migraciones completados$(NC)"

migrate-dry-run: ## Simular migraciones sin ejecutar (dry run)
	@echo "$(CYAN)Simulando migraciones (dry run)...$(NC)"
	@python3 scripts/run_migrations.py --env $(ENV) --dry-run
	@echo "$(GREEN)Dry run completado$(NC)"

# ==============================================================================
# COMANDOS DE DESARROLLO
# ==============================================================================

dev-setup: ## Setup completo para desarrollo
	@echo "$(CYAN)Configurando entorno de desarrollo...$(NC)"
	@ENV=development $(MAKE) db-init
	@ENV=development $(MAKE) migrate-upgrade
	@echo "$(GREEN)Entorno de desarrollo configurado$(NC)"

dev-reset: ## Reset y recarga para desarrollo
	@echo "$(CYAN)Reset completo para desarrollo...$(NC)"
	@ENV=development $(MAKE) migrate-reset
	@ENV=development $(MAKE) db-init
	@ENV=development $(MAKE) migrate-upgrade
	@echo "$(GREEN)Desarrollo reset completado$(NC)"

# ==============================================================================
# COMANDOS DE CONFIGURACION
# ==============================================================================

show-config: ## Mostrar configuracion actual
	@echo "$(CYAN)Configuracion actual:$(NC)"
	@echo "  ENV: $(ENV)"
	@echo "  DOCKER_COMPOSE_FILE: $(DOCKER_COMPOSE_FILE)"
	@echo "  Python: $(shell python3 --version)"
	@echo "  Alembic: $(shell alembic --version 2>/dev/null || echo 'No instalado')"
	@echo ""
	@echo "$(GREEN)Archivos de configuracion:$(NC)"
	@ls -la .env* 2>/dev/null || echo "  No hay archivos .env"
	@echo ""
	@echo "$(GREEN)Docker Compose:$(NC)"
	@ls -la docker-compose*.yml 2>/dev/null || echo "  No hay archivos docker-compose"

# ==============================================================================
# ALIASES RAPIDOS
# ==============================================================================

up: migrate-upgrade ## Alias para migrate-upgrade
down: migrate-downgrade ## Alias para migrate-downgrade
status: migrate-current ## Alias para migrate-current
check: migrate-check ## Alias para migrate-check
auto: migrate-auto ## Alias para migrate-auto

# ==============================================================================
# COMANDOS DE MANTENIMIENTO
# ==============================================================================

clean-migrations: ## Limpiar archivos temporales de migraciones
	@echo "$(CYAN)Limpiando archivos temporales...$(NC)"
	@find alembic/versions -name "*.pyc" -delete 2>/dev/null || true
	@find alembic -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)Limpieza completada$(NC)"

backup-db: ## Crear backup de la base de datos
	@echo "$(CYAN)Creando backup de la base de datos...$(NC)"
	@python3 scripts/run_migrations.py --env $(ENV) --operation backup
	@echo "$(GREEN)Backup creado exitosamente$(NC)"

# ==============================================================================
# FIN DEL MAKEFILE
# ==============================================================================