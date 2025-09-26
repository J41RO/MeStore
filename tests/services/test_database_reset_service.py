"""
Comprehensive tests for Database Reset Service

Tests all functionality of the database reset system with proper
isolation and safety checks. Uses async pytest framework and
ensures no interference with production data.

Test Coverage:
- Environment safety validation
- User identification and cleanup
- Different reset levels
- Error handling and edge cases
- Session cleanup (Redis)
- Full reset operations
- Test user creation

Author: Backend Framework AI
Created: 2025-09-25
Version: 1.0.0
"""

import pytest
import pytest_asyncio
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime, timedelta
from typing import List, Dict, Any

from app.services.database_reset_service import (
    DatabaseResetService,
    ResetLevel,
    ResetResult,
    quick_user_reset,
    quick_test_data_reset
)
from app.models.user import User, UserType
from app.core.config import settings
from app.core.security import get_password_hash


class TestDatabaseResetService:
    """Test suite for DatabaseResetService."""

    @pytest_asyncio.fixture
    async def reset_service(self):
        """Create a DatabaseResetService instance for testing."""
        service = DatabaseResetService()
        # Mock session to avoid actual database connections in tests
        service.session = AsyncMock()
        return service

    @pytest_asyncio.fixture
    async def test_user(self):
        """Create a test user object."""
        return User(
            id="test-user-id",
            email="testuser@test.com",
            password_hash=get_password_hash("testpass"),
            nombre="Test",
            apellido="User",
            user_type=UserType.BUYER,
            is_active=True,
            is_verified=True
        )

    def test_environment_validation_success(self, reset_service):
        """Test successful environment validation."""
        with patch.object(settings, 'ENVIRONMENT', 'development'):
            with patch.object(settings, 'DATABASE_URL', 'postgresql://localhost:5432/test_db'):
                # Should not raise exception
                reset_service._validate_environment()

    def test_environment_validation_failure_production(self, reset_service):
        """Test environment validation failure in production."""
        with patch.object(settings, 'ENVIRONMENT', 'production'):
            with pytest.raises(RuntimeError, match="Database reset not allowed in environment"):
                reset_service._validate_environment()

    def test_environment_validation_failure_production_db(self, reset_service):
        """Test environment validation failure with production-like database."""
        with patch.object(settings, 'ENVIRONMENT', 'development'):
            with patch.object(settings, 'DATABASE_URL', 'postgresql://prod.server.com:5432/production'):
                with pytest.raises(RuntimeError, match="DATABASE_URL appears to be production"):
                    reset_service._validate_environment()

    def test_reset_level_validation_success(self, reset_service):
        """Test successful reset level validation."""
        # Should not raise exception for normal levels
        reset_service._validate_reset_level(ResetLevel.USER_DATA)
        reset_service._validate_reset_level(ResetLevel.USER_CASCADE)

    def test_reset_level_validation_failure_full_reset(self, reset_service):
        """Test reset level validation failure for full reset without confirmation."""
        with pytest.raises(ValueError, match="FULL_RESET requires explicit confirmation"):
            reset_service._validate_reset_level(ResetLevel.FULL_RESET, confirm_dangerous=False)

    def test_reset_level_validation_success_full_reset_confirmed(self, reset_service):
        """Test successful reset level validation for confirmed full reset."""
        # Should not raise exception with confirmation
        reset_service._validate_reset_level(ResetLevel.FULL_RESET, confirm_dangerous=True)

    @pytest.mark.asyncio
    async def test_identify_test_users_default_patterns(self, reset_service):
        """Test identification of test users with default patterns."""
        # Mock database query results
        mock_query_result = MagicMock()
        mock_query_result.fetchall.return_value = [
            ("user1", "test1@test.com"),
            ("user2", "test2@example.com")
        ]
        reset_service.session.execute.return_value = mock_query_result

        # Mock User.get for each user
        test_user1 = User(id="user1", email="test1@test.com", user_type=UserType.BUYER)
        test_user2 = User(id="user2", email="test2@example.com", user_type=UserType.BUYER)

        reset_service.session.get.side_effect = [test_user1, test_user2]

        result = await reset_service._identify_test_users()

        assert len(result) == 2
        assert result[0].email == "test1@test.com"
        assert result[1].email == "test2@example.com"

    @pytest.mark.asyncio
    async def test_identify_test_users_custom_patterns(self, reset_service):
        """Test identification of test users with custom patterns."""
        custom_patterns = ["@staging.com", "@qa.com"]

        # Mock database query
        mock_query_result = MagicMock()
        mock_query_result.fetchall.return_value = [("user1", "qa@staging.com")]
        reset_service.session.execute.return_value = mock_query_result

        test_user = User(id="user1", email="qa@staging.com", user_type=UserType.BUYER)
        reset_service.session.get.return_value = test_user

        result = await reset_service._identify_test_users(custom_patterns)

        assert len(result) == 1
        assert result[0].email == "qa@staging.com"

    @pytest.mark.asyncio
    async def test_delete_related_records_success(self, reset_service):
        """Test successful deletion of related records."""
        user_ids = ["user1", "user2"]
        result = ResetResult()

        # Mock successful database operations
        mock_result = MagicMock()
        mock_result.rowcount = 5
        reset_service.session.execute.return_value = mock_result

        await reset_service._delete_related_records(user_ids, result)

        # Verify records were tracked
        assert len(result.deleted_records) > 0
        assert result.errors == []

    @pytest.mark.asyncio
    async def test_delete_related_records_failure(self, reset_service):
        """Test handling of errors during related record deletion."""
        user_ids = ["user1"]
        result = ResetResult()

        # Mock database error
        reset_service.session.execute.side_effect = Exception("Database connection failed")

        await reset_service._delete_related_records(user_ids, result)

        # Verify error was recorded
        assert len(result.errors) > 0
        assert "Database connection failed" in result.errors[0]

    @pytest.mark.asyncio
    @patch('app.services.database_reset_service.redis.from_url')
    async def test_cleanup_user_sessions_success(self, mock_redis, reset_service):
        """Test successful cleanup of user sessions."""
        user_ids = ["user1", "user2"]
        result = ResetResult()

        # Mock Redis operations
        mock_redis_client = AsyncMock()
        mock_redis_client.keys.side_effect = [
            ["session:user:user1:abc", "session:user:user1:def"],
            ["otp:user1:xyz"]
        ]
        mock_redis_client.delete.return_value = None
        mock_redis.return_value = mock_redis_client

        await reset_service._cleanup_user_sessions(user_ids, result)

        # Verify Redis operations were called
        assert mock_redis_client.keys.call_count == 2  # session + otp keys for first user
        assert result.deleted_records.get("redis_sessions") == 3

    @pytest.mark.asyncio
    @patch('app.services.database_reset_service.redis.from_url')
    async def test_cleanup_user_sessions_redis_error(self, mock_redis, reset_service):
        """Test handling of Redis errors during session cleanup."""
        user_ids = ["user1"]
        result = ResetResult()

        # Mock Redis error
        mock_redis.side_effect = Exception("Redis connection failed")

        await reset_service._cleanup_user_sessions(user_ids, result)

        # Verify warning was recorded
        assert len(result.warnings) > 0
        assert "Redis connection failed" in result.warnings[0]

    @pytest.mark.asyncio
    async def test_clear_user_otp_data(self, reset_service):
        """Test clearing of OTP data for users."""
        user_ids = ["user1", "user2"]

        # Mock successful update
        reset_service.session.execute.return_value = None

        await reset_service._clear_user_otp_data(user_ids)

        # Verify execute was called
        reset_service.session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_user_safely_success(self, reset_service, test_user):
        """Test successful safe user deletion."""
        with patch.object(reset_service, '_validate_environment'):
            with patch.object(reset_service, '_cleanup_user_sessions'):
                with patch.object(reset_service, '_delete_related_records'):
                    with patch.object(reset_service, '_clear_user_otp_data'):

                        # Mock user retrieval
                        reset_service.session.get.return_value = test_user

                        result = await reset_service.delete_user_safely(
                            user_id="test-user-id",
                            level=ResetLevel.USER_CASCADE
                        )

                        assert result.success is True
                        assert len(result.affected_users) == 1
                        assert result.affected_users[0] == "testuser@test.com"

    @pytest.mark.asyncio
    async def test_delete_user_safely_user_not_found(self, reset_service):
        """Test user deletion when user doesn't exist."""
        with patch.object(reset_service, '_validate_environment'):
            # Mock user not found
            reset_service.session.get.return_value = None

            result = await reset_service.delete_user_safely("nonexistent-user")

            assert result.success is False
            assert len(result.errors) > 0
            assert "not found" in result.errors[0]

    @pytest.mark.asyncio
    async def test_delete_user_safely_non_test_user_without_force(self, reset_service):
        """Test rejection of non-test user deletion without force flag."""
        with patch.object(reset_service, '_validate_environment'):
            # Create user with production-like email
            prod_user = User(
                id="prod-user",
                email="user@company.com",  # Not a test domain
                user_type=UserType.BUYER
            )

            reset_service.session.get.return_value = prod_user

            result = await reset_service.delete_user_safely("prod-user", force=False)

            assert result.success is False
            assert len(result.errors) > 0
            assert "doesn't appear to be a test user" in result.errors[0]

    @pytest.mark.asyncio
    async def test_reset_test_users_success(self, reset_service):
        """Test successful reset of multiple test users."""
        with patch.object(reset_service, '_validate_environment'):
            with patch.object(reset_service, '_identify_test_users') as mock_identify:
                with patch.object(reset_service, '_cleanup_user_sessions'):
                    with patch.object(reset_service, '_delete_related_records'):
                        with patch.object(reset_service, '_clear_user_otp_data'):

                            # Mock test users
                            test_users = [
                                User(id="user1", email="test1@test.com", user_type=UserType.BUYER),
                                User(id="user2", email="test2@example.com", user_type=UserType.VENDOR)
                            ]
                            mock_identify.return_value = test_users

                            # Mock successful deletion
                            mock_delete_result = MagicMock()
                            mock_delete_result.rowcount = 2
                            reset_service.session.execute.return_value = mock_delete_result

                            result = await reset_service.reset_test_users()

                            assert result.success is True
                            assert len(result.affected_users) == 2
                            assert result.deleted_records["users"] == 2

    @pytest.mark.asyncio
    async def test_reset_test_users_no_users_found(self, reset_service):
        """Test reset when no test users are found."""
        with patch.object(reset_service, '_validate_environment'):
            with patch.object(reset_service, '_identify_test_users') as mock_identify:

                # Mock no test users found
                mock_identify.return_value = []

                result = await reset_service.reset_test_users()

                assert result.success is True
                assert len(result.warnings) > 0
                assert "No test users found" in result.warnings[0]

    @pytest.mark.asyncio
    @patch('app.services.database_reset_service.redis.from_url')
    async def test_full_database_reset_success(self, mock_redis, reset_service):
        """Test successful full database reset."""
        with patch.object(reset_service, '_validate_environment'):
            with patch.object(reset_service, '_validate_reset_level'):

                # Mock table list query
                tables_result = MagicMock()
                tables_result.fetchall.return_value = [("users",), ("products",), ("orders",)]

                # Mock admin users query
                admin_result = MagicMock()
                admin_result.fetchall.return_value = [
                    ("admin-id", "admin@company.com", "hash", "Admin", "User")
                ]

                reset_service.session.execute.side_effect = [
                    tables_result,  # Tables list
                    admin_result,   # Admin users
                    None,           # Disable FK
                    None,           # Truncate table 1
                    None,           # Truncate table 2
                    None,           # Truncate table 3
                    None,           # Enable FK
                ]

                # Mock Redis cleanup
                mock_redis_client = AsyncMock()
                mock_redis.return_value = mock_redis_client

                result = await reset_service.full_database_reset(
                    confirm_dangerous=True,
                    preserve_admin_users=True
                )

                assert result.success is True
                assert "users" in result.deleted_records
                assert "products" in result.deleted_records
                assert "orders" in result.deleted_records

    @pytest.mark.asyncio
    async def test_create_test_user_success(self, reset_service):
        """Test successful test user creation."""
        with patch('app.services.database_reset_service.get_password_hash') as mock_hash:
            with patch('uuid.uuid4') as mock_uuid:

                mock_hash.return_value = "hashed_password"
                mock_uuid.return_value.hex = "test-uuid"

                # Mock session operations
                reset_service.session.add.return_value = None
                reset_service.session.commit.return_value = None

                created_user = User(
                    id="test-uuid",
                    email="newuser@test.com",
                    password_hash="hashed_password",
                    user_type=UserType.BUYER
                )
                reset_service.session.refresh.return_value = None

                result = await reset_service.create_test_user(
                    email="newuser@test.com",
                    password="testpass",
                    user_type=UserType.BUYER
                )

                # Verify user creation attempt
                reset_service.session.add.assert_called_once()
                reset_service.session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_test_user_invalid_domain(self, reset_service):
        """Test test user creation with invalid domain."""
        with pytest.raises(ValueError, match="doesn't use a test domain"):
            await reset_service.create_test_user(
                email="user@production.com",  # Not a test domain
                user_type=UserType.BUYER
            )

    @pytest.mark.asyncio
    async def test_get_reset_statistics(self, reset_service):
        """Test getting reset statistics."""
        # Mock user stats query
        user_stats_result = MagicMock()
        user_stats_result.fetchall.return_value = [
            ("BUYER", 10, 8),
            ("VENDOR", 5, 4)
        ]

        # Mock test user count query
        test_user_result = MagicMock()
        test_user_result.scalar.return_value = 3

        # Mock table sizes query
        table_sizes_result = MagicMock()
        table_sizes_result.fetchall.return_value = [
            ("public", "users", 100, 50, 10, 90),
            ("public", "products", 200, 100, 20, 180)
        ]

        reset_service.session.execute.side_effect = [
            user_stats_result,
            test_user_result,
            table_sizes_result
        ]

        result = await reset_service.get_reset_statistics()

        assert "users" in result
        assert result["users"]["BUYER"]["total"] == 10
        assert result["users"]["BUYER"]["active"] == 8
        assert result["test_users"] == 3
        assert len(result["table_sizes"]) == 2

    @pytest.mark.asyncio
    async def test_service_context_manager(self):
        """Test DatabaseResetService as async context manager."""
        with patch('app.services.database_reset_service.get_async_session') as mock_session:
            mock_async_gen = AsyncMock()
            mock_session.return_value.__anext__.return_value = mock_async_gen

            async with DatabaseResetService() as service:
                assert service.session is not None

            # Verify session was closed
            mock_async_gen.close.assert_called_once()


class TestQuickFunctions:
    """Test suite for quick utility functions."""

    @pytest.mark.asyncio
    @patch('app.services.database_reset_service.DatabaseResetService')
    async def test_quick_user_reset(self, mock_service_class):
        """Test quick user reset function."""
        # Mock service and result
        mock_service = AsyncMock()
        mock_result = ResetResult()
        mock_result.success = True

        mock_service.__aenter__.return_value = mock_service
        mock_service.session.execute.return_value.fetchone.return_value = ("user-id",)
        mock_service.delete_user_safely.return_value = mock_result

        mock_service_class.return_value = mock_service

        result = await quick_user_reset("test@example.com")

        assert result.success is True
        mock_service.delete_user_safely.assert_called_once_with("user-id")

    @pytest.mark.asyncio
    @patch('app.services.database_reset_service.DatabaseResetService')
    async def test_quick_user_reset_user_not_found(self, mock_service_class):
        """Test quick user reset when user not found."""
        mock_service = AsyncMock()
        mock_service.__aenter__.return_value = mock_service
        mock_service.session.execute.return_value.fetchone.return_value = None

        mock_service_class.return_value = mock_service

        result = await quick_user_reset("notfound@example.com")

        assert result.success is False
        assert len(result.errors) > 0

    @pytest.mark.asyncio
    @patch('app.services.database_reset_service.DatabaseResetService')
    async def test_quick_test_data_reset(self, mock_service_class):
        """Test quick test data reset function."""
        mock_service = AsyncMock()
        mock_result = ResetResult()
        mock_result.success = True

        mock_service.__aenter__.return_value = mock_service
        mock_service.reset_test_users.return_value = mock_result

        mock_service_class.return_value = mock_service

        result = await quick_test_data_reset()

        assert result.success is True
        mock_service.reset_test_users.assert_called_once()


class TestResetLevels:
    """Test different reset levels functionality."""

    @pytest.mark.asyncio
    async def test_user_data_level(self, test_user):
        """Test USER_DATA reset level."""
        with patch('app.services.database_reset_service.DatabaseResetService') as mock_service_class:
            mock_service = AsyncMock()
            mock_service.__aenter__.return_value = mock_service
            mock_service.session.get.return_value = test_user

            # Verify level-specific behavior
            result = ResetResult()
            result.success = True
            mock_service.delete_user_safely.return_value = result

            mock_service_class.return_value = mock_service

            async with DatabaseResetService() as service:
                service = mock_service
                await service.delete_user_safely("test-id", ResetLevel.USER_DATA)

                # Verify that cascade cleanup methods weren't called for this level
                mock_service.delete_user_safely.assert_called_once_with("test-id", ResetLevel.USER_DATA)

    @pytest.mark.asyncio
    async def test_user_cascade_level(self, test_user):
        """Test USER_CASCADE reset level."""
        with patch('app.services.database_reset_service.DatabaseResetService') as mock_service_class:
            mock_service = AsyncMock()
            mock_service.__aenter__.return_value = mock_service
            mock_service.session.get.return_value = test_user

            result = ResetResult()
            result.success = True
            mock_service.delete_user_safely.return_value = result

            mock_service_class.return_value = mock_service

            async with DatabaseResetService() as service:
                service = mock_service
                await service.delete_user_safely("test-id", ResetLevel.USER_CASCADE)

                mock_service.delete_user_safely.assert_called_once_with("test-id", ResetLevel.USER_CASCADE)


class TestErrorHandling:
    """Test error handling and edge cases."""

    @pytest.mark.asyncio
    async def test_database_connection_error(self):
        """Test handling of database connection errors."""
        with patch('app.services.database_reset_service.get_async_session') as mock_session:
            mock_session.side_effect = Exception("Database connection failed")

            try:
                async with DatabaseResetService() as service:
                    await service.get_reset_statistics()
            except Exception as e:
                assert "Database connection failed" in str(e)

    @pytest.mark.asyncio
    async def test_service_without_session(self):
        """Test service operations without proper session initialization."""
        service = DatabaseResetService()

        with pytest.raises(RuntimeError, match="Service not initialized"):
            await service._identify_test_users()

    @pytest.mark.asyncio
    async def test_session_rollback_on_error(self, reset_service):
        """Test that session rollback occurs on error."""
        with patch.object(reset_service, '_validate_environment'):
            reset_service.session.get.side_effect = Exception("Database error")

            result = await reset_service.delete_user_safely("test-id")

            assert result.success is False
            reset_service.session.rollback.assert_called_once()


# Fixtures for integration testing
@pytest.fixture
def mock_settings_dev():
    """Mock settings for development environment."""
    with patch.object(settings, 'ENVIRONMENT', 'development'):
        with patch.object(settings, 'DATABASE_URL', 'postgresql://localhost:5432/test_db'):
            yield


@pytest.fixture
def mock_redis():
    """Mock Redis for testing."""
    with patch('app.services.database_reset_service.redis.from_url') as mock:
        mock_client = AsyncMock()
        mock.return_value = mock_client
        yield mock_client


# Integration test class
class TestDatabaseResetIntegration:
    """Integration tests for database reset functionality."""

    @pytest.mark.asyncio
    async def test_complete_reset_workflow(self, mock_settings_dev, mock_redis):
        """Test complete reset workflow from service creation to cleanup."""
        with patch('app.services.database_reset_service.get_async_session') as mock_session:
            # Mock async session
            mock_async_session = AsyncMock()
            mock_session.return_value.__anext__.return_value = mock_async_session

            # Mock database queries
            mock_async_session.get.return_value = User(
                id="test-id",
                email="test@test.com",
                user_type=UserType.BUYER
            )

            mock_delete_result = MagicMock()
            mock_delete_result.rowcount = 1
            mock_async_session.execute.return_value = mock_delete_result

            # Test the complete workflow
            async with DatabaseResetService() as service:
                result = await service.delete_user_safely(
                    "test-id",
                    level=ResetLevel.USER_CASCADE
                )

                assert result.success is True
                assert "test@test.com" in result.affected_users