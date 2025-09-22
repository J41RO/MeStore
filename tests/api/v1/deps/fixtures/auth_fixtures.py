"""
Authentication Testing Fixtures for TDD
=======================================

Comprehensive fixtures for authentication dependency testing following TDD patterns.
These fixtures support RED-GREEN-REFACTOR methodology with security-focused testing.

Author: Unit Testing AI
Date: 2025-09-21
Purpose: Enterprise-grade authentication testing with comprehensive coverage
"""

import pytest
import jwt
import uuid
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, MagicMock
from typing import Dict, Any, List, Optional, Union
from fastapi.security import HTTPAuthorizationCredentials

from app.models.user import User, UserType
from app.core.config import settings


@pytest.fixture
def valid_jwt_token() -> str:
    """
    Generate a valid JWT token for testing.

    Returns:
        str: Valid JWT token with proper structure
    """
    payload = {
        "sub": "test-user-id-123",
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow(),
        "type": "access"
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


@pytest.fixture
def expired_jwt_token() -> str:
    """
    Generate an expired JWT token for testing.

    Returns:
        str: Expired JWT token
    """
    payload = {
        "sub": "test-user-id-123",
        "exp": datetime.utcnow() - timedelta(hours=1),  # Expired
        "iat": datetime.utcnow() - timedelta(hours=2),
        "type": "access"
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


@pytest.fixture
def malformed_jwt_tokens() -> List[str]:
    """
    Collection of malformed JWT tokens for security testing.

    Returns:
        List[str]: Various malformed JWT tokens
    """
    return [
        "invalid-token",
        "bearer invalid",
        "",
        "not.a.jwt",
        "eyJ0eXAi.invalid.format",  # Malformed JWT
        "too.many.parts.in.jwt.token.here",  # Too many parts
        "missing.signature",  # Missing signature
        "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.invalid-payload.signature",  # Invalid payload
        "eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.",  # None algorithm
    ]


@pytest.fixture
def injection_attack_tokens() -> List[str]:
    """
    Collection of JWT tokens with injection attack payloads.

    Returns:
        List[str]: Malicious JWT tokens for security testing
    """
    return [
        "'; DROP TABLE users; --",
        "admin'; UPDATE users SET is_admin=1; --",
        "<script>alert('xss')</script>",
        "../../../etc/passwd",
        "../../admin/config",
        "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.'; DROP TABLE users; --",
        "1' OR '1'='1",
        "../../secrets/jwt.key",
        "file:///etc/passwd",
        "javascript:alert('xss')",
    ]


@pytest.fixture
def http_authorization_credentials() -> callable:
    """
    Factory for creating HTTPAuthorizationCredentials with different tokens.

    Returns:
        callable: Factory function for creating credentials
    """
    def create_credentials(
        token: Optional[str] = None,
        scheme: str = "Bearer"
    ) -> Optional[HTTPAuthorizationCredentials]:
        """
        Create HTTPAuthorizationCredentials.

        Args:
            token: JWT token string
            scheme: Authorization scheme (default: Bearer)

        Returns:
            HTTPAuthorizationCredentials or None
        """
        if token is None:
            return None

        return HTTPAuthorizationCredentials(
            scheme=scheme,
            credentials=token
        )

    return create_credentials


@pytest.fixture
def mock_users_by_type() -> Dict[UserType, User]:
    """
    Mock users for each user type for role testing.

    Returns:
        Dict[UserType, User]: Users by type
    """
    return {
        UserType.BUYER: User(
            id=uuid.uuid4(),
            email="buyer@example.com",
            nombre="Test",
            apellido="Buyer",
            user_type=UserType.BUYER,
            is_active=True,
            documento_identidad="12345678",
            telefono="123456789"
        ),
        UserType.VENDOR: User(
            id=uuid.uuid4(),
            email="vendor@example.com",
            nombre="Test",
            apellido="Vendor",
            user_type=UserType.VENDOR,
            is_active=True,
            documento_identidad="87654321",
            telefono="987654321"
        ),
        UserType.ADMIN: User(
            id=uuid.uuid4(),
            email="admin@example.com",
            nombre="Test",
            apellido="Admin",
            user_type=UserType.ADMIN,
            is_active=True,
            documento_identidad="11111111",
            telefono="111111111"
        ),
        UserType.SUPERUSER: User(
            id=uuid.uuid4(),
            email="superuser@example.com",
            nombre="Test",
            apellido="Superuser",
            user_type=UserType.SUPERUSER,
            is_active=True,
            documento_identidad="99999999",
            telefono="999999999"
        )
    }


@pytest.fixture
def inactive_user() -> User:
    """
    Mock inactive user for testing account status validation.

    Returns:
        User: Inactive user
    """
    return User(
        id=uuid.uuid4(),
        email="inactive@example.com",
        nombre="Inactive",
        apellido="User",
        user_type=UserType.BUYER,
        is_active=False,  # Inactive
        documento_identidad="00000000",
        telefono="000000000"
    )


@pytest.fixture
def jwt_payload_variations() -> List[Dict[str, Any]]:
    """
    Various JWT payload variations for testing token validation.

    Returns:
        List[Dict]: JWT payload variations
    """
    return [
        {},  # Empty payload
        {"sub": None},  # Null subject
        {"sub": ""},  # Empty subject
        {"exp": int(time.time()) + 3600},  # Missing subject
        {"sub": 123},  # Non-string subject
        {"sub": "test-user", "exp": "invalid"},  # Invalid expiration
        {"sub": "test-user", "iat": "invalid"},  # Invalid issued at
        {"sub": "test-user", "exp": int(time.time()) - 3600},  # Expired
        {"sub": "test-user", "type": "refresh"},  # Wrong token type
        {"sub": "../../admin", "exp": int(time.time()) + 3600},  # Path traversal in subject
    ]


@pytest.fixture
def mock_decode_token_responses() -> callable:
    """
    Factory for mocking JWT decode responses.

    Returns:
        callable: Factory for creating mock decode responses
    """
    def create_mock_response(
        success: bool = True,
        payload: Optional[Dict[str, Any]] = None,
        exception: Optional[Exception] = None
    ) -> Mock:
        """
        Create mock JWT decode response.

        Args:
            success: Whether decode should succeed
            payload: Payload to return on success
            exception: Exception to raise on failure

        Returns:
            Mock: Configured mock
        """
        mock = Mock()

        if success and payload:
            mock.return_value = payload
        elif exception:
            mock.side_effect = exception
        else:
            mock.side_effect = jwt.InvalidTokenError("Invalid token")

        return mock

    return create_mock_response


@pytest.fixture
def auth_test_scenarios() -> List[Dict[str, Any]]:
    """
    Comprehensive authentication test scenarios.

    Returns:
        List[Dict]: Authentication test scenarios
    """
    return [
        {
            "name": "valid_authentication",
            "token": "valid-token",
            "user_exists": True,
            "user_active": True,
            "expected_result": "success",
            "expected_status": None
        },
        {
            "name": "missing_credentials",
            "token": None,
            "user_exists": False,
            "user_active": False,
            "expected_result": "error",
            "expected_status": 401
        },
        {
            "name": "invalid_token",
            "token": "invalid-token",
            "user_exists": False,
            "user_active": False,
            "expected_result": "error",
            "expected_status": 401
        },
        {
            "name": "expired_token",
            "token": "expired-token",
            "user_exists": True,
            "user_active": True,
            "expected_result": "error",
            "expected_status": 401
        },
        {
            "name": "user_not_found",
            "token": "valid-token",
            "user_exists": False,
            "user_active": False,
            "expected_result": "error",
            "expected_status": 401
        },
        {
            "name": "inactive_user",
            "token": "valid-token",
            "user_exists": True,
            "user_active": False,
            "expected_result": "error",
            "expected_status": 403
        }
    ]


@pytest.fixture
def role_authorization_matrix() -> Dict[str, Dict[str, bool]]:
    """
    Role authorization matrix for testing permissions.

    Returns:
        Dict: Authorization matrix mapping roles to permissions
    """
    return {
        "require_admin": {
            UserType.BUYER.value: False,
            UserType.VENDOR.value: False,
            UserType.ADMIN.value: True,
            UserType.SUPERUSER.value: True,
        },
        "require_superuser": {
            UserType.BUYER.value: False,
            UserType.VENDOR.value: False,
            UserType.ADMIN.value: False,
            UserType.SUPERUSER.value: True,
        },
        "require_vendor": {
            UserType.BUYER.value: False,
            UserType.VENDOR.value: True,
            UserType.ADMIN.value: False,
            UserType.SUPERUSER.value: False,
        },
        "require_buyer": {
            UserType.BUYER.value: True,
            UserType.VENDOR.value: False,
            UserType.ADMIN.value: False,
            UserType.SUPERUSER.value: False,
        },
        "require_vendor_or_admin": {
            UserType.BUYER.value: False,
            UserType.VENDOR.value: True,
            UserType.ADMIN.value: True,
            UserType.SUPERUSER.value: True,
        }
    }


@pytest.fixture
def endpoint_permission_test_cases() -> List[Dict[str, Any]]:
    """
    Test cases for endpoint permission validation.

    Returns:
        List[Dict]: Endpoint permission test cases
    """
    return [
        {
            "endpoint": "POST /api/v1/auth/login",
            "permissions": ["PUBLIC"],
            "test_roles": [UserType.BUYER, UserType.VENDOR, UserType.ADMIN, None],
            "expected_results": [True, True, True, True]
        },
        {
            "endpoint": "GET /api/v1/admin/*",
            "permissions": ["admin"],
            "test_roles": [UserType.BUYER, UserType.VENDOR, UserType.ADMIN, UserType.SUPERUSER],
            "expected_results": [False, False, True, True]
        },
        {
            "endpoint": "POST /api/v1/productos/",
            "permissions": ["vendor", "admin"],
            "test_roles": [UserType.BUYER, UserType.VENDOR, UserType.ADMIN, UserType.SUPERUSER],
            "expected_results": [False, True, True, True]
        },
        {
            "endpoint": "GET /api/v1/auth/me",
            "permissions": ["AUTHENTICATED"],
            "test_roles": [UserType.BUYER, UserType.VENDOR, UserType.ADMIN, None],
            "expected_results": [True, True, True, False]
        }
    ]


@pytest.fixture
def security_test_data() -> Dict[str, Any]:
    """
    Security testing data for authentication dependencies.

    Returns:
        Dict: Security test data
    """
    return {
        "timing_attack_test": {
            "valid_scenarios": [
                "valid-user-id-123",
                "another-valid-id-456"
            ],
            "invalid_scenarios": [
                "invalid-user-id",
                "non-existent-id",
                "",
                None
            ],
            "max_time_variance": 0.1  # 100ms tolerance
        },
        "information_disclosure_test": {
            "sensitive_terms": [
                "database", "sql", "query", "table", "connection",
                "user_id", "password", "secret", "key", "token"
            ],
            "allowed_terms": [
                "credentials", "authentication", "authorization",
                "permission", "access", "invalid", "error"
            ]
        },
        "privilege_escalation_test": {
            "escalation_attempts": [
                {"from_role": UserType.BUYER, "to_permissions": ["admin", "superuser", "vendor"]},
                {"from_role": UserType.VENDOR, "to_permissions": ["admin", "superuser"]},
                {"from_role": UserType.ADMIN, "to_permissions": ["superuser"]},
            ]
        }
    }


@pytest.fixture
def mock_jwt_decode_factory() -> callable:
    """
    Factory for creating JWT decode mocks with different behaviors.

    Returns:
        callable: Factory for JWT decode mocks
    """
    def create_jwt_mock(
        decode_behavior: str = "success",
        payload: Optional[Dict[str, Any]] = None,
        exception_type: type = jwt.InvalidTokenError
    ) -> Mock:
        """
        Create JWT decode mock.

        Args:
            decode_behavior: 'success', 'invalid', 'expired', 'malformed'
            payload: Payload to return on success
            exception_type: Exception type to raise

        Returns:
            Mock: Configured JWT decode mock
        """
        mock = Mock()

        if decode_behavior == "success":
            mock.return_value = payload or {"sub": "test-user-id-123"}
        elif decode_behavior == "invalid":
            mock.side_effect = jwt.InvalidTokenError("Invalid token")
        elif decode_behavior == "expired":
            mock.side_effect = jwt.ExpiredSignatureError("Token expired")
        elif decode_behavior == "malformed":
            mock.side_effect = jwt.DecodeError("Token malformed")
        else:
            mock.side_effect = exception_type("Token error")

        return mock

    return create_jwt_mock


@pytest.fixture
def performance_test_config() -> Dict[str, Any]:
    """
    Performance test configuration for authentication dependencies.

    Returns:
        Dict: Performance test configuration
    """
    return {
        "max_auth_time": 0.05,  # 50ms max for authentication
        "concurrent_requests": 100,
        "timeout_threshold": 0.1,  # 100ms timeout
        "memory_limit_mb": 50,
        "jwt_decode_max_time": 0.01,  # 10ms max for JWT decode
        "database_lookup_max_time": 0.02,  # 20ms max for DB lookup
    }


@pytest.fixture
def tdd_auth_test_phases() -> Dict[str, List[str]]:
    """
    TDD test phases specifically for authentication testing.

    Returns:
        Dict: TDD phases with specific auth test requirements
    """
    return {
        "red_phase": [
            "Authentication should fail without credentials",
            "Invalid tokens should be rejected",
            "Expired tokens should be rejected",
            "Non-existent users should be rejected",
            "Inactive users should be rejected",
            "Role requirements should be enforced"
        ],
        "green_phase": [
            "Valid authentication should succeed",
            "Correct roles should be allowed",
            "Basic error handling should work",
            "Session management should function"
        ],
        "refactor_phase": [
            "Error messages should be standardized",
            "Performance should be optimized",
            "Security should be enhanced",
            "Code should be maintainable"
        ]
    }


if __name__ == "__main__":
    print("Authentication Testing Fixtures for TDD")
    print("======================================")
    print("Available fixtures:")
    print("- valid_jwt_token: Valid JWT for testing")
    print("- expired_jwt_token: Expired JWT for testing")
    print("- malformed_jwt_tokens: Collection of malformed tokens")
    print("- injection_attack_tokens: Malicious tokens for security testing")
    print("- mock_users_by_type: Users for each role type")
    print("- auth_test_scenarios: Comprehensive test scenarios")
    print("- role_authorization_matrix: Permission matrix")
    print("- security_test_data: Security testing data")
    print("\nUse these fixtures in your TDD tests for comprehensive coverage!")