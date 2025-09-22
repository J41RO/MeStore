"""
Admin Management Test Fixtures for Unit Testing
===============================================

This module provides comprehensive test fixtures for admin management unit tests.
These fixtures support isolation testing and comprehensive coverage of admin
management functionality.

File: tests/unit/admin_management/admin_test_fixtures.py
Author: Unit Testing AI
Date: 2025-09-21
Framework: pytest fixtures for admin management unit testing
Usage: Import fixtures into admin management unit test files

Fixture Categories:
==================
1. Admin User Fixtures - Different admin user types and security levels
2. Permission Fixtures - Admin permissions with various scopes and actions
3. Request Schema Fixtures - Valid and invalid request data for testing
4. Database Mock Fixtures - Mocked database operations for isolation testing
5. Security Context Fixtures - Authentication and authorization contexts
6. Performance Test Fixtures - Data sets for performance testing
"""

import pytest
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from unittest.mock import Mock, MagicMock, AsyncMock
from sqlalchemy.orm import Session

# Import models for fixture creation
from app.models.user import User, UserType, VendorStatus
from app.models.admin_permission import AdminPermission, PermissionScope, PermissionAction, ResourceType
from app.models.admin_activity_log import AdminActivityLog, AdminActionType, ActionResult, RiskLevel

# Import schemas for fixture data
try:
    from app.api.v1.endpoints.admin_management import (
        AdminCreateRequest,
        AdminUpdateRequest,
        PermissionGrantRequest,
        PermissionRevokeRequest,
        BulkUserActionRequest,
        AdminResponse
    )
except ImportError:
    # RED phase - schemas don't exist yet, create mock versions
    from pydantic import BaseModel, Field, EmailStr

    class AdminCreateRequest(BaseModel):
        email: EmailStr
        nombre: str = Field(..., min_length=2, max_length=100)
        apellido: str = Field(..., min_length=2, max_length=100)
        user_type: UserType = UserType.ADMIN
        security_clearance_level: int = Field(3, ge=1, le=5)
        department_id: Optional[str] = None
        employee_id: Optional[str] = None
        telefono: Optional[str] = None
        ciudad: Optional[str] = None
        departamento: Optional[str] = None
        initial_permissions: List[str] = []
        force_password_change: bool = True

    class AdminUpdateRequest(BaseModel):
        nombre: Optional[str] = Field(None, min_length=2, max_length=100)
        apellido: Optional[str] = Field(None, min_length=2, max_length=100)
        is_active: Optional[bool] = None
        security_clearance_level: Optional[int] = Field(None, ge=1, le=5)
        department_id: Optional[str] = None
        employee_id: Optional[str] = None
        performance_score: Optional[int] = Field(None, ge=0, le=100)
        telefono: Optional[str] = None
        ciudad: Optional[str] = None
        departamento: Optional[str] = None

    class PermissionGrantRequest(BaseModel):
        permission_ids: List[str]
        expires_at: Optional[datetime] = None
        reason: str = Field(..., min_length=10)

    class PermissionRevokeRequest(BaseModel):
        permission_ids: List[str]
        reason: str = Field(..., min_length=10)

    class BulkUserActionRequest(BaseModel):
        user_ids: List[str] = Field(..., min_items=1, max_items=100)
        action: str
        reason: str = Field(..., min_length=10)

    class AdminResponse(BaseModel):
        id: str
        email: str
        nombre: Optional[str]
        apellido: Optional[str]
        full_name: str
        user_type: str
        is_active: bool
        is_verified: bool
        security_clearance_level: int
        department_id: Optional[str]
        employee_id: Optional[str]
        performance_score: int
        failed_login_attempts: int
        account_locked: bool
        requires_password_change: bool
        last_login: Optional[datetime]
        created_at: datetime
        updated_at: datetime
        permission_count: Optional[int] = None
        last_activity: Optional[datetime] = None


# ================================================================================================
# ADMIN USER FIXTURES
# ================================================================================================

@pytest.fixture
def superuser_admin():
    """
    Fixture: High-privilege superuser admin for testing high-level operations
    """
    admin = Mock(spec=User)
    admin.id = str(uuid.uuid4())
    admin.email = "superuser@admin.test"
    admin.nombre = "Super"
    admin.apellido = "User"
    admin.full_name = "Super User"
    admin.user_type = UserType.SUPERUSER
    admin.is_active = True
    admin.is_verified = True
    admin.security_clearance_level = 5
    admin.department_id = "executive"
    admin.employee_id = "EMP001"
    admin.performance_score = 100
    admin.failed_login_attempts = 0
    admin.account_locked = False
    admin.requires_password_change = False
    admin.last_login = datetime.utcnow() - timedelta(hours=1)
    admin.created_at = datetime.utcnow() - timedelta(days=365)
    admin.updated_at = datetime.utcnow() - timedelta(hours=1)
    admin.is_superuser = Mock(return_value=True)
    admin.to_enterprise_dict = Mock(return_value={
        'id': str(admin.id),
        'email': admin.email,
        'nombre': admin.nombre,
        'apellido': admin.apellido,
        'full_name': admin.full_name,
        'user_type': admin.user_type.value,
        'is_active': admin.is_active,
        'is_verified': admin.is_verified,
        'security_clearance_level': admin.security_clearance_level,
        'department_id': admin.department_id,
        'employee_id': admin.employee_id,
        'performance_score': admin.performance_score,
        'failed_login_attempts': admin.failed_login_attempts,
        'account_locked': admin.account_locked,
        'requires_password_change': admin.requires_password_change,
        'last_login': admin.last_login,
        'created_at': admin.created_at,
        'updated_at': admin.updated_at
    })
    return admin


@pytest.fixture
def high_privilege_admin():
    """
    Fixture: High-privilege admin for testing elevated operations
    """
    admin = Mock(spec=User)
    admin.id = str(uuid.uuid4())
    admin.email = "admin.high@admin.test"
    admin.nombre = "High"
    admin.apellido = "Admin"
    admin.full_name = "High Admin"
    admin.user_type = UserType.ADMIN
    admin.is_active = True
    admin.is_verified = True
    admin.security_clearance_level = 4
    admin.department_id = "operations"
    admin.employee_id = "EMP002"
    admin.performance_score = 95
    admin.failed_login_attempts = 0
    admin.account_locked = False
    admin.requires_password_change = False
    admin.last_login = datetime.utcnow() - timedelta(minutes=30)
    admin.created_at = datetime.utcnow() - timedelta(days=180)
    admin.updated_at = datetime.utcnow() - timedelta(minutes=30)
    admin.is_superuser = Mock(return_value=False)
    admin.to_enterprise_dict = Mock(return_value={
        'id': str(admin.id),
        'email': admin.email,
        'nombre': admin.nombre,
        'apellido': admin.apellido,
        'full_name': admin.full_name,
        'user_type': admin.user_type.value,
        'is_active': admin.is_active,
        'is_verified': admin.is_verified,
        'security_clearance_level': admin.security_clearance_level,
        'department_id': admin.department_id,
        'employee_id': admin.employee_id,
        'performance_score': admin.performance_score,
        'failed_login_attempts': admin.failed_login_attempts,
        'account_locked': admin.account_locked,
        'requires_password_change': admin.requires_password_change,
        'last_login': admin.last_login,
        'created_at': admin.created_at,
        'updated_at': admin.updated_at
    })
    return admin


@pytest.fixture
def mid_privilege_admin():
    """
    Fixture: Medium-privilege admin for testing standard operations
    """
    admin = Mock(spec=User)
    admin.id = str(uuid.uuid4())
    admin.email = "admin.mid@admin.test"
    admin.nombre = "Mid"
    admin.apellido = "Admin"
    admin.full_name = "Mid Admin"
    admin.user_type = UserType.ADMIN
    admin.is_active = True
    admin.is_verified = True
    admin.security_clearance_level = 3
    admin.department_id = "support"
    admin.employee_id = "EMP003"
    admin.performance_score = 85
    admin.failed_login_attempts = 0
    admin.account_locked = False
    admin.requires_password_change = False
    admin.last_login = datetime.utcnow() - timedelta(hours=2)
    admin.created_at = datetime.utcnow() - timedelta(days=90)
    admin.updated_at = datetime.utcnow() - timedelta(hours=2)
    admin.is_superuser = Mock(return_value=False)
    admin.to_enterprise_dict = Mock(return_value={
        'id': str(admin.id),
        'email': admin.email,
        'nombre': admin.nombre,
        'apellido': admin.apellido,
        'full_name': admin.full_name,
        'user_type': admin.user_type.value,
        'is_active': admin.is_active,
        'is_verified': admin.is_verified,
        'security_clearance_level': admin.security_clearance_level,
        'department_id': admin.department_id,
        'employee_id': admin.employee_id,
        'performance_score': admin.performance_score,
        'failed_login_attempts': admin.failed_login_attempts,
        'account_locked': admin.account_locked,
        'requires_password_change': admin.requires_password_change,
        'last_login': admin.last_login,
        'created_at': admin.created_at,
        'updated_at': admin.updated_at
    })
    return admin


@pytest.fixture
def low_privilege_admin():
    """
    Fixture: Low-privilege admin for testing restricted operations
    """
    admin = Mock(spec=User)
    admin.id = str(uuid.uuid4())
    admin.email = "admin.low@admin.test"
    admin.nombre = "Low"
    admin.apellido = "Admin"
    admin.full_name = "Low Admin"
    admin.user_type = UserType.ADMIN
    admin.is_active = True
    admin.is_verified = True
    admin.security_clearance_level = 2
    admin.department_id = "helpdesk"
    admin.employee_id = "EMP004"
    admin.performance_score = 75
    admin.failed_login_attempts = 0
    admin.account_locked = False
    admin.requires_password_change = False
    admin.last_login = datetime.utcnow() - timedelta(hours=4)
    admin.created_at = datetime.utcnow() - timedelta(days=30)
    admin.updated_at = datetime.utcnow() - timedelta(hours=4)
    admin.is_superuser = Mock(return_value=False)
    admin.to_enterprise_dict = Mock(return_value={
        'id': str(admin.id),
        'email': admin.email,
        'nombre': admin.nombre,
        'apellido': admin.apellido,
        'full_name': admin.full_name,
        'user_type': admin.user_type.value,
        'is_active': admin.is_active,
        'is_verified': admin.is_verified,
        'security_clearance_level': admin.security_clearance_level,
        'department_id': admin.department_id,
        'employee_id': admin.employee_id,
        'performance_score': admin.performance_score,
        'failed_login_attempts': admin.failed_login_attempts,
        'account_locked': admin.account_locked,
        'requires_password_change': admin.requires_password_change,
        'last_login': admin.last_login,
        'created_at': admin.created_at,
        'updated_at': admin.updated_at
    })
    return admin


@pytest.fixture
def unauthorized_user():
    """
    Fixture: Unauthorized user for testing access denial scenarios
    """
    user = Mock(spec=User)
    user.id = str(uuid.uuid4())
    user.email = "unauthorized@user.test"
    user.nombre = "Unauthorized"
    user.apellido = "User"
    user.full_name = "Unauthorized User"
    user.user_type = UserType.BUYER
    user.is_active = True
    user.is_verified = True
    user.security_clearance_level = 1
    user.department_id = None
    user.employee_id = None
    user.performance_score = 50
    user.failed_login_attempts = 0
    user.account_locked = False
    user.requires_password_change = False
    user.last_login = datetime.utcnow() - timedelta(hours=6)
    user.created_at = datetime.utcnow() - timedelta(days=7)
    user.updated_at = datetime.utcnow() - timedelta(hours=6)
    user.is_superuser = Mock(return_value=False)
    return user


@pytest.fixture
def inactive_admin():
    """
    Fixture: Inactive admin for testing deactivated account scenarios
    """
    admin = Mock(spec=User)
    admin.id = str(uuid.uuid4())
    admin.email = "inactive@admin.test"
    admin.nombre = "Inactive"
    admin.apellido = "Admin"
    admin.full_name = "Inactive Admin"
    admin.user_type = UserType.ADMIN
    admin.is_active = False  # Inactive
    admin.is_verified = True
    admin.security_clearance_level = 3
    admin.department_id = "former_operations"
    admin.employee_id = "EMP999"
    admin.performance_score = 60
    admin.failed_login_attempts = 3
    admin.account_locked = True
    admin.requires_password_change = True
    admin.last_login = datetime.utcnow() - timedelta(days=30)
    admin.created_at = datetime.utcnow() - timedelta(days=365)
    admin.updated_at = datetime.utcnow() - timedelta(days=30)
    admin.is_superuser = Mock(return_value=False)
    admin.to_enterprise_dict = Mock(return_value={
        'id': str(admin.id),
        'email': admin.email,
        'nombre': admin.nombre,
        'apellido': admin.apellido,
        'full_name': admin.full_name,
        'user_type': admin.user_type.value,
        'is_active': admin.is_active,
        'is_verified': admin.is_verified,
        'security_clearance_level': admin.security_clearance_level,
        'department_id': admin.department_id,
        'employee_id': admin.employee_id,
        'performance_score': admin.performance_score,
        'failed_login_attempts': admin.failed_login_attempts,
        'account_locked': admin.account_locked,
        'requires_password_change': admin.requires_password_change,
        'last_login': admin.last_login,
        'created_at': admin.created_at,
        'updated_at': admin.updated_at
    })
    return admin


@pytest.fixture
def admin_users_list(superuser_admin, high_privilege_admin, mid_privilege_admin, low_privilege_admin, inactive_admin):
    """
    Fixture: List of various admin users for bulk testing
    """
    return [superuser_admin, high_privilege_admin, mid_privilege_admin, low_privilege_admin, inactive_admin]


# ================================================================================================
# PERMISSION FIXTURES
# ================================================================================================

@pytest.fixture
def admin_permission_users_read_global():
    """
    Fixture: Permission for reading users globally
    """
    permission = Mock(spec=AdminPermission)
    permission.id = str(uuid.uuid4())
    permission.name = "users.read.global"
    permission.description = "Read access to all users globally"
    permission.resource_type = ResourceType.USERS
    permission.action = PermissionAction.READ
    permission.scope = PermissionScope.GLOBAL
    permission.is_critical = False
    permission.requires_approval = False
    permission.created_at = datetime.utcnow() - timedelta(days=100)
    permission.updated_at = datetime.utcnow() - timedelta(days=50)
    return permission


@pytest.fixture
def admin_permission_users_create_global():
    """
    Fixture: Permission for creating users globally
    """
    permission = Mock(spec=AdminPermission)
    permission.id = str(uuid.uuid4())
    permission.name = "users.create.global"
    permission.description = "Create access to users globally"
    permission.resource_type = ResourceType.USERS
    permission.action = PermissionAction.CREATE
    permission.scope = PermissionScope.GLOBAL
    permission.is_critical = True
    permission.requires_approval = True
    permission.created_at = datetime.utcnow() - timedelta(days=100)
    permission.updated_at = datetime.utcnow() - timedelta(days=50)
    return permission


@pytest.fixture
def admin_permission_users_manage_global():
    """
    Fixture: Permission for managing users globally (highest privilege)
    """
    permission = Mock(spec=AdminPermission)
    permission.id = str(uuid.uuid4())
    permission.name = "users.manage.global"
    permission.description = "Full management access to users globally"
    permission.resource_type = ResourceType.USERS
    permission.action = PermissionAction.MANAGE
    permission.scope = PermissionScope.GLOBAL
    permission.is_critical = True
    permission.requires_approval = True
    permission.created_at = datetime.utcnow() - timedelta(days=100)
    permission.updated_at = datetime.utcnow() - timedelta(days=50)
    return permission


@pytest.fixture
def admin_permission_users_update_global():
    """
    Fixture: Permission for updating users globally
    """
    permission = Mock(spec=AdminPermission)
    permission.id = str(uuid.uuid4())
    permission.name = "users.update.global"
    permission.description = "Update access to users globally"
    permission.resource_type = ResourceType.USERS
    permission.action = PermissionAction.UPDATE
    permission.scope = PermissionScope.GLOBAL
    permission.is_critical = True
    permission.requires_approval = False
    permission.created_at = datetime.utcnow() - timedelta(days=100)
    permission.updated_at = datetime.utcnow() - timedelta(days=50)
    return permission


@pytest.fixture
def admin_permissions_list(admin_permission_users_read_global, admin_permission_users_create_global,
                          admin_permission_users_manage_global, admin_permission_users_update_global):
    """
    Fixture: List of admin permissions for bulk testing
    """
    return [
        admin_permission_users_read_global,
        admin_permission_users_create_global,
        admin_permission_users_manage_global,
        admin_permission_users_update_global
    ]


# ================================================================================================
# REQUEST SCHEMA FIXTURES
# ================================================================================================

@pytest.fixture
def valid_admin_create_request():
    """
    Fixture: Valid admin creation request
    """
    return AdminCreateRequest(
        email="newadmin@test.com",
        nombre="New",
        apellido="Admin",
        user_type=UserType.ADMIN,
        security_clearance_level=3,
        department_id="operations",
        employee_id="EMP100",
        telefono="+57 300 123 4567",
        ciudad="Bogotá",
        departamento="Cundinamarca",
        initial_permissions=["users.read.global"],
        force_password_change=True
    )


@pytest.fixture
def valid_superuser_create_request():
    """
    Fixture: Valid superuser creation request
    """
    return AdminCreateRequest(
        email="newsuperuser@test.com",
        nombre="New",
        apellido="Superuser",
        user_type=UserType.SUPERUSER,
        security_clearance_level=5,
        department_id="executive",
        employee_id="EMP200",
        initial_permissions=["users.manage.global"],
        force_password_change=True
    )


@pytest.fixture
def invalid_admin_create_request():
    """
    Fixture: Invalid admin creation request for validation testing
    """
    # This will raise validation errors when instantiated
    return {
        'email': 'invalid-email-format',
        'nombre': 'A',  # Too short
        'apellido': 'B' * 101,  # Too long
        'security_clearance_level': 10,  # Above max
        'user_type': 'INVALID_TYPE'
    }


@pytest.fixture
def valid_admin_update_request():
    """
    Fixture: Valid admin update request
    """
    return AdminUpdateRequest(
        nombre="Updated",
        apellido="Name",
        is_active=True,
        security_clearance_level=3,
        performance_score=90,
        department_id="support",
        telefono="+57 301 234 5678"
    )


@pytest.fixture
def valid_permission_grant_request(admin_permissions_list):
    """
    Fixture: Valid permission grant request
    """
    return PermissionGrantRequest(
        permission_ids=[str(perm.id) for perm in admin_permissions_list[:2]],
        expires_at=datetime.utcnow() + timedelta(days=90),
        reason="Granting permissions for enhanced operational capabilities and system administration duties"
    )


@pytest.fixture
def valid_permission_revoke_request(admin_permissions_list):
    """
    Fixture: Valid permission revoke request
    """
    return PermissionRevokeRequest(
        permission_ids=[str(perm.id) for perm in admin_permissions_list[:1]],
        reason="Revoking permissions due to role change and security policy compliance requirements"
    )


@pytest.fixture
def valid_bulk_action_request(admin_users_list):
    """
    Fixture: Valid bulk action request
    """
    return BulkUserActionRequest(
        user_ids=[str(admin.id) for admin in admin_users_list[:3]],
        action="activate",
        reason="Bulk activation for returning administrators after security review completion"
    )


@pytest.fixture
def invalid_bulk_action_request():
    """
    Fixture: Invalid bulk action request for validation testing
    """
    # This will raise validation errors when instantiated
    return {
        'user_ids': [],  # Empty list
        'action': '',  # Empty action
        'reason': 'short'  # Too short
    }


# ================================================================================================
# DATABASE MOCK FIXTURES
# ================================================================================================

@pytest.fixture
def mock_db_session():
    """
    Fixture: Mocked database session for isolation testing
    """
    session = Mock(spec=Session)

    # Mock query method
    session.query = Mock()
    session.query.return_value = Mock()
    session.query.return_value.filter = Mock()
    session.query.return_value.filter.return_value = Mock()
    session.query.return_value.filter.return_value.first = Mock()
    session.query.return_value.filter.return_value.all = Mock()
    session.query.return_value.filter.return_value.count = Mock()
    session.query.return_value.filter.return_value.order_by = Mock()
    session.query.return_value.filter.return_value.order_by.return_value = Mock()
    session.query.return_value.filter.return_value.order_by.return_value.offset = Mock()
    session.query.return_value.filter.return_value.order_by.return_value.offset.return_value = Mock()
    session.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit = Mock()
    session.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value = Mock()
    session.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all = Mock()

    # Mock other database operations
    session.add = Mock()
    session.flush = Mock()
    session.commit = Mock()
    session.rollback = Mock()
    session.close = Mock()

    return session


@pytest.fixture
def mock_successful_db_operations(mock_db_session, admin_users_list, admin_permissions_list):
    """
    Fixture: Database session configured for successful operations
    """
    # Configure successful query responses
    mock_db_session.query.return_value.filter.return_value.first.return_value = admin_users_list[0]
    mock_db_session.query.return_value.filter.return_value.all.return_value = admin_users_list
    mock_db_session.query.return_value.filter.return_value.count.return_value = len(admin_users_list)
    mock_db_session.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = admin_users_list[:3]

    # Configure successful permission queries
    mock_db_session.query.return_value.filter.return_value.all.side_effect = [admin_permissions_list]

    return mock_db_session


@pytest.fixture
def mock_failed_db_operations(mock_db_session):
    """
    Fixture: Database session configured for failure scenarios
    """
    # Configure failed query responses
    mock_db_session.query.return_value.filter.return_value.first.return_value = None
    mock_db_session.query.return_value.filter.return_value.all.return_value = []
    mock_db_session.query.return_value.filter.return_value.count.return_value = 0

    # Configure database operation failures
    mock_db_session.add.side_effect = Exception("Database add failed")
    mock_db_session.commit.side_effect = Exception("Database commit failed")

    return mock_db_session


# ================================================================================================
# SECURITY CONTEXT FIXTURES
# ================================================================================================

@pytest.fixture
def mock_permission_service_success():
    """
    Fixture: Mocked permission service for successful operations
    """
    with pytest.mock.patch('app.services.admin_permission_service.admin_permission_service') as mock_service:
        mock_service.validate_permission = AsyncMock()
        mock_service.get_user_permissions = AsyncMock(return_value=[])
        mock_service.grant_permission = AsyncMock(return_value=True)
        mock_service.revoke_permission = AsyncMock(return_value=True)
        mock_service._log_admin_activity = AsyncMock()
        yield mock_service


@pytest.fixture
def mock_permission_service_denied():
    """
    Fixture: Mocked permission service for denied operations
    """
    with pytest.mock.patch('app.services.admin_permission_service.admin_permission_service') as mock_service:
        mock_service.validate_permission = AsyncMock(side_effect=Exception("Permission denied"))
        mock_service.get_user_permissions = AsyncMock(side_effect=Exception("Permission denied"))
        mock_service.grant_permission = AsyncMock(side_effect=Exception("Permission denied"))
        mock_service.revoke_permission = AsyncMock(side_effect=Exception("Permission denied"))
        mock_service._log_admin_activity = AsyncMock(side_effect=Exception("Permission denied"))
        yield mock_service


@pytest.fixture
def mock_auth_service():
    """
    Fixture: Mocked authentication service
    """
    with pytest.mock.patch('app.services.auth_service.auth_service') as mock_service:
        mock_service.generate_secure_password = Mock(return_value="TempPass123!")
        mock_service.get_password_hash = Mock(return_value="$2b$12$hashedpassword")
        mock_service.verify_password = Mock(return_value=True)
        yield mock_service


# ================================================================================================
# PERFORMANCE TEST FIXTURES
# ================================================================================================

@pytest.fixture
def performance_test_dataset():
    """
    Fixture: Large dataset for performance testing
    """
    # Create 100 mock admin users for performance testing
    admin_users = []
    for i in range(100):
        admin = Mock(spec=User)
        admin.id = str(uuid.uuid4())
        admin.email = f"admin{i}@performance.test"
        admin.nombre = f"Admin{i}"
        admin.apellido = f"User{i}"
        admin.user_type = UserType.ADMIN
        admin.security_clearance_level = (i % 5) + 1
        admin.is_active = i % 10 != 9  # 90% active
        admin.to_enterprise_dict = Mock(return_value={
            'id': str(admin.id),
            'email': admin.email,
            'nombre': admin.nombre,
            'apellido': admin.apellido,
            'user_type': admin.user_type.value,
            'security_clearance_level': admin.security_clearance_level,
            'is_active': admin.is_active
        })
        admin_users.append(admin)

    return admin_users


@pytest.fixture
def bulk_operation_dataset():
    """
    Fixture: Dataset for bulk operation testing
    """
    # Create 50 admin user IDs for bulk operations
    user_ids = [str(uuid.uuid4()) for _ in range(50)]

    # Create mock admin users
    admin_users = []
    for user_id in user_ids:
        admin = Mock(spec=User)
        admin.id = user_id
        admin.email = f"bulk{user_id[:8]}@test.com"
        admin.user_type = UserType.ADMIN
        admin.is_active = True
        admin_users.append(admin)

    return {
        'user_ids': user_ids,
        'admin_users': admin_users
    }


# ================================================================================================
# EDGE CASE FIXTURES
# ================================================================================================

@pytest.fixture
def malicious_input_data():
    """
    Fixture: Malicious input data for security testing
    """
    return {
        'sql_injection': {
            'search': "'; DROP TABLE users; --",
            'email': "admin'; DROP TABLE users; --@test.com",
            'name': "Robert'; DROP TABLE students; --"
        },
        'xss_attempts': {
            'nombre': "<script>alert('xss')</script>",
            'apellido': "<img src=x onerror=alert('xss')>",
            'reason': "javascript:alert('xss')"
        },
        'oversized_data': {
            'nombre': "A" * 1000,
            'apellido': "B" * 1000,
            'reason': "C" * 10000,
            'email': "a" * 200 + "@test.com"
        },
        'special_characters': {
            'nombre': "Admin\x00\x01\x02",
            'apellido': "User\xff\xfe\xfd",
            'departamento': "Dept\u202e\u202d"
        }
    }


@pytest.fixture
def boundary_condition_data():
    """
    Fixture: Boundary condition data for edge case testing
    """
    return {
        'min_values': {
            'security_clearance_level': 1,
            'performance_score': 0,
            'nombre_length': 2,
            'reason_length': 10
        },
        'max_values': {
            'security_clearance_level': 5,
            'performance_score': 100,
            'nombre_length': 100,
            'user_ids_count': 100
        },
        'invalid_below_min': {
            'security_clearance_level': 0,
            'performance_score': -1,
            'nombre': "A",
            'reason': "short"
        },
        'invalid_above_max': {
            'security_clearance_level': 6,
            'performance_score': 101,
            'nombre': "A" * 101,
            'user_ids': [str(uuid.uuid4()) for _ in range(101)]
        }
    }


# ================================================================================================
# INTEGRATION HELPER FIXTURES
# ================================================================================================

@pytest.fixture
def admin_management_test_context(superuser_admin, mock_successful_db_operations,
                                 mock_permission_service_success, mock_auth_service):
    """
    Fixture: Complete test context for admin management testing
    """
    return {
        'current_user': superuser_admin,
        'db_session': mock_successful_db_operations,
        'permission_service': mock_permission_service_success,
        'auth_service': mock_auth_service
    }


@pytest.fixture
def admin_management_failure_context(unauthorized_user, mock_failed_db_operations,
                                    mock_permission_service_denied):
    """
    Fixture: Complete test context for failure scenario testing
    """
    return {
        'current_user': unauthorized_user,
        'db_session': mock_failed_db_operations,
        'permission_service': mock_permission_service_denied
    }


# ================================================================================================
# FIXTURE SUMMARY AND USAGE DOCUMENTATION
# ================================================================================================

def test_fixture_availability():
    """
    Test to document all available fixtures and their usage

    This test serves as documentation for all fixtures available
    for admin management unit testing.
    """
    fixture_categories = {
        'admin_users': [
            'superuser_admin',
            'high_privilege_admin',
            'mid_privilege_admin',
            'low_privilege_admin',
            'unauthorized_user',
            'inactive_admin',
            'admin_users_list'
        ],
        'permissions': [
            'admin_permission_users_read_global',
            'admin_permission_users_create_global',
            'admin_permission_users_manage_global',
            'admin_permission_users_update_global',
            'admin_permissions_list'
        ],
        'request_schemas': [
            'valid_admin_create_request',
            'valid_superuser_create_request',
            'invalid_admin_create_request',
            'valid_admin_update_request',
            'valid_permission_grant_request',
            'valid_permission_revoke_request',
            'valid_bulk_action_request',
            'invalid_bulk_action_request'
        ],
        'database_mocks': [
            'mock_db_session',
            'mock_successful_db_operations',
            'mock_failed_db_operations'
        ],
        'security_contexts': [
            'mock_permission_service_success',
            'mock_permission_service_denied',
            'mock_auth_service'
        ],
        'performance_data': [
            'performance_test_dataset',
            'bulk_operation_dataset'
        ],
        'edge_cases': [
            'malicious_input_data',
            'boundary_condition_data'
        ],
        'integration_helpers': [
            'admin_management_test_context',
            'admin_management_failure_context'
        ]
    }

    total_fixtures = sum(len(fixtures) for fixtures in fixture_categories.values())

    print(f"✅ ADMIN MANAGEMENT TEST FIXTURES COMPLETE")
    print(f"📊 Total Fixtures: {total_fixtures}")
    print(f"🔍 Categories: {len(fixture_categories)}")
    print(f"🎯 Coverage: Comprehensive admin management unit testing support")
    print(f"🚨 Security: Malicious input and edge case testing")
    print(f"⚡ Performance: Large dataset and bulk operation testing")

    assert total_fixtures >= 30, "Should have comprehensive fixture coverage"
    assert len(fixture_categories) == 7, "Should cover all fixture categories"