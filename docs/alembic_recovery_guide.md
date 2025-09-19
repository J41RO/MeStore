# 🔧 GUÍA DE RECUPERACIÓN DE ALEMBIC - MESTOCKER

## 🚨 PROBLEMA COMÚN: "Can't locate revision identified by 'XXXXXXXX'"

### ⚡ SOLUCIÓN RÁPIDA (2 minutos):

```bash
# 1. Usar el script de reparación
python3 fix_alembic_version.py

# 2. Verificar que funciona
alembic current

# 3. Ya puedes usar alembic normalmente
alembic revision --autogenerate -m "descripcion"
alembic upgrade head
📋 EXPLICACIÓN DEL PROBLEMA:

La tabla alembic_version en PostgreSQL contiene un ID de revisión que no existe en los archivos
Esto ocurre cuando se eliminan archivos de migración pero la BD mantiene referencias
El script fix_alembic_version.py corrige la BD al último estado válido conocido

🛠️ MÉTODO MANUAL (si el script no funciona):
python# Conectar a BD y corregir manualmente
from app.database.session import engine
from sqlalchemy import text
import asyncio

async def manual_fix():
    async with engine.begin() as conn:
        # Ver versión actual
        result = await conn.execute(text("SELECT version_num FROM alembic_version;"))
        print(f"Actual: {result.scalar()}")

        # Corregir a última válida (ver con: alembic history)
        await conn.execute(text("UPDATE alembic_version SET version_num = '5e0e1b1f0cfc';"))
        print("✅ Corregido")

asyncio.run(manual_fix())
📊 VERIFICACIONES POST-REPARACIÓN:
bash# Verificar estado
alembic current

# Verificar historial
alembic history

# Test de funcionalidad
alembic revision -m "test" --dry-run
🎯 PREVENCIÓN FUTURA:

NUNCA eliminar archivos de migración sin hacer alembic downgrade primero
SIEMPRE usar alembic stamp si necesitas sincronizar manualmente
BACKUP de tabla alembic_version antes de cambios: pg_dump -t alembic_version


Creado: $(date)
Última reparación exitosa: 5e0e1b1f0cfc → Agosto 2025
