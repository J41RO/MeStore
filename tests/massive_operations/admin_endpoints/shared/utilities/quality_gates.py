"""
Quality Gates System for Massive Admin Testing Operation
Implements the 3-tier quality validation system for coordinated multi-squad testing.
"""

import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import subprocess
import statistics


class QualityGateStatus(Enum):
    """Quality gate status enumeration."""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    PASSED = "PASSED"
    FAILED = "FAILED"
    ERROR = "ERROR"


class ValidationLevel(Enum):
    """Validation severity levels."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass
class ValidationResult:
    """Individual validation result."""
    name: str
    status: bool
    expected: Any
    actual: Any
    level: ValidationLevel
    message: str
    timestamp: str

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        result = asdict(self)
        result['level'] = self.level.value
        return result


@dataclass
class QualityGateResult:
    """Complete quality gate validation result."""
    gate_number: int
    gate_name: str
    status: QualityGateStatus
    overall_score: float
    validations: List[ValidationResult]
    squad_results: Dict[str, Dict]
    start_time: str
    end_time: Optional[str]
    duration_seconds: Optional[float]

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        result = asdict(self)
        result['status'] = self.status.value
        result['validations'] = [v.to_dict() for v in self.validations]
        return result


class QualityGateValidator:
    """Validator for quality gates across all squads."""

    def __init__(self, workspace_path: str = ".workspace"):
        self.workspace_path = Path(workspace_path)
        self.coordination_file = self.workspace_path / "communications" / "coordination-channel.json"
        self.reports_dir = Path("tests/massive_operations/admin_endpoints/shared/reports")
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        # Setup logging
        self.logger = self._setup_logger()

        # Quality gate definitions
        self.quality_gates = {
            1: self._define_gate_1_criteria(),
            2: self._define_gate_2_criteria(),
            3: self._define_gate_3_criteria()
        }

    def _setup_logger(self) -> logging.Logger:
        """Set up logging for quality gate validation."""
        logger = logging.getLogger("quality_gates")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def _define_gate_1_criteria(self) -> Dict:
        """Define criteria for Quality Gate 1: TDD Validation."""
        return {
            "name": "TDD Validation Gate",
            "description": "Validates TDD RED-GREEN completion across all squads",
            "criteria": {
                "red_tests_completion": {
                    "threshold": 100,
                    "operator": ">=",
                    "level": ValidationLevel.CRITICAL,
                    "description": "All RED tests must be written"
                },
                "green_tests_passing": {
                    "threshold": 80,
                    "operator": ">=",
                    "level": ValidationLevel.CRITICAL,
                    "description": "Minimum 80% GREEN tests passing"
                },
                "fixture_conflicts": {
                    "threshold": 0,
                    "operator": "==",
                    "level": ValidationLevel.HIGH,
                    "description": "No fixture conflicts between squads"
                },
                "dependency_matrix_complete": {
                    "threshold": True,
                    "operator": "==",
                    "level": ValidationLevel.HIGH,
                    "description": "All squad dependencies mapped"
                },
                "squad_coverage_minimum": {
                    "threshold": 50,
                    "operator": ">=",
                    "level": ValidationLevel.MEDIUM,
                    "description": "Each squad has minimum 50% coverage"
                },
                "security_tests_implemented": {
                    "threshold": 100,
                    "operator": ">=",
                    "level": ValidationLevel.HIGH,
                    "description": "Security tests implemented in all squads"
                }
            }
        }

    def _define_gate_2_criteria(self) -> Dict:
        """Define criteria for Quality Gate 2: Integration Validation."""
        return {
            "name": "Integration Validation Gate",
            "description": "Validates integration testing and cross-squad coordination",
            "criteria": {
                "integration_tests_passing": {
                    "threshold": 90,
                    "operator": ">=",
                    "level": ValidationLevel.CRITICAL,
                    "description": "90% integration tests passing"
                },
                "dependencies_resolved": {
                    "threshold": 100,
                    "operator": ">=",
                    "level": ValidationLevel.CRITICAL,
                    "description": "All dependencies resolved between squads"
                },
                "security_tests_passing": {
                    "threshold": 100,
                    "operator": ">=",
                    "level": ValidationLevel.CRITICAL,
                    "description": "All security tests passing"
                },
                "performance_benchmarks_met": {
                    "threshold": True,
                    "operator": "==",
                    "level": ValidationLevel.HIGH,
                    "description": "Performance benchmarks met"
                },
                "cross_squad_integration": {
                    "threshold": 100,
                    "operator": ">=",
                    "level": ValidationLevel.HIGH,
                    "description": "Cross-squad integration validated"
                },
                "api_compatibility": {
                    "threshold": 100,
                    "operator": ">=",
                    "level": ValidationLevel.MEDIUM,
                    "description": "API compatibility maintained"
                }
            }
        }

    def _define_gate_3_criteria(self) -> Dict:
        """Define criteria for Quality Gate 3: Final Validation."""
        return {
            "name": "Final Validation Gate",
            "description": "Final validation for operation completion",
            "criteria": {
                "total_coverage": {
                    "threshold": 95,
                    "operator": ">=",
                    "level": ValidationLevel.CRITICAL,
                    "description": "95% total coverage achieved"
                },
                "refactor_completion": {
                    "threshold": 100,
                    "operator": ">=",
                    "level": ValidationLevel.CRITICAL,
                    "description": "REFACTOR phase completed"
                },
                "breaking_changes": {
                    "threshold": 0,
                    "operator": "==",
                    "level": ValidationLevel.CRITICAL,
                    "description": "No breaking changes introduced"
                },
                "test_suite_execution_time": {
                    "threshold": 300,
                    "operator": "<=",
                    "level": ValidationLevel.HIGH,
                    "description": "Test suite executes in <5 minutes"
                },
                "code_quality_score": {
                    "threshold": 90,
                    "operator": ">=",
                    "level": ValidationLevel.HIGH,
                    "description": "Code quality score ≥90%"
                },
                "documentation_complete": {
                    "threshold": 100,
                    "operator": ">=",
                    "level": ValidationLevel.MEDIUM,
                    "description": "Documentation completed"
                }
            }
        }

    async def validate_quality_gate(self, gate_number: int, squad_results: Dict[str, Dict]) -> QualityGateResult:
        """
        Validate a specific quality gate.

        Args:
            gate_number: Gate number (1, 2, 3)
            squad_results: Results from all squads

        Returns:
            QualityGateResult: Validation results
        """
        start_time = datetime.utcnow().isoformat() + 'Z'

        if gate_number not in self.quality_gates:
            return QualityGateResult(
                gate_number=gate_number,
                gate_name=f"Gate {gate_number}",
                status=QualityGateStatus.ERROR,
                overall_score=0.0,
                validations=[],
                squad_results=squad_results,
                start_time=start_time,
                end_time=start_time,
                duration_seconds=0.0
            )

        gate_def = self.quality_gates[gate_number]
        validations = []

        self.logger.info(f"Starting Quality Gate {gate_number} validation: {gate_def['name']}")

        # Validate each criterion
        for criterion_name, criterion_def in gate_def["criteria"].items():
            validation = await self._validate_criterion(
                criterion_name,
                criterion_def,
                squad_results
            )
            validations.append(validation)

        # Calculate overall score
        total_weight = sum(self._get_validation_weight(v.level) for v in validations)
        passed_weight = sum(
            self._get_validation_weight(v.level) for v in validations if v.status
        )
        overall_score = (passed_weight / total_weight * 100) if total_weight > 0 else 0

        # Determine gate status
        critical_failures = [v for v in validations if not v.status and v.level == ValidationLevel.CRITICAL]
        high_failures = [v for v in validations if not v.status and v.level == ValidationLevel.HIGH]

        if critical_failures:
            status = QualityGateStatus.FAILED
        elif len(high_failures) > 2:  # Allow max 2 high-level failures
            status = QualityGateStatus.FAILED
        elif overall_score >= 85:  # 85% threshold for passing
            status = QualityGateStatus.PASSED
        else:
            status = QualityGateStatus.FAILED

        end_time = datetime.utcnow().isoformat() + 'Z'
        duration = (datetime.fromisoformat(end_time.replace('Z', '+00:00')) -
                   datetime.fromisoformat(start_time.replace('Z', '+00:00'))).total_seconds()

        result = QualityGateResult(
            gate_number=gate_number,
            gate_name=gate_def["name"],
            status=status,
            overall_score=round(overall_score, 2),
            validations=validations,
            squad_results=squad_results,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=round(duration, 2)
        )

        # Save validation report
        await self._save_validation_report(result)

        self.logger.info(
            f"Quality Gate {gate_number} completed: {status.value} "
            f"(Score: {overall_score:.2f}%, Duration: {duration:.2f}s)"
        )

        return result

    async def _validate_criterion(self, name: str, criterion_def: Dict,
                                 squad_results: Dict[str, Dict]) -> ValidationResult:
        """Validate a specific criterion."""
        threshold = criterion_def["threshold"]
        operator = criterion_def["operator"]
        level = criterion_def["level"]
        description = criterion_def["description"]

        timestamp = datetime.utcnow().isoformat() + 'Z'

        try:
            # Get actual value based on criterion type
            actual = await self._get_criterion_value(name, squad_results)

            # Perform validation based on operator
            if operator == ">=":
                status = actual >= threshold
            elif operator == "<=":
                status = actual <= threshold
            elif operator == "==":
                status = actual == threshold
            elif operator == "!=":
                status = actual != threshold
            elif operator == ">":
                status = actual > threshold
            elif operator == "<":
                status = actual < threshold
            else:
                status = False

            message = f"{description}: Expected {operator} {threshold}, got {actual}"

        except Exception as e:
            status = False
            actual = f"ERROR: {str(e)}"
            message = f"Error validating {name}: {str(e)}"

        return ValidationResult(
            name=name,
            status=status,
            expected=f"{operator} {threshold}",
            actual=actual,
            level=level,
            message=message,
            timestamp=timestamp
        )

    async def _get_criterion_value(self, criterion_name: str, squad_results: Dict[str, Dict]) -> Any:
        """Get the actual value for a criterion from squad results."""

        if criterion_name == "red_tests_completion":
            # Check if all squads have completed RED phase
            red_completion = []
            for squad_id, results in squad_results.items():
                completion = results.get("red_phase_complete", False)
                red_completion.append(100 if completion else 0)
            return min(red_completion) if red_completion else 0

        elif criterion_name == "green_tests_passing":
            # Average passing rate across squads
            passing_rates = []
            for squad_id, results in squad_results.items():
                total_tests = results.get("tests_created", 0)
                passing_tests = results.get("tests_passing", 0)
                rate = (passing_tests / total_tests * 100) if total_tests > 0 else 0
                passing_rates.append(rate)
            return statistics.mean(passing_rates) if passing_rates else 0

        elif criterion_name == "fixture_conflicts":
            # Count active fixture conflicts
            total_conflicts = 0
            for squad_id, results in squad_results.items():
                conflicts = results.get("fixture_conflicts", 0)
                total_conflicts += conflicts
            return total_conflicts

        elif criterion_name == "dependency_matrix_complete":
            # Check if all dependencies are resolved
            for squad_id, results in squad_results.items():
                pending_deps = results.get("pending_dependencies", [])
                if pending_deps:
                    return False
            return True

        elif criterion_name == "squad_coverage_minimum":
            # Check minimum coverage across squads
            min_coverage = 100
            for squad_id, results in squad_results.items():
                coverage = results.get("coverage_percentage", 0)
                min_coverage = min(min_coverage, coverage)
            return min_coverage

        elif criterion_name == "security_tests_implemented":
            # Check security test implementation
            implementation_rates = []
            for squad_id, results in squad_results.items():
                expected_security_tests = results.get("expected_security_tests", 10)
                actual_security_tests = results.get("security_tests", 0)
                rate = (actual_security_tests / expected_security_tests * 100) if expected_security_tests > 0 else 0
                implementation_rates.append(rate)
            return min(implementation_rates) if implementation_rates else 0

        elif criterion_name == "integration_tests_passing":
            # Integration test passing rate
            total_integration = 0
            passing_integration = 0
            for squad_id, results in squad_results.items():
                total_integration += results.get("integration_tests_total", 0)
                passing_integration += results.get("integration_tests_passing", 0)
            return (passing_integration / total_integration * 100) if total_integration > 0 else 0

        elif criterion_name == "dependencies_resolved":
            # Check dependency resolution rate
            total_deps = 0
            resolved_deps = 0
            for squad_id, results in squad_results.items():
                total_deps += results.get("total_dependencies", 0)
                resolved_deps += results.get("resolved_dependencies", 0)
            return (resolved_deps / total_deps * 100) if total_deps > 0 else 100

        elif criterion_name == "security_tests_passing":
            # Security test passing rate
            total_security = 0
            passing_security = 0
            for squad_id, results in squad_results.items():
                total_security += results.get("security_tests", 0)
                passing_security += results.get("security_tests_passing", 0)
            return (passing_security / total_security * 100) if total_security > 0 else 0

        elif criterion_name == "performance_benchmarks_met":
            # Check if performance benchmarks are met
            for squad_id, results in squad_results.items():
                benchmarks_met = results.get("performance_benchmarks_met", False)
                if not benchmarks_met:
                    return False
            return True

        elif criterion_name == "cross_squad_integration":
            # Cross-squad integration validation
            integration_scores = []
            for squad_id, results in squad_results.items():
                integration_score = results.get("cross_squad_integration_score", 0)
                integration_scores.append(integration_score)
            return min(integration_scores) if integration_scores else 0

        elif criterion_name == "api_compatibility":
            # API compatibility check
            compatibility_scores = []
            for squad_id, results in squad_results.items():
                compatibility = results.get("api_compatibility_score", 100)
                compatibility_scores.append(compatibility)
            return min(compatibility_scores) if compatibility_scores else 100

        elif criterion_name == "total_coverage":
            # Total coverage across all squads
            return await self._calculate_total_coverage(squad_results)

        elif criterion_name == "refactor_completion":
            # REFACTOR phase completion
            refactor_rates = []
            for squad_id, results in squad_results.items():
                refactor_complete = results.get("refactor_phase_complete", False)
                refactor_rates.append(100 if refactor_complete else 0)
            return min(refactor_rates) if refactor_rates else 0

        elif criterion_name == "breaking_changes":
            # Count breaking changes
            total_breaking = 0
            for squad_id, results in squad_results.items():
                breaking = results.get("breaking_changes", 0)
                total_breaking += breaking
            return total_breaking

        elif criterion_name == "test_suite_execution_time":
            # Total test suite execution time
            total_time = 0
            for squad_id, results in squad_results.items():
                execution_time = results.get("test_execution_time", 0)
                total_time += execution_time
            return total_time

        elif criterion_name == "code_quality_score":
            # Average code quality score
            quality_scores = []
            for squad_id, results in squad_results.items():
                quality_score = results.get("code_quality_score", 0)
                quality_scores.append(quality_score)
            return statistics.mean(quality_scores) if quality_scores else 0

        elif criterion_name == "documentation_complete":
            # Documentation completion rate
            doc_rates = []
            for squad_id, results in squad_results.items():
                doc_complete = results.get("documentation_complete", False)
                doc_rates.append(100 if doc_complete else 0)
            return min(doc_rates) if doc_rates else 0

        else:
            # Unknown criterion
            raise ValueError(f"Unknown criterion: {criterion_name}")

    async def _calculate_total_coverage(self, squad_results: Dict[str, Dict]) -> float:
        """Calculate total coverage across all squads."""
        total_lines = 1785  # admin.py total lines
        covered_lines = 0

        for squad_id, results in squad_results.items():
            squad_covered = results.get("lines_covered", 0)
            covered_lines += squad_covered

        return (covered_lines / total_lines * 100) if total_lines > 0 else 0

    def _get_validation_weight(self, level: ValidationLevel) -> int:
        """Get weight for validation level."""
        weights = {
            ValidationLevel.CRITICAL: 10,
            ValidationLevel.HIGH: 5,
            ValidationLevel.MEDIUM: 3,
            ValidationLevel.LOW: 1
        }
        return weights.get(level, 1)

    async def _save_validation_report(self, result: QualityGateResult):
        """Save validation report to file."""
        try:
            report_file = self.reports_dir / f"quality_gate_{result.gate_number}_report.json"

            report_data = result.to_dict()

            with open(report_file, 'w') as f:
                json.dump(report_data, f, indent=2)

            self.logger.info(f"Validation report saved: {report_file}")

        except Exception as e:
            self.logger.error(f"Error saving validation report: {e}")

    async def run_all_quality_gates(self, squad_results: Dict[str, Dict]) -> Dict[int, QualityGateResult]:
        """
        Run all quality gates in sequence.

        Args:
            squad_results: Results from all squads

        Returns:
            Dict of gate results
        """
        gate_results = {}

        for gate_number in [1, 2, 3]:
            self.logger.info(f"Running Quality Gate {gate_number}")

            result = await self.validate_quality_gate(gate_number, squad_results)
            gate_results[gate_number] = result

            # Stop if critical gate fails
            if result.status == QualityGateStatus.FAILED and gate_number in [1, 2]:
                critical_failures = [
                    v for v in result.validations
                    if not v.status and v.level == ValidationLevel.CRITICAL
                ]
                if critical_failures:
                    self.logger.error(f"Critical failures in Gate {gate_number}, stopping validation")
                    break

        return gate_results

    def generate_final_report(self, gate_results: Dict[int, QualityGateResult]) -> Dict:
        """Generate final quality validation report."""
        total_gates = len(gate_results)
        passed_gates = sum(1 for result in gate_results.values() if result.status == QualityGateStatus.PASSED)

        overall_score = 0
        if gate_results:
            scores = [result.overall_score for result in gate_results.values()]
            overall_score = statistics.mean(scores)

        # Collect all validation issues
        all_validations = []
        for result in gate_results.values():
            all_validations.extend(result.validations)

        failed_validations = [v for v in all_validations if not v.status]
        critical_failures = [v for v in failed_validations if v.level == ValidationLevel.CRITICAL]

        final_status = "PASSED" if passed_gates == total_gates and not critical_failures else "FAILED"

        report = {
            "operation_summary": {
                "final_status": final_status,
                "overall_score": round(overall_score, 2),
                "gates_passed": passed_gates,
                "gates_total": total_gates,
                "pass_rate": round((passed_gates / total_gates * 100) if total_gates > 0 else 0, 2)
            },
            "gate_results": {
                str(gate_num): result.to_dict()
                for gate_num, result in gate_results.items()
            },
            "validation_summary": {
                "total_validations": len(all_validations),
                "passed_validations": len([v for v in all_validations if v.status]),
                "failed_validations": len(failed_validations),
                "critical_failures": len(critical_failures)
            },
            "recommendations": self._generate_recommendations(failed_validations),
            "generated_at": datetime.utcnow().isoformat() + 'Z'
        }

        return report

    def _generate_recommendations(self, failed_validations: List[ValidationResult]) -> List[str]:
        """Generate recommendations based on failed validations."""
        recommendations = []

        critical_failures = [v for v in failed_validations if v.level == ValidationLevel.CRITICAL]
        high_failures = [v for v in failed_validations if v.level == ValidationLevel.HIGH]

        if critical_failures:
            recommendations.append("URGENT: Address critical validation failures before proceeding")
            for failure in critical_failures:
                recommendations.append(f"- Fix {failure.name}: {failure.message}")

        if high_failures:
            recommendations.append("HIGH PRIORITY: Resolve high-level validation issues")
            for failure in high_failures:
                recommendations.append(f"- Address {failure.name}: {failure.message}")

        if not failed_validations:
            recommendations.append("All validations passed - operation ready for production")

        return recommendations


# Utility functions
async def run_quality_gate_validation(gate_number: int, squad_results: Dict[str, Dict]) -> QualityGateResult:
    """Utility function to run a single quality gate validation."""
    validator = QualityGateValidator()
    return await validator.validate_quality_gate(gate_number, squad_results)


async def run_full_quality_validation(squad_results: Dict[str, Dict]) -> Dict:
    """Utility function to run complete quality validation."""
    validator = QualityGateValidator()
    gate_results = await validator.run_all_quality_gates(squad_results)
    final_report = validator.generate_final_report(gate_results)
    return final_report


if __name__ == "__main__":
    # Example usage
    async def test_quality_gates():
        # Mock squad results for testing
        mock_squad_results = {
            "SQUAD_1": {
                "red_phase_complete": True,
                "tests_created": 50,
                "tests_passing": 45,
                "coverage_percentage": 85.5,
                "security_tests": 12,
                "fixture_conflicts": 0
            },
            "SQUAD_2": {
                "red_phase_complete": True,
                "tests_created": 48,
                "tests_passing": 44,
                "coverage_percentage": 82.3,
                "security_tests": 10,
                "fixture_conflicts": 1
            },
            "SQUAD_3": {
                "red_phase_complete": True,
                "tests_created": 52,
                "tests_passing": 48,
                "coverage_percentage": 88.7,
                "security_tests": 15,
                "fixture_conflicts": 0
            },
            "SQUAD_4": {
                "red_phase_complete": True,
                "tests_created": 45,
                "tests_passing": 43,
                "coverage_percentage": 79.2,
                "security_tests": 8,
                "fixture_conflicts": 0
            }
        }

        # Run Gate 1 validation
        result = await run_quality_gate_validation(1, mock_squad_results)
        print(f"Gate 1 Result: {result.status.value} (Score: {result.overall_score}%)")

        # Run full validation
        full_report = await run_full_quality_validation(mock_squad_results)
        print(f"Full Validation: {full_report['operation_summary']['final_status']}")

    # Run test
    asyncio.run(test_quality_gates())