"""CLI principal con routing dinámico."""

import importlib
import sys
from pathlib import Path
from typing import Dict, List, Type

import click

from .base_coordinator import BaseCoordinator
from .config import DEFAULT_CONFIG
from .exceptions import SurgicalModifierError
from .logging_config import get_logger

logger = get_logger("cli")


class DynamicCLI:
    """Sistema CLI con detección automática de coordinadores."""
    
    def __init__(self):
        self.coordinators: Dict[str, Type[BaseCoordinator]] = {}
        self._discover_coordinators()
    
    def _discover_coordinators(self) -> None:
        """Descubrir automáticamente coordinadores disponibles."""
        coordinators_path = Path(__file__).parent.parent / "coordinators"
        
        if not coordinators_path.exists():
            logger.debug("Directorio coordinators no existe aún")
            return
        
        sys.path.insert(0, str(coordinators_path.parent))
        
        for file_path in coordinators_path.glob("*.py"):
            if file_path.name.startswith("_"):
                continue
                
            module_name = file_path.stem
            try:
                module = importlib.import_module(f"coordinators.{module_name}")
                
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        issubclass(attr, BaseCoordinator) and 
                        attr != BaseCoordinator):
                        self.coordinators[module_name] = attr
                        logger.debug(f"Coordinador descubierto: {module_name}")
            except ImportError as e:
                logger.warning(f"Error importando {module_name}: {e}")


dynamic_cli = DynamicCLI()


@click.group(invoke_without_command=True)
@click.option("--verbose", "-v", is_flag=True, help="Modo verbose")
@click.option("--dry-run", is_flag=True, help="Simular sin ejecutar")
@click.pass_context
def main(ctx, verbose, dry_run):
    """Surgical Modifier - Sistema de Modificación Precisa de Código."""
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["dry_run"] = dry_run
    
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@main.command("list-commands")
def list_commands():
    """Listar comandos disponibles dinámicamente."""
    click.echo("Comandos disponibles:")
    
    if dynamic_cli.coordinators:
        click.echo("\nCoordinadores:")
        for name in sorted(dynamic_cli.coordinators.keys()):
            click.echo(f"  {name:<15} - Coordinador {name.title()}")
    else:
        click.echo("  (No hay coordinadores implementados aún)")
    
    click.echo("\nComandos del sistema:")
    built_in = ["list-commands", "version"]
    for cmd in built_in:
        click.echo(f"  {cmd:<15} - Comando interno")


@main.command("version")
def version():
    """Mostrar versión del sistema."""
    click.echo(f"Surgical Modifier v{DEFAULT_CONFIG['version']}")
    click.echo(f"Coordinadores disponibles: {len(dynamic_cli.coordinators)}")


if __name__ == "__main__":
    main()
