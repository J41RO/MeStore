# Functions - Surgical Modifier

## Arquitectura de Functions

Las functions son módulos reutilizables que implementan funcionalidades específicas. Son utilizadas por los coordinadores para realizar operaciones concretas.

## Categorías de Functions

### Backup Functions (`functions/backup/`)

#### `create_snapshot(filepath)`
Crea respaldo automático antes de modificaciones.

**Parámetros:**
- `filepath`: Archivo a respaldar

**Retorna:**
- `backup_path`: Ruta del backup creado

#### `rollback_changes(backup_path)`
Restaura archivo desde backup.

**Uso:**
```python
from functions.backup import create_snapshot, rollback_changes

backup = create_snapshot("app.py")
# ... operaciones ...
rollback_changes(backup)  # si hay errores
Content Functions (functions/content/)
load_file(filepath)
Carga contenido de archivo con manejo de encoding.
save_file(filepath, content)
Guarda contenido con validación de sintaxis.
generate_from_template(template_name, variables)
Genera contenido desde template con variables.
Pattern Functions (functions/pattern/)
match_pattern(content, pattern, regex=False)
Encuentra coincidencias de patrón en contenido.
Parámetros:

content: Texto donde buscar
pattern: Patrón a buscar
regex: Usar expresiones regulares

find_insertion_point(content, pattern)
Localiza punto exacto para inserción.
Insertion Functions (functions/insertion/)
insert_before(content, pattern, new_content)
Inserta contenido antes de patrón encontrado.
insert_after(content, pattern, new_content)
Inserta contenido después de patrón.
preserve_indentation(content, insertion_point)
Mantiene indentación correcta durante inserción.
Validation Functions (functions/validation/)
validate_syntax(filepath, content)
Valida sintaxis según tipo de archivo.
Soportado:

Python: AST parsing
JavaScript: Syntax check
JSON: JSON parsing
YAML: YAML parsing

validate_filepath(path)
Verifica que ruta sea válida y accesible.
Formatting Functions (functions/formatting/)
apply_language_format(content, language)
Aplica formateo específico del lenguaje.
Lenguajes soportados:

Python: black, isort
JavaScript: prettier
JSON: formateo estándar

Interface Estándar
Todas las functions siguen convenciones:
pythondef function_name(required_params, optional_param=None):
    """Descripción clara de la función.
    
    Args:
        required_params: Descripción del parámetro
        optional_param: Parámetro opcional
        
    Returns:
        Descripción del valor retornado
        
    Raises:
        ExceptionType: Cuándo se lanza la excepción
    """
    # Implementación
    return result
Testing de Functions
Cada function tiene tests independientes:
pythondef test_load_file():
    content = load_file("test.py")
    assert content is not None
    
def test_insert_before():
    result = insert_before("line1\nline2", "line2", "new_line\n")
    assert "new_line" in result
