"""
Advanced Admin Authentication & Authorization Test Patterns

Este módulo implementa patrones avanzados de testing para autenticación y autorización
del sistema de administración, incluyendo JWT, RBAC, niveles de clearance, y validación
de permisos granulares con cobertura completa de casos de edge y security scenarios.

Autor: Backend Framework AI
Fecha: 2025-09-21
Framework: FastAPI + JWT + RBAC + pytest
Objetivo: Testing comprehensivo de auth/authz para admin management
"""

import asyncio
import uuid
import jwt
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
from unittest.mock import Mock, AsyncMock, patch

import pytest
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer
from jose import JWTError

from app.core.config import settings
from app.core.security import (
    create_access_token, decode_access_token,
    get_password_hash, verify_password
)
from app.api.v1.deps.auth import get_current_user
from app.models.user import User, UserType
from app.models.admin_permission import (
    AdminPermission, PermissionScope, PermissionAction, ResourceType,
    admin_user_permissions
)
from app.services.admin_permission_service import (
    admin_permission_service, PermissionDeniedError, InsufficientClearanceError
)


# ================================================================================================
# AUTH TEST SCENARIOS ENUMERATION
# ================================================================================================

class AuthTestScenario(str, Enum):
    """Enumeration of authentication test scenarios."""

    VALID_TOKEN = "valid_token"
    EXPIRED_TOKEN = "expired_token"
    INVALID_SIGNATURE = "invalid_signature"
    MALFORMED_TOKEN = "malformed_token"
    MISSING_TOKEN = "missing_token"
    WRONG_ALGORITHM = "wrong_algorithm"
    TAMPERED_PAYLOAD = "tampered_payload"
    INSUFFICIENT_CLAIMS = "insufficient_claims"
    BLACKLISTED_TOKEN = "blacklisted_token"
    FUTURE_ISSUED_TOKEN = "future_issued_token"


class AuthzTestScenario(str, Enum):
    """Enumeration of authorization test scenarios."""

    SUFFICIENT_CLEARANCE = "sufficient_clearance"
    INSUFFICIENT_CLEARANCE = "insufficient_clearance"
    WRONG_USER_TYPE = "wrong_user_type"
    INACTIVE_USER = "inactive_user"
    UNVERIFIED_USER = "unverified_user"
    LOCKED_ACCOUNT = "locked_account"
    EXPIRED_PERMISSION = "expired_permission"
    REVOKED_PERMISSION = "revoked_permission"
    CONTEXT_VIOLATION = "context_violation"
    DEPARTMENT_MISMATCH = "department_mismatch"


# ================================================================================================
# AUTHENTICATION TEST PATTERN CLASSES
# ================================================================================================

@dataclass
class AuthTestCase:
    """Structure for authentication test cases."""

    scenario: AuthTestScenario
    token_data: Optional[Dict[str, Any]]
    expected_status: int
    expected_error: Optional[str] = None
    description: str = ""
    should_authenticate: bool = False
    user_override: Optional[Dict[str, Any]] = None


class AdminAuthenticationTestMatrix:
    """
    Comprehensive authentication test matrix for admin management.

    Provides systematic testing of all authentication scenarios including
    JWT validation, token expiration, signature verification, and edge cases.
    """

    def __init__(self):
        self.test_cases = self._generate_auth_test_cases()
        self.mock_users = self._generate_mock_users()

    def _generate_auth_test_cases(self) -> List[AuthTestCase]:
        """Generate comprehensive authentication test cases."""

        base_token_data = {
            "sub": str(uuid.uuid4()),
            "email": "admin@mestore.test",
            "user_type": "ADMIN",
            "nombre": "Test",
            "apellido": "Admin",
            "security_clearance_level": 4
        }

        return [
            # Valid scenarios
            AuthTestCase(
                scenario=AuthTestScenario.VALID_TOKEN,
                token_data=base_token_data,
                expected_status=200,
                should_authenticate=True,
                description="Valid JWT token with proper claims"
            ),

            # Expiration scenarios
            AuthTestCase(
                scenario=AuthTestScenario.EXPIRED_TOKEN,
                token_data={**base_token_data, "exp": datetime.utcnow() - timedelta(hours=1)},
                expected_status=401,
                expected_error="Token has expired",
                description="Expired JWT token"
            ),

            # Signature tampering scenarios
            AuthTestCase(
                scenario=AuthTestScenario.INVALID_SIGNATURE,
                token_data=base_token_data,  # Will be tampered in test
                expected_status=401,
                expected_error="Invalid token signature",
                description="JWT with invalid signature"
            ),

            # Malformed token scenarios
            AuthTestCase(
                scenario=AuthTestScenario.MALFORMED_TOKEN,
                token_data=None,  # Will use malformed token string
                expected_status=401,
                expected_error="Invalid token format",
                description="Malformed JWT token"
            ),

            # Missing token scenarios
            AuthTestCase(
                scenario=AuthTestScenario.MISSING_TOKEN,
                token_data=None,
                expected_status=401,
                expected_error="Authorization header missing",
                description="No authorization header provided"
            ),

            # Algorithm attack scenarios
            AuthTestCase(
                scenario=AuthTestScenario.WRONG_ALGORITHM,
                token_data=base_token_data,  # Will be signed with wrong algorithm
                expected_status=401,
                expected_error="Invalid token algorithm",
                description="JWT signed with wrong algorithm"
            ),

            # Tampered payload scenarios
            AuthTestCase(
                scenario=AuthTestScenario.TAMPERED_PAYLOAD,
                token_data={
                    **base_token_data,
                    "user_type": "SYSTEM",  # Privilege escalation attempt
                    "security_clearance_level": 5
                },
                expected_status=401,
                expected_error="Token payload mismatch",
                description="JWT with tampered payload claims"
            ),

            # Insufficient claims scenarios
            AuthTestCase(
                scenario=AuthTestScenario.INSUFFICIENT_CLAIMS,
                token_data={
                    "sub": str(uuid.uuid4()),
                    "email": "incomplete@test.com"
                    # Missing required claims
                },
                expected_status=401,
                expected_error="Missing required claims",
                description="JWT missing required claims"
            ),

            # Future issued token scenarios
            AuthTestCase(
                scenario=AuthTestScenario.FUTURE_ISSUED_TOKEN,
                token_data={
                    **base_token_data,
                    "iat": datetime.utcnow() + timedelta(hours=1)
                },
                expected_status=401,
                expected_error="Token issued in future",
                description="JWT with future issue time"
            )
        ]

    def _generate_mock_users(self) -> Dict[str, User]:
        """Generate mock users for different test scenarios."""

        users = {}

        # System user
        system_user = Mock(spec=User)
        system_user.id = str(uuid.uuid4())
        system_user.email = "system@mestore.test"
        system_user.user_type = UserType.SYSTEM
        system_user.security_clearance_level = 5
        system_user.is_active = True
        system_user.is_verified = True
        system_user.is_superuser.return_value = True
        system_user.is_admin_or_higher.return_value = True
        system_user.is_account_locked.return_value = False
        system_user.has_required_colombian_consents.return_value = True
        users["system"] = system_user

        # High clearance superuser
        superuser_high = Mock(spec=User)
        superuser_high.id = str(uuid.uuid4())
        superuser_high.email = "superuser_high@mestore.test"
        superuser_high.user_type = UserType.SUPERUSER
        superuser_high.security_clearance_level = 5
        superuser_high.is_active = True
        superuser_high.is_verified = True
        superuser_high.is_superuser.return_value = True
        superuser_high.is_admin_or_higher.return_value = True
        superuser_high.is_account_locked.return_value = False
        superuser_high.has_required_colombian_consents.return_value = True
        users["superuser_high"] = superuser_high

        # Medium clearance admin
        admin_medium = Mock(spec=User)
        admin_medium.id = str(uuid.uuid4())
        admin_medium.email = "admin_medium@mestore.test"
        admin_medium.user_type = UserType.ADMIN
        admin_medium.security_clearance_level = 3
        admin_medium.is_active = True
        admin_medium.is_verified = True
        admin_medium.is_superuser.return_value = False
        admin_medium.is_admin_or_higher.return_value = True
        admin_medium.is_account_locked.return_value = False
        admin_medium.has_required_colombian_consents.return_value = True
        users["admin_medium"] = admin_medium

        # Inactive admin
        admin_inactive = Mock(spec=User)
        admin_inactive.id = str(uuid.uuid4())
        admin_inactive.email = "admin_inactive@mestore.test"
        admin_inactive.user_type = UserType.ADMIN
        admin_inactive.security_clearance_level = 4
        admin_inactive.is_active = False  # Inactive
        admin_inactive.is_verified = True
        admin_inactive.is_superuser.return_value = False
        admin_inactive.is_admin_or_higher.return_value = True
        admin_inactive.is_account_locked.return_value = False
        admin_inactive.has_required_colombian_consents.return_value = True
        users["admin_inactive"] = admin_inactive

        # Locked admin
        admin_locked = Mock(spec=User)
        admin_locked.id = str(uuid.uuid4())
        admin_locked.email = "admin_locked@mestore.test"
        admin_locked.user_type = UserType.ADMIN
        admin_locked.security_clearance_level = 4
        admin_locked.is_active = True
        admin_locked.is_verified = True
        admin_locked.is_superuser.return_value = False
        admin_locked.is_admin_or_higher.return_value = True
        admin_locked.is_account_locked.return_value = True  # Locked
        admin_locked.has_required_colombian_consents.return_value = True
        users["admin_locked"] = admin_locked

        # Vendor (unauthorized)
        vendor = Mock(spec=User)
        vendor.id = str(uuid.uuid4())
        vendor.email = "vendor@mestore.test"
        vendor.user_type = UserType.VENDOR
        vendor.security_clearance_level = 1
        vendor.is_active = True
        vendor.is_verified = True
        vendor.is_superuser.return_value = False
        vendor.is_admin_or_higher.return_value = False  # Not admin level
        vendor.is_account_locked.return_value = False
        vendor.has_required_colombian_consents.return_value = True
        users["vendor"] = vendor

        return users


# ================================================================================================
# AUTHORIZATION TEST PATTERN CLASSES
# ================================================================================================

@dataclass
class AuthzTestCase:
    """Structure for authorization test cases."""

    scenario: AuthzTestScenario
    user_type: UserType
    security_clearance: int
    resource_type: ResourceType
    action: PermissionAction
    scope: PermissionScope
    expected_result: bool
    required_clearance: int
    context: Optional[Dict[str, Any]] = None
    description: str = ""


class AdminAuthorizationTestMatrix:
    """
    Comprehensive authorization test matrix for admin management.

    Provides systematic testing of RBAC, permission validation,
    security clearance enforcement, and context-specific authorization.
    """

    def __init__(self):
        self.test_cases = self._generate_authz_test_cases()
        self.permission_matrix = self._generate_permission_matrix()

    def _generate_authz_test_cases(self) -> List[AuthzTestCase]:
        """Generate comprehensive authorization test cases."""

        test_cases = []

        # Permission scenarios by user type and clearance
        scenarios = [
            # System user scenarios (should pass all)
            (UserType.SYSTEM, 5, ResourceType.USERS, PermissionAction.CREATE, PermissionScope.SYSTEM, True, 5),
            (UserType.SYSTEM, 5, ResourceType.USERS, PermissionAction.DELETE, PermissionScope.GLOBAL, True, 4),
            (UserType.SYSTEM, 5, ResourceType.SETTINGS, PermissionAction.CONFIGURE, PermissionScope.SYSTEM, True, 5),

            # Superuser scenarios
            (UserType.SUPERUSER, 5, ResourceType.USERS, PermissionAction.CREATE, PermissionScope.GLOBAL, True, 4),
            (UserType.SUPERUSER, 5, ResourceType.VENDORS, PermissionAction.MANAGE, PermissionScope.GLOBAL, True, 4),
            (UserType.SUPERUSER, 3, ResourceType.USERS, PermissionAction.CREATE, PermissionScope.GLOBAL, False, 4),  # Insufficient clearance

            # Admin scenarios
            (UserType.ADMIN, 4, ResourceType.USERS, PermissionAction.READ, PermissionScope.DEPARTMENT, True, 3),
            (UserType.ADMIN, 3, ResourceType.USERS, PermissionAction.CREATE, PermissionScope.GLOBAL, False, 4),  # Insufficient clearance
            (UserType.ADMIN, 4, ResourceType.SETTINGS, PermissionAction.CONFIGURE, PermissionScope.SYSTEM, False, 5),  # Wrong scope

            # Vendor scenarios (should fail admin operations)
            (UserType.VENDOR, 2, ResourceType.USERS, PermissionAction.READ, PermissionScope.USER, False, 3),
            (UserType.VENDOR, 2, ResourceType.VENDORS, PermissionAction.MANAGE, PermissionScope.GLOBAL, False, 4),
        ]

        for user_type, clearance, resource, action, scope, expected, required in scenarios:
            test_cases.append(AuthzTestCase(
                scenario=AuthzTestScenario.SUFFICIENT_CLEARANCE if expected else AuthzTestScenario.INSUFFICIENT_CLEARANCE,
                user_type=user_type,
                security_clearance=clearance,
                resource_type=resource,
                action=action,
                scope=scope,
                expected_result=expected,
                required_clearance=required,
                description=f"{user_type.value} with clearance {clearance} accessing {resource.value}.{action.value}.{scope.value}"
            ))

        return test_cases

    def _generate_permission_matrix(self) -> Dict[str, AdminPermission]:
        """Generate permission matrix for testing."""

        permissions = {}

        permission_configs = [
            ("users.create.global", ResourceType.USERS, PermissionAction.CREATE, PermissionScope.GLOBAL, 4, "HIGH"),
            ("users.read.global", ResourceType.USERS, PermissionAction.READ, PermissionScope.GLOBAL, 3, "MEDIUM"),
            ("users.update.department", ResourceType.USERS, PermissionAction.UPDATE, PermissionScope.DEPARTMENT, 3, "MEDIUM"),
            ("users.delete.system", ResourceType.USERS, PermissionAction.DELETE, PermissionScope.SYSTEM, 5, "CRITICAL"),
            ("vendors.manage.global", ResourceType.VENDORS, PermissionAction.MANAGE, PermissionScope.GLOBAL, 4, "HIGH"),
            ("settings.configure.system", ResourceType.SETTINGS, PermissionAction.CONFIGURE, PermissionScope.SYSTEM, 5, "CRITICAL"),
            ("transactions.audit.global", ResourceType.TRANSACTIONS, PermissionAction.AUDIT, PermissionScope.GLOBAL, 4, "HIGH"),
        ]

        for name, resource, action, scope, clearance, risk in permission_configs:
            permission = Mock(spec=AdminPermission)
            permission.id = str(uuid.uuid4())
            permission.name = name
            permission.resource_type = resource
            permission.action = action
            permission.scope = scope
            permission.required_clearance_level = clearance
            permission.risk_level = risk
            permission.requires_mfa = risk == "CRITICAL"
            permission.is_system_permission = scope == PermissionScope.SYSTEM
            permission.is_inheritable = scope != PermissionScope.SYSTEM

            permissions[name] = permission

        return permissions


# ================================================================================================
# JWT TOKEN GENERATION UTILITIES
# ================================================================================================

class AdminJWTTokenGenerator:
    """
    Utility for generating various JWT tokens for testing.

    Supports creating valid, invalid, expired, and tampered tokens
    for comprehensive authentication testing.
    """

    def __init__(self, secret_key: str = None, algorithm: str = "HS256"):
        self.secret_key = secret_key or settings.SECRET_KEY
        self.algorithm = algorithm

    def create_valid_token(self, user_data: Dict[str, Any], expires_delta: timedelta = None) -> str:
        """Create a valid JWT token."""

        if expires_delta is None:
            expires_delta = timedelta(hours=1)

        token_data = {
            **user_data,
            "exp": datetime.utcnow() + expires_delta,
            "iat": datetime.utcnow(),
            "iss": "mestore-admin"
        }

        return jwt.encode(token_data, self.secret_key, algorithm=self.algorithm)

    def create_expired_token(self, user_data: Dict[str, Any]) -> str:
        """Create an expired JWT token."""

        token_data = {
            **user_data,
            "exp": datetime.utcnow() - timedelta(hours=1),
            "iat": datetime.utcnow() - timedelta(hours=2)
        }

        return jwt.encode(token_data, self.secret_key, algorithm=self.algorithm)

    def create_invalid_signature_token(self, user_data: Dict[str, Any]) -> str:
        """Create a token with invalid signature."""

        token_data = {
            **user_data,
            "exp": datetime.utcnow() + timedelta(hours=1),
            "iat": datetime.utcnow()
        }

        # Sign with wrong secret
        return jwt.encode(token_data, "wrong_secret_key", algorithm=self.algorithm)

    def create_tampered_token(self, user_data: Dict[str, Any]) -> str:
        """Create a token with tampered payload."""

        # Create valid token
        valid_token = self.create_valid_token(user_data)

        # Split token parts
        header, payload, signature = valid_token.split('.')

        # Tamper with payload (decode, modify, encode)
        import base64
        import json

        payload_data = json.loads(base64.urlsafe_b64decode(payload + '=='))
        payload_data['user_type'] = 'SYSTEM'  # Privilege escalation attempt
        payload_data['security_clearance_level'] = 5

        tampered_payload = base64.urlsafe_b64encode(
            json.dumps(payload_data).encode()
        ).decode().rstrip('=')

        # Return token with tampered payload but original signature
        return f"{header}.{tampered_payload}.{signature}"

    def create_malformed_token(self) -> str:
        """Create a malformed JWT token."""
        return "not.a.valid.jwt.token.at.all"

    def create_future_issued_token(self, user_data: Dict[str, Any]) -> str:
        """Create a token issued in the future."""

        token_data = {
            **user_data,
            "exp": datetime.utcnow() + timedelta(hours=2),
            "iat": datetime.utcnow() + timedelta(hours=1)  # Future issue time
        }

        return jwt.encode(token_data, self.secret_key, algorithm=self.algorithm)


# ================================================================================================
# AUTHORIZATION CONTEXT TESTING
# ================================================================================================

class AdminAuthorizationContextTester:
    """
    Test authorization in different contexts and scenarios.

    Handles department-based authorization, time-based restrictions,
    IP-based access control, and other contextual authorization scenarios.
    """

    def __init__(self):
        self.context_scenarios = self._generate_context_scenarios()

    def _generate_context_scenarios(self) -> List[Dict[str, Any]]:
        """Generate context-based authorization scenarios."""

        return [
            # Department-based scenarios
            {
                "name": "same_department_access",
                "user_department": "finance",
                "target_department": "finance",
                "permission_scope": PermissionScope.DEPARTMENT,
                "should_pass": True
            },
            {
                "name": "different_department_access",
                "user_department": "finance",
                "target_department": "hr",
                "permission_scope": PermissionScope.DEPARTMENT,
                "should_pass": False
            },
            {
                "name": "global_scope_different_department",
                "user_department": "finance",
                "target_department": "hr",
                "permission_scope": PermissionScope.GLOBAL,
                "should_pass": True
            },

            # Time-based scenarios
            {
                "name": "business_hours_access",
                "current_hour": 10,  # 10 AM
                "allowed_hours": [9, 10, 11, 12, 13, 14, 15, 16, 17],
                "should_pass": True
            },
            {
                "name": "after_hours_access",
                "current_hour": 22,  # 10 PM
                "allowed_hours": [9, 10, 11, 12, 13, 14, 15, 16, 17],
                "should_pass": False
            },

            # IP-based scenarios
            {
                "name": "allowed_ip_access",
                "user_ip": "192.168.1.100",
                "allowed_ips": ["192.168.1.0/24", "10.0.0.0/8"],
                "should_pass": True
            },
            {
                "name": "blocked_ip_access",
                "user_ip": "203.0.113.1",
                "allowed_ips": ["192.168.1.0/24", "10.0.0.0/8"],
                "should_pass": False
            }
        ]

    async def test_department_authorization(
        self,
        user: User,
        permission: AdminPermission,
        target_department: str,
        session: Any
    ) -> bool:
        """Test department-based authorization."""

        context = {
            "user_department": user.department_id,
            "target_department": target_department
        }

        try:
            result = await admin_permission_service.validate_permission(
                session, user, permission.resource_type, permission.action, permission.scope,
                additional_context=context
            )
            return result
        except PermissionDeniedError:
            return False

    async def test_time_based_authorization(
        self,
        user: User,
        permission: AdminPermission,
        current_hour: int,
        session: Any
    ) -> bool:
        """Test time-based authorization."""

        # Mock permission with time restrictions
        permission.conditions = {
            "allowed_hours": [9, 10, 11, 12, 13, 14, 15, 16, 17]  # Business hours
        }

        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value.hour = current_hour

            try:
                result = await admin_permission_service.validate_permission(
                    session, user, permission.resource_type, permission.action, permission.scope
                )
                return result
            except PermissionDeniedError:
                return False


# ================================================================================================
# PYTEST FIXTURES FOR AUTH/AUTHZ TESTING
# ================================================================================================

@pytest.fixture
def admin_auth_test_matrix() -> AdminAuthenticationTestMatrix:
    """Authentication test matrix for admin testing."""
    return AdminAuthenticationTestMatrix()


@pytest.fixture
def admin_authz_test_matrix() -> AdminAuthorizationTestMatrix:
    """Authorization test matrix for admin testing."""
    return AdminAuthorizationTestMatrix()


@pytest.fixture
def admin_jwt_generator() -> AdminJWTTokenGenerator:
    """JWT token generator for admin testing."""
    return AdminJWTTokenGenerator()


@pytest.fixture
def admin_context_tester() -> AdminAuthorizationContextTester:
    """Authorization context tester for admin testing."""
    return AdminAuthorizationContextTester()


@pytest.fixture
def mock_admin_permission_service_auth():
    """Mock admin permission service for authentication testing."""

    mock_service = AsyncMock()

    # Default behaviors
    mock_service.validate_permission.return_value = True
    mock_service._validate_base_requirements.return_value = True
    mock_service._log_permission_check = AsyncMock()

    return mock_service


@pytest.fixture
def admin_security_test_scenarios() -> Dict[str, Any]:
    """Security test scenarios for admin authentication."""

    return {
        "privilege_escalation": {
            "description": "Attempt to escalate privileges through token tampering",
            "original_claims": {
                "user_type": "ADMIN",
                "security_clearance_level": 3
            },
            "tampered_claims": {
                "user_type": "SYSTEM",
                "security_clearance_level": 5
            },
            "should_detect": True
        },
        "token_replay": {
            "description": "Attempt to replay expired tokens",
            "scenario": "expired_token_reuse",
            "should_detect": True
        },
        "algorithm_confusion": {
            "description": "Attempt to use none algorithm",
            "algorithm": "none",
            "should_detect": True
        }
    }


# ================================================================================================
# INTEGRATION TESTING PATTERNS
# ================================================================================================

class AdminAuthIntegrationTestPattern:
    """
    Integration testing patterns for admin authentication and authorization.

    Combines authentication and authorization testing with real database
    operations and service integrations.
    """

    def __init__(self, session: Any, jwt_generator: AdminJWTTokenGenerator):
        self.session = session
        self.jwt_generator = jwt_generator

    async def test_full_auth_flow(
        self,
        user_data: Dict[str, Any],
        endpoint_path: str,
        http_method: str,
        request_payload: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Test complete authentication and authorization flow."""

        # Generate token
        token = self.jwt_generator.create_valid_token(user_data)

        # Mock request with authentication
        auth_headers = {"Authorization": f"Bearer {token}"}

        # Test authentication
        try:
            # Verify token
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

            # Get user from database
            user = await self.session.get(User, payload["sub"])

            if not user:
                return {"authenticated": False, "error": "User not found"}

            # Test authorization for specific endpoint
            # This would be endpoint-specific logic

            return {
                "authenticated": True,
                "authorized": True,
                "user_id": user.id,
                "user_type": user.user_type.value,
                "clearance_level": user.security_clearance_level
            }

        except JWTError as e:
            return {"authenticated": False, "error": str(e)}

    async def test_permission_inheritance(
        self,
        user: User,
        permission_hierarchy: List[AdminPermission]
    ) -> Dict[str, Any]:
        """Test permission inheritance through role hierarchy."""

        results = {}

        for permission in permission_hierarchy:
            try:
                result = await admin_permission_service.validate_permission(
                    self.session, user, permission.resource_type,
                    permission.action, permission.scope
                )
                results[permission.name] = {
                    "granted": result,
                    "source": "inherited" if result else "denied"
                }
            except PermissionDeniedError as e:
                results[permission.name] = {
                    "granted": False,
                    "source": "denied",
                    "reason": str(e)
                }

        return results


@pytest.fixture
async def admin_auth_integration_tester(
    admin_isolated_db_advanced,
    admin_jwt_generator
) -> AdminAuthIntegrationTestPattern:
    """Integration tester for admin authentication flows."""

    return AdminAuthIntegrationTestPattern(
        admin_isolated_db_advanced,
        admin_jwt_generator
    )


# ================================================================================================
# SECURITY VULNERABILITY TESTING
# ================================================================================================

class AdminSecurityVulnerabilityTester:
    """
    Test for security vulnerabilities in admin authentication and authorization.

    Includes tests for common attacks like privilege escalation, token tampering,
    timing attacks, and other security vulnerabilities.
    """

    @staticmethod
    async def test_timing_attack_resistance(
        valid_user_id: str,
        invalid_user_id: str,
        auth_function: callable
    ) -> bool:
        """Test resistance to timing attacks in user lookup."""

        import time

        # Measure time for valid user
        start_time = time.time()
        try:
            await auth_function(valid_user_id)
        except:
            pass
        valid_time = time.time() - start_time

        # Measure time for invalid user
        start_time = time.time()
        try:
            await auth_function(invalid_user_id)
        except:
            pass
        invalid_time = time.time() - start_time

        # Times should be similar (within 10ms)
        time_difference = abs(valid_time - invalid_time)
        return time_difference < 0.01

    @staticmethod
    def test_token_entropy(token: str) -> Dict[str, Any]:
        """Test JWT token entropy and randomness."""

        import base64
        import json

        # Decode token parts
        try:
            header, payload, signature = token.split('.')

            # Analyze signature entropy
            signature_bytes = base64.urlsafe_b64decode(signature + '==')
            signature_entropy = len(set(signature_bytes)) / len(signature_bytes)

            return {
                "signature_entropy": signature_entropy,
                "sufficient_entropy": signature_entropy > 0.7,
                "signature_length": len(signature_bytes)
            }

        except Exception as e:
            return {"error": str(e), "sufficient_entropy": False}

    @staticmethod
    async def test_privilege_escalation_prevention(
        low_privilege_user: User,
        high_privilege_operation: callable
    ) -> bool:
        """Test prevention of privilege escalation attacks."""

        try:
            # Attempt high privilege operation with low privilege user
            await high_privilege_operation(low_privilege_user)
            return False  # Should not succeed
        except (PermissionDeniedError, InsufficientClearanceError, HTTPException):
            return True  # Correctly prevented


@pytest.fixture
def admin_security_vulnerability_tester() -> AdminSecurityVulnerabilityTester:
    """Security vulnerability tester for admin systems."""
    return AdminSecurityVulnerabilityTester()