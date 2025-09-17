
import sqlite3
import sys
from passlib.context import CryptContext

def test_login(email, password):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    try:
        conn = sqlite3.connect("./mestore_auth_test.db")
        cursor = conn.cursor()

        cursor.execute("SELECT password_hash, user_type, is_active FROM users WHERE email = ?", (email,))
        user_data = cursor.fetchone()

        if not user_data:
            print(f"❌ User {email} not found")
            return False

        password_hash, user_type, is_active = user_data

        if not is_active:
            print(f"❌ User {email} is not active")
            return False

        if pwd_context.verify(password, password_hash):
            print(f"✅ Login successful: {email} | {user_type}")
            return True
        else:
            print(f"❌ Invalid password for {email}")
            return False

    except Exception as e:
        print(f"❌ Login test error: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    email = sys.argv[1] if len(sys.argv) > 1 else "super@mestore.com"
    password = sys.argv[2] if len(sys.argv) > 2 else "123456"
    test_login(email, password)
