"""CLI principal de Surgical Modifier."""

import click


@click.group()
@click.version_option(version="0.1.0")
def main():
    """Surgical Modifier - Sistema de Modificación Precisa de Código."""
    pass


if __name__ == "__main__":
    main()
