#!/usr/bin/env python3
"""
Create Superuser Script for MeStore
Creates a superuser with email: super@mestore.com and password: 123456
"""

import asyncio
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
import uuid
from datetime import datetime

# Database configuration
DATABASE_URL = "sqlite:///./mestore_production.db"

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)

def create_superuser():
    """Create superuser using direct SQLite connection."""
    print("🚀 Creating superuser for MeStore...")

    # Create SQLite engine (sync for simplicity)
    engine = create_engine(DATABASE_URL.replace("sqlite:///", "sqlite:///"))
    Session = sessionmaker(bind=engine)

    with Session() as session:
        try:
            # Check if superuser already exists
            result = session.execute(
                text("SELECT email FROM users WHERE email = :email"),
                {"email": "super@mestore.com"}
            ).fetchone()

            if result:
                print("⚠️  Superuser already exists! Updating password...")
                # Update existing user
                hashed_password = hash_password("123456")
                session.execute(
                    text("""
                        UPDATE users
                        SET password_hash = :password_hash,
                            user_type = 'SUPERUSER',
                            is_active = 1,
                            is_verified = 1,
                            email_verified = 1,
                            updated_at = :updated_at
                        WHERE email = :email
                    """),
                    {
                        "password_hash": hashed_password,
                        "email": "super@mestore.com",
                        "updated_at": datetime.utcnow()
                    }
                )
            else:
                print("📝 Creating new superuser...")
                # Create new superuser
                user_id = str(uuid.uuid4())
                hashed_password = hash_password("123456")

                session.execute(
                    text("""
                        INSERT INTO users (
                            id, email, password_hash, user_type,
                            is_active, is_verified, email_verified, phone_verified,
                            created_at, updated_at, nombre, apellido,
                            otp_attempts, reset_attempts
                        ) VALUES (
                            :id, :email, :password_hash, :user_type,
                            :is_active, :is_verified, :email_verified, :phone_verified,
                            :created_at, :updated_at, :nombre, :apellido,
                            :otp_attempts, :reset_attempts
                        )
                    """),
                    {
                        "id": user_id,
                        "email": "super@mestore.com",
                        "password_hash": hashed_password,
                        "user_type": "SUPERUSER",
                        "is_active": 1,
                        "is_verified": 1,
                        "email_verified": 1,
                        "phone_verified": 0,
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow(),
                        "nombre": "Super",
                        "apellido": "Admin",
                        "otp_attempts": 0,
                        "reset_attempts": 0
                    }
                )

            session.commit()
            print("✅ Superuser created successfully!")
            print("📧 Email: super@mestore.com")
            print("🔑 Password: 123456")
            print("🔐 Type: SUPERUSER")
            print("🌐 Ready for login at: http://192.168.1.137:5173/admin-login")

            # Verify the user was created
            result = session.execute(
                text("SELECT email, user_type, is_active FROM users WHERE email = :email"),
                {"email": "super@mestore.com"}
            ).fetchone()

            if result:
                print(f"🔍 Verification: User {result[0]} with type {result[1]} is {'active' if result[2] else 'inactive'}")
            else:
                print("❌ Error: Superuser verification failed!")

        except Exception as e:
            session.rollback()
            print(f"❌ Error creating superuser: {e}")
            raise

if __name__ == "__main__":
    create_superuser()