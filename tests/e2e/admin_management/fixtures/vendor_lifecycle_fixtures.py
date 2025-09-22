# ~/tests/e2e/admin_management/fixtures/vendor_lifecycle_fixtures.py
# Vendor Lifecycle Fixtures for E2E Testing
# Complete vendor journey data for admin management workflows

"""
Vendor Lifecycle Fixtures for E2E Testing.

This module provides comprehensive vendor lifecycle data for testing
admin management workflows in vendor onboarding and management scenarios.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from enum import Enum
import uuid
from dataclasses import dataclass, field

from .colombian_business_data import (
    ColombianBusinessDataFactory,
    COLOMBIAN_DEPARTMENTS,
    VENDOR_CATEGORIES,
    COLOMBIA_TZ
)


class VendorStatus(Enum):
    """Vendor status enum for lifecycle management."""
    PENDING = "PENDING"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    SUSPENDED = "SUSPENDED"
    DEACTIVATED = "DEACTIVATED"


class VendorCategory(Enum):
    """Vendor category enum."""
    MODA = "moda"
    ELECTRONICOS = "electronicos"
    HOGAR = "hogar"
    DEPORTES = "deportes"
    ALIMENTACION = "alimentacion"


@dataclass
class VendorWorkflowStage:
    """Vendor workflow stage data."""
    stage_name: str
    required_documents: List[str]
    approval_criteria: List[str]
    estimated_duration_hours: int
    responsible_admin_level: int


@dataclass
class VendorTestProfile:
    """Complete vendor test profile for E2E scenarios."""
    vendor_id: str
    business_name: str
    email: str
    owner_name: str
    documento_tipo: str
    documento_numero: str
    telefono: str
    departamento: str
    ciudad: str
    categoria: str
    subcategoria: str
    status: VendorStatus
    registration_date: datetime
    approval_date: Optional[datetime] = None
    products_count: int = 0
    monthly_sales: float = 0.0
    performance_score: int = 80
    compliance_issues: List[str] = field(default_factory=list)
    admin_notes: List[str] = field(default_factory=list)


# Vendor Workflow Stages
VENDOR_WORKFLOW_STAGES = {
    "registration": VendorWorkflowStage(
        stage_name="Initial Registration",
        required_documents=["CC/NIT", "RUT", "Banking Information"],
        approval_criteria=["Valid documentation", "Clean background check"],
        estimated_duration_hours=24,
        responsible_admin_level=2
    ),
    "documentation_review": VendorWorkflowStage(
        stage_name="Documentation Review",
        required_documents=["Business License", "Tax Certificate", "Product Catalog"],
        approval_criteria=["Complete documentation", "Legal compliance"],
        estimated_duration_hours=48,
        responsible_admin_level=3
    ),
    "compliance_check": VendorWorkflowStage(
        stage_name="Compliance Verification",
        required_documents=["Quality Certificates", "Insurance Policy"],
        approval_criteria=["Regulatory compliance", "Quality standards"],
        estimated_duration_hours=72,
        responsible_admin_level=3
    ),
    "final_approval": VendorWorkflowStage(
        stage_name="Final Approval",
        required_documents=["All previous documents verified"],
        approval_criteria=["Admin interview passed", "Platform training completed"],
        estimated_duration_hours=24,
        responsible_admin_level=4
    )
}


class VendorLifecycleFactory:
    """Factory for generating vendor lifecycle test data."""

    @staticmethod
    def create_vendor_batch(department: str, category: str, count: int,
                          status_distribution: Dict[VendorStatus, float] = None) -> List[VendorTestProfile]:
        """
        Create a batch of vendors with realistic distribution across statuses.

        Args:
            department: Colombian department code
            category: Vendor category
            count: Number of vendors to create
            status_distribution: Distribution of statuses (defaults to realistic distribution)
        """
        if status_distribution is None:
            status_distribution = {
                VendorStatus.APPROVED: 0.60,      # 60% approved
                VendorStatus.PENDING: 0.20,       # 20% pending
                VendorStatus.UNDER_REVIEW: 0.10,  # 10% under review
                VendorStatus.REJECTED: 0.05,      # 5% rejected
                VendorStatus.SUSPENDED: 0.05      # 5% suspended
            }

        vendors = []
        dept_data = COLOMBIAN_DEPARTMENTS[department]
        category_data = VENDOR_CATEGORIES[category]

        # Calculate vendor counts per status
        status_counts = {}
        remaining = count
        for status, percentage in status_distribution.items():
            if status == list(status_distribution.keys())[-1]:  # Last status gets remaining
                status_counts[status] = remaining
            else:
                status_count = int(count * percentage)
                status_counts[status] = status_count
                remaining -= status_count

        # Generate vendors for each status
        vendor_index = 0
        for status, status_count in status_counts.items():
            for i in range(status_count):
                vendor = VendorLifecycleFactory.create_single_vendor(
                    department=department,
                    category=category,
                    index=vendor_index,
                    status=status
                )
                vendors.append(vendor)
                vendor_index += 1

        return vendors

    @staticmethod
    def create_single_vendor(department: str, category: str, index: int,
                           status: VendorStatus = VendorStatus.PENDING) -> VendorTestProfile:
        """Create a single vendor with realistic data."""
        dept_data = COLOMBIAN_DEPARTMENTS[department]
        category_data = VENDOR_CATEGORIES[category]

        vendor_id = str(uuid.uuid4())
        registration_date = ColombianBusinessDataFactory.get_current_colombia_time() - timedelta(days=index*3)

        # Determine approval date based on status
        approval_date = None
        if status in [VendorStatus.APPROVED, VendorStatus.SUSPENDED]:
            approval_date = registration_date + timedelta(days=7)

        # Generate realistic business name
        subcategory = category_data["subcategories"][index % len(category_data["subcategories"])]
        city = dept_data.major_cities[index % len(dept_data.major_cities)]
        business_name = f"{subcategory} {city} {index+1:03d}"

        # Performance metrics based on status
        performance_score = 80
        products_count = 0
        monthly_sales = 0.0

        if status == VendorStatus.APPROVED:
            performance_score = 85 + (index % 15)  # 85-99
            products_count = 5 + (index % 20)      # 5-24 products
            monthly_sales = 500000 + (index * 50000)  # Colombian pesos
        elif status == VendorStatus.SUSPENDED:
            performance_score = 40 + (index % 20)  # 40-59
            products_count = 2 + (index % 8)       # 2-9 products
            monthly_sales = 100000 + (index * 10000)

        # Generate compliance issues based on status
        compliance_issues = []
        if status == VendorStatus.REJECTED:
            compliance_issues = ["Documentación incompleta", "Verificación de identidad fallida"]
        elif status == VendorStatus.SUSPENDED:
            compliance_issues = ["Quejas de calidad", "Retraso en entregas"]

        return VendorTestProfile(
            vendor_id=vendor_id,
            business_name=business_name,
            email=f"vendor.{category}.{department}.{index+1:03d}@example.com",
            owner_name=f"Propietario {index+1:03d}",
            documento_tipo="NIT" if index % 3 == 0 else "CC",
            documento_numero=f"90012345{index:03d}" if index % 3 == 0 else f"10123456{index:03d}",
            telefono=f"+57 30{index%10} {100+index:03d} {1000+index:04d}",
            departamento=dept_data.name,
            ciudad=city,
            categoria=category,
            subcategoria=subcategory,
            status=status,
            registration_date=registration_date,
            approval_date=approval_date,
            products_count=products_count,
            monthly_sales=monthly_sales,
            performance_score=performance_score,
            compliance_issues=compliance_issues,
            admin_notes=VendorLifecycleFactory._generate_admin_notes(status, index)
        )

    @staticmethod
    def _generate_admin_notes(status: VendorStatus, index: int) -> List[str]:
        """Generate realistic admin notes based on vendor status."""
        base_date = ColombianBusinessDataFactory.get_current_colombia_time() - timedelta(days=index*2)

        notes = [f"Registro inicial completado - {base_date.strftime('%Y-%m-%d %H:%M')}"]

        if status == VendorStatus.UNDER_REVIEW:
            notes.append(f"Revisión de documentos iniciada - {(base_date + timedelta(days=1)).strftime('%Y-%m-%d %H:%M')}")
        elif status == VendorStatus.APPROVED:
            notes.extend([
                f"Documentos verificados - {(base_date + timedelta(days=2)).strftime('%Y-%m-%d %H:%M')}",
                f"Entrevista completada satisfactoriamente - {(base_date + timedelta(days=5)).strftime('%Y-%m-%d %H:%M')}",
                f"Aprobación final otorgada - {(base_date + timedelta(days=7)).strftime('%Y-%m-%d %H:%M')}"
            ])
        elif status == VendorStatus.REJECTED:
            notes.extend([
                f"Problemas en documentación detectados - {(base_date + timedelta(days=2)).strftime('%Y-%m-%d %H:%M')}",
                f"Solicitud rechazada - {(base_date + timedelta(days=5)).strftime('%Y-%m-%d %H:%M')}"
            ])
        elif status == VendorStatus.SUSPENDED:
            notes.extend([
                f"Quejas de usuarios reportadas - {(base_date + timedelta(days=10)).strftime('%Y-%m-%d %H:%M')}",
                f"Suspensión temporal aplicada - {(base_date + timedelta(days=15)).strftime('%Y-%m-%d %H:%M')}"
            ])

        return notes

    @staticmethod
    def create_bulk_onboarding_scenario(department: str, vendor_count: int = 20) -> Dict[str, Any]:
        """
        Create a bulk vendor onboarding scenario for testing admin workflows.

        This simulates a situation where an admin needs to process multiple
        vendor applications simultaneously.
        """
        # Mix of categories for realistic scenario
        categories = list(VENDOR_CATEGORIES.keys())
        vendors_per_category = vendor_count // len(categories)

        all_vendors = []
        for i, category in enumerate(categories):
            count = vendors_per_category + (1 if i < vendor_count % len(categories) else 0)
            category_vendors = VendorLifecycleFactory.create_vendor_batch(
                department=department,
                category=category,
                count=count,
                status_distribution={
                    VendorStatus.PENDING: 0.70,      # 70% pending - need processing
                    VendorStatus.UNDER_REVIEW: 0.30  # 30% under review
                }
            )
            all_vendors.extend(category_vendors)

        return {
            "scenario_name": "Bulk Vendor Onboarding",
            "department": department,
            "total_vendors": len(all_vendors),
            "vendors": all_vendors,
            "processing_timeline": {
                "estimated_hours": len(all_vendors) * 2,  # 2 hours per vendor
                "stages": list(VENDOR_WORKFLOW_STAGES.keys()),
                "admin_workload": "HIGH"
            },
            "success_criteria": {
                "approval_rate_target": 0.85,  # 85% approval target
                "processing_time_max_hours": 72,
                "quality_score_min": 90
            }
        }

    @staticmethod
    def create_vendor_performance_crisis() -> Dict[str, Any]:
        """
        Create a vendor performance crisis scenario for testing admin response.

        This simulates multiple vendors having performance issues simultaneously
        requiring immediate admin intervention.
        """
        crisis_vendors = []

        # Create problematic vendors across different departments
        departments = ["cundinamarca", "antioquia", "valle_del_cauca"]

        for i, dept in enumerate(departments):
            # Create vendors with different crisis types
            for j in range(3):  # 3 vendors per department
                vendor = VendorLifecycleFactory.create_single_vendor(
                    department=dept,
                    category=list(VENDOR_CATEGORIES.keys())[j % len(VENDOR_CATEGORIES)],
                    index=i*3 + j,
                    status=VendorStatus.APPROVED
                )

                # Add crisis-specific data
                vendor.performance_score = 25 + (j * 10)  # Low performance
                vendor.compliance_issues = [
                    "Alto número de quejas de clientes",
                    "Productos defectuosos reportados",
                    "Incumplimiento en tiempos de entrega",
                    "Comunicación deficiente con clientes"
                ][:(j+1)]

                vendor.admin_notes.extend([
                    f"CRISIS: Múltiples quejas recibidas en las últimas 24 horas",
                    f"URGENTE: Requiere intervención inmediata del administrador",
                    f"IMPACTO: Afectando reputación de la plataforma"
                ])

                crisis_vendors.append(vendor)

        return {
            "scenario_name": "Vendor Performance Crisis",
            "crisis_type": "PERFORMANCE_DEGRADATION",
            "affected_vendors": crisis_vendors,
            "crisis_metrics": {
                "customer_complaints": 45,
                "refund_requests": 23,
                "platform_reputation_impact": "HIGH",
                "estimated_revenue_loss": 2500000  # Colombian pesos
            },
            "required_actions": [
                "Immediate vendor contact and investigation",
                "Temporary suspension of problematic vendors",
                "Customer communication and refund processing",
                "Root cause analysis and prevention measures",
                "Performance improvement plan implementation"
            ],
            "success_criteria": {
                "response_time_max_hours": 6,
                "customer_satisfaction_recovery": 0.90,
                "vendor_performance_improvement": 0.80
            }
        }

    @staticmethod
    def create_regional_expansion_scenario() -> Dict[str, Any]:
        """
        Create a regional expansion scenario for testing admin scalability.

        This simulates expanding operations to new Colombian departments
        with coordinated vendor onboarding.
        """
        new_departments = ["huila", "tolima", "caldas"]
        expansion_data = {}

        for dept in new_departments:
            # Create initial vendor batch for new department
            vendors = []
            for category in VENDOR_CATEGORIES.keys():
                category_vendors = VendorLifecycleFactory.create_vendor_batch(
                    department=dept,
                    category=category,
                    count=8,  # 8 vendors per category per department
                    status_distribution={
                        VendorStatus.PENDING: 1.0  # All new, need processing
                    }
                )
                vendors.extend(category_vendors)

            expansion_data[dept] = {
                "vendors": vendors,
                "launch_date": ColombianBusinessDataFactory.get_current_colombia_time() + timedelta(weeks=4),
                "target_metrics": {
                    "active_vendors": 35,
                    "categories_covered": 5,
                    "monthly_gmv_target": 50000000  # 50M Colombian pesos
                },
                "required_admin_resources": {
                    "new_admins_needed": 2,
                    "training_hours": 40,
                    "admin_security_level": 3
                }
            }

        return {
            "scenario_name": "Regional Expansion",
            "expansion_type": "MULTI_DEPARTMENT",
            "new_departments": new_departments,
            "department_data": expansion_data,
            "coordination_requirements": {
                "total_new_vendors": sum(len(data["vendors"]) for data in expansion_data.values()),
                "cross_department_admin_coordination": True,
                "centralized_approval_workflow": True,
                "performance_monitoring": "REAL_TIME"
            },
            "success_criteria": {
                "vendor_onboarding_completion": 0.90,
                "admin_efficiency_target": 0.85,
                "regional_launch_on_time": True,
                "quality_standards_maintained": True
            }
        }


# Export key classes and functions
__all__ = [
    "VendorStatus",
    "VendorCategory",
    "VendorWorkflowStage",
    "VendorTestProfile",
    "VendorLifecycleFactory",
    "VENDOR_WORKFLOW_STAGES"
]