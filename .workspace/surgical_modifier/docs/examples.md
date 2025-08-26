# Ejemplos Prácticos - Surgical Modifier

## Casos de Uso Comunes

### Modernización de Código Python

#### Actualizar Imports Obsoletos
```bash
# Reemplazar imports antiguos
surgical-modifier replace src/ "from collections import OrderedDict" "from typing import OrderedDict"

# Modernizar format strings
surgical-modifier replace --regex "*.py" "\".*%.*\"" "f\"...\""
Agregar Type Hints
bash# Agregar imports de typing
surgical-modifier after utils.py "import os" "from typing import List, Dict, Optional"

# Modificar signatures de funciones
surgical-modifier replace functions.py "def process_data(data):" "def process_data(data: List[Dict]) -> Optional[Dict]:"
Refactoring de Proyectos JavaScript
Migrar a ES6+
bash# Convertir var a const/let
surgical-modifier replace --regex src/ "var\s+(\w+)" "const $1"

# Modernizar funciones
surgical-modifier replace app.js "function(data)" "(data) =>"
Agregar Imports ES6
bash# Convertir requires a imports
surgical-modifier replace index.js "const express = require('express')" "import express from 'express'"
Configuración de Proyectos
Setup Inicial de Python
bash# Crear estructura base
surgical-modifier create setup.py --template python-setup
surgical-modifier create requirements.txt --template requirements
surgical-modifier create .gitignore --template python-gitignore

# Agregar headers a archivos Python
surgical-modifier before "*.py" "#!/usr/bin/env python3" "# -*- coding: utf-8 -*-"
Configurar Linting
bash# Agregar configuración pre-commit
surgical-modifier create .pre-commit-config.yaml --template pre-commit

# Setup de CI/CD
surgical-modifier create .github/workflows/ci.yml --template github-ci
Mantenimiento de Código
Análisis de Código
bash# Explorar proyecto completo
surgical-modifier explore . --analyze

# Generar reporte de métricas
surgical-modifier explore src/ --report --output metrics.json
Limpieza Automática
bash# Eliminar imports no usados
surgical-modifier replace --regex "*.py" "^import \w+$" ""

# Normalizar espaciado
surgical-modifier replace --regex "*.py" "\s{2,}" " "
Proyectos Web
Migración React
bash# Convertir class components a functional
surgical-modifier replace components/ "class.*extends React.Component" "function"

# Actualizar hooks
surgical-modifier after App.jsx "import React" "import { useState, useEffect }"
Configurar TypeScript
bash# Cambiar extensiones
surgical-modifier explore src/ --rename-extensions js tsx

# Agregar tipos básicos
surgical-modifier replace --regex "*.tsx" "const \w+ =" "const name: string ="
Flujos de Trabajo Completos
Nuevo Proyecto Python
bash# 1. Estructura inicial
surgical-modifier create src/__init__.py --template python-init
surgical-modifier create tests/__init__.py --template python-init
surgical-modifier create setup.py --template python-setup

# 2. Configuración de desarrollo
surgical-modifier create .pre-commit-config.yaml --template pre-commit
surgical-modifier create pytest.ini --template pytest-config

# 3. Documentación
surgical-modifier create README.md --template readme-python
surgical-modifier create CHANGELOG.md --template changelog

# 4. CI/CD
surgical-modifier create .github/workflows/test.yml --template python-ci
Refactoring Masivo
bash# 1. Análisis inicial
surgical-modifier explore . --analyze --report

# 2. Backup completo
surgical-modifier backup --create-snapshot

# 3. Aplicar cambios sistemáticos
surgical-modifier replace --regex "*.py" "old_pattern" "new_pattern"
surgical-modifier update src/ --multiple-operations

# 4. Validación
surgical-modifier validate . --syntax-check --test-run

# 5. Rollback si necesario
surgical-modifier backup --rollback-if-failed
