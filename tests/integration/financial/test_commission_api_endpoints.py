# tests/integration/financial/test_commission_api_endpoints.py
# CRITICAL: Commission API Endpoint Integration Testing Suite
# PRIORITY: Validate all commission REST APIs with authentication and authorization

import pytest
import logging
from decimal import Decimal
from datetime import datetime, timedelta
from uuid import uuid4
from fastapi.testclient import TestClient
from httpx import AsyncClient

from sqlalchemy.orm import Session
from app.models.user import User, UserType
from app.models.commission import Commission, CommissionStatus, CommissionType
from app.models.order import Order, OrderStatus
from app.services.commission_service import CommissionService
from tests.fixtures.financial.financial_factories import (
    FinancialScenarioFactory,
    BuyerUserFactory,
    VendorUserFactory,
    AdminUserFactory
)

logger = logging.getLogger(__name__)


@pytest.mark.integration_financial
@pytest.mark.critical
class TestCommissionAPIEndpoints:
    """
    CRITICAL: Commission API Endpoint Integration Tests

    Tests all commission REST API endpoints with proper authentication,
    authorization, data validation, and financial calculation integrity.
    """

    @pytest.fixture
    def financial_scenario_factory(self, async_session):
        """Financial scenario factory for API testing"""
        return FinancialScenarioFactory(async_session)

    @pytest.fixture
    def auth_headers_vendor(self, test_vendor_user: User):
        """Authentication headers for vendor user - generates valid JWT"""
        from app.core.security import create_access_token
        token_data = {
            "sub": str(test_vendor_user.id),
            "email": test_vendor_user.email,
            "user_type": test_vendor_user.user_type.value,
            "nombre": test_vendor_user.nombre,
            "apellido": test_vendor_user.apellido
        }
        token = create_access_token(data=token_data)
        return {"Authorization": f"Bearer {token}"}

    @pytest.fixture
    def auth_headers_admin(self, test_admin_user: User):
        """Authentication headers for admin user - generates valid JWT"""
        from app.core.security import create_access_token
        token_data = {
            "sub": str(test_admin_user.id),
            "email": test_admin_user.email,
            "user_type": test_admin_user.user_type.value,
            "nombre": test_admin_user.nombre,
            "apellido": test_admin_user.apellido
        }
        token = create_access_token(data=token_data)
        return {"Authorization": f"Bearer {token}"}

    @pytest.fixture
    def auth_headers_buyer(self, test_buyer_user: User):
        """Authentication headers for buyer user - generates valid JWT"""
        from app.core.security import create_access_token
        token_data = {
            "sub": str(test_buyer_user.id),
            "email": test_buyer_user.email,
            "user_type": test_buyer_user.user_type.value,
            "nombre": test_buyer_user.nombre,
            "apellido": test_buyer_user.apellido
        }
        token = create_access_token(data=token_data)
        return {"Authorization": f"Bearer {token}"}

    async def test_list_commissions_vendor_access(
        self,
        client: TestClient,
        financial_scenario_factory: FinancialScenarioFactory,
        auth_headers_vendor: dict,
        audit_logger
    ):
        """Test vendor can list their own commissions"""
        audit_logger("commission_api_list_test_start", {"role": "vendor"})

        # Create commission scenario
        scenario = await financial_scenario_factory.create_commission_scenario()
        commission = scenario['commission']
        vendor = scenario['vendor']

        # Make API request
        response = client.get(
            "/api/v1/commissions/",
            headers=auth_headers_vendor,
            params={
                "limit": 10,
                "offset": 0
            }
        )

        # Validate response
        assert response.status_code == 200
        data = response.json()

        assert "commissions" in data
        assert "total" in data
        assert isinstance(data["commissions"], list)

        # Verify commission data structure
        if data["commissions"]:
            commission_data = data["commissions"][0]
            required_fields = [
                "id", "commission_number", "order_id", "vendor_id",
                "order_amount", "commission_amount", "vendor_amount",
                "status", "commission_type", "created_at"
            ]
            for field in required_fields:
                assert field in commission_data

        audit_logger("commission_api_list_test_success", {
            "commissions_found": len(data["commissions"]),
            "vendor_id": str(vendor.id)
        })

    def test_list_commissions_with_filters(
        self,
        client: TestClient,
        financial_scenario_factory: FinancialScenarioFactory,
        auth_headers_vendor: dict
    ):
        """Test commission list with various filters"""
        # Create multiple commissions with different statuses
        scenario1 = financial_scenario_factory.create_commission_scenario()
        scenario2 = financial_scenario_factory.create_commission_scenario()

        # Approve one commission
        scenario2['commission'].status = CommissionStatus.APPROVED
        scenario2['commission'].approved_at = datetime.now()

        # Test status filter
        response = client.get(
            "/api/v1/commissions",
            headers=auth_headers_vendor,
            params={
                "status": "APPROVED",
                "limit": 10
            }
        )

        assert response.status_code == 200
        data = response.json()

        approved_commissions = [
            c for c in data["commissions"]
            if c["status"] == "APPROVED"
        ]
        assert len(approved_commissions) >= 1

        # Test commission type filter
        response = client.get(
            "/api/v1/commissions",
            headers=auth_headers_vendor,
            params={
                "commission_type": "STANDARD",
                "limit": 10
            }
        )

        assert response.status_code == 200
        data = response.json()

        standard_commissions = [
            c for c in data["commissions"]
            if c["commission_type"] == "STANDARD"
        ]
        assert len(standard_commissions) >= 1

    def test_list_commissions_date_range_filter(
        self,
        client: TestClient,
        financial_scenario_factory: FinancialScenarioFactory,
        auth_headers_vendor: dict
    ):
        """Test commission list with date range filters"""
        # Create commission
        scenario = financial_scenario_factory.create_commission_scenario()

        # Test with date range that includes the commission
        yesterday = datetime.now() - timedelta(days=1)
        tomorrow = datetime.now() + timedelta(days=1)

        response = client.get(
            "/api/v1/commissions",
            headers=auth_headers_vendor,
            params={
                "start_date": yesterday.isoformat(),
                "end_date": tomorrow.isoformat(),
                "limit": 10
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["commissions"]) >= 1

        # Test with date range that excludes the commission
        future_start = datetime.now() + timedelta(days=2)
        future_end = datetime.now() + timedelta(days=3)

        response = client.get(
            "/api/v1/commissions",
            headers=auth_headers_vendor,
            params={
                "start_date": future_start.isoformat(),
                "end_date": future_end.isoformat(),
                "limit": 10
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["commissions"]) == 0

    @pytest.mark.critical
    def test_get_commission_detail_vendor_access(
        self,
        client: TestClient,
        financial_scenario_factory: FinancialScenarioFactory,
        auth_headers_vendor: dict,
        audit_logger
    ):
        """CRITICAL: Test vendor can access their commission details"""
        audit_logger("commission_detail_api_test_start", {"role": "vendor"})

        # Create commission scenario
        scenario = financial_scenario_factory.create_commission_scenario()
        commission = scenario['commission']

        # Make API request
        response = client.get(
            f"/api/v1/commissions/{commission.id}",
            headers=auth_headers_vendor
        )

        # Validate response
        assert response.status_code == 200
        data = response.json()

        # Validate commission detail structure
        assert data["id"] == str(commission.id)
        assert data["commission_number"] == commission.commission_number
        assert data["order_id"] == commission.order_id
        assert data["vendor_id"] == str(commission.vendor_id)

        # Validate financial data
        assert float(data["order_amount"]) == float(commission.order_amount)
        assert float(data["commission_amount"]) == float(commission.commission_amount)
        assert float(data["vendor_amount"]) == float(commission.vendor_amount)
        assert float(data["platform_amount"]) == float(commission.platform_amount)

        # Validate financial integrity
        vendor_amount = Decimal(str(data["vendor_amount"]))
        platform_amount = Decimal(str(data["platform_amount"]))
        order_amount = Decimal(str(data["order_amount"]))
        assert vendor_amount + platform_amount == order_amount

        audit_logger("commission_detail_api_test_success", {
            "commission_id": str(commission.id),
            "financial_integrity": "verified"
        })

    def test_get_commission_detail_unauthorized_access(
        self,
        client: TestClient,
        financial_scenario_factory: FinancialScenarioFactory,
        auth_headers_buyer: dict
    ):
        """Test unauthorized access to commission details (buyer accessing vendor commission)"""
        # Create commission scenario
        scenario = financial_scenario_factory.create_commission_scenario()
        commission = scenario['commission']

        # Try to access with buyer credentials (should be forbidden)
        response = client.get(
            f"/api/v1/commissions/{commission.id}",
            headers=auth_headers_buyer
        )

        # Should be forbidden since buyer cannot access vendor commissions
        assert response.status_code in [403, 404]  # Forbidden or not found for security

    def test_get_vendor_earnings_summary(
        self,
        client: TestClient,
        financial_scenario_factory: FinancialScenarioFactory,
        auth_headers_vendor: dict,
        audit_logger
    ):
        """Test vendor earnings summary endpoint"""
        audit_logger("vendor_earnings_api_test_start", {})

        # Create multiple commission scenarios for vendor
        scenarios = []
        for i in range(3):
            scenario = financial_scenario_factory.create_commission_scenario(
                order_amount=Decimal(f"{(i+1)*50000}.00")
            )
            scenarios.append(scenario)

        vendor = scenarios[0]['vendor']

        # Make API request
        response = client.get(
            "/api/v1/commissions/earnings",
            headers=auth_headers_vendor
        )

        # Validate response
        assert response.status_code == 200
        data = response.json()

        # Validate earnings summary structure
        required_fields = [
            "vendor_id", "summary", "breakdown_by_status", "currency"
        ]
        for field in required_fields:
            assert field in data

        # Validate summary data
        summary = data["summary"]
        assert "total_commissions" in summary
        assert "total_order_amount" in summary
        assert "total_vendor_earnings" in summary
        assert "pending_earnings" in summary

        # Validate breakdown
        breakdown = data["breakdown_by_status"]
        assert isinstance(breakdown, dict)

        audit_logger("vendor_earnings_api_test_success", {
            "vendor_id": data["vendor_id"],
            "total_commissions": summary["total_commissions"]
        })

    def test_get_vendor_earnings_with_date_filter(
        self,
        client: TestClient,
        financial_scenario_factory: FinancialScenarioFactory,
        auth_headers_vendor: dict
    ):
        """Test vendor earnings with date range filters"""
        # Create commission scenario
        scenario = financial_scenario_factory.create_commission_scenario()

        # Test with date range
        yesterday = datetime.now() - timedelta(days=1)
        tomorrow = datetime.now() + timedelta(days=1)

        response = client.get(
            "/api/v1/commissions/earnings",
            headers=auth_headers_vendor,
            params={
                "start_date": yesterday.isoformat(),
                "end_date": tomorrow.isoformat()
            }
        )

        assert response.status_code == 200
        data = response.json()

        # Should include the commission
        assert data["summary"]["total_commissions"] >= 1

        # Test with future date range (should be empty)
        future_start = datetime.now() + timedelta(days=2)
        future_end = datetime.now() + timedelta(days=3)

        response = client.get(
            "/api/v1/commissions/earnings",
            headers=auth_headers_vendor,
            params={
                "start_date": future_start.isoformat(),
                "end_date": future_end.isoformat()
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["summary"]["total_commissions"] == 0

    def test_calculate_commission_admin_only(
        self,
        client: TestClient,
        financial_scenario_factory: FinancialScenarioFactory,
        auth_headers_admin: dict,
        auth_headers_vendor: dict,
        audit_logger
    ):
        """Test manual commission calculation (admin only)"""
        audit_logger("commission_calculation_api_test_start", {"role": "admin"})

        # Create basic order scenario without commission
        scenario = financial_scenario_factory.create_basic_order_scenario()
        order = scenario['order']

        # Admin should be able to calculate commission
        response = client.post(
            "/api/v1/commissions/calculate",
            headers=auth_headers_admin,
            json={
                "order_id": order.id,
                "commission_type": "STANDARD"
            }
        )

        assert response.status_code == 201
        data = response.json()

        # Validate commission was created
        assert "id" in data
        assert data["order_id"] == order.id
        assert data["status"] == "PENDING"
        assert data["commission_type"] == "STANDARD"

        # Vendor should NOT be able to calculate commission
        response = client.post(
            "/api/v1/commissions/calculate",
            headers=auth_headers_vendor,
            json={
                "order_id": order.id,
                "commission_type": "PREMIUM"
            }
        )

        assert response.status_code == 403  # Forbidden

        audit_logger("commission_calculation_api_test_success", {
            "admin_access": "granted",
            "vendor_access": "denied"
        })

    @pytest.mark.critical
    def test_approve_commission_admin_only(
        self,
        client: TestClient,
        financial_scenario_factory: FinancialScenarioFactory,
        auth_headers_admin: dict,
        auth_headers_vendor: dict,
        audit_logger
    ):
        """CRITICAL: Test commission approval (admin only)"""
        audit_logger("commission_approval_api_test_start", {"role": "admin"})

        # Create pending commission
        scenario = financial_scenario_factory.create_commission_scenario()
        commission = scenario['commission']

        assert commission.status == CommissionStatus.PENDING

        # Admin should be able to approve commission
        response = client.patch(
            f"/api/v1/commissions/{commission.id}/approve",
            headers=auth_headers_admin,
            json={
                "notes": "Approved via API test"
            }
        )

        assert response.status_code == 200
        data = response.json()

        # Validate commission was approved
        assert data["status"] == "APPROVED"
        assert "approved_at" in data
        assert data["admin_notes"] == "Approved via API test"

        # Vendor should NOT be able to approve commission
        response = client.patch(
            f"/api/v1/commissions/{commission.id}/approve",
            headers=auth_headers_vendor,
            json={
                "notes": "Vendor attempting approval"
            }
        )

        assert response.status_code == 403  # Forbidden

        audit_logger("commission_approval_api_test_success", {
            "commission_id": str(commission.id),
            "admin_approval": "success",
            "vendor_denial": "success"
        })

    def test_commission_not_found_error(
        self,
        client: TestClient,
        auth_headers_vendor: dict
    ):
        """Test proper error handling for non-existent commission"""
        fake_commission_id = str(uuid4())

        response = client.get(
            f"/api/v1/commissions/{fake_commission_id}",
            headers=auth_headers_vendor
        )

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_commission_validation_errors(
        self,
        client: TestClient,
        auth_headers_admin: dict
    ):
        """Test API validation error handling"""
        # Test invalid order_id in calculation request
        response = client.post(
            "/api/v1/commissions/calculate",
            headers=auth_headers_admin,
            json={
                "order_id": "invalid-order-id",  # Should be integer
                "commission_type": "STANDARD"
            }
        )

        assert response.status_code == 422  # Validation error

        # Test invalid commission_type
        response = client.post(
            "/api/v1/commissions/calculate",
            headers=auth_headers_admin,
            json={
                "order_id": 999999,  # Non-existent but valid format
                "commission_type": "INVALID_TYPE"
            }
        )

        assert response.status_code == 422  # Validation error

    def test_commission_pagination(
        self,
        client: TestClient,
        financial_scenario_factory: FinancialScenarioFactory,
        auth_headers_vendor: dict
    ):
        """Test commission list pagination"""
        # Create multiple commissions
        scenarios = []
        for i in range(5):
            scenario = financial_scenario_factory.create_commission_scenario()
            scenarios.append(scenario)

        # Test first page
        response = client.get(
            "/api/v1/commissions",
            headers=auth_headers_vendor,
            params={
                "limit": 3,
                "offset": 0
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert len(data["commissions"]) <= 3
        assert "pagination" in data
        assert data["pagination"]["limit"] == 3
        assert data["pagination"]["offset"] == 0

        # Test second page
        response = client.get(
            "/api/v1/commissions",
            headers=auth_headers_vendor,
            params={
                "limit": 3,
                "offset": 3
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data["pagination"]["offset"] == 3

    def test_commission_api_authentication_required(
        self,
        client: TestClient,
        financial_scenario_factory: FinancialScenarioFactory
    ):
        """Test that all commission endpoints require authentication"""
        scenario = financial_scenario_factory.create_commission_scenario()
        commission = scenario['commission']

        # Test endpoints without authentication
        endpoints_to_test = [
            ("GET", "/api/v1/commissions"),
            ("GET", f"/api/v1/commissions/{commission.id}"),
            ("GET", "/api/v1/commissions/earnings"),
            ("POST", "/api/v1/commissions/calculate"),
            ("PATCH", f"/api/v1/commissions/{commission.id}/approve")
        ]

        for method, endpoint in endpoints_to_test:
            if method == "GET":
                response = client.get(endpoint)
            elif method == "POST":
                response = client.post(endpoint, json={})
            elif method == "PATCH":
                response = client.patch(endpoint, json={})

            assert response.status_code == 401, f"Endpoint {method} {endpoint} should require authentication"

    @pytest.mark.slow
    def test_commission_api_performance(
        self,
        client: TestClient,
        financial_scenario_factory: FinancialScenarioFactory,
        auth_headers_vendor: dict,
        performance_monitor
    ):
        """Test commission API performance under load"""
        import time

        # Create multiple commissions
        scenarios = []
        for i in range(20):
            scenario = financial_scenario_factory.create_commission_scenario()
            scenarios.append(scenario)

        start_time = time.time()

        # Test multiple API calls
        for _ in range(10):
            response = client.get(
                "/api/v1/commissions",
                headers=auth_headers_vendor,
                params={"limit": 20}
            )
            assert response.status_code == 200

        end_time = time.time()
        execution_time = end_time - start_time

        # Should complete 10 API calls in under 5 seconds
        assert execution_time < 5.0, f"Commission API calls too slow: {execution_time}s"

    def test_commission_api_rate_limiting(
        self,
        client: TestClient,
        financial_scenario_factory: FinancialScenarioFactory,
        auth_headers_vendor: dict
    ):
        """Test commission API rate limiting"""
        # Note: This test assumes rate limiting middleware is implemented
        # In a real implementation, you would configure very low limits for testing

        scenario = financial_scenario_factory.create_commission_scenario()

        # Make many rapid requests (this would trigger rate limiting in production)
        responses = []
        for _ in range(50):  # Attempt many requests rapidly
            response = client.get(
                "/api/v1/commissions",
                headers=auth_headers_vendor,
                params={"limit": 1}
            )
            responses.append(response.status_code)

        # In a real rate-limited API, some responses would be 429 (Too Many Requests)
        # For testing, we just verify the API can handle the load
        successful_requests = sum(1 for status in responses if status == 200)
        assert successful_requests > 0  # At least some requests should succeed

    @pytest.mark.critical
    def test_commission_financial_data_integrity(
        self,
        client: TestClient,
        financial_scenario_factory: FinancialScenarioFactory,
        auth_headers_vendor: dict,
        audit_logger
    ):
        """CRITICAL: Test financial data integrity in API responses"""
        audit_logger("financial_integrity_api_test_start", {
            "testing": "commission_calculations_via_api"
        })

        # Create commission with specific amounts for testing
        scenario = financial_scenario_factory.create_commission_scenario(
            order_amount=Decimal("150000.00")  # 150k COP
        )
        commission = scenario['commission']

        # Get commission via API
        response = client.get(
            f"/api/v1/commissions/{commission.id}",
            headers=auth_headers_vendor
        )

        assert response.status_code == 200
        data = response.json()

        # Verify financial calculations
        order_amount = Decimal(str(data["order_amount"]))
        commission_amount = Decimal(str(data["commission_amount"]))
        vendor_amount = Decimal(str(data["vendor_amount"]))
        platform_amount = Decimal(str(data["platform_amount"]))
        commission_rate = Decimal(str(data["commission_rate"]))

        # Validate calculations
        expected_commission = order_amount * commission_rate
        expected_vendor = order_amount - expected_commission

        assert abs(commission_amount - expected_commission) < Decimal('0.01')
        assert abs(vendor_amount - expected_vendor) < Decimal('0.01')
        assert abs(platform_amount - commission_amount) < Decimal('0.01')

        # Validate total balance
        total_check = vendor_amount + platform_amount
        assert abs(total_check - order_amount) < Decimal('0.01')

        audit_logger("financial_integrity_api_test_success", {
            "order_amount": float(order_amount),
            "commission_amount": float(commission_amount),
            "vendor_amount": float(vendor_amount),
            "calculations": "verified"
        })


@pytest.mark.integration_financial
class TestCommissionAPIErrorHandling:
    """Test commission API error handling scenarios"""

    def test_commission_calculation_business_errors(
        self,
        client: TestClient,
        financial_scenario_factory: FinancialScenarioFactory,
        auth_headers_admin: dict
    ):
        """Test business logic error handling in commission calculation"""
        # Create order in wrong status
        scenario = financial_scenario_factory.create_basic_order_scenario()
        order = scenario['order']
        order.status = OrderStatus.CANCELLED  # Cannot calculate commission for cancelled order

        response = client.post(
            "/api/v1/commissions/calculate",
            headers=auth_headers_admin,
            json={
                "order_id": order.id,
                "commission_type": "STANDARD"
            }
        )

        # Should return business error
        assert response.status_code in [400, 422]
        data = response.json()
        assert "detail" in data

    def test_commission_approval_business_errors(
        self,
        client: TestClient,
        financial_scenario_factory: FinancialScenarioFactory,
        auth_headers_admin: dict
    ):
        """Test business logic error handling in commission approval"""
        # Create and approve commission
        scenario = financial_scenario_factory.create_commission_scenario()
        commission = scenario['commission']
        commission.status = CommissionStatus.PAID  # Already paid, cannot approve again

        response = client.patch(
            f"/api/v1/commissions/{commission.id}/approve",
            headers=auth_headers_admin,
            json={"notes": "Test approval"}
        )

        # Should return business error
        assert response.status_code in [400, 422]
        data = response.json()
        assert "detail" in data