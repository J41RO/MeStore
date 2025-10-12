#!/bin/bash

echo "=== TESTING STATS ENDPOINT ==="

# Get token
TOKEN=$(curl -X POST "http://localhost:8000/api/v1/auth/admin-login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@mestocker.com","password":"admin123"}' \
  -s | python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('access_token', ''))")

if [ -z "$TOKEN" ]; then
    echo "❌ LOGIN FAILED"
    exit 1
fi

echo "✅ LOGIN SUCCESS"

# Test stats
echo "Testing stats endpoint:"
curl -H "Authorization: Bearer $TOKEN" \
     "http://localhost:8000/api/v1/superuser-admin/users/stats" \
     -s | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if 'totalUsers' in data:
        print('✅ STATS SUCCESS:', data)
    else:
        print('❌ STATS FAILED:', data)
except Exception as e:
    print('❌ Error:', str(e))
"

# Test users list
echo "Testing users list:"
curl -H "Authorization: Bearer $TOKEN" \
     "http://localhost:8000/api/v1/superuser-admin/users?page=1&size=10" \
     -s | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if 'users' in data:
        print(f'✅ USERS LIST WORKING: {len(data[\"users\"])} usuarios')
        for user in data['users'][:2]:
            print(f'   - {user[\"email\"]} ({user[\"user_type\"]})')
    else:
        print('❌ USERS LIST FAILED:', data)
except Exception as e:
    print('❌ Error:', str(e))
"

echo "=== FINAL STATUS ==="
echo "Backend:" $(curl -s "http://localhost:8000/health" > /dev/null && echo "✅ UP" || echo "❌ DOWN")
echo "Frontend:" $(lsof -i :5173 > /dev/null && echo "✅ UP" || echo "❌ DOWN")