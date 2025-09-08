#!/usr/bin/env python3
"""CLI principal de Surgical Modifier."""

import click


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
def replace(filepath, pattern, replacement):
    """Reemplazar contenido en archivos."""
    print(f"Reemplazando '{pattern}' por '{replacement}' en {filepath}")


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
