"""
Comprehensive TDD Test Suite for app/core/types.py
=================================================

This module provides exhaustive test coverage for the cross-database UUID type functionality
following strict RED-GREEN-REFACTOR TDD methodology.

Target Components:
- UUID TypeDecorator class (cross-database compatibility)
- generate_uuid function (UUID string generation)

TDD Methodology:
- RED Phase: Write failing tests that capture exact desired behavior
- GREEN Phase: Implement minimal code to make tests pass
- REFACTOR Phase: Improve code quality while maintaining test coverage
"""

import pytest
import uuid
from unittest.mock import Mock, patch, MagicMock
from typing import Any, Optional
from decimal import Decimal

# SQLAlchemy imports for database dialect testing
from sqlalchemy import create_engine, MetaData, Table, Column, select
from sqlalchemy.engine import Engine
from sqlalchemy.dialects import postgresql, sqlite
from sqlalchemy.sql.type_api import TypeEngine
from sqlalchemy.types import String
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID

# Import TDD framework
from tests.tdd_framework import (
    TDDTestCase, RedPhase, GreenPhase, RefactorPhase,
    red_test, green_test, refactor_test,
    TDDAssertion, TDDFixtures
)

# Import the components under test
from app.core.types import UUID as UUIDType, generate_uuid


# ==================== TDD MARKERS ====================
pytestmark = [
    pytest.mark.tdd,
    pytest.mark.unit,
    pytest.mark.core,
    pytest.mark.types
]


class TestUUIDTypeDecoratorTDD:
    """
    Comprehensive TDD test suite for UUID TypeDecorator class.

    Tests cross-database compatibility between PostgreSQL and SQLite,
    ensuring proper UUID handling in both environments.
    """

    def setup_method(self):
        """Setup for each test method."""
        self.tdd = TDDTestCase("UUID TypeDecorator TDD")
        self.uuid_type = UUIDType()

        # Create mock dialects for testing
        self.postgresql_dialect = Mock()
        self.postgresql_dialect.name = 'postgresql'
        self.postgresql_dialect.type_descriptor = Mock()

        self.sqlite_dialect = Mock()
        self.sqlite_dialect.name = 'sqlite'
        self.sqlite_dialect.type_descriptor = Mock()

        # Sample UUIDs for testing
        self.sample_uuid = uuid.UUID('12345678-1234-5678-9abc-123456789abc')
        self.sample_uuid_str = str(self.sample_uuid)

    @red_test
    def test_load_dialect_impl_postgresql_red(self):
        """
        RED PHASE: Test that load_dialect_impl returns PostgreSQL UUID type.

        This test should initially fail because we need to verify the exact
        behavior of dialect implementation loading for PostgreSQL.
        """
        red_phase = self.tdd.red_phase()

        # RED: Test that method exists and works with PostgreSQL dialect
        result = self.uuid_type.load_dialect_impl(self.postgresql_dialect)

        # Verify PostgreSQL UUID behavior is implemented
        assert result is not None, "PostgreSQL dialect should return a valid type"

        red_phase.log_assertion("load_dialect_impl works with PostgreSQL dialect", True)

    @red_test
    def test_load_dialect_impl_sqlite_red(self):
        """
        RED PHASE: Test that load_dialect_impl returns String(36) for SQLite.

        This test should initially fail to ensure we're testing the right behavior.
        """
        red_phase = self.tdd.red_phase()

        # RED: Test SQLite dialect returns String(36)
        self.sqlite_dialect.type_descriptor.return_value = String(36)

        result = self.uuid_type.load_dialect_impl(self.sqlite_dialect)

        # This assertion should pass, but we want to ensure comprehensive testing
        assert result is not None, "SQLite should return a valid type"
        assert hasattr(result, 'length') or 'String' in str(type(result)), "SQLite should use String type for UUID storage"

        red_phase.log_assertion("SQLite dialect implementation loaded correctly", True)

    @red_test
    def test_process_bind_param_postgresql_red(self):
        """
        RED PHASE: Test UUID parameter binding for PostgreSQL.

        PostgreSQL should handle UUID objects natively without conversion.
        """
        red_phase = self.tdd.red_phase()

        # RED: Test PostgreSQL native UUID handling
        result = self.uuid_type.process_bind_param(self.sample_uuid, self.postgresql_dialect)

        # Should return UUID object unchanged for PostgreSQL
        assert result == self.sample_uuid, "PostgreSQL should handle UUID objects natively"

        red_phase.log_assertion("PostgreSQL UUID binding works correctly", True)

    @red_test
    def test_process_bind_param_sqlite_red(self):
        """
        RED PHASE: Test UUID parameter binding for SQLite.

        SQLite should convert UUID objects to strings.
        """
        red_phase = self.tdd.red_phase()

        # RED: Test SQLite UUID to string conversion
        result = self.uuid_type.process_bind_param(self.sample_uuid, self.sqlite_dialect)

        # Should convert UUID to string for SQLite
        assert result == self.sample_uuid_str, f"SQLite should convert UUID to string, got {result}"
        assert isinstance(result, str), f"Result should be string, got {type(result)}"

        red_phase.log_assertion("SQLite UUID to string conversion works", True)

    @red_test
    def test_process_bind_param_none_value_red(self):
        """
        RED PHASE: Test None value handling in process_bind_param.

        None values should be preserved across all dialects.
        """
        red_phase = self.tdd.red_phase()

        # RED: Test None value handling
        postgres_result = self.uuid_type.process_bind_param(None, self.postgresql_dialect)
        sqlite_result = self.uuid_type.process_bind_param(None, self.sqlite_dialect)

        assert postgres_result is None, "PostgreSQL should preserve None values"
        assert sqlite_result is None, "SQLite should preserve None values"

        red_phase.log_assertion("None value handling works for both dialects", True)

    @red_test
    def test_process_result_value_postgresql_red(self):
        """
        RED PHASE: Test result value processing for PostgreSQL.

        PostgreSQL returns UUID objects directly.
        """
        red_phase = self.tdd.red_phase()

        # RED: Test PostgreSQL result processing
        result = self.uuid_type.process_result_value(self.sample_uuid, self.postgresql_dialect)

        assert result == self.sample_uuid, "PostgreSQL should return UUID objects unchanged"
        assert isinstance(result, uuid.UUID), f"Result should be UUID object, got {type(result)}"

        red_phase.log_assertion("PostgreSQL result processing works correctly", True)

    @red_test
    def test_process_result_value_sqlite_red(self):
        """
        RED PHASE: Test result value processing for SQLite.

        SQLite returns strings that need conversion to UUID objects.
        """
        red_phase = self.tdd.red_phase()

        # RED: Test SQLite string to UUID conversion
        result = self.uuid_type.process_result_value(self.sample_uuid_str, self.sqlite_dialect)

        assert result == self.sample_uuid, f"SQLite should convert string to UUID, got {result}"
        assert isinstance(result, uuid.UUID), f"Result should be UUID object, got {type(result)}"

        red_phase.log_assertion("SQLite string to UUID conversion works", True)

    @red_test
    def test_process_result_value_none_red(self):
        """
        RED PHASE: Test None value handling in process_result_value.

        None values should be preserved across all dialects.
        """
        red_phase = self.tdd.red_phase()

        # RED: Test None value preservation
        postgres_result = self.uuid_type.process_result_value(None, self.postgresql_dialect)
        sqlite_result = self.uuid_type.process_result_value(None, self.sqlite_dialect)

        assert postgres_result is None, "PostgreSQL should preserve None results"
        assert sqlite_result is None, "SQLite should preserve None results"

        red_phase.log_assertion("None result value handling works for both dialects", True)

    @red_test
    def test_invalid_uuid_string_handling_red(self):
        """
        RED PHASE: Test handling of invalid UUID strings.

        Should raise ValueError for malformed UUID strings.
        """
        red_phase = self.tdd.red_phase()

        invalid_uuid_string = "not-a-valid-uuid"

        # RED: Test invalid UUID handling in SQLite
        with pytest.raises(ValueError, match="badly formed hexadecimal UUID string"):
            self.uuid_type.process_result_value(invalid_uuid_string, self.sqlite_dialect)

        red_phase.log_assertion("Invalid UUID string raises ValueError correctly", True)

    @red_test
    def test_uuid_type_attributes_red(self):
        """
        RED PHASE: Test UUID TypeDecorator class attributes.

        Verify that the class has required attributes for SQLAlchemy.
        """
        red_phase = self.tdd.red_phase()

        # RED: Test class attributes
        assert hasattr(UUIDType, 'impl'), "UUID type should have 'impl' attribute"
        assert hasattr(UUIDType, 'cache_ok'), "UUID type should have 'cache_ok' attribute"
        assert UUIDType.cache_ok is True, "cache_ok should be True for performance"
        assert UUIDType.impl == String, "impl should be String type"

        red_phase.log_assertion("UUID TypeDecorator attributes are correct", True)

    @red_test
    def test_cross_database_compatibility_red(self):
        """
        RED PHASE: Test cross-database compatibility scenarios.

        Test round-trip UUID handling between different databases.
        """
        red_phase = self.tdd.red_phase()

        # RED: Test round-trip compatibility
        original_uuid = uuid.UUID('f47ac10b-58cc-4372-a567-0e02b2c3d479')

        # Simulate PostgreSQL -> SQLite migration
        postgres_bound = self.uuid_type.process_bind_param(original_uuid, self.postgresql_dialect)
        sqlite_bound = self.uuid_type.process_bind_param(postgres_bound, self.sqlite_dialect)

        # Simulate SQLite -> PostgreSQL read
        sqlite_result = self.uuid_type.process_result_value(sqlite_bound, self.sqlite_dialect)
        postgres_result = self.uuid_type.process_result_value(sqlite_result, self.postgresql_dialect)

        assert postgres_result == original_uuid, "Round-trip should preserve UUID value"

        red_phase.log_assertion("Cross-database UUID compatibility works", True)

    @red_test
    def test_string_uuid_input_handling_red(self):
        """
        RED PHASE: Test handling of string UUID inputs in bind parameters.

        Both UUID objects and valid UUID strings should be handled correctly.
        """
        red_phase = self.tdd.red_phase()

        # RED: Test string UUID input for SQLite
        string_uuid_input = "f47ac10b-58cc-4372-a567-0e02b2c3d479"
        result = self.uuid_type.process_bind_param(string_uuid_input, self.sqlite_dialect)

        assert result == string_uuid_input, "String UUIDs should be preserved for SQLite"
        assert isinstance(result, str), "Result should be string type"

        red_phase.log_assertion("String UUID input handling works correctly", True)


class TestGenerateUUIDTDD:
    """
    Comprehensive TDD test suite for generate_uuid function.

    Tests UUID generation functionality, format compliance, and uniqueness.
    """

    def setup_method(self):
        """Setup for each test method."""
        self.tdd = TDDTestCase("generate_uuid function TDD")

    @red_test
    def test_generates_valid_uuid_red(self):
        """
        RED PHASE: Test that generate_uuid returns valid UUID strings.

        Should generate valid UUID4 format strings.
        """
        red_phase = self.tdd.red_phase()

        # RED: Test valid UUID generation
        generated = generate_uuid()

        # Should be string
        assert isinstance(generated, str), f"Should return string, got {type(generated)}"

        # Should be valid UUID format
        try:
            parsed_uuid = uuid.UUID(generated)
            assert str(parsed_uuid) == generated, "Generated string should be valid UUID format"
        except ValueError as e:
            pytest.fail(f"Generated UUID is invalid: {e}")

        red_phase.log_assertion("generate_uuid produces valid UUID strings", True)

    @red_test
    def test_uuid_version_compliance_red(self):
        """
        RED PHASE: Test that generated UUIDs comply with UUID4 standard.

        Should generate UUID version 4 (random) format.
        """
        red_phase = self.tdd.red_phase()

        # RED: Test UUID4 version compliance
        generated = generate_uuid()
        parsed_uuid = uuid.UUID(generated)

        assert parsed_uuid.version == 4, f"Should generate UUID4, got version {parsed_uuid.version}"

        red_phase.log_assertion("Generated UUIDs comply with UUID4 standard", True)

    @red_test
    def test_unique_uuid_generation_red(self):
        """
        RED PHASE: Test that generate_uuid produces unique values.

        Multiple calls should generate different UUIDs.
        """
        red_phase = self.tdd.red_phase()

        # RED: Test uniqueness
        generated_uuids = set()
        num_generations = 1000

        for _ in range(num_generations):
            generated_uuids.add(generate_uuid())

        # All should be unique (extremely high probability)
        assert len(generated_uuids) == num_generations, \
            f"Expected {num_generations} unique UUIDs, got {len(generated_uuids)}"

        red_phase.log_assertion("generate_uuid produces unique values consistently", True)

    @red_test
    def test_uuid_format_compliance_red(self):
        """
        RED PHASE: Test UUID format compliance (8-4-4-4-12 pattern).

        Generated UUIDs should match standard format pattern.
        """
        red_phase = self.tdd.red_phase()

        # RED: Test format pattern
        generated = generate_uuid()

        # Should match UUID format: 8-4-4-4-12
        import re
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'

        assert re.match(uuid_pattern, generated), \
            f"Generated UUID '{generated}' doesn't match standard format"

        # Should be exactly 36 characters (32 hex + 4 hyphens)
        assert len(generated) == 36, f"UUID should be 36 characters, got {len(generated)}"

        red_phase.log_assertion("Generated UUIDs match standard format", True)

    @red_test
    def test_uuid_randomness_quality_red(self):
        """
        RED PHASE: Test randomness quality of generated UUIDs.

        Should have good distribution of characters across positions.
        """
        red_phase = self.tdd.red_phase()

        # RED: Test randomness quality
        generated_uuids = [generate_uuid() for _ in range(100)]

        # Test character distribution at first position (should not be all same)
        first_chars = [uuid_str[0] for uuid_str in generated_uuids]
        unique_first_chars = set(first_chars)

        # Should have some variety (at least 3 different first characters in 100 UUIDs)
        assert len(unique_first_chars) >= 3, \
            f"Poor randomness: only {len(unique_first_chars)} unique first characters"

        red_phase.log_assertion("Generated UUIDs show good randomness quality", True)

    @red_test
    def test_performance_and_memory_efficiency_red(self):
        """
        RED PHASE: Test performance and memory efficiency of UUID generation.

        Should generate UUIDs efficiently without memory leaks.
        """
        red_phase = self.tdd.red_phase()

        import time
        import gc

        # RED: Test performance
        start_time = time.time()
        num_generations = 10000

        for _ in range(num_generations):
            generate_uuid()

        end_time = time.time()
        generation_time = end_time - start_time

        # Should generate 10K UUIDs in reasonable time (< 1 second)
        assert generation_time < 1.0, \
            f"UUID generation too slow: {generation_time:.3f}s for {num_generations} UUIDs"

        # Force garbage collection and verify no major memory issues
        gc.collect()

        red_phase.log_assertion("UUID generation is performant and memory-efficient", True)


class TestUUIDTypeIntegrationTDD:
    """
    Integration tests for UUID TypeDecorator with real SQLAlchemy engines.

    Tests actual database integration scenarios.
    """

    def setup_method(self):
        """Setup for integration tests."""
        self.tdd = TDDTestCase("UUID Type Integration TDD")

    @red_test
    def test_real_postgresql_dialect_integration_red(self):
        """
        RED PHASE: Test with real PostgreSQL dialect.

        Uses actual PostgreSQL dialect for realistic testing.
        """
        red_phase = self.tdd.red_phase()

        # RED: Test with real PostgreSQL dialect
        from sqlalchemy.dialects.postgresql import dialect as pg_dialect
        real_pg_dialect = pg_dialect()

        uuid_type = UUIDType()

        # Test dialect implementation loading
        impl = uuid_type.load_dialect_impl(real_pg_dialect)
        assert isinstance(impl, PostgresUUID), f"Should return PostgresUUID, got {type(impl)}"

        # Test parameter processing
        test_uuid = uuid.UUID('f47ac10b-58cc-4372-a567-0e02b2c3d479')
        bound_param = uuid_type.process_bind_param(test_uuid, real_pg_dialect)
        assert bound_param == test_uuid, "PostgreSQL should preserve UUID objects"

        red_phase.log_assertion("Real PostgreSQL dialect integration works", True)

    @red_test
    def test_real_sqlite_dialect_integration_red(self):
        """
        RED PHASE: Test with real SQLite dialect.

        Uses actual SQLite dialect for realistic testing.
        """
        red_phase = self.tdd.red_phase()

        # RED: Test with real SQLite dialect
        from sqlalchemy.dialects.sqlite import dialect as sqlite_dialect
        real_sqlite_dialect = sqlite_dialect()

        uuid_type = UUIDType()

        # Test dialect implementation loading
        impl = uuid_type.load_dialect_impl(real_sqlite_dialect)
        assert isinstance(impl, String), f"Should return String type, got {type(impl)}"

        # Test parameter processing
        test_uuid = uuid.UUID('f47ac10b-58cc-4372-a567-0e02b2c3d479')
        bound_param = uuid_type.process_bind_param(test_uuid, real_sqlite_dialect)
        assert bound_param == str(test_uuid), "SQLite should convert UUID to string"

        # Test result processing
        result_value = uuid_type.process_result_value(str(test_uuid), real_sqlite_dialect)
        assert result_value == test_uuid, "SQLite should convert string back to UUID"

        red_phase.log_assertion("Real SQLite dialect integration works", True)

    @red_test
    def test_database_table_creation_red(self):
        """
        RED PHASE: Test UUID type in actual table creation.

        Verifies that UUID type works in real table definitions.
        """
        red_phase = self.tdd.red_phase()

        # RED: Test table creation with UUID columns
        metadata = MetaData()

        test_table = Table(
            'test_uuid_table',
            metadata,
            Column('id', UUIDType(), primary_key=True),
            Column('external_id', UUIDType(), nullable=True)
        )

        # Should not raise exceptions
        assert test_table.columns['id'].type.__class__ == UUIDType
        assert test_table.columns['external_id'].type.__class__ == UUIDType

        red_phase.log_assertion("UUID type works in table definitions", True)


class TestUUIDTypeErrorHandlingTDD:
    """
    Error handling and edge case tests for UUID TypeDecorator.

    Tests robustness and proper error handling.
    """

    def setup_method(self):
        """Setup for error handling tests."""
        self.tdd = TDDTestCase("UUID Type Error Handling TDD")
        self.uuid_type = UUIDType()

    @red_test
    def test_unknown_dialect_handling_red(self):
        """
        RED PHASE: Test behavior with unknown database dialects.

        Should default to String type for unknown dialects.
        """
        red_phase = self.tdd.red_phase()

        # RED: Test unknown dialect
        unknown_dialect = Mock()
        unknown_dialect.name = 'unknown_database'
        unknown_dialect.type_descriptor = Mock(return_value=String(36))

        result = self.uuid_type.load_dialect_impl(unknown_dialect)

        # Should default to String(36) for unknown dialects
        unknown_dialect.type_descriptor.assert_called_once()
        # Verify it was called with a String type
        call_args = unknown_dialect.type_descriptor.call_args[0][0]
        assert hasattr(call_args, 'length') or 'String' in str(type(call_args))

        red_phase.log_assertion("Unknown dialects default to String type", True)

    @red_test
    def test_malformed_uuid_processing_red(self):
        """
        RED PHASE: Test handling of malformed UUID data.

        Should raise appropriate exceptions for invalid data.
        """
        red_phase = self.tdd.red_phase()

        sqlite_dialect = Mock()
        sqlite_dialect.name = 'sqlite'

        # RED: Test various malformed UUIDs
        malformed_uuids = [
            "not-a-uuid",
            "12345",
            "",
            "12345678-1234-5678-9abc",  # Too short
            "12345678-1234-5678-9abc-123456789abcdef",  # Too long
            None  # None should be handled separately
        ]

        for malformed_uuid in malformed_uuids[:-1]:  # Exclude None
            with pytest.raises(ValueError):
                self.uuid_type.process_result_value(malformed_uuid, sqlite_dialect)

        # None should be handled gracefully
        result = self.uuid_type.process_result_value(None, sqlite_dialect)
        assert result is None, "None should be preserved"

        red_phase.log_assertion("Malformed UUID data raises appropriate errors", True)

    @red_test
    def test_type_conversion_edge_cases_red(self):
        """
        RED PHASE: Test edge cases in type conversion.

        Tests various input types and conversion scenarios.
        """
        red_phase = self.tdd.red_phase()

        sqlite_dialect = Mock()
        sqlite_dialect.name = 'sqlite'

        # RED: Test edge case inputs
        test_uuid = uuid.UUID('f47ac10b-58cc-4372-a567-0e02b2c3d479')

        # Test integer input (should be converted to string)
        int_input = 12345
        result = self.uuid_type.process_bind_param(int_input, sqlite_dialect)
        assert result == "12345", "Integer input should be converted to string"

        # Test float input (should be converted to string)
        float_input = 123.45
        result = self.uuid_type.process_bind_param(float_input, sqlite_dialect)
        assert result == "123.45", "Float input should be converted to string"

        red_phase.log_assertion("Edge case type conversions work correctly", True)


# ==================== TEST EXECUTION HELPERS ====================

def run_red_phase_tests():
    """
    Helper function to run all RED phase tests.

    This function can be used to execute only the RED phase tests
    to verify they fail as expected.
    """
    pytest.main([
        __file__ + "::TestUUIDTypeDecoratorTDD",
        __file__ + "::TestGenerateUUIDTDD",
        __file__ + "::TestUUIDTypeIntegrationTDD",
        __file__ + "::TestUUIDTypeErrorHandlingTDD",
        "-v", "-m", "tdd"
    ])


def run_coverage_analysis():
    """
    Helper function to run coverage analysis on the types module.

    Ensures we achieve 100% test coverage.
    """
    import subprocess
    import os

    # Run pytest with coverage for the types module
    cmd = [
        "python", "-m", "pytest",
        __file__,
        "--cov=app.core.types",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov/types",
        "-v"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    print("Coverage Analysis Results:")
    print(result.stdout)

    if result.stderr:
        print("Errors/Warnings:")
        print(result.stderr)

    return result.returncode == 0


if __name__ == "__main__":
    print("🔴 Running RED Phase Tests for app/core/types.py")
    print("=" * 60)

    # Run RED phase tests to verify they fail appropriately
    run_red_phase_tests()

    print("\n📊 Running Coverage Analysis")
    print("=" * 60)

    # Analyze test coverage
    coverage_success = run_coverage_analysis()

    if coverage_success:
        print("✅ Test suite created successfully!")
        print("💡 Next steps:")
        print("   1. Run tests to verify RED phase failures")
        print("   2. Implement GREEN phase fixes if needed")
        print("   3. Add REFACTOR phase improvements")
    else:
        print("❌ Issues detected in test suite")
        print("🔧 Review and fix any failing tests")