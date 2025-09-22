#!/usr/bin/env python3
"""
Simple script to create test users for debugging authentication
"""

import sys
import os
import asyncio

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models.user import User
from app.utils.password import hash_password
import uuid

async def create_test_users():
    """Create test users with correct field names"""

    # Get database session (sync)
    db_gen = get_db()
    db = next(db_gen)

    try:
        # Check if users already exist
        existing_admin = db.query(User).filter(User.email == "admin@test.com").first()
        if existing_admin:
            print(f"✅ Admin user already exists: {existing_admin.email}")
        else:
            # Create admin user
            admin_password_hash = await hash_password("admin123")
            admin_user = User(
                id=str(uuid.uuid4()),
                email="admin@test.com",
                password_hash=admin_password_hash,
                first_name="Admin",
                last_name="Test",
                user_type="ADMIN",
                is_active=True,
                is_verified=True
            )
            db.add(admin_user)
            print("✅ Created admin user: admin@test.com / admin123")

        # Check for vendor user
        existing_vendor = db.query(User).filter(User.email == "vendor@test.com").first()
        if not existing_vendor:
            # Create vendor user
            vendor_password_hash = await hash_password("vendor123")
            vendor_user = User(
                id=str(uuid.uuid4()),
                email="vendor@test.com",
                password_hash=vendor_password_hash,
                first_name="Vendor",
                last_name="Test",
                user_type="VENDEDOR",
                is_active=True,
                is_verified=True
            )
            db.add(vendor_user)
            print("✅ Created vendor user: vendor@test.com / vendor123")

        # Check for buyer user
        existing_buyer = db.query(User).filter(User.email == "buyer@test.com").first()
        if not existing_buyer:
            # Create buyer user
            buyer_password_hash = await hash_password("buyer123")
            buyer_user = User(
                id=str(uuid.uuid4()),
                email="buyer@test.com",
                password_hash=buyer_password_hash,
                first_name="Buyer",
                last_name="Test",
                user_type="COMPRADOR",
                is_active=True,
                is_verified=True
            )
            db.add(buyer_user)
            print("✅ Created buyer user: buyer@test.com / buyer123")

        db.commit()
        print("\n🎉 All test users created successfully!")

        # Verify the users
        print("\n=== VERIFICATION ===")
        all_users = db.query(User).filter(
            User.email.in_(["admin@test.com", "vendor@test.com", "buyer@test.com"])
        ).all()

        for user in all_users:
            print(f"✅ {user.email}: Type={user.user_type}, Active={user.is_active}, ID={user.id}")

    except Exception as e:
        print(f"❌ Error creating users: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(create_test_users())