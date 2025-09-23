#!/usr/bin/env python3
"""
Boundary and Negative Testing Scenarios - Performance Testing AI
Comprehensive testing of edge cases, error conditions, and boundary values
to maximize code path coverage through error handling logic
"""
import pytest
import json
import string
import random
from typing import Dict, Any, List
from fastapi.testclient import TestClient
from tests.conftest import client


class TestInputBoundaryConditions:
    """Test boundary conditions for input validation and processing"""

    @pytest.mark.asyncio
    @pytest.mark.boundary_test
    async def test_string_length_boundaries(self, client: TestClient):
        """Test string field length boundaries across endpoints"""

        # Test very short strings (empty, single char)
        short_strings = ["", "a", "ab"]

        # Test normal length strings
        normal_strings = ["test@example.com", "Normal Product Name", "Standard Description"]

        # Test maximum length strings
        max_strings = [
            "x" * 255,  # Typical max field length
            "x" * 1000,  # Long text
            "x" * 5000   # Very long text
        ]

        # Test excessive length strings
        excessive_strings = [
            "x" * 10000,   # 10KB
            "x" * 100000,  # 100KB
            "x" * 1000000  # 1MB
        ]

        endpoints_to_test = [
            ("/api/v1/vendedores/registro", "email"),
            ("/api/v1/productos/", "name"),
            ("/api/v1/admins", "full_name"),
            ("/api/v1/categories/", "name")
        ]

        for endpoint, field_name in endpoints_to_test:
            for test_strings in [short_strings, normal_strings, max_strings, excessive_strings]:
                for test_string in test_strings:
                    test_data = {field_name: test_string}

                    # Add required fields based on endpoint
                    if "vendedores" in endpoint:
                        test_data.update({
                            "password": "TestPass123!",
                            "company_name": "Test Company",
                            "phone": "3001234567",
                            "documento_identidad": "1234567890"
                        })
                    elif "productos" in endpoint:
                        test_data.update({
                            "description": "Test description",
                            "price": 29.99,
                            "stock": 10
                        })
                    elif "admins" in endpoint:
                        test_data.update({
                            "email": "admin@test.com",
                            "password": "AdminPass123!"
                        })

                    response = client.post(endpoint, json=test_data)

                    # Should handle boundary conditions gracefully
                    assert response.status_code in [200, 201, 422, 400, 413, 404]

                    # Requests that are too large should be rejected
                    if len(test_string) > 100000:
                        assert response.status_code in [413, 422, 400]  # Payload too large

    @pytest.mark.asyncio
    @pytest.mark.boundary_test
    async def test_numeric_boundaries(self, client: TestClient):
        """Test numeric field boundaries (prices, quantities, IDs)"""

        # Price boundaries
        price_values = [
            -1000.00,    # Negative price
            -0.01,       # Small negative
            0.00,        # Zero price
            0.01,        # Minimum positive
            999999.99,   # Large price
            float('inf'), # Infinity
            float('-inf'), # Negative infinity
            float('nan')  # Not a number
        ]

        # Stock boundaries
        stock_values = [
            -1000,       # Negative stock
            -1,          # Small negative
            0,           # Zero stock
            1,           # Minimum stock
            999999,      # Large stock
            2147483647,  # Max 32-bit int
            2147483648   # Overflow 32-bit int
        ]

        product_endpoints = ["/api/v1/productos/", "/api/v1/products"]

        for endpoint in product_endpoints:
            # Test price boundaries
            for price in price_values:
                product_data = {
                    "name": f"Boundary Test Product Price {price}",
                    "description": "Testing price boundaries",
                    "price": price,
                    "stock": 10
                }

                try:
                    response = client.post(endpoint, json=product_data)
                    assert response.status_code in [200, 201, 422, 400, 404]

                    # Negative or invalid prices should be rejected
                    if price <= 0 or price != price or price == float('inf'):  # NaN or infinity check
                        assert response.status_code in [422, 400]

                except (ValueError, TypeError):
                    # JSON serialization might fail for special float values
                    pass

            # Test stock boundaries
            for stock in stock_values:
                product_data = {
                    "name": f"Boundary Test Product Stock {stock}",
                    "description": "Testing stock boundaries",
                    "price": 19.99,
                    "stock": stock
                }

                response = client.post(endpoint, json=product_data)
                assert response.status_code in [200, 201, 422, 400, 404]

                # Negative stock should be handled appropriately
                if stock < 0:
                    assert response.status_code in [422, 400]

    @pytest.mark.asyncio
    @pytest.mark.boundary_test
    async def test_date_time_boundaries(self, client: TestClient):
        """Test date/time boundary conditions"""

        # Date boundary values
        date_values = [
            "1900-01-01",        # Very old date
            "2000-01-01",        # Y2K
            "2024-02-29",        # Leap year
            "2025-12-31",        # Future date
            "2100-01-01",        # Far future
            "invalid-date",      # Invalid format
            "2024-13-01",        # Invalid month
            "2024-01-32",        # Invalid day
            "",                  # Empty date
            "0000-00-00"         # Zero date
        ]

        # Test with vendor registration (birthdate)
        for date_value in date_values:
            vendor_data = {
                "email": f"boundary.test.{random.randint(1000, 9999)}@test.com",
                "password": "TestPass123!",
                "company_name": "Boundary Test Company",
                "phone": "3001234567",
                "documento_identidad": str(random.randint(1000000000, 9999999999)),
                "fecha_nacimiento": date_value
            }

            response = client.post("/api/v1/vendedores/registro", json=vendor_data)
            assert response.status_code in [200, 201, 422, 400, 404]

            # Invalid dates should be rejected
            if date_value in ["invalid-date", "2024-13-01", "2024-01-32", "", "0000-00-00"]:
                assert response.status_code in [422, 400]


class TestAuthenticationBoundaries:
    """Test authentication and authorization boundary conditions"""

    @pytest.mark.asyncio
    @pytest.mark.security_test
    async def test_password_boundaries(self, client: TestClient):
        """Test password validation boundaries"""

        password_tests = [
            ("", "Empty password"),
            ("a", "Single character"),
            ("12345", "Numbers only"),
            ("abcdef", "Letters only"),
            ("!@#$%^", "Special chars only"),
            ("password", "Common password"),
            ("Password", "Missing number and special"),
            ("Password123", "Missing special char"),
            ("Password!", "Missing number"),
            ("Pass1!", "Too short but valid format"),
            ("ValidPassword123!", "Valid password"),
            ("a" * 1000, "Very long password"),
            ("ValidPassword123!" * 100, "Extremely long valid password")
        ]

        base_vendor_data = {
            "email": "password.test@boundary.com",
            "company_name": "Password Test Company",
            "phone": "3001234567",
            "documento_identidad": "1234567890"
        }

        for password, description in password_tests:
            vendor_data = base_vendor_data.copy()
            vendor_data["password"] = password
            vendor_data["email"] = f"test.{random.randint(1000, 9999)}@boundary.com"

            response = client.post("/api/v1/vendedores/registro", json=vendor_data)
            assert response.status_code in [200, 201, 422, 400, 404]

            print(f"Password test '{description}': {response.status_code}")

            # Weak passwords should be rejected
            if len(password) < 8 or password in ["", "password", "12345", "abcdef"]:
                assert response.status_code in [422, 400]

    @pytest.mark.asyncio
    @pytest.mark.security_test
    async def test_email_format_boundaries(self, client: TestClient):
        """Test email format validation boundaries"""

        email_tests = [
            ("", "Empty email"),
            ("notanemail", "No @ symbol"),
            ("@domain.com", "Missing local part"),
            ("user@", "Missing domain"),
            ("user@domain", "Missing TLD"),
            ("user.@domain.com", "Dot before @"),
            ("user..user@domain.com", "Double dots"),
            ("user@.domain.com", "Dot after @"),
            ("user@domain..com", "Double dots in domain"),
            ("user@domain.c", "Short TLD"),
            ("user@domain.toolongtld", "Long TLD"),
            ("a" * 64 + "@domain.com", "Long local part"),
            ("user@" + "a" * 253 + ".com", "Long domain"),
            ("valid@email.com", "Valid email"),
            ("user+tag@domain.co.uk", "Complex valid email"),
            ("user.name@sub.domain.com", "Subdomain email")
        ]

        base_data = {
            "password": "ValidPass123!",
            "company_name": "Email Test Company",
            "phone": "3001234567",
            "documento_identidad": "1234567890"
        }

        for email, description in email_tests:
            test_data = base_data.copy()
            test_data["email"] = email

            response = client.post("/api/v1/vendedores/registro", json=test_data)
            assert response.status_code in [200, 201, 422, 400, 404]

            print(f"Email test '{description}': {response.status_code}")

            # Invalid emails should be rejected
            invalid_emails = ["", "notanemail", "@domain.com", "user@", "user@domain",
                             "user.@domain.com", "user..user@domain.com"]
            if email in invalid_emails:
                assert response.status_code in [422, 400]

    @pytest.mark.asyncio
    @pytest.mark.security_test
    async def test_token_format_boundaries(self, client: TestClient):
        """Test JWT token format boundaries"""

        token_tests = [
            ("", "Empty token"),
            ("invalid", "Invalid format"),
            ("Bearer", "Bearer without token"),
            ("Bearer ", "Bearer with space only"),
            ("NotBearer validtoken", "Wrong auth type"),
            ("Bearer " + "a" * 1000, "Very long token"),
            ("Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9", "Incomplete JWT"),
            ("Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWV9", "JWT without signature"),
            ("Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWV9.TJVA95OrM7E2cBab30RMHrHDcEfxjoYZgeFONFh7HgQ", "Valid JWT format"),
        ]

        protected_endpoints = [
            "/api/v1/vendedores/dashboard/resumen",
            "/api/v1/admins/test-id",
            "/api/v1/payments/methods"
        ]

        for token, description in token_tests:
            headers = {"Authorization": token} if token else {}

            for endpoint in protected_endpoints:
                response = client.get(endpoint, headers=headers)
                assert response.status_code in [200, 401, 422, 404]

                print(f"Token test '{description}' on {endpoint}: {response.status_code}")

                # Invalid tokens should return 401
                if token in ["", "invalid", "Bearer", "Bearer ", "NotBearer validtoken"]:
                    assert response.status_code in [401, 422]


class TestPayloadSizeAndFormatBoundaries:
    """Test request payload size and format boundaries"""

    @pytest.mark.asyncio
    @pytest.mark.boundary_test
    async def test_json_payload_size_boundaries(self, client: TestClient):
        """Test JSON payload size limits"""

        # Small payload
        small_payload = {"test": "small"}

        # Medium payload
        medium_payload = {"data": "x" * 10000}  # 10KB

        # Large payload
        large_payload = {"data": "x" * 1000000}  # 1MB

        # Extremely large payload
        try:
            huge_payload = {"data": "x" * 10000000}  # 10MB
        except MemoryError:
            huge_payload = None

        endpoints_to_test = [
            "/api/v1/vendedores/registro",
            "/api/v1/productos/",
            "/api/v1/admins",
            "/api/v1/search"
        ]

        payloads = [
            (small_payload, "Small payload"),
            (medium_payload, "Medium payload"),
            (large_payload, "Large payload")
        ]

        if huge_payload:
            payloads.append((huge_payload, "Huge payload"))

        for payload, description in payloads:
            for endpoint in endpoints_to_test:
                try:
                    response = client.post(endpoint, json=payload)
                    assert response.status_code in [200, 201, 422, 400, 413, 414, 404]

                    print(f"{description} to {endpoint}: {response.status_code}")

                    # Large payloads should be handled appropriately
                    if len(str(payload)) > 1000000:  # > 1MB
                        assert response.status_code in [413, 422, 400]  # Payload too large

                except Exception as e:
                    # Large payloads might cause memory or timeout errors
                    print(f"Exception with {description}: {e}")

    @pytest.mark.asyncio
    @pytest.mark.boundary_test
    async def test_malformed_json_boundaries(self, client: TestClient):
        """Test malformed and edge case JSON"""

        malformed_json_tests = [
            ('', "Empty body"),
            ('{', "Incomplete JSON object"),
            ('{"key":}', "Missing value"),
            ('{"key": "value",}', "Trailing comma"),
            ('{"key": "value" "key2": "value2"}', "Missing comma"),
            ('{"duplicate": 1, "duplicate": 2}', "Duplicate keys"),
            ('{"unicode": "\\u0000"}', "Null unicode"),
            ('{"nested": {"deep": {"very": {"deep": {"object": "value"}}}}}', "Deep nesting"),
            ('{"array": [1, 2, [3, 4, [5, 6, [7, 8]]]]}', "Nested arrays"),
            ('{"number": 999999999999999999999999999999}', "Very large number"),
            ('{"float": 1.7976931348623157e+308}', "Max float"),
            ('{"string": "' + "x" * 100000 + '"}', "Very long string"),
        ]

        endpoints_to_test = [
            "/api/v1/vendedores/registro",
            "/api/v1/productos/",
            "/api/v1/payments/create-intent",
            "/api/v1/search"
        ]

        for json_data, description in malformed_json_tests:
            for endpoint in endpoints_to_test:
                try:
                    response = client.post(
                        endpoint,
                        data=json_data,
                        headers={"Content-Type": "application/json"}
                    )

                    assert response.status_code in [200, 201, 400, 422, 413, 404]

                    print(f"Malformed JSON '{description}' to {endpoint}: {response.status_code}")

                    # Malformed JSON should be rejected
                    if json_data in ['', '{', '{"key":}', '{"key": "value",}']:
                        assert response.status_code in [400, 422]

                except Exception as e:
                    # Some malformed JSON might cause parsing exceptions
                    print(f"Exception with malformed JSON '{description}': {e}")


class TestConcurrencyAndRaceConditions:
    """Test race conditions and concurrent access scenarios"""

    @pytest.mark.asyncio
    @pytest.mark.race_condition_test
    async def test_concurrent_user_creation(self, client: TestClient):
        """Test concurrent creation of users with same email to test race conditions"""

        import threading
        import time

        results = []
        duplicate_email = f"race.condition.{int(time.time())}@test.com"

        def create_user(user_id: int):
            """Create user with duplicate email"""
            user_data = {
                "email": duplicate_email,
                "password": f"Password{user_id}123!",
                "company_name": f"Race Test Company {user_id}",
                "phone": f"300123456{user_id % 10}",
                "documento_identidad": f"100000000{user_id}"
            }

            response = client.post("/api/v1/vendedores/registro", json=user_data)
            results.append({
                "user_id": user_id,
                "status_code": response.status_code,
                "response_time": time.time()
            })

        # Create multiple threads trying to create the same user
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_user, args=(i,))
            threads.append(thread)

        # Start all threads simultaneously
        for thread in threads:
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Analyze results
        success_count = sum(1 for r in results if r["status_code"] in [200, 201])
        conflict_count = sum(1 for r in results if r["status_code"] in [409, 422])

        print(f"Race condition test results:")
        print(f"- Successes: {success_count}")
        print(f"- Conflicts: {conflict_count}")
        print(f"- Total: {len(results)}")

        # Should only allow one successful creation
        assert success_count <= 1  # At most one should succeed
        assert conflict_count >= 4  # Others should get conflicts

    @pytest.mark.asyncio
    @pytest.mark.race_condition_test
    async def test_concurrent_stock_updates(self, client: TestClient):
        """Test concurrent stock updates to check for race conditions"""

        import threading
        import time

        product_id = f"race-product-{int(time.time())}"
        results = []

        def update_stock(update_id: int):
            """Update product stock"""
            stock_data = {
                "product_id": product_id,
                "quantity_change": -1,  # Reduce by 1
                "operation": "sale"
            }

            response = client.post("/api/v1/inventory/movement", json=stock_data)
            results.append({
                "update_id": update_id,
                "status_code": response.status_code,
                "timestamp": time.time()
            })

        # Create multiple concurrent stock updates
        threads = []
        for i in range(10):
            thread = threading.Thread(target=update_stock, args=(i,))
            threads.append(thread)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # Analyze results
        print(f"Concurrent stock update results: {len(results)} operations")
        status_codes = [r["status_code"] for r in results]

        # Should handle concurrent updates gracefully
        valid_codes = [200, 201, 404, 422, 409]  # Include conflict codes
        assert all(code in valid_codes for code in status_codes)


@pytest.mark.asyncio
@pytest.mark.edge_case_test
async def test_unusual_character_sets(client: TestClient):
    """Test handling of unusual character sets and encodings"""

    unusual_strings = [
        "普通话测试",  # Chinese characters
        "العربية اختبار",  # Arabic characters
        "русский тест",  # Cyrillic characters
        "🎉🚀💻🔥⭐",  # Emojis
        "café naïve résumé",  # Accented characters
        "\x00\x01\x02\x03",  # Control characters
        "\\n\\r\\t\\\\",  # Escaped characters
        "<script>alert('xss')</script>",  # XSS attempt
        "'; DROP TABLE users; --",  # SQL injection attempt
        "../../../etc/passwd",  # Path traversal attempt
    ]

    for test_string in unusual_strings:
        # Test in vendor registration
        vendor_data = {
            "email": f"unusual.{random.randint(1000, 9999)}@test.com",
            "password": "TestPass123!",
            "company_name": test_string,
            "phone": "3001234567",
            "documento_identidad": str(random.randint(1000000000, 9999999999))
        }

        try:
            response = client.post("/api/v1/vendedores/registro", json=vendor_data)
            assert response.status_code in [200, 201, 422, 400, 404]

            # Security-sensitive strings should be rejected or sanitized
            if any(danger in test_string for danger in ["<script>", "DROP TABLE", "../"]):
                assert response.status_code in [422, 400]

        except UnicodeError:
            # Some character sets might cause encoding issues
            pass

        print(f"Unusual character test completed for: {test_string[:20]}...")


# Performance monitoring for boundary tests
@pytest.fixture(autouse=True)
def monitor_boundary_test_performance():
    """Monitor performance of boundary tests"""
    import time
    start_time = time.time()
    yield
    end_time = time.time()

    test_duration = end_time - start_time
    if test_duration > 10.0:  # Log very slow boundary tests
        print(f"SLOW BOUNDARY TEST: took {test_duration:.2f}s")

    # Boundary tests should complete quickly
    assert test_duration < 30.0  # No boundary test should take more than 30 seconds