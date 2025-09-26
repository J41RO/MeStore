# Database Reset System - Quick Start Guide

## 🚀 Quick Usage for Testing

Need to reset database for testing? Here are the fastest ways:

### 1. Reset All Test Users (Most Common)

```bash
# Interactive (recommended for first-time users)
python scripts/reset_database.py --quick

# Or via API
curl -X POST "http://localhost:8000/api/v1/admin/database-reset/quick-reset" \
  -H "Authorization: Bearer your-admin-token"
```

### 2. Reset Specific User

```bash
# CLI
python scripts/reset_database.py --user test@example.com

# API
curl -X POST "http://localhost:8000/api/v1/admin/database-reset/user" \
  -H "Authorization: Bearer your-admin-token" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "level": "user_cascade"}'
```

### 3. Create Test User

```bash
# CLI (interactive)
python scripts/reset_database.py --create-user test@example.com

# API
curl -X POST "http://localhost:8000/api/v1/admin/database-reset/create-test-user" \
  -H "Authorization: Bearer your-admin-token" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@test.com",
    "password": "testpass123",
    "user_type": "BUYER"
  }'
```

## 🔧 For Registration Testing

**Problem**: Need to test user registration with the same email repeatedly.

**Solution**:
1. Reset the user: `python scripts/reset_database.py --user your-test@test.com`
2. Run your registration test
3. Repeat as needed

## 📊 Check What's in Database

```bash
python scripts/reset_database.py --stats
```

## 🎯 Interactive Mode (Recommended)

```bash
python scripts/reset_database.py --interactive
```

This gives you a menu with all options and safety prompts.

## ⚠️ Safety Notes

- Only works in development/testing environments
- Automatically identifies test users (emails with @test.com, @example.com, etc.)
- For non-test users, add `--force` flag
- All operations are logged

## 🆘 Need Help?

```bash
python scripts/reset_database.py --help
```

For detailed documentation: [DATABASE_RESET_SYSTEM.md](docs/DATABASE_RESET_SYSTEM.md)