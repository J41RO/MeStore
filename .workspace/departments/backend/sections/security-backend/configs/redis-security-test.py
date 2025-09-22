#!/usr/bin/env python3
"""
REDIS SECURITY PENETRATION TEST - MeStore Backend Security
============================================================
Security Backend AI - Comprehensive Security Validation
Deployment Priority: IMMEDIATE VALIDATION
Security Testing: Authentication, Authorization, and Data Protection
"""

import asyncio
import redis
import time
import json
import sys
import traceback
from typing import Dict, List, Any
from dataclasses import dataclass, asdict


@dataclass
class SecurityTestResult:
    """Security test result container"""
    test_name: str
    status: str  # PASS, FAIL, WARNING, ERROR
    description: str
    risk_level: int  # 1-10 scale
    details: str = ""
    recommendations: List[str] = None

    def __post_init__(self):
        if self.recommendations is None:
            self.recommendations = []


class RedisSecurityTester:
    """Comprehensive Redis security testing framework"""

    def __init__(self):
        self.results: List[SecurityTestResult] = []
        self.redis_host = "localhost"
        self.redis_port = 6379
        self.secure_password = "mestore-redis-secure-password-2025-min-32-chars"
        self.wrong_password = "wrong-password-for-testing"

    def log_test(self, result: SecurityTestResult):
        """Log test result and add to results list"""
        self.results.append(result)
        status_emoji = {
            "PASS": "✅",
            "FAIL": "❌",
            "WARNING": "⚠️",
            "ERROR": "🔥"
        }

        print(f"{status_emoji.get(result.status, '❓')} {result.test_name}: {result.status}")
        if result.details:
            print(f"   Details: {result.details}")
        if result.recommendations:
            for rec in result.recommendations:
                print(f"   💡 {rec}")
        print()

    def test_unauthenticated_access(self):
        """Test 1: Verify unauthenticated access is blocked"""
        try:
            client = redis.Redis(host=self.redis_host, port=self.redis_port,
                                socket_connect_timeout=5, socket_timeout=5)
            client.ping()

            # If we reach here, authentication is not enabled
            self.log_test(SecurityTestResult(
                test_name="Unauthenticated Access Protection",
                status="FAIL",
                description="Redis allows access without authentication",
                risk_level=10,
                details="Critical vulnerability: Redis accessible without credentials",
                recommendations=[
                    "Enable Redis authentication immediately",
                    "Set requirepass in Redis configuration",
                    "Restart Redis service with authentication"
                ]
            ))
        except redis.AuthenticationError:
            self.log_test(SecurityTestResult(
                test_name="Unauthenticated Access Protection",
                status="PASS",
                description="Authentication required for Redis access",
                risk_level=1,
                details="Redis correctly rejects unauthenticated connections"
            ))
        except redis.ConnectionError as e:
            self.log_test(SecurityTestResult(
                test_name="Unauthenticated Access Protection",
                status="ERROR",
                description="Cannot connect to Redis service",
                risk_level=8,
                details=f"Connection error: {str(e)}",
                recommendations=["Check if Redis service is running", "Verify network connectivity"]
            ))
        except Exception as e:
            self.log_test(SecurityTestResult(
                test_name="Unauthenticated Access Protection",
                status="ERROR",
                description="Unexpected error during authentication test",
                risk_level=5,
                details=f"Error: {str(e)}"
            ))

    def test_wrong_password(self):
        """Test 2: Verify wrong password is rejected"""
        try:
            client = redis.Redis(host=self.redis_host, port=self.redis_port,
                                password=self.wrong_password,
                                socket_connect_timeout=5, socket_timeout=5)
            client.ping()

            # If we reach here, wrong password was accepted
            self.log_test(SecurityTestResult(
                test_name="Wrong Password Rejection",
                status="FAIL",
                description="Redis accepts incorrect password",
                risk_level=9,
                details="Authentication bypass possible with wrong credentials",
                recommendations=[
                    "Verify Redis password configuration",
                    "Check for authentication bypass vulnerabilities",
                    "Review Redis configuration files"
                ]
            ))
        except redis.AuthenticationError:
            self.log_test(SecurityTestResult(
                test_name="Wrong Password Rejection",
                status="PASS",
                description="Wrong password correctly rejected",
                risk_level=1,
                details="Redis properly validates authentication credentials"
            ))
        except Exception as e:
            self.log_test(SecurityTestResult(
                test_name="Wrong Password Rejection",
                status="ERROR",
                description="Error testing wrong password",
                risk_level=3,
                details=f"Error: {str(e)}"
            ))

    def test_correct_password(self):
        """Test 3: Verify correct password is accepted"""
        try:
            client = redis.Redis(host=self.redis_host, port=self.redis_port,
                                password=self.secure_password,
                                socket_connect_timeout=5, socket_timeout=5)
            response = client.ping()

            if response:
                self.log_test(SecurityTestResult(
                    test_name="Correct Password Authentication",
                    status="PASS",
                    description="Correct password accepted",
                    risk_level=1,
                    details="Redis authentication working correctly"
                ))
                return client  # Return for use in other tests
            else:
                self.log_test(SecurityTestResult(
                    test_name="Correct Password Authentication",
                    status="FAIL",
                    description="Correct password rejected",
                    risk_level=8,
                    details="Authentication configured incorrectly",
                    recommendations=["Verify Redis password configuration"]
                ))
        except redis.AuthenticationError:
            self.log_test(SecurityTestResult(
                test_name="Correct Password Authentication",
                status="FAIL",
                description="Correct password rejected",
                risk_level=8,
                details="Password mismatch or configuration error",
                recommendations=[
                    "Verify password in Redis configuration",
                    "Check environment variables",
                    "Confirm Redis restart after configuration change"
                ]
            ))
        except Exception as e:
            self.log_test(SecurityTestResult(
                test_name="Correct Password Authentication",
                status="ERROR",
                description="Error testing correct password",
                risk_level=5,
                details=f"Error: {str(e)}"
            ))

        return None

    def test_dangerous_commands(self, client):
        """Test 4: Verify dangerous commands are disabled"""
        if not client:
            self.log_test(SecurityTestResult(
                test_name="Dangerous Commands Protection",
                status="ERROR",
                description="Cannot test - no authenticated client",
                risk_level=5,
                details="Authentication test must pass first"
            ))
            return

        dangerous_commands = [
            ("FLUSHALL", "Deletes all data from all databases"),
            ("FLUSHDB", "Deletes all data from current database"),
            ("CONFIG", "Allows configuration changes"),
            ("DEBUG", "Provides debug information"),
            ("KEYS", "Can cause performance issues")
        ]

        for command, description in dangerous_commands:
            try:
                if command == "CONFIG":
                    result = client.execute_command("CONFIG", "GET", "requirepass")
                elif command == "KEYS":
                    result = client.execute_command("KEYS", "*")
                else:
                    result = client.execute_command(command)

                # If command succeeds, it's a security issue
                self.log_test(SecurityTestResult(
                    test_name=f"Dangerous Command Protection ({command})",
                    status="WARNING",
                    description=f"{command} command is enabled",
                    risk_level=6,
                    details=f"{description} - Command executed successfully",
                    recommendations=[
                        f"Consider disabling {command} command",
                        "Use Redis rename-command to secure dangerous operations"
                    ]
                ))
            except redis.ResponseError as e:
                if "unknown command" in str(e).lower() or "renamed" in str(e).lower():
                    self.log_test(SecurityTestResult(
                        test_name=f"Dangerous Command Protection ({command})",
                        status="PASS",
                        description=f"{command} command is disabled/renamed",
                        risk_level=1,
                        details=f"Command properly secured: {str(e)}"
                    ))
                else:
                    self.log_test(SecurityTestResult(
                        test_name=f"Dangerous Command Protection ({command})",
                        status="WARNING",
                        description=f"{command} command error",
                        risk_level=3,
                        details=f"Unexpected error: {str(e)}"
                    ))
            except Exception as e:
                self.log_test(SecurityTestResult(
                    test_name=f"Dangerous Command Protection ({command})",
                    status="ERROR",
                    description=f"Error testing {command}",
                    risk_level=3,
                    details=f"Error: {str(e)}"
                ))

    def test_network_security(self):
        """Test 5: Network binding and access control"""
        try:
            # Test if Redis is accessible from different interfaces
            test_hosts = ["127.0.0.1", "localhost", "0.0.0.0"]

            for host in test_hosts:
                try:
                    client = redis.Redis(host=host, port=self.redis_port,
                                       password=self.secure_password,
                                       socket_connect_timeout=2, socket_timeout=2)
                    client.ping()

                    if host == "0.0.0.0":
                        self.log_test(SecurityTestResult(
                            test_name="Network Security (Wildcard Binding)",
                            status="WARNING",
                            description="Redis accessible on all interfaces",
                            risk_level=7,
                            details="Wildcard binding (0.0.0.0) detected",
                            recommendations=[
                                "Bind Redis to specific interfaces only",
                                "Use 'bind 127.0.0.1' for localhost only"
                            ]
                        ))
                    else:
                        self.log_test(SecurityTestResult(
                            test_name=f"Network Security ({host})",
                            status="PASS",
                            description=f"Redis accessible on {host}",
                            risk_level=2,
                            details="Normal network access"
                        ))
                except redis.ConnectionError:
                    self.log_test(SecurityTestResult(
                        test_name=f"Network Security ({host})",
                        status="PASS",
                        description=f"Redis not accessible on {host}",
                        risk_level=1,
                        details="Good - restricted network access"
                    ))
        except Exception as e:
            self.log_test(SecurityTestResult(
                test_name="Network Security Test",
                status="ERROR",
                description="Error testing network security",
                risk_level=5,
                details=f"Error: {str(e)}"
            ))

    def test_data_encryption(self, client):
        """Test 6: Data encryption in transit (TLS)"""
        if not client:
            return

        try:
            # Check if Redis is using TLS
            info = client.info()

            # Look for TLS indicators in Redis info
            tls_enabled = False
            if 'ssl_enabled' in info or 'tls_enabled' in info:
                tls_enabled = True

            if tls_enabled:
                self.log_test(SecurityTestResult(
                    test_name="Data Encryption (TLS)",
                    status="PASS",
                    description="TLS encryption enabled",
                    risk_level=1,
                    details="Data encrypted in transit"
                ))
            else:
                self.log_test(SecurityTestResult(
                    test_name="Data Encryption (TLS)",
                    status="WARNING",
                    description="TLS encryption not detected",
                    risk_level=5,
                    details="Data transmitted in plaintext",
                    recommendations=[
                        "Enable TLS encryption for production",
                        "Configure Redis with TLS certificates"
                    ]
                ))
        except Exception as e:
            self.log_test(SecurityTestResult(
                test_name="Data Encryption (TLS)",
                status="ERROR",
                description="Error checking TLS status",
                risk_level=3,
                details=f"Error: {str(e)}"
            ))

    def test_session_security(self, client):
        """Test 7: Session data security and TTL"""
        if not client:
            return

        try:
            # Test session storage and TTL
            test_session_key = "session:security_test_session"
            test_data = {"user_id": "test_user", "role": "test_role"}

            # Store session data
            client.setex(test_session_key, 10, json.dumps(test_data))

            # Verify storage
            stored_data = client.get(test_session_key)
            if stored_data:
                self.log_test(SecurityTestResult(
                    test_name="Session Storage Security",
                    status="PASS",
                    description="Session data storage working",
                    risk_level=2,
                    details="Session data can be stored and retrieved"
                ))

                # Check TTL
                ttl = client.ttl(test_session_key)
                if ttl > 0:
                    self.log_test(SecurityTestResult(
                        test_name="Session TTL Security",
                        status="PASS",
                        description="Session TTL configured",
                        risk_level=1,
                        details=f"Session expires in {ttl} seconds"
                    ))
                else:
                    self.log_test(SecurityTestResult(
                        test_name="Session TTL Security",
                        status="WARNING",
                        description="Session TTL not set",
                        risk_level=6,
                        details="Sessions may persist indefinitely",
                        recommendations=["Set appropriate TTL for sessions"]
                    ))

                # Clean up
                client.delete(test_session_key)
            else:
                self.log_test(SecurityTestResult(
                    test_name="Session Storage Security",
                    status="FAIL",
                    description="Session data storage failed",
                    risk_level=7,
                    details="Cannot store session data"
                ))
        except Exception as e:
            self.log_test(SecurityTestResult(
                test_name="Session Security Test",
                status="ERROR",
                description="Error testing session security",
                risk_level=5,
                details=f"Error: {str(e)}"
            ))

    def test_performance_security(self, client):
        """Test 8: Performance-related security issues"""
        if not client:
            return

        try:
            # Test memory limits
            info = client.info("memory")
            used_memory = info.get('used_memory', 0)
            max_memory = info.get('maxmemory', 0)

            if max_memory > 0:
                memory_usage_percent = (used_memory / max_memory) * 100
                self.log_test(SecurityTestResult(
                    test_name="Memory Limit Security",
                    status="PASS",
                    description="Memory limits configured",
                    risk_level=2,
                    details=f"Memory usage: {memory_usage_percent:.1f}% of {max_memory} bytes"
                ))
            else:
                self.log_test(SecurityTestResult(
                    test_name="Memory Limit Security",
                    status="WARNING",
                    description="No memory limits configured",
                    risk_level=5,
                    details="Redis may consume unlimited memory",
                    recommendations=["Set maxmemory limit in Redis configuration"]
                ))

            # Test slow log
            slowlog_len = client.execute_command("SLOWLOG", "LEN")
            if isinstance(slowlog_len, int):
                self.log_test(SecurityTestResult(
                    test_name="Performance Monitoring",
                    status="PASS",
                    description="Slow query logging enabled",
                    risk_level=1,
                    details=f"Slow log entries: {slowlog_len}"
                ))

        except Exception as e:
            self.log_test(SecurityTestResult(
                test_name="Performance Security Test",
                status="ERROR",
                description="Error testing performance security",
                risk_level=3,
                details=f"Error: {str(e)}"
            ))

    def run_all_tests(self):
        """Run all security tests"""
        print("🔒 REDIS SECURITY PENETRATION TEST - MeStore Backend Security")
        print("=" * 70)
        print(f"Target: {self.redis_host}:{self.redis_port}")
        print(f"Test Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        print()

        # Run authentication tests
        print("🔐 AUTHENTICATION SECURITY TESTS")
        print("-" * 35)
        self.test_unauthenticated_access()
        self.test_wrong_password()
        authenticated_client = self.test_correct_password()

        # Run authorization and command tests
        print("🚫 AUTHORIZATION & COMMAND SECURITY TESTS")
        print("-" * 45)
        self.test_dangerous_commands(authenticated_client)

        # Run network security tests
        print("🌐 NETWORK SECURITY TESTS")
        print("-" * 25)
        self.test_network_security()

        # Run data security tests
        print("🔐 DATA SECURITY TESTS")
        print("-" * 22)
        self.test_data_encryption(authenticated_client)
        self.test_session_security(authenticated_client)

        # Run performance security tests
        print("⚡ PERFORMANCE SECURITY TESTS")
        print("-" * 29)
        self.test_performance_security(authenticated_client)

    def generate_security_report(self) -> Dict[str, Any]:
        """Generate comprehensive security report"""
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r.status == "PASS"])
        failed_tests = len([r for r in self.results if r.status == "FAIL"])
        warning_tests = len([r for r in self.results if r.status == "WARNING"])
        error_tests = len([r for r in self.results if r.status == "ERROR"])

        # Calculate security score
        max_score = 10
        deductions = sum([
            (10 - r.risk_level) if r.status == "PASS" else r.risk_level
            for r in self.results
        ])
        security_score = max(0, max_score - (deductions / total_tests) if total_tests > 0 else 0)

        # Determine overall status
        if failed_tests > 0:
            overall_status = "CRITICAL"
        elif error_tests > 0:
            overall_status = "ERROR"
        elif warning_tests > 0:
            overall_status = "WARNING"
        else:
            overall_status = "SECURE"

        # Get critical issues
        critical_issues = [r for r in self.results if r.status == "FAIL" and r.risk_level >= 8]

        report = {
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "target": f"{self.redis_host}:{self.redis_port}",
            "overall_status": overall_status,
            "security_score": round(security_score, 1),
            "test_summary": {
                "total": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "warnings": warning_tests,
                "errors": error_tests
            },
            "critical_issues": [asdict(issue) for issue in critical_issues],
            "all_results": [asdict(result) for result in self.results]
        }

        return report

    def print_summary(self):
        """Print test summary"""
        report = self.generate_security_report()

        print("\n" + "=" * 70)
        print("🎯 SECURITY TEST SUMMARY")
        print("=" * 70)
        print(f"Overall Status: {report['overall_status']}")
        print(f"Security Score: {report['security_score']}/10")
        print(f"Tests: {report['test_summary']['passed']} PASS, "
              f"{report['test_summary']['failed']} FAIL, "
              f"{report['test_summary']['warnings']} WARNING, "
              f"{report['test_summary']['errors']} ERROR")

        if report['critical_issues']:
            print("\n🚨 CRITICAL SECURITY ISSUES:")
            for issue in report['critical_issues']:
                print(f"   ❌ {issue['test_name']}: {issue['description']}")
                for rec in issue['recommendations']:
                    print(f"      💡 {rec}")

        print("\n📋 RECOMMENDATIONS:")
        all_recommendations = []
        for result in self.results:
            all_recommendations.extend(result.recommendations)

        unique_recommendations = list(set(all_recommendations))
        for i, rec in enumerate(unique_recommendations[:5], 1):  # Top 5
            print(f"   {i}. {rec}")

        print("\n" + "=" * 70)

        if report['overall_status'] == "SECURE":
            print("✅ REDIS SECURITY VALIDATION SUCCESSFUL")
            print("✅ Configuration meets security requirements")
            return True
        else:
            print("❌ REDIS SECURITY ISSUES DETECTED")
            print("❌ Immediate action required")
            return False


def main():
    """Main test execution"""
    tester = RedisSecurityTester()

    try:
        tester.run_all_tests()
        success = tester.print_summary()

        # Save detailed report
        report = tester.generate_security_report()
        with open("redis-security-test-report.json", "w") as f:
            json.dump(report, f, indent=2)

        print(f"\n📄 Detailed report saved to: redis-security-test-report.json")

        # Exit with appropriate code
        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n❌ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n🔥 FATAL ERROR: {str(e)}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()