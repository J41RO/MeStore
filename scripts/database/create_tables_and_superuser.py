#!/usr/bin/env python3
"""
Create SQLite tables and superuser for MeStore
This script creates all tables and the superuser in one go.
"""

import sys
from pathlib import Path
import sqlite3
import uuid
from datetime import datetime
from passlib.context import CryptContext

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

DATABASE_FILE = "./mestore_production.db"

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)

def create_users_table():
    """Create the users table with all required fields"""

    create_table_sql = """
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        nombre TEXT,
        apellido TEXT,
        user_type TEXT NOT NULL DEFAULT 'COMPRADOR',
        vendor_status TEXT DEFAULT 'draft',
        is_active INTEGER NOT NULL DEFAULT 1,
        is_verified INTEGER NOT NULL DEFAULT 0,
        cedula TEXT UNIQUE,
        telefono TEXT,
        ciudad TEXT,
        empresa TEXT,
        direccion TEXT,
        email_verified INTEGER NOT NULL DEFAULT 0,
        phone_verified INTEGER NOT NULL DEFAULT 0,
        otp_secret TEXT,
        otp_expires_at DATETIME,
        otp_attempts INTEGER NOT NULL DEFAULT 0,
        otp_type TEXT,
        last_otp_sent DATETIME,
        reset_token TEXT,
        reset_token_expires_at DATETIME,
        reset_attempts INTEGER NOT NULL DEFAULT 0,
        last_reset_request DATETIME,
        last_login DATETIME,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        banco TEXT,
        tipo_cuenta TEXT,
        numero_cuenta TEXT,
        avatar_url TEXT,
        business_name TEXT,
        business_description TEXT,
        website_url TEXT,
        social_media_links TEXT,
        business_hours TEXT,
        shipping_policy TEXT,
        return_policy TEXT,
        notification_preferences TEXT,
        bank_name TEXT,
        account_holder_name TEXT,
        account_number TEXT
    );
    """

    # Create indexes
    indexes_sql = [
        "CREATE INDEX IF NOT EXISTS ix_users_email ON users (email);",
        "CREATE INDEX IF NOT EXISTS ix_users_user_type ON users (user_type);",
        "CREATE INDEX IF NOT EXISTS ix_users_is_active ON users (is_active);",
        "CREATE INDEX IF NOT EXISTS ix_users_cedula ON users (cedula);",
        "CREATE INDEX IF NOT EXISTS ix_users_reset_token ON users (reset_token);",
        "CREATE INDEX IF NOT EXISTS ix_user_type_active ON users (user_type, is_active);",
        "CREATE INDEX IF NOT EXISTS ix_user_email_active ON users (email, is_active);",
        "CREATE INDEX IF NOT EXISTS ix_user_created_type ON users (created_at, user_type);",
        "CREATE INDEX IF NOT EXISTS ix_user_active_created ON users (is_active, created_at);",
        "CREATE INDEX IF NOT EXISTS ix_user_otp_expires ON users (otp_expires_at);",
        "CREATE INDEX IF NOT EXISTS ix_user_email_verified ON users (email_verified);"
    ]

    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    try:
        # Create table
        print("🔧 Creating users table...")
        cursor.execute(create_table_sql)

        # Create indexes
        print("🔧 Creating indexes...")
        for index_sql in indexes_sql:
            cursor.execute(index_sql)

        conn.commit()
        print("✅ Users table and indexes created successfully!")

        return conn

    except Exception as e:
        conn.rollback()
        print(f"❌ Error creating users table: {e}")
        conn.close()
        raise

def create_superuser(conn):
    """Create superuser in the database"""

    cursor = conn.cursor()

    try:
        # Check if superuser already exists
        cursor.execute("SELECT email FROM users WHERE email = ?", ("super@mestore.com",))
        result = cursor.fetchone()

        if result:
            print("⚠️  Superuser already exists! Updating password...")
            # Update existing user
            hashed_password = hash_password("123456")
            cursor.execute("""
                UPDATE users
                SET password_hash = ?,
                    user_type = 'SUPERUSER',
                    is_active = 1,
                    is_verified = 1,
                    email_verified = 1,
                    updated_at = ?
                WHERE email = ?
            """, (hashed_password, datetime.utcnow().isoformat(), "super@mestore.com"))
        else:
            print("📝 Creating new superuser...")
            # Create new superuser
            user_id = str(uuid.uuid4())
            hashed_password = hash_password("123456")

            cursor.execute("""
                INSERT INTO users (
                    id, email, password_hash, user_type,
                    is_active, is_verified, email_verified, phone_verified,
                    created_at, updated_at, nombre, apellido,
                    otp_attempts, reset_attempts
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, "super@mestore.com", hashed_password, "SUPERUSER",
                1, 1, 1, 0,
                datetime.utcnow().isoformat(), datetime.utcnow().isoformat(),
                "Super", "Admin", 0, 0
            ))

        conn.commit()
        print("✅ Superuser created successfully!")
        print("📧 Email: super@mestore.com")
        print("🔑 Password: 123456")
        print("🔐 Type: SUPERUSER")
        print("🌐 Ready for login at: http://192.168.1.137:5173/admin-login")

        # Verify the user was created
        cursor.execute("SELECT email, user_type, is_active FROM users WHERE email = ?", ("super@mestore.com",))
        result = cursor.fetchone()

        if result:
            print(f"🔍 Verification: User {result[0]} with type {result[1]} is {'active' if result[2] else 'inactive'}")
        else:
            print("❌ Error: Superuser verification failed!")

    except Exception as e:
        conn.rollback()
        print(f"❌ Error creating superuser: {e}")
        raise

def main():
    """Main function to create tables and superuser"""
    print("🚀 Setting up MeStore database and superuser...")

    try:
        # Create tables and get connection
        conn = create_users_table()

        # Create superuser
        create_superuser(conn)

        # Close connection
        conn.close()

        print("\n🎉 SUCCESS! Database setup complete!")
        print("🔐 Superuser credentials:")
        print("   Email: super@mestore.com")
        print("   Password: 123456")
        print("🌐 Admin login: http://192.168.1.137:5173/admin-login")

    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()