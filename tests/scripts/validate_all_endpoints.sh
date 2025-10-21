#!/bin/bash
# ==========================================================================
# API Endpoint Validation Script
# ==========================================================================
# Validates all active endpoints on MeStore API
# API Testing Specialist - Phase 5
# ==========================================================================

BASE_URL="http://192.168.1.137:8000"
PASSED=0
FAILED=0
TOTAL=0

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "================================================================"
echo "API ENDPOINT VALIDATION REPORT"
echo "================================================================"
echo "Base URL: $BASE_URL"
echo "Date: $(date)"
echo "================================================================"

# Helper function to test endpoint
test_endpoint() {
    local method=$1
    local path=$2
    local expected_status=$3
    local description=$4
    local data=$5
    local token=$6

    TOTAL=$((TOTAL + 1))

    if [ -n "$token" ]; then
        if [ -n "$data" ]; then
            response=$(curl -s -w "\n%{http_code}" -X $method "$BASE_URL$path" \
                -H "Content-Type: application/json" \
                -H "Authorization: Bearer $token" \
                -d "$data" 2>/dev/null)
        else
            response=$(curl -s -w "\n%{http_code}" -X $method "$BASE_URL$path" \
                -H "Authorization: Bearer $token" 2>/dev/null)
        fi
    else
        if [ -n "$data" ]; then
            response=$(curl -s -w "\n%{http_code}" -X $method "$BASE_URL$path" \
                -H "Content-Type: application/json" \
                -d "$data" 2>/dev/null)
        else
            response=$(curl -s -w "\n%{http_code}" -X $method "$BASE_URL$path" 2>/dev/null)
        fi
    fi

    status=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$status" = "$expected_status" ]; then
        echo -e "${GREEN}✓${NC} $method $path - Status: $status - $description"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}✗${NC} $method $path - Expected: $expected_status, Got: $status - $description"
        FAILED=$((FAILED + 1))
    fi
}

# ==========================================================================
# CORE ENDPOINTS
# ==========================================================================
echo ""
echo "=== CORE ENDPOINTS ==="

test_endpoint "GET" "/" "200" "Root endpoint"
test_endpoint "GET" "/health" "200" "Health check"
test_endpoint "GET" "/health/services" "200" "Service health check"

# ==========================================================================
# HEALTH ENDPOINTS
# ==========================================================================
echo ""
echo "=== HEALTH ENDPOINTS (/api/v1/health/*) ==="

test_endpoint "GET" "/api/v1/health/health" "200" "Health status"
test_endpoint "GET" "/api/v1/health/ready" "200" "Readiness check"

# ==========================================================================
# AUTH ENDPOINTS
# ==========================================================================
echo ""
echo "=== AUTHENTICATION ENDPOINTS (/api/v1/auth/*) ==="

# Register new buyer
unique_email="test_$(date +%s)@test.com"
register_data="{\"email\":\"$unique_email\",\"password\":\"TestPass123!\",\"user_type\":\"BUYER\",\"full_name\":\"Test User\"}"
test_endpoint "POST" "/api/v1/auth/register" "201" "Register new buyer" "$register_data"

# Login with invalid credentials
invalid_login="{\"email\":\"nonexistent@test.com\",\"password\":\"wrong\"}"
test_endpoint "POST" "/api/v1/auth/login" "401" "Login with invalid credentials" "$invalid_login"

# Missing fields validation
invalid_data="{\"email\":\"test@test.com\"}"
test_endpoint "POST" "/api/v1/auth/register" "422" "Register with missing password" "$invalid_data"

# Admin login with superuser
admin_login="{\"email\":\"admin@mestocker.com\",\"password\":\"Admin123456\"}"
test_endpoint "POST" "/api/v1/auth/admin-login" "200" "Admin login with superuser" "$admin_login"

# Get current user without token (should fail)
test_endpoint "GET" "/api/v1/auth/me" "403" "Get current user without token"

# ==========================================================================
# PRODUCTOS ENDPOINTS
# ==========================================================================
echo ""
echo "=== PRODUCTOS ENDPOINTS (/api/v1/productos/*) ==="

test_endpoint "GET" "/api/v1/productos/" "200" "List products (public)"
test_endpoint "GET" "/api/v1/productos/?skip=0&limit=10" "200" "List products with pagination"
test_endpoint "GET" "/api/v1/productos/999999" "404" "Get non-existent product"
test_endpoint "GET" "/api/v1/productos/check-name?nombre=UniqueProduct123" "200" "Check product name uniqueness"

# Create product without auth (should fail)
product_data="{\"nombre\":\"Test Product\",\"precio\":100.0,\"descripcion\":\"Test\"}"
test_endpoint "POST" "/api/v1/productos/" "403" "Create product without auth" "$product_data"

# ==========================================================================
# CATEGORIES ENDPOINTS
# ==========================================================================
echo ""
echo "=== CATEGORIES ENDPOINTS (/api/v1/categories/*) ==="

test_endpoint "GET" "/api/v1/categories/" "200" "List categories"
test_endpoint "GET" "/api/v1/categories/tree" "200" "Get category tree"
test_endpoint "GET" "/api/v1/categories/stats" "200" "Get category stats"
test_endpoint "GET" "/api/v1/categories/health" "200" "Categories health check"
test_endpoint "GET" "/api/v1/categories/invalid-id" "404" "Get category with invalid ID"

# ==========================================================================
# ORDERS ENDPOINTS
# ==========================================================================
echo ""
echo "=== ORDERS ENDPOINTS (/api/v1/orders/*) ==="

test_endpoint "GET" "/api/v1/orders/" "403" "List orders without auth"
test_endpoint "GET" "/api/v1/orders/health" "200" "Orders health check"

# ==========================================================================
# VENDORS ENDPOINTS
# ==========================================================================
echo ""
echo "=== VENDORS ENDPOINTS (/api/v1/vendors/*) ==="

unique_vendor="vendor_$(date +%s)@test.com"
vendor_data="{\"email\":\"$unique_vendor\",\"password\":\"VendorPass123!\",\"full_name\":\"Test Vendor\",\"numero_documento\":\"900123456\",\"tipo_documento\":\"NIT\",\"celular\":\"3001234567\"}"
test_endpoint "POST" "/api/v1/vendors/register" "200" "Register vendor with valid data" "$vendor_data"

# Missing fields
vendor_incomplete="{\"email\":\"incomplete@test.com\"}"
test_endpoint "POST" "/api/v1/vendors/register" "422" "Register vendor with missing fields" "$vendor_incomplete"

# ==========================================================================
# INVENTORY ENDPOINTS
# ==========================================================================
echo ""
echo "=== INVENTORY ENDPOINTS (/api/v1/inventory/*) ==="

test_endpoint "GET" "/api/v1/inventory/" "403" "List inventory without auth"
test_endpoint "GET" "/api/v1/inventory/alertas" "403" "Get inventory alerts without auth"
test_endpoint "GET" "/api/v1/inventory/audits" "403" "Get inventory audits without auth"

# ==========================================================================
# SCHEMA VALIDATION TESTS
# ==========================================================================
echo ""
echo "=== SCHEMA VALIDATION TESTS ==="

# Invalid JSON
test_endpoint "POST" "/api/v1/auth/register" "422" "Invalid JSON structure" "invalid-json-data"

# Invalid field types (precio should be number, not string)
invalid_price="{\"nombre\":\"Test\",\"precio\":\"not-a-number\",\"descripcion\":\"Test\"}"
# This requires a token, skipping for now
# test_endpoint "POST" "/api/v1/productos/" "422" "Invalid field types" "$invalid_price"

# ==========================================================================
# FINAL RESULTS
# ==========================================================================
echo ""
echo "================================================================"
echo "VALIDATION SUMMARY"
echo "================================================================"
echo -e "Total Tests: $TOTAL"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ ALL ENDPOINT VALIDATIONS PASSED${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠ SOME VALIDATIONS FAILED${NC}"
    exit 1
fi
