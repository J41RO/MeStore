# API Reference - Surgical Modifier

## Comandos CLI

### surgical-modifier [OPCIONES GLOBALES] COMANDO [ARGUMENTOS]

#### Opciones Globales
- `--verbose, -v`: Activar modo detallado
- `--dry-run`: Simular operación sin ejecutar
- `--version`: Mostrar versión del programa
- `--help`: Mostrar ayuda

### Comandos Disponibles

#### CREATE
Crear nuevos archivos con templates predefinidos.

```bash
surgical-modifier create FILEPATH [--template TIPO]
Parámetros:

FILEPATH: Ruta del archivo a crear
--template: Tipo de template (python, javascript, html, etc.)

Ejemplo:
bashsurgical-modifier create src/utils.py --template python
REPLACE
Reemplazar contenido en archivos existentes.
bashsurgical-modifier replace FILEPATH PATTERN REPLACEMENT [--regex]
Parámetros:

FILEPATH: Archivo a modificar
PATTERN: Texto o patrón a buscar
REPLACEMENT: Texto de reemplazo
--regex: Usar expresiones regulares

Ejemplo:
bashsurgical-modifier replace app.py "old_function" "new_function"
surgical-modifier replace --regex config.js "port:\s*\d+" "port: 3000"
BEFORE
Insertar contenido antes de un patrón específico.
bashsurgical-modifier before FILEPATH PATTERN CONTENT
Ejemplo:
bashsurgical-modifier before main.py "def main():" "    # Initialize logging"
AFTER
Insertar contenido después de un patrón específico.
bashsurgical-modifier after FILEPATH PATTERN CONTENT
Ejemplo:
bashsurgical-modifier after imports.py "import os" "import sys"
EXPLORE
Analizar y explorar estructura de código.
bashsurgical-modifier explore PATH [--analyze] [--report]
Opciones:

--analyze: Análisis detallado de estructura
--report: Generar reporte completo

LIST-COMMANDS
Mostrar todos los comandos disponibles.
bashsurgical-modifier list-commands
Códigos de Salida

0: Operación exitosa
1: Error de argumentos
2: Archivo no encontrado
3: Error de permisos
4: Error de sintaxis
5: Error de validación

Variables de Entorno

SURGICAL_MODIFIER_CONFIG: Archivo de configuración personalizado
SURGICAL_MODIFIER_BACKUP_DIR: Directorio para backups
SURGICAL_MODIFIER_VERBOSE: Activar modo verbose por defecto
