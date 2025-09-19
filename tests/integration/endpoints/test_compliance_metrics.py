"""
API Standardization Compliance Metrics and Reporting.
Comprehensive testing framework that aggregates all integration test results and generates compliance reports.

File: tests/integration/endpoints/test_compliance_metrics.py
Author: Integration Testing AI
Date: 2025-09-17
Purpose: Generate comprehensive compliance metrics and standardization reports
"""

import pytest
import json
import time
from typing import Dict, List, Any, Optional
from httpx import AsyncClient
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession
from dataclasses import dataclass
from enum import Enum

from app.models.user import User, UserType
from app.core.security import create_access_token

# Import all test modules for comprehensive testing
from .test_api_standardization import APIStandardizationTester
from .test_contract_validation import APIContractValidator
from .test_auth_flows import AuthenticationFlowTester
from .test_crud_operations import CRUDOperationsTester
from .test_error_handling import ErrorHandlingValidator
from ..workflows.test_user_journeys import UserJourneyTester

# Test markers
pytestmark = [
    pytest.mark.integration,
    pytest.mark.compliance,
    pytest.mark.metrics,
    pytest.mark.critical
]


class ComplianceLevel(Enum):
    """Compliance level enumeration."""
    EXCELLENT = "EXCELLENT"
    GOOD = "GOOD"
    ACCEPTABLE = "ACCEPTABLE"
    NEEDS_IMPROVEMENT = "NEEDS_IMPROVEMENT"
    CRITICAL = "CRITICAL"


@dataclass
class ComplianceMetric:
    """Individual compliance metric."""
    name: str
    description: str
    score: float
    max_score: float
    percentage: float
    level: ComplianceLevel
    details: Dict[str, Any]
    recommendations: List[str]


class ComplianceMetricsAggregator:
    """
    Comprehensive compliance metrics aggregator.
    Runs all integration tests and generates unified compliance reports.
    """

    def __init__(self, client: AsyncClient, session: AsyncSession):
        self.client = client
        self.session = session
        self.metrics = {}
        self.detailed_results = {}
        self.execution_time = 0
        self.test_summary = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "skipped_tests": 0
        }

    async def run_comprehensive_compliance_assessment(self) -> Dict[str, Any]:
        """Run comprehensive compliance assessment across all areas."""

        start_time = time.time()

        print("🚀 Starting Comprehensive API Standardization Compliance Assessment...")

        # 1. API Endpoint Standardization
        print("📊 Testing API Endpoint Standardization...")
        standardization_results = await self._assess_api_standardization()

        # 2. Contract Validation
        print("📋 Testing API Contract Validation...")
        contract_results = await self._assess_contract_validation()

        # 3. Authentication Flows
        print("🔐 Testing Authentication Flows...")
        auth_results = await self._assess_authentication_flows()

        # 4. CRUD Operations
        print("🔄 Testing CRUD Operations...")
        crud_results = await self._assess_crud_operations()

        # 5. Error Handling
        print("⚠️ Testing Error Handling...")
        error_handling_results = await self._assess_error_handling()

        # 6. User Journeys
        print("👤 Testing User Journeys...")
        journey_results = await self._assess_user_journeys()

        self.execution_time = time.time() - start_time

        # Generate comprehensive report
        compliance_report = self._generate_comprehensive_report()

        print(f"✅ Compliance Assessment Completed in {self.execution_time:.2f} seconds")

        return compliance_report

    async def _assess_api_standardization(self) -> ComplianceMetric:
        """Assess API endpoint standardization compliance."""
        try:
            tester = APIStandardizationTester(self.client, self.session)
            results = await tester.run_comprehensive_tests()

            compliance_data = results.get("compliance_summary", {})
            total_tests = compliance_data.get("total_tests", 0)
            passed_tests = compliance_data.get("passed_tests", 0)
            percentage = compliance_data.get("compliance_percentage", 0)

            self.test_summary["total_tests"] += total_tests
            self.test_summary["passed_tests"] += passed_tests
            self.test_summary["failed_tests"] += (total_tests - passed_tests)

            level = self._determine_compliance_level(percentage)

            metric = ComplianceMetric(
                name="API Endpoint Standardization",
                description="Validates endpoint consistency, URL patterns, and standardization",
                score=passed_tests,
                max_score=total_tests,
                percentage=percentage,
                level=level,
                details=results.get("detailed_results", {}),
                recommendations=results.get("recommendations", [])
            )

            self.metrics["api_standardization"] = metric
            self.detailed_results["api_standardization"] = results

            return metric

        except Exception as e:
            print(f"❌ Error in API standardization assessment: {str(e)}")
            return self._create_error_metric("API Endpoint Standardization", str(e))

    async def _assess_contract_validation(self) -> ComplianceMetric:
        """Assess API contract validation compliance."""
        try:
            validator = APIContractValidator(self.client, self.session)
            results = await validator.validate_all_contracts()

            compliance_data = results.get("contract_compliance", {})
            total_validations = compliance_data.get("total_validations", 0)
            passed_validations = compliance_data.get("passed_validations", 0)
            percentage = compliance_data.get("compliance_percentage", 0)

            self.test_summary["total_tests"] += total_validations
            self.test_summary["passed_tests"] += passed_validations
            self.test_summary["failed_tests"] += (total_validations - passed_validations)

            level = self._determine_compliance_level(percentage)

            metric = ComplianceMetric(
                name="API Contract Validation",
                description="Validates API schemas, response formats, and data contracts",
                score=passed_validations,
                max_score=total_validations,
                percentage=percentage,
                level=level,
                details=results.get("detailed_results", {}),
                recommendations=results.get("recommendations", [])
            )

            self.metrics["contract_validation"] = metric
            self.detailed_results["contract_validation"] = results

            return metric

        except Exception as e:
            print(f"❌ Error in contract validation assessment: {str(e)}")
            return self._create_error_metric("API Contract Validation", str(e))

    async def _assess_authentication_flows(self) -> ComplianceMetric:
        """Assess authentication flows compliance."""
        try:
            tester = AuthenticationFlowTester(self.client, self.session)
            results = await tester.run_comprehensive_auth_tests()

            compliance_data = results.get("auth_compliance", {})
            total_tests = compliance_data.get("total_tests", 0)
            passed_tests = compliance_data.get("passed_tests", 0)
            percentage = compliance_data.get("compliance_percentage", 0)

            self.test_summary["total_tests"] += total_tests
            self.test_summary["passed_tests"] += passed_tests
            self.test_summary["failed_tests"] += (total_tests - passed_tests)

            level = self._determine_compliance_level(percentage)

            metric = ComplianceMetric(
                name="Authentication Flows",
                description="Validates authentication security, token management, and authorization",
                score=passed_tests,
                max_score=total_tests,
                percentage=percentage,
                level=level,
                details=results.get("detailed_results", {}),
                recommendations=results.get("security_recommendations", [])
            )

            self.metrics["authentication_flows"] = metric
            self.detailed_results["authentication_flows"] = results

            return metric

        except Exception as e:
            print(f"❌ Error in authentication flows assessment: {str(e)}")
            return self._create_error_metric("Authentication Flows", str(e))

    async def _assess_crud_operations(self) -> ComplianceMetric:
        """Assess CRUD operations compliance."""
        try:
            tester = CRUDOperationsTester(self.client, self.session)
            results = await tester.run_comprehensive_crud_tests()

            compliance_data = results.get("crud_compliance", {})
            total_tests = compliance_data.get("total_tests", 0)
            passed_tests = compliance_data.get("passed_tests", 0)
            percentage = compliance_data.get("compliance_percentage", 0)

            self.test_summary["total_tests"] += total_tests
            self.test_summary["passed_tests"] += passed_tests
            self.test_summary["failed_tests"] += (total_tests - passed_tests)

            level = self._determine_compliance_level(percentage)

            metric = ComplianceMetric(
                name="CRUD Operations",
                description="Validates Create, Read, Update, Delete operations and data integrity",
                score=passed_tests,
                max_score=total_tests,
                percentage=percentage,
                level=level,
                details=results.get("detailed_results", {}),
                recommendations=results.get("recommendations", [])
            )

            self.metrics["crud_operations"] = metric
            self.detailed_results["crud_operations"] = results

            return metric

        except Exception as e:
            print(f"❌ Error in CRUD operations assessment: {str(e)}")
            return self._create_error_metric("CRUD Operations", str(e))

    async def _assess_error_handling(self) -> ComplianceMetric:
        """Assess error handling compliance."""
        try:
            validator = ErrorHandlingValidator(self.client, self.session)
            results = await validator.validate_all_error_handling()

            compliance_data = results.get("error_handling_compliance", {})
            total_validations = compliance_data.get("total_validations", 0)
            passed_validations = compliance_data.get("passed_validations", 0)
            percentage = compliance_data.get("compliance_percentage", 0)

            self.test_summary["total_tests"] += total_validations
            self.test_summary["passed_tests"] += passed_validations
            self.test_summary["failed_tests"] += (total_validations - passed_validations)

            level = self._determine_compliance_level(percentage)

            metric = ComplianceMetric(
                name="Error Handling",
                description="Validates error response consistency, status codes, and error message formatting",
                score=passed_validations,
                max_score=total_validations,
                percentage=percentage,
                level=level,
                details=results.get("detailed_results", {}),
                recommendations=results.get("recommendations", [])
            )

            self.metrics["error_handling"] = metric
            self.detailed_results["error_handling"] = results

            return metric

        except Exception as e:
            print(f"❌ Error in error handling assessment: {str(e)}")
            return self._create_error_metric("Error Handling", str(e))

    async def _assess_user_journeys(self) -> ComplianceMetric:
        """Assess user journeys compliance."""
        try:
            tester = UserJourneyTester(self.client, self.session)
            results = await tester.run_comprehensive_journey_tests()

            compliance_data = results.get("journey_compliance", {})
            total_steps = compliance_data.get("total_journey_steps", 0)
            successful_steps = compliance_data.get("successful_steps", 0)
            success_rate = compliance_data.get("success_rate", 0)

            self.test_summary["total_tests"] += total_steps
            self.test_summary["passed_tests"] += successful_steps
            self.test_summary["failed_tests"] += (total_steps - successful_steps)

            level = self._determine_compliance_level(success_rate)

            metric = ComplianceMetric(
                name="User Journeys",
                description="Validates complete user workflows and business process integration",
                score=successful_steps,
                max_score=total_steps,
                percentage=success_rate,
                level=level,
                details=results.get("detailed_results", {}),
                recommendations=results.get("recommendations", [])
            )

            self.metrics["user_journeys"] = metric
            self.detailed_results["user_journeys"] = results

            return metric

        except Exception as e:
            print(f"❌ Error in user journeys assessment: {str(e)}")
            return self._create_error_metric("User Journeys", str(e))

    def _determine_compliance_level(self, percentage: float) -> ComplianceLevel:
        """Determine compliance level based on percentage."""
        if percentage >= 95:
            return ComplianceLevel.EXCELLENT
        elif percentage >= 85:
            return ComplianceLevel.GOOD
        elif percentage >= 70:
            return ComplianceLevel.ACCEPTABLE
        elif percentage >= 50:
            return ComplianceLevel.NEEDS_IMPROVEMENT
        else:
            return ComplianceLevel.CRITICAL

    def _create_error_metric(self, name: str, error: str) -> ComplianceMetric:
        """Create error metric when assessment fails."""
        return ComplianceMetric(
            name=name,
            description=f"Assessment failed due to error: {error}",
            score=0,
            max_score=1,
            percentage=0,
            level=ComplianceLevel.CRITICAL,
            details={"error": error},
            recommendations=[f"Fix error in {name} assessment: {error}"]
        )

    def _generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive compliance report."""

        # Calculate overall compliance
        total_possible_score = sum(metric.max_score for metric in self.metrics.values() if isinstance(metric, ComplianceMetric))
        total_actual_score = sum(metric.score for metric in self.metrics.values() if isinstance(metric, ComplianceMetric))
        overall_percentage = (total_actual_score / total_possible_score * 100) if total_possible_score > 0 else 0
        overall_level = self._determine_compliance_level(overall_percentage)

        # Generate priority recommendations
        all_recommendations = []
        for metric in self.metrics.values():
            if isinstance(metric, ComplianceMetric):
                all_recommendations.extend(metric.recommendations)

        priority_recommendations = self._prioritize_recommendations(all_recommendations)

        # Generate compliance summary by area
        compliance_by_area = {}
        for area_name, metric in self.metrics.items():
            if isinstance(metric, ComplianceMetric):
                compliance_by_area[area_name] = {
                    "percentage": metric.percentage,
                    "level": metric.level.value,
                    "score": f"{metric.score}/{metric.max_score}",
                    "status": "✅" if metric.level in [ComplianceLevel.EXCELLENT, ComplianceLevel.GOOD] else
                             "⚠️" if metric.level == ComplianceLevel.ACCEPTABLE else "❌"
                }

        # Generate detailed report
        report = {
            "compliance_assessment": {
                "overall_compliance": {
                    "percentage": round(overall_percentage, 2),
                    "level": overall_level.value,
                    "score": f"{total_actual_score}/{total_possible_score}",
                    "status": "✅ COMPLIANT" if overall_level in [ComplianceLevel.EXCELLENT, ComplianceLevel.GOOD] else
                             "⚠️ NEEDS ATTENTION" if overall_level == ComplianceLevel.ACCEPTABLE else
                             "❌ NON-COMPLIANT"
                },
                "execution_summary": {
                    "total_execution_time": round(self.execution_time, 2),
                    "total_tests": self.test_summary["total_tests"],
                    "passed_tests": self.test_summary["passed_tests"],
                    "failed_tests": self.test_summary["failed_tests"],
                    "skipped_tests": self.test_summary["skipped_tests"],
                    "success_rate": round((self.test_summary["passed_tests"] / self.test_summary["total_tests"] * 100) if self.test_summary["total_tests"] > 0 else 0, 2)
                },
                "compliance_by_area": compliance_by_area,
                "priority_recommendations": priority_recommendations,
                "assessment_timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
                "assessment_version": "1.0.0"
            },
            "detailed_metrics": {
                area_name: {
                    "name": metric.name,
                    "description": metric.description,
                    "score": metric.score,
                    "max_score": metric.max_score,
                    "percentage": metric.percentage,
                    "level": metric.level.value,
                    "recommendations": metric.recommendations
                } for area_name, metric in self.metrics.items() if isinstance(metric, ComplianceMetric)
            },
            "detailed_results": self.detailed_results,
            "compliance_matrix": self._generate_compliance_matrix(),
            "trend_analysis": self._generate_trend_analysis(),
            "next_steps": self._generate_next_steps()
        }

        return report

    def _prioritize_recommendations(self, recommendations: List[str]) -> List[str]:
        """Prioritize recommendations based on criticality."""
        # Simple prioritization - can be enhanced with more sophisticated logic
        critical_keywords = ["critical", "security", "authentication", "authorization", "500", "error"]
        important_keywords = ["performance", "optimization", "standardization", "consistency"]

        critical_recs = [rec for rec in recommendations if any(keyword in rec.lower() for keyword in critical_keywords)]
        important_recs = [rec for rec in recommendations if any(keyword in rec.lower() for keyword in important_keywords) and rec not in critical_recs]
        other_recs = [rec for rec in recommendations if rec not in critical_recs and rec not in important_recs]

        return critical_recs[:5] + important_recs[:5] + other_recs[:5]  # Top 15 recommendations

    def _generate_compliance_matrix(self) -> Dict[str, Any]:
        """Generate compliance matrix showing area-by-area breakdown."""
        matrix = {
            "areas": [],
            "scores": [],
            "levels": [],
            "summary": {}
        }

        for area_name, metric in self.metrics.items():
            if isinstance(metric, ComplianceMetric):
                matrix["areas"].append(metric.name)
                matrix["scores"].append(metric.percentage)
                matrix["levels"].append(metric.level.value)

        # Calculate summary statistics
        if matrix["scores"]:
            matrix["summary"] = {
                "average_compliance": round(sum(matrix["scores"]) / len(matrix["scores"]), 2),
                "highest_compliance": max(matrix["scores"]),
                "lowest_compliance": min(matrix["scores"]),
                "areas_above_90": len([s for s in matrix["scores"] if s >= 90]),
                "areas_below_70": len([s for s in matrix["scores"] if s < 70])
            }

        return matrix

    def _generate_trend_analysis(self) -> Dict[str, Any]:
        """Generate trend analysis (placeholder for future implementation)."""
        return {
            "note": "Trend analysis requires historical data collection",
            "current_baseline": {
                "overall_compliance": round(sum(metric.percentage for metric in self.metrics.values() if isinstance(metric, ComplianceMetric)) / len(self.metrics), 2),
                "assessment_date": time.strftime("%Y-%m-%d", time.gmtime())
            },
            "recommendations": [
                "Implement regular compliance assessments to track trends",
                "Store compliance metrics in a time-series database",
                "Set up automated compliance monitoring"
            ]
        }

    def _generate_next_steps(self) -> List[str]:
        """Generate next steps based on compliance results."""
        next_steps = []

        overall_compliance = sum(metric.percentage for metric in self.metrics.values() if isinstance(metric, ComplianceMetric)) / len(self.metrics)

        if overall_compliance >= 90:
            next_steps.extend([
                "🎉 Excellent compliance! Focus on maintaining standards",
                "📈 Implement continuous monitoring",
                "🔄 Set up automated regression testing",
                "📚 Document best practices for team reference"
            ])
        elif overall_compliance >= 75:
            next_steps.extend([
                "✅ Good compliance foundation established",
                "🔧 Address high-priority recommendations",
                "📊 Focus on areas with lower compliance scores",
                "🔍 Implement additional monitoring"
            ])
        else:
            next_steps.extend([
                "🚨 Critical compliance issues need immediate attention",
                "🔥 Address all critical and high-priority recommendations",
                "🛠️ Implement comprehensive API standardization",
                "📋 Establish compliance monitoring and governance"
            ])

        # Add specific technical next steps
        next_steps.extend([
            "🔄 Schedule regular compliance assessments",
            "📝 Update API documentation with compliance standards",
            "🧪 Integrate compliance tests into CI/CD pipeline",
            "👥 Train development team on API standards"
        ])

        return next_steps


# Main test class for compliance metrics
@pytest.mark.asyncio
@pytest.mark.integration
class TestComplianceMetrics:
    """
    Comprehensive API standardization compliance testing.
    """

    async def test_comprehensive_api_compliance(
        self,
        async_client: AsyncClient,
        async_session: AsyncSession
    ):
        """
        Run comprehensive API standardization compliance assessment.
        This is the main entry point for complete compliance testing.
        """

        aggregator = ComplianceMetricsAggregator(async_client, async_session)
        compliance_report = await aggregator.run_comprehensive_compliance_assessment()

        # Assert overall compliance standards
        overall_compliance = compliance_report["compliance_assessment"]["overall_compliance"]

        # Minimum compliance threshold (can be adjusted based on requirements)
        min_compliance_threshold = 70.0

        assert overall_compliance["percentage"] >= min_compliance_threshold, \
            f"Overall API compliance below threshold: {overall_compliance['percentage']}% < {min_compliance_threshold}%"

        # Print comprehensive compliance report
        print("\n" + "="*80)
        print("🏆 COMPREHENSIVE API STANDARDIZATION COMPLIANCE REPORT")
        print("="*80)

        print(f"\n📊 OVERALL COMPLIANCE: {overall_compliance['percentage']}% ({overall_compliance['level']})")
        print(f"📈 STATUS: {overall_compliance['status']}")
        print(f"⏱️ EXECUTION TIME: {compliance_report['compliance_assessment']['execution_summary']['total_execution_time']} seconds")
        print(f"🧪 TOTAL TESTS: {compliance_report['compliance_assessment']['execution_summary']['total_tests']}")
        print(f"✅ PASSED: {compliance_report['compliance_assessment']['execution_summary']['passed_tests']}")
        print(f"❌ FAILED: {compliance_report['compliance_assessment']['execution_summary']['failed_tests']}")

        print("\n📋 COMPLIANCE BY AREA:")
        for area_name, area_data in compliance_report["compliance_assessment"]["compliance_by_area"].items():
            print(f"  {area_data['status']} {area_name.replace('_', ' ').title()}: {area_data['percentage']}% ({area_data['score']})")

        print("\n🎯 PRIORITY RECOMMENDATIONS:")
        for i, recommendation in enumerate(compliance_report["compliance_assessment"]["priority_recommendations"][:10], 1):
            print(f"  {i:2d}. {recommendation}")

        print("\n🚀 NEXT STEPS:")
        for i, step in enumerate(compliance_report["compliance_assessment"]["next_steps"][:8], 1):
            print(f"  {i}. {step}")

        print("\n" + "="*80)
        print("📄 Full detailed report available in compliance_report object")
        print("="*80)

        return compliance_report

    async def test_compliance_metrics_aggregation(
        self,
        async_client: AsyncClient,
        async_session: AsyncSession
    ):
        """Test compliance metrics aggregation functionality."""

        aggregator = ComplianceMetricsAggregator(async_client, async_session)

        # Test individual assessment methods
        api_metric = await aggregator._assess_api_standardization()
        assert isinstance(api_metric, ComplianceMetric)
        assert api_metric.name == "API Endpoint Standardization"

        contract_metric = await aggregator._assess_contract_validation()
        assert isinstance(contract_metric, ComplianceMetric)
        assert contract_metric.name == "API Contract Validation"

    async def test_compliance_level_determination(
        self,
        async_client: AsyncClient,
        async_session: AsyncSession
    ):
        """Test compliance level determination logic."""

        aggregator = ComplianceMetricsAggregator(async_client, async_session)

        # Test compliance level boundaries
        assert aggregator._determine_compliance_level(98) == ComplianceLevel.EXCELLENT
        assert aggregator._determine_compliance_level(87) == ComplianceLevel.GOOD
        assert aggregator._determine_compliance_level(75) == ComplianceLevel.ACCEPTABLE
        assert aggregator._determine_compliance_level(60) == ComplianceLevel.NEEDS_IMPROVEMENT
        assert aggregator._determine_compliance_level(30) == ComplianceLevel.CRITICAL

    async def test_compliance_report_structure(
        self,
        async_client: AsyncClient,
        async_session: AsyncSession
    ):
        """Test compliance report structure and completeness."""

        aggregator = ComplianceMetricsAggregator(async_client, async_session)
        compliance_report = await aggregator.run_comprehensive_compliance_assessment()

        # Verify report structure
        assert "compliance_assessment" in compliance_report
        assert "detailed_metrics" in compliance_report
        assert "detailed_results" in compliance_report
        assert "compliance_matrix" in compliance_report

        # Verify compliance assessment structure
        assessment = compliance_report["compliance_assessment"]
        assert "overall_compliance" in assessment
        assert "execution_summary" in assessment
        assert "compliance_by_area" in assessment
        assert "priority_recommendations" in assessment

        # Verify overall compliance structure
        overall = assessment["overall_compliance"]
        assert "percentage" in overall
        assert "level" in overall
        assert "score" in overall
        assert "status" in overall


# Pytest configuration for comprehensive testing
def pytest_configure(config):
    """Configure pytest for comprehensive compliance testing."""
    config.addinivalue_line("markers", "compliance: Compliance testing markers")
    config.addinivalue_line("markers", "metrics: Metrics and reporting tests")


if __name__ == "__main__":
    # Allow running compliance tests directly
    pytest.main([__file__, "-v", "--tb=short"])