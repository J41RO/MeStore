#!/bin/bash

echo "=== TESTING PROTECTED ENDPOINT /api/v1/auth/me ==="

echo "1. Testing with VENDOR token..."
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login -H "Content-Type: application/json" -d '{"email":"vendor@test.com","password":"vendor123"}' | python3 -c "import json,sys; print(json.load(sys.stdin)['access_token'])")
echo "Vendor Token: ${TOKEN:0:50}..."
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/auth/me
echo -e "\n"

echo "2. Testing with ADMIN token..."
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login -H "Content-Type: application/json" -d '{"email":"admin@test.com","password":"admin123"}' | python3 -c "import json,sys; print(json.load(sys.stdin)['access_token'])")
echo "Admin Token: ${TOKEN:0:50}..."
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/auth/me
echo -e "\n"

echo "3. Testing with BUYER token..."
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login -H "Content-Type: application/json" -d '{"email":"buyer@test.com","password":"buyer123"}' | python3 -c "import json,sys; print(json.load(sys.stdin)['access_token'])")
echo "Buyer Token: ${TOKEN:0:50}..."
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/auth/me
echo -e "\n"

echo "=== TESTING COMPLETE ==="