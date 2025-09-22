"""
Test Fixtures for Admin User Management TDD Tests

This file provides comprehensive fixtures for testing admin user management endpoints
with different permission levels, security clearances, and user types.

File: tests/unit/admin_management/conftest_admin_user_management.py
Author: TDD Specialist AI
Date: 2025-09-21
Framework: pytest fixtures for TDD RED-GREEN-REFACTOR methodology
"""

import pytest
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from unittest.mock import Mock, MagicMock
from sqlalchemy.orm import Session

from app.models.user import User, UserType, VendorStatus
from app.models.admin_permission import (
    AdminPermission,
    PermissionScope,
    PermissionAction,
    ResourceType,
    admin_user_permissions
)
from app.models.admin_activity_log import (
    AdminActivityLog,
    AdminActionType,
    ActionResult,
    RiskLevel
)
from app.api.v1.endpoints.admin_management import (
    AdminCreateRequest,
    AdminUpdateRequest,
    PermissionGrantRequest,
    PermissionRevokeRequest,
    BulkUserActionRequest,
    AdminResponse
)


# ================================================================================================
# MOCK DATABASE SESSION FIXTURES
# ================================================================================================

@pytest.fixture
def mock_db_session():
    """Mock database session for TDD tests."""
    session = Mock(spec=Session)
    session.query = Mock()
    session.add = Mock()
    session.commit = Mock()
    session.rollback = Mock()
    session.flush = Mock()
    return session


# ================================================================================================
# ADMIN USER FIXTURES WITH DIFFERENT SECURITY LEVELS
# ================================================================================================

@pytest.fixture
def superuser_admin():
    """Fixture for a SUPERUSER admin with maximum privileges."""
    user = Mock(spec=User)
    user.id = str(uuid.uuid4())
    user.email = "superuser@mestore.com"
    user.nombre = "Super"
    user.apellido = "User"
    user.user_type = UserType.SUPERUSER
    user.security_clearance_level = 5
    user.is_active = True
    user.is_verified = True
    user.department_id = "IT_SECURITY"
    user.employee_id = "EMP_001"
    user.performance_score = 100
    user.failed_login_attempts = 0
    user.account_locked = False
    user.requires_password_change = False
    user.last_login = datetime.utcnow()
    user.created_at = datetime.utcnow() - timedelta(days=30)
    user.updated_at = datetime.utcnow()
    user.is_superuser.return_value = True
    user.to_enterprise_dict.return_value = {
        'id': user.id,
        'email': user.email,
        'nombre': user.nombre,
        'apellido': user.apellido,
        'full_name': f"{user.nombre} {user.apellido}",
        'user_type': user.user_type.value,
        'is_active': user.is_active,
        'is_verified': user.is_verified,
        'security_clearance_level': user.security_clearance_level,
        'department_id': user.department_id,
        'employee_id': user.employee_id,
        'performance_score': user.performance_score,
        'failed_login_attempts': user.failed_login_attempts,
        'account_locked': user.account_locked,
        'requires_password_change': user.requires_password_change,
        'last_login': user.last_login,
        'created_at': user.created_at,
        'updated_at': user.updated_at
    }
    return user


@pytest.fixture
def high_level_admin():
    """Fixture for a high-level ADMIN with extensive privileges."""
    user = Mock(spec=User)
    user.id = str(uuid.uuid4())
    user.email = "admin.highlevel@mestore.com"
    user.nombre = "High"
    user.apellido = "Admin"
    user.user_type = UserType.ADMIN
    user.security_clearance_level = 4
    user.is_active = True
    user.is_verified = True
    user.department_id = "MANAGEMENT"
    user.employee_id = "EMP_002"
    user.performance_score = 95
    user.failed_login_attempts = 0
    user.account_locked = False
    user.requires_password_change = False
    user.last_login = datetime.utcnow() - timedelta(hours=2)
    user.created_at = datetime.utcnow() - timedelta(days=15)
    user.updated_at = datetime.utcnow() - timedelta(hours=1)
    user.is_superuser.return_value = False
    user.to_enterprise_dict.return_value = {
        'id': user.id,
        'email': user.email,
        'nombre': user.nombre,
        'apellido': user.apellido,
        'full_name': f"{user.nombre} {user.apellido}",
        'user_type': user.user_type.value,
        'is_active': user.is_active,
        'is_verified': user.is_verified,
        'security_clearance_level': user.security_clearance_level,
        'department_id': user.department_id,
        'employee_id': user.employee_id,
        'performance_score': user.performance_score,
        'failed_login_attempts': user.failed_login_attempts,
        'account_locked': user.account_locked,
        'requires_password_change': user.requires_password_change,
        'last_login': user.last_login,
        'created_at': user.created_at,
        'updated_at': user.updated_at
    }
    return user


@pytest.fixture
def medium_level_admin():
    """Fixture for a medium-level ADMIN with limited privileges."""
    user = Mock(spec=User)
    user.id = str(uuid.uuid4())
    user.email = "admin.medium@mestore.com"
    user.nombre = "Medium"
    user.apellido = "Admin"
    user.user_type = UserType.ADMIN
    user.security_clearance_level = 3
    user.is_active = True
    user.is_verified = True
    user.department_id = "OPERATIONS"
    user.employee_id = "EMP_003"
    user.performance_score = 88
    user.failed_login_attempts = 0
    user.account_locked = False
    user.requires_password_change = False
    user.last_login = datetime.utcnow() - timedelta(hours=6)
    user.created_at = datetime.utcnow() - timedelta(days=10)
    user.updated_at = datetime.utcnow() - timedelta(hours=3)
    user.is_superuser.return_value = False
    user.to_enterprise_dict.return_value = {
        'id': user.id,
        'email': user.email,
        'nombre': user.nombre,
        'apellido': user.apellido,
        'full_name': f"{user.nombre} {user.apellido}",
        'user_type': user.user_type.value,
        'is_active': user.is_active,
        'is_verified': user.is_verified,
        'security_clearance_level': user.security_clearance_level,
        'department_id': user.department_id,
        'employee_id': user.employee_id,
        'performance_score': user.performance_score,
        'failed_login_attempts': user.failed_login_attempts,
        'account_locked': user.account_locked,
        'requires_password_change': user.requires_password_change,
        'last_login': user.last_login,
        'created_at': user.created_at,
        'updated_at': user.updated_at
    }
    return user


@pytest.fixture
def low_level_admin():
    """Fixture for a low-level ADMIN with minimal privileges."""
    user = Mock(spec=User)
    user.id = str(uuid.uuid4())
    user.email = "admin.low@mestore.com"
    user.nombre = "Low"
    user.apellido = "Admin"
    user.user_type = UserType.ADMIN
    user.security_clearance_level = 2
    user.is_active = True
    user.is_verified = True
    user.department_id = "SUPPORT"
    user.employee_id = "EMP_004"
    user.performance_score = 75
    user.failed_login_attempts = 1
    user.account_locked = False
    user.requires_password_change = True
    user.last_login = datetime.utcnow() - timedelta(days=1)
    user.created_at = datetime.utcnow() - timedelta(days=5)
    user.updated_at = datetime.utcnow() - timedelta(hours=12)
    user.is_superuser.return_value = False
    user.to_enterprise_dict.return_value = {
        'id': user.id,
        'email': user.email,
        'nombre': user.nombre,
        'apellido': user.apellido,
        'full_name': f"{user.nombre} {user.apellido}",
        'user_type': user.user_type.value,
        'is_active': user.is_active,
        'is_verified': user.is_verified,
        'security_clearance_level': user.security_clearance_level,
        'department_id': user.department_id,
        'employee_id': user.employee_id,
        'performance_score': user.performance_score,
        'failed_login_attempts': user.failed_login_attempts,
        'account_locked': user.account_locked,
        'requires_password_change': user.requires_password_change,
        'last_login': user.last_login,
        'created_at': user.created_at,
        'updated_at': user.updated_at
    }
    return user


@pytest.fixture
def unauthorized_user():
    """Fixture for a non-admin user (VENDEDOR) with no admin privileges."""
    user = Mock(spec=User)
    user.id = str(uuid.uuid4())
    user.email = "vendor@mestore.com"
    user.nombre = "Regular"
    user.apellido = "Vendor"
    user.user_type = UserType.VENDOR
    user.security_clearance_level = 1
    user.is_active = True
    user.is_verified = True
    user.department_id = None
    user.employee_id = None
    user.performance_score = 85
    user.failed_login_attempts = 0
    user.account_locked = False
    user.requires_password_change = False
    user.last_login = datetime.utcnow() - timedelta(hours=1)
    user.created_at = datetime.utcnow() - timedelta(days=7)
    user.updated_at = datetime.utcnow() - timedelta(minutes=30)
    user.is_superuser.return_value = False
    return user


@pytest.fixture
def inactive_admin():
    """Fixture for an inactive admin user."""
    user = Mock(spec=User)
    user.id = str(uuid.uuid4())
    user.email = "admin.inactive@mestore.com"
    user.nombre = "Inactive"
    user.apellido = "Admin"
    user.user_type = UserType.ADMIN
    user.security_clearance_level = 3
    user.is_active = False  # Inactive
    user.is_verified = True
    user.department_id = "OPERATIONS"
    user.employee_id = "EMP_005"
    user.performance_score = 65
    user.failed_login_attempts = 0
    user.account_locked = True
    user.account_locked_until = datetime.utcnow() + timedelta(hours=24)
    user.requires_password_change = True
    user.last_login = datetime.utcnow() - timedelta(days=7)
    user.created_at = datetime.utcnow() - timedelta(days=20)
    user.updated_at = datetime.utcnow() - timedelta(days=3)
    user.is_superuser.return_value = False
    return user


# ================================================================================================
# ADMIN PERMISSION FIXTURES
# ================================================================================================

@pytest.fixture
def admin_permissions_list():
    """Fixture for a list of admin permissions."""
    permissions = []

    # Users management permissions
    user_read_permission = Mock(spec=AdminPermission)
    user_read_permission.id = str(uuid.uuid4())
    user_read_permission.name = "users.read.global"
    user_read_permission.description = "Read all users globally"
    user_read_permission.resource_type = ResourceType.USERS
    user_read_permission.action = PermissionAction.READ
    user_read_permission.scope = PermissionScope.GLOBAL
    user_read_permission.is_active = True
    permissions.append(user_read_permission)

    user_create_permission = Mock(spec=AdminPermission)
    user_create_permission.id = str(uuid.uuid4())
    user_create_permission.name = "users.create.global"
    user_create_permission.description = "Create new users globally"
    user_create_permission.resource_type = ResourceType.USERS
    user_create_permission.action = PermissionAction.CREATE
    user_create_permission.scope = PermissionScope.GLOBAL
    user_create_permission.is_active = True
    permissions.append(user_create_permission)

    user_manage_permission = Mock(spec=AdminPermission)
    user_manage_permission.id = str(uuid.uuid4())
    user_manage_permission.name = "users.manage.global"
    user_manage_permission.description = "Full user management globally"
    user_manage_permission.resource_type = ResourceType.USERS
    user_manage_permission.action = PermissionAction.MANAGE
    user_manage_permission.scope = PermissionScope.GLOBAL
    user_manage_permission.is_active = True
    permissions.append(user_manage_permission)

    return permissions


@pytest.fixture
def high_risk_permissions():
    """Fixture for high-risk admin permissions."""
    permissions = []

    system_admin_permission = Mock(spec=AdminPermission)
    system_admin_permission.id = str(uuid.uuid4())
    system_admin_permission.name = "system.admin.global"
    system_admin_permission.description = "Full system administration"
    system_admin_permission.resource_type = ResourceType.SYSTEM
    system_admin_permission.action = PermissionAction.MANAGE
    system_admin_permission.scope = PermissionScope.GLOBAL
    system_admin_permission.is_active = True
    system_admin_permission.risk_level = 5
    permissions.append(system_admin_permission)

    security_admin_permission = Mock(spec=AdminPermission)
    security_admin_permission.id = str(uuid.uuid4())
    security_admin_permission.name = "security.admin.global"
    security_admin_permission.description = "Security administration"
    security_admin_permission.resource_type = ResourceType.SECURITY
    security_admin_permission.action = PermissionAction.MANAGE
    security_admin_permission.scope = PermissionScope.GLOBAL
    security_admin_permission.is_active = True
    security_admin_permission.risk_level = 5
    permissions.append(security_admin_permission)

    return permissions


# ================================================================================================
# REQUEST FIXTURES FOR ADMIN OPERATIONS
# ================================================================================================

@pytest.fixture
def valid_admin_create_request():
    """Fixture for a valid admin creation request."""
    return AdminCreateRequest(
        email="newadmin@mestore.com",
        nombre="New",
        apellido="Admin",
        user_type=UserType.ADMIN,
        security_clearance_level=2,
        department_id="OPERATIONS",
        employee_id="EMP_NEW_001",
        telefono="+57300123456",
        ciudad="Bogotá",
        departamento="Cundinamarca",
        initial_permissions=["users.read.global"],
        force_password_change=True
    )


@pytest.fixture
def valid_superuser_create_request():
    """Fixture for a valid superuser creation request."""
    return AdminCreateRequest(
        email="newsuperuser@mestore.com",
        nombre="New",
        apellido="SuperUser",
        user_type=UserType.SUPERUSER,
        security_clearance_level=4,
        department_id="IT_SECURITY",
        employee_id="EMP_SUPER_001",
        initial_permissions=["users.read.global", "users.create.global"],
        force_password_change=True
    )


@pytest.fixture
def valid_admin_update_request():
    """Fixture for a valid admin update request."""
    return AdminUpdateRequest(
        nombre="Updated",
        apellido="Name",
        is_active=True,
        security_clearance_level=3,
        department_id="MANAGEMENT",
        performance_score=90,
        telefono="+57300654321",
        ciudad="Medellín",
        departamento="Antioquia"
    )


@pytest.fixture
def valid_permission_grant_request():
    """Fixture for a valid permission grant request."""
    return PermissionGrantRequest(
        permission_ids=[str(uuid.uuid4()), str(uuid.uuid4())],
        expires_at=datetime.utcnow() + timedelta(days=90),
        reason="Granting permissions for new project responsibilities"
    )


@pytest.fixture
def valid_permission_revoke_request():
    """Fixture for a valid permission revoke request."""
    return PermissionRevokeRequest(
        permission_ids=[str(uuid.uuid4())],
        reason="Removing permissions due to role change"
    )


@pytest.fixture
def valid_bulk_action_request():
    """Fixture for a valid bulk action request."""
    return BulkUserActionRequest(
        user_ids=[str(uuid.uuid4()) for _ in range(3)],
        action="activate",
        reason="Bulk activation after security review"
    )


# ================================================================================================
# INVALID REQUEST FIXTURES FOR NEGATIVE TESTING
# ================================================================================================

@pytest.fixture
def invalid_admin_create_requests():
    """Fixture for various invalid admin creation requests."""
    return {
        'duplicate_email': AdminCreateRequest(
            email="existing@mestore.com",
            nombre="Test",
            apellido="Admin",
            user_type=UserType.ADMIN
        ),
        'high_clearance': AdminCreateRequest(
            email="test@mestore.com",
            nombre="Test",
            apellido="Admin",
            user_type=UserType.ADMIN,
            security_clearance_level=5  # Too high for most users
        ),
        'superuser_request': AdminCreateRequest(
            email="test@mestore.com",
            nombre="Test",
            apellido="Admin",
            user_type=UserType.SUPERUSER  # Requires special privileges
        )
    }


@pytest.fixture
def invalid_bulk_action_requests():
    """Fixture for invalid bulk action requests."""
    return {
        'too_many_users': BulkUserActionRequest(
            user_ids=[str(uuid.uuid4()) for _ in range(101)],  # Exceeds limit
            action="activate",
            reason="Too many users for bulk operation"
        ),
        'empty_users': BulkUserActionRequest(
            user_ids=[],  # Empty list
            action="activate",
            reason="Empty user list"
        ),
        'invalid_action': BulkUserActionRequest(
            user_ids=[str(uuid.uuid4())],
            action="invalid_action",  # Invalid action
            reason="Testing invalid action"
        )
    }


# ================================================================================================
# MOCK SERVICE FIXTURES
# ================================================================================================

@pytest.fixture
def mock_admin_permission_service():
    """Mock admin permission service for testing."""
    service = Mock()
    service.validate_permission = Mock()
    service.get_user_permissions = Mock()
    service.grant_permission = Mock()
    service.revoke_permission = Mock()
    service._log_admin_activity = Mock()
    return service


@pytest.fixture
def mock_auth_service():
    """Mock auth service for testing."""
    service = Mock()
    service.generate_secure_password = Mock(return_value="TempPass123!")
    service.get_password_hash = Mock(return_value="hashed_password")
    return service


# ================================================================================================
# ADMIN ACTIVITY LOG FIXTURES
# ================================================================================================

@pytest.fixture
def sample_admin_activity_logs():
    """Fixture for sample admin activity logs."""
    logs = []

    log1 = Mock(spec=AdminActivityLog)
    log1.id = str(uuid.uuid4())
    log1.admin_user_id = str(uuid.uuid4())
    log1.action_type = AdminActionType.USER_MANAGEMENT
    log1.action_name = "create_admin"
    log1.description = "Created new admin user"
    log1.result = ActionResult.SUCCESS
    log1.risk_level = RiskLevel.HIGH
    log1.created_at = datetime.utcnow() - timedelta(hours=1)
    logs.append(log1)

    log2 = Mock(spec=AdminActivityLog)
    log2.id = str(uuid.uuid4())
    log2.admin_user_id = str(uuid.uuid4())
    log2.action_type = AdminActionType.SECURITY
    log2.action_name = "grant_permissions"
    log2.description = "Granted high-risk permissions"
    log2.result = ActionResult.SUCCESS
    log2.risk_level = RiskLevel.HIGH
    log2.created_at = datetime.utcnow() - timedelta(minutes=30)
    logs.append(log2)

    return logs


# ================================================================================================
# UTILITY FIXTURES
# ================================================================================================

@pytest.fixture
def sample_admin_response():
    """Fixture for a sample admin response."""
    return AdminResponse(
        id=str(uuid.uuid4()),
        email="sample@mestore.com",
        nombre="Sample",
        apellido="Admin",
        full_name="Sample Admin",
        user_type="ADMIN",
        is_active=True,
        is_verified=True,
        security_clearance_level=3,
        department_id="OPERATIONS",
        employee_id="EMP_SAMPLE",
        performance_score=85,
        failed_login_attempts=0,
        account_locked=False,
        requires_password_change=False,
        last_login=datetime.utcnow() - timedelta(hours=2),
        created_at=datetime.utcnow() - timedelta(days=10),
        updated_at=datetime.utcnow() - timedelta(hours=1),
        permission_count=5,
        last_activity=datetime.utcnow() - timedelta(minutes=15)
    )


@pytest.fixture
def mock_database_error():
    """Fixture for simulating database errors."""
    def _error_side_effect(*args, **kwargs):
        raise Exception("Database connection failed")
    return _error_side_effect


@pytest.fixture
def admin_test_data():
    """Comprehensive test data for admin operations."""
    return {
        'valid_emails': [
            "admin1@mestore.com",
            "admin2@mestore.com",
            "superuser@mestore.com"
        ],
        'invalid_emails': [
            "invalid-email",
            "missing@domain",
            "@missinguser.com",
            "spaces in@email.com"
        ],
        'valid_names': [
            "John",
            "María José",
            "José Luis",
            "Ana",
            "Carlos Alberto"
        ],
        'invalid_names': [
            "A",  # Too short
            "X" * 101,  # Too long
            "<script>alert('xss')</script>",  # XSS attempt
            "'; DROP TABLE users; --"  # SQL injection attempt
        ],
        'valid_security_levels': [1, 2, 3, 4, 5],
        'invalid_security_levels': [0, 6, 10, -1],
        'valid_departments': [
            "IT_SECURITY",
            "MANAGEMENT",
            "OPERATIONS",
            "SUPPORT",
            "FINANCE"
        ],
        'valid_actions': [
            "activate",
            "deactivate",
            "lock",
            "unlock"
        ],
        'invalid_actions': [
            "delete",
            "destroy",
            "escalate",
            "invalid_action"
        ]
    }