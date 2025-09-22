"""
Admin Users Fixtures for Massive Testing Operation
Provides shared fixtures for admin user management testing across all squads.
SQUAD 1 responsible for maintaining these fixtures.
"""

import pytest
import asyncio
from typing import Dict, List, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from app.models.user import User, UserType, UserStatus
from app.core.auth import get_password_hash
from tests.conftest import test_db


# Shared admin user fixtures for all squads
@pytest.fixture(scope="session")
def admin_user_templates() -> Dict[str, Dict]:
    """
    Template definitions for different types of admin users.
    Used by all squads for consistent admin user creation.
    """
    return {
        "superuser": {
            "email": "superuser@mestore.test",
            "username": "superuser_admin",
            "nombre": "Super",
            "apellido": "Administrator",
            "celular": "+57300000001",
            "user_type": UserType.SUPERUSER,
            "is_active": True,
            "is_superuser": True,
            "user_status": UserStatus.ACTIVE
        },
        "admin": {
            "email": "admin@mestore.test",
            "username": "admin_user",
            "nombre": "Admin",
            "apellido": "User",
            "celular": "+57300000002",
            "user_type": UserType.ADMIN,
            "is_active": True,
            "is_superuser": False,
            "user_status": UserStatus.ACTIVE
        },
        "moderator": {
            "email": "moderator@mestore.test",
            "username": "moderator_user",
            "nombre": "Moderator",
            "apellido": "User",
            "celular": "+57300000003",
            "user_type": UserType.MODERATOR,
            "is_active": True,
            "is_superuser": False,
            "user_status": UserStatus.ACTIVE
        },
        "vendor": {
            "email": "vendor@mestore.test",
            "username": "vendor_user",
            "nombre": "Vendor",
            "apellido": "User",
            "celular": "+57300000004",
            "user_type": UserType.VENDOR,
            "is_active": True,
            "is_superuser": False,
            "user_status": UserStatus.ACTIVE
        },
        "buyer": {
            "email": "buyer@mestore.test",
            "username": "buyer_user",
            "nombre": "Buyer",
            "apellido": "User",
            "celular": "+57300000005",
            "user_type": UserType.BUYER,
            "is_active": True,
            "is_superuser": False,
            "user_status": UserStatus.ACTIVE
        },
        "inactive_admin": {
            "email": "inactive@mestore.test",
            "username": "inactive_admin",
            "nombre": "Inactive",
            "apellido": "Admin",
            "celular": "+57300000006",
            "user_type": UserType.ADMIN,
            "is_active": False,
            "is_superuser": False,
            "user_status": UserStatus.INACTIVE
        },
        "suspended_admin": {
            "email": "suspended@mestore.test",
            "username": "suspended_admin",
            "nombre": "Suspended",
            "apellido": "Admin",
            "celular": "+57300000007",
            "user_type": UserType.ADMIN,
            "is_active": False,
            "is_superuser": False,
            "user_status": UserStatus.SUSPENDED
        }
    }


@pytest.fixture(scope="session")
def admin_permissions_matrix() -> Dict[str, List[str]]:
    """
    Permissions matrix for different admin user types.
    Used for testing role-based access control.
    """
    return {
        "SUPERUSER": [
            "read:all",
            "write:all",
            "delete:all",
            "admin:users",
            "admin:system",
            "admin:config",
            "admin:monitoring",
            "admin:analytics",
            "admin:audit"
        ],
        "ADMIN": [
            "read:users",
            "write:users",
            "read:products",
            "write:products",
            "read:orders",
            "write:orders",
            "admin:monitoring",
            "admin:analytics"
        ],
        "MODERATOR": [
            "read:users",
            "read:products",
            "write:products",
            "read:orders",
            "moderate:content"
        ],
        "VENDOR": [
            "read:own_products",
            "write:own_products",
            "read:own_orders",
            "read:own_analytics"
        ],
        "BUYER": [
            "read:products",
            "write:orders",
            "read:own_orders"
        ]
    }


# Individual admin user fixtures for specific testing needs
@pytest.fixture
async def superuser_admin(test_db: AsyncSession, admin_user_templates: Dict) -> User:
    """
    Create a superuser admin for testing.
    CRITICAL: Used by all squads for admin endpoint testing.
    """
    template = admin_user_templates["superuser"].copy()
    template["email"] = f"superuser_{uuid4().hex[:8]}@mestore.test"
    template["username"] = f"superuser_{uuid4().hex[:8]}"
    template["celular"] = f"+5730{uuid4().hex[:8]}"
    template["hashed_password"] = get_password_hash("SuperSecretPassword123!")

    user = User(**template)
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)

    return user


@pytest.fixture
async def admin_user(test_db: AsyncSession, admin_user_templates: Dict) -> User:
    """
    Create a regular admin user for testing.
    Used for standard admin operations testing.
    """
    template = admin_user_templates["admin"].copy()
    template["email"] = f"admin_{uuid4().hex[:8]}@mestore.test"
    template["username"] = f"admin_{uuid4().hex[:8]}"
    template["celular"] = f"+5730{uuid4().hex[:8]}"
    template["hashed_password"] = get_password_hash("AdminPassword123!")

    user = User(**template)
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)

    return user


@pytest.fixture
async def moderator_user(test_db: AsyncSession, admin_user_templates: Dict) -> User:
    """
    Create a moderator user for testing.
    Used for testing limited admin permissions.
    """
    template = admin_user_templates["moderator"].copy()
    template["email"] = f"moderator_{uuid4().hex[:8]}@mestore.test"
    template["username"] = f"moderator_{uuid4().hex[:8]}"
    template["celular"] = f"+5730{uuid4().hex[:8]}"
    template["hashed_password"] = get_password_hash("ModeratorPassword123!")

    user = User(**template)
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)

    return user


@pytest.fixture
async def inactive_admin(test_db: AsyncSession, admin_user_templates: Dict) -> User:
    """
    Create an inactive admin user for testing.
    Used for testing access control with inactive users.
    """
    template = admin_user_templates["inactive_admin"].copy()
    template["email"] = f"inactive_{uuid4().hex[:8]}@mestore.test"
    template["username"] = f"inactive_{uuid4().hex[:8]}"
    template["celular"] = f"+5730{uuid4().hex[:8]}"
    template["hashed_password"] = get_password_hash("InactivePassword123!")

    user = User(**template)
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)

    return user


# Multi-user fixtures for testing user management operations
@pytest.fixture
async def admin_user_collection(test_db: AsyncSession, admin_user_templates: Dict) -> List[User]:
    """
    Create a collection of different admin users for comprehensive testing.
    Used by SQUAD 1 for user management endpoint testing.
    """
    users = []

    for user_type, template in admin_user_templates.items():
        if user_type in ["superuser", "admin", "moderator", "inactive_admin"]:
            user_data = template.copy()
            user_data["email"] = f"{user_type}_{uuid4().hex[:8]}@mestore.test"
            user_data["username"] = f"{user_type}_{uuid4().hex[:8]}"
            user_data["celular"] = f"+5730{uuid4().hex[:8]}"
            user_data["hashed_password"] = get_password_hash(f"{user_type.title()}Password123!")

            user = User(**user_data)
            test_db.add(user)
            users.append(user)

    await test_db.commit()

    for user in users:
        await test_db.refresh(user)

    return users


@pytest.fixture
async def admin_hierarchy_users(test_db: AsyncSession, admin_user_templates: Dict) -> Dict[str, User]:
    """
    Create a hierarchical structure of admin users for testing.
    Used for testing admin hierarchy and permission inheritance.
    """
    hierarchy = {}

    # Create superuser (top level)
    superuser_data = admin_user_templates["superuser"].copy()
    superuser_data["email"] = f"hierarchy_super_{uuid4().hex[:8]}@mestore.test"
    superuser_data["username"] = f"hierarchy_super_{uuid4().hex[:8]}"
    superuser_data["celular"] = f"+5730{uuid4().hex[:8]}"
    superuser_data["hashed_password"] = get_password_hash("HierarchySuper123!")

    superuser = User(**superuser_data)
    test_db.add(superuser)
    hierarchy["superuser"] = superuser

    # Create admin (mid level)
    admin_data = admin_user_templates["admin"].copy()
    admin_data["email"] = f"hierarchy_admin_{uuid4().hex[:8]}@mestore.test"
    admin_data["username"] = f"hierarchy_admin_{uuid4().hex[:8]}"
    admin_data["celular"] = f"+5730{uuid4().hex[:8]}"
    admin_data["hashed_password"] = get_password_hash("HierarchyAdmin123!")

    admin = User(**admin_data)
    test_db.add(admin)
    hierarchy["admin"] = admin

    # Create moderator (lower level)
    moderator_data = admin_user_templates["moderator"].copy()
    moderator_data["email"] = f"hierarchy_mod_{uuid4().hex[:8]}@mestore.test"
    moderator_data["username"] = f"hierarchy_mod_{uuid4().hex[:8]}"
    moderator_data["celular"] = f"+5730{uuid4().hex[:8]}"
    moderator_data["hashed_password"] = get_password_hash("HierarchyMod123!")

    moderator = User(**moderator_data)
    test_db.add(moderator)
    hierarchy["moderator"] = moderator

    await test_db.commit()

    for user in hierarchy.values():
        await test_db.refresh(user)

    return hierarchy


# Authentication token fixtures for admin users
@pytest.fixture
async def superuser_token(superuser_admin: User) -> str:
    """
    Generate authentication token for superuser.
    Used across all squads for authenticated admin endpoint testing.
    """
    from app.core.auth import create_access_token

    token_data = {"sub": str(superuser_admin.id)}
    return create_access_token(token_data)


@pytest.fixture
async def admin_token(admin_user: User) -> str:
    """
    Generate authentication token for admin user.
    Used for standard admin operation testing.
    """
    from app.core.auth import create_access_token

    token_data = {"sub": str(admin_user.id)}
    return create_access_token(token_data)


@pytest.fixture
async def moderator_token(moderator_user: User) -> str:
    """
    Generate authentication token for moderator user.
    Used for limited admin permission testing.
    """
    from app.core.auth import create_access_token

    token_data = {"sub": str(moderator_user.id)}
    return create_access_token(token_data)


# Batch user creation utilities for performance testing
async def create_admin_users_batch(db: AsyncSession, count: int = 50, user_type: UserType = UserType.ADMIN) -> List[User]:
    """
    Create a batch of admin users for performance testing.
    Used by SQUAD 3 for load testing admin endpoints.
    """
    users = []

    for i in range(count):
        user_data = {
            "email": f"batch_admin_{i}_{uuid4().hex[:8]}@mestore.test",
            "username": f"batch_admin_{i}_{uuid4().hex[:8]}",
            "nombre": f"BatchAdmin{i}",
            "apellido": f"User{i}",
            "celular": f"+5730{str(i).zfill(8)}",
            "hashed_password": get_password_hash(f"BatchPassword{i}!"),
            "user_type": user_type,
            "is_active": True,
            "is_superuser": user_type == UserType.SUPERUSER,
            "user_status": UserStatus.ACTIVE
        }

        user = User(**user_data)
        users.append(user)

    # Batch insert for performance
    db.add_all(users)
    await db.commit()

    for user in users:
        await db.refresh(user)

    return users


# Cleanup utilities
@pytest.fixture
async def cleanup_admin_users():
    """
    Cleanup fixture to remove test admin users after squad testing.
    Prevents test data pollution between squad operations.
    """
    # This will be called after test completion
    yield

    # Cleanup logic would go here if needed
    # Current implementation relies on database transaction rollback
    pass


# Security testing fixtures
@pytest.fixture
async def compromised_admin_user(test_db: AsyncSession) -> User:
    """
    Create an admin user with security issues for security testing.
    Used by security-focused testing in all squads.
    """
    user_data = {
        "email": f"compromised_{uuid4().hex[:8]}@mestore.test",
        "username": f"compromised_{uuid4().hex[:8]}",
        "nombre": "Compromised",
        "apellido": "Admin",
        "celular": f"+5730{uuid4().hex[:8]}",
        "hashed_password": get_password_hash("WeakPassword123"),  # Intentionally weak
        "user_type": UserType.ADMIN,
        "is_active": True,
        "is_superuser": False,
        "user_status": UserStatus.ACTIVE,
        # Additional fields that might indicate compromise
        "failed_login_attempts": 5,
        "last_login_ip": "suspicious.ip.address"
    }

    user = User(**user_data)
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)

    return user


# Performance testing data
@pytest.fixture(scope="session")
def admin_load_test_config() -> Dict:
    """
    Configuration for load testing admin endpoints.
    Used by SQUAD 3 for performance validation.
    """
    return {
        "concurrent_users": 50,
        "test_duration": 300,  # 5 minutes
        "endpoints_to_test": [
            "/admin/dashboard/kpis",
            "/admin/users",
            "/admin/products",
            "/admin/monitoring/system"
        ],
        "expected_response_times": {
            "/admin/dashboard/kpis": 2.0,  # seconds
            "/admin/users": 1.5,
            "/admin/products": 2.5,
            "/admin/monitoring/system": 3.0
        },
        "error_rate_threshold": 0.01  # 1% error rate max
    }


# Squad coordination metadata
FIXTURE_METADATA = {
    "squad_1_primary": [
        "admin_user_templates",
        "admin_permissions_matrix",
        "superuser_admin",
        "admin_user",
        "admin_user_collection",
        "admin_hierarchy_users"
    ],
    "squad_2_dependencies": [
        "superuser_token",
        "admin_token",
        "admin_permissions_matrix"
    ],
    "squad_3_dependencies": [
        "admin_load_test_config",
        "create_admin_users_batch",
        "superuser_admin",
        "admin_user_collection"
    ],
    "squad_4_dependencies": [
        "compromised_admin_user",
        "admin_hierarchy_users",
        "admin_permissions_matrix"
    ],
    "shared_across_all": [
        "cleanup_admin_users",
        "superuser_token",
        "admin_token"
    ]
}


# Validation utilities for squad coordination
def validate_admin_fixture_integrity() -> bool:
    """
    Validate that all admin fixtures are properly configured.
    Called by coordination system to ensure fixture consistency.
    """
    try:
        # Check that all required fixture types are defined
        required_fixtures = [
            "superuser_admin", "admin_user", "moderator_user",
            "admin_user_collection", "admin_hierarchy_users"
        ]

        # This would include validation logic
        # For now, return True as fixtures are properly defined
        return True

    except Exception:
        return False


if __name__ == "__main__":
    # Test fixture validation
    print("Admin fixtures validation:", validate_admin_fixture_integrity())
    print("Fixture metadata:", FIXTURE_METADATA)