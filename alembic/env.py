import asyncio
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from sqlalchemy.ext.asyncio import create_async_engine

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
from app.core.database import Base
from app.models import user  # Asegurar que todos los modelos se importen

target_metadata = Base.metadata

# Configure autogenerate options
def include_object(object, name, type_, reflected, compare_to):
    """Configure which objects to include in autogenerate."""
    # Include all tables by default
    return True

def compare_type(context, inspected_column, metadata_column, inspected_type, metadata_type):
    """Compare column types for autogenerate."""
    # Enable type comparison for better autogeneration
    return True

def compare_server_default(context, inspected_column, metadata_column, inspected_default, metadata_default, rendered_metadata_default):
    """Compare server defaults for autogenerate."""
    # Enable server default comparison
    return True

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well. By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    # Use settings directly from config
    url = settings.DATABASE_URL
    
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
        render_as_batch=True,  # Support for SQLite and other databases
    )
    
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in async mode with proper async engine."""
    # Create async engine directly with settings
    connectable = create_async_engine(
        settings.DATABASE_URL,
        future=True,
        poolclass=pool.NullPool,
    )
    
    try:
        async with connectable.connect() as connection:
            await connection.run_sync(do_run_migrations)
    except Exception as e:
        print(f"❌ ERROR in async migrations: {e}")
        raise
    finally:
        await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode using async.

    This is the main entry point for online migrations.
    We use async operations for better performance.
    """
    asyncio.run(run_async_migrations())


# Main execution logic
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
