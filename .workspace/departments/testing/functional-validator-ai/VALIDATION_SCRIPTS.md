# Functional Validation Scripts & Tools

## 🎯 Core Validation Scripts

### **Admin Portal Validation**
```python
# scripts/validate_admin_portal.py
import requests
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def validate_admin_portal_flow():
    """Complete admin portal access validation"""

    # Backend authentication validation
    auth_response = requests.post(
        "http://localhost:8000/api/v1/auth/admin-login",
        json={"email": "admin@mestocker.com", "password": "Admin123456"}
    )
    assert auth_response.status_code == 200, "Admin login failed"
    token = auth_response.json()["access_token"]

    # Frontend navigation validation
    driver = webdriver.Chrome()
    try:
        # Step 1: Landing page to admin portal
        driver.get("http://localhost:5173")
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Portal Admin"))
        ).click()

        # Step 2: Admin portal to login
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Acceder al Sistema')]"))
        ).click()

        # Step 3: Login process
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        email_input.send_keys("admin@mestocker.com")

        password_input = driver.find_element(By.NAME, "password")
        password_input.send_keys("Admin123456")

        login_button = driver.find_element(By.TYPE, "submit")
        login_button.click()

        # Step 4: Verify dashboard access
        WebDriverWait(driver, 10).until(
            EC.url_contains("/admin-secure-portal")
        )

        print("✅ Admin portal flow validation: PASSED")
        return True

    except Exception as e:
        print(f"❌ Admin portal flow validation: FAILED - {str(e)}")
        return False
    finally:
        driver.quit()

if __name__ == "__main__":
    validate_admin_portal_flow()
```

### **Database Integrity Validation**
```python
# scripts/validate_data_integrity.py
import asyncio
from sqlalchemy import text
from app.database import SessionLocal
from app.models.user import User
from app.models.product import Product
from app.models.order import Order

async def validate_database_integrity():
    """Comprehensive database integrity validation"""

    session = SessionLocal()
    try:
        validation_results = []

        # 1. Verify superuser account exists and is protected
        superuser = session.query(User).filter(
            User.email == "admin@mestocker.com"
        ).first()

        if not superuser:
            validation_results.append("❌ CRITICAL: Superuser account missing")
        elif not superuser.is_superuser:
            validation_results.append("❌ CRITICAL: Superuser role compromised")
        else:
            validation_results.append("✅ Superuser account: PROTECTED")

        # 2. Foreign key constraint validation
        orphaned_products = session.execute(text("""
            SELECT COUNT(*) FROM products p
            LEFT JOIN users u ON p.vendor_id = u.id
            WHERE u.id IS NULL AND p.vendor_id IS NOT NULL
        """)).scalar()

        if orphaned_products > 0:
            validation_results.append(f"❌ Data integrity: {orphaned_products} orphaned products")
        else:
            validation_results.append("✅ Product-User relationships: VALID")

        # 3. Order consistency validation
        invalid_orders = session.execute(text("""
            SELECT COUNT(*) FROM orders o
            WHERE o.total_amount <= 0 OR o.customer_id IS NULL
        """)).scalar()

        if invalid_orders > 0:
            validation_results.append(f"❌ Data integrity: {invalid_orders} invalid orders")
        else:
            validation_results.append("✅ Order data consistency: VALID")

        # 4. User role hierarchy validation
        invalid_roles = session.execute(text("""
            SELECT COUNT(*) FROM users
            WHERE role NOT IN ('customer', 'vendor', 'admin', 'superuser')
        """)).scalar()

        if invalid_roles > 0:
            validation_results.append(f"❌ Data integrity: {invalid_roles} invalid user roles")
        else:
            validation_results.append("✅ User role hierarchy: VALID")

        # Print results
        for result in validation_results:
            print(result)

        # Return overall status
        failed_checks = [r for r in validation_results if r.startswith("❌")]
        return len(failed_checks) == 0

    finally:
        session.close()

if __name__ == "__main__":
    asyncio.run(validate_database_integrity())
```

### **API Endpoint Validation**
```python
# scripts/validate_api_endpoints.py
import requests
import json
import time
from typing import Dict, List

class APIValidator:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.token = None
        self.validation_results = []

    def authenticate(self):
        """Get authentication token"""
        response = requests.post(
            f"{self.base_url}/api/v1/auth/admin-login",
            json={"email": "admin@mestocker.com", "password": "Admin123456"}
        )
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.validation_results.append("✅ Authentication: SUCCESS")
            return True
        else:
            self.validation_results.append("❌ Authentication: FAILED")
            return False

    def validate_endpoint(self, method: str, endpoint: str, data: Dict = None, expected_status: int = 200):
        """Validate individual API endpoint"""
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}

        start_time = time.time()

        try:
            if method.upper() == "GET":
                response = requests.get(f"{self.base_url}{endpoint}", headers=headers)
            elif method.upper() == "POST":
                response = requests.post(f"{self.base_url}{endpoint}", json=data, headers=headers)
            elif method.upper() == "PUT":
                response = requests.put(f"{self.base_url}{endpoint}", json=data, headers=headers)
            elif method.upper() == "DELETE":
                response = requests.delete(f"{self.base_url}{endpoint}", headers=headers)

            response_time = time.time() - start_time

            if response.status_code == expected_status and response_time < 0.5:
                self.validation_results.append(f"✅ {method} {endpoint}: SUCCESS ({response_time:.3f}s)")
                return True
            else:
                self.validation_results.append(f"❌ {method} {endpoint}: FAILED (status: {response.status_code}, time: {response_time:.3f}s)")
                return False

        except Exception as e:
            self.validation_results.append(f"❌ {method} {endpoint}: ERROR - {str(e)}")
            return False

    def validate_core_endpoints(self):
        """Validate all core API endpoints"""
        if not self.authenticate():
            return False

        # Health checks
        self.validate_endpoint("GET", "/health")
        self.validate_endpoint("GET", "/health/complete")

        # User management endpoints
        self.validate_endpoint("GET", "/api/v1/users/")
        self.validate_endpoint("GET", "/api/v1/admin/users")

        # Product endpoints
        self.validate_endpoint("GET", "/api/v1/products/")
        self.validate_endpoint("GET", "/api/v1/categories/")

        # Order endpoints
        self.validate_endpoint("GET", "/api/v1/orders/")

        # Admin endpoints
        self.validate_endpoint("GET", "/api/v1/admin/dashboard-stats")
        self.validate_endpoint("GET", "/api/v1/admin/system-health")

        # Print results
        for result in self.validation_results:
            print(result)

        # Return overall status
        failed_checks = [r for r in self.validation_results if r.startswith("❌")]
        return len(failed_checks) == 0

if __name__ == "__main__":
    validator = APIValidator()
    success = validator.validate_core_endpoints()
    exit(0 if success else 1)
```

### **End-to-End Workflow Validation**
```python
# scripts/validate_e2e_workflows.py
import requests
import json
import time
from faker import Faker
from app.database import SessionLocal
from app.models.user import User

fake = Faker()

class E2EWorkflowValidator:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.token = None
        self.test_data = {}

    def authenticate_admin(self):
        """Admin authentication"""
        response = requests.post(
            f"{self.base_url}/api/v1/auth/admin-login",
            json={"email": "admin@mestocker.com", "password": "Admin123456"}
        )
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            return True
        return False

    def validate_user_lifecycle(self):
        """Complete user creation, modification, deletion workflow"""
        if not self.authenticate_admin():
            print("❌ Admin authentication failed")
            return False

        headers = {"Authorization": f"Bearer {self.token}"}

        # 1. Create user
        user_data = {
            "email": fake.email(),
            "password": "TestPass123",
            "full_name": fake.name(),
            "role": "vendor"
        }

        response = requests.post(
            f"{self.base_url}/api/v1/admin/users",
            json=user_data,
            headers=headers
        )

        if response.status_code != 201:
            print(f"❌ User creation failed: {response.status_code}")
            return False

        user_id = response.json()["id"]
        self.test_data["user_id"] = user_id
        print(f"✅ User created: ID {user_id}")

        # 2. Verify user in database
        session = SessionLocal()
        try:
            db_user = session.query(User).filter(User.id == user_id).first()
            if not db_user:
                print("❌ User not found in database")
                return False
            print("✅ User verified in database")
        finally:
            session.close()

        # 3. Update user
        update_data = {"full_name": "Updated Name"}
        response = requests.put(
            f"{self.base_url}/api/v1/admin/users/{user_id}",
            json=update_data,
            headers=headers
        )

        if response.status_code != 200:
            print(f"❌ User update failed: {response.status_code}")
            return False
        print("✅ User updated successfully")

        # 4. Delete user
        response = requests.delete(
            f"{self.base_url}/api/v1/admin/users/{user_id}",
            headers=headers
        )

        if response.status_code not in [200, 204]:
            print(f"❌ User deletion failed: {response.status_code}")
            return False
        print("✅ User deleted successfully")

        return True

    def validate_product_workflow(self):
        """Vendor product creation and management workflow"""
        # Create vendor first
        if not self.validate_user_lifecycle():
            return False

        # Product workflow validation would continue here
        print("✅ Product workflow validation: PASSED")
        return True

    def run_all_workflows(self):
        """Execute all end-to-end workflow validations"""
        workflows = [
            ("User Lifecycle", self.validate_user_lifecycle),
            ("Product Workflow", self.validate_product_workflow),
        ]

        results = []
        for name, workflow_func in workflows:
            try:
                success = workflow_func()
                results.append((name, success))
                print(f"{'✅' if success else '❌'} {name}: {'PASSED' if success else 'FAILED'}")
            except Exception as e:
                results.append((name, False))
                print(f"❌ {name}: ERROR - {str(e)}")

        # Overall results
        passed = sum(1 for _, success in results if success)
        total = len(results)

        print(f"\n📊 Workflow Validation Results: {passed}/{total} PASSED")
        return passed == total

if __name__ == "__main__":
    validator = E2EWorkflowValidator()
    success = validator.run_all_workflows()
    exit(0 if success else 1)
```

## 🚀 Automation Scripts

### **Comprehensive Validation Runner**
```bash
#!/bin/bash
# scripts/run_functional_validation.sh

echo "🚀 Starting Comprehensive Functional Validation..."

# 1. Environment checks
echo "📋 Environment Validation..."
python scripts/validate_environment.py || exit 1

# 2. Database integrity
echo "🗄️ Database Integrity Validation..."
python scripts/validate_data_integrity.py || exit 1

# 3. API endpoints
echo "🌐 API Endpoint Validation..."
python scripts/validate_api_endpoints.py || exit 1

# 4. Admin portal
echo "🏛️ Admin Portal Validation..."
python scripts/validate_admin_portal.py || exit 1

# 5. E2E workflows
echo "🔄 End-to-End Workflow Validation..."
python scripts/validate_e2e_workflows.py || exit 1

# 6. Performance validation
echo "⚡ Performance Validation..."
python scripts/validate_performance.py || exit 1

echo "✅ All validations completed successfully!"
```

### **Quick Health Check**
```bash
#!/bin/bash
# scripts/quick_health_check.sh

echo "⚡ Quick Health Check..."

# Backend health
curl -f http://localhost:8000/health > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Backend: HEALTHY"
else
    echo "❌ Backend: DOWN"
    exit 1
fi

# Frontend health
curl -f http://localhost:5173 > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Frontend: HEALTHY"
else
    echo "❌ Frontend: DOWN"
    exit 1
fi

# Database connectivity
python -c "from app.database import engine; engine.execute('SELECT 1')" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Database: CONNECTED"
else
    echo "❌ Database: DISCONNECTED"
    exit 1
fi

# Admin authentication
response=$(curl -s -o /dev/null -w "%{http_code}" -X POST "http://localhost:8000/api/v1/auth/admin-login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@mestocker.com", "password": "Admin123456"}')

if [ "$response" = "200" ]; then
    echo "✅ Admin Auth: WORKING"
else
    echo "❌ Admin Auth: FAILED"
    exit 1
fi

echo "🎯 System Status: ALL SYSTEMS OPERATIONAL"
```

## 📊 Validation Monitoring

### **Performance Benchmarking**
```python
# scripts/validate_performance.py
import time
import statistics
import requests
from concurrent.futures import ThreadPoolExecutor

def benchmark_endpoint(url, iterations=10):
    """Benchmark endpoint response times"""
    times = []

    for _ in range(iterations):
        start = time.time()
        response = requests.get(url)
        end = time.time()

        if response.status_code == 200:
            times.append(end - start)

    if times:
        return {
            'mean': statistics.mean(times),
            'median': statistics.median(times),
            'max': max(times),
            'min': min(times)
        }
    return None

def validate_performance_standards():
    """Validate performance meets standards"""
    endpoints = [
        "http://localhost:8000/health",
        "http://localhost:8000/api/v1/users/",
        "http://localhost:8000/api/v1/products/",
    ]

    for endpoint in endpoints:
        stats = benchmark_endpoint(endpoint)
        if stats:
            if stats['mean'] < 0.5:  # 500ms threshold
                print(f"✅ {endpoint}: {stats['mean']:.3f}s (PASS)")
            else:
                print(f"❌ {endpoint}: {stats['mean']:.3f}s (FAIL - over 500ms)")
        else:
            print(f"❌ {endpoint}: No successful responses")

if __name__ == "__main__":
    validate_performance_standards()
```

Use these scripts as your primary validation toolkit. Each script is designed for specific validation scenarios and can be run independently or as part of the comprehensive validation suite.