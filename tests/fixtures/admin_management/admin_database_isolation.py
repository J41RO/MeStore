"""
Advanced Database Test Isolation Strategy for Admin Management

Este módulo implementa estrategias avanzadas de aislamiento de base de datos
específicamente diseñadas para testing del sistema de administración con
transacciones complejas, rollback automático, y limpieza garantizada.

Autor: Backend Framework AI
Fecha: 2025-09-21
Framework: SQLAlchemy + pytest + FastAPI
Objetivo: Aislamiento perfecto entre tests de admin management
"""

import asyncio
import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict, List, Any, Optional, Type
from dataclasses import dataclass
from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine, text, event
from sqlalchemy.ext.asyncio import (
    AsyncSession, AsyncEngine, async_sessionmaker,
    create_async_engine, AsyncConnection
)
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.sql import func

from app.database import Base
from app.models.user import User, UserType
from app.models.admin_permission import AdminPermission, admin_user_permissions
from app.models.admin_activity_log import AdminActivityLog


# ================================================================================================
# ISOLATION STRATEGY CONFIGURATION
# ================================================================================================

@dataclass
class AdminDatabaseIsolationConfig:
    """Configuration for database isolation strategies."""

    # Engine Configuration
    engine_url: str = "sqlite+aiosqlite:///:memory:"
    engine_echo: bool = False
    engine_pool_pre_ping: bool = True

    # Transaction Configuration
    auto_rollback: bool = True
    nested_transactions: bool = True
    savepoint_strategy: bool = True

    # Cleanup Configuration
    table_cleanup_order: List[str] = None
    foreign_key_checks: bool = False
    cascade_deletes: bool = True

    # Performance Configuration
    connection_pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: int = 30

    def __post_init__(self):
        if self.table_cleanup_order is None:
            # Define cleanup order based on foreign key dependencies
            self.table_cleanup_order = [
                "admin_activity_logs",       # No dependencies
                "admin_user_permissions",    # References users and permissions
                "admin_permissions",         # No dependencies
                "users"                      # Primary entity
            ]


# ================================================================================================
# ADVANCED ISOLATION ENGINE
# ================================================================================================

class AdminDatabaseIsolationEngine:
    """
    Advanced database isolation engine for admin management testing.

    Features:
    - Multi-level transaction isolation
    - Automatic rollback on test completion
    - Savepoint management for nested operations
    - Table-specific cleanup strategies
    - Foreign key constraint handling
    """

    def __init__(self, config: AdminDatabaseIsolationConfig = None):
        self.config = config or AdminDatabaseIsolationConfig()
        self._engines: Dict[str, AsyncEngine] = {}
        self._sessions: Dict[str, async_sessionmaker] = {}
        self._active_connections: Dict[str, AsyncConnection] = {}

    async def create_isolated_engine(self, test_id: str = None) -> AsyncEngine:
        """Create an isolated database engine for a specific test."""

        if test_id is None:
            test_id = f"test_{uuid.uuid4().hex[:8]}"

        # Create unique engine for this test
        engine = create_async_engine(
            self.config.engine_url,
            echo=self.config.engine_echo,
            pool_pre_ping=self.config.engine_pool_pre_ping,
            poolclass=StaticPool,
            connect_args={"check_same_thread": False}
        )

        self._engines[test_id] = engine

        # Create session maker
        session_maker = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

        self._sessions[test_id] = session_maker

        return engine

    async def initialize_schema(self, engine: AsyncEngine) -> None:
        """Initialize database schema with all required tables."""

        async with engine.begin() as conn:
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)

            # Enable foreign key constraints for SQLite
            if "sqlite" in str(engine.url):
                await conn.execute(text("PRAGMA foreign_keys=ON"))

    async def create_isolated_session(self, test_id: str) -> AsyncSession:
        """Create an isolated session with transaction management."""

        if test_id not in self._sessions:
            await self.create_isolated_engine(test_id)

        session_maker = self._sessions[test_id]
        session = session_maker()

        return session

    @asynccontextmanager
    async def isolated_transaction_context(self, test_id: str) -> AsyncGenerator[AsyncSession, None]:
        """
        Context manager for isolated transactions with automatic rollback.

        Features:
        - Automatic transaction start
        - Guaranteed rollback on exit
        - Exception handling
        - Resource cleanup
        """

        session = await self.create_isolated_session(test_id)

        # Begin transaction
        trans = await session.begin()

        try:
            yield session
        except Exception as e:
            # Rollback on any exception
            await trans.rollback()
            raise
        finally:
            # Always rollback to maintain isolation
            if trans.is_active:
                await trans.rollback()
            await session.close()

    @asynccontextmanager
    async def nested_savepoint_context(self, session: AsyncSession, savepoint_name: str = None) -> AsyncGenerator[AsyncSession, None]:
        """
        Context manager for nested savepoints within transactions.

        Allows for nested test operations with individual rollback capability.
        """

        if savepoint_name is None:
            savepoint_name = f"sp_{uuid.uuid4().hex[:8]}"

        # Create savepoint
        savepoint = await session.begin_nested()

        try:
            yield session
        except Exception as e:
            # Rollback to savepoint
            await savepoint.rollback()
            raise
        else:
            # Commit savepoint if no exceptions
            await savepoint.commit()

    async def cleanup_test_data(self, session: AsyncSession, selective: bool = False) -> None:
        """
        Clean up test data with proper foreign key handling.

        Args:
            session: Database session
            selective: If True, only clean admin-related tables
        """

        # Disable foreign key checks temporarily
        if "sqlite" in str(session.bind.url):
            await session.execute(text("PRAGMA foreign_keys=OFF"))

        try:
            if selective:
                # Clean only admin-related tables
                cleanup_tables = [
                    "admin_activity_logs",
                    "admin_user_permissions",
                    "admin_permissions"
                ]
            else:
                cleanup_tables = self.config.table_cleanup_order

            # Clean tables in reverse dependency order
            for table_name in cleanup_tables:
                await session.execute(text(f"DELETE FROM {table_name}"))

            await session.commit()

        finally:
            # Re-enable foreign key checks
            if "sqlite" in str(session.bind.url):
                await session.execute(text("PRAGMA foreign_keys=ON"))

    async def dispose_engine(self, test_id: str) -> None:
        """Dispose of engine and clean up resources."""

        if test_id in self._engines:
            await self._engines[test_id].dispose()
            del self._engines[test_id]

        if test_id in self._sessions:
            del self._sessions[test_id]


# ================================================================================================
# PYTEST FIXTURES FOR ISOLATION
# ================================================================================================

@pytest.fixture(scope="function")
async def admin_isolation_engine() -> AsyncGenerator[AdminDatabaseIsolationEngine, None]:
    """Create isolation engine for admin testing."""

    engine = AdminDatabaseIsolationEngine()
    yield engine

    # Cleanup all engines created during test
    for test_id in list(engine._engines.keys()):
        await engine.dispose_engine(test_id)


@pytest.fixture(scope="function")
async def admin_isolated_db_advanced(admin_isolation_engine: AdminDatabaseIsolationEngine) -> AsyncGenerator[AsyncSession, None]:
    """
    Advanced isolated database session with transaction rollback.

    Features:
    - Complete transaction isolation
    - Automatic rollback
    - Schema initialization
    - Resource cleanup
    """

    test_id = f"admin_test_{uuid.uuid4().hex[:8]}"

    # Create and initialize engine
    engine = await admin_isolation_engine.create_isolated_engine(test_id)
    await admin_isolation_engine.initialize_schema(engine)

    # Use isolated transaction context
    async with admin_isolation_engine.isolated_transaction_context(test_id) as session:
        yield session


@pytest.fixture(scope="function")
async def admin_nested_transaction_db(admin_isolation_engine: AdminDatabaseIsolationEngine) -> AsyncGenerator[AsyncSession, None]:
    """
    Database session with nested transaction support.

    Allows for complex test scenarios with multiple savepoints.
    """

    test_id = f"admin_nested_{uuid.uuid4().hex[:8]}"

    # Create and initialize engine
    engine = await admin_isolation_engine.create_isolated_engine(test_id)
    await admin_isolation_engine.initialize_schema(engine)

    # Create session with nested transaction capability
    session = await admin_isolation_engine.create_isolated_session(test_id)

    # Begin main transaction
    main_trans = await session.begin()

    try:
        yield session
    finally:
        await main_trans.rollback()
        await session.close()


# ================================================================================================
# SPECIALIZED ISOLATION STRATEGIES
# ================================================================================================

class AdminPermissionIsolationStrategy:
    """
    Specialized isolation strategy for admin permission testing.

    Handles complex permission relationships and ensures clean state
    between permission-related tests.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self._permission_snapshots: List[Dict[str, Any]] = []
        self._user_permission_snapshots: List[Dict[str, Any]] = []

    async def create_permission_snapshot(self) -> str:
        """Create snapshot of current permission state."""

        snapshot_id = f"perm_snapshot_{uuid.uuid4().hex[:8]}"

        # Capture current permissions
        permissions = await self.session.execute(
            text("SELECT * FROM admin_permissions")
        )
        self._permission_snapshots.extend([
            dict(row._mapping) for row in permissions
        ])

        # Capture current user-permission relationships
        user_perms = await self.session.execute(
            text("SELECT * FROM admin_user_permissions WHERE is_active = 1")
        )
        self._user_permission_snapshots.extend([
            dict(row._mapping) for row in user_perms
        ])

        return snapshot_id

    async def restore_permission_snapshot(self, snapshot_id: str) -> None:
        """Restore permission state to snapshot."""

        # Clear current state
        await self.session.execute(text("DELETE FROM admin_user_permissions"))
        await self.session.execute(text("DELETE FROM admin_permissions"))

        # Restore permissions
        for perm_data in self._permission_snapshots:
            await self.session.execute(
                text("""
                    INSERT INTO admin_permissions
                    (id, name, display_name, description, resource_type, action, scope,
                     required_clearance_level, risk_level, created_at, updated_at)
                    VALUES
                    (:id, :name, :display_name, :description, :resource_type, :action, :scope,
                     :required_clearance_level, :risk_level, :created_at, :updated_at)
                """),
                perm_data
            )

        # Restore user-permission relationships
        for user_perm_data in self._user_permission_snapshots:
            await self.session.execute(
                text("""
                    INSERT INTO admin_user_permissions
                    (user_id, permission_id, granted_by_id, granted_at, expires_at, is_active)
                    VALUES
                    (:user_id, :permission_id, :granted_by_id, :granted_at, :expires_at, :is_active)
                """),
                user_perm_data
            )

        await self.session.commit()

    async def clean_permission_grants_for_user(self, user_id: str) -> None:
        """Clean all permission grants for a specific user."""

        await self.session.execute(
            text("DELETE FROM admin_user_permissions WHERE user_id = :user_id"),
            {"user_id": user_id}
        )
        await self.session.commit()


class AdminUserIsolationStrategy:
    """
    Specialized isolation strategy for admin user testing.

    Handles user creation, modification, and cleanup with proper
    relationship management.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self._created_users: List[str] = []
        self._modified_users: Dict[str, Dict[str, Any]] = {}

    async def track_user_creation(self, user_id: str) -> None:
        """Track user creation for cleanup."""
        self._created_users.append(user_id)

    async def snapshot_user_state(self, user_id: str) -> None:
        """Snapshot user state before modification."""

        result = await self.session.execute(
            text("SELECT * FROM users WHERE id = :user_id"),
            {"user_id": user_id}
        )

        user_data = result.fetchone()
        if user_data:
            self._modified_users[user_id] = dict(user_data._mapping)

    async def restore_user_state(self, user_id: str) -> None:
        """Restore user to original state."""

        if user_id in self._modified_users:
            user_data = self._modified_users[user_id]

            # Update user back to original state
            update_fields = ", ".join([
                f"{key} = :{key}" for key in user_data.keys() if key != 'id'
            ])

            await self.session.execute(
                text(f"UPDATE users SET {update_fields} WHERE id = :id"),
                user_data
            )
            await self.session.commit()

    async def cleanup_created_users(self) -> None:
        """Clean up all users created during test."""

        for user_id in self._created_users:
            # Clean up related data first
            await self.session.execute(
                text("DELETE FROM admin_user_permissions WHERE user_id = :user_id"),
                {"user_id": user_id}
            )

            await self.session.execute(
                text("DELETE FROM admin_activity_logs WHERE admin_user_id = :user_id"),
                {"user_id": user_id}
            )

            # Delete user
            await self.session.execute(
                text("DELETE FROM users WHERE id = :user_id"),
                {"user_id": user_id}
            )

        await self.session.commit()
        self._created_users.clear()


# ================================================================================================
# PERFORMANCE OPTIMIZATION FOR ISOLATION
# ================================================================================================

class AdminDatabasePerformanceOptimizer:
    """
    Performance optimization for database isolation in admin testing.

    Reduces overhead of isolation strategies while maintaining data integrity.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self._batch_operations: List[str] = []
        self._deferred_cleanup: List[callable] = []

    async def batch_cleanup_operations(self, operations: List[str]) -> None:
        """Batch multiple cleanup operations for efficiency."""

        # Combine operations into single transaction
        async with self.session.begin():
            for operation in operations:
                await self.session.execute(text(operation))

    async def defer_cleanup(self, cleanup_func: callable) -> None:
        """Defer cleanup operation until test completion."""
        self._deferred_cleanup.append(cleanup_func)

    async def execute_deferred_cleanup(self) -> None:
        """Execute all deferred cleanup operations."""

        for cleanup_func in self._deferred_cleanup:
            try:
                await cleanup_func()
            except Exception as e:
                # Log but don't fail test cleanup
                print(f"Warning: Cleanup operation failed: {e}")

        self._deferred_cleanup.clear()

    @asynccontextmanager
    async def optimized_isolation_context(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Optimized isolation context with batched operations.
        """

        try:
            yield self.session
        finally:
            await self.execute_deferred_cleanup()


# ================================================================================================
# INTEGRATION WITH EXISTING FIXTURES
# ================================================================================================

@pytest.fixture(scope="function")
async def admin_permission_isolation(admin_isolated_db_advanced: AsyncSession) -> AsyncGenerator[AdminPermissionIsolationStrategy, None]:
    """Permission isolation strategy for admin testing."""

    strategy = AdminPermissionIsolationStrategy(admin_isolated_db_advanced)
    snapshot_id = await strategy.create_permission_snapshot()

    try:
        yield strategy
    finally:
        await strategy.restore_permission_snapshot(snapshot_id)


@pytest.fixture(scope="function")
async def admin_user_isolation(admin_isolated_db_advanced: AsyncSession) -> AsyncGenerator[AdminUserIsolationStrategy, None]:
    """User isolation strategy for admin testing."""

    strategy = AdminUserIsolationStrategy(admin_isolated_db_advanced)

    try:
        yield strategy
    finally:
        await strategy.cleanup_created_users()


@pytest.fixture(scope="function")
async def admin_performance_optimizer(admin_isolated_db_advanced: AsyncSession) -> AsyncGenerator[AdminDatabasePerformanceOptimizer, None]:
    """Performance optimizer for admin database operations."""

    optimizer = AdminDatabasePerformanceOptimizer(admin_isolated_db_advanced)

    async with optimizer.optimized_isolation_context():
        yield optimizer


# ================================================================================================
# VALIDATION AND TESTING UTILITIES
# ================================================================================================

class AdminIsolationValidator:
    """
    Validator to ensure database isolation is working correctly.
    """

    @staticmethod
    async def validate_clean_state(session: AsyncSession) -> Dict[str, int]:
        """Validate that database is in clean state."""

        tables = ["users", "admin_permissions", "admin_user_permissions", "admin_activity_logs"]
        counts = {}

        for table in tables:
            result = await session.execute(text(f"SELECT COUNT(*) FROM {table}"))
            counts[table] = result.scalar()

        return counts

    @staticmethod
    async def validate_isolation_integrity(session_1: AsyncSession, session_2: AsyncSession) -> bool:
        """Validate that two sessions are properly isolated."""

        # Create test data in session 1
        test_user_id = str(uuid.uuid4())
        await session_1.execute(
            text("""
                INSERT INTO users (id, email, password_hash, nombre, apellido, user_type, is_active, is_verified)
                VALUES (:id, :email, :password_hash, :nombre, :apellido, :user_type, :is_active, :is_verified)
            """),
            {
                "id": test_user_id,
                "email": "isolation_test@test.com",
                "password_hash": "test_hash",
                "nombre": "Test",
                "apellido": "User",
                "user_type": "ADMIN",
                "is_active": True,
                "is_verified": True
            }
        )

        # Check that session 2 cannot see the data
        result = await session_2.execute(
            text("SELECT COUNT(*) FROM users WHERE id = :id"),
            {"id": test_user_id}
        )

        count = result.scalar()
        return count == 0  # Should be 0 if properly isolated


@pytest.fixture
def admin_isolation_validator() -> AdminIsolationValidator:
    """Isolation validator for admin testing."""
    return AdminIsolationValidator()