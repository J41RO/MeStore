# Configuración - Surgical Modifier

## Archivo de Configuración

### Ubicación por Defecto
- `~/.surgical-modifier/config.yaml`
- `./surgical-modifier.yaml` (directorio actual)
- Variable de entorno: `SURGICAL_MODIFIER_CONFIG`

### Estructura de Configuración

```yaml
# surgical-modifier.yaml
general:
 backup_enabled: true
 backup_directory: "./.backups"
 verbose: false
 dry_run: false

templates:
 directory: "./templates"
 default_language: "python"
 
validation:
 syntax_check: true
 strict_mode: false
 
formatting:
 auto_format: true
 preserve_indentation: true
 max_line_length: 88
 
coordinators:
 create:
   default_template: "basic"
 replace:
   case_sensitive: true
   regex_enabled: false
 explore:
   include_hidden: false
   max_depth: 10
Variables de Entorno

SURGICAL_MODIFIER_CONFIG: Ruta del archivo de configuración
SURGICAL_MODIFIER_BACKUP_DIR: Directorio para backups
SURGICAL_MODIFIER_VERBOSE: Activar modo verbose
SURGICAL_MODIFIER_DRY_RUN: Modo simulación por defecto

Configuración por Comando
CREATE
yamlcreate:
  templates_path: "./templates"
  default_permissions: "644"
  auto_format: true
REPLACE
yamlreplace:
  backup_before: true
  case_sensitive: false
  max_replacements: -1  # ilimitado
