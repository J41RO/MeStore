"""
Models package - Auto-imports all models for SQLAlchemy discovery.

This module automatically imports all models in the package to ensure
they are registered with SQLAlchemy's Base.metadata for Alembic detection.
"""

import importlib
import pkgutil
from typing import List

# Import base model first
from .base import BaseModel
from .inventory import Inventory
from .product import Product
from .storage import Storage
from .transaction import Transaction
from .user import User


# Auto-import all model modules
def _import_all_models() -> List[str]:
    """Import all model modules in this package."""
    imported = []
    current_module = __name__

    for importer, modname, ispkg in pkgutil.iter_modules(
        __path__, current_module + "."
    ):
        # Skip base module (already imported) and non-model files
        if modname.endswith(".base") or "base" in modname.split(".")[-1]:
            continue

        try:
            importlib.import_module(modname)
            imported.append(modname.split(".")[-1])
        except ImportError:
            pass  # Skip modules that can't be imported

    return imported


# Execute auto-import
_imported_models = _import_all_models()

# Create __all__ list with all available models
__all__ = ["BaseModel"] + _imported_models

# Import specific models that were auto-discovered
from .base import BaseModel

# Import user model explicitly (if it exists)
try:
    from .user import User

    __all__.append("User")
except ImportError:
    pass

# Import incoming product queue model explicitly
try:
    from .incoming_product_queue import IncomingProductQueue, QueuePriority, VerificationStatus, DelayReason
    
    __all__.extend(["IncomingProductQueue", "QueuePriority", "VerificationStatus", "DelayReason"])
except ImportError:
    pass

# Import incident inventory model explicitly
try:
    from .incidente_inventario import IncidenteInventario, TipoIncidente, EstadoIncidente
    
    __all__.extend(["IncidenteInventario", "TipoIncidente", "EstadoIncidente"])
except ImportError:
    pass

# Import storage model explicitly (if it exists)
try:
    from .storage import Storage

    __all__.append("Storage")
except ImportError:
    pass

from .storage import Storage, StorageType

# Import vendor note and audit models explicitly
try:
    from .vendor_note import VendorNote
    __all__.append("VendorNote")
except ImportError:
    pass

try:
    from .vendor_audit import VendorAuditLog, ActionType
    __all__.extend(["VendorAuditLog", "ActionType"])
except ImportError:
    pass

try:
    from .vendor_document import VendorDocument, DocumentType, DocumentStatus
    __all__.extend(["VendorDocument", "DocumentType", "DocumentStatus"])
except ImportError:
    pass

# Agregar a __all__
"StorageType"