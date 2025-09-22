#!/usr/bin/env python3
"""
Comprehensive Integration Test Runner for MeStore API Standardization.
Executes complete integration test suite and generates compliance reports.

File: run_integration_tests.py
Author: Integration Testing AI
Date: 2025-09-17
Purpose: Main entry point for running API standardization integration tests
"""

import sys
import os
import asyncio
import argparse
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import test modules
try:
    import pytest
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
    from httpx import AsyncClient, ASGITransport

    # Import the main test classes
    from tests.integration.endpoints.test_compliance_metrics import ComplianceMetricsAggregator
    from app.main import app
    from app.database import Base
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Please ensure all dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)


class IntegrationTestRunner:
    """
    Main integration test runner for API standardization validation.
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._load_default_config()
        self.test_engine = None
        self.test_session = None
        self.async_client = None
        self.results = {}

    def _load_default_config(self) -> Dict[str, Any]:
        """Load default test configuration."""
        return {
            "database_url": "sqlite+aiosqlite:///:memory:",
            "test_mode": True,
            "verbose": True,
            "generate_report": True,
            "report_format": "json",
            "output_file": "compliance_report.json",
            "coverage": False,
            "parallel": False,
            "timeout": 300  # 5 minutes
        }

    async def setup_test_environment(self):
        """Setup test environment with database and client."""
        print("🔧 Setting up test environment...")

        # Setup test database
        self.test_engine = create_async_engine(
            self.config["database_url"],
            echo=False,
            pool_pre_ping=True
        )

        # Create async session factory
        async_session_factory = async_sessionmaker(
            bind=self.test_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

        # Create tables
        async with self.test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        # Create session
        self.test_session = async_session_factory()

        # Setup async client
        transport = ASGITransport(app=app)
        self.async_client = AsyncClient(
            transport=transport,
            base_url="http://testserver",
            headers={"User-Agent": "IntegrationTestRunner/1.0"}
        )

        print("✅ Test environment setup completed")

    async def teardown_test_environment(self):
        """Teardown test environment."""
        print("🧹 Cleaning up test environment...")

        if self.async_client:
            await self.async_client.aclose()

        if self.test_session:
            await self.test_session.close()

        if self.test_engine:
            await self.test_engine.dispose()

        print("✅ Test environment cleanup completed")

    async def run_integration_tests(self) -> Dict[str, Any]:
        """Run comprehensive integration tests."""
        print("🚀 Starting Comprehensive Integration Test Suite...")
        print("="*80)

        try:
            # Setup environment
            await self.setup_test_environment()

            # Initialize compliance aggregator
            aggregator = ComplianceMetricsAggregator(self.async_client, self.test_session)

            # Run comprehensive compliance assessment
            compliance_report = await aggregator.run_comprehensive_compliance_assessment()

            # Store results
            self.results = compliance_report

            print("="*80)
            print("✅ Integration test suite completed successfully!")

            return compliance_report

        except Exception as e:
            print(f"❌ Integration test suite failed: {str(e)}")
            raise

        finally:
            # Always cleanup
            await self.teardown_test_environment()

    def generate_report(self, report_data: Dict[str, Any], format_type: str = "json") -> str:
        """Generate test report in specified format."""
        if format_type == "json":
            return self._generate_json_report(report_data)
        elif format_type == "html":
            return self._generate_html_report(report_data)
        elif format_type == "markdown":
            return self._generate_markdown_report(report_data)
        else:
            raise ValueError(f"Unsupported report format: {format_type}")

    def _generate_json_report(self, report_data: Dict[str, Any]) -> str:
        """Generate JSON format report."""
        output_file = self.config.get("output_file", "compliance_report.json")

        with open(output_file, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)

        return output_file

    def _generate_html_report(self, report_data: Dict[str, Any]) -> str:
        """Generate HTML format report."""
        output_file = self.config.get("output_file", "compliance_report.html").replace(".json", ".html")

        compliance = report_data["compliance_assessment"]["overall_compliance"]
        areas = report_data["compliance_assessment"]["compliance_by_area"]
        recommendations = report_data["compliance_assessment"]["priority_recommendations"]

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>API Standardization Compliance Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .compliance-score {{ font-size: 48px; font-weight: bold; color: {'green' if compliance['percentage'] >= 80 else 'orange' if compliance['percentage'] >= 60 else 'red'}; }}
        .area {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .recommendations {{ background: #f5f5f5; padding: 20px; border-radius: 5px; }}
        .metric {{ display: inline-block; margin: 10px; padding: 15px; background: #f9f9f9; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🏆 API Standardization Compliance Report</h1>
        <div class="compliance-score">{compliance['percentage']}%</div>
        <p>Overall Compliance Level: <strong>{compliance['level']}</strong></p>
        <p>Status: {compliance['status']}</p>
    </div>

    <h2>📊 Compliance by Area</h2>
"""

        for area_name, area_data in areas.items():
            html_content += f"""
    <div class="area">
        <h3>{area_data['status']} {area_name.replace('_', ' ').title()}</h3>
        <p>Compliance: <strong>{area_data['percentage']}%</strong> ({area_data['score']})</p>
        <p>Level: <strong>{area_data['level']}</strong></p>
    </div>
"""

        html_content += """
    <h2>🎯 Priority Recommendations</h2>
    <div class="recommendations">
        <ol>
"""

        for recommendation in recommendations[:10]:
            html_content += f"            <li>{recommendation}</li>\n"

        html_content += """
        </ol>
    </div>

    <h2>📈 Test Execution Summary</h2>
    <div class="metric">
        <strong>Total Tests:</strong> {total_tests}
    </div>
    <div class="metric">
        <strong>Passed:</strong> {passed_tests}
    </div>
    <div class="metric">
        <strong>Failed:</strong> {failed_tests}
    </div>
    <div class="metric">
        <strong>Success Rate:</strong> {success_rate}%
    </div>

    <footer style="margin-top: 50px; text-align: center; color: #666;">
        <p>Generated on {timestamp}</p>
        <p>Integration Testing AI - API Standardization Validation Suite</p>
    </footer>
</body>
</html>
""".format(
            total_tests=report_data["compliance_assessment"]["execution_summary"]["total_tests"],
            passed_tests=report_data["compliance_assessment"]["execution_summary"]["passed_tests"],
            failed_tests=report_data["compliance_assessment"]["execution_summary"]["failed_tests"],
            success_rate=report_data["compliance_assessment"]["execution_summary"]["success_rate"],
            timestamp=report_data["compliance_assessment"]["assessment_timestamp"]
        )

        with open(output_file, 'w') as f:
            f.write(html_content)

        return output_file

    def _generate_markdown_report(self, report_data: Dict[str, Any]) -> str:
        """Generate Markdown format report."""
        output_file = self.config.get("output_file", "compliance_report.md").replace(".json", ".md")

        compliance = report_data["compliance_assessment"]["overall_compliance"]
        areas = report_data["compliance_assessment"]["compliance_by_area"]
        recommendations = report_data["compliance_assessment"]["priority_recommendations"]
        execution = report_data["compliance_assessment"]["execution_summary"]

        markdown_content = f"""# 🏆 API Standardization Compliance Report

## Overall Compliance: {compliance['percentage']}%

**Level:** {compliance['level']}
**Status:** {compliance['status']}
**Assessment Date:** {report_data["compliance_assessment"]["assessment_timestamp"]}

## 📊 Compliance by Area

| Area | Score | Percentage | Level | Status |
|------|-------|------------|-------|--------|
"""

        for area_name, area_data in areas.items():
            markdown_content += f"| {area_name.replace('_', ' ').title()} | {area_data['score']} | {area_data['percentage']}% | {area_data['level']} | {area_data['status']} |\n"

        markdown_content += f"""

## 📈 Test Execution Summary

- **Total Tests:** {execution['total_tests']}
- **Passed Tests:** {execution['passed_tests']}
- **Failed Tests:** {execution['failed_tests']}
- **Success Rate:** {execution['success_rate']}%
- **Execution Time:** {execution['total_execution_time']} seconds

## 🎯 Priority Recommendations

"""

        for i, recommendation in enumerate(recommendations[:15], 1):
            markdown_content += f"{i}. {recommendation}\n"

        markdown_content += f"""

## 🚀 Next Steps

"""

        for i, step in enumerate(report_data["compliance_assessment"]["next_steps"][:10], 1):
            markdown_content += f"{i}. {step}\n"

        markdown_content += """

---

*Generated by Integration Testing AI - API Standardization Validation Suite*
"""

        with open(output_file, 'w') as f:
            f.write(markdown_content)

        return output_file

    def print_summary(self, report_data: Dict[str, Any]):
        """Print test summary to console."""
        compliance = report_data["compliance_assessment"]["overall_compliance"]
        execution = report_data["compliance_assessment"]["execution_summary"]

        print("\n" + "="*80)
        print("📋 INTEGRATION TEST SUMMARY")
        print("="*80)
        print(f"🏆 Overall Compliance: {compliance['percentage']}% ({compliance['level']})")
        print(f"📊 Status: {compliance['status']}")
        print(f"🧪 Total Tests: {execution['total_tests']}")
        print(f"✅ Passed: {execution['passed_tests']}")
        print(f"❌ Failed: {execution['failed_tests']}")
        print(f"📈 Success Rate: {execution['success_rate']}%")
        print(f"⏱️ Execution Time: {execution['total_execution_time']} seconds")
        print("="*80)


async def main():
    """Main entry point for integration test runner."""
    parser = argparse.ArgumentParser(description="MeStore API Standardization Integration Test Runner")
    parser.add_argument("--format", choices=["json", "html", "markdown"], default="json",
                       help="Report format (default: json)")
    parser.add_argument("--output", default="compliance_report",
                       help="Output file name (without extension)")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")
    parser.add_argument("--quick", action="store_true",
                       help="Run quick tests only")
    parser.add_argument("--area", choices=[
        "api_standardization", "contract_validation", "auth_flows",
        "crud_operations", "error_handling", "user_journeys"
    ], help="Run tests for specific area only")

    args = parser.parse_args()

    # Configure test runner
    config = {
        "verbose": args.verbose,
        "report_format": args.format,
        "output_file": f"{args.output}.{args.format}",
        "quick_mode": args.quick,
        "specific_area": args.area
    }

    runner = IntegrationTestRunner(config)

    try:
        # Run integration tests
        report_data = await runner.run_integration_tests()

        # Generate report
        if config["report_format"]:
            report_file = runner.generate_report(report_data, config["report_format"])
            print(f"📄 Report generated: {report_file}")

        # Print summary
        runner.print_summary(report_data)

        # Return appropriate exit code
        overall_compliance = report_data["compliance_assessment"]["overall_compliance"]["percentage"]
        if overall_compliance >= 80:
            print("🎉 Integration tests passed with excellent compliance!")
            return 0
        elif overall_compliance >= 60:
            print("⚠️ Integration tests passed with acceptable compliance")
            return 0
        else:
            print("❌ Integration tests failed - compliance below threshold")
            return 1

    except Exception as e:
        print(f"❌ Integration test runner failed: {str(e)}")
        return 1


def run_with_pytest():
    """Run integration tests using pytest."""
    pytest_args = [
        "tests/integration/endpoints/test_compliance_metrics.py::TestComplianceMetrics::test_comprehensive_api_compliance",
        "-v",
        "--tb=short",
        "--disable-warnings"
    ]

    print("🧪 Running integration tests via pytest...")
    exit_code = pytest.main(pytest_args)
    return exit_code


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--pytest":
        # Run via pytest
        exit_code = run_with_pytest()
        sys.exit(exit_code)
    else:
        # Run via async main
        exit_code = asyncio.run(main())
        sys.exit(exit_code)