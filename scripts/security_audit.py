#!/usr/bin/env python3
# ~/scripts/security_audit.py
# ---------------------------------------------------------------------------------------------
# MeStore - Security Audit Script
# Copyright (c) 2025 Jairo. Todos los derechos reservados.
# Licensed under the proprietary license detailed in a LICENSE file in the root of this project.
# ---------------------------------------------------------------------------------------------
#
# Nombre del Archivo: security_audit.py
# Ruta: ~/scripts/security_audit.py
# Autor: Security Backend AI
# Fecha de Creación: 2025-09-17
# Última Actualización: 2025-09-17
# Versión: 1.0.0
# Propósito: Comprehensive security audit script for MeStore JWT secret management
#            Validates security implementation and generates compliance reports
#
# Usage:
#   python scripts/security_audit.py [--format json|html|console] [--output file.ext]
#
# ---------------------------------------------------------------------------------------------

"""
MeStore Security Audit Script

This script performs comprehensive security auditing of the JWT secret management
system and generates detailed reports for compliance and security validation.

Features:
- JWT secret security validation
- Token blacklisting functionality testing
- Colombian compliance verification
- Security configuration assessment
- Vulnerability identification
- Compliance reporting
"""

import asyncio
import argparse
import json
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from app.services.security_validation_service import run_security_audit
    from app.core.secret_manager import get_secret_security_report
    from app.core.config import settings
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    print("Make sure you're running this script from the project root directory.")
    sys.exit(1)


class SecurityAuditReporter:
    """Generates security audit reports in various formats."""

    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def generate_console_report(self, audit_report: Dict[str, Any]) -> str:
        """Generate console-formatted audit report."""
        report = []
        report.append("=" * 80)
        report.append("🔒 MESTORE SECURITY AUDIT REPORT")
        report.append("=" * 80)
        report.append(f"📅 Timestamp: {audit_report['timestamp']}")
        report.append(f"🌍 Environment: {audit_report['environment']}")
        report.append(f"🔐 Security Level: {audit_report['security_level']}")
        report.append(f"📊 Overall Score: {audit_report['overall_score']}/100")
        report.append("")

        # Summary
        summary = audit_report['summary']
        report.append("📋 AUDIT SUMMARY")
        report.append("-" * 40)
        report.append(f"Total Tests: {summary['total_tests']}")
        report.append(f"Passed Tests: {summary['passed_tests']}")
        report.append(f"Failed Tests: {summary['failed_tests']}")
        report.append(f"Pass Rate: {summary['pass_rate']:.1f}%")
        report.append(f"Critical Issues: {summary['critical_issues']}")
        report.append(f"High Issues: {summary['high_issues']}")
        report.append("")

        # Test Results
        report.append("🧪 TEST RESULTS")
        report.append("-" * 40)
        for test in audit_report['test_results']:
            status = "✅ PASS" if test['passed'] else "❌ FAIL"
            report.append(f"{status} {test['test_name']} - Score: {test['score']}/100")
            if not test['passed'] and test['recommendations']:
                for rec in test['recommendations'][:2]:  # Show top 2 recommendations
                    report.append(f"   💡 {rec}")
        report.append("")

        # Compliance Status
        report.append("🏛️ COMPLIANCE STATUS")
        report.append("-" * 40)
        for compliance, status in audit_report['compliance_status'].items():
            symbol = "✅" if status else "❌"
            report.append(f"{symbol} {compliance.replace('_', ' ').title()}")
        report.append("")

        # Vulnerabilities
        if audit_report['vulnerabilities']:
            report.append("⚠️ IDENTIFIED VULNERABILITIES")
            report.append("-" * 40)
            for vuln in audit_report['vulnerabilities']:
                report.append(f"🚨 {vuln['severity'].upper()}: {vuln['description']}")
                report.append(f"   Component: {vuln['affected_component']}")
                report.append(f"   Risk Score: {vuln['risk_score']}/100")
        else:
            report.append("✅ NO CRITICAL VULNERABILITIES IDENTIFIED")
        report.append("")

        # Recommendations
        if audit_report['recommendations']:
            report.append("💡 SECURITY RECOMMENDATIONS")
            report.append("-" * 40)
            for i, rec in enumerate(audit_report['recommendations'][:5], 1):
                report.append(f"{i}. {rec}")
        report.append("")

        report.append("=" * 80)
        report.append("🔒 End of Security Audit Report")
        report.append("=" * 80)

        return "\n".join(report)

    def generate_json_report(self, audit_report: Dict[str, Any]) -> str:
        """Generate JSON-formatted audit report."""
        return json.dumps(audit_report, indent=2, default=str)

    def generate_html_report(self, audit_report: Dict[str, Any]) -> str:
        """Generate HTML-formatted audit report."""
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MeStore Security Audit Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; margin-bottom: 30px; }}
        .score-badge {{ display: inline-block; padding: 10px 20px; border-radius: 25px; font-weight: bold; margin: 10px 5px; }}
        .score-excellent {{ background: #4CAF50; color: white; }}
        .score-good {{ background: #8BC34A; color: white; }}
        .score-fair {{ background: #FF9800; color: white; }}
        .score-poor {{ background: #FF5722; color: white; }}
        .score-critical {{ background: #F44336; color: white; }}
        .test-result {{ margin: 15px 0; padding: 15px; border-left: 4px solid #ddd; border-radius: 4px; }}
        .test-pass {{ border-left-color: #4CAF50; background: #f8fff8; }}
        .test-fail {{ border-left-color: #F44336; background: #fff8f8; }}
        .vulnerability {{ background: #ffebee; border: 1px solid #ffcdd2; padding: 15px; margin: 10px 0; border-radius: 4px; }}
        .compliance-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 15px; margin: 20px 0; }}
        .compliance-item {{ padding: 15px; border-radius: 8px; text-align: center; }}
        .compliance-pass {{ background: #e8f5e8; color: #2e7d32; }}
        .compliance-fail {{ background: #ffebee; color: #c62828; }}
        .summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
        .summary-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }}
        .recommendations {{ background: #e3f2fd; padding: 20px; border-radius: 8px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔒 MeStore Security Audit Report</h1>
            <p>Comprehensive JWT Secret Management Security Assessment</p>
            <p><strong>Environment:</strong> {audit_report['environment']} | <strong>Timestamp:</strong> {audit_report['timestamp']}</p>
        </div>

        <div class="score-badge score-{audit_report['security_level'].lower()}">
            Overall Security Score: {audit_report['overall_score']}/100 - {audit_report['security_level']}
        </div>

        <h2>📋 Audit Summary</h2>
        <div class="summary-grid">
            <div class="summary-card">
                <h3>{audit_report['summary']['total_tests']}</h3>
                <p>Total Tests</p>
            </div>
            <div class="summary-card">
                <h3>{audit_report['summary']['passed_tests']}</h3>
                <p>Passed Tests</p>
            </div>
            <div class="summary-card">
                <h3>{audit_report['summary']['pass_rate']:.1f}%</h3>
                <p>Pass Rate</p>
            </div>
            <div class="summary-card">
                <h3>{audit_report['summary']['critical_issues']}</h3>
                <p>Critical Issues</p>
            </div>
        </div>

        <h2>🧪 Test Results</h2>
        """

        for test in audit_report['test_results']:
            status_class = "test-pass" if test['passed'] else "test-fail"
            status_icon = "✅" if test['passed'] else "❌"
            html += f"""
        <div class="test-result {status_class}">
            <h3>{status_icon} {test['test_name']} - Score: {test['score']}/100</h3>
            <p><strong>Severity:</strong> {test['severity']}</p>
            <p>{test['message']}</p>
            """
            if test['recommendations']:
                html += "<strong>Recommendations:</strong><ul>"
                for rec in test['recommendations'][:3]:
                    html += f"<li>{rec}</li>"
                html += "</ul>"
            html += "</div>"

        html += """
        <h2>🏛️ Compliance Status</h2>
        <div class="compliance-grid">
        """

        for compliance, status in audit_report['compliance_status'].items():
            status_class = "compliance-pass" if status else "compliance-fail"
            status_icon = "✅" if status else "❌"
            html += f"""
            <div class="compliance-item {status_class}">
                <h3>{status_icon}</h3>
                <p>{compliance.replace('_', ' ').title()}</p>
            </div>
            """

        html += "</div>"

        if audit_report['vulnerabilities']:
            html += "<h2>⚠️ Identified Vulnerabilities</h2>"
            for vuln in audit_report['vulnerabilities']:
                html += f"""
            <div class="vulnerability">
                <h3>🚨 {vuln['severity'].upper()}: {vuln['description']}</h3>
                <p><strong>Component:</strong> {vuln['affected_component']}</p>
                <p><strong>Risk Score:</strong> {vuln['risk_score']}/100</p>
                <strong>Remediation:</strong>
                <ul>
                """
                for rem in vuln['remediation']:
                    html += f"<li>{rem}</li>"
                html += "</ul></div>"

        if audit_report['recommendations']:
            html += """
        <div class="recommendations">
            <h2>💡 Security Recommendations</h2>
            <ol>
            """
            for rec in audit_report['recommendations'][:10]:
                html += f"<li>{rec}</li>"
            html += """
            </ol>
        </div>
        """

        html += """
        <footer style="text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #666;">
            <p>Generated by MeStore Security Audit System | Security Backend AI</p>
        </footer>
    </div>
</body>
</html>
        """

        return html


async def main():
    """Main security audit function."""
    parser = argparse.ArgumentParser(description="MeStore Security Audit")
    parser.add_argument(
        "--format",
        choices=["console", "json", "html"],
        default="console",
        help="Output format (default: console)"
    )
    parser.add_argument(
        "--output",
        help="Output file path (default: stdout or auto-generated filename)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )

    args = parser.parse_args()

    print("🔒 Starting MeStore Security Audit...")
    print(f"📊 Environment: {settings.ENVIRONMENT}")
    print(f"📝 Format: {args.format}")

    try:
        # Run comprehensive security audit
        print("🔍 Running comprehensive security tests...")
        audit_report = await run_security_audit()

        # Convert to dictionary for reporting
        audit_dict = {
            "audit_id": audit_report.audit_id,
            "timestamp": audit_report.timestamp.isoformat(),
            "environment": audit_report.environment,
            "overall_score": audit_report.overall_score,
            "security_level": audit_report.security_level,
            "test_results": [
                {
                    "test_type": result.test_type.value,
                    "test_name": result.test_name,
                    "passed": result.passed,
                    "severity": result.severity.value,
                    "score": result.score,
                    "message": result.message,
                    "details": result.details,
                    "recommendations": result.recommendations,
                    "compliance_notes": result.compliance_notes
                }
                for result in audit_report.test_results
            ],
            "summary": audit_report.summary,
            "recommendations": audit_report.recommendations,
            "compliance_status": audit_report.compliance_status,
            "vulnerabilities": audit_report.vulnerabilities
        }

        # Generate report
        reporter = SecurityAuditReporter()

        if args.format == "console":
            output = reporter.generate_console_report(audit_dict)
        elif args.format == "json":
            output = reporter.generate_json_report(audit_dict)
        elif args.format == "html":
            output = reporter.generate_html_report(audit_dict)

        # Output to file or stdout
        if args.output:
            output_path = Path(args.output)
        else:
            if args.format == "console":
                print(output)
                return
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = Path(f"security_audit_{timestamp}.{args.format}")

        output_path.write_text(output, encoding="utf-8")
        print(f"✅ Security audit report saved to: {output_path}")

        # Print summary to console
        if args.format != "console":
            print(f"\n📊 Security Summary:")
            print(f"   Overall Score: {audit_dict['overall_score']}/100")
            print(f"   Security Level: {audit_dict['security_level']}")
            print(f"   Tests Passed: {audit_dict['summary']['passed_tests']}/{audit_dict['summary']['total_tests']}")
            print(f"   Critical Issues: {audit_dict['summary']['critical_issues']}")

        # Exit with appropriate code
        if audit_dict['overall_score'] < 70:
            print("\n⚠️ WARNING: Security score below acceptable threshold (70)")
            sys.exit(1)
        elif audit_dict['summary']['critical_issues'] > 0:
            print("\n⚠️ WARNING: Critical security issues identified")
            sys.exit(1)
        else:
            print("\n✅ Security audit completed successfully")
            sys.exit(0)

    except Exception as e:
        print(f"❌ Security audit failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())