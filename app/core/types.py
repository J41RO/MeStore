"""
Database-agnostic types for MeStore.

This module provides database types that work across different databases
(PostgreSQL, SQLite) to ensure compatibility in both production and testing.
"""

import uuid
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy import create_engine


class UUID(PostgresUUID):
    """
    Cross-database UUID type that works with both PostgreSQL and SQLite.

    - In PostgreSQL: Uses native UUID type
    - In SQLite/other dialects: Stores as String(36) and converts automatically
    """

    cache_ok = True

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("as_uuid", True)
        super().__init__(*args, **kwargs)

    def load_dialect_impl(self, dialect):
        """Load appropriate type based on database dialect."""
        if dialect.name == 'postgresql':
            return super().load_dialect_impl(dialect)
        # For SQLite and other databases, use String(36)
        return dialect.type_descriptor(String(36))

    def bind_processor(self, dialect):
        """Return processor for binding parameters based on dialect."""
        if dialect.name == 'postgresql':
            base_processor = super().bind_processor(dialect)

            def process(value):
                if value is None:
                    return value
                processed = str(value)
                return base_processor(processed) if base_processor else processed

            return process

        string_processor = String(36).bind_processor(dialect)

        def process(value):
            if value is None:
                return value
            processed = str(value)
            return string_processor(processed) if string_processor else processed

        return process

    def result_processor(self, dialect, coltype):
        """Return processor for result values based on dialect."""
        if dialect.name == 'postgresql':
            return super().result_processor(dialect, coltype)

        string_processor = String(36).result_processor(dialect, coltype)

        def process(value):
            if string_processor:
                value = string_processor(value)
            if value is None:
                return None
            if isinstance(value, uuid.UUID):
                return str(value)
            return str(value)

        return process


def generate_uuid():
    """Generate a new UUID as string for use as default in models."""
    # Return canonical UUID string with hyphens for cross-system consistency
    return str(uuid.uuid4())
