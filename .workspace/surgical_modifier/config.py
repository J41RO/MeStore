import os
from pathlib import Path

# Configuración base
BASE_DIR = Path(__file__).parent
TEMP_DIR = BASE_DIR / "temp"
BACKUP_DIR = BASE_DIR / "backups"

# Configuración del surgical modifier
DEBUG = True
VERBOSE = True
SAFE_MODE = True

# Configuración de validación
SYNTAX_VALIDATION = True
DEPENDENCY_CHECK = True
AUTO_ROLLBACK = True

# Configuración de archivos
DEFAULT_ENCODING = "utf-8"
BACKUP_EXTENSION = ".backup"

# Configuración de operaciones
MAX_OPERATION_SIZE = 1000000  # 1MB
VERIFICATION_ENABLED = True

# Configuración de escape de caracteres
ESCAPE_SPECIAL_CHARS = True
BASH_SAFE_MODE = True

# Configuración TypeScript/React
TS_VALIDATION = True
INTERFACE_ORDER_CHECK = True
DEPENDENCY_RESOLUTION = True

# Configuración de la aplicación
DATABASE_URL = "postgresql://localhost/myapp"
