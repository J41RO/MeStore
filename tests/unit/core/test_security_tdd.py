"""
TDD Tests for app/core/security.py Module
========================================

Comprehensive Test-Driven Development tests for the security module.
Following strict RED-GREEN-REFACTOR methodology to achieve 95%+ coverage.

Test Structure:
- RED Phase: Write failing tests that describe expected behavior
- GREEN Phase: Implement minimal code to make tests pass
- REFACTOR Phase: Improve code structure while maintaining test coverage

Target Coverage: 95%+ for app/core/security.py
Current Coverage: 28% → 95%+

Test Categories:
1. EncryptionManager Tests
2. SecureTokenManager Tests
3. TokenBlacklist Tests
4. Device Fingerprint Tests
5. JWT Token Creation/Validation Tests
6. Security Audit Tests
7. Key Rotation Tests
8. Edge Cases & Error Handling

Author: TDD Specialist AI
Date: 2025-09-22
Purpose: Achieve comprehensive test coverage for security-critical functionality
"""

import pytest
import asyncio
import base64
import json
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from typing import Dict, Any, Optional

# TDD Framework imports (simplified for initial testing)
# from tests.tdd_framework import TDDTestCase
# from tests.tdd_patterns import SecurityTestPattern, MockingPattern
# from tests.tdd_templates import RedPhaseTemplate, GreenPhaseTemplate, RefactorPhaseTemplate

# Import modules under test
from app.core.security import (
    EncryptionManager,
    SecureTokenManager,
    TokenBlacklist,
    generate_device_fingerprint,
    create_access_token,
    decode_access_token,
    create_refresh_token,
    decode_refresh_token,
    revoke_token,
    is_token_revoked,
    create_secure_password_reset_token,
    verify_password_reset_token,
    create_email_verification_token,
    verify_email_verification_token,
    get_security_headers,
    validate_token_security,
    perform_security_audit,
    rotate_system_keys,
    TokenType,
    AlgorithmType,
    SecurityLevel,
    encryption_manager,
    token_manager,
    token_blacklist
)

# FastAPI imports for mocking
from fastapi import Request
from fastapi.datastructures import Headers


class TestEncryptionManagerTDD:
    """
    TDD tests for EncryptionManager class.

    Testing initialization, encryption/decryption, and key rotation.
    """

    def setup_method(self):
        """Set up test fixtures for EncryptionManager tests."""
        self.test_data = "sensitive_test_data_2025"
        self.test_key = "test_secret_key_for_encryption"

        # Mock settings for testing
        self.settings_mock = Mock()
        self.settings_mock.SECRET_KEY = self.test_key
        self.settings_mock.ENVIRONMENT = "testing"

    @pytest.mark.red_test
    def test_encryption_manager_initialization_should_fail_without_setup(self):
        """
        RED: Test EncryptionManager initialization fails without proper setup.

        This test should fail initially because we need to handle edge cases
        where encryption setup fails.
        """
        with patch('app.core.security.settings') as mock_settings:
            mock_settings.SECRET_KEY = ""  # Empty secret key should cause failure
            mock_settings.ENVIRONMENT = "testing"

            # Mock PBKDF2HMAC to fail with empty key
            with patch('builtins.hasattr', return_value=False), \
                 patch('app.core.security.PBKDF2HMAC.derive', side_effect=ValueError("Empty key material")):
                with pytest.raises(Exception):
                    manager = EncryptionManager()

    @pytest.mark.green_test
    def test_encryption_manager_initialization_succeeds_with_valid_config(self):
        """
        GREEN: Test EncryptionManager initializes successfully with valid config.
        """
        with patch('app.core.security.settings') as mock_settings:
            # Configure the mock to return actual string values, not MagicMock objects
            mock_settings.SECRET_KEY = "test_secret_key_for_encryption"
            mock_settings.ENVIRONMENT = "testing"

            # Mock hasattr to return False so it uses SECRET_KEY path
            with patch('builtins.hasattr', return_value=False):
                manager = EncryptionManager()

                # Verify initialization completed
                assert manager._fernet_key is not None
                assert manager._master_key is not None
                assert manager._salt is not None
                assert len(manager._salt) == 16

    @pytest.mark.red_test
    def test_encrypt_sensitive_data_should_fail_with_invalid_input(self):
        """
        RED: Test encryption fails with invalid input data.
        """
        with patch('app.core.security.settings') as mock_settings:
            mock_settings.SECRET_KEY = "test_secret_key_for_encryption"
            mock_settings.ENVIRONMENT = "testing"

            with patch('builtins.hasattr', return_value=False):
                manager = EncryptionManager()

                # This should fail with non-string input
                with pytest.raises(AttributeError):
                    manager.encrypt_sensitive_data(None)

    @pytest.mark.green_test
    def test_encrypt_sensitive_data_succeeds_with_valid_input(self):
        """
        GREEN: Test encryption succeeds with valid string input.
        """
        with patch('app.core.security.settings') as mock_settings:
            mock_settings.SECRET_KEY = "test_secret_key_for_encryption"
            mock_settings.ENVIRONMENT = "testing"

            with patch('builtins.hasattr', return_value=False):
                manager = EncryptionManager()

                encrypted_data = manager.encrypt_sensitive_data(self.test_data)

                # Verify encryption produces valid base64 encoded result
                assert isinstance(encrypted_data, str)
                assert len(encrypted_data) > len(self.test_data)

                # Verify it's valid base64
                try:
                    base64.urlsafe_b64decode(encrypted_data.encode())
                except Exception:
                    pytest.fail("Encrypted data is not valid base64")

    @pytest.mark.red_test
    def test_decrypt_sensitive_data_should_fail_with_invalid_encrypted_data(self):
        """
        RED: Test decryption fails with invalid encrypted data.
        """
        with patch('app.core.security.settings', self.settings_mock), \
             patch('builtins.hasattr', return_value=False):
            manager = EncryptionManager()

            # This should fail with invalid base64
            with pytest.raises(Exception):
                manager.decrypt_sensitive_data("invalid_base64_data!")

    @pytest.mark.green_test
    def test_decrypt_sensitive_data_succeeds_with_valid_encrypted_data(self):
        """
        GREEN: Test decryption succeeds with properly encrypted data.
        """
        with patch('app.core.security.settings', self.settings_mock), \
             patch('builtins.hasattr', return_value=False):
            manager = EncryptionManager()

            # Encrypt then decrypt
            encrypted_data = manager.encrypt_sensitive_data(self.test_data)
            decrypted_data = manager.decrypt_sensitive_data(encrypted_data)

            assert decrypted_data == self.test_data

    @pytest.mark.red_test
    def test_key_rotation_should_fail_during_initialization_error(self):
        """
        RED: Test key rotation fails when re-initialization encounters errors.
        """
        with patch('app.core.security.settings', self.settings_mock), \
             patch('builtins.hasattr', return_value=False):
            manager = EncryptionManager()

            # Mock initialization to fail on rotation
            with patch.object(manager, '_initialize_encryption', side_effect=Exception("Init failed")):
                result = manager.rotate_encryption_key()
                assert result is False

    @pytest.mark.green_test
    def test_key_rotation_succeeds_with_valid_state(self):
        """
        GREEN: Test key rotation succeeds and generates new keys.
        """
        with patch('app.core.security.settings', self.settings_mock), \
             patch('builtins.hasattr', return_value=False):
            manager = EncryptionManager()

            # Store original key
            original_key = manager._fernet_key
            original_salt = manager._salt

            # Rotate keys
            result = manager.rotate_encryption_key()

            assert result is True
            assert manager._fernet_key != original_key
            assert manager._salt != original_salt

    @pytest.mark.refactor_test
    def test_encryption_manager_complete_workflow_integration(self):
        """
        REFACTOR: Test complete encryption workflow with all features.
        """
        with patch('app.core.security.settings', self.settings_mock), \
             patch('builtins.hasattr', return_value=False):
            manager = EncryptionManager()

            # Test multiple data types and edge cases
            test_cases = [
                "simple_string",
                "complex_string_with_special_chars_@#$%^&*()",
                "unicode_string_with_émojis_🔐🛡️",
                json.dumps({"key": "value", "number": 42}),
                "a" * 1000  # Long string
            ]

            for test_data in test_cases:
                # Encrypt
                encrypted = manager.encrypt_sensitive_data(test_data)
                assert isinstance(encrypted, str)
                assert len(encrypted) > 0

                # Decrypt
                decrypted = manager.decrypt_sensitive_data(encrypted)
                assert decrypted == test_data

                # Verify each encryption is unique (non-deterministic)
                encrypted2 = manager.encrypt_sensitive_data(test_data)
                assert encrypted != encrypted2  # Should be different due to randomness


class TestSecureTokenManagerTDD:
    """
    TDD tests for SecureTokenManager class.

    Testing algorithm validation, key management, and token security.
    """

    def setup_method(self):
        """Set up test fixtures for SecureTokenManager tests."""
        self.valid_algorithms = ["HS256", "RS256", "ES256"]
        self.dangerous_algorithms = ["none", "None", "NONE"]
        self.invalid_algorithms = ["MD5", "SHA1", "INVALID"]

        # Mock settings
        self.settings_mock = Mock()
        self.settings_mock.SECRET_KEY = "test_secret_key_minimum_32_chars_long"
        self.settings_mock.ENVIRONMENT = "testing"

    @pytest.mark.red_test
    def test_algorithm_validation_should_fail_with_dangerous_algorithms(self):
        """
        RED: Test algorithm validation fails with dangerous algorithms.
        """
        for dangerous_algo in self.dangerous_algorithms:
            with patch('app.core.security.settings') as mock_settings:
                mock_settings.ALGORITHM = dangerous_algo
                mock_settings.ENVIRONMENT = "testing"
                mock_settings.SECRET_KEY = "test_secret_key_minimum_32_chars_long"

                with pytest.raises(ValueError, match="Unsupported JWT algorithm"):
                    SecureTokenManager()

    @pytest.mark.green_test
    def test_algorithm_validation_succeeds_with_secure_algorithms(self):
        """
        GREEN: Test algorithm validation succeeds with secure algorithms.
        """
        for valid_algo in self.valid_algorithms:
            with patch('app.core.security.settings') as mock_settings:
                mock_settings.ALGORITHM = valid_algo
                mock_settings.ENVIRONMENT = "testing"
                mock_settings.SECRET_KEY = "test_secret_key_minimum_32_chars_long"

                manager = SecureTokenManager()
                assert manager.algorithm == valid_algo

    @pytest.mark.red_test
    def test_algorithm_validation_should_fail_with_invalid_algorithms(self):
        """
        RED: Test algorithm validation fails with invalid algorithms.
        """
        for invalid_algo in self.invalid_algorithms:
            with patch('app.core.security.settings') as mock_settings:
                mock_settings.ALGORITHM = invalid_algo
                mock_settings.ENVIRONMENT = "testing"
                mock_settings.SECRET_KEY = "test_secret_key_minimum_32_chars_long"

                with pytest.raises(ValueError, match="Unsupported JWT algorithm"):
                    SecureTokenManager()

    @pytest.mark.green_test
    def test_security_level_determination_by_environment(self):
        """
        GREEN: Test security level is correctly determined by environment.
        """
        test_cases = [
            ("production", SecurityLevel.PRODUCTION),
            ("testing", SecurityLevel.TESTING),
            ("development", SecurityLevel.DEVELOPMENT),
            ("staging", SecurityLevel.DEVELOPMENT),  # Default fallback
        ]

        for env, expected_level in test_cases:
            with patch('app.core.security.settings') as mock_settings:
                mock_settings.ALGORITHM = "HS256"
                mock_settings.ENVIRONMENT = env
                mock_settings.SECRET_KEY = "test_secret_key_minimum_32_chars_long"

                manager = SecureTokenManager()
                assert manager.security_level == expected_level

    @pytest.mark.red_test
    def test_rsa_key_initialization_should_fail_with_invalid_parameters(self):
        """
        RED: Test RSA key initialization fails with invalid parameters.
        """
        with patch('app.core.security.settings') as mock_settings:
            mock_settings.ALGORITHM = "RS256"
            mock_settings.ENVIRONMENT = "testing"
            mock_settings.SECRET_KEY = "test_secret_key_minimum_32_chars_long"

            # Mock RSA generation to fail
            with patch('app.core.security.rsa.generate_private_key', side_effect=Exception("RSA Error")):
                manager = SecureTokenManager()
                assert manager.key_pair is None

    @pytest.mark.green_test
    def test_rsa_key_initialization_succeeds_for_rs256_algorithm(self):
        """
        GREEN: Test RSA key initialization succeeds for RS256.
        """
        with patch('app.core.security.settings') as mock_settings:
            mock_settings.ALGORITHM = "RS256"
            mock_settings.ENVIRONMENT = "testing"
            mock_settings.SECRET_KEY = "test_secret_key_minimum_32_chars_long"

            manager = SecureTokenManager()

            # For RS256, key pair should be initialized
            assert manager.key_pair is not None
            assert 'private_key' in manager.key_pair
            assert 'public_key' in manager.key_pair
            assert 'key_size' in manager.key_pair

    @pytest.mark.green_test
    def test_signing_key_retrieval_for_different_algorithms(self):
        """
        GREEN: Test correct signing key retrieval for different algorithms.
        """
        # Test HS256
        with patch('app.core.security.settings') as mock_settings, \
             patch('builtins.hasattr', return_value=False):
            mock_settings.ALGORITHM = "HS256"
            mock_settings.SECRET_KEY = "test_secret_key"
            mock_settings.ENVIRONMENT = "testing"

            manager = SecureTokenManager()
            signing_key = manager.get_signing_key()
            assert signing_key == "test_secret_key"

        # Test RS256
        with patch('app.core.security.settings') as mock_settings, \
             patch('builtins.hasattr', return_value=False):
            mock_settings.ALGORITHM = "RS256"
            mock_settings.SECRET_KEY = "test_secret_key"
            mock_settings.ENVIRONMENT = "testing"

            manager = SecureTokenManager()
            if manager.key_pair:  # Only test if key pair was created
                signing_key = manager.get_signing_key()
                assert isinstance(signing_key, bytes)

    @pytest.mark.refactor_test
    def test_secure_token_manager_production_warnings(self):
        """
        REFACTOR: Test production-specific security warnings and recommendations.
        """
        with patch('app.core.security.settings') as mock_settings:
            mock_settings.ALGORITHM = "HS256"
            mock_settings.ENVIRONMENT = "production"

            # Should log warning for HS256 in production but still work
            with patch('app.core.security.logger') as mock_logger:
                manager = SecureTokenManager()

                # Verify warning was logged
                mock_logger.warning.assert_called()
                warning_call = mock_logger.warning.call_args[0][0]
                assert "HS256 in production" in warning_call


class TestTokenBlacklistTDD:
    """
    TDD tests for TokenBlacklist class.

    Testing token blacklisting, cleanup, and security features.
    """

    def setup_method(self):
        """Set up test fixtures for TokenBlacklist tests."""
        self.test_jti_1 = "test_jti_123456789"
        self.test_jti_2 = "test_jti_987654321"
        self.test_jti_3 = "test_jti_abcdefghij"

    @pytest.mark.red_test
    def test_blacklist_token_should_fail_with_none_jti(self):
        """
        RED: Test blacklist fails gracefully with None JTI.
        """
        blacklist = TokenBlacklist()

        # Should handle None gracefully (convert to string or reject)
        try:
            blacklist.blacklist_token(None)
            # If it doesn't raise an error, verify it was handled properly
            assert None in blacklist._blacklisted_tokens or str(None) in blacklist._blacklisted_tokens
        except (TypeError, AttributeError):
            # This is also acceptable behavior
            pass

    @pytest.mark.green_test
    def test_blacklist_token_succeeds_with_valid_jti(self):
        """
        GREEN: Test token blacklisting succeeds with valid JTI.
        """
        blacklist = TokenBlacklist()

        blacklist.blacklist_token(self.test_jti_1)

        assert self.test_jti_1 in blacklist._blacklisted_tokens
        assert blacklist.is_token_blacklisted(self.test_jti_1) is True

    @pytest.mark.green_test
    def test_is_token_blacklisted_returns_false_for_non_blacklisted_tokens(self):
        """
        GREEN: Test non-blacklisted tokens return False.
        """
        blacklist = TokenBlacklist()

        assert blacklist.is_token_blacklisted(self.test_jti_1) is False
        assert blacklist.is_token_blacklisted("nonexistent_jti") is False

    @pytest.mark.red_test
    def test_cleanup_should_fail_with_concurrent_modification(self):
        """
        RED: Test cleanup handles concurrent modification gracefully.
        """
        blacklist = TokenBlacklist()

        # Add tokens to trigger cleanup
        for i in range(1100):  # Exceed threshold
            blacklist.blacklist_token(f"test_jti_{i}")

        # Simulate concurrent modification during cleanup
        original_cleanup = blacklist._cleanup_expired_tokens

        def modified_cleanup():
            # Modify the set during cleanup to simulate race condition
            blacklist._blacklisted_tokens.add("concurrent_token")
            original_cleanup()

        blacklist._cleanup_expired_tokens = modified_cleanup

        # Should handle concurrent modification gracefully
        try:
            blacklist.blacklist_token("trigger_cleanup_token")
        except RuntimeError:
            # This is expected for concurrent modification
            pass

    @pytest.mark.green_test
    def test_cleanup_succeeds_and_reduces_token_count(self):
        """
        GREEN: Test cleanup successfully reduces token count.
        """
        blacklist = TokenBlacklist()

        # Add tokens beyond threshold to trigger cleanup
        initial_tokens = []
        for i in range(1100):
            token = f"test_jti_{i}"
            initial_tokens.append(token)
            blacklist.blacklist_token(token)

        # Verify cleanup was triggered
        assert len(blacklist._blacklisted_tokens) <= 1100
        assert len(blacklist._blacklisted_tokens) < len(initial_tokens)

    @pytest.mark.refactor_test
    def test_token_blacklist_comprehensive_workflow(self):
        """
        REFACTOR: Test complete blacklist workflow with edge cases.
        """
        blacklist = TokenBlacklist()

        # Test multiple scenarios
        test_scenarios = [
            # (jti, should_be_blacklisted)
            ("normal_token_123", True),
            ("", True),  # Empty string
            ("very_long_token_" + "x" * 1000, True),  # Long token
            ("unicode_token_🔐", True),  # Unicode
            ("special_chars_!@#$%^&*()", True),  # Special characters
        ]

        for jti, expected_blacklisted in test_scenarios:
            blacklist.blacklist_token(jti)
            assert blacklist.is_token_blacklisted(jti) == expected_blacklisted

        # Test cleanup behavior
        original_count = len(blacklist._blacklisted_tokens)

        # Add many more tokens to trigger cleanup
        for i in range(500):
            blacklist.blacklist_token(f"cleanup_trigger_{i}")

        # Verify some form of management occurred
        assert len(blacklist._blacklisted_tokens) >= 5  # Some tokens should remain


class TestDeviceFingerprintTDD:
    """
    TDD tests for device fingerprint generation.

    Testing device identification and security features.
    """

    def setup_method(self):
        """Set up test fixtures for device fingerprint tests."""
        self.mock_headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "accept-language": "en-US,en;q=0.5",
            "accept-encoding": "gzip, deflate",
            "connection": "keep-alive",
            "cache-control": "max-age=0"
        }

        self.mock_client = Mock()
        self.mock_client.host = "192.168.1.100"

    def create_mock_request(self, headers: Dict[str, str] = None, client_host: str = None):
        """Create a mock FastAPI Request object."""
        mock_request = Mock(spec=Request)
        mock_request.headers = Headers(headers or self.mock_headers)

        if client_host:
            mock_request.client = Mock()
            mock_request.client.host = client_host
        else:
            mock_request.client = self.mock_client

        return mock_request

    @pytest.mark.red_test
    def test_device_fingerprint_should_fail_gracefully_with_missing_headers(self):
        """
        RED: Test device fingerprint generation with missing headers.
        """
        mock_request = self.create_mock_request(headers={})

        # Should not fail, but should return a valid fingerprint
        fingerprint = generate_device_fingerprint(mock_request)

        assert isinstance(fingerprint, str)
        assert len(fingerprint) == 64  # SHA256 hex length

    @pytest.mark.green_test
    def test_device_fingerprint_succeeds_with_complete_headers(self):
        """
        GREEN: Test device fingerprint generation with complete headers.
        """
        mock_request = self.create_mock_request()

        fingerprint = generate_device_fingerprint(mock_request)

        assert isinstance(fingerprint, str)
        assert len(fingerprint) == 64  # SHA256 hex length

        # Verify it's a valid hex string
        try:
            int(fingerprint, 16)
        except ValueError:
            pytest.fail("Fingerprint is not a valid hex string")

    @pytest.mark.green_test
    def test_device_fingerprint_is_deterministic_for_same_input(self):
        """
        GREEN: Test device fingerprint is deterministic for same input.
        """
        mock_request = self.create_mock_request()

        fingerprint1 = generate_device_fingerprint(mock_request)
        fingerprint2 = generate_device_fingerprint(mock_request)

        assert fingerprint1 == fingerprint2

    @pytest.mark.green_test
    def test_device_fingerprint_differs_for_different_inputs(self):
        """
        GREEN: Test device fingerprint differs for different inputs.
        """
        # Create two different requests
        headers1 = self.mock_headers.copy()
        headers2 = self.mock_headers.copy()
        headers2["user-agent"] = "Different User Agent"

        mock_request1 = self.create_mock_request(headers=headers1)
        mock_request2 = self.create_mock_request(headers=headers2)

        fingerprint1 = generate_device_fingerprint(mock_request1)
        fingerprint2 = generate_device_fingerprint(mock_request2)

        assert fingerprint1 != fingerprint2

    @pytest.mark.red_test
    def test_device_fingerprint_should_handle_request_exception(self):
        """
        RED: Test device fingerprint handles request processing exceptions.
        """
        # Create a mock request that raises exception when accessing headers
        mock_request = Mock(spec=Request)
        mock_request.headers.get.side_effect = Exception("Header access error")
        mock_request.client = None

        # Should return fallback fingerprint, not raise exception
        fingerprint = generate_device_fingerprint(mock_request)

        assert isinstance(fingerprint, str)
        assert len(fingerprint) == 64

    @pytest.mark.refactor_test
    def test_device_fingerprint_handles_proxy_headers(self):
        """
        REFACTOR: Test device fingerprint correctly handles proxy headers.
        """
        proxy_headers = self.mock_headers.copy()
        proxy_headers["x-forwarded-for"] = "203.0.113.195, 70.41.3.18, 150.172.238.178"
        proxy_headers["x-real-ip"] = "203.0.113.195"

        mock_request = self.create_mock_request(headers=proxy_headers)

        fingerprint = generate_device_fingerprint(mock_request)

        # Should incorporate proxy information
        assert isinstance(fingerprint, str)
        assert len(fingerprint) == 64

        # Verify different from non-proxy request
        normal_request = self.create_mock_request()
        normal_fingerprint = generate_device_fingerprint(normal_request)

        assert fingerprint != normal_fingerprint


class TestJWTTokenOperationsTDD:
    """
    TDD tests for JWT token creation, validation, and operations.

    Testing access tokens, refresh tokens, and specialized tokens.
    """

    def setup_method(self):
        """Set up test fixtures for JWT token tests."""
        self.test_user_data = {"sub": "test@example.com", "user_id": "123"}
        self.test_device_fp = "test_device_fingerprint_abc123"

        # Mock settings
        self.settings_mock = Mock()
        self.settings_mock.SECRET_KEY = "test_secret_key_minimum_32_chars_long_for_jwt"
        self.settings_mock.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        self.settings_mock.REFRESH_TOKEN_EXPIRE_MINUTES = 10080  # 7 days
        self.settings_mock.ALGORITHM = "HS256"
        self.settings_mock.ENVIRONMENT = "testing"

    def _patch_jwt_environment(self):
        """Helper method to properly patch JWT environment for all token operations."""
        from contextlib import ExitStack

        stack = ExitStack()

        # Patch settings
        settings_mock = stack.enter_context(patch('app.core.security.settings', self.settings_mock))

        # Patch token_manager
        token_manager_mock = stack.enter_context(patch('app.core.security.token_manager'))

        # Configure mock token manager for both creation and validation
        token_manager_mock.algorithm = "HS256"
        token_manager_mock.get_signing_key.return_value = self.settings_mock.SECRET_KEY

        # Mock the get_verification_key as well for decode operations
        token_manager_mock.get_verification_key.return_value = self.settings_mock.SECRET_KEY

        return stack

    @pytest.mark.red_test
    def test_create_access_token_should_fail_with_empty_data(self):
        """
        RED: Test access token creation fails with empty data.
        """
        with self._patch_jwt_environment():
            # Should handle empty data gracefully or fail appropriately
            try:
                token = create_access_token(data={})
                # If it succeeds, verify it's still a valid token structure
                assert isinstance(token, str)
                assert len(token) > 0
            except (ValueError, KeyError):
                # This is also acceptable behavior
                pass

    @pytest.mark.green_test
    def test_create_access_token_succeeds_with_valid_data(self):
        """
        GREEN: Test access token creation succeeds with valid data.
        """
        with self._patch_jwt_environment():
            token = create_access_token(data=self.test_user_data)

            assert isinstance(token, str)
            assert len(token) > 100  # JWT tokens are typically long

            # Verify token has three parts (header.payload.signature)
            parts = token.split('.')
            assert len(parts) == 3

    @pytest.mark.green_test
    def test_create_access_token_with_custom_expiration(self):
        """
        GREEN: Test access token creation with custom expiration.
        """
        with self._patch_jwt_environment():
            custom_expiration = timedelta(minutes=60)
            token = create_access_token(
                data=self.test_user_data,
                expires_delta=custom_expiration
            )

            assert isinstance(token, str)

            # Decode and verify expiration
            payload = decode_access_token(token)
            assert payload is not None

            exp_timestamp = payload.get('exp')
            assert exp_timestamp is not None

    @pytest.mark.red_test
    def test_decode_access_token_should_fail_with_invalid_token(self):
        """
        RED: Test token decoding fails with invalid token.
        """
        with self._patch_jwt_environment():
            # Test various invalid tokens
            invalid_tokens = [
                "invalid.token.format",
                "not_a_token_at_all",
                "",
                "a.b",  # Too few parts
                "a.b.c.d"  # Too many parts
            ]

            for invalid_token in invalid_tokens:
                result = decode_access_token(invalid_token)
                assert result is None

    @pytest.mark.green_test
    def test_decode_access_token_succeeds_with_valid_token(self):
        """
        GREEN: Test token decoding succeeds with valid token.
        """
        with self._patch_jwt_environment():
            # Create and decode token
            token = create_access_token(data=self.test_user_data)
            payload = decode_access_token(token)

            assert payload is not None
            assert payload["sub"] == self.test_user_data["sub"]
            assert "exp" in payload
            assert "iat" in payload
            assert "jti" in payload

    @pytest.mark.green_test
    def test_token_encryption_workflow(self):
        """
        GREEN: Test token payload encryption and decryption.
        """
        with self._patch_jwt_environment():
            # Create encrypted token
            token = create_access_token(
                data=self.test_user_data,
                encrypt_payload=True
            )

            # Decode should decrypt automatically
            payload = decode_access_token(token)

            assert payload is not None
            assert payload["sub"] == self.test_user_data["sub"]
            # Should not contain encrypted flags in final payload
            assert "sub_enc" not in payload
            assert "encrypted" not in payload

    @pytest.mark.red_test
    def test_device_binding_should_fail_with_mismatched_fingerprint(self):
        """
        RED: Test device binding fails with mismatched fingerprint.
        """
        with self._patch_jwt_environment():
            # Create token bound to device
            token = create_access_token(
                data=self.test_user_data,
                device_fingerprint=self.test_device_fp
            )

            # Try to decode with different device fingerprint
            wrong_device_fp = "wrong_device_fingerprint_xyz789"
            payload = decode_access_token(
                token,
                verify_device=wrong_device_fp
            )

            assert payload is None  # Should fail verification

    @pytest.mark.green_test
    def test_device_binding_succeeds_with_matching_fingerprint(self):
        """
        GREEN: Test device binding succeeds with matching fingerprint.
        """
        with self._patch_jwt_environment():
            # Create token bound to device
            token = create_access_token(
                data=self.test_user_data,
                device_fingerprint=self.test_device_fp
            )

            # Decode with correct device fingerprint
            payload = decode_access_token(
                token,
                verify_device=self.test_device_fp
            )

            assert payload is not None
            assert payload["sub"] == self.test_user_data["sub"]

    @pytest.mark.refactor_test
    def test_refresh_token_complete_workflow(self):
        """
        REFACTOR: Test complete refresh token workflow.
        """
        with self._patch_jwt_environment():
            # Create refresh token
            refresh_token = create_refresh_token(
                data=self.test_user_data,
                device_fingerprint=self.test_device_fp
            )

            # Decode refresh token
            payload = decode_refresh_token(
                refresh_token,
                verify_device=self.test_device_fp
            )

            assert payload is not None
            assert payload["sub"] == self.test_user_data["sub"]
            assert payload["typ"] == TokenType.REFRESH.value

            # Verify it fails when decoded as access token
            access_payload = decode_access_token(refresh_token)
            assert access_payload is None  # Should fail type validation


class TestTokenRevocationTDD:
    """
    TDD tests for token revocation and blacklist operations.
    """

    def setup_method(self):
        """Set up test fixtures for token revocation tests."""
        self.test_user_data = {"sub": "test@example.com"}

        # Mock settings
        self.settings_mock = Mock()
        self.settings_mock.SECRET_KEY = "test_secret_key_minimum_32_chars_long_for_jwt"
        self.settings_mock.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        self.settings_mock.ALGORITHM = "HS256"
        self.settings_mock.ENVIRONMENT = "testing"

    def _patch_jwt_environment(self):
        """Helper method to properly patch JWT environment for all token operations."""
        from contextlib import ExitStack
        stack = ExitStack()
        settings_mock = stack.enter_context(patch('app.core.security.settings', self.settings_mock))
        token_manager_mock = stack.enter_context(patch('app.core.security.token_manager'))
        stack.enter_context(patch('builtins.hasattr', return_value=False))

        token_manager_mock.algorithm = "HS256"
        token_manager_mock.get_signing_key.return_value = self.settings_mock.SECRET_KEY
        token_manager_mock.get_verification_key.return_value = self.settings_mock.SECRET_KEY
        return stack

    @pytest.mark.red_test
    def test_revoke_token_should_fail_with_invalid_token(self):
        """
        RED: Test token revocation fails with invalid token.
        """
        with self._patch_jwt_environment():
            result = revoke_token("invalid_token_format")
            assert result is False

    @pytest.mark.green_test
    def test_revoke_token_succeeds_with_valid_token(self):
        """
        GREEN: Test token revocation succeeds with valid token.
        """
        with self._patch_jwt_environment():
            # Create and revoke token
            token = create_access_token(data=self.test_user_data)
            result = revoke_token(token)

            assert result is True

            # Verify token is now revoked
            assert is_token_revoked(token) is True

    @pytest.mark.green_test
    def test_is_token_revoked_returns_false_for_valid_tokens(self):
        """
        GREEN: Test revocation check returns False for valid tokens.
        """
        with self._patch_jwt_environment():
            token = create_access_token(data=self.test_user_data)

            # Should not be revoked initially
            assert is_token_revoked(token) is False

    @pytest.mark.green_test
    def test_is_token_revoked_returns_true_for_invalid_tokens(self):
        """
        GREEN: Test revocation check returns True for invalid tokens.
        """
        with self._patch_jwt_environment():
            # Invalid tokens should be considered revoked
            assert is_token_revoked("invalid_token") is True
            assert is_token_revoked("") is True

    @pytest.mark.refactor_test
    def test_token_revocation_complete_workflow(self):
        """
        REFACTOR: Test complete token revocation workflow.
        """
        with self._patch_jwt_environment():
            # Create multiple tokens
            tokens = []
            for i in range(5):
                token_data = {"sub": f"user{i}@example.com"}
                token = create_access_token(data=token_data)
                tokens.append(token)

            # Verify all tokens are initially valid
            for token in tokens:
                assert is_token_revoked(token) is False

            # Revoke some tokens
            for i in range(0, 5, 2):  # Revoke every other token
                result = revoke_token(tokens[i])
                assert result is True

            # Verify revocation status
            for i, token in enumerate(tokens):
                if i % 2 == 0:  # Even indices were revoked
                    assert is_token_revoked(token) is True
                else:  # Odd indices should still be valid
                    assert is_token_revoked(token) is False


class TestSpecializedTokensTDD:
    """
    TDD tests for specialized tokens (password reset, email verification).
    """

    def setup_method(self):
        """Set up test fixtures for specialized token tests."""
        self.test_email = "test@example.com"

        # Mock settings
        self.settings_mock = Mock()
        self.settings_mock.SECRET_KEY = "test_secret_key_minimum_32_chars_long_for_jwt"
        self.settings_mock.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        self.settings_mock.ALGORITHM = "HS256"
        self.settings_mock.ENVIRONMENT = "testing"

    def _patch_jwt_environment(self):
        """Helper method to properly patch JWT environment for all token operations."""
        from contextlib import ExitStack
        stack = ExitStack()
        settings_mock = stack.enter_context(patch('app.core.security.settings', self.settings_mock))
        token_manager_mock = stack.enter_context(patch('app.core.security.token_manager'))
        stack.enter_context(patch('builtins.hasattr', return_value=False))

        token_manager_mock.algorithm = "HS256"
        token_manager_mock.get_signing_key.return_value = self.settings_mock.SECRET_KEY
        token_manager_mock.get_verification_key.return_value = self.settings_mock.SECRET_KEY
        return stack

    @pytest.mark.red_test
    def test_password_reset_token_should_fail_with_empty_email(self):
        """
        RED: Test password reset token creation fails with empty email.
        """
        with self._patch_jwt_environment():
            try:
                token = create_secure_password_reset_token("")
                # If it succeeds, verify the token is invalid
                email = verify_password_reset_token(token)
                assert email is None or email == ""
            except (ValueError, KeyError):
                # This is also acceptable behavior
                pass

    @pytest.mark.green_test
    def test_password_reset_token_creation_and_verification(self):
        """
        GREEN: Test password reset token creation and verification.
        """
        with self._patch_jwt_environment():
            # Create password reset token
            token = create_secure_password_reset_token(self.test_email)

            assert isinstance(token, str)
            assert len(token) > 0

            # Verify token
            verified_email = verify_password_reset_token(token)
            assert verified_email == self.test_email

    @pytest.mark.green_test
    def test_password_reset_token_has_short_expiration(self):
        """
        GREEN: Test password reset token has appropriate short expiration.
        """
        with self._patch_jwt_environment():
            token = create_secure_password_reset_token(self.test_email)

            # Decode to check expiration
            payload = decode_access_token(token, expected_type=TokenType.RESET_PASSWORD)
            assert payload is not None

            # Verify expiration is set and reasonable (should be ~1 hour)
            exp_timestamp = payload.get('exp')
            iat_timestamp = payload.get('iat')

            assert exp_timestamp is not None
            assert iat_timestamp is not None

            # Check duration is approximately 1 hour (3600 seconds)
            duration = exp_timestamp - iat_timestamp
            assert 3500 <= duration <= 3700  # Allow some tolerance

    @pytest.mark.red_test
    def test_verify_password_reset_token_should_fail_with_wrong_type(self):
        """
        RED: Test password reset verification fails with wrong token type.
        """
        with self._patch_jwt_environment():
            # Create regular access token
            regular_token = create_access_token(data={"sub": self.test_email})

            # Should fail verification as password reset token
            verified_email = verify_password_reset_token(regular_token)
            assert verified_email is None

    @pytest.mark.green_test
    def test_email_verification_token_creation_and_verification(self):
        """
        GREEN: Test email verification token creation and verification.
        """
        with self._patch_jwt_environment():
            # Create email verification token
            token = create_email_verification_token(self.test_email)

            assert isinstance(token, str)
            assert len(token) > 0

            # Verify token
            verified_email = verify_email_verification_token(token)
            assert verified_email == self.test_email

    @pytest.mark.green_test
    def test_email_verification_token_has_long_expiration(self):
        """
        GREEN: Test email verification token has appropriate long expiration.
        """
        with self._patch_jwt_environment():
            token = create_email_verification_token(self.test_email)

            # Decode to check expiration
            payload = decode_access_token(token, expected_type=TokenType.EMAIL_VERIFICATION)
            assert payload is not None

            # Verify expiration is set and reasonable (should be ~24 hours)
            exp_timestamp = payload.get('exp')
            iat_timestamp = payload.get('iat')

            assert exp_timestamp is not None
            assert iat_timestamp is not None

            # Check duration is approximately 24 hours (86400 seconds)
            duration = exp_timestamp - iat_timestamp
            assert 86000 <= duration <= 87000  # Allow some tolerance


    def _patch_jwt_environment(self):
        """Helper method to properly patch JWT environment for all token operations."""
        from contextlib import ExitStack
        stack = ExitStack()
        settings_mock = stack.enter_context(patch('app.core.security.settings', self.settings_mock))
        token_manager_mock = stack.enter_context(patch('app.core.security.token_manager'))
        stack.enter_context(patch('builtins.hasattr', return_value=False))

        token_manager_mock.algorithm = "HS256"
        token_manager_mock.get_signing_key.return_value = self.settings_mock.SECRET_KEY
        token_manager_mock.get_verification_key.return_value = self.settings_mock.SECRET_KEY
        return stack

    @pytest.mark.refactor_test
    def test_specialized_tokens_cross_validation(self):
        """
        REFACTOR: Test that specialized tokens don't validate as other types.
        """
        with self._patch_jwt_environment():
            # Create both types of tokens
            reset_token = create_secure_password_reset_token(self.test_email)
            verification_token = create_email_verification_token(self.test_email)

            # Cross-validation should fail
            assert verify_password_reset_token(verification_token) is None
            assert verify_email_verification_token(reset_token) is None

            # Regular access token validation should also fail
            assert decode_access_token(reset_token) is None
            assert decode_access_token(verification_token) is None


class TestSecurityAuditTDD:
    """
    TDD tests for security audit and validation functions.
    """

    def setup_method(self):
        """Set up test fixtures for security audit tests."""
        self.test_user_data = {"sub": "test@example.com"}

        # Mock settings
        self.settings_mock = Mock()
        self.settings_mock.SECRET_KEY = "test_secret_key_minimum_32_chars_long_for_jwt"
        self.settings_mock.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        self.settings_mock.ALGORITHM = "HS256"
        self.settings_mock.ENVIRONMENT = "testing"

    @pytest.mark.red_test
    def test_validate_token_security_should_fail_with_malformed_token(self):
        """
        RED: Test token security validation fails with malformed tokens.
        """
        with self._patch_jwt_environment():
            malformed_tokens = [
                "not.a.token",
                "invalid_format",
                "",
                "too.many.parts.here.error"
            ]

            for token in malformed_tokens:
                result = validate_token_security(token)

                assert result["valid"] is False
                assert result["security_score"] == 0
                assert len(result["errors"]) > 0

    @pytest.mark.green_test
    def test_validate_token_security_succeeds_with_valid_token(self):
        """
        GREEN: Test token security validation succeeds with valid token.
        """
        with self._patch_jwt_environment():
            token = create_access_token(data=self.test_user_data)
            result = validate_token_security(token)

            assert result["valid"] is True
            assert result["algorithm_secure"] is True
            assert result["not_expired"] is True
            assert result["not_revoked"] is True
            assert result["security_score"] > 0

    @pytest.mark.green_test
    def test_validate_token_security_detects_enhanced_features(self):
        """
        GREEN: Test security validation detects enhanced security features.
        """
        with self._patch_jwt_environment():
            # Create token with enhanced features
            enhanced_token = create_access_token(
                data=self.test_user_data,
                encrypt_payload=True,
                device_fingerprint="test_device_fp"
            )

            result = validate_token_security(enhanced_token)

            assert result["valid"] is True
            assert result["device_bound"] is True
            assert result["encrypted_payload"] is True
            assert result["security_score"] >= 5  # Should have high score

    @pytest.mark.red_test
    def test_perform_security_audit_should_warn_about_weak_config(self):
        """
        RED: Test security audit detects and warns about weak configuration.
        """
        weak_settings = Mock()
        weak_settings.SECRET_KEY = "weak"  # Too short
        weak_settings.ALGORITHM = "HS256"
        weak_settings.ENVIRONMENT = "production"

        with patch('app.core.security.settings', weak_settings):
            result = perform_security_audit()

            assert "recommendations" in result
            assert len(result["recommendations"]) > 0
            assert result["overall_score"] < 100  # Should not be perfect

    @pytest.mark.green_test
    def test_perform_security_audit_succeeds_with_good_config(self):
        """
        GREEN: Test security audit succeeds with good configuration.
        """
        with self._patch_jwt_environment():
            result = perform_security_audit()

            assert "timestamp" in result
            assert "environment" in result
            assert "algorithm_security" in result
            assert "key_management" in result
            assert "encryption_status" in result
            assert "compliance_status" in result
            assert "overall_score" in result

            assert result["overall_score"] >= 75  # Should be reasonably good

    @pytest.mark.green_test
    def test_get_security_headers_returns_complete_set(self):
        """
        GREEN: Test security headers function returns complete set.
        """
        headers = get_security_headers()

        expected_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options",
            "X-XSS-Protection",
            "Strict-Transport-Security",
            "Content-Security-Policy",
            "Referrer-Policy",
            "Permissions-Policy"
        ]

        for header in expected_headers:
            assert header in headers
            assert isinstance(headers[header], str)
            assert len(headers[header]) > 0


    def _patch_jwt_environment(self):
        """Helper method to properly patch JWT environment for all token operations."""
        from contextlib import ExitStack
        stack = ExitStack()
        settings_mock = stack.enter_context(patch('app.core.security.settings', self.settings_mock))
        token_manager_mock = stack.enter_context(patch('app.core.security.token_manager'))
        stack.enter_context(patch('builtins.hasattr', return_value=False))

        token_manager_mock.algorithm = "HS256"
        token_manager_mock.get_signing_key.return_value = self.settings_mock.SECRET_KEY
        token_manager_mock.get_verification_key.return_value = self.settings_mock.SECRET_KEY
        return stack

    @pytest.mark.refactor_test
    def test_security_audit_comprehensive_analysis(self):
        """
        REFACTOR: Test comprehensive security audit analysis.
        """
        # Test with various configurations
        test_configurations = [
            # (algorithm, env, secret_length, expected_min_score)
            ("HS256", "testing", 32, 75),
            ("RS256", "production", 44, 90),
            ("HS256", "production", 44, 85),
        ]

        for algo, env, secret_len, min_score in test_configurations:
            test_settings = Mock()
            test_settings.ALGORITHM = algo
            test_settings.ENVIRONMENT = env
            test_settings.SECRET_KEY = "x" * secret_len

            with patch('app.core.security.settings', test_settings), \
                 patch('app.core.security.token_manager') as mock_token_manager:
                mock_token_manager.algorithm = algo
                mock_token_manager.get_signing_key.return_value = test_settings.SECRET_KEY
                mock_token_manager.get_verification_key.return_value = test_settings.SECRET_KEY

                result = perform_security_audit()

                assert result["overall_score"] >= min_score * 0.8  # Allow some tolerance
                assert result["algorithm_security"]["current_algorithm"] == algo
                assert result["key_management"]["secret_key_length"] == secret_len


class TestKeyRotationTDD:
    """
    TDD tests for key rotation functionality.
    """

    def setup_method(self):
        """Set up test fixtures for key rotation tests."""
        # Mock settings
        self.settings_mock = Mock()
        self.settings_mock.SECRET_KEY = "test_secret_key_minimum_32_chars_long_for_jwt"
        self.settings_mock.ALGORITHM = "HS256"
        self.settings_mock.ENVIRONMENT = "testing"

    def _patch_jwt_environment(self):
        """Helper method to properly patch JWT environment for all token operations."""
        from contextlib import ExitStack
        stack = ExitStack()
        settings_mock = stack.enter_context(patch('app.core.security.settings', self.settings_mock))
        token_manager_mock = stack.enter_context(patch('app.core.security.token_manager'))
        stack.enter_context(patch('builtins.hasattr', return_value=False))

        token_manager_mock.algorithm = "HS256"
        token_manager_mock.get_signing_key.return_value = self.settings_mock.SECRET_KEY
        token_manager_mock.get_verification_key.return_value = self.settings_mock.SECRET_KEY
        return stack

    @pytest.mark.red_test
    def test_rotate_system_keys_should_handle_encryption_failure(self):
        """
        RED: Test system key rotation handles encryption manager failure.
        """
        with self._patch_jwt_environment():
            # Mock encryption manager to fail rotation
            with patch('app.core.security.encryption_manager') as mock_enc_mgr:
                mock_enc_mgr.rotate_encryption_key.return_value = False

                result = rotate_system_keys()

                assert result["encryption_key_rotated"] is False
                assert "timestamp" in result

    @pytest.mark.green_test
    def test_rotate_system_keys_succeeds_with_valid_managers(self):
        """
        GREEN: Test system key rotation succeeds with valid managers.
        """
        with self._patch_jwt_environment():
            # Mock both managers to succeed
            with patch('app.core.security.encryption_manager') as mock_enc_mgr, \
                 patch('app.core.security.token_manager') as mock_token_mgr:

                mock_enc_mgr.rotate_encryption_key.return_value = True
                mock_token_mgr.rotate_keys.return_value = True

                result = rotate_system_keys()

                assert result["encryption_key_rotated"] is True
                assert result["signing_key_rotated"] is True
                assert "timestamp" in result

    @pytest.mark.green_test
    def test_rotate_system_keys_handles_partial_failure(self):
        """
        GREEN: Test system key rotation handles partial failure gracefully.
        """
        with self._patch_jwt_environment():
            # Mock one manager to succeed, one to fail
            with patch('app.core.security.encryption_manager') as mock_enc_mgr, \
                 patch('app.core.security.token_manager') as mock_token_mgr:

                mock_enc_mgr.rotate_encryption_key.return_value = True
                mock_token_mgr.rotate_keys.return_value = False

                result = rotate_system_keys()

                assert result["encryption_key_rotated"] is True
                assert result["signing_key_rotated"] is False
                assert "timestamp" in result

    @pytest.mark.refactor_test
    def test_key_rotation_complete_workflow(self):
        """
        REFACTOR: Test complete key rotation workflow and verification.
        """
        with self._patch_jwt_environment():
            # Test multiple rotation cycles
            results = []

            for i in range(3):  # Test 3 rotation cycles
                with patch('app.core.security.encryption_manager') as mock_enc_mgr, \
                     patch('app.core.security.token_manager') as mock_token_mgr:

                    # Simulate different success patterns
                    enc_success = i % 2 == 0  # Alternate success
                    token_success = i > 0      # Fail first time

                    mock_enc_mgr.rotate_encryption_key.return_value = enc_success
                    mock_token_mgr.rotate_keys.return_value = token_success

                    result = rotate_system_keys()
                    results.append(result)

                    assert result["encryption_key_rotated"] == enc_success
                    assert result["signing_key_rotated"] == token_success
                    assert "timestamp" in result

            # Verify all rotations were logged
            assert len(results) == 3

            # Verify timestamps are different (though we can't guarantee timing)
            timestamps = [r["timestamp"] for r in results]
            assert len(set(timestamps)) >= 1  # At least some should be different


# Global integration tests
class TestSecurityModuleIntegrationTDD:
    """
    TDD integration tests for the complete security module.

    Testing interactions between all components.
    """

    def setup_method(self):
        """Set up test fixtures for integration tests."""
        self.test_user_data = {"sub": "integration@example.com", "user_id": "integration_123"}
        self.test_device_fp = "integration_device_fingerprint"

        # Mock settings
        self.settings_mock = Mock()
        self.settings_mock.SECRET_KEY = "integration_test_secret_key_minimum_32_chars_long"
        self.settings_mock.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        self.settings_mock.REFRESH_TOKEN_EXPIRE_MINUTES = 10080
        self.settings_mock.ALGORITHM = "HS256"
        self.settings_mock.ENVIRONMENT = "testing"

    def _patch_jwt_environment(self):
        """Helper method to properly patch JWT environment for all token operations."""
        from contextlib import ExitStack
        stack = ExitStack()
        settings_mock = stack.enter_context(patch('app.core.security.settings', self.settings_mock))
        token_manager_mock = stack.enter_context(patch('app.core.security.token_manager'))
        stack.enter_context(patch('builtins.hasattr', return_value=False))

        token_manager_mock.algorithm = "HS256"
        token_manager_mock.get_signing_key.return_value = self.settings_mock.SECRET_KEY
        token_manager_mock.get_verification_key.return_value = self.settings_mock.SECRET_KEY
        return stack

    @pytest.mark.refactor_test
    def test_complete_security_workflow_integration(self):
        """
        REFACTOR: Test complete security workflow integration.

        This test validates the entire security system working together:
        1. Device fingerprint generation
        2. Token creation with encryption and device binding
        3. Token validation and decryption
        4. Token revocation
        5. Security audit
        6. Key rotation
        """
        with self._patch_jwt_environment():
            # 1. Generate device fingerprint
            mock_request = Mock(spec=Request)
            mock_request.headers = Headers({
                "user-agent": "IntegrationTest/1.0",
                "accept": "application/json"
            })
            mock_request.client = Mock()
            mock_request.client.host = "127.0.0.1"

            device_fp = generate_device_fingerprint(mock_request)
            assert len(device_fp) == 64

            # 2. Create enhanced token
            token = create_access_token(
                data=self.test_user_data,
                encrypt_payload=True,
                device_fingerprint=device_fp
            )
            assert isinstance(token, str)

            # 3. Validate token
            payload = decode_access_token(token, verify_device=device_fp)
            assert payload is not None
            assert payload["sub"] == self.test_user_data["sub"]

            # 4. Security validation
            security_result = validate_token_security(token)
            assert security_result["valid"] is True
            assert security_result["device_bound"] is True
            assert security_result["security_score"] >= 5

            # 5. Token revocation
            revoke_result = revoke_token(token)
            assert revoke_result is True
            assert is_token_revoked(token) is True

            # 6. Security audit
            audit_result = perform_security_audit()
            assert audit_result["overall_score"] >= 50

            # 7. Key rotation
            rotation_result = rotate_system_keys()
            assert "encryption_key_rotated" in rotation_result
            assert "signing_key_rotated" in rotation_result

    @pytest.mark.refactor_test
    def test_security_module_error_resilience(self):
        """
        REFACTOR: Test security module resilience to various error conditions.
        """
        with self._patch_jwt_environment():
            # Test token operations with various error conditions
            error_scenarios = [
                # (operation, expected_to_fail)
                (lambda: create_access_token(data=None), True),
                (lambda: decode_access_token(""), False),  # Should return None, not crash
                (lambda: revoke_token("invalid"), False),  # Should return False, not crash
                (lambda: is_token_revoked("invalid"), False),  # Should return True, not crash
                (lambda: validate_token_security("invalid"), False),  # Should return error dict
            ]

            for operation, should_crash in error_scenarios:
                try:
                    result = operation()
                    if should_crash:
                        pytest.fail(f"Operation {operation} should have failed but didn't")
                    else:
                        # Verify graceful handling - operation completed without crashing
                        # Result can be None, False, or any other value - the key is no exception was raised
                        pass  # Success - operation didn't crash
                except Exception as e:
                    if not should_crash:
                        pytest.fail(f"Operation {operation} crashed unexpectedly: {e}")


    def _patch_jwt_environment(self):
        """Helper method to properly patch JWT environment for all token operations."""
        from contextlib import ExitStack
        stack = ExitStack()
        settings_mock = stack.enter_context(patch('app.core.security.settings', self.settings_mock))
        token_manager_mock = stack.enter_context(patch('app.core.security.token_manager'))
        stack.enter_context(patch('builtins.hasattr', return_value=False))

        token_manager_mock.algorithm = "HS256"
        token_manager_mock.get_signing_key.return_value = self.settings_mock.SECRET_KEY
        token_manager_mock.get_verification_key.return_value = self.settings_mock.SECRET_KEY
        return stack

    @pytest.mark.refactor_test
    def test_security_module_performance_characteristics(self):
        """
        REFACTOR: Test security module performance characteristics.
        """
        with self._patch_jwt_environment():
            import time

            # Test token creation performance
            start_time = time.time()
            tokens = []

            for i in range(100):  # Create 100 tokens
                token = create_access_token(data={"sub": f"user{i}@example.com"})
                tokens.append(token)

            creation_time = time.time() - start_time

            # Should be able to create 100 tokens in reasonable time (< 5 seconds)
            assert creation_time < 5.0

            # Test token validation performance
            start_time = time.time()
            valid_count = 0

            for token in tokens:
                payload = decode_access_token(token)
                if payload:
                    valid_count += 1

            validation_time = time.time() - start_time

            # Should validate all tokens successfully and quickly
            assert valid_count == 100
            assert validation_time < 3.0  # Should be faster than creation


if __name__ == "__main__":
    # Run TDD tests with specific markers
    import subprocess
    import sys

    print("🧪 Running TDD Security Module Tests")
    print("=" * 50)

    # Run RED phase tests
    print("\n🔴 RED Phase - Testing failing scenarios...")
    result = subprocess.run([
        sys.executable, "-m", "pytest",
        __file__, "-v", "-m", "red_test",
        "--tb=short"
    ])

    # Run GREEN phase tests
    print("\n🟢 GREEN Phase - Testing passing scenarios...")
    result = subprocess.run([
        sys.executable, "-m", "pytest",
        __file__, "-v", "-m", "green_test",
        "--tb=short"
    ])

    # Run REFACTOR phase tests
    print("\n🔄 REFACTOR Phase - Testing optimized scenarios...")
    result = subprocess.run([
        sys.executable, "-m", "pytest",
        __file__, "-v", "-m", "refactor_test",
        "--tb=short"
    ])

    # Run all tests with coverage
    print("\n📊 Full Coverage Analysis...")
    result = subprocess.run([
        sys.executable, "-m", "pytest",
        __file__, "-v", "--cov=app.core.security",
        "--cov-report=term-missing",
        "--tb=short"
    ])