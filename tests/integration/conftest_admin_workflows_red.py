"""
🚨 RED PHASE: Integration Fixtures for Admin Workflow Testing - SQUAD 2

MISSION: Provide comprehensive fixtures for admin workflow integration testing
TARGET: Support complex workflow scenarios for RED phase testing
FOCUS: Mock objects, database sessions, and workflow components

These fixtures support RED phase testing by providing realistic mock objects
and test data that will trigger failures in unimplemented workflow components.

Integration Fixture Scope:
- Admin workflow mock objects
- Quality assessment test data
- Photo upload simulation
- Database session management
- Performance testing utilities

Author: Integration Testing Specialist (Squad 2 Leader)
Date: 2025-09-21
Phase: RED (Test-Driven Development)
Purpose: Support comprehensive integration testing
"""

import pytest
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from unittest.mock import Mock, AsyncMock, MagicMock
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile
from PIL import Image
import io

from app.models.user import User, UserType
from app.models.incoming_product_queue import IncomingProductQueue, VerificationStatus, QueuePriority
from app.services.product_verification_workflow import (
    ProductVerificationWorkflow,
    VerificationStep,
    StepResult,
    ProductRejection,
    RejectionReason
)


# ================================================================================================
# ADMIN USER FIXTURES
# ================================================================================================

@pytest.fixture
def mock_admin_user():
    """Mock admin user with full permissions for workflow testing"""
    admin = Mock(spec=User)
    admin.id = str(uuid.uuid4())
    admin.email = "admin@mestore.test"
    admin.nombre = "Admin"
    admin.apellido = "User"
    admin.user_type = UserType.ADMIN
    admin.is_superuser = True
    admin.security_clearance_level = 4
    admin.is_active = True
    admin.is_verified = True
    return admin

@pytest.fixture
def mock_superuser():
    """Mock superuser with maximum permissions"""
    superuser = Mock(spec=User)
    superuser.id = str(uuid.uuid4())
    superuser.email = "superuser@mestore.test"
    superuser.nombre = "Super"
    superuser.apellido = "User"
    superuser.user_type = UserType.SUPERUSER
    superuser.is_superuser = True
    superuser.security_clearance_level = 5
    superuser.is_active = True
    superuser.is_verified = True
    return superuser

@pytest.fixture
def mock_basic_admin():
    """Mock basic admin with limited permissions"""
    basic_admin = Mock(spec=User)
    basic_admin.id = str(uuid.uuid4())
    basic_admin.email = "basic.admin@mestore.test"
    basic_admin.user_type = UserType.ADMIN
    basic_admin.is_superuser = False
    basic_admin.security_clearance_level = 2
    basic_admin.is_active = True
    basic_admin.is_verified = True
    return basic_admin


# ================================================================================================
# INCOMING PRODUCT QUEUE FIXTURES
# ================================================================================================

@pytest.fixture
def mock_incoming_product_queue():
    """Mock incoming product queue item in various states"""
    queue_item = Mock(spec=IncomingProductQueue)
    queue_item.id = uuid.uuid4()
    queue_item.product_id = str(uuid.uuid4())
    queue_item.vendor_id = str(uuid.uuid4())
    queue_item.tracking_number = f"TR{uuid.uuid4().hex[:8].upper()}"
    queue_item.verification_status = VerificationStatus.PENDING
    queue_item.priority = QueuePriority.NORMAL
    queue_item.quality_score = None
    queue_item.verification_notes = None
    queue_item.quality_issues = None
    queue_item.assigned_to = None
    queue_item.assigned_at = None
    queue_item.processing_started_at = None
    queue_item.processing_completed_at = None
    queue_item.verification_attempts = 0
    queue_item.created_at = datetime.now()
    queue_item.updated_at = datetime.now()

    # Mock vendor relationship
    queue_item.vendor = Mock()
    queue_item.vendor.id = queue_item.vendor_id
    queue_item.vendor.email = "vendor@test.com"
    queue_item.vendor.telefono = "+57123456789"
    queue_item.vendor.nombre = "Test Vendor"

    return queue_item

@pytest.fixture
def mock_quality_check_queue():
    """Mock queue item ready for quality check"""
    queue_item = Mock(spec=IncomingProductQueue)
    queue_item.id = uuid.uuid4()
    queue_item.verification_status = VerificationStatus.QUALITY_CHECK
    queue_item.tracking_number = f"QC{uuid.uuid4().hex[:6].upper()}"
    queue_item.vendor_id = str(uuid.uuid4())
    queue_item.assigned_to = str(uuid.uuid4())
    queue_item.assigned_at = datetime.now() - timedelta(hours=1)
    queue_item.processing_started_at = datetime.now() - timedelta(minutes=30)
    queue_item.verification_attempts = 1
    return queue_item

@pytest.fixture
def mock_approved_queue():
    """Mock queue item that has been approved"""
    queue_item = Mock(spec=IncomingProductQueue)
    queue_item.id = uuid.uuid4()
    queue_item.verification_status = VerificationStatus.APPROVED
    queue_item.tracking_number = f"AP{uuid.uuid4().hex[:6].upper()}"
    queue_item.quality_score = 8
    queue_item.verification_notes = "Product approved after quality assessment"
    queue_item.processing_completed_at = datetime.now()
    return queue_item

@pytest.fixture
def mock_rejected_queue():
    """Mock queue item that has been rejected"""
    queue_item = Mock(spec=IncomingProductQueue)
    queue_item.id = uuid.uuid4()
    queue_item.verification_status = VerificationStatus.REJECTED
    queue_item.tracking_number = f"RJ{uuid.uuid4().hex[:6].upper()}"
    queue_item.quality_score = 3
    queue_item.quality_issues = "Multiple defects identified"
    queue_item.verification_notes = "Product rejected due to quality issues"
    queue_item.processing_completed_at = datetime.now()
    return queue_item


# ================================================================================================
# PHOTO UPLOAD FIXTURES
# ================================================================================================

@pytest.fixture
def mock_upload_files():
    """Mock list of upload files for photo verification"""
    upload_files = []
    photo_types = ["general", "damage", "label", "packaging"]

    for i, photo_type in enumerate(photo_types):
        # Create realistic image data
        img = Image.new('RGB', (800, 600), color=(100 + i*50, 150, 200))
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG', quality=85)
        img_bytes.seek(0)

        upload_file = Mock(spec=UploadFile)
        upload_file.filename = f"verification_{photo_type}_{i}.jpg"
        upload_file.content_type = "image/jpeg"
        upload_file.size = len(img_bytes.getvalue())
        upload_file.read = AsyncMock(return_value=img_bytes.getvalue())
        upload_files.append(upload_file)

    return upload_files

@pytest.fixture
def mock_large_upload_files():
    """Mock large upload files for performance testing"""
    large_files = []

    for i in range(20):  # 20 large files
        # Create large image for performance testing
        large_img = Image.new('RGB', (3000, 2000), color=(i*10, 100, 150))
        img_bytes = io.BytesIO()
        large_img.save(img_bytes, format='JPEG', quality=100)
        img_bytes.seek(0)

        upload_file = Mock(spec=UploadFile)
        upload_file.filename = f"large_verification_{i}.jpg"
        upload_file.content_type = "image/jpeg"
        upload_file.size = len(img_bytes.getvalue())
        upload_file.read = AsyncMock(return_value=img_bytes.getvalue())
        large_files.append(upload_file)

    return large_files

@pytest.fixture
def mock_invalid_upload_files():
    """Mock invalid upload files for error testing"""
    invalid_files = []

    # File with wrong content type
    text_file = Mock(spec=UploadFile)
    text_file.filename = "document.txt"
    text_file.content_type = "text/plain"
    text_file.read = AsyncMock(return_value=b"This is not an image")
    invalid_files.append(text_file)

    # File too large
    large_file = Mock(spec=UploadFile)
    large_file.filename = "too_large.jpg"
    large_file.content_type = "image/jpeg"
    large_file.read = AsyncMock(return_value=b"x" * (11 * 1024 * 1024))  # 11MB
    invalid_files.append(large_file)

    # Corrupted image file
    corrupted_file = Mock(spec=UploadFile)
    corrupted_file.filename = "corrupted.jpg"
    corrupted_file.content_type = "image/jpeg"
    corrupted_file.read = AsyncMock(return_value=b"corrupted_image_data")
    invalid_files.append(corrupted_file)

    return invalid_files


# ================================================================================================
# QUALITY ASSESSMENT FIXTURES
# ================================================================================================

@pytest.fixture
def mock_quality_checklist_valid():
    """Mock valid quality checklist data"""
    return {
        "inspector_id": str(uuid.uuid4()),
        "inspection_duration_minutes": 30,
        "quality_score": 8,
        "overall_condition": "good",
        "has_damage": False,
        "has_missing_parts": False,
        "has_defects": False,
        "inspector_notes": "Product in excellent condition",
        "approved": True,
        "compliance_checked": True,
        "safety_verified": True,
        "documentation_complete": True
    }

@pytest.fixture
def mock_quality_checklist_invalid():
    """Mock invalid quality checklist data for validation testing"""
    return {
        "inspector_id": str(uuid.uuid4()),
        "inspection_duration_minutes": -5,  # Invalid: negative duration
        "quality_score": 15,  # Invalid: above maximum
        "overall_condition": "unknown",  # Invalid: not in enum
        "has_damage": True,
        "damage_severity": None,  # Invalid: required when has_damage is True
        "has_missing_parts": False,
        "missing_parts_list": ["part1"],  # Invalid: list when has_missing_parts is False
        "inspector_notes": "",  # Invalid: empty when issues present
        "approved": True,  # Invalid: can't approve with damage
    }

@pytest.fixture
def mock_quality_checklist_complex():
    """Mock complex quality checklist with advanced validation"""
    return {
        "inspector_id": str(uuid.uuid4()),
        "inspection_duration_minutes": 45,
        "quality_score": None,  # To be calculated
        "material_quality": 9,
        "manufacturing_precision": 8,
        "packaging_condition": 7,
        "documentation_completeness": 10,
        "regulatory_compliance": 9,
        "brand_authenticity": 10,
        "functional_testing": 8,
        "aesthetic_condition": 6,
        "vendor_history_factor": 8.5,
        "product_category_weights": {
            "electronics": 0.3,
            "luxury": 0.2,
            "safety_critical": 0.5
        },
        "compliance_standards": {
            "iso_certified": True,
            "ce_marking": True,
            "fcc_approved": True
        },
        "test_results": {
            "electrical_safety": "passed",
            "material_composition": {"primary": "aluminum", "secondary": "plastic"},
            "performance_metrics": [8.5, 9.0, 7.5]
        },
        "inspector_notes": "Complex multi-factor assessment completed",
        "approved": None  # To be determined by algorithm
    }


# ================================================================================================
# WORKFLOW FIXTURES
# ================================================================================================

@pytest.fixture
def mock_verification_workflow():
    """Mock ProductVerificationWorkflow for testing"""
    workflow = Mock(spec=ProductVerificationWorkflow)
    workflow.queue_item = Mock(spec=IncomingProductQueue)
    workflow.get_current_step = Mock(return_value=VerificationStep.INITIAL_INSPECTION)
    workflow.execute_step = Mock(return_value=False)  # Fail by default in RED phase
    workflow.get_workflow_progress = Mock(return_value={
        "current_step": "initial_inspection",
        "completed_steps": [],
        "total_steps": 6,
        "progress_percentage": 0
    })
    workflow.reject_product = AsyncMock(return_value=False)
    workflow.approve_product = AsyncMock(return_value=False)
    workflow.auto_assign_location = AsyncMock(return_value={
        "success": False,
        "message": "Location assignment not implemented",
        "location": None
    })
    return workflow

@pytest.fixture
def mock_verification_step_result():
    """Mock StepResult for workflow testing"""
    return StepResult(
        passed=False,  # Fail by default in RED phase
        notes="Test step execution",
        issues=["Implementation not complete"],
        metadata={"test": True}
    )

@pytest.fixture
def mock_product_rejection():
    """Mock ProductRejection for testing"""
    rejection = Mock()
    rejection.reason = RejectionReason.QUALITY_ISSUES
    rejection.description = "Test rejection description"
    rejection.quality_score = 3
    rejection.evidence_photos = ["test_photo1.jpg", "test_photo2.jpg"]
    rejection.inspector_notes = "Test rejection notes"
    rejection.can_appeal = True
    rejection.appeal_deadline = datetime.now() + timedelta(days=7)
    return rejection


# ================================================================================================
# DATABASE SESSION FIXTURES
# ================================================================================================

@pytest.fixture
def mock_async_db_session():
    """Mock async database session for testing"""
    session = Mock(spec=AsyncSession)
    session.execute = AsyncMock(return_value=Mock())
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    return session

@pytest.fixture
def mock_sync_db_session():
    """Mock sync database session for testing"""
    session = Mock(spec=Session)
    session.query = Mock()
    session.commit = Mock()
    session.rollback = Mock()
    session.close = Mock()
    return session

@pytest.fixture
def mock_failing_db_session():
    """Mock database session that fails operations"""
    session = Mock(spec=AsyncSession)
    session.execute = AsyncMock(side_effect=Exception("Database connection failed"))
    session.commit = AsyncMock(side_effect=Exception("Commit failed"))
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    return session


# ================================================================================================
# PERFORMANCE TESTING FIXTURES
# ================================================================================================

@pytest.fixture
def large_dataset_queue_items():
    """Generate large dataset of queue items for performance testing"""
    items = []
    for i in range(1000):  # 1000 items for stress testing
        item = Mock(spec=IncomingProductQueue)
        item.id = i
        item.tracking_number = f"TR{i:06d}"
        item.verification_status = VerificationStatus.PENDING
        item.priority = QueuePriority.NORMAL if i % 5 != 0 else QueuePriority.HIGH
        item.quality_score = (i % 10) + 1
        item.verification_attempts = (i % 3) + 1
        item.vendor_id = str(uuid.uuid4())
        item.created_at = datetime.now() - timedelta(days=i % 30)
        item.updated_at = datetime.now() - timedelta(hours=i % 24)
        items.append(item)
    return items

@pytest.fixture
def performance_timer():
    """Performance timing utility for tests"""
    class PerformanceTimer:
        def __init__(self):
            self.start_time = None
            self.end_time = None

        def start(self):
            self.start_time = datetime.now()

        def stop(self):
            self.end_time = datetime.now()

        def elapsed_seconds(self):
            if self.start_time and self.end_time:
                return (self.end_time - self.start_time).total_seconds()
            return None

        def assert_under_threshold(self, threshold_seconds):
            elapsed = self.elapsed_seconds()
            if elapsed and elapsed > threshold_seconds:
                raise AssertionError(f"Performance threshold exceeded: {elapsed}s > {threshold_seconds}s")

    return PerformanceTimer()


# ================================================================================================
# VALIDATION AND ERROR TESTING FIXTURES
# ================================================================================================

@pytest.fixture
def mock_business_rule_violations():
    """Mock data that violates business rules"""
    return {
        "quality_score_vs_approval": {
            "quality_score": 2,  # Very low
            "approved": True,    # But approved - violation
            "override_reason": None  # No override
        },
        "inspector_qualification": {
            "inspector_qualification": "basic",
            "product_category": "luxury",  # Basic inspector for luxury - violation
            "quality_score": 6  # Below luxury threshold
        },
        "vendor_tier_mismatch": {
            "vendor_tier": "premium",
            "quality_score": 4,  # Premium vendor with low quality - violation
            "approved": True
        }
    }

@pytest.fixture
def mock_concurrent_access_scenario():
    """Mock scenario for testing concurrent access"""
    scenario = {
        "admin1_id": str(uuid.uuid4()),
        "admin2_id": str(uuid.uuid4()),
        "queue_id": uuid.uuid4(),
        "simultaneous_actions": ["approve", "reject"],
        "expected_conflict": True
    }
    return scenario

@pytest.fixture
def mock_audit_trail_requirements():
    """Mock audit trail requirements for compliance testing"""
    return {
        "required_fields": [
            "inspector_certification",
            "witness_signatures",
            "assessment_photos",
            "measurement_data",
            "compliance_documentation"
        ],
        "regulatory_standards": ["ISO9001", "CE", "FCC"],
        "audit_level": "full",
        "retention_period_days": 2555,  # 7 years
        "encryption_required": True,
        "access_logging": True
    }


# ================================================================================================
# UTILITY FIXTURES
# ================================================================================================

@pytest.fixture
def uuid_generator():
    """UUID generator utility for tests"""
    def generate_uuid():
        return str(uuid.uuid4())
    return generate_uuid

@pytest.fixture
def datetime_utils():
    """Datetime utility functions for tests"""
    class DateTimeUtils:
        @staticmethod
        def days_ago(days):
            return datetime.now() - timedelta(days=days)

        @staticmethod
        def hours_ago(hours):
            return datetime.now() - timedelta(hours=hours)

        @staticmethod
        def minutes_ago(minutes):
            return datetime.now() - timedelta(minutes=minutes)

        @staticmethod
        def future_datetime(days):
            return datetime.now() + timedelta(days=days)

    return DateTimeUtils()

@pytest.fixture
def red_phase_marker():
    """Marker to identify RED phase tests"""
    return {
        "phase": "RED",
        "expected_outcome": "FAILURE",
        "purpose": "Drive implementation through failing tests",
        "squad": "Squad 2 - Integration Testing",
        "coverage_target": "Lines 451-900+ of admin.py"
    }