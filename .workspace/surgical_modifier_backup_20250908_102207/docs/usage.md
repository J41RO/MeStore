# Guía de Uso - Surgical Modifier

## Instalación

### Requisitos del Sistema
- Python 3.9 o superior
- Git para control de versiones
- Entorno virtual (recomendado)

### Instalación Rápida
```bash
git clone <repository-url>
cd surgical_modifier
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
Verificar Instalación
bashsurgical-modifier --version
python -m surgical_modifier --help
Primeros Pasos
Comando Básico
bashsurgical-modifier --help
Opciones Globales

--verbose, -v: Modo detallado
--dry-run: Simular sin ejecutar
--version: Mostrar versión

Comandos Principales
CREATE - Crear Archivos
bash# Crear archivo Python básico
surgical-modifier create archivo.py --template python

# Crear con contenido personalizado
surgical-modifier create config.json --template json
REPLACE - Reemplazar Contenido
bash# Reemplazo simple
surgical-modifier replace archivo.py "texto_viejo" "texto_nuevo"

# Con patrones regex
surgical-modifier replace --regex archivo.js "function.*old" "function newFunction"
BEFORE/AFTER - Inserción Posicional
bash# Insertar antes de patrón
surgical-modifier before archivo.py "def main():" "    # Setup inicial"

# Insertar después de patrón  
surgical-modifier after archivo.py "import os" "import sys"
EXPLORE - Análisis de Código
bash# Explorar estructura
surgical-modifier explore proyecto/ --analyze

# Generar reporte
surgical-modifier explore . --report
Casos de Uso Comunes
Modernizar Imports
bashsurgical-modifier replace --regex src/ "from.*import.*" "from modern_module import updated_function"
Agregar Headers
bashsurgical-modifier before *.py "#!/usr/bin/env python3" "# -*- coding: utf-8 -*-"
Refactoring Masivo
bashsurgical-modifier explore . --analyze
surgical-modifier replace --multiple proyecto/ "old_pattern" "new_pattern"
