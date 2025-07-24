"""
Models package - Auto-imports all models for SQLAlchemy discovery.

This module automatically imports all models in the package to ensure
they are registered with SQLAlchemy's Base.metadata for Alembic detection.
"""

import pkgutil
import importlib
from typing import List

# Import base model first
from .base import BaseModel

# Auto-import all model modules
def _import_all_models() -> List[str]:
    """Import all model modules in this package."""
    imported = []
    current_module = __name__

    for importer, modname, ispkg in pkgutil.iter_modules(__path__, current_module + '.'):
        # Skip base module (already imported) and non-model files
        if modname.endswith('.base') or 'base' in modname.split('.')[-1]:
            continue

        try:
            importlib.import_module(modname)
            imported.append(modname.split('.')[-1])
        except ImportError:
            pass  # Skip modules that can't be imported

    return imported

# Execute auto-import
_imported_models = _import_all_models()

# Create __all__ list with all available models
__all__ = ['BaseModel'] + _imported_models

# Import specific models that were auto-discovered
from .base import BaseModel

# Import user model explicitly (if it exists)
try:
    from .user import User
    __all__.append('User')
except ImportError:
    pass