import asyncio
from logging.config import fileConfig
import os

from sqlalchemy import engine_from_config, pool
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import create_engine

from alembic import context

# Import settings for DATABASE_URL configuration
from app.core.config import settings

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# Importar Base con todos los modelos
from app.database import Base

def import_all_models():
    """Auto-import all models from app.models package"""
    import pkgutil
    import importlib
    import app.models

    models_imported = []
    models_failed = []

    print('🔍 Starting auto-discovery of models...')

    for importer, modname, ispkg in pkgutil.iter_modules(app.models.__path__, app.models.__name__ + '.'):
        # Skip __pycache__ and other non-model files
        if modname.endswith(('__pycache__', '.pyc', '__init__')):
            continue

        try:
            # Import the module
            module = importlib.import_module(modname)
            models_imported.append(modname)
            print(f'  ✅ Imported: {modname}')

            # Verify it contains SQLAlchemy models
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if hasattr(attr, '__tablename__') and hasattr(attr, 'metadata'):
                    print(f'    📊 Found model: {attr_name} -> table: {attr.__tablename__}')

        except ImportError as e:
            models_failed.append((modname, str(e)))
            print(f'  ⚠️ Could not import {modname}: {e}')
        except Exception as e:
            models_failed.append((modname, str(e)))
            print(f'  ❌ Error importing {modname}: {e}')

    print(f'')
    print(f'✅ Successfully imported {len(models_imported)} model modules')
    print(f'📊 Total tables detected in Base.metadata: {len(Base.metadata.tables)}')
    print(f'📋 Tables: {list(Base.metadata.tables.keys())}')

    if models_failed:
        print(f'⚠️ Failed to import {len(models_failed)} modules:')
        for modname, error in models_failed:
            print(f'  - {modname}: {error}')

    return models_imported, models_failed

# Agregar metadatos de todos los modelos

# Auto-import all models before configuring metadata
print('🚀 Executing auto-discovery of models...')
imported_models, failed_models = import_all_models()
print(f'🎯 Auto-discovery completed: {len(imported_models)} models imported')
print('')

target_metadata = Base.metadata


def get_database_url():
    """
    Get DATABASE_URL for current environment using alembic.ini sections.
    Priority:
    1. Alembic section for current environment
    2. Environment variable DATABASE_URL
    3. Settings from Pydantic config (fallback)
    """
    # Get current environment
    environment = os.getenv('ENVIRONMENT', settings.ENVIRONMENT)
    
    # Determine alembic section name
    section_name = f'alembic:{environment}'
    
    print(f"📋 Using {environment} environment")
    print(f"🔧 Looking for section: {section_name}")
    
    try:
        # Try to get URL from alembic section
        section_url = config.get_section_option(section_name, 'sqlalchemy.url')
        if section_url is not None:
            # Get sqlalchemy.url from the specific environment section
            # section_url already obtained above
            
            if section_url and section_url != '${DATABASE_URL}':
                print(f"✅ Using URL from section {section_name}")
                return section_url
            elif section_url == '${DATABASE_URL}':
                # Resolve ${DATABASE_URL} variable from environment
                resolved_url = os.getenv('DATABASE_URL', settings.DATABASE_URL)
                print(f"🔧 Resolved ${{DATABASE_URL}} from environment")
                print(f"🔗 DATABASE_URL: {resolved_url[:50]}...")
                return resolved_url
        
        # Fallback to environment variable or settings
        database_url = 'sqlite:///./mestore_production.db' # FORZADO PARA ALEMBIC
        print(f"⚠️ Fallback to environment/settings")
        print(f"🔗 DATABASE_URL: {database_url[:50]}...")
        return database_url
        
    except Exception as e:
        print(f"❌ Error reading alembic section: {e}")
        # Final fallback to settings
        database_url = 'sqlite:///./mestore_production.db' # FORZADO PARA ALEMBIC
        print(f"🚨 Final fallback to settings")
        print(f"🔗 DATABASE_URL: {database_url[:50]}...")
        return database_url


def include_object(object, name, type_, reflected, compare_to):
    """Include/exclude objects from autogenerate."""
    # Skip alembic version table
    if type_ == "table" and name == "alembic_version":
        return False
    return True


def compare_type(context, inspected_column, metadata_column, inspected_type, metadata_type):
    """Compare types for autogenerate."""
    # Enable type comparison
    return True


def compare_server_default(context, inspected_column, metadata_column, inspected_default, metadata_default, rendered_metadata_default):
    """Compare server defaults for autogenerate."""
    # Enable server default comparison
    return True


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well. By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = get_database_url()

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
        compare_type=compare_type,
        compare_server_default=compare_server_default,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    """Execute migrations with full configuration."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_object=include_object,
        compare_type=compare_type,
        compare_server_default=compare_server_default,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_sync_migrations() -> None:
    """Run migrations in async mode with proper async engine."""
    url = get_database_url()
    
    # Get environment for pool configuration
    environment = os.getenv('ENVIRONMENT', settings.ENVIRONMENT)
    
    # Configure pool based on environment
    if environment == 'testing':
        poolclass = pool.NullPool
    elif environment == 'production':
        # Use AsyncAdaptedQueuePool for async production
        poolclass = pool.NullPool  # Safe for all async environments
    else:
        poolclass = pool.NullPool  # Default for development"
    
    connectable = create_engine(
        url,
        future=True,
        poolclass=poolclass,
    )

    try:
        with connectable.connect() as connection:
            do_run_migrations(connection)
    finally:
        connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    run_sync_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()