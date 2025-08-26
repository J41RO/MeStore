# Surgical Modifier

> Sistema de Modificación Precisa de Código con coordinadores especializados y CLI inteligente

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)

[![Documentation](https://img.shields.io/badge/docs-available-blue.svg)](/docs)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

## Descripción

Surgical Modifier es una herramienta CLI avanzada para realizar modificaciones precisas y quirúrgicas en archivos de código fuente. Utiliza una arquitectura modular con coordinadores especializados que orquestan funciones específicas para diferentes tipos de operaciones.

### Características Principales

- **Modificaciones Quirúrgicas**: Cambios precisos sin afectar el código circundante
- **Arquitectura Modular**: Coordinadores ligeros + functions reutilizables
- **CLI Inteligente**: Routing dinámico y detección automática de comandos
- **Sistema de Backup**: Snapshots automáticos con rollback inteligente
- **Validación Integral**: Verificación de sintaxis y coherencia
- **Soporte Multi-lenguaje**: Python, JavaScript, TypeScript, HTML, CSS, y más

## Instalación

### Requisitos

- Python 3.9 o superior
- Git (para control de versiones)
- Entorno virtual recomendado

### Instalación desde código fuente

```bash
git clone <repository-url>
cd surgical_modifier
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows
pip install -e .[dev]
Verificar instalación
bashsurgical-modifier --version
smod --help
Uso Básico
Comandos principales disponibles
bash# Listar comandos disponibles
surgical-modifier --list-commands

# Crear nuevos archivos
surgical-modifier create archivo.py --template python

# Reemplazar contenido
surgical-modifier replace archivo.py "patrón" "nuevo_contenido"

# Insertar antes/después de patrón
surgical-modifier before archivo.py "patrón" "nuevo_código"
surgical-modifier after archivo.py "patrón" "nuevo_código"

# Operaciones avanzadas
surgical-modifier explore proyecto/ --analyze
surgical-modifier update archivo.py --multiple-operations

## Arquitectura

### Estructura del Proyecto
surgical_modifier/
├── coordinators/          # Coordinadores ligeros (150-200 líneas)
│   ├── create.py         # Creación de archivos
│   ├── replace.py        # Reemplazos de contenido
│   ├── before.py         # Inserción antes
│   ├── after.py          # Inserción después
│   ├── append.py         # Adición al final
│   ├── update.py         # Operaciones múltiples
│   ├── delete.py         # Eliminación segura
│   └── explore.py        # Análisis de código
│
├── functions/            # Funcionalidades modulares reutilizables
│   ├── backup/           # Sistema de backup y rollback
│   ├── content/          # Procesamiento de contenido
│   ├── pattern/          # Matching de patrones
│   ├── insertion/        # Lógica de inserción
│   ├── validation/       # Validaciones
│   └── formatting/       # Formateo por lenguaje
│
├── utils/                # Herramientas de soporte
└── tests/                # Suite de testing completa

### Principios de Diseño

1. **Coordinadores Ligeros**: Solo orquestan, no implementan lógica de negocio
2. **Functions Modulares**: Reutilizables entre coordinadores
3. **Separación Clara**: Cada function tiene una responsabilidad específica
4. **Testabilidad**: Cada componente es testeable independientemente

## Stack Tecnológico

- **Lenguaje**: Python 3.9+
- **CLI**: Click para interface de línea de comandos
- **Testing**: pytest con cobertura completa
- **Formateo**: black, isort, flake8
- **Calidad**: pre-commit hooks automáticos

## Desarrollo

### Setup para desarrollo

```bash
# Clonar e instalar dependencias dev
pip install -e .[dev]

# Instalar pre-commit hooks
pre-commit install

# Ejecutar tests
pytest tests/ -v --cov=surgical_modifier

# Formatear código
black surgical_modifier/
isort surgical_modifier/
flake8 surgical_modifier/
Ejecutar tests
bash# Tests unitarios
pytest tests/test_coordinators/ -v

# Tests de integración
pytest tests/integration/ -v

# Coverage completo
pytest --cov=surgical_modifier --cov-report=html
Contribuir

Fork el repositorio
Crear branch para feature (git checkout -b feature/nueva-funcionalidad)
Commit cambios siguiendo conventional commits
Push al branch (git push origin feature/nueva-funcionalidad)
Crear Pull Request

Licencia
MIT License - ver archivo LICENSE para detalles.
Autor
Admin Jairo

Surgical Modifier - Modificaciones precisas de código con arquitectura modular
