#!/bin/bash
# Quick test for vendor orders API endpoints
# Tests with mock authentication

echo "🧪 Testing Vendor Orders API Endpoints"
echo "======================================="
echo ""

# Backend URL
API_URL="http://localhost:8000/api/v1"

# Mock token for testing (if server allows)
TOKEN="mock-test-token"

echo "📋 Test 1: GET /vendor/orders (list all vendor orders)"
echo "---------------------------------------------------"
curl -s -X GET "$API_URL/vendor/orders" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" | python3 -m json.tool || echo "❌ Failed"

echo -e "\n\n"

echo "📋 Test 2: GET /vendor/orders?status=pending (filter by status)"
echo "---------------------------------------------------------------"
curl -s -X GET "$API_URL/vendor/orders?status=pending" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" | python3 -m json.tool || echo "❌ Failed"

echo -e "\n\n"

echo "📋 Test 3: GET /vendor/orders/stats/summary (vendor statistics)"
echo "---------------------------------------------------------------"
curl -s -X GET "$API_URL/vendor/orders/stats/summary" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" | python3 -m json.tool || echo "❌ Failed"

echo -e "\n\n"

echo "✅ All endpoint tests completed!"
echo "Note: Actual results depend on:"
echo "  - Server running on localhost:8000"
echo "  - Valid authentication token"
echo "  - Existing vendor orders in database"
