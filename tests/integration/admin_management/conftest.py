# ~/tests/integration/admin_management/conftest.py
# ---------------------------------------------------------------------------------------------
# MeStore - Integration Testing Framework Configuration for Admin Management
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: conftest.py
# Ruta: ~/tests/integration/admin_management/conftest.py
# Autor: Integration Testing Specialist
# Fecha de Creación: 2025-09-21
# Última Actualización: 2025-09-21
# Versión: 1.0.0
# Propósito: Integration test configuration and fixtures for admin management system
#
# Integration Testing Framework for admin_management.py:
# - Service-to-service integration fixtures
# - Database transaction isolation
# - Redis session management mocks
# - Email service integration mocks
# - Audit logging validation fixtures
# - Performance and concurrency test setup
#
# ---------------------------------------------------------------------------------------------

"""
Integration Testing Configuration for Admin Management System.

Este módulo proporciona fixtures y configuración para testing de integración:
- Database transaction isolation with realistic data
- Service mocking for external dependencies
- Redis session management integration
- Email service integration testing
- Audit logging validation fixtures
- Performance and load testing setup
- Concurrent operations testing configuration
"""

import pytest
import asyncio
import redis
import uuid
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
try:
    from testcontainers.postgres import PostgresContainer
    from testcontainers.redis import RedisContainer
    TESTCONTAINERS_AVAILABLE = True
except ImportError:
    # Fallback for environments without testcontainers
    TESTCONTAINERS_AVAILABLE = False
    PostgresContainer = None
    RedisContainer = None

from app.core.database import get_db, Base
from app.database import get_async_db
from app.core.config import settings
from app.models.user import User, UserType
from app.models.admin_permission import AdminPermission, PermissionScope, PermissionAction, ResourceType
from app.models.admin_activity_log import AdminActivityLog, AdminActionType, ActionResult, RiskLevel
from app.services.admin_permission_service import AdminPermissionService, admin_permission_service
from app.services.auth_service import AuthService
import asyncio

# Create auth service instance
auth_service = AuthService()

# Helper function to get password hash synchronously
def get_password_hash_sync(password: str) -> str:
    """Get password hash synchronously for fixtures."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop is already running, use a pre-computed hash
            # This is a fallback for complex async scenarios
            return auth_service.pwd_context.hash(password)
        else:
            return loop.run_until_complete(auth_service.get_password_hash(password))
    except RuntimeError:
        # Fallback to synchronous hashing if async fails
        return auth_service.pwd_context.hash(password)


# === CONTAINER-BASED TEST DATABASE ===

# Add integration-specific async client
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session, create_async_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture
async def integration_async_client(integration_db_session: Session) -> AsyncClient:
    """
    Integration-specific async client that properly handles async database operations.
    This ensures API calls and fixtures use the same database state.
    """
    # Create a wrapper that simulates async behavior for the sync session
    class AsyncSessionWrapper:
        def __init__(self, sync_session):
            self.sync_session = sync_session

        def __getattr__(self, name):
            # Forward all other attributes to the sync session
            return getattr(self.sync_session, name)

        async def add(self, instance):
            self.sync_session.add(instance)

        async def refresh(self, instance):
            try:
                self.sync_session.refresh(instance)
            except Exception:
                pass

        def add(self, instance):
            return self.sync_session.add(instance)

        def refresh(self, instance):
            try:
                return self.sync_session.refresh(instance)
            except Exception:
                pass

        async def execute(self, statement, parameters=None):
            # Execute sync queries in the sync session
            # Ensure any pending changes are visible
            try:
                self.sync_session.flush()
            except Exception:
                pass
            return self.sync_session.execute(statement, parameters)

        async def scalar(self, statement, parameters=None):
            # Ensure session is flushed before executing scalar queries
            try:
                self.sync_session.flush()
            except Exception:
                pass
            # Execute scalar queries
            return self.sync_session.scalar(statement, parameters)

        async def commit(self):
            try:
                self.sync_session.commit()
            except Exception:
                pass

        async def rollback(self):
            try:
                self.sync_session.rollback()
            except Exception:
                # If rollback fails, just pass - this happens during test teardown
                pass

        async def close(self):
            return self.sync_session.close()

    async def get_integration_db():
        """Override database dependency to use wrapped async session."""
        # Create a wrapper that shares the exact same session
        wrapper = AsyncSessionWrapper(integration_db_session)
        # Ensure the wrapper sees all existing data by flushing any pending changes
        try:
            integration_db_session.flush()
        except Exception:
            pass
        try:
            yield wrapper
        finally:
            pass  # Don't close as the original session is managed elsewhere

    # Override both database dependencies
    app.dependency_overrides[get_db] = get_integration_db
    app.dependency_overrides[get_async_db] = get_integration_db

    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
        headers=headers
    ) as client:
        yield client

    # Clean up the overrides
    if get_db in app.dependency_overrides:
        del app.dependency_overrides[get_db]
    if get_async_db in app.dependency_overrides:
        del app.dependency_overrides[get_async_db]

@pytest.fixture(scope="session")
def postgres_container():
    """PostgreSQL container for integration tests."""
    if not TESTCONTAINERS_AVAILABLE:
        # Return None to trigger fallback in integration_db_engine
        yield None
        return

    with PostgresContainer("postgres:13") as postgres:
        postgres.start()
        yield postgres


@pytest.fixture(scope="session")
def redis_container():
    """Redis container for integration tests."""
    if not TESTCONTAINERS_AVAILABLE:
        # Return None to trigger fallback in integration_redis_client
        yield None
        return

    with RedisContainer("redis:6-alpine") as redis_cont:
        redis_cont.start()
        yield redis_cont


# Import the isolated_sync_session fixture from database_isolation
from tests.database_isolation import isolated_sync_session

@pytest.fixture
def integration_db_session(request, isolated_sync_session: Session) -> Generator[Session, None, None]:
    """Database session with transaction isolation for integration tests."""
    # Skip database setup for standalone auth tests
    if hasattr(request, 'node') and hasattr(request.node, 'get_closest_marker'):
        if request.node.get_closest_marker('standalone_auth'):
            # Provide a mock session that doesn't interfere
            from unittest.mock import MagicMock
            mock_session = MagicMock()
            mock_session._test_objects = []
            yield mock_session
            return

    # Add tracking for cleanup
    isolated_sync_session._test_objects = []
    yield isolated_sync_session


@pytest.fixture
def integration_redis_client(redis_container):
    """Redis client for integration tests."""
    if not TESTCONTAINERS_AVAILABLE or redis_container is None:
        # Fallback to mock Redis client
        import fakeredis
        client = fakeredis.FakeRedis()
        yield client
        return

    redis_url = redis_container.get_connection_url()
    client = redis.from_url(redis_url)

    yield client

    # Cleanup
    client.flushall()
    client.close()


# === SERVICE INTEGRATION FIXTURES ===

@pytest.fixture
def mock_email_service():
    """Mock email service for integration testing."""
    email_service = MagicMock()
    email_service.send_admin_welcome_email = AsyncMock(return_value=True)
    email_service.send_admin_permission_notification = AsyncMock(return_value=True)
    email_service.send_admin_security_alert = AsyncMock(return_value=True)
    email_service.send_admin_password_reset = AsyncMock(return_value=True)

    with patch('app.services.email_service.email_service', email_service):
        yield email_service


@pytest.fixture
def mock_notification_service():
    """Mock notification service for integration testing."""
    notification_service = MagicMock()
    notification_service.send_admin_notification = AsyncMock(return_value=True)
    notification_service.send_security_alert = AsyncMock(return_value=True)
    notification_service.send_bulk_notification = AsyncMock(return_value=True)

    with patch('app.services.notification_service.notification_service', notification_service):
        yield notification_service


@pytest.fixture
def admin_permission_service_with_redis(integration_redis_client):
    """Admin permission service with real Redis integration."""
    original_redis = admin_permission_service.redis_client
    admin_permission_service.redis_client = integration_redis_client
    admin_permission_service.cache_ttl = 300  # 5 minutes for testing

    yield admin_permission_service

    # Restore original Redis client
    admin_permission_service.redis_client = original_redis


# === USER AND PERMISSION FIXTURES ===

@pytest.fixture
def system_user(integration_db_session: Session) -> User:
    """Create system user for integration tests."""
    user = User(
        id=str(uuid.uuid4()),
        email="system@mestore.com",
        nombre="System",
        apellido="User",
        user_type=UserType.SYSTEM,
        security_clearance_level=5,
        is_active=True,
        is_verified=True,
        password_hash=get_password_hash_sync("system_password_123"),
        performance_score=100
    )
    integration_db_session.add(user)
    integration_db_session.commit()
    integration_db_session.refresh(user)
    integration_db_session._test_objects.append(user)
    return user


@pytest.fixture
def superuser(integration_db_session: Session) -> User:
    """Create superuser for integration tests."""
    user = User(
        id=str(uuid.uuid4()),
        email="superuser@mestore.com",
        nombre="Super",
        apellido="User",
        user_type=UserType.SUPERUSER,
        security_clearance_level=4,
        is_active=True,
        is_verified=True,
        password_hash=get_password_hash_sync("super_password_123"),
        performance_score=95,
        department_id="IT_DEPT",
        employee_id="SU001"
    )
    integration_db_session.add(user)
    integration_db_session.commit()
    integration_db_session.refresh(user)
    integration_db_session._test_objects.append(user)
    return user


@pytest.fixture
def admin_user(integration_db_session: Session) -> User:
    """Create admin user for integration tests."""
    user = User(
        id=str(uuid.uuid4()),
        email="admin@mestore.com",
        nombre="Admin",
        apellido="User",
        user_type=UserType.ADMIN,
        security_clearance_level=3,
        is_active=True,
        is_verified=True,
        password_hash=get_password_hash_sync("admin_password_123"),
        performance_score=90,
        department_id="SALES_DEPT",
        employee_id="AD001"
    )
    integration_db_session.add(user)
    integration_db_session.commit()
    integration_db_session.refresh(user)
    integration_db_session._test_objects.append(user)
    return user


@pytest.fixture
def locked_admin_user(integration_db_session: Session) -> User:
    """Create locked admin user for integration tests."""
    user = User(
        id=str(uuid.uuid4()),
        email="locked.admin@mestore.com",
        nombre="Locked",
        apellido="Admin",
        user_type=UserType.ADMIN,
        security_clearance_level=3,
        is_active=True,
        is_verified=True,
        password_hash=get_password_hash_sync("locked_password_123"),
        account_locked_until=datetime.utcnow() + timedelta(hours=1),
        failed_login_attempts=5,
        performance_score=50
    )
    integration_db_session.add(user)
    integration_db_session.commit()
    integration_db_session.refresh(user)
    integration_db_session._test_objects.append(user)
    return user


@pytest.fixture
def multiple_admin_users(integration_db_session: Session) -> List[User]:
    """Create multiple admin users for bulk operations testing."""
    users = []

    for i in range(5):
        user = User(
            id=str(uuid.uuid4()),
            email=f"admin{i+1}@mestore.com",
            nombre=f"Admin{i+1}",
            apellido="User",
            user_type=UserType.ADMIN,
            security_clearance_level=3,
            is_active=True if i < 3 else False,  # First 3 active, last 2 inactive
            is_verified=True,
            password_hash=get_password_hash_sync(f"admin{i+1}_password_123"),
            performance_score=80 + (i * 5),
            department_id="BULK_DEPT" if i < 3 else "INACTIVE_DEPT",
            employee_id=f"BU00{i+1}"
        )
        integration_db_session.add(user)
        users.append(user)
        integration_db_session._test_objects.append(user)

    integration_db_session.commit()
    for user in users:
        integration_db_session.refresh(user)

    return users


@pytest.fixture
def system_permissions(integration_db_session: Session) -> List[AdminPermission]:
    """Create system permissions for integration tests."""
    permissions = [
        AdminPermission(
            id=str(uuid.uuid4()),
            name="users.create.global",
            display_name="Create Users Globally",
            description="Create users globally",
            resource_type=ResourceType.USERS,
            action=PermissionAction.CREATE,
            scope=PermissionScope.GLOBAL,
            required_clearance_level=4,
            is_inheritable=True,
            is_system_permission=True
        ),
        AdminPermission(
            id=str(uuid.uuid4()),
            name="users.manage.global",
            display_name="Manage Users Globally",
            description="Manage users globally",
            resource_type=ResourceType.USERS,
            action=PermissionAction.MANAGE,
            scope=PermissionScope.GLOBAL,
            required_clearance_level=4,
            is_inheritable=True,
            is_system_permission=True
        ),
        AdminPermission(
            id=str(uuid.uuid4()),
            name="users.read.global",
            display_name="Read Users Globally",
            description="Read users globally",
            resource_type=ResourceType.USERS,
            action=PermissionAction.READ,
            scope=PermissionScope.GLOBAL,
            required_clearance_level=3,
            is_inheritable=True,
            is_system_permission=True
        ),
        AdminPermission(
            id=str(uuid.uuid4()),
            name="permissions.grant.system",
            display_name="Grant System Permissions",
            description="Grant system permissions",
            resource_type=ResourceType.PERMISSIONS,
            action=PermissionAction.GRANT,
            scope=PermissionScope.SYSTEM,
            required_clearance_level=5,
            is_inheritable=False,
            is_system_permission=True
        ),
        AdminPermission(
            id=str(uuid.uuid4()),
            name="audit.read.global",
            display_name="Read Audit Logs Globally",
            description="Read audit logs globally",
            resource_type=ResourceType.AUDIT_LOGS,
            action=PermissionAction.READ,
            scope=PermissionScope.GLOBAL,
            required_clearance_level=4,
            is_inheritable=True,
            is_system_permission=True
        )
    ]

    for permission in permissions:
        integration_db_session.add(permission)
        integration_db_session._test_objects.append(permission)

    integration_db_session.commit()
    for permission in permissions:
        integration_db_session.refresh(permission)

    return permissions


# === PERFORMANCE AND LOAD TESTING FIXTURES ===

@pytest.fixture
def performance_metrics():
    """Performance metrics collection for integration tests."""
    metrics = {
        'response_times': [],
        'database_queries': [],
        'cache_hits': 0,
        'cache_misses': 0,
        'concurrent_users': 0,
        'error_count': 0
    }
    return metrics


@pytest.fixture
def concurrent_test_data():
    """Data for concurrent operations testing."""
    return {
        'user_ids': [str(uuid.uuid4()) for _ in range(50)],
        'permission_ids': [str(uuid.uuid4()) for _ in range(20)],
        'operation_types': ['create', 'update', 'delete', 'grant', 'revoke'],
        'departments': ['SALES', 'IT', 'HR', 'MARKETING', 'FINANCE']
    }


# === INTEGRATION TEST SCENARIOS ===

@pytest.fixture
def admin_lifecycle_scenario():
    """Complete admin lifecycle scenario data."""
    return {
        'create_data': {
            'email': 'lifecycle.admin@mestore.com',
            'nombre': 'Lifecycle',
            'apellido': 'Admin',
            'user_type': UserType.ADMIN,
            'security_clearance_level': 3,
            'department_id': 'LIFECYCLE_DEPT',
            'initial_permissions': ['users.read.global']
        },
        'update_data': {
            'nombre': 'Updated Lifecycle',
            'security_clearance_level': 4,
            'performance_score': 95
        },
        'permission_grants': [
            'users.create.global',
            'users.manage.global'
        ],
        'bulk_operations': ['activate', 'deactivate', 'lock', 'unlock']
    }


@pytest.fixture
def error_scenario_data():
    """Error handling scenario data."""
    return {
        'invalid_emails': [
            'invalid.email',
            '@invalid.com',
            'user@',
            '',
            None
        ],
        'invalid_clearance_levels': [-1, 0, 6, 100, 'invalid'],
        'nonexistent_ids': [str(uuid.uuid4()) for _ in range(5)],
        'permission_conflicts': [
            ('system.permission', UserType.ADMIN),
            ('high.clearance', 2),
            ('department.permission', None)
        ]
    }


# === AUDIT AND LOGGING FIXTURES ===

@pytest.fixture
def audit_validation_helper():
    """Helper for validating audit log entries."""

    class AuditValidator:
        def __init__(self, db_session: Session):
            self.db = db_session

        def get_recent_logs(self, admin_user_id: str, action_type: AdminActionType = None) -> List[AdminActivityLog]:
            """Get recent audit logs for a user."""
            query = self.db.query(AdminActivityLog).filter(
                AdminActivityLog.admin_user_id == admin_user_id
            ).order_by(AdminActivityLog.created_at.desc())

            if action_type:
                query = query.filter(AdminActivityLog.action_type == action_type)

            return query.limit(10).all()

        def validate_log_entry(self, log: AdminActivityLog, expected_data: Dict[str, Any]) -> bool:
            """Validate a log entry against expected data."""
            for field, value in expected_data.items():
                if not hasattr(log, field):
                    return False
                if getattr(log, field) != value:
                    return False
            return True

        def count_logs_by_action(self, action_name: str) -> int:
            """Count logs by action name."""
            return self.db.query(AdminActivityLog).filter(
                AdminActivityLog.action_name == action_name
            ).count()

    return AuditValidator


# === MOCK EXTERNAL SERVICES ===

@pytest.fixture
def mock_smtp_server():
    """Mock SMTP server for email integration testing."""

    class MockSMTPServer:
        def __init__(self):
            self.sent_emails = []
            self.connection_errors = 0
            self.send_failures = 0

        async def send_email(self, to: str, subject: str, body: str, **kwargs) -> bool:
            """Mock email sending."""
            if self.send_failures > 0:
                self.send_failures -= 1
                return False

            self.sent_emails.append({
                'to': to,
                'subject': subject,
                'body': body,
                'timestamp': datetime.utcnow(),
                'kwargs': kwargs
            })
            return True

        def get_sent_emails(self, to_email: str = None) -> List[Dict]:
            """Get sent emails, optionally filtered by recipient."""
            if to_email:
                return [email for email in self.sent_emails if email['to'] == to_email]
            return self.sent_emails

        def simulate_connection_error(self):
            """Simulate SMTP connection error."""
            self.connection_errors += 1

        def simulate_send_failure(self, count: int = 1):
            """Simulate email send failures."""
            self.send_failures = count

    return MockSMTPServer()


@pytest.fixture
def integration_test_context():
    """Complete integration test context with all services."""

    class IntegrationContext:
        def __init__(self):
            self.start_time = datetime.utcnow()
            self.operation_count = 0
            self.error_count = 0
            self.performance_metrics = {}

        def record_operation(self, operation_name: str, duration: float, success: bool = True):
            """Record operation performance."""
            self.operation_count += 1
            if not success:
                self.error_count += 1

            if operation_name not in self.performance_metrics:
                self.performance_metrics[operation_name] = []
            self.performance_metrics[operation_name].append(duration)

        def get_average_response_time(self, operation_name: str) -> float:
            """Get average response time for operation."""
            times = self.performance_metrics.get(operation_name, [])
            return sum(times) / len(times) if times else 0.0

        def get_success_rate(self) -> float:
            """Get overall success rate."""
            if self.operation_count == 0:
                return 1.0
            return (self.operation_count - self.error_count) / self.operation_count

    return IntegrationContext()


# === EVENT LOOP AND ASYNC FIXTURES ===

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# === DATABASE TRANSACTION FIXTURES ===

@pytest.fixture
def transaction_test_helper():
    """Helper for testing database transactions."""

    class TransactionHelper:
        def __init__(self, db_session: Session):
            self.db = db_session
            self.savepoints = []

        def create_savepoint(self, name: str):
            """Create a database savepoint."""
            savepoint = self.db.begin_nested()
            self.savepoints.append((name, savepoint))
            return savepoint

        def rollback_to_savepoint(self, name: str):
            """Rollback to specific savepoint."""
            for sp_name, savepoint in reversed(self.savepoints):
                if sp_name == name:
                    savepoint.rollback()
                    self.savepoints = [sp for sp in self.savepoints if sp[0] != name]
                    break

        def commit_savepoint(self, name: str):
            """Commit specific savepoint."""
            for sp_name, savepoint in self.savepoints:
                if sp_name == name:
                    savepoint.commit()
                    self.savepoints = [sp for sp in self.savepoints if sp[0] != name]
                    break

    return TransactionHelper


# === CLEANUP UTILITIES ===

@pytest.fixture(autouse=True)
def cleanup_test_data(integration_db_session: Session):
    """Automatic cleanup of test data after each test."""
    yield

    # Clean up any test objects created during the test
    if hasattr(integration_db_session, '_test_objects'):
        for obj in reversed(integration_db_session._test_objects):
            try:
                integration_db_session.delete(obj)
            except Exception:
                pass  # Object might already be deleted

        try:
            integration_db_session.commit()
        except Exception:
            integration_db_session.rollback()