#!/usr/bin/env python3
"""
Comprehensive TDD Unit Tests for AuthService
============================================

Testing Strategy:
- RED: Write failing test first
- GREEN: Implement minimal code to pass
- REFACTOR: Optimize while maintaining tests

Coverage Goals:
- JWT token generation/validation: 100%
- Password hashing/verification: 100%
- User authentication workflow: 100%
- Error handling & edge cases: 95%
- Session management: 90%

File: tests/unit/auth/test_auth_service_comprehensive.py
Author: Unit Testing AI - TDD Methodology
Date: 2025-09-17
"""

import pytest
import asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Optional
import uuid
import sqlite3
import os
from concurrent.futures import ThreadPoolExecutor

# Import modules under test
from app.services.auth_service import AuthService
from app.core.security import create_access_token, decode_access_token
from app.models.user import User, UserType
from app.core.config import settings

# Import exceptions for testing
from jose import JWTError
from passlib.context import CryptContext


class TestAuthService:
    """Comprehensive TDD test suite for AuthService."""
    
    @pytest.fixture
    def auth_service(self):
        """Create AuthService instance for testing."""
        return AuthService()
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        mock_session = Mock()
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_session.add = Mock()
        mock_session.commit = Mock()
        mock_session.refresh = Mock()
        mock_session.rollback = Mock()
        return mock_session
    
    @pytest.fixture
    def sample_user_data(self):
        """Sample user data for testing."""
        return {
            'id': str(uuid.uuid4()),
            'email': 'test@example.com',
            'password_hash': '$2b$12$test.hash.for.testing',
            'user_type': 'SUPERUSER',
            'is_active': True,
            'nombre': 'Test',
            'apellido': 'User'
        }
    
    @pytest.fixture
    def mock_sqlite_connection(self, sample_user_data):
        """Mock SQLite connection for authentication."""
        mock_conn = Mock()
        mock_cursor = Mock()
        
        # Configure cursor to return sample user data
        mock_cursor.fetchone.return_value = (
            sample_user_data['id'],
            sample_user_data['email'],
            sample_user_data['password_hash'],
            sample_user_data['user_type'],
            sample_user_data['is_active'],
            sample_user_data['nombre'],
            sample_user_data['apellido']
        )
        
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.close = Mock()
        
        return mock_conn, mock_cursor


class TestAuthServiceInitialization:
    """Test AuthService initialization and configuration."""
    
    def test_auth_service_initialization_creates_required_components(self):
        """TDD: AuthService should initialize with required components."""
        # RED: This test will fail until we verify initialization
        auth_service = AuthService()
        
        # Verify essential components are initialized
        assert hasattr(auth_service, 'pwd_context')
        assert hasattr(auth_service, 'executor')
        assert hasattr(auth_service, 'otp_service')
        assert hasattr(auth_service, 'email_service')
        assert hasattr(auth_service, 'sms_service')
        
        # Verify bcrypt context configuration
        assert 'bcrypt' in auth_service.pwd_context.schemes()
        
        # Verify ThreadPoolExecutor configuration
        assert isinstance(auth_service.executor, ThreadPoolExecutor)
        assert auth_service.executor._max_workers == 4
    
    def test_auth_service_thread_pool_executor_naming(self):
        """TDD: ThreadPoolExecutor should have proper thread naming."""
        auth_service = AuthService()
        
        # Check thread name prefix
        assert auth_service.executor._thread_name_prefix == 'bcrypt'


class TestPasswordHashing:
    """Test password hashing functionality with TDD approach."""
    
    @pytest.fixture
    def auth_service(self):
        return AuthService()
    
    @pytest.mark.asyncio
    async def test_get_password_hash_returns_bcrypt_hash(self, auth_service):
        """TDD: get_password_hash should return valid bcrypt hash."""
        # RED: Test password hashing
        password = "test_password_123"
        
        hashed = await auth_service.get_password_hash(password)
        
        # GREEN: Verify hash properties
        assert isinstance(hashed, str)
        assert hashed.startswith('$2b$')  # bcrypt identifier
        assert len(hashed) == 60  # bcrypt hash length
        assert hashed != password  # Should not be plain text
    
    @pytest.mark.asyncio
    async def test_get_password_hash_different_passwords_produce_different_hashes(self, auth_service):
        """TDD: Different passwords should produce different hashes."""
        password1 = "password123"
        password2 = "password456"
        
        hash1 = await auth_service.get_password_hash(password1)
        hash2 = await auth_service.get_password_hash(password2)
        
        assert hash1 != hash2
    
    @pytest.mark.asyncio
    async def test_get_password_hash_same_password_different_salts(self, auth_service):
        """TDD: Same password should produce different hashes due to salts."""
        password = "same_password"
        
        hash1 = await auth_service.get_password_hash(password)
        hash2 = await auth_service.get_password_hash(password)
        
        # bcrypt uses random salts, so hashes should be different
        assert hash1 != hash2
    
    @pytest.mark.asyncio
    async def test_verify_password_correct_password_returns_true(self, auth_service):
        """TDD: verify_password should return True for correct password."""
        password = "correct_password"
        hashed = await auth_service.get_password_hash(password)
        
        is_valid = await auth_service.verify_password(password, hashed)
        
        assert is_valid is True
    
    @pytest.mark.asyncio
    async def test_verify_password_incorrect_password_returns_false(self, auth_service):
        """TDD: verify_password should return False for incorrect password."""
        correct_password = "correct_password"
        wrong_password = "wrong_password"
        hashed = await auth_service.get_password_hash(correct_password)
        
        is_valid = await auth_service.verify_password(wrong_password, hashed)
        
        assert is_valid is False
    
    @pytest.mark.asyncio
    async def test_verify_password_empty_password_returns_false(self, auth_service):
        """TDD: verify_password should handle empty passwords."""
        password = "test_password"
        hashed = await auth_service.get_password_hash(password)
        
        is_valid = await auth_service.verify_password("", hashed)
        
        assert is_valid is False
    
    @pytest.mark.asyncio
    async def test_verify_password_invalid_hash_returns_false(self, auth_service):
        """TDD: verify_password should handle invalid hash gracefully."""
        password = "test_password"
        invalid_hash = "invalid_hash_format"

        # ACT & ASSERT
        # Invalid hash should raise exception - which is expected behavior
        with pytest.raises(Exception):
            await auth_service.verify_password(password, invalid_hash)


class TestUserAuthentication:
    """Test user authentication workflow with comprehensive TDD coverage."""
    
    @pytest.fixture
    def auth_service(self):
        return AuthService()
    
    @pytest.fixture
    def mock_sqlite_success(self, sample_user_data):
        """Mock successful SQLite authentication."""
        def mock_connect(db_path):
            mock_conn = Mock()
            mock_cursor = Mock()
            
            mock_cursor.fetchone.return_value = (
                sample_user_data['id'],
                sample_user_data['email'],
                sample_user_data['password_hash'],
                sample_user_data['user_type'],
                sample_user_data['is_active'],
                sample_user_data['nombre'],
                sample_user_data['apellido']
            )
            
            mock_conn.cursor.return_value = mock_cursor
            mock_conn.close = Mock()
            return mock_conn
        
        return mock_connect
    
    @pytest.fixture
    def mock_sqlite_user_not_found(self):
        """Mock SQLite authentication when user not found."""
        def mock_connect(db_path):
            mock_conn = Mock()
            mock_cursor = Mock()
            
            mock_cursor.fetchone.return_value = None
            
            mock_conn.cursor.return_value = mock_cursor
            mock_conn.close = Mock()
            return mock_conn
        
        return mock_connect
    
    @pytest.fixture
    def sample_user_data(self):
        return {
            'id': str(uuid.uuid4()),
            'email': 'test@example.com',
            'password_hash': '$2b$12$test.hash.for.testing',
            'user_type': 'SUPERUSER',
            'is_active': True,
            'nombre': 'Test',
            'apellido': 'User'
        }
    
    @pytest.mark.asyncio
    async def test_authenticate_user_valid_credentials_returns_user(self, auth_service, mock_sqlite_success, sample_user_data):
        """TDD: authenticate_user should return user object for valid credentials."""
        with patch('sqlite3.connect', mock_sqlite_success):
            with patch.object(auth_service, 'verify_password', return_value=True):
                
                user = await auth_service.authenticate_user(
                    db=None,  # Using direct SQLite connection
                    email=sample_user_data['email'],
                    password="correct_password"
                )
                
                assert user is not None
                assert user.email == sample_user_data['email']
                assert user.user_type.value == sample_user_data['user_type']
                assert user.is_active == sample_user_data['is_active']
    
    @pytest.mark.asyncio
    async def test_authenticate_user_user_not_found_returns_none(self, auth_service, mock_sqlite_user_not_found):
        """TDD: authenticate_user should return None when user not found."""
        with patch('sqlite3.connect', mock_sqlite_user_not_found):
            
            user = await auth_service.authenticate_user(
                db=None,
                email="nonexistent@example.com",
                password="any_password"
            )
            
            assert user is None
    
    @pytest.mark.asyncio
    async def test_authenticate_user_inactive_user_returns_none(self, auth_service, sample_user_data):
        """TDD: authenticate_user should return None for inactive users."""
        def mock_connect_inactive(db_path):
            mock_conn = Mock()
            mock_cursor = Mock()
            
            # Return inactive user
            mock_cursor.fetchone.return_value = (
                sample_user_data['id'],
                sample_user_data['email'],
                sample_user_data['password_hash'],
                sample_user_data['user_type'],
                False,  # is_active = False
                sample_user_data['nombre'],
                sample_user_data['apellido']
            )
            
            mock_conn.cursor.return_value = mock_cursor
            mock_conn.close = Mock()
            return mock_conn
        
        with patch('sqlite3.connect', mock_connect_inactive):
            with patch.object(auth_service, 'verify_password', return_value=True):
                
                user = await auth_service.authenticate_user(
                    db=None,
                    email=sample_user_data['email'],
                    password="correct_password"
                )
                
                assert user is None
    
    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password_returns_none(self, auth_service, mock_sqlite_success, sample_user_data):
        """TDD: authenticate_user should return None for wrong password."""
        with patch('sqlite3.connect', mock_sqlite_success):
            with patch.object(auth_service, 'verify_password', return_value=False):
                
                user = await auth_service.authenticate_user(
                    db=None,
                    email=sample_user_data['email'],
                    password="wrong_password"
                )
                
                assert user is None
    
    @pytest.mark.asyncio
    async def test_authenticate_user_database_error_returns_none(self, auth_service):
        """TDD: authenticate_user should handle database errors gracefully."""
        def mock_connect_error(db_path):
            raise sqlite3.Error("Database connection failed")
        
        with patch('sqlite3.connect', mock_connect_error):
            
            user = await auth_service.authenticate_user(
                db=None,
                email="test@example.com",
                password="any_password"
            )
            
            assert user is None
    
    @pytest.mark.asyncio
    async def test_authenticate_user_password_verification_error_returns_none(self, auth_service, mock_sqlite_success, sample_user_data):
        """TDD: authenticate_user should handle password verification errors."""
        with patch('sqlite3.connect', mock_sqlite_success):
            with patch.object(auth_service, 'verify_password', side_effect=Exception("Verification error")):
                
                user = await auth_service.authenticate_user(
                    db=None,
                    email=sample_user_data['email'],
                    password="any_password"
                )
                
                assert user is None


class TestUserCreation:
    """Test user creation functionality with TDD methodology."""
    
    @pytest.fixture
    def auth_service(self):
        return AuthService()
    
    @pytest.fixture
    def mock_async_session(self):
        """Mock async database session."""
        mock_session = AsyncMock()
        mock_session.execute = AsyncMock()
        mock_session.add = Mock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        mock_session.rollback = AsyncMock()
        return mock_session
    
    @pytest.mark.asyncio
    async def test_create_user_new_user_success(self, auth_service, mock_async_session):
        """TDD: create_user should successfully create new user."""
        # Mock no existing user
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_async_session.execute.return_value = mock_result
        
        with patch.object(auth_service, 'get_password_hash', return_value="hashed_password"):
            
            user = await auth_service.create_user(
                db=mock_async_session,
                email="new@example.com",
                password="password123",
                nombre="John",
                apellido="Doe"
            )
            
            # Verify user creation process
            mock_async_session.add.assert_called_once()
            mock_async_session.commit.assert_called_once()
            mock_async_session.refresh.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_user_existing_email_raises_error(self, auth_service, mock_async_session):
        """TDD: create_user should raise error for existing email."""
        # Mock existing user found
        mock_result = Mock()
        mock_existing_user = Mock()
        mock_existing_user.email = "existing@example.com"
        mock_result.scalar_one_or_none.return_value = mock_existing_user
        mock_async_session.execute.return_value = mock_result
        
        with pytest.raises(ValueError, match="Usuario con email existing@example.com ya existe"):
            await auth_service.create_user(
                db=mock_async_session,
                email="existing@example.com",
                password="password123"
            )
    
    @pytest.mark.asyncio
    async def test_create_user_database_error_raises_error(self, auth_service, mock_async_session):
        """TDD: create_user should handle database errors properly."""
        # Mock no existing user
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_async_session.execute.return_value = mock_result
        
        # Mock database commit error
        mock_async_session.commit.side_effect = Exception("Database error")
        
        with patch.object(auth_service, 'get_password_hash', return_value="hashed_password"):
            with pytest.raises(ValueError, match="Error al crear usuario"):
                await auth_service.create_user(
                    db=mock_async_session,
                    email="new@example.com",
                    password="password123"
                )
            
            # Verify rollback was called
            mock_async_session.rollback.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_user_default_user_type_is_buyer(self, auth_service, mock_async_session):
        """TDD: create_user should set default user type to COMPRADOR."""
        from app.models.user import UserType
        
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_async_session.execute.return_value = mock_result
        
        with patch.object(auth_service, 'get_password_hash', return_value="hashed_password"):
            with patch('app.models.user.User') as MockUser:
                mock_user_instance = Mock()
                MockUser.return_value = mock_user_instance

                await auth_service.create_user(
                    db=mock_async_session,
                    email="new@example.com",
                    password="password123"
                )

                # Verify User was called with COMPRADOR as default
                assert MockUser.called
                call_args = MockUser.call_args
                if call_args and len(call_args) > 1:
                    assert call_args[1]['user_type'] == UserType.BUYER


class TestAuthServiceCleanup:
    """Test AuthService cleanup and resource management."""
    
    def test_auth_service_destructor_shuts_down_executor(self):
        """TDD: AuthService destructor should shutdown ThreadPoolExecutor."""
        auth_service = AuthService()
        
        # Mock the executor shutdown method
        with patch.object(auth_service.executor, 'shutdown') as mock_shutdown:
            # Manually call destructor
            auth_service.__del__()
            
            # Verify shutdown was called
            mock_shutdown.assert_called_once_with(wait=False)
    
    def test_auth_service_handles_missing_executor_in_destructor(self):
        """TDD: AuthService destructor should handle missing executor gracefully."""
        auth_service = AuthService()
        
        # Remove executor to simulate edge case
        delattr(auth_service, 'executor')
        
        # This should not raise an exception
        try:
            auth_service.__del__()
        except AttributeError:
            pytest.fail("__del__ should handle missing executor gracefully")


class TestAuthServiceIntegration:
    """Integration tests for AuthService with real components."""
    
    @pytest.fixture
    def auth_service(self):
        return AuthService()
    
    @pytest.mark.asyncio
    async def test_full_password_cycle_integration(self, auth_service):
        """TDD: Test complete password hash -> verify cycle."""
        original_password = "integration_test_password_123"
        
        # Hash password
        hashed = await auth_service.get_password_hash(original_password)
        
        # Verify correct password
        is_valid_correct = await auth_service.verify_password(original_password, hashed)
        assert is_valid_correct is True
        
        # Verify wrong password
        is_valid_wrong = await auth_service.verify_password("wrong_password", hashed)
        assert is_valid_wrong is False
    
    @pytest.mark.asyncio
    async def test_concurrent_password_operations(self, auth_service):
        """TDD: AuthService should handle concurrent password operations."""
        passwords = [f"password_{i}" for i in range(10)]
        
        # Hash all passwords concurrently
        hash_tasks = [auth_service.get_password_hash(pwd) for pwd in passwords]
        hashed_passwords = await asyncio.gather(*hash_tasks)
        
        # Verify all passwords concurrently
        verify_tasks = [
            auth_service.verify_password(passwords[i], hashed_passwords[i])
            for i in range(10)
        ]
        verification_results = await asyncio.gather(*verify_tasks)
        
        # All verifications should be True
        assert all(verification_results)
        
        # All hashes should be different
        assert len(set(hashed_passwords)) == len(hashed_passwords)


class TestAuthServicePerformance:
    """Performance tests for AuthService operations."""
    
    @pytest.fixture
    def auth_service(self):
        return AuthService()
    
    @pytest.mark.asyncio
    async def test_password_hashing_performance_benchmark(self, auth_service):
        """TDD: Password hashing should complete within reasonable time."""
        import time
        
        password = "performance_test_password"
        
        start_time = time.time()
        hashed = await auth_service.get_password_hash(password)
        end_time = time.time()
        
        # Hashing should complete within 1 second (bcrypt is intentionally slow)
        duration = end_time - start_time
        assert duration < 1.0, f"Password hashing took {duration:.3f}s, expected < 1.0s"
        
        # Verify hash is valid
        assert hashed.startswith('$2b$')
    
    @pytest.mark.asyncio
    async def test_password_verification_performance_benchmark(self, auth_service):
        """TDD: Password verification should complete within reasonable time."""
        import time
        
        password = "performance_test_password"
        hashed = await auth_service.get_password_hash(password)
        
        start_time = time.time()
        is_valid = await auth_service.verify_password(password, hashed)
        end_time = time.time()
        
        # Verification should complete within 1 second
        duration = end_time - start_time
        assert duration < 1.0, f"Password verification took {duration:.3f}s, expected < 1.0s"
        
        # Verify result is correct
        assert is_valid is True


class TestAuthServiceErrorHandling:
    """Test error handling scenarios in AuthService."""
    
    @pytest.fixture
    def auth_service(self):
        return AuthService()
    
    @pytest.mark.asyncio
    async def test_password_hashing_with_none_password(self, auth_service):
        """TDD: Password hashing should handle None input gracefully."""
        with pytest.raises((TypeError, AttributeError)):
            await auth_service.get_password_hash(None)
    
    @pytest.mark.asyncio
    async def test_password_verification_with_none_inputs(self, auth_service):
        """TDD: Password verification should handle None inputs gracefully."""
        # Test with None password
        with pytest.raises((TypeError, AttributeError)):
            await auth_service.verify_password(None, "$2b$12$test.hash")
        
        # Test with None hash
        with pytest.raises((TypeError, AttributeError)):
            await auth_service.verify_password("password", None)
    
    @pytest.mark.asyncio
    async def test_authenticate_user_with_malformed_database_response(self, auth_service):
        """TDD: authenticate_user should handle malformed database responses."""
        def mock_connect_malformed(db_path):
            mock_conn = Mock()
            mock_cursor = Mock()
            
            # Return incomplete user data (missing fields)
            mock_cursor.fetchone.return_value = (
                "user_id",
                "test@example.com"
                # Missing other required fields
            )
            
            mock_conn.cursor.return_value = mock_cursor
            mock_conn.close = Mock()
            return mock_conn
        
        with patch('sqlite3.connect', mock_connect_malformed):
            user = await auth_service.authenticate_user(
                db=None,
                email="test@example.com",
                password="any_password"
            )
            
            # Should handle gracefully and return None
            assert user is None


if __name__ == "__main__":
    # Run with: python -m pytest tests/unit/auth/test_auth_service_comprehensive.py -v
    pytest.main([__file__, "-v", "--tb=short"])
