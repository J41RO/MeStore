# 🔧 Universal Code Modifier

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Development Status](https://img.shields.io/badge/status-alpha-orange)](https://github.com/yourusername/universal-code-modifier)

> Una herramienta poderosa y segura para modificar código de forma universal a través de múltiples lenguajes de programación.

## 📋 Tabla de Contenidos

- [🎯 Descripción](#-descripción)
- [✨ Características](#-características)
- [🚀 Instalación](#-instalación)
- [📖 Uso Básico](#-uso-básico)
- [📁 Estructura del Proyecto](#-estructura-del-proyecto)
- [🧪 Testing](#-testing)
- [🤝 Contribuir](#-contribuir)
- [📋 Roadmap](#-roadmap)
- [📄 Licencia](#-licencia)

## 🎯 Descripción

Universal Code Modifier es una herramienta de línea de comandos diseñada para realizar modificaciones seguras y controladas en archivos de código fuente de múltiples lenguajes de programación. El proyecto está en fase **alpha** y proporciona una base sólida para transformaciones de código automatizadas.

### 🔍 Problema que Resuelve

- **Modificaciones manuales repetitivas** en múltiples archivos de código
- **Falta de consistencia** en transformaciones de código a gran escala  
- **Riesgo de errores** al modificar código manualmente
- **Ausencia de herramientas universales** que funcionen con múltiples lenguajes

### 🎯 Objetivo

Proporcionar una interfaz unificada y segura para aplicar modificaciones programáticas a código fuente, con respaldo automático, validación y soporte multi-lenguaje.

## ✨ Características

### 🚀 Funcionalidades Actuales (v0.1.0)

- ✅ **Detección automática** de archivos de código por extensión
- ✅ **Sistema de respaldo automático** antes de modificaciones
- ✅ **Logging detallado** de todas las operaciones
- ✅ **Validación de archivos** antes de procesamiento
- ✅ **Soporte multi-lenguaje** (Python, JavaScript, TypeScript, Java, C++, C, C#)
- ✅ **Listado recursivo** de archivos en directorios
- ✅ **Interfaz programática** simple y extensible

### 🔮 Funcionalidades Planificadas

- 🔲 **Interfaz CLI** interactiva con click
- 🔲 **Patrones de transformación** configurables
- 🔲 **Integración con Git** para manejo de versiones
- 🔲 **Soporte para archivos de configuración** (YAML, TOML)
- 🔲 **Análisis AST** para transformaciones avanzadas
- 🔲 **Plugin system** para extensiones personalizadas

## 🚀 Instalación

### Prerrequisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Git (opcional, para desarrollo)

### Instalación Rápida

```bash
# Clonar el repositorio
git clone https://github.com/yourusername/universal-code-modifier.git
cd universal-code-modifier

# Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Verificar instalación
python universal_modifier.py
Instalación para Desarrollo
bash# Instalar dependencias de desarrollo
pip install -r requirements.txt

# Instalar herramientas de desarrollo adicionales
pip install black flake8 mypy pytest pytest-cov

# Verificar herramientas de desarrollo
black --version && flake8 --version && mypy --version
📖 Uso Básico
Interfaz Programática
pythonfrom universal_modifier import UniversalModifier

# Crear instancia del modificador
modifier = UniversalModifier(base_path="/ruta/a/tu/proyecto")

# Listar archivos de código en un directorio
files = modifier.list_files(recursive=True)
print(f"Encontrados {len(files)} archivos de código")

# Validar un archivo específico
if modifier.validate_file("mi_archivo.py"):
    print("Archivo válido para procesamiento")
    
    # Crear respaldo antes de modificar
    backup = modifier.create_backup("mi_archivo.py")
    if backup:
        print(f"Respaldo creado en: {backup}")
Ejecutar Directamente
bash# Ejecutar la herramienta directamente
python universal_modifier.py

# Ver información del proyecto
python universal_modifier.py --info  # (Funcionalidad futura)
Ejemplos de Uso
python# Ejemplo 1: Listar archivos Python en proyecto
modifier = UniversalModifier()
python_files = [f for f in modifier.list_files() if f.suffix == '.py']

# Ejemplo 2: Procesar múltiples archivos con respaldo
for file_path in python_files:
    if modifier.validate_file(file_path):
        backup = modifier.create_backup(file_path)
        # Aquí irían las modificaciones específicas
        print(f"Procesado: {file_path}")
📁 Estructura del Proyecto
universal-code-modifier/
├── 📄 README.md                 # Este archivo
├── 🐍 universal_modifier.py     # Módulo principal
├── 📋 requirements.txt          # Dependencias del proyecto
├── 📁 tests/                    # Tests unitarios (futuro)
├── 📁 examples/                 # Ejemplos de uso (futuro)
└── 📁 docs/                     # Documentación adicional (futuro)
Descripción de Archivos

universal_modifier.py: Contiene la clase UniversalModifier con toda la funcionalidad principal
requirements.txt: Lista de dependencias mínimas para el proyecto
tests/: Directorio preparado para tests unitarios y de integración
examples/: Directorio para ejemplos de uso y casos prácticos
docs/: Directorio para documentación técnica adicional

🧪 Testing
Ejecutar Tests (Futuro)
bash# Ejecutar todos los tests
pytest tests/

# Ejecutar tests con coverage
pytest tests/ --cov=universal_modifier --cov-report=html

# Ejecutar tests específicos
pytest tests/test_universal_modifier.py -v
Verificación de Código
bash# Verificar formato de código
black --check universal_modifier.py

# Verificar estilo de código
flake8 universal_modifier.py

# Verificar tipos estáticos
mypy universal_modifier.py
🤝 Contribuir
Proceso de Contribución

Fork el repositorio
Crear una rama para tu feature (git checkout -b feature/nueva-funcionalidad)
Desarrollar tu funcionalidad con tests apropiados
Verificar que el código pasa todas las verificaciones:
bashblack universal_modifier.py
flake8 universal_modifier.py
mypy universal_modifier.py
pytest tests/

Commit tus cambios (git commit -am 'Agregar nueva funcionalidad')
Push a la rama (git push origin feature/nueva-funcionalidad)
Crear un Pull Request

Estándares de Código

Formato: Black para formateo automático
Linting: Flake8 para verificación de estilo
Type Hints: MyPy para verificación de tipos
Testing: Pytest para tests unitarios
Documentación: Docstrings para todas las funciones y clases

📋 Roadmap
v0.2.0 - CLI Interface

🔲 Implementar interfaz de línea de comandos con Click
🔲 Comandos básicos: list, backup, modify
🔲 Configuración por archivos YAML/TOML

v0.3.0 - Transformaciones Básicas

🔲 Sistema de patrones de transformación
🔲 Modificaciones basadas en regex
🔲 Soporte para plantillas de código

v0.4.0 - Integración Avanzada

🔲 Integración con Git para manejo de versiones
🔲 Análisis AST para transformaciones avanzadas
🔲 Plugin system para extensiones

v1.0.0 - Release Estable

🔲 API estable y documentada
🔲 Suite completa de tests
🔲 Documentación completa
🔲 Ejemplos y casos de uso

📄 Licencia
Este proyecto está bajo la Licencia MIT. Consulta el archivo LICENSE para más detalles.

Desarrollado con ❤️ para la comunidad de desarrolladores
