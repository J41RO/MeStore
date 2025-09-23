"""
E2E Test Fixtures for Integration Testing
Provides standardized fixtures for E2E test suites

STANDARDIZED ARCHITECTURE:
- Aligns with main conftest.py fixture naming conventions
- Eliminates duplicate fixture definitions across test files
- Ensures consistent authentication patterns across all E2E tests
- Supports proper test isolation and data management
"""

import pytest
import uuid
from typing import Dict, Any
from unittest.mock import Mock
from fastapi.testclient import TestClient

from app.models.user import User


# ================================================================================================
# STANDARDIZED AUTHENTICATION FIXTURES (ALIGNED WITH MAIN CONFTEST.PY)
# ================================================================================================

@pytest.fixture
def e2e_admin_token() -> str:
    """
    E2E admin token fixture - provides raw JWT token without Bearer prefix

    Note: This aligns with main conftest.py auth_token_admin naming pattern.
    The Bearer prefix should be added in header construction, not in the fixture.
    """
    return "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiYWRtaW4iLCJleHAiOjk5OTk5OTk5OTl9.mock_token"


@pytest.fixture
def e2e_superuser_token() -> str:
    """
    E2E superuser token fixture - provides raw JWT token without Bearer prefix

    Note: This aligns with main conftest.py naming conventions.
    The Bearer prefix should be added in header construction, not in the fixture.
    """
    return "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoic3VwZXJ1c2VyIiwiZXhwIjo5OTk5OTk5OTk5fQ.mock_token"


@pytest.fixture
def e2e_vendor_token() -> str:
    """
    E2E vendor token fixture - provides raw JWT token without Bearer prefix
    """
    return "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoidmVuZG9yIiwiZXhwIjo5OTk5OTk5OTk5fQ.mock_token"


@pytest.fixture
def e2e_buyer_token() -> str:
    """
    E2E buyer token fixture - provides raw JWT token without Bearer prefix
    """
    return "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiYnV5ZXIiLCJleHAiOjk5OTk5OTk5OTl9.mock_token"


@pytest.fixture
def e2e_low_privilege_token() -> str:
    """
    E2E low privilege token fixture - provides raw JWT token without Bearer prefix
    """
    return "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoibG93cHJpdiIsImV4cCI6OTk5OTk5OTk5OX0.mock_token"


# ================================================================================================
# STANDARDIZED HEADER FIXTURES (PROPER BEARER TOKEN CONSTRUCTION)
# ================================================================================================

@pytest.fixture
def e2e_admin_headers(e2e_admin_token: str) -> Dict[str, str]:
    """
    Authorization headers for admin requests with proper Bearer token construction
    """
    return {
        "Authorization": f"Bearer {e2e_admin_token}",
        "Content-Type": "application/json"
    }


@pytest.fixture
def e2e_superuser_headers(e2e_superuser_token: str) -> Dict[str, str]:
    """
    Authorization headers for superuser requests with proper Bearer token construction
    """
    return {
        "Authorization": f"Bearer {e2e_superuser_token}",
        "Content-Type": "application/json"
    }


@pytest.fixture
def e2e_vendor_headers(e2e_vendor_token: str) -> Dict[str, str]:
    """
    Authorization headers for vendor requests with proper Bearer token construction
    """
    return {
        "Authorization": f"Bearer {e2e_vendor_token}",
        "Content-Type": "application/json"
    }


@pytest.fixture
def e2e_buyer_headers(e2e_buyer_token: str) -> Dict[str, str]:
    """
    Authorization headers for buyer requests with proper Bearer token construction
    """
    return {
        "Authorization": f"Bearer {e2e_buyer_token}",
        "Content-Type": "application/json"
    }


@pytest.fixture
def e2e_low_privilege_headers(e2e_low_privilege_token: str) -> Dict[str, str]:
    """
    Authorization headers for low privilege requests with proper Bearer token construction
    """
    return {
        "Authorization": f"Bearer {e2e_low_privilege_token}",
        "Content-Type": "application/json"
    }


# ================================================================================================
# STANDARDIZED USER MOCK FIXTURES (CONSISTENT WITH BUSINESS LOGIC)
# ================================================================================================

@pytest.fixture
def e2e_mock_admin_user() -> Mock:
    """
    Mock admin user for E2E testing with realistic attributes
    """
    admin_user = Mock(spec=User)
    admin_user.id = str(uuid.uuid4())
    admin_user.email = "admin@e2etest.local"
    admin_user.nombre = "Admin"
    admin_user.apellido = "User"
    admin_user.documento = "12345678"
    admin_user.security_clearance_level = 4
    admin_user.is_admin = True
    admin_user.is_superuser = False
    admin_user.is_active = True
    admin_user.is_verified = True
    return admin_user


@pytest.fixture
def e2e_mock_superuser() -> Mock:
    """
    Mock superuser for E2E testing with realistic attributes
    """
    superuser = Mock(spec=User)
    superuser.id = str(uuid.uuid4())
    superuser.email = "superuser@e2etest.local"
    superuser.nombre = "Super"
    superuser.apellido = "User"
    superuser.documento = "87654321"
    superuser.security_clearance_level = 5
    superuser.is_admin = True
    superuser.is_superuser = True
    superuser.is_active = True
    superuser.is_verified = True
    return superuser


@pytest.fixture
def e2e_mock_vendor_user() -> Mock:
    """
    Mock vendor user for E2E testing with realistic attributes
    """
    vendor_user = Mock(spec=User)
    vendor_user.id = str(uuid.uuid4())
    vendor_user.email = "vendor@e2etest.local"
    vendor_user.nombre = "Vendor"
    vendor_user.apellido = "User"
    vendor_user.documento = "11223344"
    vendor_user.security_clearance_level = 2
    vendor_user.is_admin = False
    vendor_user.is_superuser = False
    vendor_user.is_active = True
    vendor_user.is_verified = True
    vendor_user.user_type = "vendor"
    return vendor_user


@pytest.fixture
def e2e_mock_buyer_user() -> Mock:
    """
    Mock buyer user for E2E testing with realistic attributes
    """
    buyer_user = Mock(spec=User)
    buyer_user.id = str(uuid.uuid4())
    buyer_user.email = "buyer@e2etest.local"
    buyer_user.nombre = "Buyer"
    buyer_user.apellido = "User"
    buyer_user.documento = "44332211"
    buyer_user.security_clearance_level = 1
    buyer_user.is_admin = False
    buyer_user.is_superuser = False
    buyer_user.is_active = True
    buyer_user.is_verified = True
    buyer_user.user_type = "buyer"
    return buyer_user


# ================================================================================================
# TEST SECURITY FIXTURES (FOR SECURITY-FOCUSED E2E TESTS)
# ================================================================================================

@pytest.fixture
def e2e_invalid_tokens() -> Dict[str, str]:
    """
    Collection of invalid tokens for security testing
    """
    return {
        "expired": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoidGVzdCIsImV4cCI6MTY0MDk5NTIwMH0.expired",
        "malformed": "invalid.token.format",
        "oversized": "A" * 500,
        "empty": "",
        "wrong_prefix": "NotBearer valid.token.here",
        "null_signature": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoidGVzdCJ9.",
        "tampered_payload": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.TAMPERED_PAYLOAD.signature"
    }


@pytest.fixture
def e2e_malicious_payloads() -> Dict[str, Any]:
    """
    Collection of malicious payloads for security testing
    """
    return {
        "sql_injection": {
            "email": "admin@test.com'; DROP TABLE users; --",
            "nombre": "Robert'; DELETE FROM orders; --"
        },
        "xss": {
            "nombre": "<script>alert('xss')</script>",
            "apellido": "javascript:alert(document.cookie)"
        },
        "mass_assignment": {
            "is_admin": True,
            "is_superuser": True,
            "security_clearance_level": 5,
            "verification_token": "malicious_token",
            "reset_token": "malicious_reset"
        },
        "oversized_data": {
            "nombre": "A" * 10000,
            "description": "B" * 50000
        }
    }


# ================================================================================================
# PERFORMANCE TESTING FIXTURES
# ================================================================================================

@pytest.fixture
def e2e_performance_config() -> Dict[str, Any]:
    """
    Configuration for E2E performance testing
    """
    return {
        "concurrent_requests": 10,
        "max_response_time_ms": 5000,
        "memory_threshold_mb": 100,
        "cpu_threshold_percent": 80,
        "rate_limit_threshold": 100,
        "batch_size": 50
    }


# ================================================================================================
# TEST DATA MANAGEMENT FIXTURES
# ================================================================================================

@pytest.fixture(scope="function")
def e2e_test_data_cleanup():
    """
    Auto-cleanup fixture for E2E test data isolation

    This ensures each E2E test starts with a clean state and cleans up after execution.
    """
    # Setup: Clear any existing test data
    test_data_registry = []

    yield test_data_registry

    # Teardown: Clean up any test data created during the test
    # Note: In a real implementation, this would connect to the test database
    # and clean up any records created with test-specific identifiers


@pytest.fixture(scope="session")
def e2e_test_markers() -> Dict[str, str]:
    """
    Standardized test markers for E2E test categorization
    """
    return {
        "auth": "Authentication and authorization tests",
        "security": "Security-focused tests (penetration testing)",
        "performance": "Performance and load testing",
        "compliance": "Regulatory compliance tests (GDPR, SOX, PCI)",
        "integration": "Cross-service integration tests",
        "workflow": "End-to-end business workflow tests",
        "admin": "Admin panel and management tests",
        "vendor": "Vendor-specific functionality tests",
        "buyer": "Buyer-specific functionality tests",
        "red_test": "TDD Red phase - failing tests",
        "green_test": "TDD Green phase - passing tests",
        "refactor_test": "TDD Refactor phase - optimization tests"
    }


# ================================================================================================
# LEGACY FIXTURE COMPATIBILITY (TEMPORARY - FOR MIGRATION)
# ================================================================================================

# These fixtures provide backward compatibility while migrating existing tests
# TODO: Remove these after all E2E tests are migrated to the new naming convention

@pytest.fixture
def admin_token(e2e_admin_token: str) -> str:
    """DEPRECATED: Use e2e_admin_headers instead for proper Bearer token handling"""
    return f"Bearer {e2e_admin_token}"


@pytest.fixture
def superuser_token(e2e_superuser_token: str) -> str:
    """DEPRECATED: Use e2e_superuser_headers instead for proper Bearer token handling"""
    return f"Bearer {e2e_superuser_token}"


@pytest.fixture
def low_privilege_token(e2e_low_privilege_token: str) -> str:
    """DEPRECATED: Use e2e_low_privilege_headers instead for proper Bearer token handling"""
    return f"Bearer {e2e_low_privilege_token}"


@pytest.fixture
def admin_headers(e2e_admin_headers: Dict[str, str]) -> Dict[str, str]:
    """DEPRECATED: Use e2e_admin_headers instead"""
    return e2e_admin_headers


@pytest.fixture
def superuser_headers(e2e_superuser_headers: Dict[str, str]) -> Dict[str, str]:
    """DEPRECATED: Use e2e_superuser_headers instead"""
    return e2e_superuser_headers


@pytest.fixture
def mock_admin_user(e2e_mock_admin_user: Mock) -> Mock:
    """DEPRECATED: Use e2e_mock_admin_user instead"""
    return e2e_mock_admin_user


@pytest.fixture
def mock_superuser(e2e_mock_superuser: Mock) -> Mock:
    """DEPRECATED: Use e2e_mock_superuser instead"""
    return e2e_mock_superuser


# ================================================================================================
# DOCUMENTATION AND USAGE EXAMPLES
# ================================================================================================

"""
USAGE EXAMPLES:

1. Standard Authentication Test:
   def test_admin_endpoint(client: TestClient, e2e_admin_headers: Dict[str, str]):
       response = client.get("/api/v1/admin/dashboard", headers=e2e_admin_headers)
       assert response.status_code == 200

2. Security Test:
   def test_invalid_tokens(client: TestClient, e2e_invalid_tokens: Dict[str, str]):
       for token_name, token_value in e2e_invalid_tokens.items():
           headers = {"Authorization": f"Bearer {token_value}"}
           response = client.get("/api/v1/admin/dashboard", headers=headers)
           assert response.status_code in [401, 403]

3. Performance Test:
   def test_concurrent_requests(client: TestClient, e2e_admin_headers: Dict[str, str],
                               e2e_performance_config: Dict[str, Any]):
       # Use e2e_performance_config for test parameters

4. Mock User Test:
   def test_user_operations(e2e_mock_admin_user: Mock):
       with patch('app.api.v1.deps.auth.get_current_user', return_value=e2e_mock_admin_user):
           # Test with mocked user
"""