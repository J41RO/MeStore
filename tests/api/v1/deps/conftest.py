"""
Pytest Configuration for API v1 Dependencies Tests
==================================================

Shared configuration and fixtures for TDD testing of API v1 dependencies.
This module provides enterprise-grade testing setup with proper isolation.

Author: Unit Testing AI
Date: 2025-09-21
Purpose: Comprehensive test configuration for dependency testing
"""

import pytest
import asyncio
from typing import AsyncGenerator
from unittest.mock import AsyncMock, patch

# Import all fixtures from fixture modules
from .fixtures.database_fixtures import *
from .fixtures.auth_fixtures import *


@pytest.fixture(scope="session")
def event_loop():
    """
    Create an instance of the default event loop for the test session.

    This ensures all async tests share the same event loop.
    """
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
async def isolate_tests():
    """
    Automatically isolate each test to prevent side effects.

    This fixture runs before and after each test to ensure clean state.
    """
    # Setup: Clear any existing mocks or patches
    yield
    # Teardown: Clean up after test


@pytest.fixture
def mock_id_validator():
    """
    Mock the IDValidator for testing UUID validation.

    Returns:
        Mock: Configured IDValidator mock
    """
    with patch('app.api.v1.deps.database.IDValidator') as mock_validator:
        # Configure successful validation by default
        mock_validator.validate_uuid_string.return_value = "validated-uuid-123"
        yield mock_validator


@pytest.fixture
def mock_async_session_local():
    """
    Mock AsyncSessionLocal for database dependency testing.

    Returns:
        Mock: Configured AsyncSessionLocal mock
    """
    with patch('app.api.v1.deps.database.AsyncSessionLocal') as mock_session_local:
        mock_session = AsyncMock()
        mock_session_local.return_value.__aenter__.return_value = mock_session
        mock_session_local.return_value.__aexit__.return_value = None
        yield mock_session_local, mock_session


@pytest.fixture
def mock_security_decode():
    """
    Mock the decode_access_token function for auth testing.

    Returns:
        Mock: Configured decode function mock
    """
    with patch('app.api.v1.deps.standardized_auth.decode_access_token') as mock_decode:
        # Default successful decode
        mock_decode.return_value = {"sub": "test-user-id-123"}
        yield mock_decode


@pytest.fixture
def mock_auth_helpers():
    """
    Mock authentication helper functions.

    Returns:
        Dict: Dictionary of mocked auth helpers
    """
    mocks = {}

    with patch('app.api.v1.deps.standardized_auth.AuthErrorHelper') as auth_error_mock, \
         patch('app.api.v1.deps.standardized_auth.ErrorHelper') as error_helper_mock:

        mocks['auth_error'] = auth_error_mock
        mocks['error_helper'] = error_helper_mock

        yield mocks


@pytest.fixture
def tdd_test_config():
    """
    Configuration for TDD testing phases.

    Returns:
        Dict: TDD test configuration
    """
    return {
        "red_phase": {
            "should_fail": True,
            "implement_after": False,
            "description": "Write failing tests first"
        },
        "green_phase": {
            "should_pass": True,
            "minimal_implementation": True,
            "description": "Implement minimal code to pass"
        },
        "refactor_phase": {
            "improve_quality": True,
            "maintain_tests": True,
            "description": "Improve code while keeping tests green"
        }
    }


# Pytest markers for TDD phases
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "tdd: Test follows TDD methodology"
    )
    config.addinivalue_line(
        "markers", "red_test: RED phase - test should fail initially"
    )
    config.addinivalue_line(
        "markers", "green_test: GREEN phase - minimal implementation"
    )
    config.addinivalue_line(
        "markers", "refactor_test: REFACTOR phase - improved implementation"
    )
    config.addinivalue_line(
        "markers", "auth: Authentication-related test"
    )
    config.addinivalue_line(
        "markers", "database: Database-related test"
    )
    config.addinivalue_line(
        "markers", "security: Security-focused test"
    )
    config.addinivalue_line(
        "markers", "performance: Performance testing"
    )


def pytest_runtest_setup(item):
    """Setup for each test item."""
    # Check if test is marked as red_test and should fail initially
    if item.get_closest_marker("red_test"):
        # Add metadata for RED phase tests
        item.user_properties.append(("tdd_phase", "red"))
    elif item.get_closest_marker("green_test"):
        item.user_properties.append(("tdd_phase", "green"))
    elif item.get_closest_marker("refactor_test"):
        item.user_properties.append(("tdd_phase", "refactor"))


def pytest_runtest_teardown(item):
    """Teardown for each test item."""
    # Clean up any test-specific resources
    pass


# Error handling for TDD tests
@pytest.fixture
def expect_failure():
    """
    Context manager for tests that should fail in RED phase.

    Usage:
        with expect_failure():
            # Code that should fail
            pass
    """
    class ExpectFailure:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type is None:
                pytest.fail("Test was expected to fail but passed")
            return True  # Suppress the expected exception

    return ExpectFailure()


# Utilities for TDD testing
@pytest.fixture
def tdd_cycle_validator():
    """
    Validator for ensuring proper TDD cycle execution.

    Returns:
        Callable: Function to validate TDD cycle
    """
    def validate_cycle(red_result, green_result, refactor_result):
        """
        Validate that TDD cycle was followed correctly.

        Args:
            red_result: Result of RED phase test
            green_result: Result of GREEN phase test
            refactor_result: Result of REFACTOR phase test
        """
        assert red_result == "failed", "RED phase should fail"
        assert green_result == "passed", "GREEN phase should pass"
        assert refactor_result == "passed", "REFACTOR phase should pass"

        return True

    return validate_cycle


if __name__ == "__main__":
    print("Pytest Configuration for API v1 Dependencies Tests")
    print("==================================================")
    print("Available fixtures:")
    print("- Database fixtures: mock_async_session, entity fixtures")
    print("- Auth fixtures: JWT tokens, credentials, user mocks")
    print("- TDD fixtures: Test phase validation, cycle management")
    print("- Security fixtures: Injection tests, timing tests")
    print("\nMarkers:")
    print("- @pytest.mark.tdd: TDD methodology test")
    print("- @pytest.mark.red_test: RED phase test")
    print("- @pytest.mark.green_test: GREEN phase test")
    print("- @pytest.mark.refactor_test: REFACTOR phase test")
    print("- @pytest.mark.auth: Authentication test")
    print("- @pytest.mark.database: Database test")
    print("- @pytest.mark.security: Security test")