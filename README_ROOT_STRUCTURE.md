# 🧭 Estructura Limpia del Proyecto MeStore

Este archivo define las reglas para mantener la raíz del repositorio ordenada.

## 📂 Carpetas Principales

| Carpeta | Propósito |
|----------|------------|
| **app/** | Código fuente principal del backend. |
| **frontend/** | Proyecto del frontend (React / Vite). |
| **alembic/** | Migraciones de base de datos. |
| **scripts/** | Scripts de mantenimiento y utilidades. |
| **tests/** | Tests automatizados (unitarios, integraciones, e2e). |
| **reports/** | Reportes de test, coverage y logs. |
| **config/** | Archivos de configuración y entorno. |
| **data/** | Bases de datos locales o temporales. |
| **docs/** | Documentación general e inteligencia artificial. |
| **logs/** | Logs de ejecución y auditoría. |
| **uploads/** | Archivos subidos por el sistema. |
| **temp/** | Archivos temporales o transitorios. |

## 🧹 Buenas prácticas
1. No dejar archivos sueltos en la raíz salvo los esenciales (`Makefile`, `setup.py`, `pytest.ini`, etc.).
2. Toda base de datos o dump debe ir en `data/` o `reports/db/`.
3. No subir a Git carpetas `coverage/`, `htmlcov/`, ni bases `.db` de test.
4. Ejecutar periódicamente `make clean-project` (si existe) o limpiar manualmente los directorios de logs y reports antiguos.

**Última auditoría:** $(date +"%F %T")
