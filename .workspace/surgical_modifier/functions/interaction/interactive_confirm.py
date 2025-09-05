import sys
from typing import Optional, Literal, Dict, Any
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.text import Text


class InteractiveConfirm:
    """Maneja confirmaciones interactivas para operaciones de modificación."""
    
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.user_choice = None  # Para recordar 'apply all'
    
    def show_summary(self, filename: str, old_content: str, 
                    new_content: str, match_count: int = 1) -> None:
        """Muestra resumen de cambios propuestos."""
        
        old_lines = len(old_content.splitlines())
        new_lines = len(new_content.splitlines())
        line_diff = new_lines - old_lines
        
        summary_text = f'''
[bold]📋 RESUMEN DE OPERACIÓN:[/bold]
- Archivo: [cyan]{filename}[/cyan]
- Coincidencias encontradas: [yellow]{match_count}[/yellow]
- Líneas antes: {old_lines}
- Líneas después: {new_lines}
- Cambio neto: [{'green' if line_diff >= 0 else 'red'}]{line_diff:+d}[/] líneas
        '''
        
        panel = Panel(
            summary_text.strip(),
            title='[bold blue]📊 Información de Cambios[/bold blue]',
            border_style='blue'
        )
        
        self.console.print(panel)
    
    def prompt_user(self, filename: str, change_description: str = '') -> Literal['yes', 'no', 'all', 'quit']:
        """
        Solicita confirmación del usuario con opciones:
        - y/yes: Aplicar este cambio
        - a/all: Aplicar este y todos los siguientes
        - n/no: Saltar este cambio
        - q/quit: Cancelar operación completa
        """
        
        # Si ya eligió 'all', aplicar automáticamente
        if self.user_choice == 'all':
            self.console.print('[green]✅ Aplicando automáticamente (modo ALL activado)[/green]')
            return 'yes'
        
        # Mostrar prompt con opciones
        prompt_text = f'''
[bold yellow]❓ CONFIRMAR CAMBIO:[/bold yellow]
Archivo: [cyan]{filename}[/cyan]
{change_description}

[bold]Opciones:[/bold]
- [green]y[/green]/[green]yes[/green] - Aplicar este cambio
- [blue]a[/blue]/[blue]all[/blue] - Aplicar TODOS los cambios restantes
- [red]n[/red]/[red]no[/red] - Saltar este cambio
- [red]q[/red]/[red]quit[/red] - Cancelar operación completa
        '''
        
        self.console.print(Panel(prompt_text.strip(), border_style='yellow'))
        
        while True:
            try:
                response = Prompt.ask(
                    '[bold]¿Continuar?[/bold]',
                    choices=['y', 'yes', 'a', 'all', 'n', 'no', 'q', 'quit'],
                    default='y'
                ).lower()
                
                if response in ['y', 'yes']:
                    return 'yes'
                elif response in ['a', 'all']:
                    self.user_choice = 'all'  # Recordar para siguientes
                    self.console.print('[bold green]✅ Modo ALL activado - aplicando todos los cambios restantes[/bold green]')
                    return 'yes'
                elif response in ['n', 'no']:
                    return 'no'
                elif response in ['q', 'quit']:
                    return 'quit'
                    
            except KeyboardInterrupt:
                self.console.print('\n[red]❌ Operación cancelada por usuario[/red]')
                return 'quit'
            except EOFError:
                self.console.print('\n[red]❌ Input terminado, cancelando operación[/red]')
                return 'quit'
    
    def confirm_batch_operation(self, total_files: int, total_changes: int) -> bool:
        """Confirma operación en lote antes de ejecutar."""
        
        summary = f'''
[bold red]⚠️  OPERACIÓN EN LOTE:[/bold red]
- Archivos a modificar: [yellow]{total_files}[/yellow]
- Total de cambios: [yellow]{total_changes}[/yellow]

[bold]Esta operación modificará múltiples archivos.[/bold]
¿Está seguro de que desea continuar?
        '''
        
        panel = Panel(
            summary.strip(),
            title='[bold red]🚨 Confirmación Requerida[/bold red]',
            border_style='red'
        )
        
        self.console.print(panel)
        
        return Confirm.ask('[bold]¿Continuar con la operación?[/bold]', default=False)
    
    def show_operation_result(self, success: bool, files_modified: int, 
                            changes_applied: int, errors: Optional[Dict[str, str]] = None) -> None:
        """Muestra resultado final de la operación."""
        
        if success:
            result_text = f'''
[bold green]✅ OPERACIÓN COMPLETADA EXITOSAMENTE[/bold green]
- Archivos modificados: [green]{files_modified}[/green]
- Cambios aplicados: [green]{changes_applied}[/green]
            '''
            border_style = 'green'
            title = '[bold green]🎉 Éxito[/bold green]'
        else:
            error_count = len(errors) if errors else 0
            result_text = f'''
[bold red]❌ OPERACIÓN COMPLETADA CON ERRORES[/bold red]
- Archivos modificados: [yellow]{files_modified}[/yellow]
- Cambios aplicados: [yellow]{changes_applied}[/yellow]
- Errores encontrados: [red]{error_count}[/red]
            '''
            border_style = 'red'
            title = '[bold red]⚠️ Completado con Errores[/bold red]'
            
            if errors:
                result_text += '\n\n[bold]Errores:[/bold]'
                for file, error in errors.items():
                    result_text += f'\n• {file}: [red]{error}[/red]'
        
        panel = Panel(
            result_text.strip(),
            title=title,
            border_style=border_style
        )
        
        self.console.print(panel)
    
    def reset_user_choice(self) -> None:
        """Resetea la elección del usuario para nueva operación."""
        self.user_choice = None
