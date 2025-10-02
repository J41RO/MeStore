#!/bin/bash
# Test Stock API Integration
# Database Architect AI - Verification Script

echo "========================================"
echo "Stock API Integration Test"
echo "Database Architect AI"
echo "========================================"
echo ""

BASE_URL="http://localhost:8000/api/v1/productos"

echo "1. Testing List Products Endpoint..."
echo "   GET $BASE_URL/?skip=0&limit=3"
echo ""

RESPONSE=$(curl -s "$BASE_URL/?skip=0&limit=3")

if echo "$RESPONSE" | grep -q "stock"; then
    echo "✅ Response contains 'stock' field"

    # Extract stock values
    STOCKS=$(echo "$RESPONSE" | grep -o '"stock":[0-9]*' | head -3)
    echo ""
    echo "Stock values found:"
    echo "$STOCKS"
    echo ""

    # Check if any stock > 0
    if echo "$STOCKS" | grep -q '"stock":[1-9]'; then
        echo "✅ SUCCESS: Products have stock > 0"
    else
        echo "❌ WARNING: All products still showing stock=0"
    fi
else
    echo "❌ ERROR: No stock field in response"
    echo "Response preview:"
    echo "$RESPONSE" | head -20
fi

echo ""
echo "2. Sample Product Response:"
echo ""
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null | head -40 || echo "$RESPONSE" | head -40

echo ""
echo "========================================"
echo "Test Complete"
echo "========================================"
