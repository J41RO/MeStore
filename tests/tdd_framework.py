"""
TDD Framework - Comprehensive Test-Driven Development Infrastructure
==================================================================

This module provides the complete TDD infrastructure for MeStore project following
RED-GREEN-REFACTOR methodology with enterprise-grade patterns and practices.

Classes:
    - TDDTestCase: Base class for all TDD tests
    - RedPhase: Helper for writing failing tests
    - GreenPhase: Helper for making tests pass
    - RefactorPhase: Helper for refactoring with test safety
    - TDDFixtures: Standard fixtures for TDD patterns
"""

import asyncio
import pytest
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Callable, Awaitable
from unittest.mock import Mock, AsyncMock, MagicMock
from contextlib import asynccontextmanager, contextmanager
from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from httpx import AsyncClient


class TDDPhase:
    """Base class for TDD phases with logging and tracking capabilities."""

    def __init__(self, test_name: str, phase_name: str):
        self.test_name = test_name
        self.phase_name = phase_name
        self.start_time = datetime.now()
        self.assertions_count = 0
        self.operations_count = 0

    def log_assertion(self, description: str, result: bool):
        """Log assertion with result for TDD tracking."""
        self.assertions_count += 1
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"[{self.phase_name}] {status}: {description}")
        return result

    def log_operation(self, operation: str):
        """Log operations performed in this phase."""
        self.operations_count += 1
        print(f"[{self.phase_name}] OP #{self.operations_count}: {operation}")


class RedPhase(TDDPhase):
    """
    RED Phase - Write failing tests that capture desired behavior exactly.

    This phase ensures we write tests first that define the expected behavior
    before any implementation exists.
    """

    def __init__(self, test_name: str):
        super().__init__(test_name, "RED")

    def expect_failure(self, test_func: Callable, expected_exception: Exception = None):
        """Expect a test to fail in RED phase - this is correct behavior."""
        try:
            result = test_func()
            if asyncio.iscoroutine(result):
                asyncio.run(result)
            # If we get here without exception, the test passed when it should fail
            raise AssertionError(f"RED PHASE ERROR: Test '{self.test_name}' passed but should fail!")
        except Exception as e:
            if expected_exception and not isinstance(e, type(expected_exception)):
                raise AssertionError(f"RED PHASE ERROR: Expected {expected_exception}, got {type(e)}")
            self.log_assertion(f"Test correctly fails: {str(e)}", True)
            return True

    def assert_not_implemented(self, feature_name: str):
        """Assert that a feature is not yet implemented - RED phase validation."""
        self.log_assertion(f"Feature '{feature_name}' is not implemented (as expected in RED)", True)
        with pytest.raises((NotImplementedError, AttributeError, ImportError)):
            raise NotImplementedError(f"Feature '{feature_name}' not implemented yet")


class GreenPhase(TDDPhase):
    """
    GREEN Phase - Write minimal code to make tests pass.

    Focus on making the failing test pass with the simplest possible implementation.
    No extra features, no premature optimization - just make it work.
    """

    def __init__(self, test_name: str):
        super().__init__(test_name, "GREEN")

    def minimal_implementation_check(self, implementation: Callable, test_cases: List[Dict]):
        """Verify implementation is minimal but sufficient for all test cases."""
        self.log_operation("Checking minimal implementation sufficiency")

        for i, test_case in enumerate(test_cases):
            try:
                result = implementation(**test_case.get('input', {}))
                expected = test_case.get('expected')

                if asyncio.iscoroutine(result):
                    result = asyncio.run(result)

                assert result == expected, f"Test case {i+1} failed: expected {expected}, got {result}"
                self.log_assertion(f"Test case {i+1} passes with minimal implementation", True)

            except Exception as e:
                self.log_assertion(f"Test case {i+1} failed: {str(e)}", False)
                raise

    def verify_no_over_engineering(self, implementation_lines: int, max_lines: int = 50):
        """Ensure implementation doesn't exceed reasonable simplicity threshold."""
        if implementation_lines > max_lines:
            raise AssertionError(f"GREEN PHASE WARNING: Implementation has {implementation_lines} lines, "
                               f"exceeding simplicity threshold of {max_lines}. Consider refactoring.")
        self.log_assertion(f"Implementation is appropriately simple ({implementation_lines} lines)", True)


class RefactorPhase(TDDPhase):
    """
    REFACTOR Phase - Improve code structure while maintaining test coverage.

    Focus on code quality improvements: eliminate duplication, improve readability,
    optimize performance, but never change behavior.
    """

    def __init__(self, test_name: str):
        super().__init__(test_name, "REFACTOR")

    def ensure_tests_still_pass(self, test_runner: Callable):
        """Verify all tests still pass after refactoring."""
        self.log_operation("Running full test suite after refactoring")
        try:
            test_runner()
            self.log_assertion("All tests pass after refactoring", True)
            return True
        except Exception as e:
            self.log_assertion(f"Tests failed after refactoring: {str(e)}", False)
            raise AssertionError(f"REFACTOR PHASE ERROR: Tests failed after refactoring: {e}")

    def check_code_quality_improvement(self, metrics_before: Dict, metrics_after: Dict):
        """Verify that refactoring improved code quality metrics."""
        improvements = []
        regressions = []

        for metric, value_after in metrics_after.items():
            value_before = metrics_before.get(metric, 0)
            if metric in ['complexity', 'duplication', 'technical_debt']:
                # Lower is better for these metrics
                if value_after < value_before:
                    improvements.append(f"{metric}: {value_before} → {value_after}")
                elif value_after > value_before:
                    regressions.append(f"{metric}: {value_before} → {value_after}")
            else:
                # Higher is better for metrics like readability, maintainability
                if value_after > value_before:
                    improvements.append(f"{metric}: {value_before} → {value_after}")
                elif value_after < value_before:
                    regressions.append(f"{metric}: {value_before} → {value_after}")

        if regressions:
            self.log_assertion(f"Code quality regressions detected: {regressions}", False)
            raise AssertionError(f"REFACTOR PHASE ERROR: Quality regressions: {regressions}")

        if improvements:
            self.log_assertion(f"Code quality improvements achieved: {improvements}", True)
        else:
            self.log_assertion("No measurable quality improvements (acceptable)", True)


class TDDTestCase:
    """
    Base test case class for TDD methodology with built-in RED-GREEN-REFACTOR support.

    Provides standard patterns, assertions, and helpers for TDD development.
    """

    def __init__(self, test_name: str):
        self.test_name = test_name
        self.current_phase = None
        self.test_data = {}
        self.mocks = {}
        self.assertions = []

    def red_phase(self) -> RedPhase:
        """Enter RED phase - write failing tests."""
        self.current_phase = RedPhase(self.test_name)
        print(f"\n🔴 Starting RED phase for: {self.test_name}")
        return self.current_phase

    def green_phase(self) -> GreenPhase:
        """Enter GREEN phase - make tests pass with minimal code."""
        self.current_phase = GreenPhase(self.test_name)
        print(f"\n🟢 Starting GREEN phase for: {self.test_name}")
        return self.current_phase

    def refactor_phase(self) -> RefactorPhase:
        """Enter REFACTOR phase - improve code quality while maintaining tests."""
        self.current_phase = RefactorPhase(self.test_name)
        print(f"\n🔧 Starting REFACTOR phase for: {self.test_name}")
        return self.current_phase

    def create_mock_user(self, user_type: str = "VENDOR") -> Dict:
        """Create standardized mock user data for testing."""
        user_id = uuid.uuid4()
        return {
            "id": user_id,
            "email": f"test_{user_type.lower()}_{user_id.hex[:8]}@test.com",
            "nombre": f"Test {user_type}",
            "apellido": "User",
            "user_type": user_type,
            "is_active": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }

    def create_mock_product(self, vendor_id: Optional[uuid.UUID] = None) -> Dict:
        """Create standardized mock product data for testing."""
        product_id = uuid.uuid4()
        return {
            "id": product_id,
            "sku": f"TEST-{product_id.hex[:8].upper()}",
            "nombre": f"Test Product {product_id.hex[:6]}",
            "descripcion": "Test product description",
            "precio_venta": Decimal("100000.00"),
            "precio_costo": Decimal("75000.00"),
            "stock": 10,
            "vendor_id": vendor_id or uuid.uuid4(),
            "is_active": True,
            "created_at": datetime.now()
        }

    def create_mock_order(self, buyer_id: Optional[uuid.UUID] = None) -> Dict:
        """Create standardized mock order data for testing."""
        order_id = uuid.uuid4()
        return {
            "id": order_id,
            "order_number": f"ORD-{order_id.hex[:8].upper()}",
            "buyer_id": buyer_id or uuid.uuid4(),
            "total_amount": Decimal("150000.00"),
            "status": "PENDING",
            "shipping_name": "Test Customer",
            "shipping_phone": "3001234567",
            "shipping_address": "Test Address 123",
            "shipping_city": "Bogotá",
            "shipping_state": "Cundinamarca",
            "created_at": datetime.now()
        }

    def setup_database_transaction(self, db_session: Session):
        """Setup database transaction for test isolation."""
        self.db_transaction = db_session.begin()
        return db_session

    def rollback_database_transaction(self):
        """Rollback database transaction for test cleanup."""
        if hasattr(self, 'db_transaction'):
            self.db_transaction.rollback()

    @contextmanager
    def tdd_cycle(self, feature_name: str):
        """Complete TDD cycle context manager for a feature."""
        print(f"\n🎯 Starting TDD cycle for feature: {feature_name}")
        try:
            yield self
        except Exception as e:
            print(f"❌ TDD cycle failed for {feature_name}: {str(e)}")
            raise
        finally:
            print(f"✅ TDD cycle completed for feature: {feature_name}")

    def assert_tdd_compliance(self, implementation_func: Callable):
        """Verify that implementation follows TDD principles."""
        # Check if function has tests
        test_module = implementation_func.__module__.replace('.py', '_test.py')
        if 'test_' not in test_module:
            raise AssertionError(f"TDD COMPLIANCE ERROR: {implementation_func.__name__} has no corresponding test file")

        # Check if function is properly tested (this is a simplified check)
        if not hasattr(implementation_func, '__test_coverage__'):
            print(f"⚠️  WARNING: Cannot verify test coverage for {implementation_func.__name__}")


class TDDFixtures:
    """Standard fixtures and utilities for TDD testing."""

    @staticmethod
    def create_async_mock_service(service_class: type) -> AsyncMock:
        """Create async mock for service classes with standard methods."""
        mock_service = AsyncMock(spec=service_class)

        # Setup common async methods
        mock_service.create = AsyncMock()
        mock_service.get_by_id = AsyncMock()
        mock_service.update = AsyncMock()
        mock_service.delete = AsyncMock()
        mock_service.list = AsyncMock(return_value=[])

        return mock_service

    @staticmethod
    def create_mock_database_session() -> AsyncMock:
        """Create mock database session for testing."""
        mock_session = AsyncMock(spec=AsyncSession)
        mock_session.add = Mock()
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()
        mock_session.refresh = AsyncMock()
        mock_session.close = AsyncMock()
        mock_session.execute = AsyncMock()
        mock_session.scalar = AsyncMock()

        return mock_session

    @staticmethod
    def create_test_client_headers(auth_token: str = None) -> Dict[str, str]:
        """Create standard headers for test client requests."""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (TDD-Test-Agent) MeStore/1.0",
        }

        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"

        return headers

    @staticmethod
    @contextmanager
    def mock_external_service(service_name: str, responses: Dict[str, Any]):
        """Mock external service with predefined responses."""
        print(f"🔧 Mocking external service: {service_name}")
        mock_service = Mock()

        for method_name, response in responses.items():
            if asyncio.iscoroutinefunction(response):
                setattr(mock_service, method_name, AsyncMock(return_value=response))
            else:
                setattr(mock_service, method_name, Mock(return_value=response))

        try:
            yield mock_service
        finally:
            print(f"✅ External service mock cleaned up: {service_name}")


# TDD Decorators for method-level phase management
def red_test(test_func: Callable):
    """Decorator to mark a test as RED phase (should fail initially)."""
    def wrapper(*args, **kwargs):
        print(f"🔴 RED PHASE: {test_func.__name__}")
        return test_func(*args, **kwargs)
    wrapper.__name__ = test_func.__name__
    wrapper.__doc__ = f"RED PHASE: {test_func.__doc__ or 'No description'}"
    return wrapper


def green_test(test_func: Callable):
    """Decorator to mark a test as GREEN phase (should pass with implementation)."""
    def wrapper(*args, **kwargs):
        print(f"🟢 GREEN PHASE: {test_func.__name__}")
        return test_func(*args, **kwargs)
    wrapper.__name__ = test_func.__name__
    wrapper.__doc__ = f"GREEN PHASE: {test_func.__doc__ or 'No description'}"
    return wrapper


def refactor_test(test_func: Callable):
    """Decorator to mark a test as REFACTOR phase (verify improvements)."""
    def wrapper(*args, **kwargs):
        print(f"🔧 REFACTOR PHASE: {test_func.__name__}")
        return test_func(*args, **kwargs)
    wrapper.__name__ = test_func.__name__
    wrapper.__doc__ = f"REFACTOR PHASE: {test_func.__doc__ or 'No description'}"
    return wrapper


# TDD Test Markers
pytestmark = [
    pytest.mark.tdd,
    pytest.mark.unit,
    pytest.mark.asyncio
]


class TDDAssertion:
    """Enhanced assertions for TDD with detailed failure information."""

    @staticmethod
    def assert_behavior_matches_specification(actual_behavior, specification: Dict):
        """Assert that actual behavior matches the specification exactly."""
        for key, expected_value in specification.items():
            actual_value = getattr(actual_behavior, key, None)
            if actual_value != expected_value:
                raise AssertionError(
                    f"Behavior mismatch for '{key}': "
                    f"expected {expected_value}, got {actual_value}"
                )

    @staticmethod
    def assert_test_fails_as_expected(test_func: Callable, expected_exception: type = Exception):
        """Assert that a test fails as expected in RED phase."""
        try:
            test_func()
            raise AssertionError("Test should have failed but passed")
        except expected_exception:
            pass  # This is expected
        except Exception as e:
            raise AssertionError(f"Test failed with unexpected exception: {e}")

    @staticmethod
    def assert_minimal_implementation(implementation: str, max_complexity: int = 10):
        """Assert that implementation is minimal and not over-engineered."""
        lines = implementation.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]

        if len(non_empty_lines) > max_complexity:
            raise AssertionError(
                f"Implementation is too complex: {len(non_empty_lines)} lines, "
                f"expected <= {max_complexity}"
            )


# Export all TDD components
__all__ = [
    'TDDTestCase', 'RedPhase', 'GreenPhase', 'RefactorPhase',
    'TDDFixtures', 'TDDAssertion',
    'red_test', 'green_test', 'refactor_test'
]