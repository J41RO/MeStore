#!/usr/bin/env python3
"""CLI principal de Surgical Modifier v6.0 - UX Mejorada Completa con Validador JS/TS"""

import click
import re
import sys
import os
from pathlib import Path
from rich.console import Console
from functions.analysis.file_explorer import FileExplorer
import py_compile

# ========================
# FUNCIONES UX MEJORADAS
# ========================

def is_file(arg):
    """Detecta si un argumento parece ser un archivo basado en extensión"""
    return '.' in arg and not arg.startswith('.')

def order_detect(a1, a2, a3):
    """Detecta si los argumentos están en orden intuitivo o tradicional"""
    return 'intuitive' if is_file(a3) and not is_file(a1) else 'traditional'

def suggest_correction(a1, a2, a3):
    """Sugiere corrección cuando detecta posible orden incorrecto"""
    # Caso 1: archivo pattern replacement -> pattern replacement archivo
    if is_file(a1) and not is_file(a3):
        return f'Did you mean: python3 cli.py replace "{a2}" "{a3}" {a1} ?'
    # Caso 2: pattern replacement archivo -> archivo pattern replacement  
    elif is_file(a3) and not is_file(a1):
        return f'Did you mean: python3 cli.py replace {a3} "{a1}" "{a2}" ?'
    return None

def help_msg(err_type, detail=''):
    """Genera mensajes de error informativos con ejemplos"""
    if err_type == 'not_found':
        return f'File not found: {detail}\n\nExamples:\n  python3 cli.py replace file.txt old new\n  python3 cli.py replace old new file.txt'
    return f'Error: {detail}'

# ========================
# IMPORTS Y SETUP
# ========================

# Agregar path para importar coordinadores
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))
from coordinators.replace import ReplaceCoordinator
from coordinators.after import AfterCoordinator
from coordinators.before import BeforeCoordinator
from coordinators.append import AppendCoordinator
from functions.validation.js_ts_validator import JsTsValidator

console = Console()

# ========================
# FUNCIONES HELPER
# ========================

def validate_class_insertion(pattern, content):
    """Validar inserción después de definición de clase para evitar IndentationError"""
    if re.search(r'class\s+\w+.*:', pattern):
        if content and not content.startswith('    '):
            lines = content.split('\n')
            indented_lines = ['    ' + line if line.strip() else line for line in lines]
            content = '\n'.join(indented_lines)
    return content

def backup_file(filepath):
    """Crear backup antes de modificación"""
    backup_path = f"{filepath}.backup_temp"
    try:
        with open(filepath, 'r', encoding='utf-8') as original:
            with open(backup_path, 'w', encoding='utf-8') as backup:
                backup.write(original.read())
        return backup_path
    except Exception as e:
        console.print(f"❌ Error creando backup: {e}", style="red")
        return None

def restore_from_backup(filepath, backup_path):
    """Restaurar archivo desde backup"""
    try:
        with open(backup_path, 'r', encoding='utf-8') as backup:
            with open(filepath, 'w', encoding='utf-8') as original:
                original.write(backup.read())
        os.remove(backup_path)
        return True
    except Exception as e:
        console.print(f"❌ Error restaurando backup: {e}", style="red")
        return False

def is_js_ts_file(filepath):
    """Verifica si el archivo es JavaScript o TypeScript"""
    js_ts_extensions = ['.js', '.jsx', '.ts', '.tsx']
    return any(filepath.endswith(ext) for ext in js_ts_extensions)

def preview_replacement(filepath, pattern, replacement, matcher_options):
    """Muestra preview del resultado sin aplicar cambios"""
    try:
        # Leer contenido actual
        with open(filepath, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Simular el reemplazo usando el coordinador en modo dry-run
        coordinator = ReplaceCoordinator()
        
        # Crear una versión temporal para simular
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix=Path(filepath).suffix, delete=False) as temp_file:
            temp_file.write(original_content)
            temp_filepath = temp_file.name
        
        try:
            # Ejecutar reemplazo en archivo temporal
            result = coordinator.execute(
                file_path=temp_filepath,
                pattern=pattern,
                replacement=replacement,
                **matcher_options
            )
            
            if result.get('success'):
                # Leer resultado
                with open(temp_filepath, 'r', encoding='utf-8') as f:
                    new_content = f.read()
                
                # Validar sintaxis JS/TS si aplica
                validation_result = {'valid': True, 'errors': []}
                if is_js_ts_file(filepath):
                    validator = JsTsValidator()
                    file_extension = Path(filepath).suffix
                    errors = validator.get_syntax_errors(new_content, file_extension)
                    validation_result = {
                        'valid': len(errors) == 0,
                        'errors': errors
                    }
                
                return {
                    'success': True,
                    'original_content': original_content,
                    'new_content': new_content,
                    'matches_count': result.get('matches_count', 0),
                    'validation': validation_result
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Preview failed')
                }
        finally:
            # Limpiar archivo temporal
            os.unlink(temp_filepath)
            
    except Exception as e:
        return {
            'success': False,
            'error': f'Error en preview: {str(e)}'
        }

def show_preview_diff(original, new, filepath):
    """Muestra diferencias entre contenido original y nuevo"""
    import difflib
    
    original_lines = original.splitlines(keepends=True)
    new_lines = new.splitlines(keepends=True)
    
    diff = list(difflib.unified_diff(
        original_lines,
        new_lines,
        fromfile=f"{filepath} (original)",
        tofile=f"{filepath} (después del reemplazo)",
        lineterm=''
    ))
    
    if diff:
        console.print("🔍 PREVIEW - Cambios que se aplicarían:", style="bold blue")
        console.print("=" * 60, style="blue")
        for line in diff:
            if line.startswith('+++') or line.startswith('---'):
                console.print(line.rstrip(), style="bold")
            elif line.startswith('@@'):
                console.print(line.rstrip(), style="cyan")
            elif line.startswith('+'):
                console.print(line.rstrip(), style="green")
            elif line.startswith('-'):
                console.print(line.rstrip(), style="red")
            else:
                console.print(line.rstrip(), style="dim")
        console.print("=" * 60, style="blue")
    else:
        console.print("ℹ️ No se detectaron cambios", style="yellow")

# ========================
# CLI PRINCIPAL
# ========================

@click.group()
@click.version_option(version="6.0-UX-Complete")
@click.option("--verbose", "-v", is_flag=True, help="Modo verbose")
@click.option("--dry-run", is_flag=True, help="Simular sin ejecutar")
def main(verbose, dry_run):
    """Surgical Modifier v6.0 - Sistema de Modificación Precisa de Código con UX Mejorada Completa."""
    if verbose:
        print("Modo verbose activado")
    if dry_run:
        print("Modo dry-run activado")

# ========================
# COMANDO CREATE
# ========================

@main.command()
@click.argument("filepath")
@click.argument("content", required=False, default="")
@click.option("--template", help="Tipo de template a usar")
@click.option("--from-stdin", is_flag=True, help="Leer contenido desde stdin")
def create(filepath, content, template, from_stdin):
    """Crear nuevos archivos con contenido directo o templates."""
    try:
        if content and from_stdin:
            click.echo("Error: No se puede usar contenido directo y --from-stdin simultáneamente", err=True)
            return
            
        if from_stdin:
            content = sys.stdin.read()
            
        filepath_obj = Path(filepath)
        filepath_obj.parent.mkdir(parents=True, exist_ok=True)
        
        if filepath_obj.exists():
            click.echo(f"Error: El archivo {filepath} ya existe", err=True)
            return
            
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
            
        click.echo(f"✅ Archivo {filepath} creado exitosamente")
        
    except Exception as e:
        click.echo(f"Error creando archivo: {e}", err=True)

# ========================
# COMANDO REPLACE (CON MEJORAS UX COMPLETAS + PREVIEW + ROLLBACK)
# ========================

@main.command()
@click.argument("filepath")
@click.argument("pattern")
@click.argument("replacement")
@click.option("--fuzzy", is_flag=True, help="Usar matching aproximado")
@click.option("--regex", is_flag=True, help="Usar patrones regex") 
@click.option("--threshold", type=float, default=0.8, help="Threshold fuzzy (0.0-1.0)")
@click.option("--strict-syntax", is_flag=True, help="Solo acepta orden tradicional archivo pattern replacement")
@click.option("--preview", is_flag=True, help="Mostrar preview del resultado antes de aplicar cambios")
@click.option("--force", is_flag=True, help="Forzar reemplazo incluso si la validación JS/TS falla")
def replace(filepath, pattern, replacement, fuzzy=False, regex=False, threshold=0.8, strict_syntax=False, preview=False, force=False):
    """
    Reemplazar contenido en archivos usando ReplaceCoordinator.
    
    MEJORAS UX v6.0 - Soporta ambas sintaxis:
    - Tradicional: python3 cli.py replace archivo.txt 'viejo' 'nuevo'
    - Intuitiva:   python3 cli.py replace 'viejo' 'nuevo' archivo.txt
    
    Opciones avanzadas:
    --strict-syntax : Solo acepta orden tradicional (archivo pattern replacement)
    --preview       : Mostrar preview antes de aplicar cambios
    --force         : Saltear validación JS/TS si es necesario
    """
    # MEJORA UX 1: Detección automática de orden de argumentos (solo si no está en modo strict)
    if not strict_syntax and order_detect(filepath, pattern, replacement) == 'intuitive':
        filepath, pattern, replacement = replacement, filepath, pattern
    elif strict_syntax and order_detect(filepath, pattern, replacement) == 'intuitive':
        click.echo('❌ Error: Orden incorrecto. Modo strict-syntax solo acepta: archivo pattern replacement', err=True)
        return 1
    
    try:
        # Determinar tipo de matcher basado en opciones
        matcher_type = 'literal'
        matcher_options = {}

        if fuzzy:
            matcher_type = 'fuzzy'
            matcher_options['threshold'] = threshold
        elif regex:
            matcher_type = 'regex'

        matcher_options['matcher_type'] = matcher_type
        # Propagar parámetro force al coordinador/workflow
        matcher_options['force'] = force

        # NUEVA FUNCIONALIDAD: Modo preview
        if preview:
            preview_result = preview_replacement(filepath, pattern, replacement, matcher_options)
            
            if not preview_result['success']:
                click.echo(f"❌ Error en preview: {preview_result['error']}", err=True)
                return 1
            
            # Mostrar preview
            show_preview_diff(preview_result['original_content'], preview_result['new_content'], filepath)
            
            if preview_result['matches_count'] > 0:
                click.echo(f"📊 Coincidencias que se reemplazarían: {preview_result['matches_count']}")
            
            # Mostrar validación JS/TS si aplica
            validation = preview_result['validation']
            if not validation['valid']:
                console.print("⚠️ ADVERTENCIA: El reemplazo resultaría en sintaxis JS/TS inválida:", style="yellow")
                for error in validation['errors']:
                    console.print(f"  - {error}", style="red")
                if not force:
                    console.print("💡 Usa --force para aplicar de todas formas", style="blue")
            else:
                console.print("✅ Validación JS/TS: Sintaxis válida", style="green")
            
            # Pedir confirmación
            if click.confirm("¿Aplicar estos cambios?"):
                click.echo("Aplicando cambios...")
            else:
                click.echo("Operación cancelada")
                return 0

        # Usar ReplaceCoordinator para ejecutar replace real
        coordinator = ReplaceCoordinator()
        result = coordinator.execute(
            file_path=filepath,
            pattern=pattern,
            replacement=replacement,
            **matcher_options
        )

        if result.get('success'):
            click.echo(f"✅ Reemplazo exitoso en {filepath}")
            if result.get('matches_count'):
                click.echo(f"📊 Coincidencias reemplazadas: {result['matches_count']}")
        else:
            click.echo(f"❌ Error: {result.get('error', 'Unknown error')}", err=True)
            import sys
            sys.exit(1)

    except FileNotFoundError:
        # MEJORA UX 3: Sugerencias inteligentes para archivos no encontrados
        suggestion = suggest_correction(filepath, pattern, replacement)
        if suggestion:
            click.echo(f'💡 {suggestion}', err=True)
        # MEJORA UX 4: Mensajes de error informativos con ejemplos
        click.echo(help_msg('not_found', filepath), err=True)
        return 1
    except Exception as e:
        click.echo(f"❌ Error inesperado: {str(e)}", err=True)
        return 1

# ========================
# COMANDO BEFORE
# ========================

@main.command()
@click.argument("filepath")
@click.argument("pattern")
@click.argument("content", required=False, default="")
@click.option('--from-stdin', is_flag=True, help='Leer contenido desde stdin para contenido multilínea')
@click.option('--flexible', is_flag=True, help='Usar fuzzy matching flexible que ignora diferencias de espaciado')
def before(filepath, pattern, content, from_stdin, flexible):
    """Insertar contenido antes de un patrón."""
    if from_stdin:
        content = sys.stdin.read().strip()
    
    validated_content = validate_class_insertion(pattern, content)
    
    backup_path = None
    if os.path.exists(filepath):
        backup_path = backup_file(filepath)
        if not backup_path:
            console.print("❌ Error creando backup, abortando operación", style="red")
            sys.exit(1)
    
    try:
        coordinator = BeforeCoordinator()
        result = coordinator.execute(filepath, pattern, validated_content, flexible=flexible)
        
        if result.get('success', False):
            if filepath.endswith('.py'):
                try:
                    py_compile.compile(filepath, doraise=True)
                    if backup_path:
                        os.remove(backup_path)
                    console.print(f"✅ Contenido insertado antes de '{pattern}' en {filepath}", style="green")
                    if result.get('message'):
                        console.print(f"📝 {result['message']}", style="blue")
                except py_compile.PyCompileError as syntax_error:
                    console.print(f"❌ Error de sintaxis detectado tras modificación", style="red")
                    console.print(f"📝 {str(syntax_error)}", style="yellow")
                    if backup_path:
                        if restore_from_backup(filepath, backup_path):
                            console.print("🔄 Archivo restaurado desde backup", style="cyan")
                        else:
                            console.print("❌ Error restaurando backup", style="red")
                    sys.exit(1)
            else:
                if backup_path:
                    os.remove(backup_path)
                console.print(f"✅ Contenido insertado antes de '{pattern}' en {filepath}", style="green")
                if result.get('message'):
                    console.print(f"📝 {result['message']}", style="blue")
        else:
            console.print(f"❌ Error: {result.get('error', 'Operación fallida')}", style="red")
            if backup_path:
                restore_from_backup(filepath, backup_path)
            sys.exit(1)
            
    except Exception as e:
        console.print(f"❌ Error ejecutando operación before: {str(e)}", style="red")
        if backup_path:
            restore_from_backup(filepath, backup_path)
        sys.exit(1)

# ========================
# COMANDO AFTER
# ========================

@main.command()
@click.argument("filepath")
@click.argument("pattern")
@click.argument("content", required=False, default="")
@click.option('--from-stdin', is_flag=True, help='Leer contenido desde stdin para contenido multilínea')
@click.option('--flexible', is_flag=True, help='Usar fuzzy matching flexible que ignora diferencias de espaciado')
def after(filepath, pattern, content, from_stdin, flexible):
    """Insertar contenido después de un patrón."""
    if from_stdin:
        content = sys.stdin.read().strip()
    
    validated_content = validate_class_insertion(pattern, content)
    
    backup_path = None
    if os.path.exists(filepath):
        backup_path = backup_file(filepath)
        if not backup_path:
            click.echo("❌ Error creando backup, abortando operación", err=True)
            return 1
    
    try:
        coordinator = AfterCoordinator()
        result = coordinator.execute(filepath, pattern, validated_content, flexible=flexible)
        
        if result.get('success', False):
            if filepath.endswith('.py'):
                try:
                    py_compile.compile(filepath, doraise=True)
                    if backup_path:
                        os.remove(backup_path)
                    click.echo(f"✅ Contenido insertado exitosamente después de '{pattern}' en {filepath}")
                    return 0
                except py_compile.PyCompileError as syntax_error:
                    click.echo(f"❌ Error de sintaxis detectado tras modificación", err=True)
                    click.echo(f"📝 {str(syntax_error)}", err=True)
                    if backup_path:
                        if restore_from_backup(filepath, backup_path):
                            click.echo("🔄 Archivo restaurado desde backup", err=True)
                        else:
                            click.echo("❌ Error restaurando backup", err=True)
                    return 1
            else:
                if backup_path:
                    os.remove(backup_path)
                click.echo(f"✅ Contenido insertado exitosamente después de '{pattern}' en {filepath}")
                return 0
        else:
            error_msg = result.get('error', 'Error desconocido')
            click.echo(f"❌ Error: {error_msg}", err=True)
            if backup_path:
                restore_from_backup(filepath, backup_path)
            return 1
            
    except Exception as e:
        click.echo(f"❌ Error inesperado: {str(e)}", err=True)
        if backup_path:
            restore_from_backup(filepath, backup_path)
        return 1

# ========================
# COMANDO APPEND
# ========================

@main.command()
@click.argument("filepath")
@click.argument("content")
@click.option("--separator", default="\n", help="Separador entre contenido existente y nuevo")
def append(filepath, content, separator):
    """Agregar contenido al final del archivo."""
    try:
        coordinator = AppendCoordinator()
        content_with_separator = separator + content
        result = coordinator.execute(filepath, "", content_with_separator)
        
        if result.get('success', False):
            click.echo(f"Contenido agregado exitosamente al final de {filepath}")
        else:
            click.echo(f"Error: {result.get('error', 'Error desconocido')}", err=True)
            return 1
            
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        return 1

# ========================
# COMANDO EXPLORE
# ========================
@main.command()
@click.argument("path")
@click.option("--analyze", is_flag=True, help="Analizar estructura")
@click.option("--lines", help="Rango de líneas (formato: start:end)")
@click.option("--around", type=int, help="Línea central para contexto")
@click.option("--context", type=int, default=5, help="Líneas de contexto (default: 5)")
def explore(path, analyze, lines, around, context):
    """Explorar y analizar estructura de código con opciones avanzadas.
    
    Ejemplos de uso:
      explore archivo.py                    # Mostrar primeras 20 líneas
      explore archivo.py --lines 10:20      # Mostrar líneas 10 a 20
      explore archivo.py --around 50 --context 3  # 3 líneas alrededor de la 50
      explore archivo.py --analyze          # Análisis básico (legacy)
    """
    explorer = FileExplorer()
    
    try:
        # Leer archivo
        file_lines = explorer.read_file_lines(path)
        
        # Funcionalidad legacy (backward compatibility)
        if analyze:
            print(f"Analizando estructura de {path}...")
            print(f"Total de líneas: {len(file_lines)}")
            return
        
        # Nueva funcionalidad --lines
        if lines:
            try:
                start, end = explorer.parse_lines_range(lines)
                range_lines = explorer.get_lines_range(file_lines, start, end)
                output = explorer.format_output(range_lines, start_line=start)
                print(f"Líneas {start}-{end} de {path}:")
                print(output)
                return
            except ValueError as e:
                print(f"Error en parámetro --lines: {e}")
                return
        
        # Nueva funcionalidad --around
        if around:
            try:
                context_lines, start_line = explorer.get_context_around(file_lines, around, context)
                output = explorer.format_output(context_lines, start_line=start_line, highlight_line=around)
                print(f"Contexto alrededor de línea {around} (±{context} líneas) en {path}:")
                print(output)
                return
            except ValueError as e:
                print(f"Error en parámetro --around: {e}")
                return
        
        # Si no hay parámetros específicos, mostrar primeras 20 líneas
        default_lines = explorer.get_lines_range(file_lines, 1, min(20, len(file_lines)))
        output = explorer.format_output(default_lines)
        print(f"Primeras líneas de {path}:")
        print(output)
        
    except (FileNotFoundError, PermissionError, UnicodeDecodeError, ValueError) as e:
        print(f"Error explorando {path}: {e}")

# ========================
# COMANDOS DE AYUDA
# ========================

@main.command("list-commands")
def list_commands():
    """Listar todos los comandos disponibles con ejemplos de mejoras UX."""
    print("=" * 60)
    print("SURGICAL MODIFIER v6.0 - COMANDOS DISPONIBLES")
    print("=" * 60)
    print("COMANDOS BÁSICOS:")
    print("  create      : Crear nuevos archivos")
    print("  replace     : Reemplazar contenido (🎯 CON MEJORAS UX + PREVIEW)")
    print("  before      : Insertar antes de patrón")
    print("  after       : Insertar después de patrón")  
    print("  append      : Agregar al final")
    print("  explore     : Explorar estructura")
    print("  list-commands : Mostrar este listado")
    print()
    print("🎯 MEJORAS UX v6.0 EN COMANDO REPLACE:")
    print("  ✅ ORDEN INTUITIVO:")
    print("    python3 cli.py replace 'buscar' 'reemplazar' archivo.txt")
    print("  ✅ ORDEN TRADICIONAL (mantiene compatibilidad):")
    print("    python3 cli.py replace archivo.txt 'buscar' 'reemplazar'")
    print("  ✅ MODO PREVIEW:")
    print("    python3 cli.py replace --preview archivo.js 'props' 'properties'")
    print("  ✅ VALIDACIÓN JS/TS AUTOMÁTICA con rollback")
    print("  ✅ MODO FORCE para saltear validación:")
    print("    python3 cli.py replace --force archivo.tsx 'old' 'new'")
    print("  ✅ SUGERENCIAS AUTOMÁTICAS cuando hay errores de orden")
    print("  ✅ MENSAJES DE ERROR informativos con ejemplos")
    print()
    print("EJEMPLOS PRÁCTICOS:")
    print("  python3 cli.py replace --preview 'old_function' 'new_function' main.js")
    print("  python3 cli.py replace --strict-syntax main.py 'old' 'new'")
    print("  python3 cli.py replace --regex '\\bclass\\b' 'class Modern' app.py")
    print("=" * 60)

@main.command("help-ux")
def help_ux():
    """Ayuda específica sobre las mejoras UX v6.0."""
    print("🎯 MEJORAS UX SURGICAL MODIFIER v6.0")
    print("=" * 50)
    print()
    print("1. ORDEN INTUITIVO DE ARGUMENTOS:")
    print("   Antes: python3 cli.py replace archivo.txt 'viejo' 'nuevo'")
    print("   Ahora: python3 cli.py replace 'viejo' 'nuevo' archivo.txt")
    print("   Ambas sintaxis funcionan automáticamente!")
    print()
    print("2. MODO PREVIEW:")
    print("   --preview : Muestra cambios antes de aplicar")
    print("   Incluye validación JS/TS automática")
    print()
    print("3. VALIDACIÓN JS/TS AUTOMÁTICA:")
    print("   Detecta automáticamente archivos .js/.jsx/.ts/.tsx")
    print("   Valida sintaxis después de modificaciones")
    print("   Rollback automático si detecta errores")
    print()
    print("4. MODO FORCE:")
    print("   --force : Saltear validación JS/TS si es necesario")
    print("   Útil para casos especiales")
    print()
    print("5. MODO STRICT-SYNTAX:")
    print("   --strict-syntax : Solo acepta orden tradicional")
    print("   Útil para scripts automatizados")
    print()
    print("6. SUGERENCIAS INTELIGENTES:")
    print("   Cuando detecta posible confusión de orden, sugiere corrección")
    print("   Ejemplo: '💡 Did you mean: python3 cli.py replace ...'")
    print()
    print("7. MENSAJES DE ERROR MEJORADOS:")
    print("   Incluyen ejemplos de sintaxis correcta")
    print("   Reducen tiempo de debugging")
    print()
    print("8. COMPATIBILIDAD TOTAL:")
    print("   Todo código existente sigue funcionando")
    print("   Cero regresiones, solo mejoras")

# ========================
# ENTRY POINT
# ========================

if __name__ == "__main__":
    main()