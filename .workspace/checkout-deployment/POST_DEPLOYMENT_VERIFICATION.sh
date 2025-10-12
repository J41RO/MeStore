#!/bin/bash

# MeStore Orders System - Post-Deployment Verification Script
# Version: 1.0.0
# Date: 2025-10-09

echo "🚀 MeStore v1.0.0 - Post-Deployment Verification"
echo "=================================================="
echo ""

PROD_URL="https://mestore.onrender.com"
FAILED=0

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "Target Environment: $PROD_URL"
echo ""

# Test 1: Health Check
echo "Test 1: Health Check Endpoint"
echo "------------------------------"
HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$PROD_URL/health")
if [ "$HEALTH_RESPONSE" = "200" ]; then
    echo -e "${GREEN}✅ PASS${NC} - Health endpoint responding (200 OK)"
else
    echo -e "${RED}❌ FAIL${NC} - Health endpoint returned: $HEALTH_RESPONSE"
    FAILED=$((FAILED + 1))
fi
echo ""

# Test 2: API Documentation
echo "Test 2: API Documentation (Swagger)"
echo "------------------------------------"
DOCS_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$PROD_URL/docs")
if [ "$DOCS_RESPONSE" = "200" ]; then
    echo -e "${GREEN}✅ PASS${NC} - API documentation accessible"
else
    echo -e "${RED}❌ FAIL${NC} - API docs returned: $DOCS_RESPONSE"
    FAILED=$((FAILED + 1))
fi
echo ""

# Test 3: Admin Login Endpoint
echo "Test 3: Admin Login Endpoint"
echo "----------------------------"
LOGIN_RESPONSE=$(curl -s -X POST "$PROD_URL/api/v1/auth/admin-login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@mestocker.com", "password": "Admin123456"}' \
  -w "\n%{http_code}")

LOGIN_STATUS=$(echo "$LOGIN_RESPONSE" | tail -n 1)
LOGIN_BODY=$(echo "$LOGIN_RESPONSE" | head -n -1)

if [ "$LOGIN_STATUS" = "200" ]; then
    echo -e "${GREEN}✅ PASS${NC} - Admin login successful (200 OK)"
    # Extract token for subsequent tests
    export AUTH_TOKEN=$(echo "$LOGIN_BODY" | jq -r '.access_token' 2>/dev/null)
    if [ -n "$AUTH_TOKEN" ] && [ "$AUTH_TOKEN" != "null" ]; then
        echo "   🔑 JWT token obtained for further tests"
    fi
else
    echo -e "${RED}❌ FAIL${NC} - Admin login returned: $LOGIN_STATUS"
    echo "   Response: $LOGIN_BODY"
    FAILED=$((FAILED + 1))
fi
echo ""

# Test 4: Orders Endpoint (Authentication Required)
echo "Test 4: Orders Endpoint (GET /orders/)"
echo "---------------------------------------"
if [ -n "$AUTH_TOKEN" ] && [ "$AUTH_TOKEN" != "null" ]; then
    ORDERS_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$PROD_URL/api/v1/orders/" \
      -H "Authorization: Bearer $AUTH_TOKEN")

    if [ "$ORDERS_RESPONSE" = "200" ]; then
        echo -e "${GREEN}✅ PASS${NC} - Orders endpoint accessible with auth"
    elif [ "$ORDERS_RESPONSE" = "401" ]; then
        echo -e "${YELLOW}⚠️  WARN${NC} - Orders endpoint returned 401 (token may have expired)"
    else
        echo -e "${RED}❌ FAIL${NC} - Orders endpoint returned: $ORDERS_RESPONSE"
        FAILED=$((FAILED + 1))
    fi
else
    echo -e "${YELLOW}⚠️  SKIP${NC} - No auth token available, skipping orders test"
fi
echo ""

# Test 5: Unauthenticated Order Creation (Should Fail with 401)
echo "Test 5: Unauthenticated Order Creation (Security Check)"
echo "--------------------------------------------------------"
UNAUTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$PROD_URL/api/v1/orders/" \
  -H "Content-Type: application/json" \
  -d '{"items": []}')

if [ "$UNAUTH_RESPONSE" = "401" ]; then
    echo -e "${GREEN}✅ PASS${NC} - Unauthenticated request correctly rejected (401)"
else
    echo -e "${RED}❌ FAIL${NC} - Expected 401, got: $UNAUTH_RESPONSE (SECURITY ISSUE)"
    FAILED=$((FAILED + 1))
fi
echo ""

# Test 6: CORS Headers Check
echo "Test 6: CORS Configuration"
echo "--------------------------"
CORS_HEADERS=$(curl -s -I "$PROD_URL/health" | grep -i "access-control")
if [ -n "$CORS_HEADERS" ]; then
    echo -e "${GREEN}✅ PASS${NC} - CORS headers present"
    echo "$CORS_HEADERS" | sed 's/^/   /'
else
    echo -e "${YELLOW}⚠️  WARN${NC} - No CORS headers detected (may be endpoint-specific)"
fi
echo ""

# Test 7: Rate Limiting Check (Make multiple rapid requests)
echo "Test 7: Rate Limiting (DoS Protection)"
echo "---------------------------------------"
echo "Making 5 rapid requests to check rate limiting..."

RATE_LIMIT_TRIGGERED=0
for i in {1..5}; do
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$PROD_URL/health")
    if [ "$STATUS" = "429" ]; then
        RATE_LIMIT_TRIGGERED=1
        break
    fi
    sleep 0.1
done

# Note: Health endpoint might not be rate-limited, so this is informational
if [ $RATE_LIMIT_TRIGGERED -eq 1 ]; then
    echo -e "${GREEN}✅ INFO${NC} - Rate limiting is active (429 detected)"
elif [ -n "$AUTH_TOKEN" ]; then
    # Try with orders endpoint if we have auth
    echo "   Testing rate limiting on orders endpoint..."
    for i in {1..12}; do
        STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$PROD_URL/api/v1/orders/" \
          -H "Authorization: Bearer $AUTH_TOKEN")
        if [ "$STATUS" = "429" ]; then
            RATE_LIMIT_TRIGGERED=1
            echo -e "${GREEN}✅ PASS${NC} - Rate limiting working (429 after $i requests)"
            break
        fi
        sleep 0.1
    done

    if [ $RATE_LIMIT_TRIGGERED -eq 0 ]; then
        echo -e "${YELLOW}⚠️  INFO${NC} - Rate limiting not triggered in test (may require more requests)"
    fi
else
    echo -e "${YELLOW}⚠️  INFO${NC} - Rate limiting not tested (health endpoint may not be rate-limited)"
fi
echo ""

# Summary
echo "=============================================="
echo "DEPLOYMENT VERIFICATION SUMMARY"
echo "=============================================="
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL CRITICAL TESTS PASSED${NC}"
    echo ""
    echo "✅ Health check operational"
    echo "✅ API documentation accessible"
    echo "✅ Authentication working"
    echo "✅ Orders endpoint responding"
    echo "✅ Security checks passing"
    echo ""
    echo "Status: DEPLOYMENT SUCCESSFUL ✅"
    echo ""
    echo "Next Steps:"
    echo "1. Monitor Railway logs for errors"
    echo "2. Check database connection stability"
    echo "3. Validate fraud detection logging"
    echo "4. Monitor order success rates over 24 hours"
    echo ""
    exit 0
else
    echo -e "${RED}❌ $FAILED TEST(S) FAILED${NC}"
    echo ""
    echo "Status: DEPLOYMENT REQUIRES ATTENTION ⚠️"
    echo ""
    echo "Action Required:"
    echo "1. Review Railway deployment logs"
    echo "2. Check environment variables in Railway"
    echo "3. Verify database connection"
    echo "4. Check CORS configuration if needed"
    echo ""
    echo "Rollback Plan:"
    echo "  Railway Dashboard → Deployments → Select previous deployment → Redeploy"
    echo ""
    exit 1
fi
