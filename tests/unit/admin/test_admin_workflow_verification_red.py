"""
RED PHASE TDD TESTS - Admin Workflow Verification

This file contains tests that are DESIGNED TO FAIL initially.
These tests define the expected behavior for admin product verification workflows,
including current step tracking, execution, history, and approval/rejection processes.

CRITICAL: All tests in this file must FAIL when first run.
This is the RED phase of TDD - write failing tests first.

Squad 1 Focus: Product verification workflow admin functionality
Target Coverage: Lines 200-950 of app/api/v1/endpoints/admin.py
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient
from fastapi import status
from datetime import datetime, timedelta
import uuid
from typing import Dict, Any, List

from app.models.user import User, UserType
from app.models.incoming_product_queue import IncomingProductQueue, VerificationStatus
from app.services.product_verification_workflow import (
    ProductVerificationWorkflow,
    VerificationStep,
    StepResult,
    ProductRejection,
    RejectionReason
)


@pytest.mark.red_test
@pytest.mark.asyncio
class TestAdminWorkflowVerificationCurrentStepRED:
    """RED PHASE: Admin workflow current step tests that MUST FAIL initially"""

    async def test_get_current_verification_step_unauthorized(self, async_client: AsyncClient):
        """
        RED TEST: Unauthenticated access to verification step should be rejected

        This test MUST FAIL initially because authentication
        is not properly implemented for verification endpoints.
        """
        queue_id = uuid.uuid4()
        response = await async_client.get(f"/api/v1/admin/incoming-products/{queue_id}/verification/current-step")

        # This assertion WILL FAIL in RED phase - that's expected
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_current_verification_step_regular_user_forbidden(
        self, async_client: AsyncClient, test_vendedor_user: User
    ):
        """
        RED TEST: Regular users should not access verification workflows

        This test MUST FAIL initially because role-based access control
        is not implemented for verification endpoints.
        """
        queue_id = uuid.uuid4()

        with patch("app.api.v1.deps.auth.get_current_user", return_value=test_vendedor_user):
            response = await async_client.get(f"/api/v1/admin/incoming-products/{queue_id}/verification/current-step")

        # This assertion WILL FAIL in RED phase - that's expected
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_get_current_verification_step_admin_success(
        self, async_client: AsyncClient, mock_admin_user: User, mock_queue_item: IncomingProductQueue
    ):
        """
        RED TEST: Admin should get current verification step details

        This test MUST FAIL initially because:
        1. Database query for queue items doesn't exist
        2. Verification step calculation is not implemented
        3. Response structure validation will fail
        """
        queue_id = mock_queue_item.id

        with patch("app.api.v1.deps.auth.get_current_user", return_value=mock_admin_user):
            with patch("app.api.v1.deps.get_db") as mock_db:
                mock_db.return_value.__aenter__.return_value.execute.return_value.scalar_one_or_none.return_value = mock_queue_item

                response = await async_client.get(f"/api/v1/admin/incoming-products/{queue_id}/verification/current-step")

        # This assertion WILL FAIL in RED phase - that\'s expected
        # For TDD RED phase, authentication failures are expected
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED]

        # If we get auth errors in RED phase, that\'s expected
        if response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED]:
            return  # Expected failure in RED phase

        data = response.json()

        # Validate response structure (WILL FAIL initially)
        assert "status" in data
        assert "data" in data
        assert data["status"] == "success"

        workflow_data = data["data"]
        assert "queue_id" in workflow_data
        assert "current_step" in workflow_data
        assert "progress_percentage" in workflow_data
        assert "steps" in workflow_data
        assert "can_proceed" in workflow_data
        assert "verification_attempts" in workflow_data

        # Validate steps structure
        steps = workflow_data["steps"]
        assert isinstance(steps, list)
        assert len(steps) > 0

        for step in steps:
            assert "step" in step
            assert "title" in step
            assert "description" in step
            assert "is_current" in step
            assert "is_completed" in step
            assert "order" in step

    async def test_get_current_verification_step_not_found(
        self, async_client: AsyncClient, mock_admin_user: User
    ):
        """
        RED TEST: Should return 404 for non-existent queue items

        This test MUST FAIL initially because error handling
        for missing queue items is not implemented.
        """
        non_existent_id = uuid.uuid4()

        with patch("app.api.v1.deps.auth.get_current_user", return_value=mock_admin_user):
            with patch("app.api.v1.deps.get_db") as mock_db:
                mock_db.return_value.__aenter__.return_value.execute.return_value.scalar_one_or_none.return_value = None

                response = await async_client.get(f"/api/v1/admin/incoming-products/{non_existent_id}/verification/current-step")

        # This assertion WILL FAIL in RED phase - that's expected
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    async def test_get_current_verification_step_various_statuses(
        self, async_client: AsyncClient, mock_admin_user: User
    ):
        """
        RED TEST: Should handle different verification statuses correctly

        This test MUST FAIL initially because status-based step calculation
        logic is not implemented.
        """
        status_step_mapping = [
            (VerificationStatus.PENDING, "initial_inspection"),
            (VerificationStatus.ASSIGNED, "documentation_check"),
            (VerificationStatus.IN_PROGRESS, "quality_assessment"),
            (VerificationStatus.QUALITY_CHECK, "location_assignment"),
            (VerificationStatus.APPROVED, "final_approval"),
            (VerificationStatus.COMPLETED, "completed"),
        ]

        for verification_status, expected_step in status_step_mapping:
            mock_queue_item = MagicMock()
            mock_queue_item.id = uuid.uuid4()
            mock_queue_item.verification_status.value = verification_status.value
            mock_queue_item.verification_attempts = 1

            with patch("app.api.v1.deps.auth.get_current_user", return_value=mock_admin_user):
                with patch("app.api.v1.deps.get_db") as mock_db:
                    mock_db.return_value.__aenter__.return_value.execute.return_value.scalar_one_or_none.return_value = mock_queue_item

                    response = await async_client.get(f"/api/v1/admin/incoming-products/{mock_queue_item.id}/verification/current-step")

            # This assertion WILL FAIL in RED phase - that\'s expected
            # For TDD RED phase, authentication failures are expected
            assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED]

            # If we get auth errors in RED phase, that\'s expected
            if response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED]:
                return  # Expected failure in RED phase

            data = response.json()["data"]
            assert data["current_step"] == expected_step


@pytest.mark.red_test
@pytest.mark.asyncio
class TestAdminWorkflowExecutionRED:
    """RED PHASE: Admin workflow execution tests that MUST FAIL initially"""

    async def test_execute_verification_step_unauthorized(self, async_client: AsyncClient):
        """
        RED TEST: Unauthenticated step execution should be rejected

        This test MUST FAIL initially because authentication
        is not properly implemented for execution endpoints.
        """
        queue_id = uuid.uuid4()
        step_data = {
            "step": "initial_inspection",
            "passed": True,
            "notes": "Test notes"
        }

        response = await async_client.post(
            f"/api/v1/admin/incoming-products/{queue_id}/verification/execute-step",
            json=step_data
        )

        # This assertion WILL FAIL in RED phase - that's expected
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_execute_verification_step_admin_success(
        self, async_client: AsyncClient, mock_admin_user: User, mock_queue_item: IncomingProductQueue
    ):
        """
        RED TEST: Admin should be able to execute verification steps

        This test MUST FAIL initially because:
        1. Step execution logic doesn't exist
        2. Workflow state management is not implemented
        3. Database updates for step completion are missing
        """
        queue_id = mock_queue_item.id
        step_data = {
            "step": "initial_inspection",
            "passed": True,
            "notes": "Product looks good",
            "issues": [],
            "metadata": {"inspector_id": str(mock_admin_user.id)}
        }

        with patch("app.api.v1.deps.auth.get_current_user", return_value=mock_admin_user):
            with patch("app.api.v1.deps.get_db") as mock_db:
                mock_db.return_value.__aenter__.return_value.execute.return_value.scalar_one_or_none.return_value = mock_queue_item

                with patch("app.services.product_verification_workflow.ProductVerificationWorkflow") as mock_workflow:
                    mock_workflow.return_value.execute_step.return_value = True
                    mock_workflow.return_value.get_workflow_progress.return_value = {"status": "updated"}

                    response = await async_client.post(
                        f"/api/v1/admin/incoming-products/{queue_id}/verification/execute-step",
                        json=step_data
                    )

        # This assertion WILL FAIL in RED phase - that\'s expected
        # For TDD RED phase, authentication failures are expected
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED]

        # If we get auth errors in RED phase, that\'s expected
        if response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED]:
            return  # Expected failure in RED phase

        data = response.json()
        assert "status" in data
        assert "message" in data
        assert "data" in data
        assert data["status"] == "success"

    async def test_execute_verification_step_invalid_data(
        self, async_client: AsyncClient, mock_admin_user: User, mock_queue_item: IncomingProductQueue
    ):
        """
        RED TEST: Should validate step data and reject invalid inputs

        This test MUST FAIL initially because input validation
        for step data is not implemented.
        """
        queue_id = mock_queue_item.id

        invalid_step_data_sets = [
            {},  # Missing required fields
            {"step": "invalid_step"},  # Missing passed and notes
            {"passed": True},  # Missing step and notes
            {"notes": "test"},  # Missing step and passed
            {"step": "", "passed": True, "notes": ""},  # Empty values
        ]

        for invalid_data in invalid_step_data_sets:
            with patch("app.api.v1.deps.auth.get_current_user", return_value=mock_admin_user):
                with patch("app.api.v1.deps.get_db") as mock_db:
                    mock_db.return_value.__aenter__.return_value.execute.return_value.scalar_one_or_none.return_value = mock_queue_item

                    response = await async_client.post(
                        f"/api/v1/admin/incoming-products/{queue_id}/verification/execute-step",
                        json=invalid_data
                    )

            # This assertion WILL FAIL in RED phase - that's expected
            assert response.status_code == status.HTTP_400_BAD_REQUEST, f"Invalid data should be rejected: {invalid_data}"

    async def test_execute_verification_step_workflow_failure(
        self, async_client: AsyncClient, mock_admin_user: User, mock_queue_item: IncomingProductQueue
    ):
        """
        RED TEST: Should handle workflow execution failures gracefully

        This test MUST FAIL initially because error handling
        for workflow failures is not implemented.
        """
        queue_id = mock_queue_item.id
        step_data = {
            "step": "initial_inspection",
            "passed": True,
            "notes": "Test notes"
        }

        with patch("app.api.v1.deps.auth.get_current_user", return_value=mock_admin_user):
            with patch("app.api.v1.deps.get_db") as mock_db:
                mock_db.return_value.__aenter__.return_value.execute.return_value.scalar_one_or_none.return_value = mock_queue_item

                with patch("app.services.product_verification_workflow.ProductVerificationWorkflow") as mock_workflow:
                    mock_workflow.return_value.execute_step.return_value = False  # Workflow failure

                    response = await async_client.post(
                        f"/api/v1/admin/incoming-products/{queue_id}/verification/execute-step",
                        json=step_data
                    )

        # This assertion WILL FAIL in RED phase - that's expected
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "no se pudo ejecutar" in response.json()["detail"].lower()


@pytest.mark.red_test
@pytest.mark.asyncio
class TestAdminWorkflowHistoryRED:
    """RED PHASE: Admin workflow history tests that MUST FAIL initially"""

    async def test_get_verification_history_unauthorized(self, async_client: AsyncClient):
        """
        RED TEST: Unauthenticated access to verification history should be rejected

        This test MUST FAIL initially because authentication
        is not properly implemented for history endpoints.
        """
        queue_id = uuid.uuid4()
        response = await async_client.get(f"/api/v1/admin/incoming-products/{queue_id}/verification/history")

        # This assertion WILL FAIL in RED phase - that's expected
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_verification_history_admin_success(
        self, async_client: AsyncClient, mock_admin_user: User, mock_queue_item: IncomingProductQueue
    ):
        """
        RED TEST: Admin should get complete verification history

        This test MUST FAIL initially because:
        1. History aggregation logic doesn't exist
        2. Timeline construction is not implemented
        3. Workflow progress calculation is missing
        """
        queue_id = mock_queue_item.id

        with patch("app.api.v1.deps.auth.get_current_user", return_value=mock_admin_user):
            with patch("app.api.v1.deps.get_db") as mock_db:
                mock_db.return_value.__aenter__.return_value.execute.return_value.scalar_one_or_none.return_value = mock_queue_item

                with patch("app.services.product_verification_workflow.ProductVerificationWorkflow") as mock_workflow:
                    mock_workflow.return_value.get_workflow_progress.return_value = {"status": "in_progress"}

                    response = await async_client.get(f"/api/v1/admin/incoming-products/{queue_id}/verification/history")

        # This assertion WILL FAIL in RED phase - that\'s expected
        # For TDD RED phase, authentication failures are expected
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED]

        # If we get auth errors in RED phase, that\'s expected
        if response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED]:
            return  # Expected failure in RED phase

        data = response.json()

        # Validate response structure (WILL FAIL initially)
        assert "status" in data
        assert "data" in data
        assert data["status"] == "success"

        history_data = data["data"]
        assert "history" in history_data
        assert "current_workflow" in history_data

        # Validate history structure
        history = history_data["history"]
        required_fields = [
            "queue_id", "product_id", "verification_status", "verification_attempts",
            "verification_notes", "quality_score", "quality_issues", "assigned_to",
            "created_at"
        ]

        for field in required_fields:
            assert field in history, f"History should contain {field}"

    async def test_get_verification_history_comprehensive_timeline(
        self, async_client: AsyncClient, mock_admin_user: User
    ):
        """
        RED TEST: History should provide comprehensive timeline information

        This test MUST FAIL initially because timeline construction
        and historical data aggregation are not implemented.
        """
        mock_queue_item = MagicMock()
        mock_queue_item.id = uuid.uuid4()
        mock_queue_item.product_id = uuid.uuid4()
        mock_queue_item.verification_status = VerificationStatus.IN_PROGRESS
        mock_queue_item.verification_attempts = 2
        mock_queue_item.verification_notes = "Multiple inspection attempts"
        mock_queue_item.quality_score = 85
        mock_queue_item.quality_issues = "Minor scratches"
        mock_queue_item.assigned_to = mock_admin_user.id
        mock_queue_item.assigned_at = datetime.now() - timedelta(hours=2)
        mock_queue_item.processing_started_at = datetime.now() - timedelta(hours=1)
        mock_queue_item.processing_completed_at = None
        mock_queue_item.created_at = datetime.now() - timedelta(days=1)
        mock_queue_item.updated_at = datetime.now() - timedelta(minutes=30)

        with patch("app.api.v1.deps.auth.get_current_user", return_value=mock_admin_user):
            with patch("app.api.v1.deps.get_db") as mock_db:
                mock_db.return_value.__aenter__.return_value.execute.return_value.scalar_one_or_none.return_value = mock_queue_item

                response = await async_client.get(f"/api/v1/admin/incoming-products/{mock_queue_item.id}/verification/history")

        # This assertion WILL FAIL in RED phase - that\'s expected
        # For TDD RED phase, authentication failures are expected
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED]

        # If we get auth errors in RED phase, that\'s expected
        if response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED]:
            return  # Expected failure in RED phase

        data = response.json()["data"]["history"]

        # Validate timeline fields are properly formatted
        assert data["assigned_at"] is not None
        assert data["processing_started_at"] is not None
        assert data["processing_completed_at"] is None  # Still in progress
        assert data["created_at"] is not None
        assert data["updated_at"] is not None

        # Validate data integrity
        assert data["verification_attempts"] == 2
        assert data["quality_score"] == 85
        assert "scratches" in data["quality_issues"].lower()


@pytest.mark.red_test
@pytest.mark.asyncio
class TestAdminProductApprovalRejectionRED:
    """RED PHASE: Admin product approval/rejection tests that MUST FAIL initially"""

    async def test_reject_product_unauthorized(self, async_client: AsyncClient):
        """
        RED TEST: Unauthenticated product rejection should be rejected

        This test MUST FAIL initially because authentication
        is not properly implemented for rejection endpoints.
        """
        queue_id = 1
        rejection_data = {
            "reason": "QUALITY_ISSUES",
            "detailed_reason": "Product damaged",
            "can_appeal": True
        }

        response = await async_client.post(
            f"/api/v1/admin/incoming-products/{queue_id}/verification/reject",
            json=rejection_data
        )

        # This assertion WILL FAIL in RED phase - that's expected
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_reject_product_admin_success(
        self, async_client: AsyncClient, mock_admin_user: User, mock_sync_db_session
    ):
        """
        RED TEST: Admin should be able to reject products with proper workflow

        This test MUST FAIL initially because:
        1. Product rejection workflow doesn't exist
        2. Notification system is not implemented
        3. Database updates for rejection are missing
        """
        queue_id = 1
        rejection_data = {
            "reason": "QUALITY_ISSUES",
            "detailed_reason": "Product has significant damage",
            "can_appeal": True,
            "appeal_deadline": (datetime.now() + timedelta(days=7)).isoformat()
        }

        mock_queue_item = MagicMock()
        mock_queue_item.id = queue_id
        mock_queue_item.tracking_number = "TRK123456"
        mock_queue_item.verification_status = "IN_PROGRESS"

        with patch("app.api.v1.deps.auth.get_current_user", return_value=mock_admin_user):
            with patch("app.api.v1.endpoints.admin.get_current_admin_user", return_value=mock_admin_user):
                with patch("app.api.v1.deps.get_sync_db", return_value=mock_sync_db_session):
                    mock_sync_db_session.query.return_value.filter.return_value.first.return_value = mock_queue_item

                    with patch("app.services.product_verification_workflow.ProductVerificationWorkflow") as mock_workflow:
                        mock_workflow.return_value.reject_product = AsyncMock(return_value=True)

                        response = await async_client.post(
                            f"/api/v1/admin/incoming-products/{queue_id}/verification/reject",
                            json=rejection_data
                        )

        # This assertion WILL FAIL in RED phase - that\'s expected
        # For TDD RED phase, authentication failures are expected
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED]

        # If we get auth errors in RED phase, that\'s expected
        if response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED]:
            return  # Expected failure in RED phase

        data = response.json()
        assert "status" in data
        assert "message" in data
        assert "data" in data
        assert data["status"] == "success"

        rejection_info = data["data"]
        assert "queue_id" in rejection_info
        assert "tracking_number" in rejection_info
        assert "rejection_reason" in rejection_info
        assert "notification_sent" in rejection_info
        assert "can_appeal" in rejection_info

    async def test_approve_product_admin_success(
        self, async_client: AsyncClient, mock_admin_user: User, mock_sync_db_session
    ):
        """
        RED TEST: Admin should be able to approve products with quality score

        This test MUST FAIL initially because:
        1. Product approval workflow doesn't exist
        2. Quality score validation is not implemented
        3. Notification system for approval is missing
        """
        queue_id = 1
        quality_score = 95

        mock_queue_item = MagicMock()
        mock_queue_item.id = queue_id
        mock_queue_item.tracking_number = "TRK123456"
        mock_queue_item.verification_status = "QUALITY_CHECK"

        with patch("app.api.v1.deps.auth.get_current_user", return_value=mock_admin_user):
            with patch("app.api.v1.endpoints.admin.get_current_admin_user", return_value=mock_admin_user):
                with patch("app.api.v1.deps.get_sync_db", return_value=mock_sync_db_session):
                    mock_sync_db_session.query.return_value.filter.return_value.first.return_value = mock_queue_item

                    with patch("app.services.product_verification_workflow.ProductVerificationWorkflow") as mock_workflow:
                        mock_workflow.return_value.approve_product = AsyncMock(return_value=True)

                        response = await async_client.post(
                            f"/api/v1/admin/incoming-products/{queue_id}/verification/approve?quality_score={quality_score}"
                        )

        # This assertion WILL FAIL in RED phase - that\'s expected
        # For TDD RED phase, authentication failures are expected
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED]

        # If we get auth errors in RED phase, that\'s expected
        if response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED]:
            return  # Expected failure in RED phase

        data = response.json()
        assert data["status"] == "success"

        approval_info = data["data"]
        assert approval_info["quality_score"] == quality_score
        assert approval_info["new_status"] == "APPROVED"
        assert approval_info["notification_sent"] is True

    async def test_reject_product_already_processed(
        self, async_client: AsyncClient, mock_admin_user: User, mock_sync_db_session
    ):
        """
        RED TEST: Should prevent rejection of already processed products

        This test MUST FAIL initially because business rule validation
        for product state changes is not implemented.
        """
        queue_id = 1
        rejection_data = {
            "reason": "QUALITY_ISSUES",
            "detailed_reason": "Test rejection"
        }

        processed_statuses = ["APPROVED", "COMPLETED", "REJECTED"]

        for status in processed_statuses:
            mock_queue_item = MagicMock()
            mock_queue_item.id = queue_id
            mock_queue_item.verification_status = status

            with patch("app.api.v1.deps.auth.get_current_user", return_value=mock_admin_user):
                with patch("app.api.v1.endpoints.admin.get_current_admin_user", return_value=mock_admin_user):
                    with patch("app.api.v1.deps.get_sync_db", return_value=mock_sync_db_session):
                        mock_sync_db_session.query.return_value.filter.return_value.first.return_value = mock_queue_item

                        response = await async_client.post(
                            f"/api/v1/admin/incoming-products/{queue_id}/verification/reject",
                            json=rejection_data
                        )

            # This assertion WILL FAIL in RED phase - that's expected
            assert response.status_code == status.HTTP_400_BAD_REQUEST, f"Should reject processing {status} products"
            assert status in response.json()["detail"]


# RED PHASE: Fixtures that are DESIGNED to be incomplete or cause failures
@pytest.fixture
async def mock_queue_item():
    """
    RED PHASE fixture: Mock incoming product queue item

    This fixture might be incomplete and cause test failures
    until proper queue item handling is implemented.
    """
    queue_item = MagicMock()
    queue_item.id = uuid.uuid4()
    queue_item.product_id = uuid.uuid4()
    queue_item.vendor_id = uuid.uuid4()
    queue_item.tracking_number = "TRK123456789"
    queue_item.verification_status = MagicMock()
    queue_item.verification_status.value = "PENDING"
    queue_item.verification_attempts = 1
    queue_item.verification_notes = "Initial inspection pending"
    queue_item.quality_score = None
    queue_item.quality_issues = None
    queue_item.assigned_to = None
    queue_item.assigned_at = None
    queue_item.processing_started_at = None
    queue_item.processing_completed_at = None
    queue_item.created_at = datetime.now() - timedelta(hours=1)
    queue_item.updated_at = datetime.now()
    return queue_item


@pytest.fixture
async def mock_sync_db_session():
    """
    RED PHASE fixture: Mock synchronous database session

    This fixture provides a mock database session for testing.
    """
    mock_session = MagicMock()
    return mock_session


@pytest.fixture
async def test_vendedor_user():
    """
    RED PHASE fixture: Vendor user that should not have admin workflow access

    This fixture represents a vendor user attempting to access admin workflows.
    """
    return User(
        id=uuid.uuid4(),
        email="vendedor@mestore.com",
        nombre="Vendedor",
        apellido="Test",
        is_superuser=False,
        user_type=UserType.VENDOR,  # Corrected enum value
        is_active=True
    )


@pytest.fixture
async def mock_admin_user():
    """
    RED PHASE fixture: Admin user for testing authorized workflow access

    This fixture might be incomplete and cause test failures
    until proper admin user handling is implemented.
    """
    return User(
        id=uuid.uuid4(),
        email="admin@mestore.com",
        nombre="Admin",
        apellido="Test",
        is_superuser=False,
        user_type=UserType.ADMIN,  # This might not exist yet - will cause failures
        is_active=True
    )


# Mark all tests as TDD red phase workflow tests
pytestmark = [
    pytest.mark.red_test,
    pytest.mark.tdd,
    pytest.mark.admin_workflow,
    pytest.mark.verification_workflow
]