#!/usr/bin/env python3
"""CLI principal de Surgical Modifier v6.0 - UX Mejorada Completa con Sistema de Preview/Dry-Run"""

import click
import re
import sys
import os
from pathlib import Path
from rich.console import Console
from functions.analysis.file_explorer import FileExplorer
from functions.analysis.technology_detector import detect_technology_by_extension, get_coordinator_for_technology
import py_compile

# Agregar import del CoordinatorRouter
from coordinators.coordinator_router import CoordinatorRouter

# ========================
# FUNCIONES UX MEJORADAS
# ========================

def is_file(arg):
   """Detecta si un argumento parece ser un archivo basado en extensión"""
   return '.' in arg and not arg.startswith('.')

def get_technology_coordinator(file_path):
   """Detecta tecnología y retorna coordinador apropiado usando CoordinatorRouter"""
   try:
       # Usar el nuevo CoordinatorRouter para detección automática
       router = CoordinatorRouter()
       coordinator = router.get_coordinator(file_path)
       
       # Detectar tecnología específica para logging
       technology = router._detect_file_technology(file_path, router._find_project_root(file_path))
       
       return coordinator, technology
   except Exception as e:
       console.print(f"[yellow]Warning: Error en CoordinatorRouter, usando coordinador fallback: {e}[/yellow]")
       from coordinators.replace import ReplaceCoordinator
       return ReplaceCoordinator(), 'fallback'

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
from functions.visualization.diff_visualizer import DiffVisualizer
from functions.interaction.interactive_confirm import InteractiveConfirm

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

def preview_replacement(filepath, pattern, replacement, matcher_options, dry_run=False):
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
   """Muestra diferencias entre contenido original y nuevo usando DiffVisualizer"""
   diff_visualizer = DiffVisualizer(console)
   diff_visualizer.display_preview(filepath, original, new)
   diff_visualizer.show_summary(filepath, original, new)

# ========================
# CLI PRINCIPAL
# ========================

@click.group()
@click.version_option(version="6.0-UX-Complete-With-Preview")
@click.option("--verbose", "-v", is_flag=True, help="Modo verbose")
@click.option("--dry-run", is_flag=True, help="Simular sin ejecutar")
def main(verbose, dry_run):
   """Surgical Modifier v6.0 - Sistema Multi-Tecnología (Python + TypeScript + React)."""
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
@click.option("--from-stdin", is_flag=True, help="Leer contenido complejo desde stdin (ideal para código con f-strings, comillas anidadas, o contenido multilínea)")
def create(filepath, content, template, from_stdin):
   """Crear archivos con contenido directo, templates o stdin (--from-stdin para código complejo).
    
    EJEMPLOS:
    • Básico: python3 cli.py create file.py "print('hello')"  
    • Complejo: echo "código multilínea" | python3 cli.py create file.py --from-stdin
    • Template: python3 cli.py create --template class.py User.py
    """
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
           
       # Usar CreateCoordinator apropiadamente
       from coordinators.create import CreateCoordinator
       coordinator = CreateCoordinator()
       
       # Ejecutar usando coordinador con soporte para templates
       result = coordinator.execute(
           file_path=filepath,
           content=content if content else None,
           template=template
       )
       
       if result.get('success'):
           return
       else:
           click.echo(f"Error: {result.get('error', 'Error desconocido')}", err=True)
           return 1
       
       # CÓDIGO ORIGINAL (FALLBACK - NO DEBERÍA EJECUTARSE):
       with open(filepath, 'w', encoding='utf-8') as f:
           f.write(content)
           
       click.echo(f"✅ Archivo {filepath} creado exitosamente")
       
   except Exception as e:
       click.echo(f"Error creando archivo: {e}", err=True)

# ========================
# COMANDO REPLACE (CON MEJORAS UX COMPLETAS + PREVIEW + ROLLBACK + ANÁLISIS ESTRUCTURAL + DRY-RUN)
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
@click.option("--dry-run", is_flag=True, help="Mostrar preview de cambios sin aplicar - modo simulación")
@click.option("--interactive", is_flag=True, help="Confirmación interactiva para cada cambio")
@click.option("--force", is_flag=True, help="Forzar reemplazo incluso si la validación JS/TS falla")
@click.option('--verbose', is_flag=True, help='Mostrar información detallada de errores')
@click.option('--structural-analysis', is_flag=True, default=True, help='Ejecutar análisis estructural preventivo (por defecto: activado)')
@click.option('--skip-structural-analysis', is_flag=True, default=False, help='Omitir análisis estructural preventivo')
def replace(filepath, pattern, replacement, fuzzy=False, regex=False, threshold=0.8, strict_syntax=False, preview=False, dry_run=False, interactive=False, force=False, verbose=False, structural_analysis=True, skip_structural_analysis=False):
   """
   Reemplazar contenido en archivos usando ReplaceCoordinator.
   
   MEJORAS UX v6.0 - Soporta ambas sintaxis:
   - Tradicional: python3 cli.py replace archivo.txt 'viejo' 'nuevo'
   - Intuitiva:   python3 cli.py replace 'viejo' 'nuevo' archivo.txt
   
   Opciones avanzadas:
   --strict-syntax : Solo acepta orden tradicional (archivo pattern replacement)
   --preview       : Mostrar preview antes de aplicar cambios
   --dry-run       : Mostrar preview sin aplicar cambios (modo simulación)
   --interactive   : Confirmación interactiva para cada cambio
   --force         : Saltear validación JS/TS si es necesario
   --structural-analysis : Análisis estructural preventivo (por defecto)
   --skip-structural-analysis : Omitir análisis estructural
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
       # Propagar parámetros al coordinador/workflow
       matcher_options['force'] = force
       matcher_options['verbose'] = verbose
       matcher_options['skip_structural_analysis'] = skip_structural_analysis or not structural_analysis

       # NUEVA FUNCIONALIDAD: Modo dry-run
       if dry_run:
           console.print("[bold blue]🔍 MODO DRY-RUN ACTIVADO - Solo mostrando preview[/bold blue]")
           preview_result = preview_replacement(filepath, pattern, replacement, matcher_options, dry_run=True)
           
           if not preview_result['success']:
               click.echo(f"❌ Error en preview: {preview_result['error']}", err=True)
               return 1
           
           # Mostrar preview usando DiffVisualizer
           if preview_result['matches_count'] > 0:
               show_preview_diff(preview_result['original_content'], preview_result['new_content'], filepath)
               console.print(f"[green]📊 Coincidencias que se reemplazarían: {preview_result['matches_count']}[/green]")
               
               # Mostrar validación JS/TS si aplica
               validation = preview_result['validation']
               if not validation['valid']:
                   console.print("[yellow]⚠️ ADVERTENCIA: El reemplazo resultaría en sintaxis JS/TS inválida:[/yellow]")
                   for error in validation['errors']:
                       console.print(f"  - [red]{error}[/red]")
               else:
                   console.print("[green]✅ Validación JS/TS: Sintaxis válida[/green]")
           else:
               console.print("[yellow]ℹ️ No se encontraron coincidencias para reemplazar[/yellow]")
           
           console.print("[blue]💡 Para aplicar los cambios, ejecute el comando sin --dry-run[/blue]")
           return 0

       # NUEVA FUNCIONALIDAD: Modo preview (con posible aplicación)
       if preview or interactive:
           preview_result = preview_replacement(filepath, pattern, replacement, matcher_options)
           
           if not preview_result['success']:
               click.echo(f"❌ Error en preview: {preview_result['error']}", err=True)
               return 1
           
           # Mostrar preview usando DiffVisualizer
           if preview_result['matches_count'] > 0:
               show_preview_diff(preview_result['original_content'], preview_result['new_content'], filepath)
               
               # Mostrar validación JS/TS si aplica
               validation = preview_result['validation']
               if not validation['valid']:
                   console.print("[yellow]⚠️ ADVERTENCIA: El reemplazo resultaría en sintaxis JS/TS inválida:[/yellow]")
                   for error in validation['errors']:
                       console.print(f"  - [red]{error}[/red]")
                   if not force:
                       console.print("[blue]💡 Usa --force para aplicar de todas formas[/blue]")
               else:
                   console.print("[green]✅ Validación JS/TS: Sintaxis válida[/green]")
               
               # Confirmación interactiva
               if interactive:
                   interactive_confirm = InteractiveConfirm(console)
                   interactive_confirm.show_summary(filepath, preview_result['original_content'], 
                                                  preview_result['new_content'], preview_result['matches_count'])
                   
                   choice = interactive_confirm.prompt_user(filepath, f"Reemplazar '{pattern}' con '{replacement}'")
                   if choice in ['no', 'quit']:
                       console.print("[yellow]Operación cancelada[/yellow]")
                       return 0
               elif preview:
                   # Pedir confirmación simple
                   if not click.confirm("¿Aplicar estos cambios?"):
                       click.echo("Operación cancelada")
                       return 0
           else:
               console.print("[yellow]ℹ️ No se encontraron coincidencias para reemplazar[/yellow]")
               return 0

       # MEJORA v6.0: Detección automática de tecnología
       # Para operaciones replace, usar ReplaceCoordinator directamente
       from coordinators.replace import ReplaceCoordinator
       coordinator = ReplaceCoordinator()
       detected_tech = 'replace_operation'
       if verbose:
           console.print(f"[blue]🔍 Tecnología detectada: {detected_tech}[/blue]")
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
           
           # Mostrar información de análisis estructural si está disponible
           if result.get('structural_analysis'):
               analysis = result['structural_analysis']
               if analysis.get('warnings', 0) > 0:
                   console.print(f"⚠️ Advertencias estructurales: {analysis['warnings']}", style="yellow")
               if analysis.get('critical_issues', 0) > 0:
                   console.print(f"🚨 Problemas críticos detectados: {analysis['critical_issues']}", style="red")
       else:
           click.echo(f"❌ Error: {result.get('error', 'Unknown error')}", err=True)
           
           # Si hay problemas estructurales, mostrar detalles
           if result.get('structural_analysis'):
               analysis = result['structural_analysis']
               console.print("🔍 Problemas estructurales detectados:", style="yellow")
               for detail in analysis.get('details', []):
                   console.print(f"  - {detail['type']}: {detail['message']}", style="red")
           
           return 1

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
   print("  replace     : Reemplazar contenido (🎯 CON MEJORAS UX + PREVIEW + DRY-RUN)")
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
   print("  ✅ MODO DRY-RUN (solo mostrar cambios):")
   print("    python3 cli.py replace --dry-run archivo.js 'old' 'new'")
   print("  ✅ MODO INTERACTIVO:")
   print("    python3 cli.py replace --interactive archivo.js 'old' 'new'")
   print("  ✅ ANÁLISIS ESTRUCTURAL PREVENTIVO:")
   print("    python3 cli.py replace --structural-analysis archivo.ts 'old' 'new'")
   print("  ✅ OMITIR ANÁLISIS ESTRUCTURAL:")
   print("    python3 cli.py replace --skip-structural-analysis archivo.js 'old' 'new'")
   print("  ✅ VALIDACIÓN JS/TS AUTOMÁTICA con rollback")
   print("  ✅ MODO FORCE para saltear validación:")
   print("    python3 cli.py replace --force archivo.tsx 'old' 'new'")
   print("  ✅ SUGERENCIAS AUTOMÁTICAS cuando hay errores de orden")
   print("  ✅ MENSAJES DE ERROR informativos con ejemplos")
   print()
   print("EJEMPLOS PRÁCTICOS:")
   print("  python3 cli.py replace --dry-run 'old_function' 'new_function' main.js")
   print("  python3 cli.py replace --preview --interactive 'old' 'new' app.py")
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
   print("2. SISTEMA DE PREVIEW/DRY-RUN:")
   print("   --preview : Muestra cambios antes de aplicar con confirmación")
   print("   --dry-run : Solo muestra cambios sin aplicar (modo simulación)")
   print("   --interactive : Confirmación paso a paso con opciones y/a/n")
   print("   Incluye validación JS/TS automática y diff visual colorido")
   print()
   print("3. ANÁLISIS ESTRUCTURAL PREVENTIVO:")
   print("   --structural-analysis : Detecta problemas antes de modificar (por defecto)")
   print("   --skip-structural-analysis : Omite análisis para casos especiales")
   print("   Detecta: interfaces duplicadas, referencias circulares, sintaxis rota")
   print()
   print("4. VALIDACIÓN JS/TS AUTOMÁTICA:")
   print("   Detecta automáticamente archivos .js/.jsx/.ts/.tsx")
   print("   Valida sintaxis después de modificaciones")
   print("   Rollback automático si detecta errores")
   print()
   print("5. MODO FORCE:")
   print("   --force : Saltear validación JS/TS si es necesario")
   print("   Útil para casos especiales")
   print()
   print("6. MODO STRICT-SYNTAX:")
   print("   --strict-syntax : Solo acepta orden tradicional")
   print("   Útil para scripts automatizados")
   print()
   print("7. SUGERENCIAS INTELIGENTES:")
   print("   Cuando detecta posible confusión de orden, sugiere corrección")
   print("   Ejemplo: '💡 Did you mean: python3 cli.py replace ...'")
   print()
   print("8. MENSAJES DE ERROR MEJORADOS:")
   print("   Incluyen ejemplos de sintaxis correcta")
   print("   Reducen tiempo de debugging")
   print()
   print("9. COMPATIBILIDAD TOTAL:")
   print("   Todo código existente sigue funcionando")
   print("   Cero regresiones, solo mejoras")

# ========================
# COMANDOS BATCH Y TRANSACTION
# ========================

@main.command("batch")
@click.option("--file", "-f", required=True, help="Archivo de comandos batch (JSON/YAML)")
@click.option("--dry-run", is_flag=True, help="Simular sin ejecutar")
def batch_command(file, dry_run):
   """Ejecutar múltiples operaciones desde archivo de comandos"""
   from coordinators.batch import BatchCoordinator
   
   coordinator = BatchCoordinator()
   
   try:
       result = coordinator.execute(file, dry_run=dry_run)
       
       if result["success"]:
           console.print(f"[green]✅ Batch ejecutado exitosamente[/green]")
           console.print(f"Operaciones ejecutadas: {result['operations_executed']}")
           console.print(f"Operaciones fallidas: {result['operations_failed']}")
           
           for detail in result["details"]:
               status_color = "green" if detail["status"] == "success" else "red"
               console.print(f"  [{status_color}]Op {detail['operation']}: {detail['status']}[/{status_color}]")
       else:
           console.print(f"[red]❌ Error en batch: {result.get('error', 'Unknown error')}[/red]")
           
   except Exception as e:
       console.print(f"[red]❌ Error ejecutando batch: {str(e)}[/red]")

@main.command('config-detect')
@click.option('--detailed', '-d', is_flag=True, help='Mostrar análisis detallado')
@click.option('--json-output', '-j', is_flag=True, help='Salida en formato JSON')
@click.option('--suggestions', '-s', is_flag=True, help='Mostrar sugerencias de mejora')
@click.argument('project-path', default='.', type=click.Path(exists=True))
def config_detect_command(detailed, json_output, suggestions, project_path):
    """Detectar y mostrar configuración automática del proyecto"""
    import json
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.tree import Tree
    from config import detect_project_config
    
    console = Console()
    
    try:
        # Detectar configuración del proyecto
        with console.status('[bold green]Analizando proyecto...'):
            result = detect_project_config(project_path)
        
        if not result.get('detected'):
            console.print('[red]❌ No se pudo detectar configuración del proyecto[/red]')
            if 'error' in result:
                console.print(f'[red]Error: {result["error"]}[/red]')
            return
        
        config = result.get('config', {})
        raw_analysis = result.get('raw_analysis', {})
        
        # Salida JSON si se solicita
        if json_output:
            console.print(json.dumps(result, indent=2, default=str))
            return
        
        # Mostrar resumen principal
        project_type = config.get('project_type', 'unknown')
        console.print(Panel(
            f'[bold cyan]Proyecto detectado:[/bold cyan] {project_type}\n'
            f'[bold cyan]Ruta:[/bold cyan] {project_path}',
            title='🎯 Configuración Detectada',
            border_style='cyan'
        ))
        
        # Tabla de tecnologías
        tech_stack = config.get('technology_stack', {})
        if tech_stack:
            table = Table(title='🛠️ Stack Tecnológico')
            table.add_column('Categoría', style='cyan')
            table.add_column('Tecnologías', style='green')
            
            frameworks = tech_stack.get('frameworks', [])
            if frameworks:
                table.add_row('Frameworks', ', '.join(frameworks))
            
            build_tools = tech_stack.get('build_tools', [])
            if build_tools:
                table.add_row('Build Tools', ', '.join(build_tools))
            
            testing = tech_stack.get('testing', [])
            if testing:
                table.add_row('Testing', ', '.join(testing))
            
            ui_libs = tech_stack.get('ui_libraries', [])
            if ui_libs:
                table.add_row('UI Libraries', ', '.join(ui_libs))
            
            if tech_stack.get('is_typescript'):
                table.add_row('TypeScript', '✅ Detectado')
            
            console.print(table)
        
        # Configuración de alias
        alias_config = config.get('alias_configuration', {})
        total_aliases = alias_config.get('total_aliases', 0)
        if total_aliases > 0:
            common_aliases = alias_config.get('common_aliases', [])
            aliases_text = ', '.join(common_aliases) if common_aliases else 'Ninguno'
            console.print(Panel(
                f'[bold yellow]Total alias:[/bold yellow] {total_aliases}\n'
                f'[bold yellow]Alias comunes:[/bold yellow] {aliases_text}',
                title='📂 Configuración de Alias',
                border_style='yellow'
            ))
        
        # Configuración de build
        build_config = config.get('build_configuration', {})
        if build_config:
            primary_tool = build_config.get('primary_build_tool', 'No detectada')
            has_dev = '✅' if build_config.get('has_dev_script') else '❌'
            has_build = '✅' if build_config.get('has_build_script') else '❌'
            console.print(Panel(
                f'[bold magenta]Herramienta principal:[/bold magenta] {primary_tool}\n'
                f'[bold magenta]Script dev:[/bold magenta] {has_dev}\n'
                f'[bold magenta]Script build:[/bold magenta] {has_build}',
                title='⚙️ Configuración de Build',
                border_style='magenta'
            ))
        
        # Mostrar análisis detallado si se solicita
        if detailed:
            console.print('\n[bold blue]📊 Análisis Detallado:[/bold blue]')
            
            # Archivos de configuración encontrados
            config_files = raw_analysis.get('config_files', {})
            config_files_found = config_files.get('config_files_found', [])
            if config_files_found:
                tree = Tree('📁 Archivos de Configuración')
                for file in config_files_found:
                    tree.add(f'✅ {file}')
                console.print(tree)
            
            # Estadísticas de dependencias
            deps = raw_analysis.get('dependencies', {})
            if deps and 'dependency_stats' in deps:
                stats = deps['dependency_stats']
                total_deps = stats.get('total_dependencies', 0)
                prod_deps = stats.get('production_dependencies', 0)
                dev_deps = stats.get('development_dependencies', 0)
                console.print(Panel(
                    f'[bold]Total dependencias:[/bold] {total_deps}\n'
                    f'[bold]Producción:[/bold] {prod_deps}\n'
                    f'[bold]Desarrollo:[/bold] {dev_deps}',
                    title='📦 Estadísticas de Dependencias',
                    border_style='blue'
                ))
        
        # Mostrar sugerencias si se solicita
        if suggestions:
            recommendations = config.get('recommended_settings', {})
            if recommendations:
                console.print('\n[bold green]💡 Configuraciones Recomendadas:[/bold green]')
                
                suggestions_table = Table()
                suggestions_table.add_column('Configuración', style='cyan')
                suggestions_table.add_column('Valor Recomendado', style='green')
                
                for key, value in recommendations.items():
                    if isinstance(value, list):
                        value = ', '.join(value)
                    elif isinstance(value, bool):
                        value = '✅' if value else '❌'
                    display_key = key.replace('_', ' ').title()
                    suggestions_table.add_row(display_key, str(value))
                
                console.print(suggestions_table)
            
            # Sugerencias de alias
            aliases = raw_analysis.get('aliases', {})
            alias_suggestions = aliases.get('suggestions', [])
            if alias_suggestions:
                console.print('\n[bold yellow]📂 Sugerencias de Alias:[/bold yellow]')
                for suggestion in alias_suggestions[:3]:  # Mostrar máximo 3
                    suggested_alias = suggestion.get('suggested_alias', '')
                    target_path = suggestion.get('target_path', '')
                    console.print(f'  • {suggested_alias} → {target_path}')
        
        console.print('\n[green]✅ Análisis de configuración completado[/green]')
        
    except Exception as e:
        console.print(f'[red]❌ Error durante el análisis: {str(e)}[/red]')
        if detailed:
            console.print(f'[red]Detalles del error: {repr(e)}[/red]')

@main.command("transaction")
@click.argument("operation")
@click.argument("args", nargs=-1)
@click.option("--rollback-on-error", is_flag=True, help="Rollback automático en caso de error")
def transaction_command(operation, args, rollback_on_error):
   """Ejecutar operación con soporte transaccional"""
   from functions.transaction.manager import TransactionManager
   
   tx_manager = TransactionManager()
   
   try:
       tx_id = tx_manager.begin_transaction()
       console.print(f"[blue]🔄 Transacción iniciada: {tx_id}[/blue]")
       
       console.print(f"[yellow]🔍 Simulando: {operation} con argumentos {args}[/yellow]")
       
       result = tx_manager.commit()
       console.print(f"[green]✅ Transacción confirmada: {result['transaction_id']}[/green]")
       
   except Exception as e:
       console.print(f"[red]❌ Error en transacción: {str(e)}[/red]")
       if rollback_on_error:
           rollback_result = tx_manager.rollback()
           console.print(f"[blue]🔄 Rollback ejecutado: {rollback_result['transaction_id']}[/blue]")
       else:
           console.print("[yellow]⚠️ Use --rollback-on-error para rollback automático[/yellow]")

# ========================
# COMANDO DETECT-TECH
# ========================

@main.command("detect-tech")
@click.argument('filepath')
def detect_tech(filepath):
    """Detectar tecnología y coordinador que se usará para el archivo"""
    try:
        from coordinators.coordinator_router import CoordinatorRouter
        router = CoordinatorRouter()
        coordinator = router.get_coordinator(filepath)
        coordinator_name = type(coordinator).__name__
        
        # Mapeo de coordinadores a tecnologías
        tech_mapping = {
            'CreateCoordinator': 'Python',
            'TypeScriptCoordinator': 'TypeScript', 
            'ReactCoordinator': 'React (TypeScript + JSX)',
            'TypeScriptReactCoordinator': 'React (TypeScript + JSX)'
        }
        
        technology = tech_mapping.get(coordinator_name, 'Unknown')
        
        click.echo(f"📁 Archivo: {filepath}")
        click.echo(f"🔍 Tecnología detectada: {technology}")
        click.echo(f"⚙️  Coordinador asignado: {coordinator_name}")
        click.echo(f"📍 Ubicación: {coordinator.__class__.__module__}")
        
        # Mostrar comandos disponibles
        click.echo(f"\n🛠️  Comandos disponibles:")
        click.echo(f"   python cli.py create {filepath} 'content'")
        click.echo(f"   python cli.py replace {filepath} 'old' 'new'")
        click.echo(f"   python cli.py before {filepath} 'pattern' 'content'")
        click.echo(f"   python cli.py after {filepath} 'pattern' 'content'")
        click.echo(f"   python cli.py append {filepath} 'content'")
        
    except Exception as e:
        click.echo(f"❌ Error detectando tecnología: {e}")

# ========================
# ENTRY POINT
# ========================

if __name__ == "__main__":
   main()