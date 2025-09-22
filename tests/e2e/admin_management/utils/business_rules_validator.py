# ~/tests/e2e/admin_management/utils/business_rules_validator.py
# Business Rules Validator for Colombian Marketplace
# Validation logic for admin management business rules

"""
Business Rules Validator for Colombian Marketplace.

This module provides comprehensive validation of business rules
for admin management operations in a Colombian marketplace context.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
import re

from .colombian_timezone_utils import ColombianTimeManager, BusinessRulesValidator as TimeValidator


class ValidationLevel(Enum):
    """Validation severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ComplianceStandard(Enum):
    """Colombian compliance standards."""
    LEY_1581 = "ley_1581"  # Data Protection Law
    SUPERINTENDENCIA_FINANCIERA = "superintendencia_financiera"
    CODIGO_COMERCIO = "codigo_comercio"
    ESTATUTO_TRIBUTARIO = "estatuto_tributario"


@dataclass
class ValidationRule:
    """Business rule validation definition."""
    rule_id: str
    rule_name: str
    description: str
    validation_function: str
    compliance_standard: Optional[ComplianceStandard]
    severity: ValidationLevel
    applies_to: List[str]  # Operation types


@dataclass
class ValidationResult:
    """Result of business rule validation."""
    rule_id: str
    rule_name: str
    passed: bool
    severity: ValidationLevel
    message: str
    compliance_standard: Optional[ComplianceStandard]
    remediation_suggestion: Optional[str]
    metadata: Dict[str, Any]


class ColombianDocumentValidator:
    """Validator for Colombian legal documents."""

    @staticmethod
    def validate_cedula(cedula: str) -> ValidationResult:
        """Validate Colombian Cédula de Ciudadanía."""
        # Remove any non-numeric characters
        clean_cedula = re.sub(r'\D', '', cedula)

        if len(clean_cedula) < 6 or len(clean_cedula) > 10:
            return ValidationResult(
                rule_id="DOC_001",
                rule_name="Cédula Length Validation",
                passed=False,
                severity=ValidationLevel.ERROR,
                message="Cédula must be between 6 and 10 digits",
                compliance_standard=ComplianceStandard.CODIGO_COMERCIO,
                remediation_suggestion="Provide a valid Colombian Cédula number",
                metadata={"provided_cedula": cedula, "clean_cedula": clean_cedula}
            )

        # Validate Colombian Cédula check digit algorithm (simplified)
        if len(clean_cedula) >= 8:
            # Basic validation - real implementation would use full algorithm
            check_digit = int(clean_cedula[-1])
            # Simplified check - in reality this would be more complex
            if check_digit < 0 or check_digit > 9:
                return ValidationResult(
                    rule_id="DOC_002",
                    rule_name="Cédula Check Digit Validation",
                    passed=False,
                    severity=ValidationLevel.WARNING,
                    message="Cédula check digit may be invalid",
                    compliance_standard=ComplianceStandard.CODIGO_COMERCIO,
                    remediation_suggestion="Verify Cédula number with official source",
                    metadata={"provided_cedula": cedula}
                )

        return ValidationResult(
            rule_id="DOC_001",
            rule_name="Cédula Validation",
            passed=True,
            severity=ValidationLevel.INFO,
            message="Cédula format is valid",
            compliance_standard=ComplianceStandard.CODIGO_COMERCIO,
            remediation_suggestion=None,
            metadata={"validated_cedula": clean_cedula}
        )

    @staticmethod
    def validate_nit(nit: str) -> ValidationResult:
        """Validate Colombian NIT (Número de Identificación Tributaria)."""
        # Remove any non-numeric characters except hyphens
        clean_nit = re.sub(r'[^\d-]', '', nit)

        # NIT format: XXXXXXXXX-X (9 digits + check digit)
        nit_pattern = r'^\d{8,9}-\d$'

        if not re.match(nit_pattern, clean_nit):
            return ValidationResult(
                rule_id="DOC_003",
                rule_name="NIT Format Validation",
                passed=False,
                severity=ValidationLevel.ERROR,
                message="NIT must follow format XXXXXXXXX-X",
                compliance_standard=ComplianceStandard.ESTATUTO_TRIBUTARIO,
                remediation_suggestion="Provide NIT in format XXXXXXXXX-X",
                metadata={"provided_nit": nit, "clean_nit": clean_nit}
            )

        # Extract number and check digit
        nit_parts = clean_nit.split('-')
        nit_number = nit_parts[0]
        check_digit = int(nit_parts[1])

        # Validate NIT check digit (simplified algorithm)
        if len(nit_number) == 9:
            # Real NIT validation would use the full Colombian algorithm
            calculated_check_digit = ColombianDocumentValidator._calculate_nit_check_digit(nit_number)
            if calculated_check_digit != check_digit:
                return ValidationResult(
                    rule_id="DOC_004",
                    rule_name="NIT Check Digit Validation",
                    passed=False,
                    severity=ValidationLevel.ERROR,
                    message="NIT check digit is invalid",
                    compliance_standard=ComplianceStandard.ESTATUTO_TRIBUTARIO,
                    remediation_suggestion="Verify NIT with DIAN (Colombian tax authority)",
                    metadata={"provided_nit": nit, "calculated_check_digit": calculated_check_digit}
                )

        return ValidationResult(
            rule_id="DOC_003",
            rule_name="NIT Validation",
            passed=True,
            severity=ValidationLevel.INFO,
            message="NIT format is valid",
            compliance_standard=ComplianceStandard.ESTATUTO_TRIBUTARIO,
            remediation_suggestion=None,
            metadata={"validated_nit": clean_nit}
        )

    @staticmethod
    def _calculate_nit_check_digit(nit_number: str) -> int:
        """Calculate NIT check digit using Colombian algorithm (simplified)."""
        # Simplified version - real implementation would use full DIAN algorithm
        # This is just for testing purposes
        weights = [71, 67, 59, 53, 47, 43, 41, 37, 29, 23, 19, 17, 13, 7, 3]
        total = 0

        for i, digit in enumerate(reversed(nit_number)):
            if i < len(weights):
                total += int(digit) * weights[i]

        remainder = total % 11
        if remainder < 2:
            return remainder
        else:
            return 11 - remainder


class AdminPermissionValidator:
    """Validator for admin permission and security rules."""

    @staticmethod
    def validate_permission_assignment(admin_data: Dict[str, Any],
                                     permission_data: Dict[str, Any],
                                     assigning_admin: Dict[str, Any]) -> List[ValidationResult]:
        """Validate permission assignment business rules."""
        results = []

        # Rule: Cannot assign higher security level than own
        if admin_data.get("security_clearance_level", 0) >= assigning_admin.get("security_clearance_level", 0):
            results.append(ValidationResult(
                rule_id="PERM_001",
                rule_name="Security Clearance Level Check",
                passed=False,
                severity=ValidationLevel.ERROR,
                message="Cannot assign admin with equal or higher security clearance",
                compliance_standard=None,
                remediation_suggestion="Request approval from higher-level administrator",
                metadata={
                    "admin_level": admin_data.get("security_clearance_level"),
                    "assigning_admin_level": assigning_admin.get("security_clearance_level")
                }
            ))

        # Rule: Validate department jurisdiction
        admin_dept = admin_data.get("department_id")
        assigning_admin_dept = assigning_admin.get("department_id")

        if admin_dept != assigning_admin_dept and assigning_admin.get("user_type") != "SUPERUSER":
            results.append(ValidationResult(
                rule_id="PERM_002",
                rule_name="Department Jurisdiction Check",
                passed=False,
                severity=ValidationLevel.WARNING,
                message="Cross-department admin assignment requires SUPERUSER approval",
                compliance_standard=None,
                remediation_suggestion="Escalate to SUPERUSER for cross-department assignments",
                metadata={
                    "admin_department": admin_dept,
                    "assigning_admin_department": assigning_admin_dept
                }
            ))

        # Rule: SUPERUSER creation restrictions
        if admin_data.get("user_type") == "SUPERUSER" and assigning_admin.get("user_type") != "SUPERUSER":
            results.append(ValidationResult(
                rule_id="PERM_003",
                rule_name="SUPERUSER Creation Restriction",
                passed=False,
                severity=ValidationLevel.CRITICAL,
                message="Only SUPERUSER can create other SUPERUSER accounts",
                compliance_standard=None,
                remediation_suggestion="Only existing SUPERUSER can perform this operation",
                metadata={
                    "requested_type": admin_data.get("user_type"),
                    "assigning_admin_type": assigning_admin.get("user_type")
                }
            ))

        # If no issues found, add success result
        if not results:
            results.append(ValidationResult(
                rule_id="PERM_000",
                rule_name="Permission Assignment Validation",
                passed=True,
                severity=ValidationLevel.INFO,
                message="Permission assignment follows all business rules",
                compliance_standard=None,
                remediation_suggestion=None,
                metadata={"validation_passed": True}
            ))

        return results

    @staticmethod
    def validate_bulk_operation(operation_data: Dict[str, Any],
                              admin_data: Dict[str, Any]) -> List[ValidationResult]:
        """Validate bulk operation business rules."""
        results = []

        user_count = len(operation_data.get("user_ids", []))
        operation_type = operation_data.get("action", "")

        # Rule: Bulk operation limits
        max_bulk_limits = {
            "activate": 50,
            "deactivate": 25,
            "lock": 100,
            "unlock": 100
        }

        max_allowed = max_bulk_limits.get(operation_type, 10)
        if user_count > max_allowed:
            results.append(ValidationResult(
                rule_id="BULK_001",
                rule_name="Bulk Operation Size Limit",
                passed=False,
                severity=ValidationLevel.ERROR,
                message=f"Bulk {operation_type} limited to {max_allowed} users per operation",
                compliance_standard=None,
                remediation_suggestion=f"Split operation into batches of {max_allowed} or fewer",
                metadata={
                    "requested_count": user_count,
                    "max_allowed": max_allowed,
                    "operation_type": operation_type
                }
            ))

        # Rule: High-risk operations require business hours
        high_risk_operations = ["deactivate", "lock"]
        if operation_type in high_risk_operations:
            current_time = ColombianTimeManager.get_current_colombia_time()
            time_validation = TimeValidator.validate_business_hours_operation(
                current_time, "bulk_action", admin_data.get("persona")
            )

            if not time_validation["validation_passed"]:
                results.append(ValidationResult(
                    rule_id="BULK_002",
                    rule_name="Business Hours Requirement",
                    passed=False,
                    severity=ValidationLevel.WARNING,
                    message="High-risk bulk operations should be performed during business hours",
                    compliance_standard=None,
                    remediation_suggestion="Schedule operation during Colombian business hours (8 AM - 6 PM COT)",
                    metadata=time_validation
                ))

        # Rule: Reason requirement for high-impact operations
        reason = operation_data.get("reason", "").strip()
        if operation_type in ["deactivate", "lock"] and len(reason) < 20:
            results.append(ValidationResult(
                rule_id="BULK_003",
                rule_name="Adequate Justification Requirement",
                passed=False,
                severity=ValidationLevel.ERROR,
                message="High-impact bulk operations require detailed justification (minimum 20 characters)",
                compliance_standard=None,
                remediation_suggestion="Provide detailed reason for the bulk operation",
                metadata={
                    "provided_reason_length": len(reason),
                    "minimum_required": 20,
                    "operation_type": operation_type
                }
            ))

        # If no issues found, add success result
        if not results:
            results.append(ValidationResult(
                rule_id="BULK_000",
                rule_name="Bulk Operation Validation",
                passed=True,
                severity=ValidationLevel.INFO,
                message="Bulk operation follows all business rules",
                compliance_standard=None,
                remediation_suggestion=None,
                metadata={"validation_passed": True}
            ))

        return results


class VendorManagementValidator:
    """Validator for vendor management business rules."""

    @staticmethod
    def validate_vendor_approval_workflow(vendor_data: Dict[str, Any],
                                        admin_data: Dict[str, Any]) -> List[ValidationResult]:
        """Validate vendor approval workflow business rules."""
        results = []

        # Rule: Required documents validation
        required_documents = ["documento_identidad", "rut", "banking_info"]
        missing_documents = []

        for doc in required_documents:
            if not vendor_data.get(doc):
                missing_documents.append(doc)

        if missing_documents:
            results.append(ValidationResult(
                rule_id="VEN_001",
                rule_name="Required Documents Check",
                passed=False,
                severity=ValidationLevel.ERROR,
                message=f"Missing required documents: {', '.join(missing_documents)}",
                compliance_standard=ComplianceStandard.CODIGO_COMERCIO,
                remediation_suggestion="Collect all required documents before proceeding",
                metadata={"missing_documents": missing_documents}
            ))

        # Rule: Admin security level for approval
        vendor_category = vendor_data.get("categoria", "")
        admin_security_level = admin_data.get("security_clearance_level", 0)

        # High-value categories require higher security level
        high_value_categories = ["electronicos", "hogar"]
        required_security_level = 4 if vendor_category in high_value_categories else 3

        if admin_security_level < required_security_level:
            results.append(ValidationResult(
                rule_id="VEN_002",
                rule_name="Admin Security Level Requirement",
                passed=False,
                severity=ValidationLevel.ERROR,
                message=f"Category '{vendor_category}' requires security level {required_security_level}+",
                compliance_standard=None,
                remediation_suggestion="Escalate approval to higher-level administrator",
                metadata={
                    "vendor_category": vendor_category,
                    "admin_security_level": admin_security_level,
                    "required_security_level": required_security_level
                }
            ))

        # Rule: Regional jurisdiction validation
        vendor_department = vendor_data.get("departamento", "")
        admin_department = admin_data.get("department_id", "")

        if vendor_department != admin_department and admin_data.get("user_type") != "SUPERUSER":
            results.append(ValidationResult(
                rule_id="VEN_003",
                rule_name="Regional Jurisdiction Check",
                passed=False,
                severity=ValidationLevel.WARNING,
                message="Cross-regional vendor approval may require additional validation",
                compliance_standard=None,
                remediation_suggestion="Coordinate with regional administrator or escalate to SUPERUSER",
                metadata={
                    "vendor_department": vendor_department,
                    "admin_department": admin_department
                }
            ))

        # Rule: Compliance with Colombian tax requirements
        documento_tipo = vendor_data.get("documento_tipo", "")
        documento_numero = vendor_data.get("documento_numero", "")

        if documento_tipo == "NIT":
            nit_validation = ColombianDocumentValidator.validate_nit(documento_numero)
            if not nit_validation.passed:
                results.append(nit_validation)
        elif documento_tipo == "CC":
            cedula_validation = ColombianDocumentValidator.validate_cedula(documento_numero)
            if not cedula_validation.passed:
                results.append(cedula_validation)

        # If no issues found, add success result
        if not any(result.severity in [ValidationLevel.ERROR, ValidationLevel.CRITICAL] for result in results):
            results.append(ValidationResult(
                rule_id="VEN_000",
                rule_name="Vendor Approval Validation",
                passed=True,
                severity=ValidationLevel.INFO,
                message="Vendor approval follows all business rules",
                compliance_standard=None,
                remediation_suggestion=None,
                metadata={"validation_passed": True}
            ))

        return results


class ComprehensiveBusinessRulesValidator:
    """Main validator orchestrating all business rule validations."""

    def __init__(self):
        self.document_validator = ColombianDocumentValidator()
        self.permission_validator = AdminPermissionValidator()
        self.vendor_validator = VendorManagementValidator()
        self.time_validator = TimeValidator()

    def validate_admin_operation(self, operation_type: str, operation_data: Dict[str, Any],
                                admin_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive validation of admin operations.

        Args:
            operation_type: Type of operation being performed
            operation_data: Data related to the operation
            admin_data: Data about the admin performing the operation

        Returns:
            Comprehensive validation results
        """
        all_results = []
        operation_time = ColombianTimeManager.get_current_colombia_time()

        # Time-based validation
        time_validation = self.time_validator.validate_business_hours_operation(
            operation_time, operation_type, admin_data.get("persona")
        )

        if not time_validation["validation_passed"]:
            all_results.append(ValidationResult(
                rule_id="TIME_001",
                rule_name="Business Hours Validation",
                passed=False,
                severity=ValidationLevel.WARNING,
                message="Operation performed outside standard business hours",
                compliance_standard=None,
                remediation_suggestion="Consider rescheduling to business hours unless urgent",
                metadata=time_validation
            ))

        # Operation-specific validations
        if operation_type == "create_admin":
            all_results.extend(
                self.permission_validator.validate_permission_assignment(
                    operation_data, {}, admin_data
                )
            )

        elif operation_type == "bulk_admin_action":
            all_results.extend(
                self.permission_validator.validate_bulk_operation(operation_data, admin_data)
            )

        elif operation_type == "vendor_approval":
            all_results.extend(
                self.vendor_validator.validate_vendor_approval_workflow(operation_data, admin_data)
            )

        # Categorize results
        errors = [r for r in all_results if r.severity == ValidationLevel.ERROR]
        warnings = [r for r in all_results if r.severity == ValidationLevel.WARNING]
        critical = [r for r in all_results if r.severity == ValidationLevel.CRITICAL]
        info = [r for r in all_results if r.severity == ValidationLevel.INFO]

        return {
            "operation_type": operation_type,
            "operation_time": operation_time.isoformat(),
            "admin_persona": admin_data.get("persona", "unknown"),
            "validation_summary": {
                "total_rules_checked": len(all_results),
                "critical_issues": len(critical),
                "errors": len(errors),
                "warnings": len(warnings),
                "info": len(info),
                "overall_passed": len(critical) == 0 and len(errors) == 0
            },
            "validation_results": {
                "critical": [r.__dict__ for r in critical],
                "errors": [r.__dict__ for r in errors],
                "warnings": [r.__dict__ for r in warnings],
                "info": [r.__dict__ for r in info]
            },
            "recommendations": [
                r.remediation_suggestion for r in all_results
                if r.remediation_suggestion and r.severity in [ValidationLevel.ERROR, ValidationLevel.CRITICAL]
            ]
        }


# Export key classes and functions
__all__ = [
    "ValidationLevel",
    "ComplianceStandard",
    "ValidationRule",
    "ValidationResult",
    "ColombianDocumentValidator",
    "AdminPermissionValidator",
    "VendorManagementValidator",
    "ComprehensiveBusinessRulesValidator"
]