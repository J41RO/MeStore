#!/usr/bin/env python3
"""CLI principal de Surgical Modifier."""

import click
import sys
import os
from pathlib import Path

# Agregar path para importar coordinadores
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))
from coordinators.replace import ReplaceCoordinator


@click.group()
@click.version_option(version="0.1.0")
@click.option("--verbose", "-v", is_flag=True, help="Modo verbose")
@click.option("--dry-run", is_flag=True, help="Simular sin ejecutar")
def main(verbose, dry_run):
    """Surgical Modifier - Sistema de Modificación Precisa de Código."""
    if verbose:
        print("Modo verbose activado")
    if dry_run:
        print("Modo dry-run activado")


@main.command()
@click.argument("filepath")
@click.option("--template", help="Tipo de template a usar")
def create(filepath, template):
    """Crear nuevos archivos con templates."""
    print(f"Creando {filepath} con template {template}")


@main.command()
@click.argument("filepath")
@click.argument("pattern")
@click.argument("replacement")
@click.option("--fuzzy", is_flag=True, help="Usar matching aproximado")
@click.option("--regex", is_flag=True, help="Usar patrones regex") 
@click.option("--threshold", type=float, default=0.8, help="Threshold fuzzy (0.0-1.0)")
def replace(filepath, pattern, replacement, fuzzy=False, regex=False, threshold=0.8):
    """Reemplazar contenido en archivos."""
    """Reemplazar contenido en archivos usando ReplaceCoordinator."""
    try:
        # Determinar tipo de matcher basado en opciones
        matcher_type = 'literal'  # default
        matcher_options = {}

        if fuzzy:
            matcher_type = 'fuzzy'
            matcher_options['threshold'] = threshold
        elif regex:
            matcher_type = 'regex'

        # Agregar matcher_type a matcher_options
        matcher_options['matcher_type'] = matcher_type

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
            return 1

    except Exception as e:
        click.echo(f"❌ Error inesperado: {str(e)}", err=True)
        return 1


@main.command()
@click.argument("filepath")
@click.argument("pattern")
@click.argument("content")
def before(filepath, pattern, content):
    """Insertar contenido antes de un patrón."""
    print(f"Insertando antes de '{pattern}' en {filepath}")


@main.command()
@click.argument("filepath")
@click.argument("pattern")
@click.argument("content")
def after(filepath, pattern, content):
    """Insertar contenido después de un patrón."""
    print(f"Insertando después de '{pattern}' en {filepath}")


@main.command()
@click.argument("path")
@click.option("--analyze", is_flag=True, help="Analizar estructura")
def explore(path, analyze):
    """Explorar y analizar estructura de código."""
    print(f"Explorando {path} (análisis: {analyze})")


@main.command("list-commands")
def list_commands():
    """Listar todos los comandos disponibles."""
    print("Comandos disponibles:")
    print("  - create")
    print("  - replace") 
    print("  - before")
    print("  - after")
    print("  - explore")
    print("  - list-commands")


if __name__ == "__main__":
    main()