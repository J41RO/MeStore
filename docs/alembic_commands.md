# Comandos Alembic para MeStore

## Configuración Completada

✅ **Alembic configurado con:**
- Soporte async completo
- Auto-generación habilitada
- File template con timestamps
- DATABASE_URL desde variables de entorno
- Funciones de comparación personalizadas

## Comandos Principales

### Estado de Migraciones
```bash
# Ver migración actual
alembic current

# Verificar configuración
alembic check

# Ver historial de migraciones
alembic history
Crear Migraciones
bash# Auto-generar migración basada en cambios en modelos
alembic revision --autogenerate -m "descripción_del_cambio"

# Crear migración vacía
alembic revision -m "descripción_del_cambio"
Aplicar Migraciones
bash# Aplicar todas las migraciones pendientes
alembic upgrade head

# Aplicar migración específica
alembic upgrade <revision_id>

# Revertir una migración
alembic downgrade -1
Comandos Avanzados
bash# Ver código SQL que se ejecutará (sin aplicar)
alembic upgrade head --sql

# Generar migración desde schema existente
alembic revision --autogenerate -m "initial_migration"
Características Configuradas
Auto-generación

✅ Detecta cambios en modelos automáticamente
✅ Compara tipos de columnas
✅ Detecta cambios en defaults de servidor
✅ Incluye todos los objetos por defecto

File Template

✅ Nombres con timestamp: YYYY_MM_DD_HHMM-revision_id_description.py
✅ Organización cronológica automática

Async Support

✅ Compatible con SQLAlchemy async
✅ Usa create_async_engine
✅ Manejo de errores robusto

Troubleshooting
Error: "Can't locate revision"
bash# Verificar estado de la base de datos
alembic current

# Si es necesario, sincronizar manualmente:
# (Ya resuelto en configuración actual)
Error: "greenlet_spawn not called"
bash# Verificar que env.py usa create_async_engine
# (Ya configurado correctamente)
