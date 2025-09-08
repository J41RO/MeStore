"""Clase base para todos los coordinadores."""


class BaseCoordinator:
    """Clase base que define la interfaz común para todos los coordinadores."""

    def __init__(self):
        """Inicializar coordinador base."""
        pass

    def execute(self):
        """Ejecutar la operación del coordinador."""
        raise NotImplementedError("Subclases deben implementar execute()")
