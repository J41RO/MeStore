"""
REFACTOR Phase: Consolidated Admin Test Fixtures and Utilities
=============================================================

This module provides consolidated test fixtures and utilities for admin endpoint
testing. It eliminates duplication, provides consistent test data, and offers
reusable testing utilities for all admin management test scenarios.

File: tests/fixtures/admin_test_fixtures_refactored.py
Author: TDD Specialist AI
Date: 2025-09-21
Phase: REFACTOR - Test consolidation and optimization
Framework: pytest + TDD RED-GREEN-REFACTOR methodology

Features:
- Consolidated admin user fixtures
- Shared permission test data
- Mock service utilities
- Database test isolation
- Performance test utilities
- Security test helpers
"""

import pytest
import uuid
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Generator, AsyncGenerator
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from pydantic import BaseModel

# Import models and test dependencies
from app.models.user import User, UserType, VendorStatus
from app.models.admin_permission import AdminPermission, PermissionScope, PermissionAction, ResourceType
from app.models.admin_activity_log import AdminActivityLog, AdminActionType, RiskLevel
from app.core.admin_utils import AdminValidationResult, AdminOperationMetrics
from app.services.admin_permission_service import admin_permission_service


# ============================================================================
# SHARED TEST DATA CLASSES
# ============================================================================

class AdminTestData:
    """Consolidated test data for admin operations."""

    @staticmethod
    def valid_admin_create_data() -> Dict[str, Any]:
        """Standard valid admin creation data."""
        return {
            "email": f"admin.test.{uuid.uuid4().hex[:8]}@mestore.com",
            "nombre": "Test",
            "apellido": "Admin",
            "user_type": "ADMIN",
            "security_clearance_level": 3,
            "department_id": "IT",
            "employee_id": f"EMP{uuid.uuid4().hex[:6].upper()}",
            "telefono": "+57 300 123 4567",
            "ciudad": "Bogotá",
            "departamento": "Cundinamarca",
            "initial_permissions": ["users.read.own"],
            "force_password_change": True
        }

    @staticmethod
    def valid_admin_update_data() -> Dict[str, Any]:
        """Standard valid admin update data."""
        return {
            "nombre": "Updated",
            "apellido": "Admin",
            "is_active": True,
            "security_clearance_level": 4,
            "performance_score": 95,
            "telefono": "+57 301 987 6543",
            "ciudad": "Medellín",
            "departamento": "Antioquia"
        }

    @staticmethod
    def permission_grant_data() -> Dict[str, Any]:
        """Standard permission grant request data."""
        return {
            "permission_ids": [str(uuid.uuid4()) for _ in range(3)],
            "expires_at": (datetime.utcnow() + timedelta(days=90)).isoformat(),
            "reason": "Required for admin testing operations"
        }

    @staticmethod
    def permission_revoke_data() -> Dict[str, Any]:
        """Standard permission revoke request data."""
        return {
            "permission_ids": [str(uuid.uuid4()) for _ in range(2)],
            "reason": "No longer needed for current role"
        }

    @staticmethod
    def bulk_action_data() -> Dict[str, Any]:
        """Standard bulk action request data."""
        return {
            "user_ids": [str(uuid.uuid4()) for _ in range(5)],
            "action": "activate",
            "reason": "Bulk activation for testing purposes"
        }

    @staticmethod
    def admin_response_data() -> Dict[str, Any]:
        """Standard admin response data structure."""
        user_id = str(uuid.uuid4())
        return {
            "id": user_id,
            "email": f"admin.{user_id[:8]}@mestore.com",
            "nombre": "Test",
            "apellido": "Admin",
            "full_name": "Test Admin",
            "user_type": "ADMIN",
            "is_active": True,
            "is_verified": True,
            "security_clearance_level": 3,
            "department_id": "IT",
            "employee_id": f"EMP{user_id[:6].upper()}",
            "performance_score": 100,
            "failed_login_attempts": 0,
            "account_locked": False,
            "requires_password_change": True,
            "last_login": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "permission_count": 5,
            "last_activity": datetime.utcnow() - timedelta(hours=2)
        }


class PermissionTestData:
    """Test data for permission operations."""

    @staticmethod
    def create_permission_set() -> List[Dict[str, Any]]:
        """Create a standard set of test permissions."""
        permissions = []

        for i, (resource, action, scope) in enumerate([
            ("USERS", "READ", "GLOBAL"),
            ("USERS", "CREATE", "GLOBAL"),
            ("USERS", "UPDATE", "OWN"),
            ("PRODUCTS", "READ", "GLOBAL"),
            ("ANALYTICS", "READ", "DEPARTMENT")
        ]):
            permissions.append({
                "id": str(uuid.uuid4()),
                "name": f"{resource.lower()}.{action.lower()}.{scope.lower()}",
                "description": f"Permission to {action.lower()} {resource.lower()} at {scope.lower()} scope",
                "resource_type": resource,
                "action": action,
                "scope": scope,
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })

        return permissions


# ============================================================================
# MOCK UTILITIES AND FACTORIES
# ============================================================================

class AdminMockFactory:
    """Factory for creating consistent admin-related mocks."""

    @staticmethod
    def create_admin_user_mock(
        user_id: Optional[str] = None,
        user_type: UserType = UserType.ADMIN,
        security_clearance_level: int = 3,
        is_active: bool = True,
        email: Optional[str] = None
    ) -> Mock:
        """Create a mock admin user with specified properties."""
        if user_id is None:
            user_id = str(uuid.uuid4())
        if email is None:
            email = f"admin.{user_id[:8]}@mestore.com"

        mock_user = Mock(spec=User)
        mock_user.id = user_id
        mock_user.email = email
        mock_user.nombre = "Test"
        mock_user.apellido = "Admin"
        mock_user.user_type = user_type
        mock_user.security_clearance_level = security_clearance_level
        mock_user.is_active = is_active
        mock_user.is_verified = True
        mock_user.department_id = "IT"
        mock_user.employee_id = f"EMP{user_id[:6].upper()}"
        mock_user.performance_score = 100
        mock_user.failed_login_attempts = 0
        mock_user.account_locked = False
        mock_user.requires_password_change = True
        mock_user.last_login = None
        mock_user.created_at = datetime.utcnow()
        mock_user.updated_at = datetime.utcnow()

        # Mock methods
        mock_user.is_superuser.return_value = (user_type == UserType.SUPERUSER)
        mock_user.to_enterprise_dict.return_value = AdminTestData.admin_response_data()

        return mock_user

    @staticmethod
    def create_permission_mock(
        permission_id: Optional[str] = None,
        name: Optional[str] = None,
        resource: ResourceType = ResourceType.USERS,
        action: PermissionAction = PermissionAction.READ,
        scope: PermissionScope = PermissionScope.GLOBAL
    ) -> Mock:
        """Create a mock permission with specified properties."""
        if permission_id is None:
            permission_id = str(uuid.uuid4())
        if name is None:
            name = f"{resource.value.lower()}.{action.value.lower()}.{scope.value.lower()}"

        mock_permission = Mock(spec=AdminPermission)
        mock_permission.id = permission_id
        mock_permission.name = name
        mock_permission.description = f"Test permission: {name}"
        mock_permission.resource_type = resource
        mock_permission.action = action
        mock_permission.scope = scope
        mock_permission.is_active = True
        mock_permission.created_at = datetime.utcnow()
        mock_permission.updated_at = datetime.utcnow()

        return mock_permission

    @staticmethod
    def create_db_session_mock() -> Mock:
        """Create a mock database session with common query methods."""
        mock_db = Mock(spec=Session)
        mock_query = Mock()
        mock_db.query.return_value = mock_query

        # Configure common query methods
        mock_query.filter.return_value = mock_query
        mock_query.filter_by.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.count.return_value = 0
        mock_query.first.return_value = None
        mock_query.all.return_value = []
        mock_query.scalar.return_value = None
        mock_query.scalar_one_or_none.return_value = None

        # Configure session methods
        mock_db.add.return_value = None
        mock_db.flush.return_value = None
        mock_db.commit.return_value = None
        mock_db.rollback.return_value = None
        mock_db.execute.return_value = Mock()

        return mock_db

    @staticmethod
    def create_permission_service_mock() -> Mock:
        """Create a mock admin permission service."""
        mock_service = Mock()

        # Configure async methods
        mock_service.validate_permission = AsyncMock(return_value=None)
        mock_service.get_user_permissions = AsyncMock(return_value=[])
        mock_service.grant_permission = AsyncMock(return_value=True)
        mock_service.revoke_permission = AsyncMock(return_value=True)
        mock_service._log_admin_activity = AsyncMock(return_value=None)

        return mock_service


# ============================================================================
# TEST FIXTURES
# ============================================================================

@pytest.fixture
def admin_test_data():
    """Provide access to AdminTestData class."""
    return AdminTestData


@pytest.fixture
def permission_test_data():
    """Provide access to PermissionTestData class."""
    return PermissionTestData


@pytest.fixture
def admin_mock_factory():
    """Provide access to AdminMockFactory class."""
    return AdminMockFactory


@pytest.fixture
def mock_current_admin_user(admin_mock_factory):
    """Create a mock current admin user for testing."""
    return admin_mock_factory.create_admin_user_mock(
        user_type=UserType.ADMIN,
        security_clearance_level=4
    )


@pytest.fixture
def mock_current_superuser(admin_mock_factory):
    """Create a mock current superuser for testing."""
    return admin_mock_factory.create_admin_user_mock(
        user_type=UserType.SUPERUSER,
        security_clearance_level=5
    )


@pytest.fixture
def mock_target_admin_user(admin_mock_factory):
    """Create a mock target admin user for testing."""
    return admin_mock_factory.create_admin_user_mock(
        user_type=UserType.ADMIN,
        security_clearance_level=3
    )


@pytest.fixture
def mock_db_session(admin_mock_factory):
    """Create a mock database session for testing."""
    return admin_mock_factory.create_db_session_mock()


@pytest.fixture
def mock_permission_service(admin_mock_factory):
    """Create a mock permission service for testing."""
    return admin_mock_factory.create_permission_service_mock()


@pytest.fixture
def sample_permissions(admin_mock_factory):
    """Create a list of sample permission mocks."""
    return [
        admin_mock_factory.create_permission_mock(
            resource=ResourceType.USERS,
            action=PermissionAction.READ,
            scope=PermissionScope.GLOBAL
        ),
        admin_mock_factory.create_permission_mock(
            resource=ResourceType.USERS,
            action=PermissionAction.CREATE,
            scope=PermissionScope.GLOBAL
        ),
        admin_mock_factory.create_permission_mock(
            resource=ResourceType.PRODUCTS,
            action=PermissionAction.READ,
            scope=PermissionScope.OWN
        )
    ]


# ============================================================================
# PERFORMANCE TEST UTILITIES
# ============================================================================

class PerformanceTestHelper:
    """Helper utilities for performance testing."""

    @staticmethod
    def measure_execution_time(func, *args, **kwargs):
        """Measure execution time of a function."""
        import time
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        return result, execution_time

    @staticmethod
    async def measure_async_execution_time(func, *args, **kwargs):
        """Measure execution time of an async function."""
        import time
        start_time = time.time()
        result = await func(*args, **kwargs)
        execution_time = time.time() - start_time
        return result, execution_time

    @staticmethod
    def create_performance_threshold_validator(max_time_ms: int):
        """Create a validator for performance thresholds."""
        def validator(execution_time: float) -> bool:
            return (execution_time * 1000) <= max_time_ms
        return validator


@pytest.fixture
def performance_helper():
    """Provide access to PerformanceTestHelper."""
    return PerformanceTestHelper


# ============================================================================
# SECURITY TEST UTILITIES
# ============================================================================

class SecurityTestHelper:
    """Helper utilities for security testing."""

    @staticmethod
    def create_permission_denied_error():
        """Create a standard permission denied error."""
        from app.services.admin_permission_service import PermissionDeniedError
        return PermissionDeniedError("Insufficient permissions for operation")

    @staticmethod
    def create_unauthorized_user_mock():
        """Create a mock user without admin privileges."""
        mock_user = Mock(spec=User)
        mock_user.id = str(uuid.uuid4())
        mock_user.email = "user@mestore.com"
        mock_user.user_type = UserType.VENDOR
        mock_user.security_clearance_level = 1
        mock_user.is_active = True
        mock_user.is_superuser.return_value = False
        return mock_user

    @staticmethod
    def create_locked_user_mock():
        """Create a mock locked admin user."""
        mock_user = Mock(spec=User)
        mock_user.id = str(uuid.uuid4())
        mock_user.email = "locked.admin@mestore.com"
        mock_user.user_type = UserType.ADMIN
        mock_user.security_clearance_level = 3
        mock_user.is_active = False
        mock_user.account_locked = True
        mock_user.account_locked_until = datetime.utcnow() + timedelta(hours=24)
        mock_user.is_superuser.return_value = False
        return mock_user

    @staticmethod
    def validate_security_clearance_hierarchy(
        current_level: int,
        target_level: int,
        operation: str
    ) -> bool:
        """Validate security clearance hierarchy for operations."""
        if operation in ['create', 'update', 'delete']:
            return current_level > target_level
        elif operation in ['read', 'list']:
            return current_level >= target_level
        else:
            return current_level >= 3  # Minimum level for admin operations


@pytest.fixture
def security_helper():
    """Provide access to SecurityTestHelper."""
    return SecurityTestHelper


# ============================================================================
# DATABASE TEST ISOLATION UTILITIES
# ============================================================================

class DatabaseTestHelper:
    """Helper utilities for database test isolation."""

    @staticmethod
    def create_test_transaction_context():
        """Create a test transaction context for isolation."""
        return Mock()

    @staticmethod
    def setup_test_data_isolation():
        """Setup test data isolation patterns."""
        return {
            "isolation_level": "READ_COMMITTED",
            "autocommit": False,
            "rollback_on_teardown": True
        }

    @staticmethod
    def cleanup_test_data(db_session: Session, test_entities: List[Any]):
        """Clean up test data after test execution."""
        try:
            for entity in test_entities:
                if hasattr(entity, 'id'):
                    db_session.delete(entity)
            db_session.commit()
        except Exception:
            db_session.rollback()


@pytest.fixture
def db_helper():
    """Provide access to DatabaseTestHelper."""
    return DatabaseTestHelper


# ============================================================================
# INTEGRATION TEST UTILITIES
# ============================================================================

class IntegrationTestHelper:
    """Helper utilities for integration testing."""

    @staticmethod
    def create_test_client_with_auth(admin_user: User):
        """Create a test client with admin authentication."""
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)

        # Mock authentication
        def mock_get_current_user():
            return admin_user

        app.dependency_overrides[get_current_user] = mock_get_current_user

        return client

    @staticmethod
    def create_full_test_scenario(
        admin_count: int = 5,
        permission_count: int = 10,
        activity_log_count: int = 20
    ) -> Dict[str, List[Any]]:
        """Create a full test scenario with multiple entities."""
        scenario = {
            "admins": [],
            "permissions": [],
            "activity_logs": []
        }

        # Create admin users
        for i in range(admin_count):
            admin = AdminMockFactory.create_admin_user_mock(
                user_type=UserType.ADMIN if i < admin_count - 1 else UserType.SUPERUSER,
                security_clearance_level=3 + (i % 3)
            )
            scenario["admins"].append(admin)

        # Create permissions
        for i in range(permission_count):
            permission = AdminMockFactory.create_permission_mock()
            scenario["permissions"].append(permission)

        # Create activity logs
        for i in range(activity_log_count):
            log = Mock(spec=AdminActivityLog)
            log.id = str(uuid.uuid4())
            log.admin_user_id = scenario["admins"][i % admin_count].id
            log.action_type = AdminActionType.USER_MANAGEMENT
            log.action_name = f"test_action_{i}"
            log.risk_level = RiskLevel.MEDIUM
            log.created_at = datetime.utcnow() - timedelta(hours=i)
            scenario["activity_logs"].append(log)

        return scenario


@pytest.fixture
def integration_helper():
    """Provide access to IntegrationTestHelper."""
    return IntegrationTestHelper


# ============================================================================
# ASYNC TEST UTILITIES
# ============================================================================

@pytest.fixture
def event_loop():
    """Create an event loop for async testing."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def async_admin_operations():
    """Provide async operation utilities for testing."""
    class AsyncAdminOperations:
        @staticmethod
        async def validate_permission_async(user, resource, action, scope):
            """Mock async permission validation."""
            await asyncio.sleep(0)  # Simulate async operation
            return True

        @staticmethod
        async def create_admin_async(admin_data):
            """Mock async admin creation."""
            await asyncio.sleep(0)  # Simulate async operation
            return AdminMockFactory.create_admin_user_mock()

        @staticmethod
        async def bulk_operation_async(user_ids, operation):
            """Mock async bulk operation."""
            await asyncio.sleep(0)  # Simulate async operation
            return {"processed": len(user_ids), "failed": 0}

    return AsyncAdminOperations


# ============================================================================
# VALIDATION TEST UTILITIES
# ============================================================================

class ValidationTestHelper:
    """Helper utilities for validation testing."""

    @staticmethod
    def create_invalid_email_scenarios():
        """Create various invalid email scenarios."""
        return [
            "",
            "invalid-email",
            "@mestore.com",
            "test@",
            "test..test@mestore.com",
            "test@mestore",
            " test@mestore.com ",
            "test@mestore .com",
            "test@mestore.com."
        ]

    @staticmethod
    def create_invalid_security_clearance_scenarios():
        """Create invalid security clearance level scenarios."""
        return [0, -1, 6, 10, 99, "invalid", None, 3.5]

    @staticmethod
    def create_boundary_test_scenarios():
        """Create boundary test scenarios for various fields."""
        return {
            "string_fields": {
                "empty": "",
                "single_char": "a",
                "max_length": "a" * 100,
                "over_max_length": "a" * 101,
                "special_chars": "!@#$%^&*()",
                "unicode": "José María Ñoño",
                "sql_injection": "'; DROP TABLE users; --"
            },
            "numeric_fields": {
                "negative": -1,
                "zero": 0,
                "max_int": 2147483647,
                "over_max": 2147483648,
                "float": 3.14,
                "string_number": "123"
            },
            "array_fields": {
                "empty": [],
                "single_item": ["item1"],
                "max_items": [f"item{i}" for i in range(100)],
                "over_max": [f"item{i}" for i in range(101)],
                "duplicates": ["item1", "item1", "item2"],
                "invalid_types": [1, 2, "string", None]
            }
        }


@pytest.fixture
def validation_helper():
    """Provide access to ValidationTestHelper."""
    return ValidationTestHelper


# ============================================================================
# ERROR SCENARIO GENERATORS
# ============================================================================

class ErrorScenarioGenerator:
    """Generate various error scenarios for comprehensive testing."""

    @staticmethod
    def generate_http_error_scenarios():
        """Generate various HTTP error scenarios."""
        return [
            {
                "status_code": 400,
                "detail": "Bad Request - Invalid input data",
                "scenario": "invalid_input"
            },
            {
                "status_code": 401,
                "detail": "Unauthorized - Authentication required",
                "scenario": "unauthorized"
            },
            {
                "status_code": 403,
                "detail": "Forbidden - Insufficient permissions",
                "scenario": "forbidden"
            },
            {
                "status_code": 404,
                "detail": "Not Found - Resource does not exist",
                "scenario": "not_found"
            },
            {
                "status_code": 409,
                "detail": "Conflict - Resource already exists",
                "scenario": "conflict"
            },
            {
                "status_code": 500,
                "detail": "Internal Server Error - Something went wrong",
                "scenario": "server_error"
            }
        ]

    @staticmethod
    def generate_database_error_scenarios():
        """Generate database error scenarios."""
        return [
            {
                "error_type": "IntegrityError",
                "message": "UNIQUE constraint failed",
                "scenario": "duplicate_key"
            },
            {
                "error_type": "OperationalError",
                "message": "Database connection failed",
                "scenario": "connection_error"
            },
            {
                "error_type": "TimeoutError",
                "message": "Query timeout exceeded",
                "scenario": "timeout_error"
            }
        ]

    @staticmethod
    def generate_permission_error_scenarios():
        """Generate permission error scenarios."""
        return [
            {
                "error": "Insufficient security clearance level",
                "required_level": 4,
                "user_level": 3,
                "scenario": "clearance_too_low"
            },
            {
                "error": "Cannot modify users with equal or higher clearance",
                "current_level": 3,
                "target_level": 4,
                "scenario": "clearance_hierarchy_violation"
            },
            {
                "error": "Only SUPERUSERs can create other SUPERUSERs",
                "user_type": "ADMIN",
                "target_type": "SUPERUSER",
                "scenario": "superuser_creation_denied"
            }
        ]


@pytest.fixture
def error_scenarios():
    """Provide access to ErrorScenarioGenerator."""
    return ErrorScenarioGenerator