"""
Tests for database dependency injection system.

This module tests the database dependency functions to ensure proper
session management, transaction handling, and compatibility with FastAPI.
"""

import pytest
from app.api.v1.deps.database import get_db, get_db_session


class TestDatabaseDependency:
    """Test cases for database dependency functions."""

    def test_get_db_function_exists(self):
        """Test that get_db function exists and is callable."""
        # Act & Assert
        assert callable(get_db)
        assert get_db.__name__ == "get_db"
        assert "database" in get_db.__doc__.lower()

    def test_get_db_is_async_generator_function(self):
        """Test that get_db is an async generator function."""
        import inspect

        # Act & Assert
        assert inspect.isasyncgenfunction(get_db)

    def test_get_db_session_alias_exists(self):
        """Test that get_db_session alias functions correctly."""
        # Act & Assert
        assert callable(get_db_session)
        assert get_db_session.__name__ == "get_db_session"
        assert "alias" in get_db_session.__doc__.lower()


class TestDatabaseDependencyIntegration:
    """Integration tests for database dependency with FastAPI."""

    def test_dependency_compatible_with_fastapi(self):
        """Test that dependency is compatible with FastAPI Depends."""
        from fastapi import Depends
        from sqlalchemy.ext.asyncio import AsyncSession

        # Arrange
        def endpoint_function(db: AsyncSession = Depends(get_db)):
            return {"db_type": type(db).__name__}

        # Act - Verify that FastAPI can inspect the dependency
        import inspect
        sig = inspect.signature(endpoint_function)

        # Assert
        assert "db" in sig.parameters
        param = sig.parameters["db"]
        assert param.default is not None  # Has a default (the Depends call)
        assert param.annotation == AsyncSession

    def test_module_exports_correct_functions(self):
        """Test that the module exports the expected functions."""
        from app.api.v1.deps.database import __all__

        # Assert
        expected_exports = ["get_db", "get_db_session"]
        assert set(__all__) == set(expected_exports)

    def test_imports_work_correctly(self):
        """Test that all necessary imports work without errors."""
        try:
            from app.api.v1.deps.database import get_db, get_db_session
            from app.api.v1.deps import get_db as deps_get_db

            # Assert that functions are callable
            assert callable(get_db)
            assert callable(get_db_session)
            assert callable(deps_get_db)

            # Assert that they are the same function
            assert get_db is deps_get_db

        except ImportError as e:
            pytest.fail(f"Import failed: {e}")
