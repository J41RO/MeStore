#!/usr/bin/env python3
"""
Script to create superuser admin account
"""
import sys
import os
import uuid
from datetime import datetime

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

from app.models.user import User, UserType

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_superuser():
    """Create superuser admin account"""
    print("🔐 Creating superuser admin account...")

    # Connect to database directly
    db_url = "sqlite:///./mestore.db"
    print(f"📂 Database: {db_url}")

    engine = create_engine(db_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        # Check if admin already exists
        existing = db.query(User).filter(User.email == "admin@mestocker.com").first()
        if existing:
            print(f"⚠️  Admin user already exists with ID: {existing.id}")
            print(f"    Email: {existing.email}")
            print(f"    Type: {existing.user_type}")
            return True

        # Create admin user
        admin_id = str(uuid.uuid4())
        password_hash = pwd_context.hash("Admin123456")

        admin = User(
            id=admin_id,
            email="admin@mestocker.com",
            password_hash=password_hash,
            nombre="Admin",
            apellido="MeStocker",
            user_type=UserType.SUPERUSER,
            is_active=True,
            is_verified=True,
            email_verified=True,
            phone_verified=False,
            cedula="000000000",
            telefono="+57 300 000 0000",
            direccion="Oficina Central MeStocker",
            reset_attempts=0,
            google_verified_email=False,
            otp_attempts=0,
            security_clearance_level=5,
            performance_score=100.0,
            failed_login_attempts=0,
            force_password_change=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        print("✅ Superuser created successfully!")
        print(f"📧 Email: {admin.email}")
        print(f"🔑 Password: Admin123456")
        print(f"🆔 ID: {admin.id}")
        print(f"👤 Type: {admin.user_type.value}")
        print(f"✔️  Active: {admin.is_active}")
        print(f"✔️  Verified: {admin.is_verified}")

        return True

    except Exception as e:
        print(f"❌ Error creating superuser: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = create_superuser()
    sys.exit(0 if success else 1)