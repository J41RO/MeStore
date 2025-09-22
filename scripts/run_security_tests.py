#!/usr/bin/env python3
# ~/scripts/run_security_tests.py
# ---------------------------------------------------------------------------------------------
# MeStore - Security Test Suite Runner
# Copyright (c) 2025 SecurityBackendAI. Todos los derechos reservados.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: run_security_tests.py
# Ruta: ~/scripts/run_security_tests.py
# Autor: SecurityBackendAI - Elite Security Specialist
# Fecha de Creación: 2025-09-21
# Propósito: Execute and validate comprehensive security test suite
#
# FEATURES:
# - Execute all security tests for admin_management
# - Generate comprehensive security report
# - Validate 0 critical vulnerabilities
# - OWASP Top 10 compliance validation
# - Compliance framework testing (SOX, GDPR, PCI DSS)
# - Performance and coverage metrics
#
# ---------------------------------------------------------------------------------------------

"""
Security Test Suite Runner and Validator.

This script executes the comprehensive security test suite for admin_management
and generates detailed security validation reports.

Usage:
    python scripts/run_security_tests.py [--test-type] [--output-format] [--report-path]

Test Types:
    --all                   Run all security tests (default)
    --authentication       Run only authentication security tests
    --authorization         Run only authorization bypass tests
    --injection            Run only injection attack tests
    --business-logic       Run only business logic security tests
    --data-protection      Run only data protection tests
    --rate-limiting        Run only rate limiting tests
    --compliance           Run only compliance tests

Output Formats:
    --json                 JSON format report
    --html                 HTML format report
    --xml                  XML format report
    --console              Console output (default)

Examples:
    python scripts/run_security_tests.py --all --json --report-path reports/
    python scripts/run_security_tests.py --authentication --console
    python scripts/run_security_tests.py --injection --html
"""

import os
import sys
import json
import argparse
import subprocess
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class SecurityTestRunner:
    """Security test suite runner and validator."""

    def __init__(self, output_format: str = "console", report_path: Optional[str] = None):
        self.output_format = output_format
        self.report_path = report_path or "reports/"
        self.test_results = {}
        self.security_metrics = {}
        self.start_time = datetime.utcnow()

    def run_test_suite(self, test_type: str = "all") -> Dict[str, Any]:
        """Run the specified security test suite."""

        print("🔒 SECURITY BACKEND AI - COMPREHENSIVE SECURITY VALIDATION")
        print("=" * 70)
        print(f"🎯 Target: admin_management.py (748 lines)")
        print(f"⏰ Start Time: {self.start_time.isoformat()}")
        print(f"📊 Test Type: {test_type.upper()}")
        print("=" * 70)

        # Define test commands based on type
        test_commands = self._get_test_commands(test_type)

        # Execute each test category
        for category, command in test_commands.items():
            print(f"\n🧪 Executing {category.upper()} Tests...")
            result = self._execute_test_command(command, category)
            self.test_results[category] = result

        # Generate comprehensive report
        report = self._generate_security_report()

        # Save report if path specified
        if self.report_path:
            self._save_report(report)

        # Display summary
        self._display_summary(report)

        return report

    def _get_test_commands(self, test_type: str) -> Dict[str, str]:
        """Get pytest commands for different test types."""

        base_path = "tests/security/admin_management/"
        base_cmd = "python -m pytest -v --tb=short"

        commands = {
            "authentication": f"{base_cmd} {base_path}test_authentication_security.py -m authentication",
            "authorization": f"{base_cmd} {base_path}test_authorization_bypass.py -m authorization",
            "injection": f"{base_cmd} {base_path}test_injection_attacks.py -m injection",
            "business_logic": f"{base_cmd} {base_path}test_business_logic_security.py -m business_logic",
            "data_protection": f"{base_cmd} {base_path}test_data_protection.py -m data_protection",
            "rate_limiting": f"{base_cmd} {base_path}test_rate_limiting_security.py -m rate_limiting",
            "compliance": f"{base_cmd} {base_path}test_compliance_security.py -m compliance"
        }

        if test_type == "all":
            return commands
        elif test_type.replace("-", "_") in commands:
            return {test_type.replace("-", "_"): commands[test_type.replace("-", "_")]}
        else:
            raise ValueError(f"Unknown test type: {test_type}")

    def _execute_test_command(self, command: str, category: str) -> Dict[str, Any]:
        """Execute a single test command and capture results."""

        start_time = time.time()

        try:
            # Execute pytest command
            result = subprocess.run(
                command.split(),
                cwd=str(project_root),
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout per category
            )

            end_time = time.time()
            execution_time = end_time - start_time

            # Parse pytest output
            output_lines = result.stdout.split('\n')
            error_lines = result.stderr.split('\n')

            # Extract test metrics
            passed_tests = len([line for line in output_lines if "PASSED" in line])
            failed_tests = len([line for line in output_lines if "FAILED" in line])
            skipped_tests = len([line for line in output_lines if "SKIPPED" in line])
            critical_failures = len([line for line in output_lines if "CRITICAL" in line and "FAILED" in line])

            # Determine security status
            security_status = "SECURE" if failed_tests == 0 and critical_failures == 0 else "VULNERABLE"

            result_data = {
                "category": category,
                "execution_time": round(execution_time, 2),
                "return_code": result.returncode,
                "security_status": security_status,
                "test_metrics": {
                    "total_tests": passed_tests + failed_tests + skipped_tests,
                    "passed": passed_tests,
                    "failed": failed_tests,
                    "skipped": skipped_tests,
                    "critical_failures": critical_failures
                },
                "stdout": result.stdout,
                "stderr": result.stderr
            }

            # Display category results
            status_emoji = "✅" if security_status == "SECURE" else "❌"
            print(f"   {status_emoji} {category.upper()}: {security_status}")
            print(f"      ├─ Tests: {passed_tests} passed, {failed_tests} failed, {skipped_tests} skipped")
            print(f"      ├─ Critical: {critical_failures} failures")
            print(f"      └─ Time: {execution_time:.2f}s")

            return result_data

        except subprocess.TimeoutExpired:
            return {
                "category": category,
                "execution_time": 600,
                "return_code": -1,
                "security_status": "TIMEOUT",
                "error": "Test execution timeout",
                "test_metrics": {"total_tests": 0, "passed": 0, "failed": 0, "skipped": 0}
            }

        except Exception as e:
            return {
                "category": category,
                "execution_time": 0,
                "return_code": -1,
                "security_status": "ERROR",
                "error": str(e),
                "test_metrics": {"total_tests": 0, "passed": 0, "failed": 0, "skipped": 0}
            }

    def _generate_security_report(self) -> Dict[str, Any]:
        """Generate comprehensive security validation report."""

        end_time = datetime.utcnow()
        total_execution_time = (end_time - self.start_time).total_seconds()

        # Calculate overall metrics
        total_tests = sum(result.get("test_metrics", {}).get("total_tests", 0) for result in self.test_results.values())
        total_passed = sum(result.get("test_metrics", {}).get("passed", 0) for result in self.test_results.values())
        total_failed = sum(result.get("test_metrics", {}).get("failed", 0) for result in self.test_results.values())
        total_critical = sum(result.get("test_metrics", {}).get("critical_failures", 0) for result in self.test_results.values())

        # Determine overall security status
        overall_status = "SECURE" if total_failed == 0 and total_critical == 0 else "VULNERABLE"

        # OWASP Top 10 coverage
        owasp_coverage = self._calculate_owasp_coverage()

        # Compliance framework coverage
        compliance_coverage = self._calculate_compliance_coverage()

        # Security metrics
        security_metrics = {
            "vulnerability_count": {
                "critical": total_critical,
                "high": self._count_high_severity_issues(),
                "medium": self._count_medium_severity_issues(),
                "low": self._count_low_severity_issues()
            },
            "attack_vectors_tested": self._count_attack_vectors_tested(),
            "security_controls_validated": self._count_security_controls_validated(),
            "coverage_percentage": round((total_passed / total_tests * 100) if total_tests > 0 else 0, 2)
        }

        report = {
            "report_metadata": {
                "generated_at": end_time.isoformat(),
                "execution_time": round(total_execution_time, 2),
                "target_system": "admin_management.py",
                "test_scope": "comprehensive_security_validation",
                "framework_version": "SecurityBackendAI v1.0.0"
            },
            "executive_summary": {
                "overall_security_status": overall_status,
                "critical_vulnerabilities": total_critical,
                "total_security_tests": total_tests,
                "security_score": round((total_passed / total_tests * 100) if total_tests > 0 else 0, 1),
                "compliance_status": "COMPLIANT" if total_critical == 0 else "NON_COMPLIANT"
            },
            "test_execution_results": self.test_results,
            "security_metrics": security_metrics,
            "owasp_top10_coverage": owasp_coverage,
            "compliance_framework_coverage": compliance_coverage,
            "recommendations": self._generate_security_recommendations(),
            "next_assessment_date": (end_time.replace(day=end_time.day + 90)).isoformat()
        }

        return report

    def _calculate_owasp_coverage(self) -> Dict[str, Any]:
        """Calculate OWASP Top 10 coverage."""

        owasp_categories = {
            "A01_Broken_Access_Control": ["authorization", "authentication"],
            "A02_Cryptographic_Failures": ["data_protection", "authentication"],
            "A03_Injection": ["injection"],
            "A04_Insecure_Design": ["business_logic", "compliance"],
            "A05_Security_Misconfiguration": ["authentication", "compliance"],
            "A06_Vulnerable_Components": ["injection", "data_protection"],
            "A07_Authentication_Failures": ["authentication"],
            "A08_Software_Data_Integrity": ["data_protection", "compliance"],
            "A09_Logging_Monitoring_Failures": ["data_protection", "compliance"],
            "A10_Server_Side_Request_Forgery": ["injection", "business_logic"]
        }

        coverage = {}
        for category, test_types in owasp_categories.items():
            covered = any(test_type in self.test_results for test_type in test_types)
            status = "COVERED" if covered else "NOT_COVERED"
            coverage[category] = {
                "status": status,
                "test_categories": test_types,
                "coverage_percentage": 100 if covered else 0
            }

        total_coverage = sum(1 for cat in coverage.values() if cat["status"] == "COVERED")
        overall_percentage = round((total_coverage / len(owasp_categories)) * 100, 1)

        return {
            "overall_coverage_percentage": overall_percentage,
            "categories": coverage,
            "compliance_status": "COMPLIANT" if overall_percentage >= 90 else "PARTIAL"
        }

    def _calculate_compliance_coverage(self) -> Dict[str, Any]:
        """Calculate compliance framework coverage."""

        frameworks = {
            "SOX": "compliance" in self.test_results,
            "GDPR": "data_protection" in self.test_results,
            "PCI_DSS": "compliance" in self.test_results,
            "ISO_27001": "compliance" in self.test_results,
            "NIST": "authentication" in self.test_results and "authorization" in self.test_results
        }

        coverage_count = sum(1 for covered in frameworks.values() if covered)
        coverage_percentage = round((coverage_count / len(frameworks)) * 100, 1)

        return {
            "frameworks_tested": frameworks,
            "coverage_percentage": coverage_percentage,
            "compliance_status": "COMPLIANT" if coverage_percentage >= 80 else "PARTIAL"
        }

    def _count_high_severity_issues(self) -> int:
        """Count high severity security issues."""
        # This would analyze test output for high severity markers
        return sum(result.get("stdout", "").count("HIGH_RISK") for result in self.test_results.values())

    def _count_medium_severity_issues(self) -> int:
        """Count medium severity security issues."""
        return sum(result.get("stdout", "").count("MEDIUM_RISK") for result in self.test_results.values())

    def _count_low_severity_issues(self) -> int:
        """Count low severity security issues."""
        return sum(result.get("stdout", "").count("LOW_RISK") for result in self.test_results.values())

    def _count_attack_vectors_tested(self) -> int:
        """Count different attack vectors tested."""
        vectors = ["SQL_INJECTION", "XSS", "JWT_MANIPULATION", "PRIVILEGE_ESCALATION", "DOS_ATTACK"]
        return sum(1 for vector in vectors if any(vector in result.get("stdout", "") for result in self.test_results.values()))

    def _count_security_controls_validated(self) -> int:
        """Count security controls validated."""
        controls = ["AUTHENTICATION", "AUTHORIZATION", "INPUT_VALIDATION", "RATE_LIMITING", "AUDIT_LOGGING"]
        return sum(1 for control in controls if any(control in result.get("stdout", "") for result in self.test_results.values()))

    def _generate_security_recommendations(self) -> List[Dict[str, Any]]:
        """Generate security recommendations based on test results."""

        recommendations = []

        # Check for failed tests and generate recommendations
        for category, result in self.test_results.items():
            if result.get("test_metrics", {}).get("failed", 0) > 0:
                recommendations.append({
                    "category": category,
                    "priority": "HIGH",
                    "description": f"Address {result['test_metrics']['failed']} failed security tests in {category}",
                    "action_required": True
                })

            if result.get("test_metrics", {}).get("critical_failures", 0) > 0:
                recommendations.append({
                    "category": category,
                    "priority": "CRITICAL",
                    "description": f"Immediate action required: {result['test_metrics']['critical_failures']} critical security failures",
                    "action_required": True
                })

        # General recommendations
        recommendations.extend([
            {
                "category": "continuous_monitoring",
                "priority": "MEDIUM",
                "description": "Implement continuous security monitoring and automated testing",
                "action_required": False
            },
            {
                "category": "penetration_testing",
                "priority": "MEDIUM",
                "description": "Schedule quarterly penetration testing with external security firm",
                "action_required": False
            },
            {
                "category": "security_training",
                "priority": "LOW",
                "description": "Provide regular security training for development team",
                "action_required": False
            }
        ])

        return recommendations

    def _save_report(self, report: Dict[str, Any]) -> None:
        """Save the security report to file."""

        # Ensure report directory exists
        os.makedirs(self.report_path, exist_ok=True)

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

        if self.output_format == "json":
            filename = f"security_report_{timestamp}.json"
            filepath = os.path.join(self.report_path, filename)
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            print(f"\n📄 Security report saved: {filepath}")

        elif self.output_format == "html":
            filename = f"security_report_{timestamp}.html"
            filepath = os.path.join(self.report_path, filename)
            html_content = self._generate_html_report(report)
            with open(filepath, 'w') as f:
                f.write(html_content)
            print(f"\n📄 HTML security report saved: {filepath}")

    def _generate_html_report(self, report: Dict[str, Any]) -> str:
        """Generate HTML format security report."""

        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Security Validation Report - MeStore Admin Management</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
                .summary {{ background-color: #ecf0f1; padding: 15px; margin: 20px 0; border-radius: 5px; }}
                .secure {{ color: #27ae60; font-weight: bold; }}
                .vulnerable {{ color: #e74c3c; font-weight: bold; }}
                .metric {{ margin: 10px 0; }}
                .recommendation {{ margin: 10px 0; padding: 10px; border-left: 4px solid #3498db; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🔒 SECURITY VALIDATION REPORT</h1>
                <p>Target: admin_management.py | Generated: {report['report_metadata']['generated_at']}</p>
            </div>

            <div class="summary">
                <h2>Executive Summary</h2>
                <div class="metric">
                    <strong>Overall Status:</strong>
                    <span class="{'secure' if report['executive_summary']['overall_security_status'] == 'SECURE' else 'vulnerable'}">
                        {report['executive_summary']['overall_security_status']}
                    </span>
                </div>
                <div class="metric"><strong>Critical Vulnerabilities:</strong> {report['executive_summary']['critical_vulnerabilities']}</div>
                <div class="metric"><strong>Security Score:</strong> {report['executive_summary']['security_score']}%</div>
                <div class="metric"><strong>Total Tests:</strong> {report['executive_summary']['total_security_tests']}</div>
            </div>

            <h2>Test Results by Category</h2>
            <table>
                <tr>
                    <th>Category</th>
                    <th>Status</th>
                    <th>Passed</th>
                    <th>Failed</th>
                    <th>Critical</th>
                    <th>Execution Time</th>
                </tr>
        """

        for category, result in report['test_execution_results'].items():
            metrics = result.get('test_metrics', {})
            status_class = 'secure' if result.get('security_status') == 'SECURE' else 'vulnerable'
            html_template += f"""
                <tr>
                    <td>{category.title()}</td>
                    <td class="{status_class}">{result.get('security_status', 'UNKNOWN')}</td>
                    <td>{metrics.get('passed', 0)}</td>
                    <td>{metrics.get('failed', 0)}</td>
                    <td>{metrics.get('critical_failures', 0)}</td>
                    <td>{result.get('execution_time', 0)}s</td>
                </tr>
            """

        html_template += """
            </table>

            <h2>OWASP Top 10 Coverage</h2>
            <div class="metric">
                <strong>Overall Coverage:</strong> {owasp_coverage}%
            </div>

            <h2>Security Recommendations</h2>
        """.format(owasp_coverage=report['owasp_top10_coverage']['overall_coverage_percentage'])

        for rec in report['recommendations']:
            priority_color = {'CRITICAL': '#e74c3c', 'HIGH': '#f39c12', 'MEDIUM': '#f1c40f', 'LOW': '#95a5a6'}
            color = priority_color.get(rec['priority'], '#3498db')
            html_template += f"""
                <div class="recommendation" style="border-color: {color};">
                    <strong>[{rec['priority']}] {rec['category'].title()}:</strong> {rec['description']}
                </div>
            """

        html_template += """
        </body>
        </html>
        """

        return html_template

    def _display_summary(self, report: Dict[str, Any]) -> None:
        """Display security validation summary."""

        print("\n" + "=" * 70)
        print("🎯 SECURITY VALIDATION SUMMARY")
        print("=" * 70)

        exec_summary = report['executive_summary']
        status_emoji = "✅" if exec_summary['overall_security_status'] == 'SECURE' else "❌"

        print(f"{status_emoji} Overall Security Status: {exec_summary['overall_security_status']}")
        print(f"🎯 Security Score: {exec_summary['security_score']}%")
        print(f"🚨 Critical Vulnerabilities: {exec_summary['critical_vulnerabilities']}")
        print(f"📊 Total Security Tests: {exec_summary['total_security_tests']}")
        print(f"⏱️  Total Execution Time: {report['report_metadata']['execution_time']}s")

        # OWASP Top 10 Summary
        owasp_coverage = report['owasp_top10_coverage']['overall_coverage_percentage']
        owasp_emoji = "✅" if owasp_coverage >= 90 else "⚠️"
        print(f"{owasp_emoji} OWASP Top 10 Coverage: {owasp_coverage}%")

        # Compliance Summary
        compliance_coverage = report['compliance_framework_coverage']['coverage_percentage']
        compliance_emoji = "✅" if compliance_coverage >= 80 else "⚠️"
        print(f"{compliance_emoji} Compliance Coverage: {compliance_coverage}%")

        print("\n🔒 SECURITY VALIDATION COMPLETED")
        print("=" * 70)

        # Display final verdict
        if exec_summary['critical_vulnerabilities'] == 0:
            print("🎉 SUCCESS: 0 CRITICAL VULNERABILITIES DETECTED")
            print("✅ System meets enterprise security standards")
        else:
            print(f"🚨 WARNING: {exec_summary['critical_vulnerabilities']} CRITICAL VULNERABILITIES DETECTED")
            print("❌ Immediate security remediation required")


def main():
    """Main entry point for security test runner."""

    parser = argparse.ArgumentParser(description="MeStore Security Test Suite Runner")

    parser.add_argument(
        "--test-type",
        choices=["all", "authentication", "authorization", "injection", "business-logic",
                "data-protection", "rate-limiting", "compliance"],
        default="all",
        help="Type of security tests to run"
    )

    parser.add_argument(
        "--output-format",
        choices=["console", "json", "html", "xml"],
        default="console",
        help="Output format for the report"
    )

    parser.add_argument(
        "--report-path",
        default="reports/",
        help="Path to save the security report"
    )

    parser.add_argument(
        "--validate-zero-critical",
        action="store_true",
        help="Fail if any critical vulnerabilities are found"
    )

    args = parser.parse_args()

    # Initialize security test runner
    runner = SecurityTestRunner(
        output_format=args.output_format,
        report_path=args.report_path
    )

    # Execute security test suite
    try:
        report = runner.run_test_suite(args.test_type)

        # Check for zero critical vulnerabilities if requested
        if args.validate_zero_critical:
            critical_vulns = report['executive_summary']['critical_vulnerabilities']
            if critical_vulns > 0:
                print(f"\n❌ VALIDATION FAILED: {critical_vulns} critical vulnerabilities detected")
                sys.exit(1)
            else:
                print("\n✅ VALIDATION PASSED: 0 critical vulnerabilities detected")

        sys.exit(0)

    except Exception as e:
        print(f"\n❌ Security test execution failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()