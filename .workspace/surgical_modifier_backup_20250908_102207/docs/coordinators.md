# Coordinadores - Surgical Modifier

## Concepto

Los coordinadores son componentes ligeros que orquestan operaciones específicas sin implementar lógica de negocio compleja. Cada coordinador tiene una responsabilidad única y bien definida.

## Coordinadores Disponibles

### CreateCoordinator (`create.py`)
Gestiona la creación de nuevos archivos con templates.

**Responsabilidades:**
- Validar ruta de destino
- Seleccionar template apropiado
- Coordinar generación de contenido
- Aplicar formateo específico del lenguaje

**Functions utilizadas:**
- `template.load_template()`
- `content.generate_from_template()`
- `validation.validate_filepath()`
- `formatting.apply_language_format()`

### ReplaceCoordinator (`replace.py`)
Coordina operaciones de reemplazo de contenido.

**Responsabilidades:**
- Cargar contenido original
- Ejecutar matching de patrones
- Aplicar reemplazos
- Validar resultado final

**Functions utilizadas:**
- `content.load_file()`
- `pattern.match_and_replace()`
- `backup.create_snapshot()`
- `validation.validate_syntax()`

### BeforeCoordinator (`before.py`)
Gestiona inserción de contenido antes de patrones específicos.

**Responsabilidades:**
- Localizar patrón de inserción
- Mantener indentación correcta
- Insertar contenido en posición adecuada
- Preservar formato original

**Functions utilizadas:**
- `pattern.find_insertion_point()`
- `insertion.insert_before()`
- `formatting.preserve_indentation()`

### AfterCoordinator (`after.py`)
Coordina inserción después de patrones específicos.

**Responsabilidades:**
- Identificar punto de inserción
- Gestionar espaciado y formato
- Insertar contenido manteniendo estructura

### ExploreCoordinator (`explore.py`)
Analiza y reporta estructura de código.

**Responsabilidades:**
- Escanear directorios y archivos
- Generar métricas de código
- Crear reportes de análisis
- Identificar patrones y problemas

## Interface Estándar

Todos los coordinadores implementan la interface:

```python
class BaseCoordinator:
   def __init__(self, config):
       self.config = config
       
   def execute(self, **kwargs):
       """Método principal de ejecución"""
       pass
       
   def validate_input(self, **kwargs):
       """Validación de parámetros de entrada"""
       pass
       
   def cleanup(self):
       """Limpieza después de ejecución"""
       pass
Guías de Desarrollo
Crear Nuevo Coordinador

Heredar de BaseCoordinator
Implementar métodos obligatorios
Mantener coordinador bajo 200 líneas
Delegar lógica compleja a functions
Agregar tests comprehensivos
