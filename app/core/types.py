"""
Database-agnostic types for MeStore.

This module provides database types that work across different databases
(PostgreSQL, SQLite) to ensure compatibility in both production and testing.
"""

import uuid
from sqlalchemy import TypeDecorator, String
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy import create_engine


class UUID(TypeDecorator):
    """
    Cross-database UUID type that works with both PostgreSQL and SQLite.

    - In PostgreSQL: Uses native UUID type
    - In SQLite: Uses String(36) and handles UUID conversion
    """

    impl = String
    cache_ok = True

    def load_dialect_impl(self, dialect):
        """Load appropriate type based on database dialect."""
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PostgresUUID(as_uuid=True))
        else:
            # For SQLite and other databases, use String(36)
            return dialect.type_descriptor(String(36))

    def process_bind_param(self, value, dialect):
        """Process parameter when binding to database."""
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value  # PostgreSQL handles UUID objects natively
        else:
            # For SQLite, convert UUID to string
            if isinstance(value, uuid.UUID):
                return str(value)
            return str(value)

    def process_result_value(self, value, dialect):
        """Process value when retrieving from database."""
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value  # PostgreSQL returns UUID objects
        else:
            # For SQLite, convert string back to UUID
            if isinstance(value, str):
                return uuid.UUID(value)
            return value


def generate_uuid():
    """Generate a new UUID as string for use as default in models."""
    return str(uuid.uuid4())