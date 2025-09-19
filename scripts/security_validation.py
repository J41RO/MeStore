#!/usr/bin/env python3
"""
Security Validation Script for JWT Encryption Standards

This script validates the implementation of enterprise-grade JWT encryption
and security standards for the MeStore marketplace platform.

Usage:
    python scripts/security_validation.py [--environment production] [--verbose]

Features:
- JWT algorithm security validation
- AES-256 encryption verification
- Token binding and device fingerprinting tests
- Colombian compliance validation
- Security audit execution
- Key rotation testing
- Performance benchmarking
"""

import sys
import argparse
import asyncio
import time
import json
from datetime import datetime, timezone
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.security import (
    create_access_token,
    decode_access_token,
    create_refresh_token,
    generate_device_fingerprint,
    encryption_manager,
    token_manager,
    perform_security_audit,
    validate_token_security,
    rotate_system_keys,
    TokenType,
    SecurityLevel
)
from app.core.config import settings


class SecurityValidator:
    """Comprehensive security validation for JWT encryption standards."""

    def __init__(self, verbose=False):
        self.verbose = verbose
        self.results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "environment": settings.ENVIRONMENT,
            "tests": {},
            "summary": {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "warnings": 0
            }
        }

    def log(self, message, level="INFO"):
        """Log message with timestamp."""
        if self.verbose or level in ["ERROR", "WARNING"]:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] {level}: {message}")

    def test_result(self, test_name, passed, message="", warning=False):
        """Record test result."""
        self.results["tests"][test_name] = {
            "passed": passed,
            "message": message,
            "warning": warning,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        self.results["summary"]["total_tests"] += 1
        if passed:
            self.results["summary"]["passed"] += 1
        else:
            self.results["summary"]["failed"] += 1

        if warning:
            self.results["summary"]["warnings"] += 1

        status = "PASS" if passed else "FAIL"
        if warning:
            status += " (WARNING)"

        self.log(f"{test_name}: {status} - {message}")

    def validate_jwt_algorithm_security(self):
        """Validate JWT algorithm security implementation."""
        self.log("Testing JWT algorithm security...")

        try:
            # Test algorithm validation
            current_algo = token_manager.algorithm
            secure_algorithms = ["HS256", "RS256", "ES256"]

            if current_algo in secure_algorithms:
                self.test_result(
                    "jwt_algorithm_secure",
                    True,
                    f"Algorithm {current_algo} is secure"
                )
            else:
                self.test_result(
                    "jwt_algorithm_secure",
                    False,
                    f"Algorithm {current_algo} is not secure"
                )

            # Test production algorithm recommendations
            if settings.ENVIRONMENT == "production" and current_algo == "HS256":
                self.test_result(
                    "jwt_algorithm_production",
                    True,
                    "HS256 in production - consider RS256 upgrade",
                    warning=True
                )
            else:
                self.test_result(
                    "jwt_algorithm_production",
                    True,
                    f"Algorithm {current_algo} appropriate for {settings.ENVIRONMENT}"
                )

            # Test RSA key generation if RS256
            if current_algo == "RS256":
                if token_manager.key_pair:
                    key_size = token_manager.key_pair.get('key_size', 0)
                    if key_size >= 2048:
                        self.test_result(
                            "rsa_key_size",
                            True,
                            f"RSA key size {key_size} bits is secure"
                        )
                    else:
                        self.test_result(
                            "rsa_key_size",
                            False,
                            f"RSA key size {key_size} bits is too small"
                        )
                else:
                    self.test_result(
                        "rsa_key_generation",
                        False,
                        "RSA key pair not generated for RS256"
                    )

        except Exception as e:
            self.test_result(
                "jwt_algorithm_security",
                False,
                f"Algorithm security test failed: {str(e)}"
            )

    def validate_aes256_encryption(self):
        """Validate AES-256 encryption implementation."""
        self.log("Testing AES-256 encryption...")

        try:
            # Test encryption manager initialization
            if encryption_manager._fernet_key:
                self.test_result(
                    "encryption_manager_init",
                    True,
                    "Encryption manager initialized successfully"
                )
            else:
                self.test_result(
                    "encryption_manager_init",
                    False,
                    "Encryption manager not initialized"
                )
                return

            # Test encryption and decryption
            test_data = "user@example.com"
            try:
                encrypted = encryption_manager.encrypt_sensitive_data(test_data)
                decrypted = encryption_manager.decrypt_sensitive_data(encrypted)

                if decrypted == test_data:
                    self.test_result(
                        "aes256_encrypt_decrypt",
                        True,
                        "AES-256 encryption/decryption working correctly"
                    )
                else:
                    self.test_result(
                        "aes256_encrypt_decrypt",
                        False,
                        "Decrypted data does not match original"
                    )
            except Exception as e:
                self.test_result(
                    "aes256_encrypt_decrypt",
                    False,
                    f"Encryption/decryption failed: {str(e)}"
                )

            # Test key derivation
            master_key = encryption_manager._master_key
            if master_key and len(master_key) == 32:
                self.test_result(
                    "pbkdf2_key_derivation",
                    True,
                    "PBKDF2 key derivation generates 256-bit key"
                )
            else:
                self.test_result(
                    "pbkdf2_key_derivation",
                    False,
                    f"Invalid master key length: {len(master_key) if master_key else 0}"
                )

        except Exception as e:
            self.test_result(
                "aes256_encryption",
                False,
                f"AES-256 encryption test failed: {str(e)}"
            )

    def validate_token_binding(self):
        """Validate token binding and device fingerprinting."""
        self.log("Testing token binding and device fingerprinting...")

        try:
            # Create mock request for device fingerprinting
            class MockRequest:
                def __init__(self):
                    self.headers = {
                        "user-agent": "Mozilla/5.0 (Test Browser)",
                        "accept": "application/json",
                        "accept-language": "en-US,en;q=0.9",
                        "accept-encoding": "gzip, deflate"
                    }
                    self.client = type('Client', (), {'host': '192.168.1.100'})()

            mock_request = MockRequest()
            device_fp = generate_device_fingerprint(mock_request)

            if len(device_fp) == 64:  # SHA256 hex length
                self.test_result(
                    "device_fingerprint_generation",
                    True,
                    "Device fingerprint generated successfully"
                )
            else:
                self.test_result(
                    "device_fingerprint_generation",
                    False,
                    f"Invalid device fingerprint length: {len(device_fp)}"
                )

            # Test token binding
            token = create_access_token(
                data={"sub": "user@example.com"},
                device_fingerprint=device_fp
            )

            # Verify with correct device fingerprint
            payload = decode_access_token(token, verify_device=device_fp)
            if payload and payload.get("sub") == "user@example.com":
                self.test_result(
                    "token_device_binding",
                    True,
                    "Token device binding works correctly"
                )
            else:
                self.test_result(
                    "token_device_binding",
                    False,
                    "Token device binding validation failed"
                )

            # Test with wrong device fingerprint
            wrong_fp = "wrong_device_fingerprint"
            payload_wrong = decode_access_token(token, verify_device=wrong_fp)
            if payload_wrong is None:
                self.test_result(
                    "token_binding_security",
                    True,
                    "Token correctly rejects wrong device fingerprint"
                )
            else:
                self.test_result(
                    "token_binding_security",
                    False,
                    "Token incorrectly accepts wrong device fingerprint"
                )

        except Exception as e:
            self.test_result(
                "token_binding",
                False,
                f"Token binding test failed: {str(e)}"
            )

    def validate_payload_encryption(self):
        """Validate JWT payload encryption for sensitive data."""
        self.log("Testing JWT payload encryption...")

        try:
            # Create token with encrypted payload
            token = create_access_token(
                data={"sub": "user@example.com"},
                encrypt_payload=True
            )

            # Check that token doesn't contain plain text
            from jose import jwt
            unverified_payload = jwt.decode(token, options={"verify_signature": False})

            if "sub" not in unverified_payload and "sub_enc" in unverified_payload:
                self.test_result(
                    "payload_encryption",
                    True,
                    "Sensitive data encrypted in JWT payload"
                )
            else:
                self.test_result(
                    "payload_encryption",
                    False,
                    "Sensitive data not properly encrypted"
                )

            # Test decryption during validation
            payload = decode_access_token(token)
            if payload and payload.get("sub") == "user@example.com":
                self.test_result(
                    "payload_decryption",
                    True,
                    "Encrypted payload decrypted correctly"
                )
            else:
                self.test_result(
                    "payload_decryption",
                    False,
                    "Payload decryption failed"
                )

        except Exception as e:
            self.test_result(
                "payload_encryption",
                False,
                f"Payload encryption test failed: {str(e)}"
            )

    def validate_colombian_compliance(self):
        """Validate Colombian data protection compliance."""
        self.log("Testing Colombian compliance features...")

        try:
            # Test compliance metadata in production
            original_level = token_manager.security_level
            token_manager.security_level = SecurityLevel.PRODUCTION

            token = create_access_token(
                data={"sub": "user@example.com"},
                encrypt_payload=True
            )

            payload = decode_access_token(token)
            if payload and "compliance" in payload:
                compliance = payload["compliance"]
                if compliance.get("colombian_data_protection") is True:
                    self.test_result(
                        "colombian_compliance_metadata",
                        True,
                        "Colombian data protection metadata present"
                    )
                else:
                    self.test_result(
                        "colombian_compliance_metadata",
                        False,
                        "Colombian data protection flag not set"
                    )

                # Test data classification
                if "data_classification" in compliance:
                    self.test_result(
                        "data_classification",
                        True,
                        f"Data classified as: {compliance['data_classification']}"
                    )
                else:
                    self.test_result(
                        "data_classification",
                        False,
                        "Data classification missing"
                    )
            else:
                self.test_result(
                    "colombian_compliance",
                    False,
                    "Compliance metadata missing from token"
                )

            # Restore original security level
            token_manager.security_level = original_level

            # Test short expiration for sensitive tokens
            reset_token = create_access_token(
                data={"sub": "user@example.com", "purpose": "password_reset"},
                token_type=TokenType.RESET_PASSWORD,
                expires_delta=None
            )

            from jose import jwt
            reset_payload = jwt.decode(reset_token, options={"verify_signature": False})
            exp_time = datetime.fromtimestamp(reset_payload["exp"], tz=timezone.utc)
            iat_time = datetime.fromtimestamp(reset_payload["iat"], tz=timezone.utc)
            token_lifetime = exp_time - iat_time

            if token_lifetime.total_seconds() <= 3600:  # 1 hour
                self.test_result(
                    "data_retention_compliance",
                    True,
                    f"Sensitive token expires in {token_lifetime.total_seconds()}s"
                )
            else:
                self.test_result(
                    "data_retention_compliance",
                    False,
                    f"Sensitive token lifetime too long: {token_lifetime}"
                )

        except Exception as e:
            self.test_result(
                "colombian_compliance",
                False,
                f"Colombian compliance test failed: {str(e)}"
            )

    def validate_security_audit(self):
        """Validate security audit procedures."""
        self.log("Testing security audit procedures...")

        try:
            # Run comprehensive security audit
            audit_result = perform_security_audit()

            required_sections = [
                "algorithm_security",
                "key_management",
                "encryption_status",
                "compliance_status"
            ]

            for section in required_sections:
                if section in audit_result:
                    self.test_result(
                        f"audit_{section}",
                        True,
                        f"Security audit includes {section}"
                    )
                else:
                    self.test_result(
                        f"audit_{section}",
                        False,
                        f"Security audit missing {section}"
                    )

            # Check overall security score
            overall_score = audit_result.get("overall_score", 0)
            if overall_score >= 75:
                self.test_result(
                    "security_score",
                    True,
                    f"Security score: {overall_score}/100"
                )
            elif overall_score >= 50:
                self.test_result(
                    "security_score",
                    True,
                    f"Security score: {overall_score}/100 (needs improvement)",
                    warning=True
                )
            else:
                self.test_result(
                    "security_score",
                    False,
                    f"Security score too low: {overall_score}/100"
                )

            # Test token security validation
            test_token = create_access_token(
                data={"sub": "user@example.com"},
                encrypt_payload=True
            )

            token_validation = validate_token_security(test_token)
            if token_validation.get("valid") and token_validation.get("security_score", 0) > 5:
                self.test_result(
                    "token_security_validation",
                    True,
                    f"Token validation score: {token_validation['security_score']}"
                )
            else:
                self.test_result(
                    "token_security_validation",
                    False,
                    "Token security validation failed"
                )

        except Exception as e:
            self.test_result(
                "security_audit",
                False,
                f"Security audit test failed: {str(e)}"
            )

    def validate_key_rotation(self):
        """Validate key rotation functionality."""
        self.log("Testing key rotation functionality...")

        try:
            # Test encryption key rotation
            original_key = encryption_manager._master_key

            rotation_success = encryption_manager.rotate_encryption_key()
            if rotation_success:
                new_key = encryption_manager._master_key
                if new_key != original_key:
                    self.test_result(
                        "encryption_key_rotation",
                        True,
                        "Encryption key rotated successfully"
                    )
                else:
                    self.test_result(
                        "encryption_key_rotation",
                        False,
                        "Encryption key not changed after rotation"
                    )
            else:
                self.test_result(
                    "encryption_key_rotation",
                    False,
                    "Encryption key rotation failed"
                )

            # Test system-wide key rotation
            rotation_result = rotate_system_keys()
            if isinstance(rotation_result, dict) and "timestamp" in rotation_result:
                self.test_result(
                    "system_key_rotation",
                    True,
                    "System key rotation executed successfully"
                )
            else:
                self.test_result(
                    "system_key_rotation",
                    False,
                    "System key rotation failed"
                )

        except Exception as e:
            self.test_result(
                "key_rotation",
                False,
                f"Key rotation test failed: {str(e)}"
            )

    def performance_benchmark(self):
        """Run performance benchmarks for security operations."""
        self.log("Running performance benchmarks...")

        try:
            # Benchmark token creation
            start_time = time.time()
            for i in range(100):
                token = create_access_token(
                    data={"sub": f"user{i}@example.com"},
                    encrypt_payload=True
                )
            token_creation_time = time.time() - start_time

            if token_creation_time < 5.0:  # 100 tokens in under 5 seconds
                self.test_result(
                    "token_creation_performance",
                    True,
                    f"100 encrypted tokens created in {token_creation_time:.2f}s"
                )
            else:
                self.test_result(
                    "token_creation_performance",
                    False,
                    f"Token creation too slow: {token_creation_time:.2f}s for 100 tokens",
                    warning=True
                )

            # Benchmark token validation
            test_token = create_access_token(
                data={"sub": "user@example.com"},
                encrypt_payload=True
            )

            start_time = time.time()
            for i in range(100):
                payload = decode_access_token(test_token)
            token_validation_time = time.time() - start_time

            if token_validation_time < 2.0:  # 100 validations in under 2 seconds
                self.test_result(
                    "token_validation_performance",
                    True,
                    f"100 token validations in {token_validation_time:.2f}s"
                )
            else:
                self.test_result(
                    "token_validation_performance",
                    False,
                    f"Token validation too slow: {token_validation_time:.2f}s",
                    warning=True
                )

        except Exception as e:
            self.test_result(
                "performance_benchmark",
                False,
                f"Performance benchmark failed: {str(e)}"
            )

    def run_all_validations(self):
        """Run all security validations."""
        self.log("Starting comprehensive security validation...")

        validation_methods = [
            self.validate_jwt_algorithm_security,
            self.validate_aes256_encryption,
            self.validate_token_binding,
            self.validate_payload_encryption,
            self.validate_colombian_compliance,
            self.validate_security_audit,
            self.validate_key_rotation,
            self.performance_benchmark
        ]

        for validation_method in validation_methods:
            try:
                validation_method()
            except Exception as e:
                method_name = validation_method.__name__
                self.test_result(
                    method_name,
                    False,
                    f"Validation method failed: {str(e)}"
                )

        self.log("Security validation completed")

    def generate_report(self):
        """Generate comprehensive security validation report."""
        summary = self.results["summary"]

        print("\n" + "="*60)
        print("SECURITY VALIDATION REPORT")
        print("="*60)
        print(f"Environment: {self.results['environment']}")
        print(f"Timestamp: {self.results['timestamp']}")
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed']}")
        print(f"Failed: {summary['failed']}")
        print(f"Warnings: {summary['warnings']}")

        success_rate = (summary['passed'] / summary['total_tests'] * 100) if summary['total_tests'] > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")

        if summary['failed'] > 0:
            print("\nFAILED TESTS:")
            for test_name, result in self.results["tests"].items():
                if not result["passed"]:
                    print(f"  ❌ {test_name}: {result['message']}")

        if summary['warnings'] > 0:
            print("\nWARNINGS:")
            for test_name, result in self.results["tests"].items():
                if result["warning"]:
                    print(f"  ⚠️  {test_name}: {result['message']}")

        print("\nSUCCESSFUL TESTS:")
        for test_name, result in self.results["tests"].items():
            if result["passed"] and not result["warning"]:
                print(f"  ✅ {test_name}: {result['message']}")

        print("\n" + "="*60)

        return success_rate >= 90 and summary['failed'] == 0


def main():
    """Main function for security validation script."""
    parser = argparse.ArgumentParser(
        description="Validate JWT encryption security standards implementation"
    )
    parser.add_argument(
        "--environment",
        choices=["development", "testing", "production"],
        default=None,
        help="Override environment for testing"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--output",
        help="Output results to JSON file"
    )

    args = parser.parse_args()

    # Override environment if specified
    if args.environment:
        import app.core.config
        app.core.config.settings.ENVIRONMENT = args.environment

    # Run validation
    validator = SecurityValidator(verbose=args.verbose)
    validator.run_all_validations()

    # Generate report
    success = validator.generate_report()

    # Output to file if specified
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(validator.results, f, indent=2)
        print(f"\nResults saved to: {args.output}")

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()