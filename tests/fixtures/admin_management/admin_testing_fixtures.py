"""
Advanced Admin Management Testing Fixtures

Este módulo proporciona fixtures especializados para testing del sistema de administración
con soporte completo para FastAPI, SQLAlchemy async, y validación de permisos.

Autor: Backend Framework AI
Fecha: 2025-09-21
Framework: pytest + FastAPI + SQLAlchemy + Redis
Objetivo: Fixtures reutilizables para testing admin management
"""

import asyncio
import uuid
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, AsyncGenerator
from unittest.mock import Mock, AsyncMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session

from app.main import app
from app.core.database import get_db
from app.database import Base, get_async_db
from app.core.security import create_access_token, get_password_hash
from app.core.types import generate_uuid

# Models
from app.models.user import User, UserType, VendorStatus
from app.models.admin_permission import (
    AdminPermission, PermissionScope, PermissionAction, ResourceType,
    admin_user_permissions, SYSTEM_PERMISSIONS
)
from app.models.admin_activity_log import AdminActivityLog, AdminActionType, ActionResult, RiskLevel

# Services
from app.services.admin_permission_service import admin_permission_service


# ================================================================================================
# DATABASE FIXTURES FOR ADMIN TESTING
# ================================================================================================

@pytest.fixture(scope="function")
async def admin_isolated_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Isolated database session specifically for admin management testing.

    Features:
    - Complete isolation with transaction rollback
    - Admin-specific table setup
    - Permission system initialization
    - Activity log table ready
    """
    # Create async engine for admin testing
    admin_test_engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        pool_pre_ping=True,
        connect_args={"check_same_thread": False}
    )

    # Create session maker
    AdminAsyncSessionLocal = async_sessionmaker(
        bind=admin_test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    # Create all tables
    async with admin_test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session with transaction for isolation
    async with AdminAsyncSessionLocal() as session:
        async with session.begin() as trans:
            try:
                yield session
            finally:
                await trans.rollback()

    # Cleanup
    await admin_test_engine.dispose()


@pytest.fixture(scope="function")
async def admin_db_with_permissions(admin_isolated_db: AsyncSession) -> AsyncSession:
    """
    Database session with pre-loaded system permissions.

    Initializes:
    - All SYSTEM_PERMISSIONS from admin_permission.py
    - Permission hierarchy and relationships
    - Required permission matrix
    """
    session = admin_isolated_db

    # Initialize system permissions
    for perm_data in SYSTEM_PERMISSIONS:
        permission = AdminPermission(**perm_data)
        session.add(permission)

    await session.flush()  # Ensure permissions are available
    return session


# ================================================================================================
# ADMIN USER FIXTURES
# ================================================================================================

@pytest.fixture
async def test_system_user(admin_isolated_db: AsyncSession) -> User:
    """Create SYSTEM level user for highest privilege testing."""
    system_user = User(
        id=generate_uuid(),
        email="system@mestore.test",
        password_hash=await get_password_hash("system_test_pass"),
        nombre="System",
        apellido="Administrator",
        user_type=UserType.SYSTEM,
        security_clearance_level=5,
        is_active=True,
        is_verified=True,
        department_id="system",
        employee_id="SYS-001"
    )

    admin_isolated_db.add(system_user)
    await admin_isolated_db.flush()
    await admin_isolated_db.refresh(system_user)
    return system_user


@pytest.fixture
async def test_superuser_high_clearance(admin_isolated_db: AsyncSession) -> User:
    """Create SUPERUSER with high security clearance."""
    superuser = User(
        id=generate_uuid(),
        email="superuser@mestore.test",
        password_hash=await get_password_hash("super_test_pass"),
        nombre="Super",
        apellido="User",
        user_type=UserType.SUPERUSER,
        security_clearance_level=5,
        is_active=True,
        is_verified=True,
        department_id="executive",
        employee_id="SUP-001",
        performance_score=100
    )

    admin_isolated_db.add(superuser)
    await admin_isolated_db.flush()
    await admin_isolated_db.refresh(superuser)
    return superuser


@pytest.fixture
async def test_superuser_medium_clearance(admin_isolated_db: AsyncSession) -> User:
    """Create SUPERUSER with medium security clearance for boundary testing."""
    superuser = User(
        id=generate_uuid(),
        email="superuser_medium@mestore.test",
        password_hash=await get_password_hash("super_medium_pass"),
        nombre="Super",
        apellido="Medium",
        user_type=UserType.SUPERUSER,
        security_clearance_level=3,
        is_active=True,
        is_verified=True,
        department_id="operations",
        employee_id="SUP-002"
    )

    admin_isolated_db.add(superuser)
    await admin_isolated_db.flush()
    await admin_isolated_db.refresh(superuser)
    return superuser


@pytest.fixture
async def test_admin_high_clearance(admin_isolated_db: AsyncSession) -> User:
    """Create ADMIN with high security clearance."""
    admin = User(
        id=generate_uuid(),
        email="admin_high@mestore.test",
        password_hash=await get_password_hash("admin_high_pass"),
        nombre="Admin",
        apellido="High",
        user_type=UserType.ADMIN,
        security_clearance_level=4,
        is_active=True,
        is_verified=True,
        department_id="finance",
        employee_id="ADM-001"
    )

    admin_isolated_db.add(admin)
    await admin_isolated_db.flush()
    await admin_isolated_db.refresh(admin)
    return admin


@pytest.fixture
async def test_admin_low_clearance(admin_isolated_db: AsyncSession) -> User:
    """Create ADMIN with low security clearance for testing restrictions."""
    admin = User(
        id=generate_uuid(),
        email="admin_low@mestore.test",
        password_hash=await get_password_hash("admin_low_pass"),
        nombre="Admin",
        apellido="Low",
        user_type=UserType.ADMIN,
        security_clearance_level=2,
        is_active=True,
        is_verified=True,
        department_id="support",
        employee_id="ADM-002"
    )

    admin_isolated_db.add(admin)
    await admin_isolated_db.flush()
    await admin_isolated_db.refresh(admin)
    return admin


@pytest.fixture
async def test_vendor_user(admin_isolated_db: AsyncSession) -> User:
    """Create VENDOR user for negative testing scenarios."""
    vendor = User(
        id=generate_uuid(),
        email="vendor@mestore.test",
        password_hash=await get_password_hash("vendor_pass"),
        nombre="Test",
        apellido="Vendor",
        user_type=UserType.VENDOR,
        security_clearance_level=1,
        is_active=True,
        is_verified=True
    )

    admin_isolated_db.add(vendor)
    await admin_isolated_db.flush()
    await admin_isolated_db.refresh(vendor)
    return vendor


# ================================================================================================
# ADMIN USER COLLECTIONS
# ================================================================================================

@pytest.fixture
async def admin_user_hierarchy(
    test_system_user: User,
    test_superuser_high_clearance: User,
    test_superuser_medium_clearance: User,
    test_admin_high_clearance: User,
    test_admin_low_clearance: User,
    test_vendor_user: User
) -> Dict[str, User]:
    """Complete admin user hierarchy for comprehensive testing."""
    return {
        "system": test_system_user,
        "superuser_high": test_superuser_high_clearance,
        "superuser_medium": test_superuser_medium_clearance,
        "admin_high": test_admin_high_clearance,
        "admin_low": test_admin_low_clearance,
        "vendor": test_vendor_user  # For negative testing
    }


@pytest.fixture
async def bulk_admin_users(admin_isolated_db: AsyncSession) -> List[User]:
    """Create multiple admin users for bulk operation testing."""
    admin_users = []

    for i in range(10):
        admin = User(
            id=generate_uuid(),
            email=f"bulk_admin_{i}@mestore.test",
            password_hash=await get_password_hash(f"bulk_pass_{i}"),
            nombre=f"Bulk",
            apellido=f"Admin_{i}",
            user_type=UserType.ADMIN,
            security_clearance_level=3,
            is_active=True,
            is_verified=True,
            department_id=f"dept_{i % 3}",  # Distribute across 3 departments
            employee_id=f"BULK-{i:03d}"
        )
        admin_users.append(admin)
        admin_isolated_db.add(admin)

    await admin_isolated_db.flush()

    # Refresh all users
    for admin in admin_users:
        await admin_isolated_db.refresh(admin)

    return admin_users


# ================================================================================================
# JWT TOKEN FIXTURES
# ================================================================================================

@pytest.fixture
def admin_jwt_tokens(admin_user_hierarchy: Dict[str, User]) -> Dict[str, str]:
    """Generate JWT tokens for all admin user types."""
    tokens = {}

    for user_type, user in admin_user_hierarchy.items():
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "user_type": user.user_type.value,
            "nombre": user.nombre,
            "apellido": user.apellido,
            "security_clearance_level": user.security_clearance_level
        }
        tokens[user_type] = create_access_token(data=token_data)

    return tokens


@pytest.fixture
def admin_auth_headers(admin_jwt_tokens: Dict[str, str]) -> Dict[str, Dict[str, str]]:
    """Authentication headers for different admin user types."""
    return {
        user_type: {"Authorization": f"Bearer {token}"}
        for user_type, token in admin_jwt_tokens.items()
    }


@pytest.fixture
def expired_admin_token() -> str:
    """Generate expired JWT token for negative testing."""
    token_data = {
        "sub": str(uuid.uuid4()),
        "email": "expired@mestore.test",
        "user_type": "ADMIN"
    }
    return create_access_token(data=token_data, expires_delta=timedelta(seconds=-1))


@pytest.fixture
def invalid_admin_tokens() -> Dict[str, str]:
    """Collection of invalid tokens for security testing."""
    return {
        "malformed": "invalid.jwt.token",
        "empty": "",
        "expired": create_access_token(
            data={"sub": str(uuid.uuid4())},
            expires_delta=timedelta(seconds=-1)
        ),
        "wrong_secret": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature"
    }


# ================================================================================================
# FASTAPI CLIENT FIXTURES
# ================================================================================================

@pytest.fixture
async def admin_test_client(admin_isolated_db: AsyncSession) -> AsyncGenerator[TestClient, None]:
    """FastAPI TestClient with admin database override."""

    def get_admin_test_db():
        yield admin_isolated_db

    # Override dependencies
    app.dependency_overrides[get_db] = get_admin_test_db
    app.dependency_overrides[get_async_db] = get_admin_test_db

    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
async def admin_async_client(admin_isolated_db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """AsyncClient for admin management async operations."""

    def get_admin_test_db():
        yield admin_isolated_db

    # Override dependencies
    app.dependency_overrides[get_db] = get_admin_test_db
    app.dependency_overrides[get_async_db] = get_admin_test_db

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(
            transport=transport,
            base_url="http://testserver",
            headers={"User-Agent": "Admin-Test-Client/1.0"}
        ) as client:
            yield client
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
async def authenticated_admin_client(
    admin_async_client: AsyncClient,
    admin_auth_headers: Dict[str, Dict[str, str]]
) -> AsyncGenerator[Dict[str, AsyncClient], None]:
    """Pre-authenticated async clients for different admin levels."""

    authenticated_clients = {}

    for user_type, headers in admin_auth_headers.items():
        # Create a new client with authentication headers
        client = admin_async_client
        client.headers.update(headers)
        authenticated_clients[user_type] = client

    yield authenticated_clients


# ================================================================================================
# PERMISSION TESTING FIXTURES
# ================================================================================================

@pytest.fixture
async def test_permission_basic(admin_db_with_permissions: AsyncSession) -> AdminPermission:
    """Basic permission for testing."""
    permission = await admin_db_with_permissions.query(AdminPermission).filter(
        AdminPermission.name == "users.read.global"
    ).first()

    if not permission:
        permission = AdminPermission(
            name="users.read.global",
            display_name="Read Users Globally",
            description="Read user information across all departments",
            resource_type=ResourceType.USERS,
            action=PermissionAction.READ,
            scope=PermissionScope.GLOBAL,
            required_clearance_level=3,
            risk_level="MEDIUM"
        )
        admin_db_with_permissions.add(permission)
        await admin_db_with_permissions.flush()
        await admin_db_with_permissions.refresh(permission)

    return permission


@pytest.fixture
async def test_permission_high_risk(admin_db_with_permissions: AsyncSession) -> AdminPermission:
    """High-risk permission for security testing."""
    permission = AdminPermission(
        name="users.delete.system",
        display_name="Delete System Users",
        description="Delete users at system level",
        resource_type=ResourceType.USERS,
        action=PermissionAction.DELETE,
        scope=PermissionScope.SYSTEM,
        required_clearance_level=5,
        risk_level="CRITICAL",
        requires_mfa=True,
        is_system_permission=True
    )

    admin_db_with_permissions.add(permission)
    await admin_db_with_permissions.flush()
    await admin_db_with_permissions.refresh(permission)
    return permission


@pytest.fixture
async def permission_matrix(admin_db_with_permissions: AsyncSession) -> List[AdminPermission]:
    """Complete permission matrix for comprehensive testing."""
    permissions = []

    # Define permission combinations
    permission_configs = [
        ("users.create.global", ResourceType.USERS, PermissionAction.CREATE, PermissionScope.GLOBAL, 4),
        ("users.update.department", ResourceType.USERS, PermissionAction.UPDATE, PermissionScope.DEPARTMENT, 3),
        ("vendors.approve.global", ResourceType.VENDORS, PermissionAction.APPROVE, PermissionScope.GLOBAL, 3),
        ("transactions.audit.global", ResourceType.TRANSACTIONS, PermissionAction.AUDIT, PermissionScope.GLOBAL, 4),
        ("settings.configure.system", ResourceType.SETTINGS, PermissionAction.CONFIGURE, PermissionScope.SYSTEM, 5),
    ]

    for name, resource, action, scope, clearance in permission_configs:
        permission = AdminPermission(
            name=name,
            display_name=name.replace(".", " ").title(),
            description=f"Permission to {action.value.lower()} {resource.value.lower()} at {scope.value.lower()} scope",
            resource_type=resource,
            action=action,
            scope=scope,
            required_clearance_level=clearance,
            risk_level="HIGH" if clearance >= 4 else "MEDIUM"
        )
        permissions.append(permission)
        admin_db_with_permissions.add(permission)

    await admin_db_with_permissions.flush()

    for permission in permissions:
        await admin_db_with_permissions.refresh(permission)

    return permissions


# ================================================================================================
# ADMIN PERMISSION GRANTS FIXTURES
# ================================================================================================

@pytest.fixture
async def admin_with_permissions(
    test_admin_high_clearance: User,
    test_permission_basic: AdminPermission,
    admin_db_with_permissions: AsyncSession
) -> tuple[User, List[AdminPermission]]:
    """Admin user with pre-granted permissions."""

    # Grant permission to admin
    await admin_db_with_permissions.execute(
        admin_user_permissions.insert().values(
            user_id=test_admin_high_clearance.id,
            permission_id=test_permission_basic.id,
            granted_by_id=test_admin_high_clearance.id,  # Self-granted for test
            granted_at=datetime.utcnow(),
            is_active=True
        )
    )

    await admin_db_with_permissions.commit()

    return test_admin_high_clearance, [test_permission_basic]


# ================================================================================================
# MOCK SERVICES FIXTURES
# ================================================================================================

@pytest.fixture
def mock_admin_permission_service():
    """Mock admin permission service for unit testing."""
    mock_service = Mock()

    # Default successful validation
    mock_service.validate_permission = AsyncMock(return_value=True)
    mock_service.grant_permission = AsyncMock(return_value=True)
    mock_service.revoke_permission = AsyncMock(return_value=True)
    mock_service.get_user_permissions = AsyncMock(return_value=[])
    mock_service._log_admin_activity = AsyncMock()

    return mock_service


@pytest.fixture
def mock_redis_admin():
    """Mock Redis specifically for admin permission caching."""
    mock_redis = AsyncMock()

    # Default cache miss
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True
    mock_redis.setex.return_value = True
    mock_redis.delete.return_value = 1
    mock_redis.keys.return_value = []

    return mock_redis


@pytest.fixture
def mock_auth_service():
    """Mock authentication service for admin user creation."""
    mock_service = Mock()

    mock_service.generate_secure_password.return_value = "TempPass123!"
    mock_service.get_password_hash.return_value = "$2b$12$test.hash.for.admin.testing"
    mock_service.verify_password.return_value = True

    return mock_service


# ================================================================================================
# ACTIVITY LOG FIXTURES
# ================================================================================================

@pytest.fixture
async def admin_activity_logs(
    admin_isolated_db: AsyncSession,
    test_superuser_high_clearance: User
) -> List[AdminActivityLog]:
    """Sample admin activity logs for testing."""

    logs = []

    # Create sample log entries
    log_data = [
        (AdminActionType.USER_MANAGEMENT, "create_admin", "Created new admin user", RiskLevel.HIGH),
        (AdminActionType.SECURITY, "grant_permission", "Granted permission to user", RiskLevel.HIGH),
        (AdminActionType.CONFIGURATION, "update_settings", "Updated system settings", RiskLevel.MEDIUM),
        (AdminActionType.AUDIT, "view_logs", "Viewed audit logs", RiskLevel.LOW),
    ]

    for action_type, action_name, description, risk_level in log_data:
        log = AdminActivityLog(
            admin_user_id=test_superuser_high_clearance.id,
            admin_email=test_superuser_high_clearance.email,
            admin_full_name=test_superuser_high_clearance.full_name,
            action_type=action_type,
            action_name=action_name,
            action_description=description,
            result=ActionResult.SUCCESS,
            risk_level=risk_level,
            ip_address="127.0.0.1",
            user_agent="Admin-Test-Client/1.0"
        )
        logs.append(log)
        admin_isolated_db.add(log)

    await admin_isolated_db.flush()

    for log in logs:
        await admin_isolated_db.refresh(log)

    return logs


# ================================================================================================
# REQUEST/RESPONSE FIXTURES
# ================================================================================================

@pytest.fixture
def valid_admin_create_requests() -> Dict[str, Dict[str, Any]]:
    """Valid admin creation request payloads."""
    return {
        "basic_admin": {
            "email": "new_admin@mestore.test",
            "nombre": "New",
            "apellido": "Admin",
            "user_type": "ADMIN",
            "security_clearance_level": 3
        },
        "high_clearance_admin": {
            "email": "high_admin@mestore.test",
            "nombre": "High",
            "apellido": "Clearance",
            "user_type": "ADMIN",
            "security_clearance_level": 4,
            "department_id": "finance",
            "initial_permissions": ["users.read.global"]
        },
        "superuser": {
            "email": "new_superuser@mestore.test",
            "nombre": "New",
            "apellido": "SuperUser",
            "user_type": "SUPERUSER",
            "security_clearance_level": 5,
            "department_id": "executive"
        }
    }


@pytest.fixture
def invalid_admin_create_requests() -> Dict[str, Dict[str, Any]]:
    """Invalid admin creation request payloads for negative testing."""
    return {
        "missing_email": {
            "nombre": "Test",
            "apellido": "Admin"
        },
        "invalid_email": {
            "email": "not-an-email",
            "nombre": "Test",
            "apellido": "Admin"
        },
        "clearance_too_high": {
            "email": "test@test.com",
            "nombre": "Test",
            "apellido": "Admin",
            "security_clearance_level": 6  # Above maximum
        },
        "clearance_too_low": {
            "email": "test@test.com",
            "nombre": "Test",
            "apellido": "Admin",
            "security_clearance_level": 0  # Below minimum
        }
    }


# ================================================================================================
# ENVIRONMENT CONFIGURATION FIXTURES
# ================================================================================================

@pytest.fixture
def admin_test_settings():
    """Test-specific settings for admin management testing."""
    return {
        "TESTING": True,
        "DISABLE_REDIS_CACHE": False,  # Test with cache enabled
        "ADMIN_SESSION_TIMEOUT": 3600,
        "MAX_FAILED_LOGIN_ATTEMPTS": 3,
        "ADMIN_MFA_REQUIRED": False,  # Simplified for testing
        "ADMIN_AUDIT_LEVEL": "detailed",
        "PERMISSION_CACHE_TTL": 300
    }


@pytest.fixture
def performance_test_config():
    """Configuration for performance testing scenarios."""
    return {
        "BULK_OPERATION_MAX_SIZE": 100,
        "DATABASE_POOL_SIZE": 20,
        "MAX_CONCURRENT_REQUESTS": 50,
        "RESPONSE_TIME_THRESHOLD_MS": 500,
        "MEMORY_USAGE_THRESHOLD_MB": 512
    }


# ================================================================================================
# UTILITY FIXTURES
# ================================================================================================

@pytest.fixture
def admin_test_utils():
    """Utility functions for admin testing."""

    class AdminTestUtils:
        @staticmethod
        def create_permission_key(resource: ResourceType, action: PermissionAction, scope: PermissionScope) -> str:
            """Create standardized permission key."""
            return f"{resource.value}.{action.value}.{scope.value}".lower()

        @staticmethod
        def generate_test_admin_data(count: int = 1, prefix: str = "test") -> List[Dict[str, Any]]:
            """Generate test admin user data."""
            return [
                {
                    "email": f"{prefix}_admin_{i}@mestore.test",
                    "nombre": f"Test{i}",
                    "apellido": f"Admin{i}",
                    "user_type": "ADMIN",
                    "security_clearance_level": min(3 + (i % 3), 5)
                }
                for i in range(count)
            ]

        @staticmethod
        def extract_user_ids(users: List[User]) -> List[str]:
            """Extract user IDs from user objects."""
            return [str(user.id) for user in users]

    return AdminTestUtils()


# ================================================================================================
# INTEGRATION FIXTURES
# ================================================================================================

@pytest.fixture(scope="session")
def admin_integration_config():
    """Session-level configuration for integration testing."""
    return {
        "test_database_url": "sqlite+aiosqlite:///:memory:",
        "test_redis_url": "redis://localhost:6379/15",  # Test database
        "admin_api_prefix": "/api/v1/admin",
        "auth_header_prefix": "Bearer",
        "test_timeout_seconds": 30
    }


@pytest.fixture
async def full_admin_stack(
    admin_db_with_permissions: AsyncSession,
    admin_user_hierarchy: Dict[str, User],
    permission_matrix: List[AdminPermission],
    admin_activity_logs: List[AdminActivityLog]
) -> Dict[str, Any]:
    """Complete admin management stack for full integration testing."""

    return {
        "database": admin_db_with_permissions,
        "users": admin_user_hierarchy,
        "permissions": permission_matrix,
        "activity_logs": admin_activity_logs,
        "stack_ready": True
    }