# Database Reset System Documentation

## Overview

The MeStore Database Reset System provides comprehensive, safe, and controlled database reset functionality specifically designed for development and testing environments. This system addresses the critical need for repeated testing with the same user data by providing multiple reset levels and safety mechanisms.

## 🚨 Safety Features

### Environment Protection
- **Environment Validation**: Only works in `development`, `testing`, `dev`, or `test` environments
- **Database URL Validation**: Blocks operations on production-like database URLs
- **Multiple Confirmation Levels**: Interactive confirmations for destructive operations

### User Safety
- **Test User Identification**: Automatically identifies users with test email domains
- **Force Override**: Requires explicit `force=True` for non-test users
- **Admin Preservation**: Option to preserve admin users during full resets

### Operation Logging
- **Comprehensive Logging**: All operations are logged with admin user attribution
- **Execution Time Tracking**: Performance monitoring for all operations
- **Error Reporting**: Detailed error messages and rollback procedures

## Components

### 1. Database Reset Service (`app/services/database_reset_service.py`)

The core service providing all reset functionality.

#### Key Classes

- **`DatabaseResetService`**: Main service class with async context manager support
- **`ResetLevel`**: Enum defining different levels of reset operations
- **`ResetResult`**: Result object containing operation details and statistics

#### Reset Levels

```python
class ResetLevel(str, Enum):
    USER_DATA = "user_data"          # Only user profile data
    USER_SESSIONS = "user_sessions"   # User data + sessions
    USER_CASCADE = "user_cascade"     # User data + all related records
    ALL_TEST_DATA = "all_test_data"   # All test data (marked users)
    FULL_RESET = "full_reset"         # Complete database reset (DANGEROUS)
```

#### Main Methods

- `delete_user_safely()`: Reset single user with safety checks
- `reset_test_users()`: Reset all identified test users
- `full_database_reset()`: Complete database reset (requires confirmation)
- `create_test_user()`: Create test users for testing
- `get_reset_statistics()`: Get database statistics for planning

### 2. API Endpoints (`app/api/v1/endpoints/database_reset.py`)

RESTful API endpoints for database reset operations.

#### Available Endpoints

```bash
GET  /api/v1/admin/database-reset/status         # Service status
GET  /api/v1/admin/database-reset/statistics     # Database statistics
GET  /api/v1/admin/database-reset/health         # Health check
POST /api/v1/admin/database-reset/user           # Reset single user
POST /api/v1/admin/database-reset/test-users     # Reset test users
POST /api/v1/admin/database-reset/create-test-user # Create test user
POST /api/v1/admin/database-reset/quick-reset    # Quick reset
POST /api/v1/admin/database-reset/full-reset     # Full reset (DANGEROUS)
```

#### Authentication & Authorization

- **Admin Required**: All endpoints require admin authentication
- **Superuser for Full Reset**: Full database reset requires superuser privileges
- **Environment Checks**: All operations validate environment safety

### 3. CLI Script (`scripts/reset_database.py`)

Interactive command-line interface for database reset operations.

#### Features

- **Interactive Menu**: User-friendly menu system
- **Colored Output**: Clear visual feedback with color coding
- **Safety Confirmations**: Multiple confirmation prompts
- **Flexible Options**: Command-line arguments for automation

## Usage Examples

### 1. Using the Service Directly

```python
from app.services.database_reset_service import DatabaseResetService, ResetLevel

# Reset a single user
async with DatabaseResetService() as service:
    result = await service.delete_user_safely(
        user_id="user-123",
        level=ResetLevel.USER_CASCADE,
        force=False
    )
    print(f"Reset successful: {result.success}")

# Reset all test users
async with DatabaseResetService() as service:
    result = await service.reset_test_users()
    print(f"Affected users: {len(result.affected_users)}")

# Create test user
async with DatabaseResetService() as service:
    user = await service.create_test_user(
        email="testuser@test.com",
        password="testpass123",
        user_type=UserType.BUYER
    )
```

### 2. Using the CLI Script

```bash
# Interactive mode
python scripts/reset_database.py --interactive

# Quick reset all test users
python scripts/reset_database.py --quick

# Reset specific user
python scripts/reset_database.py --user test@example.com

# Show database statistics
python scripts/reset_database.py --stats

# Create test user
python scripts/reset_database.py --create-user newuser@test.com

# Full reset with confirmation
python scripts/reset_database.py --full-reset --confirm

# Help and options
python scripts/reset_database.py --help
```

### 3. Using the API Endpoints

```bash
# Get service status
curl -X GET "http://localhost:8000/api/v1/admin/database-reset/status" \
  -H "Authorization: Bearer your-admin-token"

# Quick reset
curl -X POST "http://localhost:8000/api/v1/admin/database-reset/quick-reset" \
  -H "Authorization: Bearer your-admin-token"

# Reset specific user
curl -X POST "http://localhost:8000/api/v1/admin/database-reset/user" \
  -H "Authorization: Bearer your-admin-token" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "level": "user_cascade",
    "force": false
  }'

# Create test user
curl -X POST "http://localhost:8000/api/v1/admin/database-reset/create-test-user" \
  -H "Authorization: Bearer your-admin-token" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@test.com",
    "password": "testpass123",
    "user_type": "BUYER",
    "nombre": "Test",
    "apellido": "User"
  }'
```

## Configuration

### Test Email Domains

The system automatically identifies test users based on email domains:

```python
safe_test_domains = {
    "@test.com",
    "@testing.com",
    "@dev.com",
    "@example.com"
}
```

### Environment Variables

```bash
# Required for safety checks
ENVIRONMENT=development  # or testing, dev, test
DATABASE_URL=postgresql://localhost:5432/test_db

# Optional Redis configuration
REDIS_URL=redis://localhost:6379/0
```

## Common Workflows

### 1. Daily Testing Reset

For daily testing cycles where you need to reset all test data:

```bash
# Using CLI
python scripts/reset_database.py --quick

# Using API
curl -X POST "http://localhost:8000/api/v1/admin/database-reset/quick-reset" \
  -H "Authorization: Bearer your-token"
```

### 2. Specific User Testing

When testing user registration repeatedly with the same email:

```python
# 1. Reset the user
async with DatabaseResetService() as service:
    result = await service.delete_user_safely(
        email="testuser@test.com",
        level=ResetLevel.USER_CASCADE
    )

# 2. Test registration again with same email
# Registration should now work without conflicts
```

### 3. Integration Test Setup

For integration tests that need clean database state:

```python
@pytest.fixture
async def clean_database():
    """Fixture to ensure clean database for tests."""
    async with DatabaseResetService() as service:
        await service.reset_test_users()
    yield
    # Optional cleanup after test
```

### 4. Development Environment Reset

When switching between different features during development:

```bash
# Full statistics first
python scripts/reset_database.py --stats

# Reset specific test users
python scripts/reset_database.py --user feature-test@test.com

# Or reset all test data
python scripts/reset_database.py --quick
```

## Safety Mechanisms

### 1. Environment Validation

```python
def _validate_environment(self):
    """Validate safe environment for reset operations."""
    current_env = settings.ENVIRONMENT.lower()
    if current_env not in self.allowed_environments:
        raise RuntimeError(f"Reset not allowed in: {current_env}")
```

### 2. User Safety Checks

```python
def _validate_user_safety(self, user: User, force: bool = False):
    """Ensure user is safe to delete."""
    if not force:
        is_test_user = any(domain in user.email for domain in self.safe_test_domains)
        if not is_test_user:
            raise ValueError("User doesn't appear to be test user")
```

### 3. Operation Confirmation

```python
# CLI confirmation example
def confirm_action(prompt: str, default: bool = False) -> bool:
    """Get user confirmation for actions."""
    response = input(f"{prompt} [y/N]: ")
    return response.lower() in ['y', 'yes']

if not confirm_action("Reset user 'test@example.com'?"):
    print("Reset cancelled.")
    return
```

## Error Handling

The system provides comprehensive error handling:

### 1. Service Errors

```python
try:
    result = await service.delete_user_safely(user_id)
    if not result.success:
        for error in result.errors:
            logger.error(f"Reset error: {error}")
except Exception as e:
    logger.error(f"Unexpected error: {str(e)}")
```

### 2. API Error Responses

```json
{
  "detail": "Database reset not allowed in environment: production",
  "status_code": 403
}
```

### 3. CLI Error Display

```bash
❌ Reset failed!
   Error: User test@production.com doesn't appear to be a test user
   Use --force to override this check
```

## Testing

### Running Tests

```bash
# Service tests
python -m pytest tests/services/test_database_reset_service.py -v

# API endpoint tests
python -m pytest tests/api/v1/endpoints/test_database_reset.py -v

# All reset system tests
python -m pytest -k "reset" -v
```

### Test Coverage

- Environment validation
- User identification and safety
- Different reset levels
- Error handling
- API authentication and authorization
- CLI functionality
- Database cleanup operations

## Performance Considerations

### 1. Batch Operations

- Reset operations use batch SQL queries for efficiency
- Related record cleanup is optimized with proper indexing
- Redis operations use pipelining when available

### 2. Connection Management

```python
async with DatabaseResetService() as service:
    # Service automatically manages database connections
    result = await service.reset_test_users()
    # Connection automatically closed
```

### 3. Background Tasks

API endpoints use background tasks for cleanup operations that don't need to block the response:

```python
background_tasks.add_task(
    _cleanup_orphaned_records,
    admin_email=current_user.email
)
```

## Security Considerations

### 1. Admin Authentication

All operations require admin-level authentication:

```python
current_user: User = Depends(get_current_admin_user)
```

### 2. Audit Logging

All operations are logged with admin attribution:

```python
logger.info(f"Admin {admin_email} reset {len(users)} test users")
```

### 3. Environment Isolation

Multiple layers prevent production access:
- Environment variable validation
- Database URL pattern checking
- Explicit confirmation requirements

## Troubleshooting

### Common Issues

1. **"Reset not allowed in environment"**
   - Check `ENVIRONMENT` variable is set to development/testing
   - Verify `DATABASE_URL` contains localhost or test patterns

2. **"User doesn't appear to be test user"**
   - Use `--force` flag if intentional
   - Ensure email uses test domains (@test.com, @example.com, etc.)

3. **"Service not initialized"**
   - Use service as async context manager: `async with DatabaseResetService() as service:`

4. **"Admin access required"**
   - Ensure user has ADMIN or SUPERUSER role
   - Check authentication token is valid

### Debugging

Enable debug logging:

```python
import logging
logging.getLogger('app.services.database_reset_service').setLevel(logging.DEBUG)
```

Get detailed statistics:

```bash
python scripts/reset_database.py --stats
```

## Migration Guide

### From Manual Database Resets

If you were previously doing manual database resets:

```sql
-- Old way (DANGEROUS)
TRUNCATE TABLE users CASCADE;
DELETE FROM orders WHERE user_id IS NULL;
```

```python
# New way (SAFE)
async with DatabaseResetService() as service:
    result = await service.reset_test_users(level=ResetLevel.USER_CASCADE)
```

### Integration with Existing Tests

Update test fixtures to use the reset service:

```python
# Before
@pytest.fixture
def clean_db():
    # Manual database cleanup
    db.execute("DELETE FROM users WHERE email LIKE '%test.com'")

# After
@pytest.fixture
async def clean_db():
    async with DatabaseResetService() as service:
        await service.reset_test_users()
```

## Best Practices

1. **Always Use Test Domains**: Ensure test users use designated test email domains
2. **Environment Validation**: Always validate environment before destructive operations
3. **Incremental Resets**: Use appropriate reset levels - start with USER_DATA before USER_CASCADE
4. **Documentation**: Document reset procedures in your testing workflows
5. **Monitoring**: Monitor reset operations in logs for unusual patterns
6. **Backup Strategy**: Have backup procedures even for test environments

## Contributing

When extending the reset system:

1. Add comprehensive tests for new functionality
2. Ensure environment safety checks are maintained
3. Add appropriate logging and error handling
4. Update this documentation
5. Follow the existing patterns for confirmation and validation

## Support

For issues or questions:

1. Check the troubleshooting section
2. Review service logs for detailed error information
3. Use the `--stats` CLI option to understand current database state
4. Test in interactive mode first: `python scripts/reset_database.py --interactive`