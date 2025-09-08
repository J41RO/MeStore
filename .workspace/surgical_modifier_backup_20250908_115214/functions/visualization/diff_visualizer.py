import difflib
from typing import List, Tuple, Optional
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel
from rich.text import Text


class DiffVisualizer:
    """Visualizador de diffs con Rich Console para preview de cambios."""
    
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
    
    def generate_diff(self, before_content: str, after_content: str, 
                     filename: str = 'file') -> List[str]:
        """Genera diff usando difflib."""
        before_lines = before_content.splitlines(keepends=True)
        after_lines = after_content.splitlines(keepends=True)
        
        diff = list(difflib.unified_diff(
            before_lines, 
            after_lines, 
            fromfile=f'{filename} (before)',
            tofile=f'{filename} (after)',
            lineterm=''
        ))
        
        return diff
    
    def display_preview(self, filename: str, before_content: str, 
                       after_content: str, context_lines: int = 3) -> None:
        """Muestra preview colorido del diff."""
        
        # Generar diff
        diff_lines = self.generate_diff(before_content, after_content, filename)
        
        if not diff_lines:
            self.console.print('[green]✅ No hay cambios para mostrar[/green]')
            return
        
        # Título del preview
        title = f'[bold blue]📋 PREVIEW DE CAMBIOS: {filename}[/bold blue]'
        
        # Crear contenido del diff con colores
        diff_content = []
        for line in diff_lines:
            if line.startswith('+++') or line.startswith('---'):
                diff_content.append(f'[bold cyan]{line}[/bold cyan]')
            elif line.startswith('@@'):
                diff_content.append(f'[bold magenta]{line}[/bold magenta]')
            elif line.startswith('+') and not line.startswith('+++'):
                diff_content.append(f'[bold green]{line}[/bold green]')
            elif line.startswith('-') and not line.startswith('---'):
                diff_content.append(f'[bold red]{line}[/bold red]')
            else:
                diff_content.append(line)
        
        # Mostrar panel con diff
        diff_text = '\n'.join(diff_content)
        panel = Panel(
            diff_text,
            title=title,
            border_style='blue',
            expand=False
        )
        
        self.console.print(panel)
    
    def show_context(self, filename: str, before_content: str, 
                    after_content: str, line_number: int, 
                    context_lines: int = 3) -> None:
        """Muestra contexto alrededor de una línea específica."""
        
        before_lines = before_content.splitlines()
        after_lines = after_content.splitlines()
        
        start_line = max(0, line_number - context_lines)
        end_line = min(len(before_lines), line_number + context_lines + 1)
        
        self.console.print(f'\n[bold]📍 Contexto alrededor de línea {line_number}:[/bold]')
        
        # Mostrar líneas de contexto
        for i in range(start_line, end_line):
            if i < len(before_lines):
                prefix = '→' if i == line_number else ' '
                self.console.print(f'{prefix} {i+1:3d}: {before_lines[i]}')
    
    def show_summary(self, filename: str, before_content: str, 
                    after_content: str) -> None:
        """Muestra resumen de cambios."""
        
        before_lines = before_content.splitlines()
        after_lines = after_content.splitlines()
        
        # Calcular estadísticas
        lines_added = len(after_lines) - len(before_lines)
        
        diff_lines = self.generate_diff(before_content, after_content, filename)
        additions = len([line for line in diff_lines if line.startswith('+') and not line.startswith('+++')])
        deletions = len([line for line in diff_lines if line.startswith('-') and not line.startswith('---')])
        
        # Mostrar resumen
        summary_text = f'''
[bold]📊 RESUMEN DE CAMBIOS:[/bold]
- Archivo: {filename}
- Líneas agregadas: [green]+{additions}[/green]
- Líneas eliminadas: [red]-{deletions}[/red]
- Cambio neto: {lines_added:+d} líneas
        '''
        
        panel = Panel(
            summary_text.strip(),
            title='[bold yellow]📈 Estadísticas[/bold yellow]',
            border_style='yellow'
        )
        
        self.console.print(panel)
