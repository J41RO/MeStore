Guía de Desarrollo - Surgical Modifier
Setup de Desarrollo
Requisitos

Python 3.9+
Git
pre-commit

Instalación Desarrollo
bashgit clone <repository>
cd surgical_modifier
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pre-commit install
Estructura de Testing
Ejecutar Tests
bash# Tests completos
pytest tests/ -v --cov=surgical_modifier

# Tests específicos
pytest tests/test_coordinators/ -v
pytest tests/test_functions/ -v

# Coverage HTML
pytest --cov-report=html
Convenciones de Testing

Un archivo test por módulo
Nombres descriptivos: test_create_coordinator_basic_functionality
Setup y teardown apropiados
Mocks para dependencies externas

Contribuir
Flujo de Trabajo

Fork del repositorio
Crear branch: git checkout -b feature/nueva-funcionalidad
Desarrollar con tests
Ejecutar pre-commit: pre-commit run --all-files
Commit: seguir conventional commits
Push y crear Pull Request

Conventional Commits
feat: nueva funcionalidad
fix: corrección de bug
docs: cambios en documentación
test: agregar tests
refactor: refactoring sin cambios funcionales
Arquitectura para Desarrolladores
Agregar Nuevo Coordinador

Crear archivo en coordinators/
Heredar de BaseCoordinator
Implementar métodos requeridos
Registrar en cli.py
Agregar tests

Agregar Nueva Function

Ubicar en directorio apropiado en functions/
Seguir interface estándar
Documentar completamente
Tests unitarios independientes

Guidelines de Código

Black para formateo
isort para imports
flake8 para linting
mypy para type checking
Máximo 88 caracteres por línea
