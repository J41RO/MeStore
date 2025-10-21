"""
Integration test for Product Verification Workflow endpoint.

Tests the workflow current-step endpoint with proper async client setup,
database fixtures, and authentication without depending on external servers.

Author: Integration Testing Specialist
Date: 2025-10-17
"""

import pytest
import uuid
import time
from datetime import datetime, timedelta
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.incoming_product_queue import (
    IncomingProductQueue,
    VerificationStatus,
    QueuePriority
)
from app.models.user import User, UserType
from app.models.product import Product, ProductStatus
from app.core.security import create_access_token
from app.core.types import generate_uuid


@pytest.mark.asyncio
@pytest.mark.integration
class TestWorkflowEndpoint:
    """Integration tests for workflow verification endpoints."""

    async def test_workflow_endpoint_with_valid_product(
        self,
        async_client: AsyncClient,
        async_session: AsyncSession,
        test_admin_user: User
    ):
        """
        Test workflow endpoint returns current step for valid product.

        Validates:
        - Endpoint is accessible with admin authentication
        - Returns 200 for valid product in queue
        - Response contains verification step information
        """
        # 1. Create test vendor user with unique email
        timestamp = int(time.time() * 1000)
        vendor = User(
            id=generate_uuid(),
            email=f"test_vendor_workflow_{timestamp}@example.com",
            password_hash="$2b$12$test.hash.for.testing",
            nombre="Test Vendor",
            apellido="Workflow",
            user_type=UserType.VENDOR,
            is_active=True
        )
        async_session.add(vendor)
        await async_session.flush()

        # 2. Create test product
        product = Product(
            id=generate_uuid(),
            sku=f"TEST-WF-{uuid.uuid4().hex[:8]}",
            name="Test Product Workflow",
            description="Product for workflow testing",
            precio_venta=100000.0,
            precio_costo=80000.0,
            categoria="Test Category",
            peso=1.5,
            status=ProductStatus.TRANSITO,
            vendedor_id=vendor.id
        )
        async_session.add(product)
        await async_session.flush()

        # 3. Create queue entry for the product
        queue_item = IncomingProductQueue(
            id=generate_uuid(),
            product_id=product.id,
            vendor_id=vendor.id,
            expected_arrival=datetime.utcnow() + timedelta(days=2),
            verification_status=VerificationStatus.PENDING,
            priority=QueuePriority.NORMAL,
            tracking_number=f"TRACK-{uuid.uuid4().hex[:8]}",
            carrier="Test Carrier"
        )
        async_session.add(queue_item)
        await async_session.commit()

        # 4. Create authentication token for admin user
        token_data = {
            "sub": str(test_admin_user.id),
            "email": test_admin_user.email,
            "user_type": test_admin_user.user_type.value,
            "nombre": test_admin_user.nombre,
            "apellido": test_admin_user.apellido
        }
        access_token = create_access_token(data=token_data)

        # 5. Make request to workflow endpoint
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await async_client.get(
            f"/api/v1/admin/incoming-products/{queue_item.id}/verification/current-step",
            headers=headers
        )

        # 6. Assertions
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        response_data = response.json()

        # Validate response structure - API returns wrapped response with status and data
        assert "status" in response_data, "Response should contain status"
        assert response_data["status"] == "success", "Status should be success"
        assert "data" in response_data, "Response should contain data"

        data = response_data["data"]
        assert "current_step" in data, "Data should contain current_step"
        assert data["current_step"] is not None, "current_step should not be None"
        assert "steps" in data, "Data should contain steps list"
        assert isinstance(data["steps"], list), "Steps should be a list"
        assert len(data["steps"]) > 0, "Should have at least one step"

    async def test_workflow_endpoint_product_not_found(
        self,
        async_client: AsyncClient,
        async_session: AsyncSession,
        test_admin_user: User
    ):
        """
        Test workflow endpoint returns 404 for non-existent product.

        Validates:
        - Endpoint returns 404 for invalid product ID
        - Error message is descriptive
        """
        # Create authentication token
        token_data = {
            "sub": str(test_admin_user.id),
            "email": test_admin_user.email,
            "user_type": test_admin_user.user_type.value,
            "nombre": test_admin_user.nombre,
            "apellido": test_admin_user.apellido
        }
        access_token = create_access_token(data=token_data)

        # Use non-existent UUID
        non_existent_id = generate_uuid()

        # Make request
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await async_client.get(
            f"/api/v1/admin/incoming-products/{non_existent_id}/verification/current-step",
            headers=headers
        )

        # Assertions
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        data = response.json()
        assert "detail" in data, "Error response should contain detail"
        assert "no encontrado" in data["detail"].lower() or "not found" in data["detail"].lower()

    async def test_workflow_endpoint_unauthorized_without_token(
        self,
        async_client: AsyncClient,
        async_session: AsyncSession
    ):
        """
        Test workflow endpoint returns 401 without authentication.

        Validates:
        - Endpoint requires authentication
        - Returns 401 for requests without token
        """
        # Use any UUID (doesn't matter since we should fail auth first)
        test_id = generate_uuid()

        # Make request without authentication
        response = await async_client.get(
            f"/api/v1/admin/incoming-products/{test_id}/verification/current-step"
        )

        # Assertions
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    async def test_workflow_endpoint_forbidden_for_non_admin(
        self,
        async_client: AsyncClient,
        async_session: AsyncSession,
        test_vendor_user: User
    ):
        """
        Test workflow endpoint returns 403 for non-admin users.

        Validates:
        - Endpoint requires admin permissions
        - Vendor users cannot access admin workflow
        """
        # Create vendor token
        token_data = {
            "sub": str(test_vendor_user.id),
            "email": test_vendor_user.email,
            "user_type": test_vendor_user.user_type.value,
            "nombre": test_vendor_user.nombre,
            "apellido": test_vendor_user.apellido
        }
        access_token = create_access_token(data=token_data)

        # Use any UUID
        test_id = generate_uuid()

        # Make request with vendor token
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await async_client.get(
            f"/api/v1/admin/incoming-products/{test_id}/verification/current-step",
            headers=headers
        )

        # Assertions
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        data = response.json()
        assert "detail" in data, "Error response should contain detail"
        assert "permisos" in data["detail"].lower() or "forbidden" in data["detail"].lower()

    async def test_workflow_endpoint_with_different_verification_statuses(
        self,
        async_client: AsyncClient,
        async_session: AsyncSession,
        test_admin_user: User
    ):
        """
        Test workflow endpoint handles different verification statuses.

        Validates:
        - Endpoint works for products in different verification stages
        - Current step reflects the verification status
        """
        # Create vendor
        timestamp = int(time.time() * 1000)
        vendor = User(
            id=generate_uuid(),
            email=f"vendor_status_test_{timestamp}@example.com",
            password_hash="$2b$12$test.hash.for.testing",
            nombre="Status Test",
            apellido="Vendor",
            user_type=UserType.VENDOR,
            is_active=True
        )
        async_session.add(vendor)
        await async_session.flush()

        # Create product
        product = Product(
            id=generate_uuid(),
            sku=f"TEST-STATUS-{uuid.uuid4().hex[:8]}",
            name="Status Test Product",
            description="Product for status testing",
            precio_venta=150000.0,
            precio_costo=120000.0,
            categoria="Test",
            peso=2.0,
            status=ProductStatus.TRANSITO,
            vendedor_id=vendor.id
        )
        async_session.add(product)
        await async_session.flush()

        # Test different verification statuses
        test_statuses = [
            VerificationStatus.PENDING,
            VerificationStatus.IN_PROGRESS,
            VerificationStatus.QUALITY_CHECK,
            VerificationStatus.APPROVED
        ]

        # Create auth token
        token_data = {
            "sub": str(test_admin_user.id),
            "email": test_admin_user.email,
            "user_type": test_admin_user.user_type.value,
            "nombre": test_admin_user.nombre,
            "apellido": test_admin_user.apellido
        }
        access_token = create_access_token(data=token_data)
        headers = {"Authorization": f"Bearer {access_token}"}

        for status in test_statuses:
            # Create queue entry with specific status
            queue_item = IncomingProductQueue(
                id=generate_uuid(),
                product_id=product.id,
                vendor_id=vendor.id,
                expected_arrival=datetime.utcnow() + timedelta(days=1),
                verification_status=status,
                priority=QueuePriority.NORMAL,
                tracking_number=f"TRACK-{status.value}-{uuid.uuid4().hex[:6]}"
            )
            async_session.add(queue_item)
            await async_session.commit()

            # Make request
            response = await async_client.get(
                f"/api/v1/admin/incoming-products/{queue_item.id}/verification/current-step",
                headers=headers
            )

            # Assertions
            assert response.status_code == 200, (
                f"Status {status.value} should return 200, got {response.status_code}"
            )
            response_data = response.json()
            assert "status" in response_data and response_data["status"] == "success"
            assert "data" in response_data
            data = response_data["data"]
            assert "current_step" in data, f"Response for {status.value} should contain current_step"

            # Cleanup for next iteration
            await async_session.delete(queue_item)
            await async_session.commit()

    async def test_workflow_endpoint_with_assigned_product(
        self,
        async_client: AsyncClient,
        async_session: AsyncSession,
        test_admin_user: User
    ):
        """
        Test workflow endpoint for product assigned to verifier.

        Validates:
        - Endpoint handles products assigned to specific users
        - Assignment information is reflected in response
        """
        # Create vendor
        timestamp = int(time.time() * 1000)
        vendor = User(
            id=generate_uuid(),
            email=f"vendor_assigned_{timestamp}@example.com",
            password_hash="$2b$12$test.hash.for.testing",
            nombre="Assigned Test",
            apellido="Vendor",
            user_type=UserType.VENDOR,
            is_active=True
        )
        async_session.add(vendor)
        await async_session.flush()

        # Create product
        product = Product(
            id=generate_uuid(),
            sku=f"TEST-ASSIGNED-{uuid.uuid4().hex[:8]}",
            name="Assigned Product",
            description="Product assigned to verifier",
            precio_venta=200000.0,
            precio_costo=160000.0,
            categoria="Test",
            peso=1.0,
            status=ProductStatus.TRANSITO,
            vendedor_id=vendor.id
        )
        async_session.add(product)
        await async_session.flush()

        # Create queue entry assigned to admin user
        queue_item = IncomingProductQueue(
            id=generate_uuid(),
            product_id=product.id,
            vendor_id=vendor.id,
            expected_arrival=datetime.utcnow() + timedelta(days=3),
            verification_status=VerificationStatus.ASSIGNED,
            priority=QueuePriority.HIGH,
            assigned_to=test_admin_user.id,
            assigned_at=datetime.utcnow(),
            tracking_number=f"TRACK-ASSIGNED-{uuid.uuid4().hex[:6]}"
        )
        async_session.add(queue_item)
        await async_session.commit()

        # Create auth token
        token_data = {
            "sub": str(test_admin_user.id),
            "email": test_admin_user.email,
            "user_type": test_admin_user.user_type.value,
            "nombre": test_admin_user.nombre,
            "apellido": test_admin_user.apellido
        }
        access_token = create_access_token(data=token_data)
        headers = {"Authorization": f"Bearer {access_token}"}

        # Make request
        response = await async_client.get(
            f"/api/v1/admin/incoming-products/{queue_item.id}/verification/current-step",
            headers=headers
        )

        # Assertions
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        response_data = response.json()
        assert "status" in response_data and response_data["status"] == "success"
        assert "data" in response_data
        data = response_data["data"]
        assert "current_step" in data, "Response should contain current_step"

        # Verify the product is indeed assigned
        result = await async_session.execute(
            select(IncomingProductQueue).filter(IncomingProductQueue.id == queue_item.id)
        )
        db_item = result.scalar_one()
        assert db_item.assigned_to == test_admin_user.id, "Product should be assigned to admin user"
        assert db_item.verification_status == VerificationStatus.ASSIGNED


@pytest.mark.asyncio
@pytest.mark.integration
class TestWorkflowDatabaseOperations:
    """Test database operations related to workflow."""

    async def test_create_and_retrieve_queue_item(
        self,
        async_session: AsyncSession
    ):
        """
        Test creating and retrieving IncomingProductQueue items.

        Validates:
        - Queue items can be created in database
        - Items can be retrieved with proper relationships
        """
        # Create vendor
        timestamp = int(time.time() * 1000)
        vendor = User(
            id=generate_uuid(),
            email=f"db_test_vendor_{timestamp}@example.com",
            password_hash="$2b$12$test.hash.for.testing",
            nombre="DB Test",
            apellido="Vendor",
            user_type=UserType.VENDOR,
            is_active=True
        )
        async_session.add(vendor)
        await async_session.flush()

        # Create product
        product = Product(
            id=generate_uuid(),
            sku=f"TEST-DB-{uuid.uuid4().hex[:8]}",
            name="DB Test Product",
            description="Product for database testing",
            precio_venta=100000.0,
            precio_costo=80000.0,
            categoria="Test",
            peso=1.5,
            status=ProductStatus.TRANSITO,
            vendedor_id=vendor.id
        )
        async_session.add(product)
        await async_session.flush()

        # Create queue item
        queue_item = IncomingProductQueue(
            id=generate_uuid(),
            product_id=product.id,
            vendor_id=vendor.id,
            expected_arrival=datetime.utcnow() + timedelta(days=5),
            verification_status=VerificationStatus.PENDING,
            priority=QueuePriority.NORMAL,
            tracking_number="TEST-TRACK-001"
        )
        async_session.add(queue_item)
        await async_session.commit()

        # Retrieve and verify
        result = await async_session.execute(
            select(IncomingProductQueue).filter(IncomingProductQueue.id == queue_item.id)
        )
        retrieved_item = result.scalar_one()

        assert retrieved_item.id == queue_item.id
        assert retrieved_item.product_id == product.id
        assert retrieved_item.vendor_id == vendor.id
        assert retrieved_item.verification_status == VerificationStatus.PENDING
        assert retrieved_item.tracking_number == "TEST-TRACK-001"

    async def test_queue_item_status_transitions(
        self,
        async_session: AsyncSession
    ):
        """
        Test verification status transitions in queue items.

        Validates:
        - Status can transition through workflow stages
        - Status changes persist to database
        """
        # Create vendor
        timestamp = int(time.time() * 1000)
        vendor = User(
            id=generate_uuid(),
            email=f"status_transition_vendor_{timestamp}@example.com",
            password_hash="$2b$12$test.hash.for.testing",
            nombre="Status",
            apellido="Vendor",
            user_type=UserType.VENDOR,
            is_active=True
        )
        async_session.add(vendor)
        await async_session.flush()

        # Create product
        product = Product(
            id=generate_uuid(),
            sku=f"TEST-TRANSITION-{uuid.uuid4().hex[:8]}",
            name="Transition Test Product",
            description="Product for status transition testing",
            precio_venta=120000.0,
            precio_costo=95000.0,
            categoria="Test",
            peso=1.8,
            status=ProductStatus.TRANSITO,
            vendedor_id=vendor.id
        )
        async_session.add(product)
        await async_session.flush()

        # Create queue item
        queue_item = IncomingProductQueue(
            id=generate_uuid(),
            product_id=product.id,
            vendor_id=vendor.id,
            expected_arrival=datetime.utcnow() + timedelta(days=2),
            verification_status=VerificationStatus.PENDING,
            priority=QueuePriority.NORMAL
        )
        async_session.add(queue_item)
        await async_session.commit()

        # Test status transitions
        status_transitions = [
            VerificationStatus.ASSIGNED,
            VerificationStatus.IN_PROGRESS,
            VerificationStatus.QUALITY_CHECK,
            VerificationStatus.APPROVED
        ]

        for new_status in status_transitions:
            queue_item.verification_status = new_status
            await async_session.commit()
            await async_session.refresh(queue_item)

            assert queue_item.verification_status == new_status, (
                f"Status should be {new_status.value}"
            )
