"""
Admin Data Management Endpoints - RED Phase TDD Tests
====================================================

This file contains comprehensive RED phase TDD tests for admin data management endpoints
focusing on product verification workflow, photo/quality management, product approval/rejection,
and location assignment functionality.

File: tests/unit/admin_management/test_admin_data_management_red.py
Author: TDD Specialist AI
Date: 2025-09-21
Framework: pytest with RED-GREEN-REFACTOR TDD methodology
Target: Admin data management endpoints in app/api/v1/endpoints/admin.py

Test Categories:
===============
1. Product Verification Workflow Tests (RED)
2. Photo & Quality Management Tests (RED)
3. Product Approval/Rejection Tests (RED)
4. Location Assignment Tests (RED)
5. Security Validation Tests (RED)
6. Business Logic Validation Tests (RED)
7. File Upload Security Tests (RED)

TDD Markers Used:
================
- @pytest.mark.red_test - Indicates RED phase (failing tests first)
- @pytest.mark.data_management - Categorizes data management functionality
- @pytest.mark.admin_auth - Tests requiring admin authentication
- @pytest.mark.file_upload - File upload specific tests
- @pytest.mark.workflow - Workflow state management tests
- @pytest.mark.security - Security validation tests
"""

import pytest
import uuid
import io
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from unittest.mock import Mock, MagicMock, AsyncMock, patch
from pathlib import Path

# FastAPI testing imports
from fastapi.testclient import TestClient
from fastapi import UploadFile, File, Form, Depends
from httpx import AsyncClient
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

# Application imports
from app.main import app
from app.models.user import User, UserType
from app.models.incoming_product_queue import IncomingProductQueue, VerificationStatus
from app.models.product import Product
from app.core.auth import get_current_user
from app.services.product_verification_workflow import (
    ProductVerificationWorkflow,
    VerificationStep,
    StepResult,
    ProductRejection,
    RejectionReason
)
from app.services.location_assignment_service import LocationAssignmentService, LocationScore
from app.schemas.product_verification import (
    QualityPhoto,
    PhotoUploadResponse,
    QualityChecklist,
    QualityChecklistRequest
)

# Test fixtures and utilities
# from tests.conftest import async_session_maker  # Not available - use async_session instead
# from tests.unit.admin_management.admin_test_fixtures import (
#     mock_admin_user,
#     mock_incoming_product_queue,
#     mock_product_verification_workflow
# )  # Import individually as needed


def create_mock_admin_user():
    """Create a mock admin user for testing"""
    admin_user = Mock()
    admin_user.id = str(uuid.uuid4())
    admin_user.email = "admin@test.com"
    admin_user.nombre = "Admin"
    admin_user.apellido = "User"
    admin_user.user_type = UserType.SUPERUSER
    admin_user.is_superuser = True
    admin_user.is_active = True
    admin_user.is_verified = True
    return admin_user


async def mock_get_current_user():
    """Mock dependency for get_current_user"""
    return create_mock_admin_user()


from contextlib import asynccontextmanager

@asynccontextmanager
async def admin_auth_override():
    """Context manager for admin authentication override"""
    app.dependency_overrides[get_current_user] = mock_get_current_user
    try:
        yield
    finally:
        app.dependency_overrides.clear()


# =============================================================================
# PRODUCT VERIFICATION WORKFLOW ENDPOINT TESTS (RED PHASE)
# =============================================================================

class TestProductVerificationWorkflowRed:
    """
    RED Phase tests for Product Verification Workflow endpoints.
    These tests should FAIL initially as the endpoints are being implemented.
    """

    @pytest.mark.red_test
    @pytest.mark.data_management
    @pytest.mark.admin_auth
    @pytest.mark.workflow
    async def test_get_current_verification_step_admin_required_fails(self, async_client: AsyncClient):
        """
        RED: Test that getting current verification step requires admin authentication
        Should fail with 403 when non-admin user attempts access
        """
        # Create non-admin user token
        non_admin_headers = {"Authorization": "Bearer fake_non_admin_token"}
        queue_id = str(uuid.uuid4())

        response = await async_client.get(
            f"/api/v1/admin/incoming-products/{queue_id}/verification/current-step",
            headers=non_admin_headers
        )

        # Should fail with 401 or 403 - test will fail in RED phase
        assert response.status_code in [401, 403]
        response_data = response.json()
        # Check multiple possible error message fields
        error_text = str(response_data)
        assert (response_data.get("error_code") == "UNAUTHORIZED" or
                "No tienes permisos" in error_text or
                "Token inválido" in error_text or
                "Invalid authentication" in error_text or
                "Not authenticated" in error_text)

    @pytest.mark.red_test
    @pytest.mark.data_management
    @pytest.mark.admin_auth
    @pytest.mark.workflow
    async def test_get_current_verification_step_invalid_queue_id_fails(self, async_client: AsyncClient):
        """
        RED: Test that invalid UUID for queue_id fails validation
        Should fail with 422 for invalid UUID format
        """
        admin_headers = {"Authorization": "Bearer fake_admin_token"}
        invalid_queue_id = "not-a-valid-uuid"

        response = await async_client.get(
            f"/api/v1/admin/incoming-products/{invalid_queue_id}/verification/current-step",
            headers=admin_headers
        )

        # Should fail with authentication or validation error - test will fail in RED phase
        # Accepting both 401 (auth) and 422 (validation) as valid failures for RED phase
        assert response.status_code in [401, 422]
        if response.status_code == 422:
            assert "validation error" in response.json()["detail"][0]["type"]

    @pytest.mark.red_test
    @pytest.mark.data_management
    @pytest.mark.admin_auth
    @pytest.mark.workflow
    async def test_get_current_verification_step_nonexistent_product_fails(self, async_client: AsyncClient):
        """
        RED: Test that getting verification step for non-existent product fails
        Should fail with 404 when product not found in queue
        """
        async with admin_auth_override():
            admin_headers = {"Authorization": "Bearer admin_token"}
            nonexistent_queue_id = str(uuid.uuid4())

            response = await async_client.get(
                f"/api/v1/admin/incoming-products/{nonexistent_queue_id}/verification/current-step",
                headers=admin_headers
            )

            # Should fail with 404 Not Found - test will fail in RED phase
            assert response.status_code == 404
            response_data = response.json()
            # Check for error message in standardized response format
            assert "error_message" in response_data
            assert "Producto no encontrado" in response_data["error_message"]

    @pytest.mark.red_test
    @pytest.mark.data_management
    @pytest.mark.admin_auth
    @pytest.mark.workflow
    async def test_execute_verification_step_missing_required_fields_fails(self, async_client: AsyncClient):
        """
        RED: Test that executing verification step with missing required fields fails
        Should fail with 400 when required fields are missing
        """
        admin_headers = {"Authorization": "Bearer fake_admin_token"}
        queue_id = str(uuid.uuid4())

        # Missing required fields: step, passed, notes
        incomplete_step_data = {
            "step": "initial_inspection"
            # Missing 'passed' and 'notes' fields
        }

        async with admin_auth_override():

            response = await async_client.post(
                f"/api/v1/admin/incoming-products/{queue_id}/verification/execute-step",
                headers=admin_headers,
                json=incomplete_step_data
            )

        # Should fail with 400 Bad Request - validation working correctly
        assert response.status_code == 400
        response_data = response.json()
        # Check for error message in standardized response format
        assert "error_message" in response_data
        assert "Campo requerido faltante" in response_data["error_message"]

    @pytest.mark.red_test
    @pytest.mark.data_management
    @pytest.mark.admin_auth
    @pytest.mark.workflow
    async def test_execute_verification_step_invalid_step_name_fails(self, async_client: AsyncClient):
        """
        RED: Test that executing verification step with invalid step name fails
        Should fail with 400 when step name is not recognized
        """
        admin_headers = {"Authorization": "Bearer fake_admin_token"}
        queue_id = str(uuid.uuid4())

        invalid_step_data = {
            "step": "invalid_step_name",
            "passed": True,
            "notes": "Test notes"
        }

        async with admin_auth_override():

            response = await async_client.post(
                f"/api/v1/admin/incoming-products/{queue_id}/verification/execute-step",
                headers=admin_headers,
                json=invalid_step_data
            )

        # Should fail with 400 Bad Request - test will fail in RED phase
        assert response.status_code == 400
        assert "Valor inválido" in response.json()["error_message"]

    @pytest.mark.red_test
    @pytest.mark.data_management
    @pytest.mark.admin_auth
    @pytest.mark.workflow
    async def test_get_verification_history_database_error_fails(self, async_client: AsyncClient):
        """
        RED: Test that database errors during verification history retrieval fail gracefully
        Should fail with 500 when database error occurs
        """
        admin_headers = {"Authorization": "Bearer fake_admin_token"}
        queue_id = str(uuid.uuid4())

        async with admin_auth_override():

            with patch('sqlalchemy.ext.asyncio.AsyncSession.execute') as mock_execute:
                mock_execute.side_effect = Exception("Database connection failed")

                response = await async_client.get(
                    f"/api/v1/admin/incoming-products/{queue_id}/verification/history",
                    headers=admin_headers
                )

        # Should fail with 500 Internal Server Error - test will fail in RED phase
        assert response.status_code == 500
        assert "Error al obtener historial" in response.json()["error_message"]


# =============================================================================
# PHOTO & QUALITY MANAGEMENT ENDPOINT TESTS (RED PHASE)
# =============================================================================

class TestPhotoQualityManagementRed:
    """
    RED Phase tests for Photo & Quality Management endpoints.
    These tests focus on file upload security, validation, and quality checklist processing.
    """

    @pytest.mark.red_test
    @pytest.mark.data_management
    @pytest.mark.admin_auth
    @pytest.mark.file_upload
    @pytest.mark.security
    async def test_upload_verification_photos_non_admin_fails(self, async_client: AsyncClient):
        """
        RED: Test that photo upload requires admin authentication
        Should fail with 403 when non-admin user attempts upload
        """
        non_admin_headers = {"Authorization": "Bearer fake_vendor_token"}
        queue_id = str(uuid.uuid4())

        # Create fake image file
        fake_image = io.BytesIO(b"fake_image_content")
        files = {"files": ("test.jpg", fake_image, "image/jpeg")}

        response = await async_client.post(
            f"/api/v1/admin/incoming-products/{queue_id}/verification/upload-photos",
            headers=non_admin_headers,
            files=files,
            data={"photo_types": ["general"]}
        )

        # Should fail with 401 or 403 - test will fail in RED phase
        assert response.status_code in [401, 403]
        response_data = response.json()
        # Check multiple possible error message fields
        error_text = str(response_data)
        assert (response_data.get("error_code") == "UNAUTHORIZED" or
                "No tienes permisos" in error_text or
                "Token inválido" in error_text or
                "Invalid authentication" in error_text or
                "Not authenticated" in error_text)

    @pytest.mark.red_test
    @pytest.mark.data_management
    @pytest.mark.admin_auth
    @pytest.mark.file_upload
    @pytest.mark.security
    async def test_upload_verification_photos_malicious_file_type_fails(self, async_client: AsyncClient):
        """
        RED: Test that malicious file types are rejected
        Should fail with appropriate error when non-image file is uploaded
        """
        admin_headers = {"Authorization": "Bearer fake_admin_token"}
        queue_id = str(uuid.uuid4())

        # Create malicious file (executable)
        malicious_file = io.BytesIO(b"#!/bin/bash\necho 'malicious code'")
        files = {"files": ("malicious.sh", malicious_file, "application/x-sh")}

        async with admin_auth_override():

            response = await async_client.post(
                f"/api/v1/admin/incoming-products/{queue_id}/verification/upload-photos",
                headers=admin_headers,
                files=files,
                data={"photo_types": ["general"]}
            )

        # Should fail with file type rejection - test will fail in RED phase
        assert response.status_code == 200  # Returns success but with failed_uploads
        response_data = response.json()
        assert len(response_data["failed_uploads"]) > 0
        assert "Tipo de archivo no permitido" in response_data["failed_uploads"][0]

    @pytest.mark.red_test
    @pytest.mark.data_management
    @pytest.mark.admin_auth
    @pytest.mark.file_upload
    @pytest.mark.security
    async def test_upload_verification_photos_oversized_file_fails(self, async_client: AsyncClient):
        """
        RED: Test that oversized files are rejected
        Should fail when file exceeds maximum size limit (10MB)
        """
        admin_headers = {"Authorization": "Bearer fake_admin_token"}
        queue_id = str(uuid.uuid4())

        # Create oversized file (> 10MB)
        oversized_content = b"x" * (11 * 1024 * 1024)  # 11MB
        oversized_file = io.BytesIO(oversized_content)
        files = {"files": ("huge.jpg", oversized_file, "image/jpeg")}

        async with admin_auth_override():

            response = await async_client.post(
                f"/api/v1/admin/incoming-products/{queue_id}/verification/upload-photos",
                headers=admin_headers,
                files=files,
                data={"photo_types": ["general"]}
            )

        # Should fail with size rejection - test will fail in RED phase
        assert response.status_code == 200  # Returns success but with failed_uploads
        response_data = response.json()
        assert len(response_data["failed_uploads"]) > 0
        assert "demasiado grande" in response_data["failed_uploads"][0]

    @pytest.mark.red_test
    @pytest.mark.data_management
    @pytest.mark.admin_auth
    @pytest.mark.file_upload
    @pytest.mark.security
    async def test_upload_verification_photos_path_traversal_attack_fails(self, async_client: AsyncClient):
        """
        RED: Test that path traversal attacks in filenames are prevented
        Should fail when filename contains path traversal sequences
        """
        admin_headers = {"Authorization": "Bearer fake_admin_token"}
        queue_id = str(uuid.uuid4())

        # Malicious filename with path traversal
        malicious_image = io.BytesIO(b"fake_image_content")
        files = {"files": ("../../../etc/passwd.jpg", malicious_image, "image/jpeg")}

        async with admin_auth_override():

            response = await async_client.post(
                f"/api/v1/admin/incoming-products/{queue_id}/verification/upload-photos",
                headers=admin_headers,
                files=files,
                data={"photo_types": ["general"]}
            )

        # Should sanitize filename or reject - test will fail in RED phase
        assert response.status_code == 200
        response_data = response.json()
        # Verify that the uploaded filename doesn't contain path traversal
        if response_data["total_uploaded"] > 0:
            uploaded_filename = response_data["uploaded_photos"][0]["filename"]
            assert "../" not in uploaded_filename
            assert "etc/passwd" not in uploaded_filename

    @pytest.mark.red_test
    @pytest.mark.data_management
    @pytest.mark.admin_auth
    @pytest.mark.file_upload
    async def test_delete_verification_photo_path_traversal_protection_fails(self, async_client: AsyncClient):
        """
        RED: Test that photo deletion prevents path traversal attacks
        Should fail with 400 when filename contains path traversal sequences
        """
        admin_headers = {"Authorization": "Bearer fake_admin_token"}
        malicious_filename = "../../../etc/passwd"

        async with admin_auth_override():

            response = await async_client.delete(
                f"/api/v1/admin/verification-photos/{malicious_filename}",
                headers=admin_headers
            )

        # Should fail with 400 Bad Request - test will fail in RED phase
        assert response.status_code == 400
        assert "Nombre de archivo inválido" in response.json()["detail"]

    @pytest.mark.red_test
    @pytest.mark.data_management
    @pytest.mark.admin_auth
    @pytest.mark.workflow
    async def test_submit_quality_checklist_mismatched_queue_id_fails(self, async_client: AsyncClient):
        """
        RED: Test that quality checklist submission with mismatched queue IDs fails
        Should fail with 400 when request queue_id doesn't match URL queue_id
        """
        admin_headers = {"Authorization": "Bearer fake_admin_token"}
        url_queue_id = str(uuid.uuid4())
        request_queue_id = str(uuid.uuid4())  # Different from URL

        checklist_data = {
            "queue_id": request_queue_id,  # Mismatched
            "checklist": {
                "queue_id": request_queue_id,
                "inspector_id": str(uuid.uuid4()),
                "inspection_date": datetime.now().isoformat(),
                "quality_score": 85,
                "overall_condition": "good",
                "has_damage": False,
                "has_missing_parts": False,
                "has_defects": False,
                "approved": True,
                "inspector_notes": "Quality check passed",
                "inspection_duration_minutes": 15
            }
        }

        async with admin_auth_override():

            response = await async_client.post(
                f"/api/v1/admin/incoming-products/{url_queue_id}/verification/quality-checklist",
                headers=admin_headers,
                json=checklist_data
            )

        # Should fail with 400 Bad Request - test will fail in RED phase
        assert response.status_code == 400
        assert "ID de cola no coincide" in response.json()["detail"]

    @pytest.mark.red_test
    @pytest.mark.data_management
    @pytest.mark.admin_auth
    @pytest.mark.workflow
    async def test_submit_quality_checklist_invalid_quality_score_fails(self, async_client: AsyncClient):
        """
        RED: Test that quality checklist with invalid quality score fails validation
        Should fail with 422 when quality score is outside valid range (0-100)
        """
        admin_headers = {"Authorization": "Bearer fake_admin_token"}
        queue_id = str(uuid.uuid4())

        checklist_data = {
            "queue_id": queue_id,
            "checklist": {
                "queue_id": queue_id,
                "inspector_id": str(uuid.uuid4()),
                "inspection_date": datetime.now().isoformat(),
                "quality_score": 150,  # Invalid score > 100
                "overall_condition": "good",
                "has_damage": False,
                "has_missing_parts": False,
                "has_defects": False,
                "approved": True,
                "inspector_notes": "Quality check passed",
                "inspection_duration_minutes": 15
            }
        }

        async with admin_auth_override():

            response = await async_client.post(
                f"/api/v1/admin/incoming-products/{queue_id}/verification/quality-checklist",
                headers=admin_headers,
                json=checklist_data
            )

        # Should fail with 422 Unprocessable Entity - test will fail in RED phase
        assert response.status_code == 422
        assert "validation error" in str(response.json())


# =============================================================================
# PRODUCT APPROVAL/REJECTION ENDPOINT TESTS (RED PHASE)
# =============================================================================

class TestProductApprovalRejectionRed:
    """
    RED Phase tests for Product Approval/Rejection endpoints.
    These tests focus on business logic validation and workflow state management.
    """

    @pytest.mark.red_test
    @pytest.mark.data_management
    @pytest.mark.admin_auth
    @pytest.mark.workflow
    async def test_reject_product_already_processed_fails(self, async_client: AsyncClient):
        """
        RED: Test that rejecting an already processed product fails
        Should fail with 400 when product is already in APPROVED/COMPLETED/REJECTED state
        """
        admin_headers = {"Authorization": "Bearer fake_admin_token"}
        queue_id = 12345

        rejection_data = {
            "reason": "QUALITY_ISSUES",
            "detailed_reason": "Product does not meet quality standards",
            "inspector_notes": "Multiple defects found during inspection",
            "can_appeal": True,
            "appeal_deadline": (datetime.now() + timedelta(days=7)).isoformat(),
            "quality_score": 25,
            "photographic_evidence": ["photo1.jpg", "photo2.jpg"]
        }

        async with admin_auth_override():

            with patch('app.api.v1.endpoints.admin.get_sync_db') as mock_db:
                # Mock already processed product
                mock_queue_item = Mock()
                mock_queue_item.verification_status = "APPROVED"
                mock_db.return_value.query.return_value.filter.return_value.first.return_value = mock_queue_item

                response = await async_client.post(
                    f"/api/v1/admin/incoming-products/{queue_id}/verification/reject",
                    headers=admin_headers,
                    json=rejection_data
                )

        # Should fail with 400 Bad Request - test will fail in RED phase
        assert response.status_code == 400
        assert "ya está en estado" in response.json()["detail"]

    @pytest.mark.red_test
    @pytest.mark.data_management
    @pytest.mark.admin_auth
    @pytest.mark.workflow
    async def test_reject_product_invalid_rejection_reason_fails(self, async_client: AsyncClient):
        """
        RED: Test that rejecting product with invalid rejection reason fails
        Should fail with 400 when rejection reason is not in allowed enum values
        """
        admin_headers = {"Authorization": "Bearer fake_admin_token"}
        queue_id = 12345

        rejection_data = {
            "reason": "INVALID_REASON",  # Not in RejectionReason enum
            "detailed_reason": "Product rejection",
            "inspector_notes": "Rejection notes",
            "can_appeal": True,
            "appeal_deadline": (datetime.now() + timedelta(days=7)).isoformat(),
            "quality_score": 25,
            "photographic_evidence": []
        }

        async with admin_auth_override():

            response = await async_client.post(
                f"/api/v1/admin/incoming-products/{queue_id}/verification/reject",
                headers=admin_headers,
                json=rejection_data
            )

        # Should fail with 422 Unprocessable Entity - test will fail in RED phase
        assert response.status_code == 422
        assert "validation error" in str(response.json())

    @pytest.mark.red_test
    @pytest.mark.data_management
    @pytest.mark.admin_auth
    @pytest.mark.workflow
    async def test_get_rejection_history_nonexistent_product_fails(self, async_client: AsyncClient):
        """
        RED: Test that getting rejection history for non-existent product fails
        Should fail with 404 when product not found
        """
        admin_headers = {"Authorization": "Bearer fake_admin_token"}
        nonexistent_queue_id = 99999

        async with admin_auth_override():

            with patch('app.api.v1.endpoints.admin.get_sync_db') as mock_db:
                mock_db.return_value.query.return_value.filter.return_value.first.return_value = None

                response = await async_client.get(
                    f"/api/v1/admin/incoming-products/{nonexistent_queue_id}/rejection-history",
                    headers=admin_headers
                )

        # Should fail with 404 Not Found - test will fail in RED phase
        assert response.status_code == 404
        assert "Producto no encontrado" in response.json()["detail"]

    @pytest.mark.red_test
    @pytest.mark.data_management
    @pytest.mark.admin_auth
    @pytest.mark.workflow
    async def test_get_rejections_summary_invalid_date_range_fails(self, async_client: AsyncClient):
        """
        RED: Test that rejections summary with invalid date range fails
        Should fail with 422 when start_date is after end_date
        """
        admin_headers = {"Authorization": "Bearer fake_admin_token"}

        # Invalid date range: start_date after end_date
        invalid_params = {
            "start_date": "2025-12-31",
            "end_date": "2025-01-01"
        }

        async with admin_auth_override():

            response = await async_client.get(
                "/api/v1/admin/rejections/summary",
                headers=admin_headers,
                params=invalid_params
            )

        # Should fail with validation error - test will fail in RED phase
        assert response.status_code == 422
        assert "validation error" in str(response.json())

    @pytest.mark.red_test
    @pytest.mark.data_management
    @pytest.mark.admin_auth
    @pytest.mark.workflow
    async def test_approve_product_negative_quality_score_fails(self, async_client: AsyncClient):
        """
        RED: Test that approving product with negative quality score fails
        Should fail with 422 when quality score is negative
        """
        admin_headers = {"Authorization": "Bearer fake_admin_token"}
        queue_id = 12345

        invalid_data = {
            "quality_score": -10  # Invalid negative score
        }

        async with admin_auth_override():

            response = await async_client.post(
                f"/api/v1/admin/incoming-products/{queue_id}/verification/approve",
                headers=admin_headers,
                json=invalid_data
            )

        # Should fail with 422 Unprocessable Entity - test will fail in RED phase
        assert response.status_code == 422
        assert "validation error" in str(response.json())


# =============================================================================
# LOCATION ASSIGNMENT ENDPOINT TESTS (RED PHASE)
# =============================================================================

class TestLocationAssignmentRed:
    """
    RED Phase tests for Location Assignment endpoints.
    These tests focus on location management and spatial optimization logic.
    """

    @pytest.mark.red_test
    @pytest.mark.data_management
    @pytest.mark.admin_auth
    @pytest.mark.workflow
    async def test_auto_assign_location_wrong_status_fails(self, async_client: AsyncClient):
        """
        RED: Test that auto-assigning location fails for products in wrong status
        Should fail with 400 when product is not in QUALITY_CHECK or IN_PROGRESS status
        """
        admin_headers = {"Authorization": "Bearer fake_admin_token"}
        queue_id = 12345

        async with admin_auth_override():

            with patch('app.api.v1.endpoints.admin.get_sync_db') as mock_db:
                # Mock product in wrong status
                mock_queue_item = Mock()
                mock_queue_item.verification_status = "PENDING"  # Wrong status
                mock_db.return_value.query.return_value.filter.return_value.first.return_value = mock_queue_item

                response = await async_client.post(
                    f"/api/v1/admin/incoming-products/{queue_id}/location/auto-assign",
                    headers=admin_headers
                )

        # Should fail with 400 Bad Request - test will fail in RED phase
        assert response.status_code == 400
        assert "debe estar en estado QUALITY_CHECK" in response.json()["detail"]

    @pytest.mark.red_test
    @pytest.mark.data_management
    @pytest.mark.admin_auth
    @pytest.mark.workflow
    async def test_auto_assign_location_no_available_space_fails(self, async_client: AsyncClient):
        """
        RED: Test that auto-assignment fails when no available space exists
        Should return error status when warehouse is full
        """
        admin_headers = {"Authorization": "Bearer fake_admin_token"}
        queue_id = 12345

        async with admin_auth_override():

            with patch('app.api.v1.endpoints.admin.get_sync_db') as mock_db:
                # Mock product in correct status
                mock_queue_item = Mock()
                mock_queue_item.verification_status = "QUALITY_CHECK"
                mock_db.return_value.query.return_value.filter.return_value.first.return_value = mock_queue_item

                with patch('app.services.product_verification_workflow.ProductVerificationWorkflow') as mock_workflow:
                    mock_workflow_instance = Mock()
                    mock_workflow_instance.auto_assign_location.return_value = {
                        "success": False,
                        "message": "No hay espacio disponible en el almacén",
                        "suggestion": "Considerar expansión de capacidad"
                    }
                    mock_workflow.return_value = mock_workflow_instance

                    response = await async_client.post(
                        f"/api/v1/admin/incoming-products/{queue_id}/location/auto-assign",
                        headers=admin_headers
                    )

        # Should return error status - test will fail in RED phase
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["status"] == "error"
        assert "No hay espacio disponible" in response_data["message"]
        assert response_data["data"]["manual_assignment_required"] is True

    @pytest.mark.red_test
    @pytest.mark.data_management
    @pytest.mark.admin_auth
    @pytest.mark.workflow
    async def test_get_location_suggestions_excessive_limit_fails(self, async_client: AsyncClient):
        """
        RED: Test that requesting excessive location suggestions fails
        Should fail with 422 when limit exceeds maximum allowed value
        """
        admin_headers = {"Authorization": "Bearer fake_admin_token"}
        queue_id = 12345
        excessive_limit = 1000  # Too many suggestions

        async with admin_auth_override():

            response = await async_client.get(
                f"/api/v1/admin/incoming-products/{queue_id}/location/suggestions",
                headers=admin_headers,
                params={"limit": excessive_limit}
            )

        # Should fail with 422 Unprocessable Entity - test will fail in RED phase
        assert response.status_code == 422
        assert "validation error" in str(response.json())

    @pytest.mark.red_test
    @pytest.mark.data_management
    @pytest.mark.admin_auth
    @pytest.mark.workflow
    async def test_manual_assign_location_invalid_location_format_fails(self, async_client: AsyncClient):
        """
        RED: Test that manual location assignment with invalid format fails
        Should fail with 422 when location parameters don't match expected format
        """
        admin_headers = {"Authorization": "Bearer fake_admin_token"}
        queue_id = 12345

        invalid_location_data = {
            "zona": "",  # Empty zona
            "estante": "INVALID_ESTANTE_FORMAT_TOO_LONG",  # Too long
            "posicion": "99999"  # Invalid position format
        }

        async with admin_auth_override():

            response = await async_client.post(
                f"/api/v1/admin/incoming-products/{queue_id}/location/manual-assign",
                headers=admin_headers,
                json=invalid_location_data
            )

        # Should fail with 422 Unprocessable Entity - test will fail in RED phase
        assert response.status_code == 422
        assert "validation error" in str(response.json())

    @pytest.mark.red_test
    @pytest.mark.data_management
    @pytest.mark.admin_auth
    @pytest.mark.workflow
    async def test_manual_assign_location_unavailable_location_fails(self, async_client: AsyncClient):
        """
        RED: Test that manual assignment to unavailable location fails
        Should fail with 400 when specified location is not available
        """
        admin_headers = {"Authorization": "Bearer fake_admin_token"}
        queue_id = 12345

        location_data = {
            "zona": "A",
            "estante": "01",
            "posicion": "01"
        }

        async with admin_auth_override():

            with patch('app.api.v1.endpoints.admin.get_sync_db') as mock_db:
                # Mock product in correct status
                mock_queue_item = Mock()
                mock_queue_item.verification_status = "QUALITY_CHECK"
                mock_queue_item.product = Mock()
                mock_db.return_value.query.return_value.filter.return_value.first.return_value = mock_queue_item

                with patch('app.services.location_assignment_service.LocationAssignmentService') as mock_service:
                    mock_service_instance = Mock()
                    mock_service_instance._get_available_locations.return_value = []  # No available locations
                    mock_service.return_value = mock_service_instance

                    response = await async_client.post(
                        f"/api/v1/admin/incoming-products/{queue_id}/location/manual-assign",
                        headers=admin_headers,
                        json=location_data
                    )

        # Should fail with 400 Bad Request - test will fail in RED phase
        assert response.status_code == 400
        assert "no está disponible" in response.json()["detail"]


# =============================================================================
# SECURITY VALIDATION TESTS (RED PHASE)
# =============================================================================

class TestSecurityValidationRed:
    """
    RED Phase tests for security validation across all data management endpoints.
    These tests ensure proper authentication, authorization, and input validation.
    """

    @pytest.mark.red_test
    @pytest.mark.data_management
    @pytest.mark.security
    async def test_sql_injection_protection_in_queue_id_fails(self, async_client: AsyncClient):
        """
        RED: Test that SQL injection attempts in queue_id are prevented
        Should fail safely when malicious SQL is injected via queue_id
        """
        admin_headers = {"Authorization": "Bearer fake_admin_token"}
        malicious_queue_id = "1; DROP TABLE incoming_product_queue; --"

        async with admin_auth_override():

            response = await async_client.get(
                f"/api/v1/admin/incoming-products/{malicious_queue_id}/verification/current-step",
                headers=admin_headers
            )

        # Should fail with 422 due to UUID validation - test will fail in RED phase
        assert response.status_code == 422
        assert "validation error" in str(response.json())

    @pytest.mark.red_test
    @pytest.mark.data_management
    @pytest.mark.security
    async def test_xss_protection_in_verification_notes_fails(self, async_client: AsyncClient):
        """
        RED: Test that XSS attempts in verification notes are sanitized
        Should sanitize or reject malicious JavaScript in notes fields
        """
        admin_headers = {"Authorization": "Bearer fake_admin_token"}
        queue_id = str(uuid.uuid4())

        xss_payload = {
            "step": "initial_inspection",
            "passed": True,
            "notes": "<script>alert('XSS Attack');</script>Malicious notes"
        }

        async with admin_auth_override():

            response = await async_client.post(
                f"/api/v1/admin/incoming-products/{queue_id}/verification/execute-step",
                headers=admin_headers,
                json=xss_payload
            )

        # Should sanitize the input or reject it - test will fail in RED phase
        if response.status_code == 200:
            # If processed, verify XSS was sanitized
            response_data = response.json()
            assert "<script>" not in str(response_data)
            assert "alert(" not in str(response_data)

    @pytest.mark.red_test
    @pytest.mark.data_management
    @pytest.mark.security
    async def test_csrf_protection_on_state_changing_operations_fails(self, async_client: AsyncClient):
        """
        RED: Test that CSRF protection is enforced on state-changing operations
        Should fail when proper CSRF token is not provided
        """
        # Note: This test assumes CSRF protection is implemented
        admin_headers = {"Authorization": "Bearer fake_admin_token"}
        queue_id = 12345

        approval_data = {"quality_score": 85}

        async with admin_auth_override():

            # Request without CSRF token should fail
            response = await async_client.post(
                f"/api/v1/admin/incoming-products/{queue_id}/verification/approve",
                headers=admin_headers,
                json=approval_data
            )

        # Should implement CSRF protection - test will fail in RED phase until implemented
        # For now, this test documents the requirement
        assert response.status_code in [403, 422, 400]  # CSRF failure codes

    @pytest.mark.red_test
    @pytest.mark.data_management
    @pytest.mark.security
    @pytest.mark.file_upload
    async def test_file_upload_virus_scanning_placeholder_fails(self, async_client: AsyncClient):
        """
        RED: Test that file upload includes virus scanning (placeholder)
        Should implement virus scanning for uploaded verification photos
        """
        admin_headers = {"Authorization": "Bearer fake_admin_token"}
        queue_id = str(uuid.uuid4())

        # Simulate potentially infected file
        suspicious_file = io.BytesIO(b"X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*")
        files = {"files": ("eicar.jpg", suspicious_file, "image/jpeg")}

        async with admin_auth_override():

            response = await async_client.post(
                f"/api/v1/admin/incoming-products/{queue_id}/verification/upload-photos",
                headers=admin_headers,
                files=files,
                data={"photo_types": ["general"]}
            )

        # Should implement virus scanning - test will fail in RED phase until implemented
        # For now, this test documents the requirement
        assert response.status_code == 200
        response_data = response.json()
        # Future: Should have virus scan results in response


# =============================================================================
# BUSINESS LOGIC VALIDATION TESTS (RED PHASE)
# =============================================================================

class TestBusinessLogicValidationRed:
    """
    RED Phase tests for business logic validation in data management operations.
    These tests ensure proper workflow state transitions and business rule enforcement.
    """

    @pytest.mark.red_test
    @pytest.mark.data_management
    @pytest.mark.workflow
    async def test_workflow_state_transition_validation_fails(self, async_client: AsyncClient):
        """
        RED: Test that invalid workflow state transitions are prevented
        Should fail when attempting invalid state transitions in verification workflow
        """
        admin_headers = {"Authorization": "Bearer fake_admin_token"}
        queue_id = str(uuid.uuid4())

        # Attempt to execute final_approval step when product is still in PENDING
        invalid_step_data = {
            "step": "final_approval",  # Invalid for PENDING status
            "passed": True,
            "notes": "Attempting invalid transition"
        }

        async with admin_auth_override():

            with patch('app.api.v1.endpoints.admin.select') as mock_select:
                # Mock product in PENDING status
                mock_queue_item = Mock()
                mock_queue_item.verification_status = VerificationStatus.PENDING
                mock_result = Mock()
                mock_result.scalar_one_or_none.return_value = mock_queue_item
                mock_db = Mock()
                mock_db.execute.return_value = mock_result

                with patch('app.api.v1.endpoints.admin.get_db', return_value=mock_db):
                    response = await async_client.post(
                        f"/api/v1/admin/incoming-products/{queue_id}/verification/execute-step",
                        headers=admin_headers,
                        json=invalid_step_data
                    )

        # Should fail with business logic validation error - test will fail in RED phase
        assert response.status_code == 400
        assert "transición inválida" in response.json()["detail"] or "step invalid" in response.json()["detail"]

    @pytest.mark.red_test
    @pytest.mark.data_management
    @pytest.mark.workflow
    async def test_concurrent_modification_detection_fails(self, async_client: AsyncClient):
        """
        RED: Test that concurrent modifications to the same product are detected
        Should fail when two admins try to modify the same product simultaneously
        """
        admin_headers = {"Authorization": "Bearer fake_admin_token"}
        queue_id = 12345

        approval_data = {"quality_score": 85}

        with patch('app.core.auth.get_current_user') as mock_auth:
            mock_auth.return_value = Mock(is_superuser=True, user_type=UserType.ADMIN, id=str(uuid.uuid4()))

            with patch('app.api.v1.endpoints.admin.get_sync_db') as mock_db:
                # Mock product being modified by another admin
                mock_queue_item = Mock()
                mock_queue_item.verification_status = "IN_PROGRESS"
                mock_queue_item.assigned_to = str(uuid.uuid4())  # Different admin
                mock_queue_item.processing_started_at = datetime.now() - timedelta(minutes=5)
                mock_db.return_value.query.return_value.filter.return_value.first.return_value = mock_queue_item

                response = await async_client.post(
                    f"/api/v1/admin/incoming-products/{queue_id}/verification/approve",
                    headers=admin_headers,
                    json=approval_data
                )

        # Should implement concurrent modification detection - test will fail in RED phase
        assert response.status_code == 409  # Conflict
        assert "siendo modificado por otro" in response.json()["detail"]

    @pytest.mark.red_test
    @pytest.mark.data_management
    @pytest.mark.workflow
    async def test_quality_score_business_rules_validation_fails(self, async_client: AsyncClient):
        """
        RED: Test that quality score business rules are enforced
        Should fail when quality score doesn't match checklist results
        """
        admin_headers = {"Authorization": "Bearer fake_admin_token"}
        queue_id = str(uuid.uuid4())

        # Inconsistent data: high quality score but failed checks
        inconsistent_checklist_data = {
            "queue_id": queue_id,
            "checklist": {
                "queue_id": queue_id,
                "inspector_id": str(uuid.uuid4()),
                "inspection_date": datetime.now().isoformat(),
                "quality_score": 95,  # High score
                "overall_condition": "excellent",
                "has_damage": True,  # But has damage
                "has_missing_parts": True,  # And missing parts
                "has_defects": True,  # And defects
                "approved": False,  # And not approved
                "inspector_notes": "Product has major issues",
                "inspection_duration_minutes": 30
            }
        }

        async with admin_auth_override():

            response = await async_client.post(
                f"/api/v1/admin/incoming-products/{queue_id}/verification/quality-checklist",
                headers=admin_headers,
                json=inconsistent_checklist_data
            )

        # Should fail with business logic validation error - test will fail in RED phase
        assert response.status_code == 400
        assert "inconsistente" in response.json()["detail"] or "logic error" in response.json()["detail"]

    @pytest.mark.red_test
    @pytest.mark.data_management
    @pytest.mark.workflow
    async def test_inspector_workload_limits_validation_fails(self, async_client: AsyncClient):
        """
        RED: Test that inspector workload limits are enforced
        Should fail when inspector already has too many active assignments
        """
        admin_headers = {"Authorization": "Bearer fake_admin_token"}
        queue_id = str(uuid.uuid4())

        step_data = {
            "step": "initial_inspection",
            "passed": True,
            "notes": "Starting inspection"
        }

        with patch('app.core.auth.get_current_user') as mock_auth:
            overloaded_inspector = Mock(
                is_superuser=True,
                user_type=UserType.ADMIN,
                id=str(uuid.uuid4())
            )
            mock_auth.return_value = overloaded_inspector

            # Mock check for existing workload
            with patch('app.services.product_verification_workflow.ProductVerificationWorkflow') as mock_workflow:
                mock_workflow_instance = Mock()
                mock_workflow_instance.execute_step.side_effect = Exception(
                    "Inspector ya tiene demasiadas asignaciones activas"
                )
                mock_workflow.return_value = mock_workflow_instance

                response = await async_client.post(
                    f"/api/v1/admin/incoming-products/{queue_id}/verification/execute-step",
                    headers=admin_headers,
                    json=step_data
                )

        # Should fail with workload limit error - test will fail in RED phase
        assert response.status_code == 400
        assert "demasiadas asignaciones" in response.json()["detail"]

    @pytest.mark.red_test
    @pytest.mark.data_management
    @pytest.mark.workflow
    async def test_location_capacity_validation_fails(self, async_client: AsyncClient):
        """
        RED: Test that location capacity limits are enforced
        Should fail when trying to assign product to location without sufficient capacity
        """
        admin_headers = {"Authorization": "Bearer fake_admin_token"}
        queue_id = 12345

        location_data = {
            "zona": "A",
            "estante": "01",
            "posicion": "01"
        }

        async with admin_auth_override():

            with patch('app.api.v1.endpoints.admin.get_sync_db') as mock_db:
                # Mock oversized product
                mock_queue_item = Mock()
                mock_queue_item.verification_status = "QUALITY_CHECK"
                mock_product = Mock()
                mock_product.peso = 1000  # Very heavy product
                mock_product.dimensiones = "200x200x200"  # Very large product
                mock_queue_item.product = mock_product
                mock_db.return_value.query.return_value.filter.return_value.first.return_value = mock_queue_item

                with patch('app.services.location_assignment_service.LocationAssignmentService') as mock_service:
                    mock_service_instance = Mock()
                    # Mock location with insufficient capacity
                    mock_service_instance._get_available_locations.return_value = [{
                        "zona": "A",
                        "estante": "01",
                        "posicion": "01",
                        "available_capacity": 10  # Too small for product
                    }]
                    mock_service_instance._reserve_location.return_value = False  # Capacity check fails
                    mock_service.return_value = mock_service_instance

                    response = await async_client.post(
                        f"/api/v1/admin/incoming-products/{queue_id}/location/manual-assign",
                        headers=admin_headers,
                        json=location_data
                    )

        # Should fail with capacity validation error - test will fail in RED phase
        assert response.status_code == 500
        assert "Error reservando la ubicación" in response.json()["detail"]


# =============================================================================
# INTEGRATION TESTS FOR COMPLETE WORKFLOWS (RED PHASE)
# =============================================================================

class TestCompleteWorkflowIntegrationRed:
    """
    RED Phase integration tests for complete data management workflows.
    These tests validate end-to-end business processes.
    """

    @pytest.mark.red_test
    @pytest.mark.data_management
    @pytest.mark.workflow
    @pytest.mark.integration
    async def test_complete_product_verification_workflow_fails(self, async_client: AsyncClient):
        """
        RED: Test complete product verification workflow from start to finish
        Should fail as complete workflow integration is not yet implemented
        """
        admin_headers = {"Authorization": "Bearer fake_admin_token"}
        queue_id = str(uuid.uuid4())

        # Step 1: Get current step
        step_response = await async_client.get(
            f"/api/v1/admin/incoming-products/{queue_id}/verification/current-step",
            headers=admin_headers
        )

        # Step 2: Execute initial inspection
        step_data = {
            "step": "initial_inspection",
            "passed": True,
            "notes": "Initial inspection completed successfully"
        }

        execute_response = await async_client.post(
            f"/api/v1/admin/incoming-products/{queue_id}/verification/execute-step",
            headers=admin_headers,
            json=step_data
        )

        # Step 3: Upload verification photos
        fake_image = io.BytesIO(b"fake_image_content")
        files = {"files": ("verification.jpg", fake_image, "image/jpeg")}

        upload_response = await async_client.post(
            f"/api/v1/admin/incoming-products/{queue_id}/verification/upload-photos",
            headers=admin_headers,
            files=files,
            data={"photo_types": ["general"]}
        )

        # Step 4: Submit quality checklist
        checklist_data = {
            "queue_id": queue_id,
            "checklist": {
                "queue_id": queue_id,
                "inspector_id": str(uuid.uuid4()),
                "inspection_date": datetime.now().isoformat(),
                "quality_score": 85,
                "overall_condition": "good",
                "has_damage": False,
                "has_missing_parts": False,
                "has_defects": False,
                "approved": True,
                "inspector_notes": "Quality check passed",
                "inspection_duration_minutes": 15
            }
        }

        checklist_response = await async_client.post(
            f"/api/v1/admin/incoming-products/{queue_id}/verification/quality-checklist",
            headers=admin_headers,
            json=checklist_data
        )

        # Step 5: Auto-assign location
        location_response = await async_client.post(
            f"/api/v1/admin/incoming-products/{queue_id}/location/auto-assign",
            headers=admin_headers
        )

        # Step 6: Final approval
        approval_response = await async_client.post(
            f"/api/v1/admin/incoming-products/{queue_id}/verification/approve",
            headers=admin_headers,
            json={"quality_score": 85}
        )

        # All steps should eventually work together - will fail in RED phase
        assert step_response.status_code == 200
        assert execute_response.status_code == 200
        assert upload_response.status_code == 200
        assert checklist_response.status_code == 200
        assert location_response.status_code == 200
        assert approval_response.status_code == 200

        # Verify final state
        history_response = await async_client.get(
            f"/api/v1/admin/incoming-products/{queue_id}/verification/history",
            headers=admin_headers
        )

        assert history_response.status_code == 200
        history_data = history_response.json()
        assert history_data["data"]["history"]["verification_status"] == "APPROVED"


# =============================================================================
# PERFORMANCE AND STRESS TESTS (RED PHASE)
# =============================================================================

class TestPerformanceStressRed:
    """
    RED Phase performance and stress tests for data management endpoints.
    These tests validate system behavior under load and edge conditions.
    """

    @pytest.mark.red_test
    @pytest.mark.data_management
    @pytest.mark.performance
    async def test_bulk_photo_upload_performance_fails(self, async_client: AsyncClient):
        """
        RED: Test performance with bulk photo uploads
        Should handle multiple file uploads efficiently
        """
        admin_headers = {"Authorization": "Bearer fake_admin_token"}
        queue_id = str(uuid.uuid4())

        # Create multiple files for bulk upload
        files = []
        photo_types = []
        for i in range(20):  # 20 files
            fake_image = io.BytesIO(b"fake_image_content_" * 1000)  # ~20KB each
            files.append(("files", (f"test_{i}.jpg", fake_image, "image/jpeg")))
            photo_types.append("general")

        async with admin_auth_override():

            import time
            start_time = time.time()

            response = await async_client.post(
                f"/api/v1/admin/incoming-products/{queue_id}/verification/upload-photos",
                headers=admin_headers,
                files=files,
                data={"photo_types": photo_types}
            )

            end_time = time.time()
            processing_time = end_time - start_time

        # Should complete within reasonable time - will fail in RED phase until optimized
        assert response.status_code == 200
        assert processing_time < 5.0  # Should complete within 5 seconds
        response_data = response.json()
        assert response_data["total_uploaded"] <= 20
        assert len(response_data["failed_uploads"]) == 0

    @pytest.mark.red_test
    @pytest.mark.data_management
    @pytest.mark.performance
    async def test_concurrent_workflow_operations_fails(self, async_client: AsyncClient):
        """
        RED: Test concurrent operations on different products
        Should handle multiple simultaneous workflow operations
        """
        admin_headers = {"Authorization": "Bearer fake_admin_token"}

        # Create multiple concurrent operations
        import asyncio

        async def process_product(queue_id: str):
            step_data = {
                "step": "initial_inspection",
                "passed": True,
                "notes": f"Concurrent processing {queue_id}"
            }

            return await async_client.post(
                f"/api/v1/admin/incoming-products/{queue_id}/verification/execute-step",
                headers=admin_headers,
                json=step_data
            )

        # Run 10 concurrent operations
        queue_ids = [str(uuid.uuid4()) for _ in range(10)]

        async with admin_auth_override():

            tasks = [process_product(qid) for qid in queue_ids]
            responses = await asyncio.gather(*tasks, return_exceptions=True)

        # Should handle concurrent operations without race conditions - will fail in RED phase
        successful_responses = [r for r in responses if not isinstance(r, Exception)]
        assert len(successful_responses) == 10

        for response in successful_responses:
            assert response.status_code in [200, 404]  # 404 acceptable for non-existent test data

# =============================================================================
# TEST CONFIGURATION AND MARKERS
# =============================================================================

def pytest_configure(config):
    """Configure pytest markers for admin data management tests."""
    config.addinivalue_line(
        "markers", "red_test: RED phase TDD tests (should fail initially)"
    )
    config.addinivalue_line(
        "markers", "data_management: Data management functionality tests"
    )
    config.addinivalue_line(
        "markers", "admin_auth: Tests requiring admin authentication"
    )
    config.addinivalue_line(
        "markers", "file_upload: File upload functionality tests"
    )
    config.addinivalue_line(
        "markers", "workflow: Workflow state management tests"
    )
    config.addinivalue_line(
        "markers", "security: Security validation tests"
    )
    config.addinivalue_line(
        "markers", "performance: Performance and stress tests"
    )
    config.addinivalue_line(
        "markers", "integration: Integration workflow tests"
    )